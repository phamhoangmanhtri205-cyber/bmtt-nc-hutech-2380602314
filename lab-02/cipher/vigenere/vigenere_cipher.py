class VigenereCipher:
    def __init__(self):
        pass

    def encrypt_text(self, text: str, key: str) -> str:
        text = text.upper()
        key = key.upper()
        encrypted_text = []
        key_index = 0
        for char in text:
            if char.isalpha():
                # Shift by key character
                shift = ord(key[key_index % len(key)]) - ord('A')
                encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                encrypted_text.append(encrypted_char)
                key_index += 1
            else:
                encrypted_text.append(char)
        return "".join(encrypted_text)

    def decrypt_text(self, text: str, key: str) -> str:
        text = text.upper()
        key = key.upper()
        decrypted_text = []
        key_index = 0
        for char in text:
            if char.isalpha():
                shift = ord(key[key_index % len(key)]) - ord('A')
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                decrypted_text.append(decrypted_char)
                key_index += 1
            else:
                decrypted_text.append(char)
        return "".join(decrypted_text)
