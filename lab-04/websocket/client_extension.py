# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

import tornado.ioloop
import tornado.websocket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import sys

# Fixed 16-byte key matching the server
AES_KEY = b'SixteenByteKey!!'

class SecureWebSocketClient:
    def __init__(self, io_loop):
        self.connection = None
        self.io_loop = io_loop

    def start(self):
        self.connect()

    def connect(self):
        print("Connecting to secure WebSocket server...")
        tornado.websocket.websocket_connect(
            url="ws://localhost:8889/websocket_aes/",
            callback=self.on_connect,
            on_message_callback=self.on_message
        )

    def on_connect(self, future):
        try:
            self.connection = future.result()
            print("Connected to Secure WebSocket Server (AES).")
            # Start console input thread once connected
            threading.Thread(target=self.console_input_loop, daemon=True).start()
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 3 seconds...")
            self.io_loop.call_later(3, self.connect)

    def on_message(self, message):
        if message is None:
            print("\nDisconnected from server.")
            self.io_loop.stop()
            return
            
        print(f"\n[Received Ciphertext (Hex)]: {message}")
        try:
            # Decode hex
            encrypted_payload = bytes.fromhex(message)
            iv = encrypted_payload[:16]
            ciphertext = encrypted_payload[16:]
            
            # Decrypt AES-CBC
            cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
            decrypted_msg = decrypted_bytes.decode('utf-8')
            print(f"[Decrypted Plaintext]: {decrypted_msg}")
        except Exception as e:
            print(f"Decryption failed: {e}")
            
        print("\nEnter message to encrypt: ", end="", flush=True)

    def console_input_loop(self):
        try:
            while True:
                msg = input("Enter message to encrypt: ")
                if msg == "exit":
                    self.io_loop.add_callback(self.close_connection)
                    break
                if msg:
                    # Write message to server via Tornado IO Loop safely
                    self.io_loop.add_callback(self.connection.write_message, msg)
        except (KeyboardInterrupt, SystemExit):
            self.io_loop.add_callback(self.close_connection)

    def close_connection(self):
        if self.connection:
            self.connection.close()
        self.io_loop.stop()

def main():
    io_loop = tornado.ioloop.IOLoop.current()
    client = SecureWebSocketClient(io_loop)
    io_loop.add_callback(client.start)
    print("Tornado Secure Client starting...")
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("\nExiting client...")
        io_loop.stop()

if __name__ == "__main__":
    main()
