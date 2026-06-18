# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import socket
import threading
import hashlib
import sys

# Initialize client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to server localhost:12345...")
client_socket.connect(('localhost', 12345))
print("Connected to server.")

# Generate RSA key pair
print("Generating RSA-2048 key pair for client...")
client_key = RSA.generate(2048)
print("Client RSA keys generated.")

# Receive server's public key
server_pub_data = client_socket.recv(2048)
server_public_key = RSA.import_key(server_pub_data)
print("Received server's RSA public key.")

# Send client's public key to the server
client_pub_pem = client_key.publickey().export_key(format='PEM')
client_socket.send(client_pub_pem)
print("Sent client's RSA public key to server.")

# Receive encrypted AES key from the server
encrypted_aes_key = client_socket.recv(2048)
print("Received encrypted AES key.")

# Decrypt the AES key using client's private key
cipher_rsa = PKCS1_OAEP.new(client_key)
aes_key = cipher_rsa.decrypt(encrypted_aes_key)
print(f"Decrypted AES Key successfully: {aes_key.hex()}")

# Function to encrypt message
def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return cipher.iv + ciphertext

# Function to decrypt message
def decrypt_message(key, encrypted_message):
    iv = encrypted_message[:AES.block_size]
    ciphertext = encrypted_message[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_message.decode('utf-8')

# Function to receive messages from server
def receive_messages():
    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                print("\nConnection closed by server.")
                break
            decrypted_message = decrypt_message(aes_key, encrypted_message)
            # In ra màn hình nhưng không đè lên prompt input nếu đang nhập
            print(f"\n[Received] {decrypted_message}")
            print("Enter message ('exit' to quit): ", end="", flush=True)
        except Exception as e:
            print("\nDisconnected from server.")
            break

# Start the receiving thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Send messages from the client
try:
    while True:
        message = input("Enter message ('exit' to quit): ")
        if not message:
            continue
        encrypted_message = encrypt_message(aes_key, message)
        client_socket.send(encrypted_message)
        if message == "exit":
            break
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    client_socket.close()
    print("Connection closed.")
