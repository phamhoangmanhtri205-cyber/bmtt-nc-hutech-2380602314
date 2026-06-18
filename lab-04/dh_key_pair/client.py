# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
import os

def generate_client_key_pair(parameters):
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

def derive_shared_secret(private_key, server_public_key):
    shared_key = private_key.exchange(server_public_key)
    return shared_key

def main():
    pub_pem_path = "server_public_key.pem"
    if not os.path.exists(pub_pem_path):
        print(f"Error: {pub_pem_path} not found. Please run server.py first to generate it!")
        return

    # Load server's public key
    print(f"Loading Server Public Key from '{pub_pem_path}'...")
    with open(pub_pem_path, "rb") as f:
        server_public_key = serialization.load_pem_public_key(f.read())
    
    # Extract DH parameters from Server's Public Key
    parameters = server_public_key.parameters()
    
    # Generate Client's Key Pair
    print("Generating Client DH Key Pair based on server's parameters...")
    private_key, public_key = generate_client_key_pair(parameters)
    
    # Derive Shared Secret
    print("Performing Diffie-Hellman Key Exchange...")
    shared_secret = derive_shared_secret(private_key, server_public_key)
    
    # Print the derived Shared Secret in Hex
    print("\n--- Key Exchange Completed Successfully ---")
    print(f"Shared Secret (Hex representation):\n{shared_secret.hex()}")
    print("------------------------------------------")

if __name__ == "__main__":
    main()
