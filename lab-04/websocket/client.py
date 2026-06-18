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
import sys

class WebSocketClient:
    def __init__(self, io_loop):
        self.connection = None
        self.io_loop = io_loop
        
    def start(self):
        self.connect_and_read()
        
    def stop(self):
        self.io_loop.stop()
        
    def connect_and_read(self):
        print("Reading...")
        tornado.websocket.websocket_connect(
            url="ws://localhost:8888/websocket/",
            callback=self.maybe_retry_connection,
            on_message_callback=self.on_message,
            ping_interval=10,
            ping_timeout=30,
        )
        
    def maybe_retry_connection(self, future):
        try:
            self.connection = future.result()
            print("Connected to WebSocket server.")
        except Exception as e:
            print("Could not reconnect, retrying in 3 seconds...")
            self.io_loop.call_later(3, self.connect_and_read)
            
    def on_message(self, message):
        if message is None:
            print("Disconnected, reconnecting...")
            self.connect_and_read()
            return
        print(f"Received word from server: {message}")
        
        # Sách trang 156 dòng 40 yêu cầu gọi read_message.
        # Bọc trong try/except để tránh crash trên một số bản Tornado mới do trùng lặp callback.
        try:
            self.connection.read_message(callback=self.on_message)
        except Exception:
            pass

def main():
    io_loop = tornado.ioloop.IOLoop.current()
    client = WebSocketClient(io_loop)
    io_loop.add_callback(client.start)
    print("Tornado WebSocket client starting...")
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("\nShutting down Tornado client...")
        io_loop.stop()

if __name__ == "__main__":
    main()
