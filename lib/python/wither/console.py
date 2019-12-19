#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import sys

from datetime import datetime

# Script filename
SCRIPT_NAME = os.path.basename(sys.argvp[0])

## {{{ notice(msg, [prefix_timestamp])
def notice(msg, prefix_timestamp=True):
  prefix = ''
  if prefix_timestamp:
    prefix = '[{0}] '.format(datetime.now().strftime('%F %T'))

  sys.stdout.write('{0}{1}\n'.format(prefix, msg))
  sys.stdout.flush()
## }}}

## {{{ error(msg)
def error(msg):
  sys.stderr.write('{}: error: {}\n'.format(SCRIPT_NAME, msg))
  sys.stderr.flush()
## }}}

## {{{ die(msg)
def die(msg):
  error(msg)
  sys.exit(1)
## }}}

## {{{ die_config(msg)
def die_config(msg):
  sys.stderr.write('configuration error: ' + msg + '\n')
  sys.exit(1)
## }}}

##
# vim: ts=2 sw=2 et fdm=marker :
