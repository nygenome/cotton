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

def install_requirements(release_path, *command_line_flags):
    '''
    Install requirements into the virtualenv from the file specified in
    `env.requirements_file`
    '''
    command = []
    command.append("install")
    command.extend(command_line_flags)
    command.append("-r %s" % env.requirements_file)

    with fab.cd(release_path):
        pip(' '.join(command))

def freeze_requirements(release_path):
    '''
    Freeze the current virtualenv into the file specified in
    `env.requirements_file`.  This is helpful when performing a
    dependency-safe rollback.
    '''
    command = [
        'freeze',
        "> %s" % env.requirements_file,    
    ]

    with fab.cd(release_path):
        pip(' '.join(command))
