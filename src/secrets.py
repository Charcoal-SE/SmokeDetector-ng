# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA256
import Cryptodome.Random
import Cryptodome.Util.Counter
import getpass
import json

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

_secrets = False


def require_secrets(function):
    def f(*args, **kwargs):
        assert _secrets
        return function(*args, **kwargs)

    return f


def open_store():
    global _secrets

    sha256 = Cryptodome.Hash.SHA256.new()
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
            globals()[key] = value

        _secrets = True


def secrets_loaded():
    return _secrets


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
            ciphertext_file.write(encrypt.encrypt(plaintext))

    print("Make sure to delete " + plain_filename)


if __name__ == "__main__":
    import sys

    make_store("../config/secrets.json" if len(sys.argv) < 2 else sys.argv[1],
               "../config/secrets.json.aes" if len(sys.argv) < 3 else sys.argv[2])
