from cotton.scm import Git

from fabric import api as fab
from fabric.api import env

class BroadGit(Git):

    def git(self, *commands):
        with fab.prefix(". /broad/tools/scripts/useuse && use Git-1.7"):
            with fab.prefix("umask 0002"):
                super(BroadGit, self).git(*commands)

