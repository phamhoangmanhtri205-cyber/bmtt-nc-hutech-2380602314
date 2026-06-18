# -*- coding: utf-8 -*-
import sys
import socket
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QLineEdit, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
import tornado.ioloop
import tornado.websocket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

AES_KEY = b'SixteenByteKey!!'

class QtWebSocketWorker(QThread):
    log_signal = pyqtSignal(str, str, str)  # plain_sent, cipher_hex, plain_received
    status_signal = pyqtSignal(str, bool)  # status, is_connected
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.connection = None
        self.io_loop = None
        self.is_connected = False
        self.last_sent_msg = ""

    def run(self):
        self.io_loop = tornado.ioloop.IOLoop()
        self.io_loop.make_current()
        self.status_signal.emit("Connecting to WebSocket...", False)
        
        # Connect asynchronously
        self.io_loop.add_callback(self.connect)
        self.io_loop.start()

    def connect(self):
        tornado.websocket.websocket_connect(
            url=self.url,
            callback=self.on_connect,
            on_message_callback=self.on_message
        )

    def on_connect(self, future):
        try:
            self.connection = future.result()
            self.is_connected = True
            self.status_signal.emit("Connected (AES Active)", True)
        except Exception as e:
            self.status_signal.emit(f"Connection Failed: {e}", False)
            self.io_loop.stop()

    def on_message(self, message):
        if message is None:
            self.status_signal.emit("Disconnected from server.", False)
            self.is_connected = False
            self.io_loop.stop()
            return
            
        try:
            # Decode hex payload
            encrypted_payload = bytes.fromhex(message)
            iv = encrypted_payload[:16]
            ciphertext = encrypted_payload[16:]
            
            # Decrypt AES-CBC
            cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
            decrypted_msg = decrypted_bytes.decode('utf-8')
            
            # Send results to UI thread
            self.log_signal.emit(self.last_sent_msg, message, decrypted_msg)
        except Exception as e:
            self.log_signal.emit(self.last_sent_msg, f"ERROR: {message}", f"Decryption failed: {e}")

    def send_message(self, text):
        if self.is_connected and self.connection:
            self.last_sent_msg = text
            # Write to server in Tornado loop thread
            self.io_loop.add_callback(self.connection.write_message, text)

    def disconnect_client(self):
        self.is_connected = False
        if self.connection:
            self.io_loop.add_callback(self.connection.close)
        if self.io_loop:
            self.io_loop.add_callback(self.io_loop.stop)


class WebSocketMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure WebSocket (AES-CBC) Chat Client")
        self.resize(1000, 600)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Modern Premium Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', Inter, sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #bb86fc;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #bb86fc;
                color: #121212;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9d5fe5;
            }
            QPushButton:pressed {
                background-color: #7b1fa2;
                color: white;
            }
            QPushButton#disconnect_btn {
                background-color: #cf6679;
                color: white;
            }
            QPushButton#disconnect_btn:hover {
                background-color: #ff4d6d;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info
        header_layout = QHBoxLayout()
        title_label = QLabel("SECURE WEBSOCKET CLIENT (AES)")
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        author_label = QLabel("Sinh viên: PhamHoangManhTri-2380602314")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        author_label.setStyleSheet("color: #03dac6; font-style: italic;")
        header_layout.addWidget(title_label)
        header_layout.addWidget(author_label)
        main_layout.addLayout(header_layout)

        # Server config
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Server URL:"))
        self.url_input = QLineEdit("ws://localhost:8889/websocket_aes/")
        conn_layout.addWidget(self.url_input)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_server)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.clicked.connect(self.disconnect_server)
        self.disconnect_btn.setEnabled(False)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #cf6679; margin-left: 15px;")
        conn_layout.addWidget(self.status_label)
        main_layout.addLayout(conn_layout)

        # Main splitter (Keys + Logs)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Parameters
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("Predefined AES Symmetric Key (128-bit):"))
        self.key_display = QLineEdit(AES_KEY.decode('utf-8'))
        self.key_display.setReadOnly(True)
        self.key_display.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333333; font-family: 'Consolas'; color: #03dac6;")
        left_layout.addWidget(self.key_display)
        
        left_layout.addWidget(QLabel("Security Configuration:"))
        self.config_display = QTextEdit()
        self.config_display.setReadOnly(True)
        self.config_display.setFont(QFont("Consolas", 10))
        self.config_display.setPlainText(
            "Protocol: WebSocket (ws://)\n"
            "Server Port: 8889\n"
            "Encryption: AES-128-CBC\n"
            "Padding: PKCS7\n"
            "Exchange format: Hex-encoded (IV + Ciphertext)\n"
            "Key Size: 16 bytes\n"
            "IV Size: 16 bytes (Generated randomly per message)\n"
            "Direction: Client sends Plaintext -> Server Encrypts -> Server returns Ciphertext -> Client Decrypts"
        )
        left_layout.addWidget(self.config_display, 2)
        splitter.addWidget(left_widget)

        # Right panel: Console Log
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel("Secure Transaction Console Logs:"))
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.console_log, 3)

        # Send row
        send_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Enter plaintext message to send...")
        self.msg_input.returnPressed.connect(self.send_message)
        self.msg_input.setEnabled(False)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        send_layout.addWidget(self.msg_input)
        send_layout.addWidget(self.send_btn)
        right_layout.addLayout(send_layout)

        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)

    def connect_server(self):
        url = self.url_input.text()
        self.worker = QtWebSocketWorker(url)
        self.worker.log_signal.connect(self.handle_log)
        self.worker.status_signal.connect(self.handle_status)
        
        self.worker.start()
        
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.url_input.setEnabled(False)

    def disconnect_server(self):
        if self.worker:
            self.worker.disconnect_client()
            self.worker.wait()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.msg_input.setEnabled(False)
        self.send_btn.setEnabled(False)

    def handle_status(self, status, is_connected):
        self.status_label.setText(status)
        if is_connected:
            self.status_label.setStyleSheet("color: #03dac6;")
            self.msg_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.console_log.append("<font color='#03dac6'>*** Secure WebSocket link established. ***</font>")
        else:
            self.status_label.setStyleSheet("color: #cf6679;")
            self.msg_input.setEnabled(False)
            self.send_btn.setEnabled(False)
            if "Offline" in status or "Disconnected" in status or "Failed" in status:
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
                self.url_input.setEnabled(True)

    def handle_log(self, plain_sent, cipher_hex, decrypted):
        self.console_log.append(f"<font color='#bb86fc'><b>[Client Sent]:</b> {plain_sent}</font>")
        self.console_log.append(f"<font color='#e0e0e0'><b>[Server Reply Ciphertext (Hex)]:</b>\n{cipher_hex}</font>")
        self.console_log.append(f"<font color='#03dac6'><b>[Client Decrypted back]:</b> {decrypted}</font>")
        self.console_log.append("-" * 60)
        self.console_log.moveCursor(QTextCursor.MoveOperation.End)

    def send_message(self):
        text = self.msg_input.text()
        if not text:
            return
            
        if self.worker and self.worker.is_connected:
            self.worker.send_message(text)
            self.msg_input.clear()

    def closeEvent(self, event):
        self.disconnect_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebSocketMainWindow()
    window.show()
    sys.exit(app.exec())
