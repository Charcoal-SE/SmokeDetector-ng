# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import websocket

import chat


def start_event_loop():
    socket = websocket.WebSocketApp("ws://qa.sockets.stackexchange.com",
        on_open=init_ws,
        on_message=lambda *x: None,
        on_close=restart_ws
    )

    socket.run_forever()


def init_ws(socket):
    socket.send("155-questions-active")


def restart_ws(_):
    chat.tell_rooms_with("debug", "Re-opened SE websocket.")
    start_event_loop()
