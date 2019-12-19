#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import sys

import glob
import string
import subprocess

from datetime import datetime

import json

## {{{ parse_json_file(path)
def parse_json_file(path):
  with open(path, 'r') as fp:
    return json.loads(fp.read())
## }}}

## {{{ parse_spec_file(path)
def parse_spec_file(path):
  obj = None

  try:
    obj = parse_json_file(path)
  except json.decoder.JSONDecodeError as ex:
    fmt = "{}: line {}: syntax error near column {}"
    raise BackupSpecError(fmt.format(path, ex.lineno, ex.colno))

  return obj
## }}}

## {{{ class BackupSpecError

class BackupSpecError(Exception):

  ## {{{ BackupSpecError.__init__(msg)
  def __init__(self, msg):
    self.msg = msg
  ## }}}

## class BackupSpecError }}}

## {{{ class BackupSpec
class BackupSpec:

  spec_file = None

  s_type = None
  s_identifier = None
  s_path = None
  s_daily = None
  s_hourly = None
  s_hooks = None

  ## {{{ BackupSpec.__init__(path)
  def __init__(self, path):
    self.spec_file = path
    self.s_hooks = {}
  ## }}}

  ## {{{ BackupSpec.parse()
  def parse(self):
    print('Parsing {}...'.format(self.spec_file))
    spec = parse_spec_file(self.spec_file)

    t = type(spec)
    if t != dict:
      fmt = "{}: invalid root object type (expecting dict, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, t))

    valid_keys = ['type', 'identifier', 'path', 'daily', 'hourly']

    for key in spec.keys():
      if key in valid_keys:
        attr = 's_' + key
        setattr(self, attr, spec[key])
        continue
      raise BackupSpecError("{}: invalid spec key '{}'".format(self.spec_file, key))

    hook_dir = os.path.dirname(self.spec_file) + '/hooks'
    if not os.path.isdir(hook_dir):
      return

    valid_hooks = ['pre', 'post']

    for hook_file in glob.glob(hook_dir + '/*.hook'):
      hook_name = os.path.splitext(os.path.basename(hook_file))[0]
      if hook_name not in valid_hooks:
        raise BackupSpecError('{}: invalid hook name'.format(hook_name))

      self.s_hooks[hook_name] = hook_file
  ## }}}

  ## {{{ BackupSpec._valid_identifier(identifier)
  def _valid_identifier(self, identifier):
    valid_chars = string.ascii_letters + string.digits + '.-_'


    i = 0
    l = len(identifier)
    while i < l:
      if identifier[i] not in valid_chars:
        print('identifier[{}] = {}'.format(i, identifier[i]))
        return False
      i += 1

    return True
  ## }}}    

  ## {{{ BackupSpec.validate()
  def validate(self):
    print('Validating {}...'.format(self.spec_file))

    # Job type
    t = type(self.s_type)
    if t != str:
      fmt = "{}: invalid type for spec variable '{}' (expecting str, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, 'type', t))
    elif self.s_type not in ['system', 'minecraft']:
      fmt = "{}: invalid backup job type '{}' (expecting either 'system' or 'minecraft')"
      raise BackupSpecError(fmt.format(self.spec_file, self.s_type))

    # Job identifier
    t = type(self.s_identifier)
    if t != str:
      fmt = "{}: invalid type for spec variable '{}' (expecting str, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, 'identifier', t))
    elif not self._valid_identifier(self.s_identifier):
      fmt = "{}: spec variable '{}' contains invalid character(s)"
      raise BackupSpecError(fmt.format(self.spec_file, 'identifier'))

    # Job source directory
    t = type(self.s_path)
    if t != str:
      fmt = "{}: invalid type for spec variable '{}' (expecting str, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, 'path', t))
    elif not os.path.isdir(self.s_path):
      fmt = "{}: backup source directory '{}' doesn't exist"
      raise BackupSpecError(fmt.format(self.spec_file, self.s_path))

    # Job frequency (daily)
    t = type(self.s_daily)
    if t != bool:
      fmt = "{}: invalid type for spec variable '{}' (expecting bool, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, 'daily', t))

    # Job frequency (hourly)
    t = type(self.s_hourly)
    if t != bool:
      fmt = "{}: invalid type for spec variable '{}' (expecting bool, got '{}')"
      raise BackupSpecError(fmt.format(self.spec_file, 'hourly', t))

    if not self.s_hooks or len(self.s_hooks) < 1:
      return

    for h in self.s_hooks.keys():
      hook_file = self.s_hooks[h]
      if not os.path.isfile(hook_file):
        fmt = "{}: {} hook '{}' doesn't exist or isn't a regular file"
        raise BackupSpecError(fmt.format(self.spec_file, h, hook_file))
      elif not os.access(hook_file, os.X_OK):
        fmt = "{}: {} hook '{}' isn't executable"
        raise BackupSpecError(fmt.format(self.spec_file, h, hook_file))
  ## }}}

  ## {{{ [static] BackupSpec.find_spec_files()
  @staticmethod
  def find_spec_files():
    spec_list = []

    for root, dirs, files in os.walk('/'):
      for name in dirs:
        if name != '.backup':
          continue

        abs_path = os.path.join(root, name)
        spec_file = os.path.join(abs_path, 'spec.json')
        if not os.path.isfile(spec_file):
          continue
        if spec_file.startswith('/backup/'):
          continue

        spec_list.append(spec_file)

    return spec_list
  ## }}}

  ## {{{ [static] BackupSpec.parse_spec_files(spec_files)
  @staticmethod
  def parse_spec_files(spec_files):
    specs = []

    try:
      for spec_file in spec_files:
        s = BackupSpec(spec_file)
        s.parse()
        s.validate()
        specs.append(s)
    except BackupSpecError as ex:
      if True:
        raise ex
      else:
        die(ex.msg)

    return specs
  ## }}}

