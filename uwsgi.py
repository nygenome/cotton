import os

from fabric.api import *
from fabric.contrib.files import exists
from config.fabric.helpers import signal

@task
def start(warn_on_already_started=False):
    '''Start the uwsgi instance.'''
    with settings(warn_only=warn_on_already_started):
        if exists(env.uwsgi_pidfile):
            abort("uwsgi pidfile already exists: %(uwsgi_pidfile)s" % env)
        

    # TODO: do we want to version this config and nginx's 
    # config as templates? see fabric.contrib.files.upload_template
    command = [
        os.path.join(env.servers_path, "uwsgi"),
        # "--http :8080", # bypass nginx, run directly on port 8080
        "--socket %(uwsgi_socket)s" % env,
        "--daemonize %s" % os.path.join(env.shared_path, "log", "uwsgi.log"),
        "--virtualenv %(virtualenv_path)s" % env,
        "--chdir %(current_path)s" % env,
        "--logdate",
        "--master",
        "--pidfile %(uwsgi_pidfile)s" % env,
        "--vacuum",
        "--module martini",
        "--callable app"
    ]
    with cd(env.current_path):
        remote(" ".join(command))


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

def running():
    '''Best guess at whether or not this process is running'''
    if exists(env.uwsgi_pidfile):
        with settings(hide("warnings"), warn_only=True):
            result = signal("0", env.uwsgi_pidfile)
            if result and result.succeeded:
                return True

    return False

# TODO: rotate logs task?

