import os

from fabric.api import task, env, prefix
from fabric.contrib.files import upload_template
from broadcloth.helpers import remote
from broadcloth.helpers import makedirs

@task
def start():
    sentry("start --daemon")

@task
def stop():
    sentry("stop")

@task
def restart():
    sentry("restart")

@task 
def update_schema():
    sentry("upgrade")

@task
def upgrade_sentry():
    '''Upgrade sentry to the latest version.  Sentry must be stopped first.'''
    # stop sentry.  if it stopped, then start again post upgrade
    with prefix("umask 0002"):
        with prefix(env.sentry_activate_virtualenv):
            remote("pip install --upgrade sentry")


@task
def install():
    '''Installs sentry, if it's not installed in the requested environment'''
    from broadcloth import deploy
    makedirs(env.sentry_root)
    deploy.setup_virtualenv(env.sentry_virtualenv_path)

    upgrade_sentry()
    update_conf()
    update_schema()

def sentry(command):
    with prefix("umask 0002"):
        with prefix(env.sentry_activate_virtualenv):
            remote("sentry %s --config=%s" % (command, env.sentry_conf))

@task
def update_conf():
    with prefix("umask 0002"):
        upload_template(env.sentry_conf_template,
                        env.sentry_conf,
                        context=env,
                        mode=0664)
