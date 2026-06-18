# -*- coding: utf-8 -*-
"""
ECC Cipher Module
Cung cấp các chức năng: sinh khóa, ký số, xác thực chữ ký
Sử dụng thư viện ecdsa với đường cong SECP256k1
"""

import os
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "privateKey.pem")
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "publicKey.pem")


class ECCCipher:
    def generate_keys(self):
        """Sinh cặp khóa ECC và lưu vào thư mục keys/"""
        os.makedirs(KEYS_DIR, exist_ok=True)
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()

        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(sk.to_pem())
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(vk.to_pem())

        return {
            "private_key": sk.to_pem().decode(),
            "public_key": vk.to_pem().decode()
        }

    def load_keys(self):
        """Đọc khóa từ file"""
        if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
            raise FileNotFoundError("Chưa có khóa ECC! Vui lòng sinh khóa trước.")

        with open(PRIVATE_KEY_FILE, "rb") as f:
            sk = SigningKey.from_pem(f.read())
        with open(PUBLIC_KEY_FILE, "rb") as f:
            vk = VerifyingKey.from_pem(f.read())

        return sk, vk

    def sign(self, message: str) -> str:
        """Ký số bằng private key, trả về chữ ký base64"""
        sk, _ = self.load_keys()
        signature = sk.sign(message.encode("utf-8"))
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, message: str, signature_b64: str) -> bool:
        """Xác thực chữ ký bằng public key"""
        try:
            _, vk = self.load_keys()
            vk.verify(base64.b64decode(signature_b64), message.encode("utf-8"))
            return True
        except (BadSignatureError, Exception):
            return False
