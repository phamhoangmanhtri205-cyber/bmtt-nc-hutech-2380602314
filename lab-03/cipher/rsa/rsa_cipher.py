# -*- coding: utf-8 -*-
"""
RSA Cipher Module
Cung cấp các chức năng: sinh khóa, mã hóa, giải mã, ký số, xác thực chữ ký
"""

import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "privateKey.pem")
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "publicKey.pem")


class RSACipher:
    def generate_keys(self, bits=2048):
        """Sinh cặp khóa RSA và lưu vào thư mục keys/"""
        os.makedirs(KEYS_DIR, exist_ok=True)
        key = RSA.generate(bits)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(private_key)
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(public_key)

        return {
            "private_key": private_key.decode(),
            "public_key": public_key.decode()
        }

    def load_keys(self):
        """Đọc khóa từ file"""
        if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
            raise FileNotFoundError("Chưa có khóa! Vui lòng sinh khóa trước.")

        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = RSA.import_key(f.read())
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = RSA.import_key(f.read())

        return private_key, public_key

    def encrypt(self, plain_text: str) -> str:
        """Mã hóa bằng public key, trả về chuỗi base64"""
        _, public_key = self.load_keys()
        cipher = PKCS1_OAEP.new(public_key)
        encrypted = cipher.encrypt(plain_text.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, cipher_text_b64: str) -> str:
        """Giải mã bằng private key"""
        private_key, _ = self.load_keys()
        cipher = PKCS1_OAEP.new(private_key)
        decrypted = cipher.decrypt(base64.b64decode(cipher_text_b64))
        return decrypted.decode("utf-8")

    def sign(self, message: str) -> str:
        """Ký số bằng private key, trả về chữ ký base64"""
        private_key, _ = self.load_keys()
        h = SHA256.new(message.encode("utf-8"))
        signature = pkcs1_15.new(private_key).sign(h)
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, message: str, signature_b64: str) -> bool:
        """Xác thực chữ ký bằng public key"""
        try:
            _, public_key = self.load_keys()
            h = SHA256.new(message.encode("utf-8"))
            pkcs1_15.new(public_key).verify(h, base64.b64decode(signature_b64))
            return True
        except (ValueError, TypeError):
            return False
