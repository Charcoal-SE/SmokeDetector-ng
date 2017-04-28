# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

from dulwich import porcelain, repo
import imp
import os.path
import regex
import sys

import config

DONT_RELOAD = set(("__main__", "secrets", "config", "command_dispatch"))
_repo = repo.Repo("..")


def rev():
    return _head_commit().id.decode("utf-8")


def short_rev():
    return rev()[:7]


def pretty_rev():
    head_commit = _head_commit()

    return ("%s by %s - %s" % (head_commit.id.decode("utf-8"), _parse_author(head_commit.author)[0],
                               head_commit.message.decode("utf-8"))).rstrip()


def handle_pull():
    porcelain.pull(_repo, remote_location=config.github + ".git")

    for name in list(sys.modules.keys()):
        if name not in DONT_RELOAD:
            try:
                fh, path, details = imp.find_module(name)
            except:
                path = None

            if path and os.path.dirname(path) == os.getcwd():
                imp.load_module(name, fh, path, details)


def _head_commit():
    return _repo.get_object(_repo.head())


def _parse_author(author):
    return regex.findall("(.*?) <(.*?)>", author.decode("utf-8"))[0]
