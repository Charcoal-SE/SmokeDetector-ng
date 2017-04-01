# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import chat
import commands
import secrets
import status
import ws


def start(handler):
    if not secrets.secrets_loaded():
        print("Secret store not already open: started without daemon?")
        secrets.open_store()

    chat.init()

#  retrieve.init_pools()
#  spam.init_pools()
    handler()

    ws.start_event_loop()


if __name__ == "__main__":
    start(status._handlers[status.START].method)
