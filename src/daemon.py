# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import multiprocessing

import entry
import secrets
import status

if __name__ == "__main__":
    secrets.open_store()

    prev_exit = status.START

    while prev_exit != status.END:
        handler = status.get_handler(prev_exit)

        if handler.defer:
            handler_code = prev_exit
        else:
            handler.method()
            handler_code = status.START

        process = multiprocessing.Process(target=entry.start, args=(handler_code,))

        process.start()
        process.join()

        prev_exit = process.exitcode
