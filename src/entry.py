# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import smokey_chat
import smokey_secrets
import smokey_status
import smokey_ws

def start(handler):
  if not smokey_secrets._secrets:
    print("Secret store not already open: started without smokey_daemon?")
    smokey_secrets.open_store()

  smokey_chat.init()

#  smokey_retrieve.init_pools()
#  smokey_spam.init_pools()
  handler()

  smokey_ws.start_event_loop()

if __name__ == "__main__":
  start(smokey_status._handlers[smokey_status.START].method)
