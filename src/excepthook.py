import threading

shutdown = threading.Event()
err_code = 0


def excepthook(func):
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            print("{}: caught exception {}".format(func.__name__, ex))  # replace with better logging
            safe_exit(1)

    return f


def safe_exit(code):
    global err_code

    err_code = code
    shutdown.set()
