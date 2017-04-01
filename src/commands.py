# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import config
import status

from command_dispatch import command


@command(int, int, reply=False)
def add(x, y) -> str:
    return "%d and %d makes %d" % (x, y, x + y)


# noinspection PyShadowingBuiltins
@command(int, reply=True, whole_msg=True)
def id(msg, x):
    return "Your message was %d. My message was %d." % (msg.id, x)


@command(reply=False)
def pull() -> None:
    exit(status.PULL)


@command(reply=False)
def location() -> str:
    return config.location
