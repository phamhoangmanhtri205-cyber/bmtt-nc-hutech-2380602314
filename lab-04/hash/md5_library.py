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

def calculate_md5(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()

def main():
    if len(sys.argv) > 1:
        input_string = " ".join(sys.argv[1:])
    else:
        input_string = input("Nhập chuỗi cần băm: ")
    
    md5_hash = calculate_md5(input_string)
    print("Mã băm MD5 của chuỗi '{}' là: {}".format(input_string, md5_hash))

if __name__ == "__main__":
    main()
