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

# Initialize server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)
print("Server is listening on localhost:12345...")

# Generate RSA key pair
print("Generating RSA-2048 key pair for server...")
server_key = RSA.generate(2048)
print("Server RSA keys generated.")

# List of connected clients (client_socket, aes_key)
clients = []
clients_lock = threading.Lock()

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

# Function to handle client connection
def handle_client(client_socket, client_address):
    print(f"Connected with {client_address}")
    try:
        # Send server's public key to client
        server_pub_pem = server_key.publickey().export_key(format='PEM')
        client_socket.send(server_pub_pem)
        
        # Receive client's public key
        client_pub_data = client_socket.recv(2048)
        if not client_pub_data:
            return
        client_received_key = RSA.import_key(client_pub_data)
        
        # Generate AES key for message encryption (16 bytes = AES-128)
        aes_key = get_random_bytes(16)
        
        # Encrypt the AES key using the client's public key
        cipher_rsa = PKCS1_OAEP.new(client_received_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)
        client_socket.send(encrypted_aes_key)
        
        # Add client to the list securely
        with clients_lock:
            clients.append((client_socket, aes_key))
            
        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            
            decrypted_message = decrypt_message(aes_key, encrypted_message)
            print(f"Received from {client_address}: {decrypted_message}")
            
            # Send received message to all other clients
            with clients_lock:
                for client, key in clients:
                    if client != client_socket:
                        try:
                            # Re-encrypt for each client with their respective AES key
                            encrypted = encrypt_message(key, f"{client_address}: {decrypted_message}")
                            client.send(encrypted)
                        except Exception as e:
                            print(f"Failed to send to client: {e}")
            
            if decrypted_message == "exit":
                break
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        # Securely remove client
        with clients_lock:
            # Find and remove
            for item in clients:
                if item[0] == client_socket:
                    clients.remove(item)
                    break
        client_socket.close()
        print(f"Connection with {client_address} closed")

def main():
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
