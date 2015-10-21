import re

from fabric import api as fab
from fabric.api import env

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
    set_env("pip_index", None, **overrides)
register_setup(setup)

@fab.task
def freeze():
    pip("freeze")

@fab.task
def install(package):
    if env.pip_index is None:
        cmd = "install "
    else:
        cmd = "install -i %s" % env.pip_index
    pip("%s %s" % (cmd, package))

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
    install_from_file(release_path, env.requirements_file, 
                      *command_line_flags)

def install_from_file(release_path, filepath, *command_line_flags):
    '''
    Install requirements into the virtualenv from the file specified.
    '''
    command = []
    command.append("install")
    command.extend(command_line_flags)
    if env.pip_index is not None:
        command.extend(['-i', env.pip_index])
    command.append("-r %s" % filepath)

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
