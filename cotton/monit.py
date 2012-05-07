import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
    set_env("monit_root", os.path.join(env.servers_path, 'monit'), **overrides)
    set_env("monit_conf_template", os.path.join("config", "servers",
                                                 "monitrc.template"), **overrides)
    set_env("monit_conf", os.path.join(env.servers_path, 'monit', 'etc', 'monitrc'), **overrides)
register_setup(setup)

default_location = "http://mmonit.com/monit/dist/monit-5.3.2.tar.gz"

@fab.task
def install(source=None):
    # TODO: support source being a local file- test for file exists,
    # then assume url
    if not source:
        source = default_location

    # move to fabfile?
    src_dir = os.path.join(env.servers_path, 'src')
    install_to = env.monit_root
    
    with fab.prefix("umask 0002"):
        fab.run("mkdir -p %s" % src_dir)
        fab.run("mkdir -p %s" % install_to)

        archive = os.path.basename(source)

        with fab.cd(src_dir):
            fab.run("curl -O %s" % source)
            fab.run("tar -xzf %s" % archive)
            
        src_dir = os.path.join(src_dir, archive[:-len('.tar.gz')])
        with fab.cd(src_dir):
            fab.run("./configure --prefix=%s" % install_to)
            fab.run("make")
            fab.run("make install")

        with fab.cd(os.path.join(env.servers_path, 'bin')):
            fab.run("ln -s %s" % os.path.join(env.monit_root, 'bin', 'monit'))

@fab.task
def start():
    monit()

@fab.task
def stop():
    monit("quit")

@fab.task
def status():
    monit("status")


def monit(command=None):
    with fab.prefix("umask 0002"):
        c = [os.path.join(env.monit_root, 'bin', 'monit')]
        if command:
            c.append(command)
        helpers.remote(' '.join(c))

@fab.task
def update_conf():
    with fab.prefix("umask 0002"):
        helpers.makedirs(os.path.dirname(env.monit_conf))
        helpers.remote("mv %(monit_conf)s{,.bak}" % env)
        upload_template(env.monit_conf_template,
                        env.monit_conf,
                        context=env,
                        backup=False,
                        mode=0664)
        helpers.remote("mv %(monit_conf)s %(monit_conf)s.tmp" % env)
        helpers.remote("cp %(monit_conf)s.tmp %(monit_conf)s" % env)
        helpers.remote("rm %(monit_conf)s.tmp" % env)
        helpers.remote("chmod 700 %(monit_conf)s" % env)





