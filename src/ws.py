# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import websocket

import smokey_chat

def start_event_loop():
  socket = websocket.WebSocketApp("ws://qa.sockets.stackexchange.com", 
    on_open    = init_ws, 
    on_message = lambda *x: None,
    on_close   = restart_ws
  )

  socket.run_forever()

def init_ws(socket):
  socket.send("155-questions-active")

def restart_ws(_):
  smokey_chat.tell_rooms_with("debug", "Re-opened SE websocket.")
  start_event_loop()
