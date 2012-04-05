import os

from fabric.api import *
from fabric.contrib.files import exists
from broadcloth.helpers import remote

@task 
def whereami():
    '''Displays some information about where this task is running.'''
    with cd(env.current_path):
        run("uname -n; pwd -P; ls")

@task(default=True)
def update(run_tests=True):
    '''Deploy a new version from origin/master. Pass :run_tests=0 to
    skip the automated tests and deploy anyway.
    '''
    from broadcloth import uwsgi

    test_locally(run_tests)
    authenticate()
    checkout_source()
    install_config(env.release_path)
    install_requirements(env.release_path)
    make_shared_children_dirs()
    make_symlinks(env.release_path)
    if exists(env.uwsgi_pidfile):
        uwsgi.reload()

@task
def cold(run_tests=True):
    '''Bootstrap a cold deployment.  This will create a functioning Olive
    install from nothing.'''
    from broadcloth import uwsgi
    from broadcloth import nginx

    test_locally(run_tests)
    authenticate()
    setup_virtualenv(env.virtualenv_path)
    make_directories()
    checkout_source()
    install_config(env.release_path)
    install_requirements(env.release_path)
    make_symlinks(env.release_path)
    nginx.update_conf()
    uwsgi.update_conf()
    uwsgi.start()
    nginx.start()

def choose_local_tar():
    with settings(hide('everything')):
        host_os = local("uname", capture=True)

    if host_os == 'Darwin':
        return 'gnutar'
    return 'tar'

@task
def from_workspace(run_tests=True):
    '''Deploy a new version from this working copy.  Not for use unless
    circumstances require.'''

    from broadcloth import uwsgi

    test_locally(run_tests)
    authenticate()
    local(choose_local_tar() + (" -czf %(release_name)s.tar *" % env))
    with prefix("umask 0002"):
        remote("mkdir %(release_path)s" % env)
        put("%(release_name)s.tar" % env, env.release_path)
        with cd(env.release_path):
                remote("tar -zxf %(release_name)s.tar" % env)
                run("rm %(release_name)s.tar" % env)

    local("rm %(release_name)s.tar" % env)
    remote("rm -f %(release_path)s/config/local.py" % env)
    install_config(env.release_path)
    make_shared_children_dirs()
    make_symlinks(env.release_path)
    make_workspace_file()
    if exists(env.uwsgi_pidfile):
        uwsgi.reload()

@task
def rollback():
    '''Rolls back the install to the most recent release that is prior to
    the current release.'''
    from broadcloth import uwsgi

    uwsgi.stop()
    
    current_release = find_canonical_current_release()

    target = os.path.join(env.releases_path, find_previous_release())
    install_config(target)
    install_requirements(target)
    make_symlinks(target)

    with cd(env.releases_path):
        remote("rm -rf %s" % current_release)

    uwsgi.start()

def find_previous_release():
    with settings(hide('stdout')):
        releases = run("ls -1 %(releases_path)s" % env)

    releases = sorted(releases.split())
    current_index = releases.index(find_canonical_current_release())
    if current_index < 1:
        raise Exception("Current release is the oldest.")

    return releases[current_index-1]

def find_canonical_current_release():
    with settings(hide('stdout')):
        with cd(env.current_path):
            current = os.path.basename(run("pwd -P"))

    return current

def setup_virtualenv(virtualenv_path):
    virtualenv_cmd = ["virtualenv",
                      "--distribute",
                      "--no-site-packages",
                      "-p python2.7",
                      "%s" % virtualenv_path]

    with path("/seq/annotation/development/tools/python/2.7.1/bin", behavior='prepend'):
        with prefix("umask 0002"):
            remote(" ".join(virtualenv_cmd))


def make_directories():
    with prefix("umask 0002"):
        remote("mkdir %(deploy_to)s" % env)
        with cd(env.deploy_to):
            remote("mkdir %(releases_dir)s" % env)
            remote("mkdir %(shared_dir)s" % env)
            make_shared_children_dirs()

def make_shared_children_dirs():
    for child in env.shared_children:
        with cd(env.shared_path):
            remote("test -d %s || mkdir %s" % (child, child))


def checkout_source():
    # TODO: move this to config/git.py
    # TODO: cached copy strategy
    # TODO: submodules
    with prefix("umask 0002"):
        puts("*** find error is git quirk when running from a remote pty, ignore..")
        run("git clone %(scm_repository)s %(release_path)s" % env)
        git_dir = os.path.join(env.release_path, ".git")
        with cd(env.release_path):
            run("git rev-parse HEAD > %s" % os.path.join(env.release_path,
                                                         "REVISION"))
        run("rm -rf %s" % git_dir)


def install_requirements(release_path, upgrade=False):
    '''Install requirements into pip from config/requirements.pip'''
    command = []
    command.append("pip")
    command.append("install")
    if upgrade:
        command.append("--upgrade")
    command.append("-r config/requirements.pip")

    with prefix("umask 0002"):
        with prefix(env.activate_virtualenv):
            with cd(release_path):
                remote(" ".join(command))


def make_symlinks(release_path):
    '''Create a 'current' symlink pointing to a release we just checked 
    out, and symlinks within pointing to the shared children'''
    with settings(hide('warnings'), warn_only=True):
        remote("test -L %(current_path)s && rm %(current_path)s" % env)

    remote("ln -s %s %s" % (release_path, env.current_path))
    for child in env.shared_children:
        child_path = os.path.join(release_path, child)
        with settings(hide('warnings'), warn_only=True):
            remote("test -L %s && rm %s" % (child_path, child_path))

        remote("ln -s %s %s" % (
            os.path.join(env.shared_path, child),
            child_path
        ))
        

def make_workspace_file():
    """Create a tag file that announces that a particular release is
    was made from a working copy, rather than from version control."""

    ws_file = os.path.join(env.current_path, "WORKSPACE_RELEASE")
    ws_host = local("hostname", capture=True)
    ws_string = "Installed from %s@%s:%s at %s" % (os.environ['USER'],
                                                   ws_host,
                                                   os.environ['PWD'],
                                                   env.release_name)
    remote("echo \"%s\" > %s" % (ws_string, ws_file))
    
def install_config(release_path):
    config_dir = os.path.join(release_path, "config")
    paths = {
        "deploy": os.path.join(config_dir, "%s.py" % env.configuration_name),
        "local": os.path.join(config_dir, "local.py")
    }
    with settings(hide('warnings'), warn_only=True):
        remote("test -L %(local)s && rm %(local)s" % paths)

    remote("ln -s %(deploy)s %(local)s" % paths)

def authenticate():
    with settings(hide('running')):
        run('echo "Authenticating..."')
        with settings(hide('stdout')):
            remote('echo -n')

def test_locally(run_tests=True):
    run_tests = to_boolean(run_tests)
    if run_tests:
        local("nosetests")

def to_boolean(obj):
    if type(obj) == type(''):
        if obj.lower() in ['0', 'false']:
            return False
    return bool(obj)
