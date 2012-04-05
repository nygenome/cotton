import os

from fabric.api import *

@task
def staging():
    '''ENVIRONMENTAL.  Sets 'staging' environment as target for task
    execution.
    '''

    from fabfile import setup_env
    setup_env(
        hosts=['olive-staging'],
        app_root="/seq/a2e0/apps/staging/olive",
        configuration_name="staging",
    )

@task
def production():
    '''ENVIRONMENTAL.  Sets 'production' environment as target for task
    execution.
    '''

    from fabfile import setup_env
    setup_env(
        hosts=['olive-prod'],
        app_root="/seq/a2e0/apps/production/olive",
        configuration_name="production",
    )
