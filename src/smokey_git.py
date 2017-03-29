# vim: set filetype=python tabstop=2 shiftwidth=2 expandtab:

import dulwich.porcelain
import dulwich.repo
import re

import smokey_config

_repo = dulwich.repo.Repo("..")

def rev():
  head_commit = _repo.get_object(_repo.head())

  return ("%s by %s - %s" % (head_commit.id.decode("utf-8"), _parse_author(head_commit.author)[0], head_commit.message.decode("utf-8"))).rstrip()

def handle_pull():
  dulwich.porcelain.pull(_repo, remote_location=smokey_config.github)

def _parse_author(author):
  return re.findall("(.*?) <(.*?)>", author.decode("utf-8"))[0]
