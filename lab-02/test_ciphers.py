import sys
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher
from cipher.railfence import RailFenceCipher
from cipher.playfair import PlayfairCipher
from cipher.transposition import TranspositionCipher

def test_caesar():
    cipher = CaesarCipher()
    plain = "HELLOWORLD"
    key = 3
    enc = cipher.encrypt_text(plain, key)
    dec = cipher.decrypt_text(enc, key)
    assert dec == plain, f"Caesar failed: {dec} != {plain}"
    print("[OK] Caesar Cipher Test Passed")

def test_vigenere():
    cipher = VigenereCipher()
    plain = "HELLOWORLD"
    key = "KEY"
    enc = cipher.encrypt_text(plain, key)
    dec = cipher.decrypt_text(enc, key)
    assert dec == plain, f"Vigenere failed: {dec} != {plain}"
    print("[OK] Vigenere Cipher Test Passed")

def test_railfence():
    cipher = RailFenceCipher()
    plain = "HELLOWORLD"
    key = 3
    enc = cipher.encrypt_text(plain, key)
    dec = cipher.decrypt_text(enc, key)
    assert dec == plain, f"Rail Fence failed: {dec} != {plain}"
    print("[OK] Rail Fence Cipher Test Passed")

def test_playfair():
    cipher = PlayfairCipher()
    plain = "HELLOWORLD" # playfair replaces duplicates in pair and J->I, pads with X
    key = "MONARCHY"
    enc = cipher.encrypt_text(plain, key)
    dec = cipher.decrypt_text(enc, key)
    # The expected output for decrypted should match the prepared text
    prepared = cipher._prepare_text(plain)
    assert dec == prepared, f"Playfair failed: {dec} != {prepared}"
    print("[OK] Playfair Cipher Test Passed")

def test_transposition():
    cipher = TranspositionCipher()
    plain = "HELLOWORLD"
    key = 4
    enc = cipher.encrypt_text(plain, key)
    dec = cipher.decrypt_text(enc, key)
    assert dec == plain, f"Transposition failed: {dec} != {plain}"
    print("[OK] Transposition Cipher Test Passed")

if __name__ == "__main__":
    try:
        test_caesar()
        test_vigenere()
        test_railfence()
        test_playfair()
        test_transposition()
        print("\nAll cipher algorithms passed successfully!")
    except AssertionError as e:
        print(f"Assertion Error: {e}")
        sys.exit(1)
