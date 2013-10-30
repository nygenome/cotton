"""
System for triggering optional application-wide alert behavior
without application redeployment.

Only one such message can be in effect at any time. Each subsequent
call overwrites whatever was there. called via::

    fab production alert.warning:msg='Zombie invasion between Monday and Tuesday.'

To clear the application of all messages:

    fab production alert.clear

Please avoid the following strings in these messages:

- comma (due to fabric argument parsing)
- double-quote (due to shell command)
- double colons (due to native severity parsing)
- other punctuation that cause general hilarity in shells (`!*$)

This module stores its state in ``alert.txt`` in your application's
deployment root. This ensures that its message is preserved across
deployments.

This facility requires the host application to handle the content of
``alert.txt`` appropriately; see :mod:`icecube/alert.py` for an
example.
"""

import os
import os.path

from fabric import api as fab
from fabric.api import env

from cotton.deploy import authenticate

from cotton import set_env, register_setup

def setup(**overrides):
    # lands in /path/to/app/codebase/alert.txt
    set_env("alert_file", os.path.join(env.deploy_to, "alert.txt"), **overrides)
register_setup(setup)


DELIM = "::"

@fab.task
def clear():
    '''clear all alert messages'''
    authenticate()
    fab.run("rm -f %(alert_file)s" % env)


def _write_alert(level, msg):
    authenticate()
    with fab.prefix("umask 0002"):
        with open(env['alert_file'], "w") as fout:
            fout.write(DELIM.join([level, msg]))

@fab.task
def notice(msg):
    '''persistent info message, call with :msg="(twss)"'''
    _write_alert("notice", msg)

@fab.task
def error(msg):
    '''persistent error message, call with :msg="(tableflip)"'''
    _write_alert("error", msg)

@fab.task
def warning(msg):
    '''persistent warn message, call with :msg="(ohcrap)"'''
    _write_alert("warning", msg)

@fab.task
def success(msg):
    '''persistent good message, call with :msg="(fuckyeah)"'''
    _write_alert("success", msg)
