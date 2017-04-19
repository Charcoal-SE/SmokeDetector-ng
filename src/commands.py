# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import random

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


@command(reply=False, whole_msg=True)
def blame(msg) -> str:
    unlucky_victim = msg._client.get_user(random.choice(msg.room.get_current_user_ids()))

    return "It's [%s](https://chat.%s/users/%d)'s fault." % (unlucky_victim.name, msg._client.host, unlucky_victim.id)


@command(str, reply=False, whole_msg=True, aliases=["blame\u180E"])
def blame2(msg, x) -> str:
    base = {"\u180E": 0, "\u200B": 1, "\u200C": 2, "\u200D": 3, "\u2060": 4, "\u2063": 5, "\uFEFF": 6}
    user = 0

    for i, char in enumerate(reversed(x)):
        user += (len(base)**i) * base[char]

    unlucky_victim = msg._client.get_user(user)
    return "It's [%s](https://chat.%s/users/%d)'s fault." % (unlucky_victim.name, msg._client.host, unlucky_victim.id)


@command(reply=False)
def stappit() -> None:
    exit(status.END)
