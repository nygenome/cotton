import os

from fabric.api import *
from config.fabric.helpers import signal

@task
def start():
    pass

@task
def stop():
    pass

@task
def restart():
    pass

@task
def reload():
    signal("HUP", env.nginx_pidfile)

