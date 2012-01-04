import re

from fabric.api import *
from config.fabric.helpers import remote

@task
def freeze():
    pip("freeze")

@task
def install(package):
    pip("install %s" % package)

@task
def uninstall(package):
    pip("uninstall %s" % package)

def pip(command):
    with prefix("umask 0002"):
        with prefix(env.activate_virtualenv):
            remote("pip %s" % command)

@task
def sanitize(command):
    '''Shell injection protection'''
    if re.search('[;&|\\\'\"]', command):
        raise Exception("Illegal command: %s" % command)

    return command
