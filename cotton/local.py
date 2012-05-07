from fabric import api as fab

@fab.task
def clean():
    '''Remove .pyc files in local workspace'''
    fab.local('find . -name \*.pyc | xargs rm')
