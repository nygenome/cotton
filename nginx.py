import os

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from config.fabric.helpers import signal
from config.fabric.helpers import remote

@task
def start():
    '''Start the nginx instance.'''
    if exists(env.nginx_pidfile):
        abort("uwsgi pidfile already exists: %(host)s:%(nginx_pidfile)s" % env)
        

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
    upload_template(env.nginx_conf_template,
                    env.nginx_conf,
                    context=env,
                    mode=0664)
