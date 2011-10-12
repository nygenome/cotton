import os

from fabric.api import *
from fabric.contrib.files import exists
from config.fabric.helpers import remote

@task(default=True)
def update(upgrade_requirements=False):
    '''Deploy a new version'''
    from config.fabric import uwsgi

    checkout_source()
    install_config()
    install_requirements(upgrade_requirements)
    make_symlinks()
    if exists(env.uwsgi_pidfile):
        uwsgi.reload()
    

@task
def cold():
    '''Bootstrap a cold deployment.  This will create a functioning Olive
    install from nothing.'''
    from config.fabric import uwsgi
    from config.fabric import nginx

    setup_virtualenv()
    make_directories()
    checkout_source()
    install_config()
    install_requirements()
    make_symlinks()
    nginx.update_conf()
    uwsgi.update_conf()
    uwsgi.start()
    nginx.start()

@task
def from_workspace():
    local("gnutar -czf %(release_name)s.tar *" % env)
    with prefix("umask 0002"):
        remote("mkdir %(release_path)s" % env)
        put("%(release_name)s.tar" % env, env.release_path)
        with cd(env.release_path):
                remote("tar -zxf %(release_name)s.tar" % env)
                run("rm %(release_name)s.tar" % env)
                remote("rm -f config/local.py" % env)

    local("rm %(release_name)s.tar" % env)
    install_config()
    make_symlinks()
    remote("touch %s" % os.path.join(env.current_path, "WORKSPACE_RELEASE"))


def setup_virtualenv():
    virtualenv_cmd = ["virtualenv",
                      "--distribute",
                      "--no-site-packages",
                      "-p python2.7",
                      "%s" % env.virtualenv_path]

    with path("/seq/annotation/development/tools/python/2.7.1/bin", behavior='prepend'):
        with prefix("umask 0002"):
            remote(" ".join(virtualenv_cmd))


def make_directories():
    with prefix("umask 0002"):
        remote("mkdir %(deploy_to)s" % env)
        with cd(env.deploy_to):
            remote("mkdir %(releases_dir)s" % env)
            remote("mkdir %(shared_dir)s" % env)
            for child in env.shared_children:
                remote("mkdir %s" % os.path.join(env.shared_dir, child))


def checkout_source():
    # TODO: move this to config/git.py
    # TODO: cached copy strategy
    # TODO: submodules
    with prefix("umask 0002"):
        run("git clone %(scm_repository)s %(release_path)s" % env)
        run("rm -rf %s" % os.path.join(env.release_path, ".git"))


def install_requirements(upgrade=False):
    '''Install requirements into pip from config/requirements.pip'''
    command = []
    command.append("pip")
    command.append("install")
    if upgrade:
        command.append("--upgrade")
    command.append("-r config/requirements.pip")

    with prefix("umask 0002"):
        with prefix(env.activate_virtualenv):
            with cd(env.release_path):
                remote(" ".join(command))


def make_symlinks():
    '''Create a 'current' symlink pointing to a release we just checked 
    out, and symlinks within pointing to the shared children'''
    with settings(hide('warnings'), warn_only=True):
        remote("test -L %(current_path)s && rm %(current_path)s" % env)

    remote("ln -s %(release_path)s %(current_path)s" % env)
    for child in env.shared_children:
        remote("ln -s %s %s" % (
            os.path.join(env.shared_path, child),
            os.path.join(env.release_path, child)
        ))
    
def install_config():
    config_dir = os.path.join(env.release_path, "config")

    remote("ln -s %(production)s %(local)s" % {
        "production": os.path.join(config_dir, "production.py"),
        "local": os.path.join(config_dir, "local.py")
    })


