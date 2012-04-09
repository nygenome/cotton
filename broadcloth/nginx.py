import os

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from broadcloth.helpers import signal
from broadcloth.helpers import remote
from broadcloth import set_env, register_setup

def setup(**overrides):
    set_env("nginx_pidfile", os.path.join(env.shared_path, "pids", "nginx.pid"), **overrides)
    set_env("nginx_error_log", os.path.join(env.shared_path, "logs", "nginx.error.log"), **overrides)
    set_env("nginx_access_log", os.path.join(env.shared_path, "logs", "nginx.access.log"), **overrides)
    set_env("nginx_conf_template", os.path.join("config", "servers", "nginx.template.conf"), **overrides)
    set_env("nginx_conf", os.path.join(env.servers_path, "nginx", "conf", "nginx.conf"), **overrides)
    set_env("maintenance_file", os.path.join(env.current_path, "maintenance"), **overrides)
register_setup(setup)

@task
def start():
    '''Start the nginx instance.'''
    if exists(env.nginx_pidfile):
        abort("nginx pidfile already exists: %(host)s:%(nginx_pidfile)s" % env)

    command = [
        os.path.join(env.servers_path, "bin", "nginx"),
        "-c %(nginx_conf)s" % env,
    ]
    with cd(env.current_path):
        remote(" ".join(command))

@task
def stop(kill=False):
    sig = "QUIT"
    if kill:
        sig = "KILL"

    signal(sig, env.nginx_pidfile)

@task
def reload():
    signal("HUP", env.nginx_pidfile)

@task
def update_conf():
    with prefix("umask 0002"):
        upload_template(env.nginx_conf_template,
                        env.nginx_conf,
                        context=env,
                        mode=0664)
