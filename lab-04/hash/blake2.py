# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

import hashlib
import sys

def blake2(message):
    blake2_hash = hashlib.blake2b(digest_size=64)
    blake2_hash.update(message)
    return blake2_hash.digest()

def main():
    if len(sys.argv) > 1:
        text_str = " ".join(sys.argv[1:])
    else:
        text_str = input("Nhập chuỗi văn bản: ")
        
    text = text_str.encode('utf-8')
    hashed_text = blake2(text)
    print("Chuỗi văn bản đã nhập:", text.decode('utf-8'))
    print("BLAKE2 Hash:", hashed_text.hex())

if __name__ == "__main__":
    main()
