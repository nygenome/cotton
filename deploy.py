import os

from fabric.api import *

@task(default=True)
def update(upgrade_requirements=False):
    from config.fabric import server

    server.stop()
    # wsgi.stop()
    # nginx.maintenance()
    # TODO: only stop servers when changing the symlink
    checkout_source()
    install_requirements(upgrade_requirements)
    make_symlink()
    server.start()
    

@task
def cold():
    '''Bootstrap a cold deployment.  This will create a functioning Olive
    install from nothing.'''
    from config.fabric import server

    setup_virtualenv()
    make_directories()
    checkout_source()
    install_requirements()
    make_symlink()
    server.start()


def setup_virtualenv():
    virtualenv_cmd = ["virtualenv",
                      "--distribute",
                      "--no-site-packages",
                      "-p python2.7",
                      "%s" % env.virtualenv_path]

    with path("/seq/annotation/development/tools/python/2.7.1/bin", behavior='prepend'):
        with prefix("umask 0002"):
            sudo(" ".join(virtualenv_cmd), user=env.app_runner)


def make_directories():
    with prefix("umask 0002"):
        sudo("mkdir %(deploy_to)s" % env, user=env.app_runner)
        with cd(env.deploy_to):
            sudo("mkdir %(releases_dir)s" % env, user=env.app_runner)
            sudo("mkdir %(shared_dir)s" % env, user=env.app_runner)
            for child in env.shared_children:
                sudo("mkdir %s" % os.path.join(env.shared_dir, child),
                     user=env.app_runner)

def checkout_source():
    # TODO: move this to config/git.py
    # TODO: cached copy strategy
    # TODO: submodules
    destination = os.path.join(env.releases_path, env.release_name)
    with prefix("umask 0002"):
        run("git clone %s %s" % (env.scm_repository, destination))
        run("rm -rf %s" % os.path.join(destination, ".git"))


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
                sudo(" ".join(command), user=env.app_runner)


def make_symlink():
    '''Create a 'current' symlink pointing to a release we just checked out'''
    with cd(env.deploy_to):
        with settings(hide('warnings'), warn_only=True):
            sudo("test -L %(current_dir)s && rm %(current_dir)s" % env, user=env.app_runner)

        sudo("ln -s %s %s" % (os.path.join(env.releases_dir, env.release_name),
                              env.current_dir), user=env.app_runner)
