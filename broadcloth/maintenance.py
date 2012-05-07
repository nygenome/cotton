from fabric import api as fab
from fabric.api import env

from broadcloth.deploy import authenticate

@fab.task
def enable():
    '''Return a maintenance page (and 503 status) in response to all
    requests
    '''
    authenticate()
    with fab.prefix("umask 0002"):
        fab.run("touch %(maintenance_file)s" % env)

@fab.task
def disable():
    '''Remove maintenance page and respond to requests normally'''
    authenticate()
    fab.run("rm -f %(maintenance_file)s" % env)
    
