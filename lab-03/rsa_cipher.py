# -*- coding: utf-8 -*-
"""
Ứng dụng Desktop RSA Cipher
Kết nối với Flask API của lab-03 (port 5001)
Chức năng: Sinh khóa, Mã hóa, Giải mã, Ký số, Xác thực chữ ký
"""

import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox, QGroupBox,
    QTabWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

API_BASE = "http://127.0.0.1:5001/api/rsa"


class ApiWorker(QThread):
    result = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url, payload=None):
        super().__init__()
        self.url = url
        self.payload = payload or {}

    def run(self):
        try:
            resp = requests.post(self.url, json=self.payload, timeout=10)
            self.result.emit(resp.json())
        except requests.ConnectionError:
            self.error.emit("Không kết nối được với server lab-03!\nHãy chạy: cd lab-03 && python api.py")
        except Exception as e:
            self.error.emit(str(e))


DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0d1117;
}
QTabWidget::pane {
    border: 1px solid #30363d;
    background: #0d1117;
}
QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 10px 20px;
    font-size: 12px;
    border: 1px solid #30363d;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #21262d;
    color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}
QGroupBox {
    color: #58a6ff;
    font-size: 12px;
    font-weight: bold;
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLabel {
    color: #8b949e;
    font-size: 11px;
}
QTextEdit {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
QTextEdit:focus {
    border: 1px solid #58a6ff;
}
QPushButton {
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 16px;
    color: white;
    border: none;
    min-height: 40px;
}
QPushButton#btn_primary {
    background-color: #238636;
}
QPushButton#btn_primary:hover { background-color: #2ea043; }
QPushButton#btn_danger {
    background-color: #da3633;
}
QPushButton#btn_danger:hover { background-color: #f85149; }
QPushButton#btn_info {
    background-color: #1f6feb;
}
QPushButton#btn_info:hover { background-color: #388bfd; }
QPushButton#btn_warning {
    background-color: #9e6a03;
}
QPushButton#btn_warning:hover { background-color: #d29922; }
QPushButton#btn_secondary {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #8b949e;
}
QPushButton#btn_secondary:hover { background-color: #30363d; }
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    font-size: 11px;
}
"""


class KeyTab(QWidget):
    """Tab: Sinh khóa"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        lbl = QLabel("Nhấn nút bên dưới để sinh cặp khóa RSA 2048-bit mới.\nKhóa sẽ được lưu vào thư mục cipher/rsa/keys/")
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #8b949e; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(lbl)

        self.btn_gen = QPushButton("🔑 SINH CẶP KHÓA RSA")
        self.btn_gen.setObjectName("btn_primary")
        self.btn_gen.setMinimumHeight(50)
        self.btn_gen.clicked.connect(self.generate_keys)
        layout.addWidget(self.btn_gen)

        pub_group = QGroupBox("🔓 Public Key")
        pub_layout = QVBoxLayout(pub_group)
        self.pub_key_display = QTextEdit()
        self.pub_key_display.setReadOnly(True)
        self.pub_key_display.setPlaceholderText("Public key sẽ hiển thị ở đây...")
        self.pub_key_display.setMinimumHeight(130)
        pub_layout.addWidget(self.pub_key_display)
        layout.addWidget(pub_group)

        priv_group = QGroupBox("🔒 Private Key")
        priv_layout = QVBoxLayout(priv_group)
        self.priv_key_display = QTextEdit()
        self.priv_key_display.setReadOnly(True)
        self.priv_key_display.setPlaceholderText("Private key sẽ hiển thị ở đây...")
        self.priv_key_display.setMinimumHeight(130)
        priv_layout.addWidget(self.priv_key_display)
        layout.addWidget(priv_group)
        layout.addStretch()

    def generate_keys(self):
        self.btn_gen.setEnabled(False)
        self.btn_gen.setText("⏳ Đang sinh khóa...")
        self.parent.statusBar().showMessage("Đang sinh khóa RSA 2048-bit...")
        self.worker = ApiWorker(f"{API_BASE}/generate_keys")
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_result(self, data):
        self.btn_gen.setEnabled(True)
        self.btn_gen.setText("🔑 SINH CẶP KHÓA RSA")
        if data.get("status") == "success":
            self.pub_key_display.setText(data.get("public_key", ""))
            self.priv_key_display.setText(data.get("private_key", ""))
            self.parent.statusBar().showMessage("✅ Sinh khóa RSA thành công! Khóa đã lưu vào cipher/rsa/keys/")
        else:
            QMessageBox.critical(self, "Lỗi", data.get("message", "Lỗi không xác định"))

    def _on_error(self, msg):
        self.btn_gen.setEnabled(True)
        self.btn_gen.setText("🔑 SINH CẶP KHÓA RSA")
        QMessageBox.critical(self, "Lỗi kết nối", msg)
        self.parent.statusBar().showMessage("❌ Lỗi kết nối!")


