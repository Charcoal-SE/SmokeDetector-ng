# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import imp
import multiprocessing
import os.path
import sys

import entry
import secrets
import status

DONT_RELOAD = set(("__main__", "secrets", "config", "command_dispatch"))

secrets.open_store()

if __name__ == "__main__":
    status_code = status.START
    handler = status.handlers[status_code]

    while status_code != status.END:
        if handler.defer:
            err_handler = handler
        else:
            err_handler = status.handlers[status.START]
            handler.method()

        for name in list(sys.modules.keys()):
            if name not in DONT_RELOAD:
                try:
                    fh, path, details = imp.find_module(name)
                except:
                    path = None

                if path and os.path.dirname(path) == os.getcwd():
                    imp.load_module(name, fh, path, details)

        process = multiprocessing.Process(target=entry.start, args=(err_handler,))

        process.start()
        process.join()

        status_code, handler = status.extract_status(process.exitcode)
