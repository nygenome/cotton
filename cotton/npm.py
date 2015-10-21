from fabric import api as fab
from fabric.api import env

from cotton import helpers
from cotton import set_env, register_setup

def setup(**overrides):
	set_env("npm_root", env.release_path, **overrides)
	set_env("npm_local", False, **overrides)
register_setup(setup)

@fab.task
def install(package, globl=False):
	cmd = [ 'install' ]
	if globl:
		cmd.append('-g')
	cmd.append(package)
	npm(" ".join(cmd))

@fab.task
def install_requirements(globl=False):
	cmd = [ 'install' ]
	if globl:
		cmd.append('-g')
	npm(" ".join(cmd))



def npm(command):
	with fab.prefix("umask 0002"):
		if env.npm_local:
			with fab.lcd(env.npm_root):
				fab.local("npm %s" % command)
		else:
			with fab.cd(env.npm_root):
				helpers.remote("npm %s" % command)