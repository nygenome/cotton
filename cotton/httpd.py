import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

"""
These tasks allow control of an Apache process. We assume your server is
running Apache through the newer systemctl control scheme.
"""

def setup(**overrides):
    set_env("httpd_init_script", "systemctl", **overrides)
    set_env("httpd_service_name", "httpd.service", **overrides)
    set_env("httpd_conf_template", os.path.join("config", "servers", "httpd.template.conf"), **overrides)
    set_env("httpd_conf_dir", os.path.join(env.servers_path, "httpd"), **overrides)
    set_env("httpd_conf", os.path.join(env.httpd_conf_dir, "httpd.conf"), **overrides)
    set_env("maintenance_file", os.path.join(env.httpd_conf_dir, "maintenance.enable"), **overrides)
register_setup(setup)

@fab.task
def start(sudo=True):
    '''Start the httpd instance.'''
    httpd_cmd('start', sudo)

@fab.task
def stop(sudo=True):
    '''Stop the httpd instance.'''
    httpd_cmd('stop', sudo)

@fab.task
def restart(sudo=True):
    '''Stop the httpd instance.'''
    httpd_cmd('restart', sudo)

@fab.task
def reload(sudo=True):
    '''Reload the httpd instance.'''
    httpd_cmd('reload', sudo)

@fab.task
def status(sudo=True):
    '''Print the current status of httpd.'''
    httpd_cmd('status', sudo)

@fab.task
def update_conf(sudo=True, reload_httpd=False):
    '''Regenerate and install the httpd config from the template.'''
    with fab.prefix("umask 0002"):
        upload_template(env.httpd_conf_template,
                        env.httpd_conf,
                        context=env,
                        mode=0664)

    if reload_httpd:
        reload(sudo)

def httpd_cmd(cmd, sudo):
    c = [ env.httpd_init_script, cmd, env.httpd_service_name ]
    if sudo:
        c.insert(0, 'sudo')
    helpers.remote(' '.join(c))
