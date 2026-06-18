# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

import sys

def left_rotate(value, shift):
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

def md5(message):
    # Initial state values
    a = 0x67452301
    b = 0xEFCDAB89
    c = 0x98BADCFE
    d = 0x10325476
    
    # Pre-processing padding
    original_length = len(message)
    message += b'\x80'
    while len(message) % 64 != 56:
        message += b'\x00'
    message += original_length.to_bytes(8, 'little')
    
    # Process 512-bit (64-byte) blocks
    for i in range(0, len(message), 64):
        block = message[i:i+64]
        words = [int.from_bytes(block[j:j+4], 'little') for j in range(0, 64, 4)]
        a0, b0, c0, d0 = a, b, c, d
        
        # 64 compression rounds
        for j in range(64):
            if j < 16:
                f = (b & c) | (~b & d)
                g = j
            elif j < 32:
                f = (d & b) | (~d & c)
                g = (5 * j + 1) % 16
            elif j < 48:
                f = b ^ c ^ d
                g = (3 * j + 5) % 16
            else:
                f = c ^ (b | ~d)
                g = (7 * j) % 16
            
            temp = d
            d = c
            c = b
            b = (b + left_rotate((a + f + 0x5A827999 + words[g]) & 0xFFFFFFFF, 3)) & 0xFFFFFFFF
            a = temp
            
        # Accumulate block hash back to main values
        a = (a + a0) & 0xFFFFFFFF
        b = (b + b0) & 0xFFFFFFFF
        c = (c + c0) & 0xFFFFFFFF
        d = (d + d0) & 0xFFFFFFFF
        
    return '{:08x}{:08x}{:08x}{:08x}'.format(a, b, c, d)

def main():
    # Allow command line inputs or prompt
    if len(sys.argv) > 1:
        input_string = " ".join(sys.argv[1:])
    else:
        input_string = input("Nhập chuỗi cần băm: ")
    
    md5_hash = md5(input_string.encode('utf-8'))
    print("Mã băm MD5 của chuỗi '{}' là: {}".format(input_string, md5_hash))

if __name__ == "__main__":
    main()
