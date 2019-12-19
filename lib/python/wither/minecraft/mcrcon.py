#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import sys

import subprocess

## {{{ class MCRcon
class MCRcon:

  addr = None
  port = -1
  password = None

  ## {{{ MCRcon.__init(addr, port, password)
  def __init__(self, addr=None, port=None, password=None):
    self.addr = addr
    self.port = port
    self.password = password

    if addr:
      os.environ['MCRCON_HOST'] = addr
    if port:
      os.environ['MCRCON_PORT'] = str(port)
    if password:
      os.environ['MCRCON_PASS'] = password
  ## }}}

  ## {{{ _wrap(cmd)
  def _wrap(self, cmd):
    return subprocess.check_output(['mcrcon', '-c', cmd], universal_newlines=True)
  ## }}}

  ## {{{ list()
  def list(self):
    return self._wrap('list').strip()
  ## }}}

## class MCRcon }}}

##
# vim: ts=2 sw=2 et fdm=marker :
##
