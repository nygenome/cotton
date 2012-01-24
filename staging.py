import os

from fabric.api import *

@task
def staging():
    '''ENVIRONMENTAL.  Execute subsequent tasks in the 'staging'
    environment
    '''

    from fabfile import setup_env
    setup_env(
        hosts=['olive-staging'],
        app_root="/seq/a2e0/apps/staging/olive",
        configuration_name="staging",
    )
