import re

from fabric import api as fab
from fabric.api import env

from cotton import helpers

@fab.task
def freeze():
    pip("freeze")

@fab.task
def install(package):
    pip("install %s" % package)

@fab.task
def uninstall(package):
    pip("uninstall %s" % package)

def pip(command):
    with fab.prefix("umask 0002"):
        with fab.prefix(env.activate_virtualenv):
            helpers.remote("pip %s" % command)

def sanitize(command):
    '''Shell injection protection'''
    if re.search('[;&|\\\'\"]', command):
        raise Exception("Illegal command: %s" % command)

    return command
