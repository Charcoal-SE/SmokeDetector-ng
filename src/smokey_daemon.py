# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import os

import smokey_entry
import smokey_secrets
import smokey_status

smokey_secrets.open_store()

err_handler = None

if __name__ == "__main__":
  status = smokey_status.START
  handler = smokey_status._handlers[smokey_status.START]

  while status != smokey_status.END:
    if handler.defer:
      err_handler = handler.method
    else:
      handler.method()

    pid = os.fork()

    if pid:
      status, handler = smokey_status.extract_status(os.waitpid(pid, 0)[1])
    else:
      smokey_entry.start(err_handler)
