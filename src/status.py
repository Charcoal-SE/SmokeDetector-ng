# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import collections

from chat import handle_err, handle_signal, handle_start
from git import handle_pull

Handler = collections.namedtuple("Handler", ["method", "defer"])

END = 0
ERR = 1
START = 2
PULL = 3
SIGNAL = 128

handlers = {
    ERR: Handler(handle_err, True),
    START: Handler(handle_start, True),
    PULL: Handler(handle_pull, False),
    SIGNAL: Handler(handle_signal, True)
}


def extract_status(exit_code):
    if exit_code >= 0:
        return exit_code, handlers.get(exit_code, 0)
    else:
        return SIGNAL, Handler(lambda: handlers[SIGNAL].method(-exit_code), True)
