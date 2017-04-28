# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import multiprocessing

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
            handler.method()
            err_handler = status.handlers[status.START]

        process = multiprocessing.Process(target=entry.start, args=(err_handler,))

        process.start()
        process.join()

        status_code, handler = status.extract_status(process.exitcode)
