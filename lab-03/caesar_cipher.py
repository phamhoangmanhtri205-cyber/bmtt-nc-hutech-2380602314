# -*- coding: utf-8 -*-
"""
Ứng dụng Desktop Caesar Cipher
Kết nối với Flask API của lab-02 (port 5000)
"""

import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox, QFrame,
    QGroupBox, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

API_BASE = "http://127.0.0.1:5000/api"


class ApiWorker(QThread):
    """Worker thread để gọi API không block UI"""
    result = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self):
        try:
            resp = requests.post(self.url, json=self.payload, timeout=5)
            self.result.emit(resp.json())
        except requests.ConnectionError:
            self.error.emit("Không kết nối được với server lab-02!\nHãy chạy: cd lab-02 && python api.py")
        except Exception as e:
            self.error.emit(str(e))


class CaesarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Caesar Cipher - Lab 03")
        self.setMinimumSize(700, 600)
        self._setup_style()
        self._setup_ui()

    def _setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget#central {
                background-color: #1a1a2e;
            }
            QGroupBox {
                color: #e94560;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #e94560;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #a8b2d8;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #16213e;
                color: #ccd6f6;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }
            QTextEdit:focus {
                border: 1px solid #e94560;
            }
            QLineEdit {
                background-color: #16213e;
                color: #ccd6f6;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #e94560;
            }
            QPushButton {
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                color: white;
            }
            QPushButton#btn_encrypt {
                background-color: #e94560;
                border: none;
            }
            QPushButton#btn_encrypt:hover {
                background-color: #c73652;
            }
            QPushButton#btn_encrypt:pressed {
                background-color: #a02840;
            }
            QPushButton#btn_decrypt {
                background-color: #0f3460;
                border: 2px solid #e94560;
            }
            QPushButton#btn_decrypt:hover {
                background-color: #16213e;
            }
            QPushButton#btn_clear {
                background-color: #2a2a4a;
                border: 1px solid #4a4a6a;
                color: #a8b2d8;
            }
            QPushButton#btn_clear:hover {
                background-color: #3a3a5a;
            }
            QStatusBar {
                background-color: #0f3460;
                color: #a8b2d8;
            }
        """)

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("🔐 CAESAR CIPHER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e94560; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Ứng dụng Mã hoá / Giải mã Caesar — Kết nối Lab-02 API")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8892b0; font-size: 11px;")
        layout.addWidget(subtitle)

        # Key input
        key_group = QGroupBox("🔑 Khóa (Key)")
        key_layout = QHBoxLayout(key_group)
        key_layout.addWidget(QLabel("Nhập key (số nguyên):"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Ví dụ: 3")
        self.key_input.setText("3")
        self.key_input.setMaximumWidth(200)
        key_layout.addWidget(self.key_input)
        key_layout.addStretch()
        layout.addWidget(key_group)

        # Plain text
        plain_group = QGroupBox("📝 Plain Text (Văn bản gốc)")
        plain_layout = QVBoxLayout(plain_group)
        self.plain_text = QTextEdit()
        self.plain_text.setPlaceholderText("Nhập văn bản cần mã hoá...")
        self.plain_text.setMinimumHeight(100)
        plain_layout.addWidget(self.plain_text)
        layout.addWidget(plain_group)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_encrypt = QPushButton("🔒 MÃ HOÁ")
        self.btn_encrypt.setObjectName("btn_encrypt")
        self.btn_encrypt.clicked.connect(self.encrypt)
        self.btn_encrypt.setMinimumHeight(45)

        self.btn_decrypt = QPushButton("🔓 GIẢI MÃ")
        self.btn_decrypt.setObjectName("btn_decrypt")
        self.btn_decrypt.clicked.connect(self.decrypt)
        self.btn_decrypt.setMinimumHeight(45)

        self.btn_clear = QPushButton("🗑 Xoá")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear.setMinimumHeight(45)
        self.btn_clear.setMaximumWidth(100)

        btn_layout.addWidget(self.btn_encrypt)
        btn_layout.addWidget(self.btn_decrypt)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        # Cipher text
        cipher_group = QGroupBox("🔐 Cipher Text (Văn bản đã mã hoá)")
        cipher_layout = QVBoxLayout(cipher_group)
        self.cipher_text = QTextEdit()
        self.cipher_text.setPlaceholderText("Kết quả sẽ xuất hiện ở đây...")
        self.cipher_text.setMinimumHeight(100)
        cipher_layout.addWidget(self.cipher_text)
        layout.addWidget(cipher_group)

        # Status bar
        self.statusBar().showMessage("Sẵn sàng | Đang kết nối Lab-02 tại port 5000")

    def encrypt(self):
        plain = self.plain_text.toPlainText().strip()
        key = self.key_input.text().strip()
        if not plain:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập văn bản cần mã hoá!")
            return
        if not key.lstrip('-').isdigit():
            QMessageBox.warning(self, "Cảnh báo", "Key phải là số nguyên!")
            return

        self.btn_encrypt.setEnabled(False)
        self.statusBar().showMessage("Đang mã hoá...")
        self.worker = ApiWorker(f"{API_BASE}/caesar/encrypt", {"plain_text": plain, "key": int(key)})
        self.worker.result.connect(self._on_encrypt_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_encrypt_result(self, data):
        self.btn_encrypt.setEnabled(True)
        self.cipher_text.setText(data.get("encrypted_message", str(data)))
        self.statusBar().showMessage("✅ Mã hoá thành công!")

    def decrypt(self):
        cipher = self.cipher_text.toPlainText().strip()
        key = self.key_input.text().strip()
        if not cipher:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập văn bản cần giải mã!")
            return
        if not key.lstrip('-').isdigit():
            QMessageBox.warning(self, "Cảnh báo", "Key phải là số nguyên!")
            return

        self.btn_decrypt.setEnabled(False)
        self.statusBar().showMessage("Đang giải mã...")
        self.worker = ApiWorker(f"{API_BASE}/caesar/decrypt", {"cipher_text": cipher, "key": int(key)})
        self.worker.result.connect(self._on_decrypt_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_decrypt_result(self, data):
        self.btn_decrypt.setEnabled(True)
        self.plain_text.setText(data.get("decrypted_message", str(data)))
        self.statusBar().showMessage("✅ Giải mã thành công!")

    def _on_error(self, msg):
        self.btn_encrypt.setEnabled(True)
        self.btn_decrypt.setEnabled(True)
        QMessageBox.critical(self, "Lỗi kết nối", msg)
        self.statusBar().showMessage("❌ Lỗi!")

    def clear_all(self):
        self.plain_text.clear()
        self.cipher_text.clear()
        self.statusBar().showMessage("Đã xoá")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = CaesarApp()
    window.show()
    sys.exit(app.exec())
