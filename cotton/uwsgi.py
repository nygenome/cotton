import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
    set_env("uwsgi_pidfile", os.path.join(env.shared_path, "pids", "uwsgi.pid"), **overrides)
    set_env("uwsgi_logfile", os.path.join(env.shared_path, "logs", "uwsgi.log"), **overrides)
    set_env("uwsgi_socket", os.path.join(env.shared_path, "sock", "uwsgi.sock"), **overrides)
    set_env("uwsgi_conf_template", os.path.join("config", "servers", "uwsgi.template.yml"), **overrides)
    set_env("uwsgi_conf_path", os.path.join(env.servers_path, "uwsgi", "conf"), **overrides)
register_setup(setup)

PCRE = "/seq/a2e0/tools/util/pcre/pcre-8.30/lib"

@fab.task
def start(command_prefix=None, linked_libraries=[]):
    '''Start the uwsgi instance.'''
    # command_prefix : environmental commands like dotkit (local)
    # linked_libraries : library prepending due to sudo-shell (remote)

    if running():
        fab.abort("uwsgi pidfile already exists: %(uwsgi_pidfile)s" % env)

    # TODO: ARRRRRG you can't source files in sudo
    # As long as we're using (0.9,1.1,1.2) built with our custom-build pcre
    # library, we need to tell uwsgi where to find this
    linked_libraries.append(PCRE)
    command = [
        "LD_LIBRARY_PATH=%s" % ":".join(linked_libraries),
        os.path.join(env.servers_path, "bin", "uwsgi"),
        "--yaml %s" % os.path.join(env.uwsgi_conf_path, "uwsgi.yml")
    ]
    if command_prefix:
        command.insert(0, command_prefix + " && ")
    with fab.cd(env.current_path):
        with fab.prefix("umask 0002"):
            helpers.remote(" ".join(command))
            fab.puts("*** speakeasy note: ignore unlink() error for pre 1.2 uwsgi.")


@fab.task
def stop():
    '''Stops the uwsgi instance, if the pidfile is present'''
    helpers.signal("INT", env.uwsgi_pidfile)


@fab.task
def restart():
    '''Hard restart of the master uwsgi process'''
    helpers.signal("TERM", env.uwsgi_pidfile)

@fab.task
def reload():
    '''Gracefully reload the master uwsgi process and workers'''
    helpers.signal("HUP", env.uwsgi_pidfile)

@fab.task
def statistics():
    '''Dump some statistics to the log file'''
    helpers.signal("USR1", env.uwsgi_pidfile)

# TODO: log rotation

@fab.task
def update_conf():
    '''Updates the uwsgi conf file on the server, using the template.  Leaves
    a backup file in the uwsgi conf directory with a .bak extension.  Use this
    to roll back if necessary'''
    with fab.prefix("umask 0002"):
        helpers.remote("mkdir -p %s" % env.uwsgi_conf_path)
        upload_template(env.uwsgi_conf_template,
                        os.path.join(env.uwsgi_conf_path, "uwsgi.yml"),
                        context=env,
                        mode=0664)

def running():
    if exists(env.uwsgi_pidfile):
        return True
    else:
        return False

