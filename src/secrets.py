# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA256
import Cryptodome.Random
import Cryptodome.Util.Counter
import ctypes
import getpass
import json
import multiprocessing
import os

import config

_required_credentials = [
    "email",
    "pw",
    "se_key"
]

_optional_credentials = [
    "ms_key",
    "gh_email",
    "gh_pw"
]

_secrets = multiprocessing.Value(ctypes.c_bool, False)


def require_secrets(function):
    def f(*args, **kwargs):
        assert _secrets
        return function(*args, **kwargs)

    return f


def open_store():
    global _secrets

    sha256 = Cryptodome.Hash.SHA256.new()
    
    if "NG_KEY" in os.environ:
        sha256.update(os.environ["NG_KEY"].encode("utf-8"))
    else:
        sha256.update(getpass.getpass("Store password: ").encode("utf-8"))

    key = sha256.digest()

    with open("../config/secrets.json.aes", "rb") as store_file:
        nonce = store_file.read(8)
        ciphertext = store_file.read()

        counter = Cryptodome.Util.Counter.new(64, prefix=nonce)
        decrypt = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CTR, counter=counter)

        plaintext = decrypt.decrypt(ciphertext).decode("utf-8")

        secrets = json.loads(plaintext)

        have_keys = secrets.keys()
        need_keys = _required_credentials

        if config.require_optional_credentials:
            need_keys += _optional_credentials

        missing_keys = [x for x in need_keys if x not in have_keys]

        for credential in missing_keys:
            secrets[credential] = getpass.getpass(credential + ": ")

        for key, value in secrets.items():
            globals()[key] = multiprocessing.Value(ctypes.c_wchar_p, value)

        _secrets.value = True


def secrets_loaded():
    return _secrets.value


def make_store(plain_filename, cipher_filename):
    sha256 = Cryptodome.Hash.SHA256.new()
    sha256.update(getpass.getpass("Store password: ").encode("utf-8"))

    key = sha256.digest()

    with open(plain_filename, "r") as plaintext_file:
        with open(cipher_filename, "wb") as ciphertext_file:
            nonce = Cryptodome.Random.get_random_bytes(8)
            plaintext = plaintext_file.read()

            counter = Cryptodome.Util.Counter.new(64, prefix=nonce)
            encrypt = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CTR, counter=counter)

            ciphertext_file.write(nonce)
            ciphertext_file.write(encrypt.encrypt(plaintext.encode("utf-8")))

    print("Make sure to delete " + plain_filename)


if __name__ == "__main__":
    import sys

    make_store("../config/secrets.json" if len(sys.argv) < 2 else sys.argv[1],
               "../config/secrets.json.aes" if len(sys.argv) < 3 else sys.argv[2])
