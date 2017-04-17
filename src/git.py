# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

from dulwich import porcelain, repo
import regex

import config

_repo = repo.Repo("..")


def rev():
    head_commit = _repo.get_object(_repo.head())

    return ("%s by %s - %s" % (head_commit.id.decode("utf-8"), _parse_author(head_commit.author)[0],
                               head_commit.message.decode("utf-8"))).rstrip()


def handle_pull():
    porcelain.pull(_repo, remote_location=config.github + ".git")


def _parse_author(author):
    return regex.findall("(.*?) <(.*?)>", author.decode("utf-8"))[0]
