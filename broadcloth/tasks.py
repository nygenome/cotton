import os
import time

from fabric.api import task, env, prefix, cd, run, settings, hide

@task
def old_releases(days=60):
    interval = days * 24 * 60 * 60

    cutoff = time.strftime(env.release_time_format, 
                           time.localtime(time.time() - interval))

    with cd(env.releases_path):
        with settings(hide('stdout')):
            result = run("ls -1")

    for line in result.split("\n"):
        if line < cutoff:
            print "%s" % os.path.join(env.releases_path, line)
