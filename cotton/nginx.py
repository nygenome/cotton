import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
    set_env("nginx_pidfile", os.path.join(env.shared_path, "pids", "nginx.pid"), **overrides)
    set_env("nginx_error_log", os.path.join(env.shared_path, "logs", "nginx.error.log"), **overrides)
    set_env("nginx_access_log", os.path.join(env.shared_path, "logs", "nginx.access.log"), **overrides)
    set_env("nginx_conf_template", os.path.join("config", "servers", "nginx.template.conf"), **overrides)
    set_env("nginx_conf", os.path.join(env.servers_path, "nginx", "conf", "nginx.conf"), **overrides)
    set_env("maintenance_file", os.path.join(env.current_path, "maintenance"), **overrides)
register_setup(setup)

@fab.task
def start():
    '''Start the nginx instance.'''
    if running():
        fab.abort("nginx pidfile already exists: %(host)s:%(nginx_pidfile)s" % env)

    command = [
        os.path.join(env.servers_path, "bin", "nginx"),
        "-c %(nginx_conf)s" % env,
    ]
    with fab.cd(env.current_path):
        helpers.remote(" ".join(command))

@fab.task
def stop(kill=False):
    sig = "QUIT"
    if kill:
        sig = "KILL"

    helpers.signal(sig, env.nginx_pidfile)

@fab.task
def reload():
    helpers.signal("HUP", env.nginx_pidfile)

@fab.task
def update_conf():
    with fab.prefix("umask 0002"):
        upload_template(env.nginx_conf_template,
                        env.nginx_conf,
                        context=env,
                        mode=0664)

def running():
    if exists(env.nginx_pidfile):
        return True
    else:
        return False

