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