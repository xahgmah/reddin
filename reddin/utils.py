import json

from Crypto.Cipher import DES3
import base64


class DESCipher:
    def __init__(self, key):
        self.bs = 16
        self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = DES3.new(self.key, DES3.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = DES3.new(self.key, DES3.MODE_ECB)
        return self._unpad(cipher.decrypt(enc))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


def xor_crypt_string(data, key, encode=False, decode=False):
    from itertools import izip, cycle
    import base64
    if decode:
        data = base64.b64decode(data)
    xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(data, cycle(key)))
    if encode:
        return base64.b64encode(xored).strip()
    return xored