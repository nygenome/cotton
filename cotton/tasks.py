import os
import time

from fabric import api as fab
from fabric.api import env

from cotton import helpers


@fab.task 
def whereami():
    '''Displays some information about where this task is running.'''
    with fab.cd(env.current_path):
        fab.run("uname -n; pwd -P; ls")

@fab.task
def old_releases(days=60, delete=False):
    interval = days * 24 * 60 * 60

    cutoff = time.strftime(env.release_time_format, 
                           time.localtime(time.time() - interval))

    with fab.cd(env.releases_path):
        with fab.settings(fab.hide('stdout')):
            result = fab.run("ls -1")

    for line in result.split("\n"):
        if line < cutoff:
            path = os.path.join(env.releases_path, line) 
            if delete:
                fab.run("rm -rf %s" % path)
            else:
                print path
