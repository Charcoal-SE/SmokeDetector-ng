# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import threading
import websocket

from excepthook import excepthook
import chat


def start_event_loop():
    socket = websocket.WebSocketApp("ws://qa.sockets.stackexchange.com", on_open=init_ws, on_message=lambda *x: None,
                                    on_close=restart_ws)
    threading.Thread(target=excepthook(socket.run_forever)).start()


def init_ws(socket):
    socket.send("155-questions-active")


def restart_ws(_):
    start_event_loop()
