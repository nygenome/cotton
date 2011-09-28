import os

from fabric.api import *

@task(default=True)
def update(upgrade_requirements=False):
    '''Deploy a new version'''
    from config.fabric import uwsgi

    checkout_source()
    install_requirements(upgrade_requirements)
    # TODO: nginx.maintenance()
    uwsgi.stop()
    make_symlinks()
    uwsgi.start()
    # TODO: nginx.unmaintenance()
    

@task
def cold():
    '''Bootstrap a cold deployment.  This will create a functioning Olive
    install from nothing.'''
    from config.fabric import uwsgi

    setup_virtualenv()
    make_directories()
    checkout_source()
    install_requirements()
    make_symlinks()
    uwsgi.start()

@task
def from_workspace():
    local("gnutar -czf %(release_name)s.tar *" % env)
    with prefix("umask 0002"):
        sudo("mkdir %(release_path)s" % env, user=env.app_runner)
        put("%(release_name)s.tar" % env, env.release_path)
        with cd(env.release_path):
                sudo("tar -zxf %(release_name)s.tar" % env, user=env.app_runner)
                run("rm %(release_name)s.tar" % env)

    local("rm %(release_name)s.tar" % env)
    make_symlinks()


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
                sudo(" ".join(command), user=env.app_runner)


def make_symlinks():
    '''Create a 'current' symlink pointing to a release we just checked 
    out, and symlinks within pointing to the shared children'''
    with settings(hide('warnings'), warn_only=True):
        sudo("test -L %(current_path)s && rm %(current_path)s" % env, user=env.app_runner)

    sudo("ln -s %(release_path)s %(current_path)s" % env, user=env.app_runner)
    for child in env.shared_children:
        sudo("ln -s %s %s" % (
            os.path.join(env.shared_path, child),
            os.path.join(env.release_path, child)
        ), user=env.app_runner)



