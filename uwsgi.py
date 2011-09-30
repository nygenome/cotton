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
        

    # TODO: do we want to version this config and nginx's 
    # config as templates? see fabric.contrib.files.upload_template
    command = [
        os.path.join(env.servers_path, "bin", "uwsgi"),
        "--yml %(uwsgi_conf)s" % env
        # # "--http :8080", # bypass nginx, run directly on port 8080
        # "--socket %(uwsgi_socket)s" % env,
        # "--daemonize %s" % os.path.join(env.shared_path, "log", "uwsgi.log"),
        # "--virtualenv %(virtualenv_path)s" % env,
        # "--chdir %(current_path)s" % env,
        # "--logdate",
        # "--master",
        # "--pidfile %(uwsgi_pidfile)s" % env,
        # "--vacuum",
        # "--module martini",
        # "--callable app"
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

# TODO: log rotation

@task
def update_conf():
    '''Updates the uwsgi conf file on the server, using the template.  Leaves
    a backup file in the uwsgi conf directory with a .bak extension.  Use this
    to roll back if necessary'''
    upload_template(env.uwsgi_conf_template,
                    env.uwsgi_conf,
                    context=env,
                    mode=0664)
