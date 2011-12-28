import os

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from config.fabric.helpers import signal
from config.fabric.helpers import remote


@task
def start():
    '''Start the redis-server instance.'''
    if exists(env.redis_pidfile):
        abort("redis-server pidfile already exists: %(redis_pidfile)s" % env)
        
    command = [
        os.path.join(env.servers_path, "bin", "redis-server"),
        env.redis_conf
    ]
    with cd(env.current_path):
        remote(" ".join(command))


@task
def stop():
    '''Stops the redis-server instance, if the pidfile is present'''
    signal("TERM", env.redis_pidfile)


@task
def restart():
    '''Hard restart of the master redis-server process'''
    stop()
    start()

# TODO: log rotation

@task
def update_conf():
    '''Updates the redis conf file on the server, using the template.  Leaves
    a backup file in the redis conf directory with a .bak extension.'''
    with prefix("umask 0002"):
        upload_template(env.redis_conf_template,
                        env.redis_conf,
                        context=env,
                        mode=0664)
