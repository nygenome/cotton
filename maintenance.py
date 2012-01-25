from config.fabric.deploy import authenticate

from fabric.api import env, task, run, prefix

@task
def enable():
    '''Return a maintenance page (and 503 status) in response to all
    requests
    '''
    authenticate()
    with prefix("umask 0002"):
        run("touch %(maintenance_file)s" % env)

@task
def disable():
    '''Remove maintenance page and respond to requests normally'''
    authenticate()
    run("rm -f %(maintenance_file)s" % env)
    
