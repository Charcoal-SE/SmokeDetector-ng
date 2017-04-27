# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import random

from command_dispatch import command
from database import Notification, SESSION
import config
import excepthook
import status


@command(int, int, reply=False)
def add(x, y) -> str:
    return "%d and %d makes %d" % (x, y, x + y)


# noinspection PyShadowingBuiltins
@command(int, reply=True, whole_msg=True)
def id(msg, x):
    return "Your message was %d. My message was %d." % (msg.id, x)


@command(reply=False)
def pull() -> None:
    excepthook.safe_exit(status.PULL)


@command(reply=False)
def stappit() -> None:
    excepthook.safe_exit(status.END)


@command(reply=False)
def location() -> str:
    return config.location


@command(int, str, reply=False, whole_msg=True)
def notify(msg, room_id, site) -> str:
    chat_host = msg.room._client.host
    user_id = msg.owner.id

    Notification.create(chat_site_url=chat_host, chat_user_id=user_id, room_id=room_id, site_url=site)

    return "You will now be notified of reports on `{}`, in room {} on chat.{}.".format(site, room_id, chat_host)


@command(int, str, reply=False, whole_msg=True)
def unnotify(msg, room_id, site) -> str:
    chat_host = msg._client.host
    user_id = msg.owner.id

    notifications = SESSION.query(Notification).filter(Notification.chat_site_url == chat_host,
                                                       Notification.chat_user_id == user_id,
                                                       Notification.room_id == room_id,
                                                       Notification.site_url == site)

    notifications.delete(synchronize_session='fetch')
    SESSION.commit()

    return "You will no longer be notified of reports on `{}`, in room {} on chat.{}.".format(site, room_id, chat_host)


@command(reply=False)
def throw() -> None:
    raise Exception


# --- JOKE COMMANDS --- #
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
def brownie() -> str:
    return "Brown!"


@command(reply=False)
def lick() -> str:
    return "*licks ice cream cone*"


@command(reply=False)
def tea() -> str:
    return "*brews a cup of {choice} tea*".format(random.choice(['earl grey', 'green', 'chamomile', 'lemon',
                                                                 'darjeeling', 'mint', 'jasmine']))


@command(reply=False)
def wut() -> str:
    return "Whaddya mean, 'wut'? Humans..."
