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
import tornado.web
import tornado.websocket
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Fixed 16-byte key for demo purposes
AES_KEY = b'SixteenByteKey!!'

class SecureWebSocketServer(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("New client connected to SECURE WebSocket (AES).")

    def on_message(self, message):
        print(f"Received plaintext from client: {message}")
        try:
            # Generate random IV
            iv = get_random_bytes(16)
            cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
            
            # Encrypt
            padded_data = pad(message.encode('utf-8'), AES.block_size)
            ciphertext = cipher.encrypt(padded_data)
            
            # Combine IV and ciphertext and encode to Hex
            encrypted_payload = (iv + ciphertext).hex()
            print(f"Encrypted payload: {encrypted_payload}")
            
            # Send back to client
            self.write_message(encrypted_payload)
        except Exception as e:
            print(f"Error encrypting message: {e}")
            self.write_message(f"Error: {e}")

    def on_close(self):
        print("Client disconnected from SECURE WebSocket.")

def main():
    app = tornado.web.Application([
        (r"/websocket_aes/", SecureWebSocketServer),
    ])
    app.listen(8889)
    print("Tornado SECURE WebSocket Server running on ws://localhost:8889/websocket_aes/")
    
    io_loop = tornado.ioloop.IOLoop.current()
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("\nShutting down Secure WebSocket server...")
        io_loop.stop()

if __name__ == "__main__":
    main()
