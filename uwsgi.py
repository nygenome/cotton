import os

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from config.fabric.helpers import signal
from config.fabric.helpers import remote


@task
def start():
    '''Start the uwsgi instance.'''
    if exists(env.uwsgi_pidfile):
        abort("uwsgi pidfile already exists: %(uwsgi_pidfile)s" % env)
        
    command = [
        os.path.join(env.servers_path, "bin", "uwsgi"),
        "--yml %(uwsgi_conf)s" % env
    ]
    with cd(env.current_path):
        remote(" ".join(command))
        puts("*** ignore unlink() error - uwsgi quirk as of 0.9.9.2") 


@task
def stop():
    '''Stops the uwsgi instance, if the pidfile is present'''
    signal("INT", env.uwsgi_pidfile)


@task
def restart():
    '''Hard restart of the master uwsgi process'''
    signal("TERM", env.uwsgi_pidfile)

@task
def reload():
    '''Gracefully reload the master uwsgi process and workers'''
    signal("HUP", env.uwsgi_pidfile)

@task
def statistics():
    '''Dump some statistics to the log file'''
    signal("USR1", env.uwsgi_pidfile)

# TODO: log rotation

@task
def update_conf():
    '''Updates the uwsgi conf file on the server, using the template.  Leaves
    a backup file in the uwsgi conf directory with a .bak extension.  Use this
    to roll back if necessary'''
    with prefix("umask 0002"):
        upload_template(env.uwsgi_conf_template,
                        env.uwsgi_conf,
                        context=env,
                        mode=0664)
