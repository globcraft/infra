#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import sys

import importlib

import json

## {{{ proc_iter(func, arg)
def proc_iter(func, arg):
  with os.scandir('/proc') as iter:
    for ent in iter:
      if not ent.is_dir():
        continue

      try:
        pid = int(ent.name)
      except ValueError:
        continue

      func(pid, arg)
## }}}

## {{{ parse_json_file(path)
def parse_json_file(path):
  with open(path, 'r') as fp:
    return json.loads(fp.read())
## }}}

## {{{ import_module(name, package=None)
def import_module(name, package=None, invalidate_caches=True):
  if invalidate_caches:
    importlib.invalidate_caches()

  return importlib.import_module(name, package=package)
## }}}

##
# vim: ts=2 sw=2 et fdm=marker :
##
