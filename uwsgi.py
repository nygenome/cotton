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
        os.path.join(env.shared_path, 'pids', 'uwsgi.pid')
    ), user=env.app_runner)

