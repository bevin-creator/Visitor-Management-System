#AES-256 encryption with Hash-based Message Authentication (HMAC-SHA256) / Protects PII at rest

import os
import hmac
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

from app.config import settings

#getting two keys from master, one for encry and another for hmac
def get_keys():
    master = settings.ENCRYPTION_KEY.encode()
    enc_key = hashlib.sha256(master + b"encryption").digest() # 32 bytes (AES-256)
    hmac_key = hashlib.sha256(master + b"authentication").digest() #32 bytes (hmac-sha256)
    return enc_key, hmac_key

#encrypting string (visitor data are of string data type) and attaches hmac for tamper detection
def encrypt_field(plaintext: str) -> str:
    if not plaintext:
        return plaintext

    enc_key, hmac_key = get_keys()

    #random initial vector(iv) ensuring same input produces different output each time
    iv = os.urandom(16)

    #padding (adding extra bytes) plaintext to AES (128 bits)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    #encrypt with AES-256-CBC
    cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data)+encryptor.finalize()

    #combining iv + cyphertext
    payload = iv + ciphertext

    #hmac over pyload
    mac = hmac.new(hmac_key, payload, hashlib.sha256).digest()

    return base64.b64encode(mac+payload).decode()


def decrypt_field(ciphertext: str) -> str:
    if not ciphertext:
        return ciphertext

    try:

        enc_key, hmac_key = get_keys()

        raw = base64.b64decode(ciphertext.encode())

        #split 32bytes hmac, next 16 iv and the rest encrypted data
        stored_mac = raw[:32]
        payload = raw[32:]
        iv = payload[:16]
        encrypted_data = payload[16:]

        #verify hmac
        computed_mac = hmac.new(hmac_key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(stored_mac, computed_mac):
            raise ValueError("Data integrity check failed!")

        #decrypt with AES-256-CBC
        cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data)+decryptor.finalize()

        #remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data)+unpadder.finalize()


        return plaintext.decode()
    except Exception:
        return ciphertext # added in case of stored plain text data stored without encryption

#not sure if this is the right approach.


