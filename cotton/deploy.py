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
        * virtualenv_python_dir


'''
import os
import time

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

from cotton.scm import BroadGit

def setup(**overrides):
    set_env("virtualenv_path", os.path.join(env.app_root, ".virtualenv"), **overrides)
    set_env("activate_virtualenv", "source %s" % os.path.join(env.virtualenv_path,
                                                                 "bin", "activate"), **overrides)
    set_env("config_dir", "config", **overrides)
    set_env("environments_dir", "environments", **overrides)
    set_env("releases_dir", "releases", **overrides)
    set_env("current_dir", "current", **overrides)
    set_env("shared_dir", "shared", **overrides)
    set_env("shared_children", ["logs", "pids", "sock", "input", "static_root"], **overrides)


    set_env("releases_path", os.path.join(env.deploy_to, env.releases_dir), **overrides)
    set_env("release_time_format", "%Y%m%d%H%M%S", **overrides)
    set_env("release_name", time.strftime(env.release_time_format), **overrides)
    set_env("release_path", os.path.join(env.releases_path, env.release_name), **overrides)

    set_env("shared_path", os.path.join(env.deploy_to, env.shared_dir), **overrides)
    set_env("current_path", os.path.join(env.deploy_to, env.current_dir), **overrides)

    set_env("config_path", os.path.join(env.release_path, env.config_dir), **overrides)
    set_env("config_environments_path", os.path.join(env.config_path,
                                                     env.environments_dir), **overrides)

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
            current = os.path.basename(fab.run("pwd -P"))

    return current

def setup_virtualenv(virtualenv_path):
    virtualenv_cmd = ["virtualenv",
                      "--distribute",
                      "--no-site-packages",
                      "-p %s" % os.path.join(env.virtualenv_python_dir, 'python'),
                      "%s" % virtualenv_path]

    with fab.path(env.virtualenv_python_dir, behavior='prepend'):
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


def checkout_source(ref=None):
    # TODO: cached copy strategy
    # TODO: submodules
    scm = env.scm_tool
    with fab.prefix("umask 0002"):
        scm.checkout(env.scm_repository, env.release_path, ref)
        # bug in early 1.7 git versions, fixed 2012-07-15 - git update needed
        fab.run("chmod g+w %(release_path)s" % env)

        revision_path = os.path.join(env.release_path, "REVISION")
        scm.branch_name(env.release_path, revision_path)
        scm.tag_name(env.release_path, revision_path, append=True)
        scm.revision(env.release_path, revision_path, append=True)
        fab.run("rm -rf %s" % os.path.join(env.release_path, ".git"))


def make_symlinks(release_path):
    '''Create a 'current' symlink pointing to a release we just checked
    out, and symlinks within pointing to the shared children'''
    make_current_symlink(release_path)
    make_shared_children_symlinks(release_path)

def make_current_symlink(release_path):
    '''Create a 'current' symlink pointing to a release we just checked
    out. '''
    with fab.settings(fab.hide('warnings'), warn_only=True):
        helpers.remote("test -L %(current_path)s && rm %(current_path)s" % env)
    helpers.remote("ln -s %s %s" % (release_path, env.current_path))


def make_shared_children_symlinks(release_path):
    ''' Create symlinks the release we just checked out pointing 
    to the shared children'''
    for child in env.shared_children:
        child_path = os.path.join(release_path, child)
        with fab.settings(fab.hide('warnings'), warn_only=True):
            helpers.remote("test -L %s && rm %s" % (child_path, child_path))

        helpers.remote("ln -s %s %s" % (
            os.path.join(env.shared_path, child),
            child_path
        ))



def install_workspace():
    fab.local(choose_local_tar() + (" -czf %(release_name)s.tar *" % env))
    with fab.prefix("umask 0002"):
        fab.run("mkdir -p %(release_path)s" % env)
        fab.put("%(release_name)s.tar" % env, env.release_path)
        with fab.cd(env.release_path):
            helpers.remote("tar -zxf %(release_name)s.tar" % env)
            helpers.remote("rm %(release_name)s.tar" % env)

    fab.local("rm %(release_name)s.tar" % env)
    helpers.remote("rm -f %(release_path)s/config/local.py" % env)


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

def install_config(release_path, config_dir='config', config_extension='py',
                   local_basename='local', command='ln -s'):
    config_dir = os.path.join(release_path, config_dir)

    if config_extension.startswith('.'):
        config_extension = config_extension[1:]

    paths = {
        "cmd": command,
        "deploy": os.path.join(
            release_path, env.config_dir, env.environments_dir,
            "%s.%s" % (env.configuration_name, config_extension)
        ),
        "local": os.path.join(
            config_dir,
            "%s.%s" % (local_basename, config_extension)
        )
    }
    with fab.settings(fab.hide('warnings'), warn_only=True):
        helpers.remote("test -L %(local)s && rm %(local)s" % paths)

    helpers.remote("test -e %(deploy)s && %(cmd)s %(deploy)s %(local)s" % paths)

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