## class BackupSpec }}}

## {{{ error(msg)
def error(msg):
  fmt = '{}: error: {}\n'
  sys.stderr.write(fmt.format(os.path.basename(sys.argv[0]), msg))
  sys.stderr.flush()
## }}}

## {{{ die(msg)
def die(msg):
  error(msg)
  sys.exit(1)
## }}}

## {{{ do_exec(argv)
def do_exec(argv):
  child = subprocess.Popen(
    argv,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )

  stdout, stderr = child.communicate()

  return child.returncode, stdout, stderr
## }}}

## {{{ do_system_backup(spec)
def do_system_backup(spec):
  print('\nSkipping spec {}'.format(spec.spec_file))
## }}}

def exec_hook(hook):
  print('Executing hook:', hook)
  st, out, err = do_exec([hook])
  if st!= 0:
    fmt = "{}: hook returned non-zero exit status {}"
    error(fmt.format(pre_hook, st))
    if out:
      print('  stdout:')
      for line in out.decode('utf-8').split('\n'):
        print('    {}'.format(line))
    if err:
      print('  stderr:')
      for line in err.decode('utf-8').split('\n'):
        print('    {}'.format(line))

## {{{ do_minecraft_backup(spec)
def do_minecraft_backup(spec):
  fmt = '\n[{}] Beginning backup job for Minecraft server: {}\n'
  print(fmt.format(datetime.now().strftime('%F %T'), spec.s_identifier))

  pre_hook = None
  post_hook = None

  if spec.s_hooks:
    if 'pre' in spec.s_hooks.keys():
      pre_hook = spec.s_hooks['pre']
    if 'post' in spec.s_hooks.keys():
      post_hook = spec.s_hooks['post']

  if pre_hook:
    exec_hook(pre_hook)

  helper_path = os.environ['LIB_DIR'] + '/helpers/btrfs-backup'
  helper_cmds = ['sync-to-local', 'snapshot-create']
  helper_failed = False

  for cmd in helper_cmds:
    argv = [helper_path, cmd]

    print('Executing helper: {} {}'.format(*argv))
    st, out, err = do_exec(argv)

    #if out:
    #  print('Output:')
    #   for line in out.decode('utf-8').rstrip().split('\n'):
    #    print('  {}'.format(line))

    if st == 0:
      # Helper command exited successfully
      continue

    error('Helper {} {} returned non-zero exit status {}'.format(os.path.basename(helper_path), cmd, st))
    helper_failed = True

    if err:
      print('  stderr:')
      for line in err.decode('utf-8').split('\n'):
        print('    {}'.format(line))

    break

  if post_hook:
    exec_hook(post_hook)

  if helper_failed:
    die('error(s) encountered, exiting...')

  print('\n[{}] Backup job finished\n'.format(datetime.now().strftime('%F %T')))
## }}}

## {{{ do_backup(spec)
def do_backup(spec):
  os.environ['BACKUP_TYPE'] = spec.s_type
  os.environ['BACKUP_PATH'] = spec.s_path
  os.environ['BACKUP_IDENTIFIER'] = spec.s_identifier

  if spec.s_type == 'minecraft':
    do_minecraft_backup(spec)
  elif spec.s_type == 'system':
    do_system_backup(spec)
  else:
    die("internal error -- job type '{}' not supported by do_backup()".format(spec.s_type))
## }}}

## {{{ init()
def init():
  os.environ['ROOT_DIR'] = os.path.abspath(os.path.dirname(__file__) + '/../../../..')
  os.environ['LIB_DIR'] = os.environ['ROOT_DIR'] + '/lib'
## }}}

## {{{ main([argv=sys.argv])
def main(argv=sys.argv):
  spec_files = BackupSpec.find_spec_files()
  specs = BackupSpec.parse_spec_files(spec_files)

  for s in specs:
    do_backup(s)

  return 0
## }}}

##
# vim: ts=2 sw=2 et fdm=marker :
##
