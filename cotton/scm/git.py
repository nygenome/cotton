from cotton.scm import SCM

from fabric import api as fab
from fabric.api import env

class Git(SCM):

    def git(self, *commands):
        commands = ' '.join(['git'] + list(commands))
        fab.run(commands)

    def checkout(self, repository, checkout_to, ref=None):

        self.git('clone', repository, checkout_to)
        if ref:
            with fab.cd(checkout_to):
                self.git('checkout', ref)


    def branch_name(self, repository, output_file=None, append=False):
        return self._log_state(command=['status | grep "On branch"'],
                               repository=repository,
                               output_file=output_file,
                               append=append)

    def revision(self, repository, output_file=None, append=False):
        return self._log_state(command=['rev-parse HEAD'],
                               repository=repository,
                               output_file=output_file,
                               append=append)


    def tag_name(self, repository, output_file=None, append=False):
        return self._log_state(command=['describe --tags'],
                               repository=repository,
                               output_file=output_file,
                               append=append)

   
    def _log_state(self, command, repository, output_file=None, append=False):
        with fab.settings(fab.hide('warnings'), warn_only=True):
            stderr_redirect = ['2>', '/dev/null']
            command.extend(stderr_redirect)

            with fab.cd(repository):
                if output_file:
                    redirect = '>'
                    if append:
                        redirect = '>>'
                    command.extend([redirect, output_file])
                return self.git(*command)




