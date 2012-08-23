
class SCM(object):

    def checkout(self, repository, checkout_to, branch=None):
        raise NotImplementedError

    def branch_name(self, checkout_to, output_file=None, append=False):
        raise NotImplementedError

    def revision(self, checkout_to, output_file=None, append=False):
        raise NotImplementedError




