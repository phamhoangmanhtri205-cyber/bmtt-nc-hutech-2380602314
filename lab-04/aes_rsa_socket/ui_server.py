# -*- coding: utf-8 -*-
import sys
import socket
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class ServerWorker(QThread):
    log_signal = pyqtSignal(str, str, str)  # client_addr, raw_hex, decrypted_text
    client_connect_signal = pyqtSignal(str, str) # client_addr, aes_key_hex
    client_disconnect_signal = pyqtSignal(str) # client_addr
    server_status_signal = pyqtSignal(str) # status message
    key_signal = pyqtSignal(str) # server public key pem

    def __init__(self, host='localhost', port=12345):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.clients = {}  # socket: (address, aes_key)
        self.clients_lock = threading.Lock()
        self.server_socket = None

    def run(self):
        # Generate RSA key pair
        self.server_status_signal.emit("Generating RSA-2048 keys...")
        self.server_key = RSA.generate(2048)
        self.key_signal.emit(self.server_key.publickey().export_key(format='PEM').decode('utf-8'))
        
        # Start socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            self.server_status_signal.emit(f"Server listening on {self.host}:{self.port}")
        except Exception as e:
            self.server_status_signal.emit(f"Failed to bind: {e}")
            return

        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                addr_str = f"{client_address[0]}:{client_address[1]}"
                threading.Thread(target=self.handle_client, args=(client_socket, addr_str), daemon=True).start()
            except Exception:
                break

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.clients_lock:
            for sock in list(self.clients.keys()):
                sock.close()
            self.clients.clear()
        self.server_status_signal.emit("Server stopped.")

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

    def handle_client(self, client_socket, addr_str):
        try:
            # Send server's public key
            client_socket.send(self.server_key.publickey().export_key(format='PEM'))
            
            # Receive client's public key
            client_pub_data = client_socket.recv(2048)
            if not client_pub_data:
                return
            client_received_key = RSA.import_key(client_pub_data)
            
            # Generate AES key
            aes_key = get_random_bytes(16)
            aes_key_hex = aes_key.hex()
            
            # Encrypt & send AES key
            cipher_rsa = PKCS1_OAEP.new(client_received_key)
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)
            client_socket.send(encrypted_aes_key)
            
            # Save client info
            with self.clients_lock:
                self.clients[client_socket] = (addr_str, aes_key)
            self.client_connect_signal.emit(addr_str, aes_key_hex)
            
            while self.running:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break
                
                raw_hex = encrypted_message.hex()
                decrypted_message = self.decrypt_message(aes_key, encrypted_message)
                
                # Emit signal to update UI
                self.log_signal.emit(addr_str, raw_hex, decrypted_message)
                
                # Broadcast
                with self.clients_lock:
                    for sock, (other_addr, other_key) in self.clients.items():
                        if sock != client_socket:
                            try:
                                encrypted = self.encrypt_message(other_key, f"{addr_str}: {decrypted_message}")
                                sock.send(encrypted)
                            except Exception:
                                pass
                if decrypted_message == "exit":
                    break
        except Exception as e:
            pass
        finally:
            client_socket.close()
            with self.clients_lock:
                if client_socket in self.clients:
                    del self.clients[client_socket]
            self.client_disconnect_signal.emit(addr_str)


class ServerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure AES-RSA Chat Server")
        self.resize(1000, 650)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Modern Dark Palette
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
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #f5f5f5;
                font-family: 'Consolas', monospace;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #f5f5f5;
            }
            QPushButton {
                background-color: #3700b3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6200ee;
            }
            QPushButton:pressed {
                background-color: #bb86fc;
            }
            QPushButton#stop_btn {
                background-color: #cf6679;
            }
            QPushButton#stop_btn:hover {
                background-color: #ff4d6d;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info
        header_layout = QHBoxLayout()
        title_label = QLabel("SECURE MULTI-CLIENT SOCKET SERVER")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        author_label = QLabel("Sinh viên: PhamHoangManhTri-2380602314")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        author_label.setStyleSheet("color: #03dac6; font-style: italic;")
        header_layout.addWidget(title_label)
        header_layout.addWidget(author_label)
        main_layout.addLayout(header_layout)

        # Control Panel
        control_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Server Offline")
        self.status_label.setStyleSheet("color: #cf6679;")
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        main_layout.addLayout(control_layout)

        # Body Layout using QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Keys & Connections
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("Server RSA Public Key:"))
        self.pub_key_text = QTextEdit()
        self.pub_key_text.setReadOnly(True)
        left_layout.addWidget(self.pub_key_text, 2)
        
        left_layout.addWidget(QLabel("Active Clients & Session AES Keys:"))
        self.client_list = QListWidget()
        left_layout.addWidget(self.client_list, 3)
        
        splitter.addWidget(left_widget)

        # Right panel: Server Console Logs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("Decrypted Chat / Log stream:"))
        self.decrypted_log = QTextEdit()
        self.decrypted_log.setReadOnly(True)
        right_layout.addWidget(self.decrypted_log, 3)

        right_layout.addWidget(QLabel("Raw Encrypted Packets (Hex IV + Ciphertext):"))
        self.raw_log = QTextEdit()
        self.raw_log.setReadOnly(True)
        right_layout.addWidget(self.raw_log, 2)
        
        splitter.addWidget(right_widget)
        
        main_layout.addWidget(splitter)

    def start_server(self):
        self.worker = ServerWorker()
        self.worker.log_signal.connect(self.handle_log)
        self.worker.client_connect_signal.connect(self.handle_connect)
        self.worker.client_disconnect_signal.connect(self.handle_disconnect)
        self.worker.server_status_signal.connect(self.handle_status)
        self.worker.key_signal.connect(self.handle_keys)
        
        self.worker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_server(self):
        if self.worker:
            self.worker.stop_server()
            self.worker.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.client_list.clear()

    def handle_status(self, text):
        self.status_label.setText(f"Status: {text}")
        if "listening" in text.lower():
            self.status_label.setStyleSheet("color: #03dac6;")
        elif "offline" in text.lower() or "stopped" in text.lower():
            self.status_label.setStyleSheet("color: #cf6679;")

    def handle_keys(self, pem_text):
        self.pub_key_text.setPlainText(pem_text)

    def handle_connect(self, addr, aes_hex):
        item = QListWidgetItem(f"🔌 {addr} | AES: {aes_hex[:16]}...")
        item.setToolTip(f"Full AES Session Key:\n{aes_hex}")
        item.setData(Qt.ItemDataRole.UserRole, addr)
        self.client_list.addItem(item)
        self.decrypted_log.append(f"<font color='#03dac6'>*** Client {addr} connected. Shared AES Key established. ***</font>")

    def handle_disconnect(self, addr):
        # Find and remove client item
        for i in range(self.client_list.count()):
            item = self.client_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == addr:
                self.client_list.takeItem(i)
                break
        self.decrypted_log.append(f"<font color='#cf6679'>*** Client {addr} disconnected. ***</font>")

    def handle_log(self, addr, raw_hex, msg):
        self.decrypted_log.append(f"<b>{addr}:</b> {msg}")
        self.raw_log.append(f"<font color='#888888'>[{addr}] -> IV+Ciphertext Hex:\n{raw_hex[:120]}...</font>\n")

    def closeEvent(self, event):
        self.stop_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerMainWindow()
    window.show()
    sys.exit(app.exec())
