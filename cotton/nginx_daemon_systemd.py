import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

"""
This version of nginx_daemon is for use under nygenome CentOS7 systems using systemd
This replaces nginx.py. Use this when you want to control nginx through
systemctl <cmd> nginx rather than working with the executable directly.
"""

def setup(**overrides):
    set_env("nginx_init_script", "systemctl {} nginx", **overrides)
    set_env("nginx_conf_template", os.path.join("config", "servers", "nginx.template.conf"), **overrides)
    set_env("nginx_conf", os.path.join(env.servers_path, "nginx", "conf", "nginx.conf"), **overrides)
    set_env("maintenance_file", os.path.join(env.current_path, "maintenance"), **overrides)
register_setup(setup)

@fab.task
def start(sudo=True):
    '''Start the nginx instance.'''
    nginx_cmd('start', sudo)

@fab.task
def stop(sudo=True):
    '''Stop the nginx instance.'''
    nginx_cmd('stop', sudo)

@fab.task
def reload(sudo=True):
    '''Reload the nginx instance.'''
    nginx_cmd('reload', sudo)

@fab.task
def status(sudo=True):
    '''Print the current status of nginx.'''
    nginx_cmd('status', sudo)

@fab.task
def update_conf(sudo=True):
    '''Regenerate and install the nginx config from the template.'''
    with fab.prefix("umask 0002"):
        upload_template(env.nginx_conf_template,
                        env.nginx_conf,
                        context=env,
                        mode=0664)
    reload(sudo)

def nginx_cmd(cmd, sudo):
    c = [ env.nginx_init_script.format(cmd) ]
    if sudo:
        c.insert(0, 'sudo')
    helpers.remote(' '.join(c))
