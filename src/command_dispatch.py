# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import regex

import config
import chat

_commands = {"reply": {}, "prefix": {}}


# noinspection PyShadowingNames,PyShadowingBuiltins,PyMissingTypeHints
def command(*type_signature, reply=False, whole_msg=False, aliases=[]):
    # noinspection PyMissingTypeHints
    def decorator(func):
        # noinspection PyShadowingBuiltins
        def f(*args, original_msg=None) -> object:
            processed_args = [type(arg) for type, arg in zip(type_signature, args)]

            if whole_msg:
                return func(original_msg, *processed_args)
            else:
                return func(*processed_args)

        command = (f, len(type_signature))

        if reply:
            _commands["reply"][func.__name__] = command

            for alias in aliases:
                _commands["reply"][alias] = command
        else:
            _commands["prefix"][func.__name__] = command

            for alias in aliases:
                _commands["prefix"][alias] = command

        return f

    return decorator


# noinspection PyShadowingNames,PyShadowingBuiltins
def dispatch_command(msg) -> str:
    command_parts = msg.content.split(" ", 1)

    if len(command_parts) == 2:
        command, args = command_parts
    else:
        command, = command_parts
        args = ""

    command_name = command[len(config.command_prefix):].lower()

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


# noinspection PyShadowingNames,PyShadowingBuiltins
def dispatch_reply_command(msg, reply, command) -> str:
    command = command.lower()

    if command not in _commands["reply"]:
        return "@%s No such command %s." % (reply.owner.name, command)
    else:
        function, arity = _commands["reply"][command]

        assert arity == 1

        return "@%s %s" % (reply.owner.name, function(msg.id, original_msg=reply))


# noinspection PyShadowingNames,PyShadowingBuiltins
def dispatch_shorthand_command(msg, room) -> str:
    commands = msg.content[len(config.shorthand_prefix):].split()

    output = []
    processed_commands = []

    for command in commands:
        count, command = regex.match(r"^(\d*)(.*)", command).groups()

        for _ in range(int(count) if count else 1):
            processed_commands.append(command)

    for current_command, message in zip(processed_commands, chat.get_last_messages(room, len(processed_commands))):
        if current_command != "-":
            output.append(dispatch_reply_command(message, msg, current_command))

    return "\n".join(output)
