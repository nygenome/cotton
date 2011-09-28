import os

from fabric.api import *

@task
def start():
    '''Start the uwsgi instance.'''
    command = [
        os.path.join(env.servers_path, "uwsgi"),
        # "--http :8080", # bypass nginx, run directly on port 8080
        "--socket %(uwsgi_socket)s" % env,
        "--daemonize %s" % os.path.join(env.shared_path, "log", "uwsgi.log"),
        "--virtualenv %(virtualenv_path)s" % env,
        "--chdir %(current_path)s" % env,
        "--logdate",
        "--pidfile %(uwsgi_pidfile)s" % env,
        "--vacuum",
        "--module martini",
        "--callable app"
    ]
    with cd(env.current_path):
        sudo(" ".join(command), user=env.app_runner)


@task
def stop():
    '''Stops the uwsgi instance, if the pidfile is present'''
    with settings(hide('warnings'), warn_only=True):
        if sudo("test -e %(uwsgi_pidfile)s" % env, user=env.app_runner).failed:
            print "PID file not found: %(uwsgi_pidfile)s" % env
            return

    signal("INT")


@task
def restart():
    '''Gracefully reload the master uwsgi process and workers'''
    signal("HUP")

@task
def statistics():
    signal("USR1")

# TODO: rotate logs task?

def signal(signal):
    sudo("kill -%s `cat %s`" % (
        signal,
        env.uwsgi_pidfile
    ), user=env.app_runner)

