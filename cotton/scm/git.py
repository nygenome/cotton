from cotton.scm import SCM

from fabric import api as fab
from fabric.api import env

class Git(SCM):

    def git(self, *commands):
        commands = ' '.join(['git'] + list(commands))
        fab.run(commands)

    def checkout(self, repository, checkout_to, branch=None):
        self.git('clone', repository, checkout_to)
        if branch:
            with fab.cd(checkout_to):
                self.git('checkout -b deploy', "origin/%s" % branch)



    def branch_name(self, checkout_to, output_file=None, append=False):
        command = ['status | grep "On branch"']
        with fab.cd(checkout_to):
            if output_file:
                redirect = '>'
                if append:
                    redirect = '>>'
                command.extend([redirect, output_file])
            return self.git(*command)

    def revision(self, checkout_to, output_file=None, append=False):
        command = ['rev-parse HEAD']
        with fab.cd(checkout_to):
            if output_file:
                redirect = '>'
                if append:
                    redirect = '>>'
                command.extend([redirect, output_file])
            return self.git(*command)




