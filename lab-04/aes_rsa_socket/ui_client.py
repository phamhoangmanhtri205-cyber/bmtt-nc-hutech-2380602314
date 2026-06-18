# -*- coding: utf-8 -*-
import sys
import socket
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QLineEdit, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class ClientWorker(QThread):
    log_signal = pyqtSignal(str) # message to print in chat
    raw_signal = pyqtSignal(str) # raw ciphertext log
    status_signal = pyqtSignal(str, bool) # status, is_connected
    keys_established_signal = pyqtSignal(str, str, str) # client_rsa_pub, server_rsa_pub, aes_key_hex

    def __init__(self, host, port, nickname):
        super().__init__()
        self.host = host
        self.port = port
        self.nickname = nickname
        self.client_socket = None
        self.aes_key = None
        self.is_connected = False

    def run(self):
        try:
            self.status_signal.emit("Connecting to server...", False)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_connected = True
            self.status_signal.emit("Connected. Establishing security...", False)

            # Generate RSA keys for client
            client_key = RSA.generate(2048)
            client_pub_pem = client_key.publickey().export_key(format='PEM').decode('utf-8')

            # Receive server's public key
            server_pub_data = self.client_socket.recv(2048)
            if not server_pub_data:
                raise ConnectionError("Server disconnected during handshake.")
            server_public_key = RSA.import_key(server_pub_data)
            server_pub_pem = server_pub_data.decode('utf-8')

            # Send client public key
            self.client_socket.send(client_key.publickey().export_key(format='PEM'))

            # Receive encrypted AES key
            encrypted_aes_key = self.client_socket.recv(2048)
            if not encrypted_aes_key:
                raise ConnectionError("Server disconnected during key exchange.")
            
            # Decrypt AES key
            cipher_rsa = PKCS1_OAEP.new(client_key)
            self.aes_key = cipher_rsa.decrypt(encrypted_aes_key)
            aes_hex = self.aes_key.hex()

            # Emit credentials to UI
            self.keys_established_signal.emit(client_pub_pem, server_pub_pem, aes_hex)
            self.status_signal.emit(f"Connected as {self.nickname} (AES Secured)", True)

            while self.is_connected:
                encrypted_msg = self.client_socket.recv(1024)
                if not encrypted_msg:
                    break
                
                self.raw_signal.emit(encrypted_msg.hex())
                msg = self.decrypt_message(self.aes_key, encrypted_msg)
                self.log_signal.emit(msg)
                
        except Exception as e:
            self.status_signal.emit(f"Error: {e}", False)
        finally:
            self.disconnect_client()

    def disconnect_client(self):
        self.is_connected = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        self.status_signal.emit("Disconnected.", False)

    def encrypt_message(self, key, message):
        cipher = AES.new(key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        return cipher.iv + ciphertext

    def decrypt_message(self, key, encrypted_message):
        iv = encrypted_message[:AES.block_size]
        ciphertext = encrypted_message[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted_message.decode('utf-8')

    def send_chat(self, msg_text):
        if self.client_socket and self.aes_key:
            try:
                encrypted = self.encrypt_message(self.aes_key, msg_text)
                self.client_socket.send(encrypted)
                return True
            except Exception as e:
                self.log_signal.emit(f"System: Failed to send. {e}")
        return False


class ClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure AES-RSA Chat Client")
        self.resize(1050, 680)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Modern Premium Dark-mode Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', Inter, sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #03dac6;
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
                background-color: #03dac6;
                color: #121212;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b3a6;
            }
            QPushButton:pressed {
                background-color: #018786;
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
        title_label = QLabel("SECURE CHAT CLIENT")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        author_label = QLabel("Sinh viên: PhamHoangManhTri-2380602314")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        author_label.setStyleSheet("color: #bb86fc; font-style: italic;")
        header_layout.addWidget(title_label)
        header_layout.addWidget(author_label)
        main_layout.addLayout(header_layout)

        # Connection Config Row
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Nickname:"))
        self.nickname_input = QLineEdit("Alice")
        self.nickname_input.setFixedWidth(120)
        conn_layout.addWidget(self.nickname_input)

        conn_layout.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit("localhost")
        self.host_input.setFixedWidth(120)
        conn_layout.addWidget(self.host_input)

        conn_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("12345")
        self.port_input.setFixedWidth(80)
        conn_layout.addWidget(self.port_input)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_server)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.clicked.connect(self.disconnect_server)
        self.disconnect_btn.setEnabled(False)
        
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)
        conn_layout.addStretch()
        
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: #cf6679;")
        conn_layout.addWidget(self.status_label)
        main_layout.addLayout(conn_layout)

        # Body Layout (Splitter)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Security parameters & cryptos
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("Decrypted Session AES Key:"))
        self.aes_key_display = QLineEdit()
        self.aes_key_display.setReadOnly(True)
        self.aes_key_display.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333333; font-family: 'Consolas'; color: #03dac6;")
        left_layout.addWidget(self.aes_key_display)
        
        left_layout.addWidget(QLabel("Client RSA Key Pair:"))
        self.client_rsa_display = QTextEdit()
        self.client_rsa_display.setReadOnly(True)
        self.client_rsa_display.setFont(QFont("Consolas", 9))
        left_layout.addWidget(self.client_rsa_display, 2)
        
        left_layout.addWidget(QLabel("Server RSA Public Key (Handshaked):"))
        self.server_rsa_display = QTextEdit()
        self.server_rsa_display.setReadOnly(True)
        self.server_rsa_display.setFont(QFont("Consolas", 9))
        left_layout.addWidget(self.server_rsa_display, 2)
        
        splitter.addWidget(left_widget)

        # Right panel: Chat messages and sending
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel("Chat Messages (AES Decrypted):"))
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display, 3)

        # Raw Encrypted Hex Log
        right_layout.addWidget(QLabel("Raw Incoming Ciphertext Stream (Hex):"))
        self.raw_display = QTextEdit()
        self.raw_display.setReadOnly(True)
        self.raw_display.setFixedHeight(80)
        self.raw_display.setStyleSheet("color: #888888; font-family: 'Consolas'; font-size: 10px;")
        right_layout.addWidget(self.raw_display)

        # Sending area
        send_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type a message to send secure...")
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
        host = self.host_input.text()
        port = int(self.port_input.text())
        nickname = self.nickname_input.text()

        self.worker = ClientWorker(host, port, nickname)
        self.worker.log_signal.connect(self.handle_log)
        self.worker.raw_signal.connect(self.handle_raw)
        self.worker.status_signal.connect(self.handle_status)
        self.worker.keys_established_signal.connect(self.handle_keys_established)
        
        self.worker.start()
        
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.nickname_input.setEnabled(False)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)

    def disconnect_server(self):
        if self.worker:
            self.worker.disconnect_client()
            self.worker.wait()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.nickname_input.setEnabled(True)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.msg_input.setEnabled(False)
        self.send_btn.setEnabled(False)

    def handle_status(self, status, is_connected):
        self.status_label.setText(f"Status: {status}")
        if is_connected:
            self.status_label.setStyleSheet("color: #03dac6;")
            self.msg_input.setEnabled(True)
            self.send_btn.setEnabled(True)
        else:
            self.status_label.setStyleSheet("color: #cf6679;")
            self.msg_input.setEnabled(False)
            self.send_btn.setEnabled(False)
            if status == "Disconnected.":
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
                self.nickname_input.setEnabled(True)
                self.host_input.setEnabled(True)
                self.port_input.setEnabled(True)

    def handle_keys_established(self, client_rsa, server_rsa, aes_hex):
        self.client_rsa_display.setPlainText(client_rsa)
        self.server_rsa_display.setPlainText(server_rsa)
        self.aes_key_display.setText(aes_hex)
        self.chat_display.append("<font color='#03dac6'>*** RSA Key exchange completed. Session AES Key established. ***</font>")

    def handle_log(self, text):
        self.chat_display.append(text)
        # Scroll to bottom
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def handle_raw(self, hex_data):
        self.raw_display.append(hex_data)
        self.raw_display.moveCursor(QTextCursor.MoveOperation.End)

    def send_message(self):
        text = self.msg_input.text()
        if not text:
            return
        
        nickname = self.nickname_input.text()
        full_msg = f"{nickname}: {text}"
        
        if self.worker and self.worker.send_chat(text):
            self.chat_display.append(f"<b>You:</b> {text}")
            self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            self.msg_input.clear()
            if text == "exit":
                self.disconnect_server()

    def closeEvent(self, event):
        self.disconnect_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientMainWindow()
    window.show()
    sys.exit(app.exec())
