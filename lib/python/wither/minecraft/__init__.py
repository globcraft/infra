#!/usr/bin/env python3
# -*- coding: utf-8 -*

import os
import sys

import subprocess

from wither.console import notice
from wither.util import proc_iter

from wither.minecraft.mcrcon import MCRcon

## {{{ parse_server_properties(path)
def parse_server_properties(path):
  props_file = path + '/server.properties'

  if not os.path.isfile(props_file):
    return None

  with open(props_file, 'r') as fp:
    content = fp.read()

  props = {}

  for line in content.split('\n'):
    if line.startswith('#'):
      continue
    elif line.strip() == '':
      continue
    tmp = line.split('=')
    props[tmp[0]] = tmp[1]

  return props
## }}}

## {{{ get_server_properties(path)
def get_server_properties(path):
  return parse_server_properties(path)
## }}}

## {{{ minecraft_server_port(path)
def minecraft_server_port(path):
  props = get_server_properties(path)
  if not props or 'server-port' not in props:
    return -1

  return int(props['server-port'])
## }}}

## {{{ minecraft_server_motd(path)
def minecraft_server_motd(path):
  props = get_server_properties(path)
  if not props or 'motd' not in props:
    return 'Unknown'

  return props['motd']
## }}}

## {{{ find_minecraft_servers(pid, arg)
def find_minecraft_servers(pid, arg):
  servers = arg

  try:
    exe = os.readlink('/proc/{0}/exe'.format(pid))
    cwd = os.readlink('/proc/{0}/cwd'.format(pid))
  except PermissionError:
    return
  except FileNotFoundError:
    return

  if not exe.endswith('/bin/java'):
    return

  port = minecraft_server_port(cwd)
  motd = minecraft_server_motd(cwd)

  servers.append(MinecraftServer(cwd, motd, port))
## }}}

## {{{ mcrcon_players()
def mcrcon_players():
  players = []

  rcon = MCRcon()
  output = rcon.list().rstrip()

  if output.startswith('There are 0'):
    return players

  tmp = output.split(': ')
  for player in tmp[1].split(', '):
    players.append(player)

  return players
## }}}

## {{{ class MinecraftServer
class MinecraftServer:

  path = None
  motd = None
  port = -1

  ## {{{ MinecraftServer.__init__(path, motd, port)
  def __init__(self, path, motd, port):
    self.path = path
    self.motd = motd
    self.port = port
  ## }}}

## class MinecraftServer }}}

## {{{ class MinecraftServerList
class MinecraftServerList:

  servers = None

  ## {{{ MinecraftServerList.__init__()
  def __init__(self):
    self.servers = []
    proc_iter(find_minecraft_servers, self.servers)
  ## }}}

## class MinecraftServerList }}}

## {{{ class MinecraftPlayerList
class MinecraftPlayerList:

  players = None

  ## {{{ MinecraftPlayerList.__init__()
  def __init__(self):
    self.players = []

    rcon = MCRcon()
    output = rcon.list().rstrip()

    if output.startswith('There are 0'):
      return

    tmp = output.split(': ')
    for player in tmp[1].split(', '):
      self.players.append(player)
  ## }}}

## class MinecraftPlayerList }}}

##
# vim: ts=2 sw=2 et fdm=marker :
##
