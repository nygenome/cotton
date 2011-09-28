import os

from fabric.api import *

@task
def start():
    command = [
        os.path.join(env.servers_path, "uwsgi"),
        "--http :8080",
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
    with settings(hide('warnings'), warn_only=True):
        if sudo("test -e %(uwsgi_pidfile)s" % env, user=env.app_runner).failed:
            print "PID file not found: %(uwsgi_pidfile)s" % env
            return

    signal("INT")


@task
def restart():
    stop()
    start()

@task
def statistics():
    signal("USR1")

def signal(signal):
    sudo("kill -%s `cat %s`" % (
        signal,
        env.uwsgi_pidfile
    ), user=env.app_runner)

