import os
import time

from fabric.api import task, local

@task
def clean():
    '''Remove .pyc files in local workspace'''
    local('find . -name \*.pyc | xargs rm')
