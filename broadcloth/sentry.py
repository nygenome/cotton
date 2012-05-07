import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import upload_template

from broadcloth import helpers
from broadcloth import set_env, register_setup

def setup(**overrides):
    set_env("sentry_root", os.path.join(env.servers_path, "sentry"), **overrides)
    set_env("sentry_virtualenv_path", os.path.join(env.sentry_root, ".virtualenv"), **overrides)
    set_env("sentry_activate_virtualenv", "source %s" % os.path.join(
        env.sentry_virtualenv_path, "bin", "activate"), **overrides)
    set_env("sentry_conf_template", os.path.join("config", "servers",
                                                 "sentry_conf.template.py"), **overrides)
    set_env("sentry_conf", os.path.join(env.sentry_root, "sentry_conf.py"), **overrides)
    set_env("sentry_host", 'olive-staging', **overrides)
    set_env("sentry_port", 9000, **overrides)
register_setup(setup)

@fab.task
def start():
    sentry("start --daemon")

@fab.task
def stop():
    sentry("stop")

@fab.task
def restart():
    sentry("restart")

@fab.task 
def update_schema():
    sentry("upgrade")

@fab.task
def upgrade_sentry():
    '''Upgrade sentry to the latest version.  Sentry must be stopped first.'''
    # stop sentry.  if it stopped, then start again post upgrade
    with fab.prefix("umask 0002"):
        with fab.prefix(env.sentry_activate_virtualenv):
            helpers.remote("pip install --upgrade sentry")


@fab.task
def install():
    '''Installs sentry, if it's not installed in the requested environment'''
    from broadcloth import deploy
    helpers.makedirs(env.sentry_root)
    deploy.setup_virtualenv(env.sentry_virtualenv_path)

    upgrade_sentry()
    update_conf()
    update_schema()

def sentry(command):
    with fab.prefix("umask 0002"):
        with fab.prefix(env.sentry_activate_virtualenv):
            helpers.remote("sentry %s --config=%s" % (command, env.sentry_conf))

@fab.task
def update_conf():
    with fab.prefix("umask 0002"):
        upload_template(env.sentry_conf_template,
                        env.sentry_conf,
                        context=env,
                        mode=0664)


