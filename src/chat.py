# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import chatexchange.client
import chatexchange.events
import collections
import itertools
import json
import os.path
import pickle
import threading

import command_dispatch
import config
import git
import secrets

_init = False

_clients = {
    "stackexchange.com": None,
    "stackoverflow.com": None,
    "meta.stackexchange.com": None
}

_room_permissions = None
_rooms = {}
_last_messages = {}

_pickle_run = threading.Event()


def require_chat(function):
    def f(*args, **kwargs):
        assert _init
        return function(*args, **kwargs)

    return f


@secrets.require_secrets
def init():
    global _clients
    global _init
    global _room_permissions
    global _rooms
    global _last_messages

    for site in _clients.keys():
        client = chatexchange.client.Client(site)
        client.login(secrets.email, secrets.pw)

        _clients[site] = client

    _room_permissions = parse_room_config()

    for site, roomid in _room_permissions["commands"]:
        room = _clients[site].get_room(roomid)

        room.join()
        room.watch(lambda msg, client: on_msg(msg, client, room))
        _rooms[(site, roomid)] = room

    if os.path.isfile("../pickles/last_messages.pck"):
        _last_messages = pickle.load(open("../pickles/last_messages.pck", "rb"))

    threading.Thread(name="pickle runner", target=pickle_last_messages).start()
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


def pickle_last_messages():
    while True:
        _pickle_run.wait()
        _pickle_run.clear()

        with open("../pickles/last_messages.pck", "wb") as pickle_file:
            pickle.dump(_last_messages, pickle_file)


@require_chat
def on_msg(msg, client, room):
    if isinstance(msg, chatexchange.events.MessagePosted) or isinstance(msg, chatexchange.events.MessageEdited):
        message = msg.message

        if message.owner.id in config.my_ids:
            identifier = (client.host, room.id)

            if identifier not in _last_messages:
                _last_messages[identifier] = collections.deque((message.id,))
            else:
                if len(_last_messages[identifier]) > 50:
                    _last_messages[identifier].popleft()

                _last_messages[identifier].append(message.id)

            _pickle_run.set()
        elif message.parent and message.parent.owner.id in config.my_ids:
            command = message.content.split(" ", 1)[1]

            message.reply(command_dispatch.dispatch_reply_command(message.parent, message, command))
        elif message.content.startswith(config.shorthand_prefix):
            message.reply(command_dispatch.dispatch_shorthand_command(message, room))
        elif message.content.startswith(config.command_prefix):
            messgae.reply(room, command_dispatch.dispatch_command(message))


@require_chat
def send_to_room(room, msg, **kwargs):
    msg = msg.rstrip()

    if kwargs.get('prefix'):
        msg = "[ [SmokeDetector-ng]({}) ] ".format(config.github) + msg

    room.send_message(msg)


@require_chat
def tell_rooms_with(prop, msg, **kwargs):
    tell_rooms(msg, (prop,), (), **kwargs)


@require_chat
def tell_rooms_without(prop, msg, **kwargs):
    tell_rooms(msg, (), (prop,), **kwargs)


@require_chat
def tell_rooms(msg, has, hasnt, **kwargs):
    global _rooms

    target_rooms = set()

    for prop_has in has:
        for room in _room_permissions[prop_has]:
            if all(map(lambda prop_hasnt: room not in _room_permissions[prop_hasnt], hasnt)):
                if room not in _rooms:
                    site, roomid = room

                    new_room = _clients[site].get_room(roomid)
                    new_room.join()

                    _rooms[room] = new_room

                target_rooms.add(_rooms[room])

    for room in target_rooms:
        send_to_room(room, msg, **kwargs)


@require_chat
def handle_start():
    tell_rooms_with("debug", "SmokeDetector-ng started at revision [{}]({})."
                    .format(git.short_rev(), config.github + "/commit/" + git.rev()),
                    prefix=True)


@require_chat
def handle_signal(signal):
    tell_rooms_with("debug", "Recovered from signal %d." % signal)


@require_chat
def handle_err():
    tell_rooms_with("debug", "Recovered from exception.")


@require_chat
def get_last_messages(room, count):
    for msg_id in itertools.islice(reversed(_last_messages[(room._client.host, room.id)]), count):
        yield room._client.get_message(msg_id)
