import os

from fabric.api import task, env, prefix
from fabric.contrib.files import upload_template
from config.fabric.helpers import remote
from config.fabric.helpers import makedirs

@task
def start():
    sentry("start --config=%(sentry_config)s" % env)

@task
def stop():
    sentry("stop")

@task
def restart():
    sentry("restart")

@task
def install():
    '''Installs sentry, if it's not installed in the requested environment'''
    from config.fabric import deploy
    makedirs(env.sentry_root)
    deploy.setup_virtualenv(env.sentry_virtualenv_path)
    with prefix("umask 0002"):
        with prefix(env.sentry_activate_virtualenv):
            remote("pip install sentry")

    update_conf()

def sentry(command):
    with prefix("umask 0002"):
        with prefix(env.sentry_activate_virtualenv):
            remote("sentry %s" % command)

@task
def update_conf():
    with prefix("umask 0002"):
        upload_template(env.sentry_conf_template,
                        env.sentry_conf,
                        context=env,
                        mode=0664)
