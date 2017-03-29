# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import chatexchange.client
import chatexchange.events
import json

import config
import git
import secrets

_init = False

_clients = {
  "stackexchange.com":      None,
  #"stackoverflow.com":      None,
  #"meta.stackexchange.com": None
}

_room_permissions = None
_rooms = {}
_last_messages = {}

def require_chat(function):
  def f(*args, **kwargs):
    assert _init
    function(*args, **kwargs)

  return f

@secrets.require_secrets
def init():
  global _clients
  global _init
  global _room_permissions
  global _rooms

  for site in _clients.keys():
    client = chatexchange.client.Client(site)
    client.login(secrets.email, secrets.pw)

    _clients[site] = client

  _room_permissions = parse_room_config()
  
  for site, roomid in _room_permissions["commands"]:
    room = _clients[site].get_room(roomid)
    
    room.join()
    room.watch(lambda msg, client: on_msg(msg, client, room))
    _rooms[roomid] = room

  _init = True

def parse_room_config():
  with open("../config/rooms.json", "r") as room_config:
    room_dict = json.load(room_config)

    rooms = {}

    for site, site_rooms in room_dict.items():
      for roomid, room in site_rooms.items():
        room_identifier = (site, roomid)

        for perm in room["msg_types"]:
          if perm not in rooms:
            rooms[perm] = set()

          rooms[perm].add(room_identifier)

  return rooms

@require_chat
def on_msg(msg, client, room):
  if isinstance(msg, chatexchange.events.MessagePosted) or isinstance(msg, chatexchange.events.MessageEdited):
    message = msg.message

    if message.owner.id in config.my_ids:
      _last_messages[room] = message
    elif message.parent and message.parent.owner.id in config.my_ids:
      send_to_room(room, commands.dispatch_reply_command(message, message.content))
    elif message.content.startswith(config.shorthand_prefix):
      send_to_room(room, commands.dispatch_shorthand_command(message, room))
    elif message.content.startswith(config.command_prefix):
      send_to_room(room, commands.dispatch_command(message))

@require_chat
def send_to_room(room, msg):
  msg = msg.rstrip()

  if (room._client.host, room.id) in _room_permissions["commands"] and room in _last_messages:
    if "\n" in msg:
      room.send_message(":%d %s" % (_last_messages[room].id, msg))
    else:
      room.send_message(":%d > %s" % (_last_messages[room].id, msg))
  else:
    room.send_message(msg)

@require_chat
def tell_rooms_with(prop, msg):
  tell_rooms(msg, (prop,), ())

@require_chat
def tell_rooms_without(prop, msg):
  tell_rooms(msg, (), (prop,))

@require_chat
def tell_rooms(msg, has, hasnt):
  global _rooms

  target_rooms = set()

  for prop_has in has:
    for room in _room_permissions[prop_has]:
      if all(map(lambda prop_hasnt: room not in _room_permissions[prop_hasnt], hasnt)):
        site, roomid = room

        if roomid not in _rooms:
          new_room = _clients[site].get_room(roomid)
          new_room.join()

          _rooms[roomid] = new_room

        target_rooms.add(_rooms[roomid])

  for room in target_rooms:
    send_to_room(room, msg)

@require_chat
def handle_start():
  tell_rooms_with("debug", "SmokeDetector-ng started at revision %s." % git.rev())

@require_chat
def handle_signal(signal):
  tell_rooms_with("debug", "Recovered from signal %d." % signal)

@require_chat
def handle_err():
  tell_rooms_with("debug", "Recovered from exception.")

@require_chat
def unwind_prev_messages(room):
  current = _last_messages[room]

  while current:
    yield current.id

    current = current.parent

import commands
