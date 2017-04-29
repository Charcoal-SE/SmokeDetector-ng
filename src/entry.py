# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import os.path
import sys

sys.path.append(os.path.abspath('..'))

import chat
import commands
import excepthook
import os
import secrets
import status
import ws


def start(handler_code):
    handler = status.get_handler(handler_code)

    if not secrets.secrets_loaded():
        print("Secret store not already open: started without daemon?")
        secrets.open_store()

    chat.init()

    handler.method()
    ws.start_event_loop()

    excepthook.shutdown.wait()
    os._exit(excepthook.err_code)


if __name__ == "__main__":
    start(status.START)
