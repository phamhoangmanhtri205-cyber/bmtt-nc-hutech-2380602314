# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QSplitter, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization

class DHMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diffie-Hellman Key Exchange Simulator")
        self.resize(1100, 700)
        
        # Cryptographic states
        self.parameters = None
        self.alice_private = None
        self.alice_public = None
        self.bob_private = None
        self.bob_public = None
        self.alice_shared_secret = None
        self.bob_shared_secret = None
        
        self.init_ui()

    def init_ui(self):
        # Premium Dark-mode Theme with Neon accents
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
                font-size: 11px;
            }
            QPushButton {
                background-color: #6200ee;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
            QPushButton:pressed {
                background-color: #bb86fc;
                color: black;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #888888;
            }
            QFrame#match_frame {
                background-color: #1e1e1e;
                border: 2px dashed #333333;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info
        header_layout = QHBoxLayout()
        title_label = QLabel("DIFFIE-HELLMAN KEY EXCHANGE VISUALIZER")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        author_label = QLabel("Sinh viên: PhamHoangManhTri-2380602314")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        author_label.setStyleSheet("color: #03dac6; font-style: italic;")
        header_layout.addWidget(title_label)
        header_layout.addWidget(author_label)
        main_layout.addLayout(header_layout)

        # Main splitter dividing Alice and Bob
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Alice (Server)
        alice_widget = QWidget()
        alice_layout = QVBoxLayout(alice_widget)
        alice_layout.setContentsMargins(0, 0, 10, 0)
        
        alice_title = QLabel("ALICE (Server / Param Generator)")
        alice_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        alice_title.setStyleSheet("color: #bb86fc;")
        alice_layout.addWidget(alice_title)
        
        self.alice_gen_btn = QPushButton("1. Generate Parameters & Alice Keys")
        self.alice_gen_btn.clicked.connect(self.generate_alice_keys)
        alice_layout.addWidget(self.alice_gen_btn)

        alice_layout.addWidget(QLabel("DH Parameters (p, g):"))
        self.alice_params_txt = QTextEdit()
        self.alice_params_txt.setReadOnly(True)
        alice_layout.addWidget(self.alice_params_txt, 1)

        alice_layout.addWidget(QLabel("Alice Private Key (Private exponent X_A):"))
        self.alice_priv_txt = QTextEdit()
        self.alice_priv_txt.setReadOnly(True)
        alice_layout.addWidget(self.alice_priv_txt, 1)

        alice_layout.addWidget(QLabel("Alice Public Key (Y_A = g^X_A mod p):"))
        self.alice_pub_txt = QTextEdit()
        self.alice_pub_txt.setReadOnly(True)
        alice_layout.addWidget(self.alice_pub_txt, 2)
        
        splitter.addWidget(alice_widget)

        # Right panel: Bob (Client)
        bob_widget = QWidget()
        bob_layout = QVBoxLayout(bob_widget)
        bob_layout.setContentsMargins(10, 0, 0, 0)
        
        bob_title = QLabel("BOB (Client / Key Receiver)")
        bob_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        bob_title.setStyleSheet("color: #03dac6;")
        bob_layout.addWidget(bob_title)
        
        self.bob_gen_btn = QPushButton("2. Read Alice Params & Generate Bob Keys")
        self.bob_gen_btn.clicked.connect(self.generate_bob_keys)
        self.bob_gen_btn.setEnabled(False)
        bob_layout.addWidget(self.bob_gen_btn)

        bob_layout.addWidget(QLabel("Read DH Parameters (Received from Alice):"))
        self.bob_params_txt = QTextEdit()
        self.bob_params_txt.setReadOnly(True)
        bob_layout.addWidget(self.bob_params_txt, 1)

        bob_layout.addWidget(QLabel("Bob Private Key (Private exponent X_B):"))
        self.bob_priv_txt = QTextEdit()
        self.bob_priv_txt.setReadOnly(True)
        bob_layout.addWidget(self.bob_priv_txt, 1)

        bob_layout.addWidget(QLabel("Bob Public Key (Y_B = g^X_B mod p):"))
        self.bob_pub_txt = QTextEdit()
        self.bob_pub_txt.setReadOnly(True)
        bob_layout.addWidget(self.bob_pub_txt, 2)
        
        splitter.addWidget(bob_widget)
        main_layout.addWidget(splitter, 4)

        # Shared Secret Panel (Exchange verification)
        self.exchange_btn = QPushButton("3. Execute Exchange & Calculate Shared Secrets")
        self.exchange_btn.clicked.connect(self.exchange_keys)
        self.exchange_btn.setEnabled(False)
        main_layout.addWidget(self.exchange_btn)

        # Result verification frame
        match_frame = QFrame()
        match_frame.setObjectName("match_frame")
        match_layout = QHBoxLayout(match_frame)
        
        secret_fields_layout = QVBoxLayout()
        secret_fields_layout.addWidget(QLabel("Alice Derived Secret (K_A = Y_B^X_A mod p):"))
        self.alice_secret_txt = QTextEdit()
        self.alice_secret_txt.setReadOnly(True)
        self.alice_secret_txt.setFixedHeight(45)
        secret_fields_layout.addWidget(self.alice_secret_txt)

        secret_fields_layout.addWidget(QLabel("Bob Derived Secret (K_B = Y_A^X_B mod p):"))
        self.bob_secret_txt = QTextEdit()
        self.bob_secret_txt.setReadOnly(True)
        self.bob_secret_txt.setFixedHeight(45)
        secret_fields_layout.addWidget(self.bob_secret_txt)
        
        match_layout.addLayout(secret_fields_layout, 3)

        # Verification Status LED
        self.status_box = QVBoxLayout()
        self.status_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_led = QLabel("PENDING")
        self.status_led.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.status_led.setStyleSheet("color: #888888;")
        self.status_desc = QLabel("Start by generating parameters.")
        self.status_desc.setStyleSheet("color: #888888; font-size: 11px;")
        self.status_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_box.addWidget(self.status_led)
        self.status_box.addWidget(self.status_desc)
        match_layout.addLayout(self.status_box, 1)

        main_layout.addWidget(match_frame, 2)

    def generate_alice_keys(self):
        # Generate DH parameters & Alice pair
        self.alice_params_txt.setPlainText("Generating DH group parameters (modulus size: 2048-bit)... Please wait...")
        QApplication.processEvents() # Refresh UI
        
        self.parameters = dh.generate_parameters(generator=2, key_size=2048)
        self.alice_private = self.parameters.generate_private_key()
        self.alice_public = self.alice_private.public_key()
        
        # Display params
        p_val = self.parameters.parameter_numbers().p
        g_val = self.parameters.parameter_numbers().g
        self.alice_params_txt.setPlainText(f"p (Modulus 2048-bit):\n{hex(p_val)}\n\ng (Generator):\n{g_val}")
        
        # Display keys
        x_a = self.alice_private.private_numbers().x
        self.alice_priv_txt.setPlainText(hex(x_a))
        
        pub_pem = self.alice_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        self.alice_pub_txt.setPlainText(pub_pem)
        
        # Enable Bob
        self.bob_gen_btn.setEnabled(True)
        self.alice_gen_btn.setEnabled(False)
        
        self.status_led.setText("STEP 1 DONE")
        self.status_led.setStyleSheet("color: #bb86fc;")
        self.status_desc.setText("Alice parameters ready. Bob can now read them.")

    def generate_bob_keys(self):
        if not self.parameters:
            return
        
        # Bob reads Alice parameters and generates keys
        p_val = self.parameters.parameter_numbers().p
        g_val = self.parameters.parameter_numbers().g
        self.bob_params_txt.setPlainText(f"p (Received 2048-bit):\n{hex(p_val)}\n\ng (Received):\n{g_val}")
        
        self.bob_private = self.parameters.generate_private_key()
        self.bob_public = self.bob_private.public_key()
        
        # Display keys
        x_b = self.bob_private.private_numbers().x
        self.bob_priv_txt.setPlainText(hex(x_b))
        
        pub_pem = self.bob_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        self.bob_pub_txt.setPlainText(pub_pem)
        
        # Enable Exchange
        self.exchange_btn.setEnabled(True)
        self.bob_gen_btn.setEnabled(False)
        
        self.status_led.setText("STEP 2 DONE")
        self.status_led.setStyleSheet("color: #03dac6;")
        self.status_desc.setText("Bob keys generated. Execute the exchange to derive secrets.")

    def exchange_keys(self):
        if not self.alice_private or not self.bob_private:
            return
            
        # Calculate shared secret
        self.alice_shared_secret = self.alice_private.exchange(self.bob_public)
        self.bob_shared_secret = self.bob_private.exchange(self.alice_public)
        
        alice_hex = self.alice_shared_secret.hex()
        bob_hex = self.bob_shared_secret.hex()
        
        self.alice_secret_txt.setPlainText(alice_hex)
        self.bob_secret_txt.setPlainText(bob_hex)
        
        # Check if secrets match
        if self.alice_shared_secret == self.bob_shared_secret:
            self.status_led.setText("MATCHED ✔")
            self.status_led.setStyleSheet("color: #03dac6; font-size: 24px;")
            self.status_desc.setText("Shared Secrets derived by Alice & Bob are identical!\nK = g^(X_A * X_B) mod p")
            self.setStyleSheet(self.styleSheet() + "\nQFrame#match_frame { border: 2px solid #03dac6; background-color: #092c28; }")
        else:
            self.status_led.setText("ERROR ✖")
            self.status_led.setStyleSheet("color: #cf6679;")
            self.status_desc.setText("Secrets do not match! Check implementation.")
            
        self.exchange_btn.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DHMainWindow()
    window.show()
    sys.exit(app.exec())
