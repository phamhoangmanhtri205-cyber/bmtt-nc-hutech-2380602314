# -*- coding: utf-8 -*-

import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

import random
import tornado.ioloop
import tornado.web
import tornado.websocket

class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()
    
    def check_origin(self, origin):
        # Allow connections from any origin (crucial for local testing and UI apps)
        return True

    def open(self):
        print("New client connected to WebSocket.")
        WebSocketServer.clients.add(self)
        
    def on_close(self):
        print("Client disconnected from WebSocket.")
        WebSocketServer.clients.remove(self)
        
    @classmethod
    def send_message(cls, message: str):
        print(f"Sending message '{message}' to {len(cls.clients)} client(s).")
        for client in cls.clients:
            try:
                client.write_message(message)
            except Exception as e:
                print(f"Error sending message: {e}")

class RandomWordSelector:
    def __init__(self, word_list):
        self.word_list = word_list
        
    def sample(self):
        return random.choice(self.word_list)

def main():
    app = tornado.web.Application(
        [
            (r"/websocket/", WebSocketServer),
        ],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )
    # Port 8888 is specified in client connection page 149
    app.listen(8888)
    print("Tornado WebSocket Server running on ws://localhost:8888/websocket/")
    
    io_loop = tornado.ioloop.IOLoop.current()
    
    word_selector = RandomWordSelector(['apple', 'banana', 'orange', 'grape', 'melon'])
    
    # Send random fruit every 3000ms (3 seconds)
    periodic_callback = tornado.ioloop.PeriodicCallback(
        lambda: WebSocketServer.send_message(word_selector.sample()), 3000
    )
    periodic_callback.start()
    
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("\nShutting down Tornado WebSocket server...")
        periodic_callback.stop()
        io_loop.stop()

if __name__ == "__main__":
    main()
