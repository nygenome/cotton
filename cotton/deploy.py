'''
Controls deployment of releases.

Uses the following env settings:
    Defined:
        * blah

    Derived:
        * blah

    Called:
        * activate_virtualenv
        * configuration_name
        * current_path
        * deploy_to
        * release_name
        * release_path
        * release_dir
        * shared_dir
        * scm_repository
        * releases_path
        * shared_children
        * shared_path
        * uwsgi_pidfile
        * virtualenv_path
      

'''
import os
import time

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
    set_env("virtualenv_path", os.path.join(env.app_root, ".virtualenv"), **overrides)
    set_env("activate_virtualenv", "source %s" % os.path.join(env.virtualenv_path,
                                                                 "bin", "activate"), **overrides)
    set_env("releases_dir", "releases", **overrides)
    set_env("current_dir", "current", **overrides)
    set_env("shared_dir", "shared", **overrides)
    set_env("shared_children", ["logs", "pids", "sock", "input"], **overrides)


    set_env("releases_path", os.path.join(env.deploy_to, env.releases_dir), **overrides)
    set_env("release_time_format", "%Y%m%d%H%M%S", **overrides)
    set_env("release_name", time.strftime(env.release_time_format), **overrides)
    set_env("release_path", os.path.join(env.releases_path, env.release_name), **overrides)

    set_env("shared_path", os.path.join(env.deploy_to, env.shared_dir), **overrides)
    set_env("current_path", os.path.join(env.deploy_to, env.current_dir), **overrides)

    set_env("config_path", os.path.join(env.releases_path, "config"), **overrides)
    set_env("config_environments_path", os.path.join(env.config_path,
                                                     "environments"), **overrides)

    set_env("servers_path", os.path.join(env.app_root, "servers"), **overrides)
register_setup(setup)

def choose_local_tar():
    with fab.settings(fab.hide('everything')):
        host_os = fab.local("uname", capture=True)

    if host_os == 'Darwin':
        return 'gnutar'
    return 'tar'

def find_previous_release():
    with fab.settings(fab.hide('stdout')):
        releases = fab.run("ls -1 %(releases_path)s" % env)

    releases = sorted(releases.split())
    current_index = releases.index(find_canonical_current_release())
    if current_index < 1:
        raise Exception("Current release is the oldest.")

    return releases[current_index-1]

def find_canonical_current_release():
    with fab.settings(fab.hide('stdout')):
        with fab.cd(env.current_path):
            current = os.path.basename(run("pwd -P"))

    return current

def setup_virtualenv(virtualenv_path):
    virtualenv_cmd = ["virtualenv",
                      "--distribute",
                      "--no-site-packages",
                      "-p python2.7",
                      "%s" % virtualenv_path]

    # TODO: extract to variable
    with fab.path("/seq/annotation/development/tools/python/2.7.1/bin", behavior='prepend'):
        with fab.prefix("umask 0002"):
            helpers.remote(" ".join(virtualenv_cmd))


def make_directories():
    with fab.prefix("umask 0002"):
        helpers.remote("mkdir -p %(deploy_to)s" % env)
        with fab.cd(env.deploy_to):
            helpers.remote("mkdir -p %(releases_dir)s" % env)
            helpers.remote("mkdir -p %(shared_dir)s" % env)
            make_shared_children_dirs()

def make_shared_children_dirs():
    for child in env.shared_children:
        with fab.cd(env.shared_path):
            helpers.remote("test -d %s || mkdir %s" % (child, child))


def checkout_source():
    # TODO: move this to git.py
    # TODO: cached copy strategy
    # TODO: submodules
    with fab.prefix("umask 0002"):
        fab.run("git clone %(scm_repository)s %(release_path)s" % env)
        git_dir = os.path.join(env.release_path, ".git")
        with fab.cd(env.release_path):
            fab.run("git rev-parse HEAD > %s" % os.path.join(env.release_path,
                                                         "REVISION"))
        fab.run("rm -rf %s" % git_dir)


def install_requirements(release_path, upgrade=False):
    '''Install requirements into pip from config/requirements.pip'''
    command = []
    command.append("pip")
    command.append("install")
    if upgrade:
        command.append("--upgrade")
    command.append("-r %s" % env.requirements_file)

    with fab.prefix("umask 0002"):
        with fab.prefix(env.activate_virtualenv):
            with fab.cd(release_path):
                helpers.remote(" ".join(command))


def make_symlinks(release_path):
    '''Create a 'current' symlink pointing to a release we just checked 
    out, and symlinks within pointing to the shared children'''
    with fab.settings(fab.hide('warnings'), warn_only=True):
        helpers.remote("test -L %(current_path)s && rm %(current_path)s" % env)

    helpers.remote("ln -s %s %s" % (release_path, env.current_path))
    for child in env.shared_children:
        child_path = os.path.join(release_path, child)
        with fab.settings(fab.hide('warnings'), warn_only=True):
            helpers.remote("test -L %s && rm %s" % (child_path, child_path))

        helpers.remote("ln -s %s %s" % (
            os.path.join(env.shared_path, child),
            child_path
        ))
        

def make_workspace_file():
    """Create a tag file that announces that a particular release is
    was made from a working copy, rather than from version control."""

    ws_file = os.path.join(env.current_path, "WORKSPACE_RELEASE")
    ws_host = fab.local("hostname", capture=True)
    ws_string = "Installed from %s@%s:%s at %s" % (os.environ['USER'],
                                                   ws_host,
                                                   os.environ['PWD'],
                                                   env.release_name)
    helpers.remote("echo \"%s\" > %s" % (ws_string, ws_file))
    
def install_config(release_path):
    config_dir = os.path.join(release_path, "config")
    paths = {
        "deploy": os.path.join(env.config_environments_path,
                               "%s.py" % env.configuration_name),
        "local": os.path.join(config_dir, "local.py")
    }
    with fab.settings(fab.hide('warnings'), warn_only=True):
        helpers.remote("test -L %(local)s && rm %(local)s" % paths)

    helpers.remote("ln -s %(deploy)s %(local)s" % paths)

# TODO: move authenticate to helpers
def authenticate():
    with fab.settings(fab.hide('running')):
        fab.run('echo "Authenticating..."')
        with fab.settings(fab.hide('stdout')):
            helpers.remote('echo -n')

def test_locally(run_tests=True):
    run_tests = to_boolean(run_tests)
    if run_tests:
        fab.local("nosetests")

def to_boolean(obj):
    if type(obj) == type(''):
        if obj.lower() in ['0', 'false']:
            return False
    return bool(obj)
