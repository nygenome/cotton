import tempfile
import os

from fabric.api import *

def signal(signal, pidfile):
    if exists(pidfile):
        remote("kill -%s `cat %s`" % (signal, pidfile))
    else:
        print "PID file not found: %s" % pidfile

def remote(command, shell=True, pty=True, combine_stderr=True):
    '''Runs a remote command using either `run()` or `sudo()`.  If
    `env.use_sudo` is exists and is true, `sudo()` is used.  Otherwise,
    `run()` is used.  Using sudo, if `env.sudo_user` is set, the value of
    that expression will be passed to `sudo()` as the `user` parameter.
    Otherwise, the command will be executed without a `user` parameter.'''
    if env.has_key("use_sudo") and env.use_sudo:
        return run(command, shell, pty, combine_stderr)
    else:
        if env.has_key("sudo_user"):
            return sudo(command, shell, pty, combine_stderr, user=env.sudo_user)
        else:
            return sudo(command, shell, pty, combine_stderr)


def generate_conf(template_file_path, interpolation_dict):
    '''Given a template file with python interpolation format strings, render
    a new (temporary) file from interpolating that file with the 
    `interpolation_dict`.  `template_file_path` should be relative to the
    repository root.  Returns the path to the temporary file.'''


    # TODO: move this to some kind of scm.cat_file functionality
    # env.source.cat_file(template_file_path)
    conf_data = local("git show HEAD:%s" % template_file_path, capture=True)
    conf_data = conf_data % interpolation_dict

    conf_file, conf_file_path = tempfile.mkstemp()

    os.write(conf_file, conf_data)
    os.close(conf_file)

    return conf_file_path

