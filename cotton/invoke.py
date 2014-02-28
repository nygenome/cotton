'''
Fabric task to run invoke tasks in a remote environment
'''

import os

from fabric import api as fab
from fabric.api import env

from fabric.contrib.files import exists
from fabric.contrib.files import upload_template

from cotton import helpers


@fab.task(default=True)
def run(task, sudo=None, shell=True, pty=True, combine_stderr=True):
    '''
    Runs an invoke task in a remote environment.  Pass the task as a string
    WITH argument parameters.

    If sudo is desired, pass either a string username, or True to respect the
    sudo conventions outlined in `cotton.helpers.remote()`.
    '''
    command = ' '.join([
        'invoke',
        task,
    ])

    with fab.prefix("umask 0002"):
        with fab.prefix(env.activate_virtualenv):
            with fab.cd(env.current_path):

                if isinstance(sudo, basestring):
                    return fab.sudo(
                        command,
                        shell,
                        pty,
                        combine_stderr,
                        user=sudo
                    )
                elif sudo:
                    return helpers.remote(
                        command,
                        shell=shell,
                        pty=pty,
                        combine_stderr=combine_stderr
                    )
                else:
                    return fab.run(command, shell, pty, combine_stderr)


