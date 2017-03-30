# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import itertools
import string

import config
import chat
import status

_commands = {"reply": {}, "prefix": {}}


def command(*type_signature, reply=False, whole_msg=False):
    def decorator(func):
        def f(*args, original_msg=None):
            processed_args = [type(arg) for type, arg in zip(type_signature, args)]

            if whole_msg:
                return func(original_msg, *processed_args)
            else:
                return func(*processed_args)

        if reply:
            _commands["reply"][func.__name__] = (f, len(type_signature))
        else:
            _commands["prefix"][func.__name__] = (f, len(type_signature))

        return f

    return decorator


def dispatch_command(msg):
    command_parts = msg.content.split(" ", 1)

    if len(command_parts) == 2:
        command, args = command_parts
    else:
        command, = command_parts

    command_name = command[len(config.command_prefix):]

    if command_name not in _commands["prefix"]:
        return "@%s No such command %s." % (msg.owner.name, command_name)
    else:
        function, arity = _commands["prefix"][command_name]

        if arity == 0:
            return function(original_msg=msg)
        elif arity == 1:
            return function(args, original_msg=msg)
        else:
            args = args.split()

            if len(args) < arity:
                return "Too few arguments."
            elif len(args) > arity:
                return "Too many arguments."
            else:
                return "@%s %s" % (msg.owner.name, function(*args, original_msg=msg))


def dispatch_reply_command(msg, reply, command):
    if command not in _commands["reply"]:
        return "@%s No such command %s." % (reply.owner.name, command)
    else:
        function, arity = _commands["reply"][command]

        assert arity == 1

        return "@%s %s" % (reply.owner.name, function(msg.id, original_msg=reply))


def dispatch_shorthand_command(msg, room):
    commands = msg.content[len(config.shorthand_prefix):].split()

    output = []

    for command in commands:
        print(command)
        if command.startswith(string.digits):
            count = int(command[0])
            command = command[1:]
        else:
            count = 1

        for message in reversed(chat.get_last_messages(room)[-count:]):
            if command != "-":
                output.append(dispatch_reply_command(message, msg, command))

    return "\n".join(output)


@command(int, int, reply=False)
def add(x, y):
    return "%d and %d makes %d" % (x, y, x + y)


@command(int, reply=True, whole_msg=True)
def id(msg, x):
    return "Your message was %d. My message was %d." % (msg.id, x)


@command(reply=False)
def pull():
    os.exit(status.PULL)


@command(reply=False)
def location():
    return config.location