class EncryptTab(QWidget):
    """Tab: Mã hóa & Giải mã"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        plain_group = QGroupBox("📝 Plain Text")
        plain_layout = QVBoxLayout(plain_group)
        self.plain_text = QTextEdit()
        self.plain_text.setPlaceholderText("Nhập văn bản cần mã hoá...")
        self.plain_text.setMinimumHeight(100)
        plain_layout.addWidget(self.plain_text)
        layout.addWidget(plain_group)

        btn_layout = QHBoxLayout()
        self.btn_enc = QPushButton("🔒 MÃ HOÁ")
        self.btn_enc.setObjectName("btn_info")
        self.btn_enc.clicked.connect(self.encrypt)

        self.btn_dec = QPushButton("🔓 GIẢI MÃ")
        self.btn_dec.setObjectName("btn_warning")
        self.btn_dec.clicked.connect(self.decrypt)

        self.btn_clear = QPushButton("🗑 Xoá")
        self.btn_clear.setObjectName("btn_secondary")
        self.btn_clear.setMaximumWidth(90)
        self.btn_clear.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.btn_enc)
        btn_layout.addWidget(self.btn_dec)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        cipher_group = QGroupBox("🔐 Cipher Text (Base64)")
        cipher_layout = QVBoxLayout(cipher_group)
        self.cipher_text = QTextEdit()
        self.cipher_text.setPlaceholderText("Kết quả mã hoá sẽ xuất hiện ở đây...")
        self.cipher_text.setMinimumHeight(130)
        cipher_layout.addWidget(self.cipher_text)
        layout.addWidget(cipher_group)

    def encrypt(self):
        plain = self.plain_text.toPlainText().strip()
        if not plain:
            QMessageBox.warning(self, "Cảnh báo", "Nhập văn bản cần mã hoá!")
            return
        self.btn_enc.setEnabled(False)
        self.parent.statusBar().showMessage("Đang mã hoá RSA...")
        self.worker = ApiWorker(f"{API_BASE}/encrypt", {"plain_text": plain})
        self.worker.result.connect(self._on_enc_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_enc_result(self, data):
        self.btn_enc.setEnabled(True)
        if data.get("status") == "success":
            self.cipher_text.setText(data.get("encrypted_message", ""))
            self.parent.statusBar().showMessage("✅ Mã hoá RSA thành công!")
        else:
            QMessageBox.critical(self, "Lỗi", data.get("message", ""))

    def decrypt(self):
        cipher = self.cipher_text.toPlainText().strip()
        if not cipher:
            QMessageBox.warning(self, "Cảnh báo", "Nhập cipher text cần giải mã!")
            return
        self.btn_dec.setEnabled(False)
        self.parent.statusBar().showMessage("Đang giải mã RSA...")
        self.worker = ApiWorker(f"{API_BASE}/decrypt", {"cipher_text": cipher})
        self.worker.result.connect(self._on_dec_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_dec_result(self, data):
        self.btn_dec.setEnabled(True)
        if data.get("status") == "success":
            self.plain_text.setText(data.get("decrypted_message", ""))
            self.parent.statusBar().showMessage("✅ Giải mã RSA thành công!")
        else:
            QMessageBox.critical(self, "Lỗi", data.get("message", ""))

    def _on_error(self, msg):
        self.btn_enc.setEnabled(True)
        self.btn_dec.setEnabled(True)
        QMessageBox.critical(self, "Lỗi kết nối", msg)
        self.parent.statusBar().showMessage("❌ Lỗi!")

    def clear_all(self):
        self.plain_text.clear()
        self.cipher_text.clear()


class SignVerifyTab(QWidget):
    """Tab: Ký số & Xác thực"""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        msg_group = QGroupBox("📩 Thông điệp (Message)")
        msg_layout = QVBoxLayout(msg_group)
        self.message = QTextEdit()
        self.message.setPlaceholderText("Nhập thông điệp cần ký...")
        self.message.setMinimumHeight(90)
        msg_layout.addWidget(self.message)
        layout.addWidget(msg_group)

        btn_layout = QHBoxLayout()
        self.btn_sign = QPushButton("✍ KÝ SỐ")
        self.btn_sign.setObjectName("btn_primary")
        self.btn_sign.clicked.connect(self.sign)

        self.btn_verify = QPushButton("✅ XÁC THỰC")
        self.btn_verify.setObjectName("btn_info")
        self.btn_verify.clicked.connect(self.verify)

        self.btn_clear = QPushButton("🗑 Xoá")
        self.btn_clear.setObjectName("btn_secondary")
        self.btn_clear.setMaximumWidth(90)
        self.btn_clear.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.btn_sign)
        btn_layout.addWidget(self.btn_verify)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        sig_group = QGroupBox("🖊 Chữ ký số (Signature - Base64)")
        sig_layout = QVBoxLayout(sig_group)
        self.signature = QTextEdit()
        self.signature.setPlaceholderText("Chữ ký sẽ xuất hiện ở đây (hoặc nhập để xác thực)...")
        self.signature.setMinimumHeight(100)
        sig_layout.addWidget(self.signature)
        layout.addWidget(sig_group)

        result_group = QGroupBox("📋 Kết quả xác thực")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel("—")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.result_label.setStyleSheet("color: #8b949e; padding: 10px;")
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_group)

    def sign(self):
        msg = self.message.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Cảnh báo", "Nhập thông điệp cần ký!")
            return
        self.btn_sign.setEnabled(False)
        self.parent.statusBar().showMessage("Đang ký số RSA...")
        self.worker = ApiWorker(f"{API_BASE}/sign", {"message": msg})
        self.worker.result.connect(self._on_sign_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_sign_result(self, data):
        self.btn_sign.setEnabled(True)
        if data.get("status") == "success":
            self.signature.setText(data.get("signature", ""))
            self.result_label.setText("✍ Đã tạo chữ ký số!")
            self.result_label.setStyleSheet("color: #3fb950; padding: 10px; font-size: 14px; font-weight: bold;")
            self.parent.statusBar().showMessage("✅ Ký số RSA thành công!")
        else:
            QMessageBox.critical(self, "Lỗi", data.get("message", ""))

    def verify(self):
        msg = self.message.toPlainText().strip()
        sig = self.signature.toPlainText().strip()
        if not msg or not sig:
            QMessageBox.warning(self, "Cảnh báo", "Nhập cả thông điệp và chữ ký!")
            return
        self.btn_verify.setEnabled(False)
        self.parent.statusBar().showMessage("Đang xác thực chữ ký RSA...")
        self.worker = ApiWorker(f"{API_BASE}/verify", {"message": msg, "signature": sig})
        self.worker.result.connect(self._on_verify_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_verify_result(self, data):
        self.btn_verify.setEnabled(True)
        if data.get("status") == "success":
            is_valid = data.get("is_valid", False)
            result_text = data.get("result", "")
            self.result_label.setText(result_text)
            if is_valid:
                self.result_label.setStyleSheet("color: #3fb950; padding: 10px; font-size: 14px; font-weight: bold;")
                self.parent.statusBar().showMessage("✅ Chữ ký HỢP LỆ!")
            else:
                self.result_label.setStyleSheet("color: #f85149; padding: 10px; font-size: 14px; font-weight: bold;")
                self.parent.statusBar().showMessage("❌ Chữ ký KHÔNG hợp lệ!")
        else:
            QMessageBox.critical(self, "Lỗi", data.get("message", ""))

    def _on_error(self, msg):
        self.btn_sign.setEnabled(True)
        self.btn_verify.setEnabled(True)
        QMessageBox.critical(self, "Lỗi kết nối", msg)
        self.parent.statusBar().showMessage("❌ Lỗi kết nối!")

    def clear_all(self):
        self.message.clear()
        self.signature.clear()
        self.result_label.setText("—")
        self.result_label.setStyleSheet("color: #8b949e; padding: 10px;")


class RSAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔑 RSA Cipher - Lab 03")
        self.setMinimumSize(750, 650)
        self.setStyleSheet(DARK_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔑 RSA CIPHER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff; margin-bottom: 2px;")
        layout.addWidget(title)

        subtitle = QLabel("Rivest–Shamir–Adleman — Mã hoá khóa công khai | Lab-03 API port 5001")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(subtitle)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(KeyTab(self), "🔑 Sinh Khóa")
        self.tabs.addTab(EncryptTab(self), "🔒 Mã hoá / Giải mã")
        self.tabs.addTab(SignVerifyTab(self), "✍ Ký số / Xác thực")
        layout.addWidget(self.tabs)

        self.statusBar().showMessage("Sẵn sàng | Kết nối Lab-03 API tại port 5001")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = RSAApp()
    window.show()
    sys.exit(app.exec())
