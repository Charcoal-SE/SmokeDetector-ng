# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import imp
import importlib
import multiprocessing
import sys
import types

import entry
import secrets
import status

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

        for name, module in sys.modules.items():
            if (name != "__main__" and
                    not imp.is_builtin(name) and
                    not imp.is_frozen(name) and
                    isinstance(name, types.ModuleType)):
                importlib.reload(module)

        process = multiprocessing.Process(target=entry.start, args=(err_handler,))

        process.start()
        process.join()

        status_code, handler = status.extract_status(process.exitcode)
