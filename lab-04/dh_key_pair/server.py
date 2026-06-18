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

def generate_dh_parameters():
    print("Generating DH parameters (key_size=2048)... This might take a moment...")
    parameters = dh.generate_parameters(generator=2, key_size=2048)
    return parameters

def generate_server_key_pair(parameters):
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

def main():
    # Generate parameters and key pair
    parameters = generate_dh_parameters()
    private_key, public_key = generate_server_key_pair(parameters)
    
    # Write Server Public Key to PEM
    pub_pem_path = "server_public_key.pem"
    with open(pub_pem_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"Server Public Key saved successfully to '{pub_pem_path}'")
    print(f"PEM Content Preview:\n{public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')[:200]}...")

if __name__ == "__main__":
    main()
