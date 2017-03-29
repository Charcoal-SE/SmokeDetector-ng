# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import collections

from chat import handle_err, handle_signal, handle_start
from git import handle_pull

Handler = collections.namedtuple("Handler", ["method", "defer"])

END    = 0
ERR    = 1
START  = 2
PULL   = 3
SIGNAL = 128

_handlers = {
  ERR:    Handler(handle_err,    True),
  START:  Handler(handle_start,  True),
  PULL:   Handler(handle_pull,   False),
  SIGNAL: Handler(handle_signal, True)
}

def extract_status(exit_code):
  if exit_code & 128:
    return SIGNAL, Handler(lambda: _handlers[SIGNAL](exit_code - 128), True)
  else:
    return exit_code, handlers[exit_code]
