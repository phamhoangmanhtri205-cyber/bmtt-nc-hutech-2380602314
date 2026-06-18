# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from Crypto.Hash import SHA3_256
import sys

def sha3(message):
    sha3_hash = SHA3_256.new()
    sha3_hash.update(message)
    return sha3_hash.digest()

def main():
    if len(sys.argv) > 1:
        text_str = " ".join(sys.argv[1:])
    else:
        text_str = input("Nhập chuỗi văn bản: ")
        
    text = text_str.encode('utf-8')
    hashed_text = sha3(text)
    print("Chuỗi văn bản đã nhập:", text.decode('utf-8'))
    print("SHA-3 Hash:", hashed_text.hex())

if __name__ == "__main__":
    main()
