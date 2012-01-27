import tempfile
import os
import errno

from fabric.api import *
from fabric.contrib.files import exists

def signal(signal, pidfile):
    if exists(pidfile):
        return remote("kill -%s `cat %s`" % (signal, pidfile))
    else:
        # TODO: should this abort?
        abort("PID file not found: %s" % pidfile)

def remote(command, shell=True, pty=True, combine_stderr=True):
    '''Runs a remote command using either `run()` or `sudo()`.  If
    `env.use_sudo` is exists and is true, `sudo()` is used.  Otherwise,
    `run()` is used.  Using sudo, if `env.sudo_user` is set, the value of
    that expression will be passed to `sudo()` as the `user` parameter.
    Otherwise, the command will be executed without a `user` parameter.'''
    if not (env.has_key("use_sudo") and env.use_sudo):
        return run(command, shell, pty, combine_stderr)
    else:
        if env.has_key("sudo_user"):
            return sudo(command, shell, pty, combine_stderr, user=env.sudo_user)
        else:
            return sudo(command, shell, pty, combine_stderr)

def makedirs(path):
    '''mkdir -p functionality'''
    import os, errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise exc
