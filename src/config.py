# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import json

_loaded = False

if not _loaded:
    with open("../config/config.json", "r") as config_file:
        for key, value in json.load(config_file).items():
            globals()[key] = value

    _loaded = True
