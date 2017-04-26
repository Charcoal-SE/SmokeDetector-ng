# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import regex

import config
import chat

_commands = {"reply": {}, "prefix": {}}


# noinspection PyMissingTypeHints
def command(*type_signature, reply=False, whole_msg=False, aliases=None):
    if aliases is None:
        aliases = []

    # noinspection PyMissingTypeHints
    def decorator(func):
        def f(*args, original_msg=None) -> object:
            processed_args = [get_type(arg) for get_type, arg in zip(type_signature, args)]

            if whole_msg:
                return func(original_msg, *processed_args)
            else:
                return func(*processed_args)

        cmd = (f, len(type_signature))

        if reply:
            _commands["reply"][func.__name__] = cmd

            for alias in aliases:
                _commands["reply"][alias] = cmd
        else:
            _commands["prefix"][func.__name__] = cmd

            for alias in aliases:
                _commands["prefix"][alias] = cmd

        return f

    return decorator


def dispatch_command(msg, client) -> str:
    command_parts = msg.content.split(" ", 1)

    if len(command_parts) == 2:
        cmd, args = command_parts
    else:
        cmd, = command_parts
        args = ""

    command_name = cmd[len(config.command_prefix):].lower()

    if command_name not in _commands["prefix"]:
        return "No such command %s." % command_name
    else:
        func, arity = _commands["prefix"][command_name]

        if arity == 0:
            return func(original_msg=msg)
        elif arity == 1:
            return func(args, original_msg=msg)
        else:
            args = args.split()

            if len(args) < arity:
                return "Too few arguments."
            elif len(args) > arity:
                return "Too many arguments."
            else:
                return func(*args, original_msg=msg)


def dispatch_reply_command(msg, reply, cmd, client) -> str:
    cmd = cmd.lower()

    if cmd not in _commands["reply"]:
        return "No such command %s." % cmd
    else:
        func, arity = _commands["reply"][cmd]

        assert arity == 1

        return func(msg.id, original_msg=reply)


def dispatch_shorthand_command(msg, room, client) -> str:
    commands = msg.content[len(config.shorthand_prefix):].split()

    output = []
    processed_commands = []

    for cmd in commands:
        count, cmd = regex.match(r"^(\d*)(.*)", cmd).groups()

        for _ in range(int(count) if count else 1):
            processed_commands.append(cmd)

    for current_command, message in zip(processed_commands, chat.get_last_messages(room, len(processed_commands))):
        if current_command != "-":
            output.append(dispatch_reply_command(message, msg, current_command))

    return "\n".join(output)
