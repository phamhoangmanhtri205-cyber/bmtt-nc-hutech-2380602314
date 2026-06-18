# -*- coding: utf-8 -*-
"""
Flask API Server - Lab 03
Cung cấp REST API cho RSA và ECC
"""

from flask import Flask, request, jsonify
from cipher.rsa import RSACipher
from cipher.ecc import ECCCipher

app = Flask(__name__)

rsa_cipher = RSACipher()
ecc_cipher = ECCCipher()


# ─────────────────────────────────────────────
# RSA ROUTES
# ─────────────────────────────────────────────

@app.route("/api/rsa/generate_keys", methods=["POST"])
def rsa_generate_keys():
    try:
        result = rsa_cipher.generate_keys()
        return jsonify({"status": "success", "message": "Đã sinh khóa RSA thành công!", **result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rsa/encrypt", methods=["POST"])
def rsa_encrypt():
    try:
        data = request.json
        plain_text = data.get("plain_text", "")
        encrypted = rsa_cipher.encrypt(plain_text)
        return jsonify({"status": "success", "encrypted_message": encrypted})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rsa/decrypt", methods=["POST"])
def rsa_decrypt():
    try:
        data = request.json
        cipher_text = data.get("cipher_text", "")
        decrypted = rsa_cipher.decrypt(cipher_text)
        return jsonify({"status": "success", "decrypted_message": decrypted})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rsa/sign", methods=["POST"])
def rsa_sign():
    try:
        data = request.json
        message = data.get("message", "")
        signature = rsa_cipher.sign(message)
        return jsonify({"status": "success", "signature": signature})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rsa/verify", methods=["POST"])
def rsa_verify():
    try:
        data = request.json
        message = data.get("message", "")
        signature = data.get("signature", "")
        is_valid = rsa_cipher.verify(message, signature)
        return jsonify({
            "status": "success",
            "is_valid": is_valid,
            "result": "Chữ ký HỢP LỆ ✓" if is_valid else "Chữ ký KHÔNG hợp lệ ✗"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─────────────────────────────────────────────
# ECC ROUTES
# ─────────────────────────────────────────────

@app.route("/api/ecc/generate_keys", methods=["POST"])
def ecc_generate_keys():
    try:
        result = ecc_cipher.generate_keys()
        return jsonify({"status": "success", "message": "Đã sinh khóa ECC thành công!", **result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ecc/sign", methods=["POST"])
def ecc_sign():
    try:
        data = request.json
        message = data.get("message", "")
        signature = ecc_cipher.sign(message)
        return jsonify({"status": "success", "signature": signature})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ecc/verify", methods=["POST"])
def ecc_verify():
    try:
        data = request.json
        message = data.get("message", "")
        signature = data.get("signature", "")
        is_valid = ecc_cipher.verify(message, signature)
        return jsonify({
            "status": "success",
            "is_valid": is_valid,
            "result": "Chữ ký HỢP LỆ ✓" if is_valid else "Chữ ký KHÔNG hợp lệ ✗"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
