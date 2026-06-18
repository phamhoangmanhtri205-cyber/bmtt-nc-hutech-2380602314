# -*- coding: utf-8 -*-
import sys
import time
import hashlib
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QComboBox, QFileDialog, QTabWidget, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from Crypto.Hash import SHA3_256

# Import our custom MD5 logic
from md5_hash import md5 as custom_md5

class HashMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Hashing Tool & Benchmark")
        self.resize(900, 620)
        self.selected_file_path = None
        self.init_ui()

    def init_ui(self):
        # Premium Dark Theme with harmonious color scheme
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
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #ffffff;
                font-family: 'Consolas', monospace;
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
            QPushButton#compare_btn {
                background-color: #bb86fc;
                color: #121212;
            }
            QPushButton#compare_btn:hover {
                background-color: #9d5fe5;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                background: #121212;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #1e1e1e;
                color: #888888;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #121212;
                color: #03dac6;
                border-bottom: 2px solid #03dac6;
                font-weight: bold;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info
        header_layout = QHBoxLayout()
        title_label = QLabel("SECURE HASHING & PERFORMANCE BENCHMARK")
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        author_label = QLabel("Sinh viên: PhamHoangManhTri-2380602314")
        author_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        author_label.setStyleSheet("color: #bb86fc; font-style: italic;")
        header_layout.addWidget(title_label)
        header_layout.addWidget(author_label)
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: Hash Generator
        self.tab_hash = QWidget()
        self.init_hash_tab()
        self.tabs.addTab(self.tab_hash, "Hash Generator")

        # TAB 2: Performance Comparison
        self.tab_perf = QWidget()
        self.init_perf_tab()
        self.tabs.addTab(self.tab_perf, "Performance Comparison (MD5)")

    def init_hash_tab(self):
        layout = QVBoxLayout(self.tab_hash)

        # Input text area
        layout.addWidget(QLabel("Input Text / String:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter text here to generate hash...")
        self.input_text.textChanged.connect(self.clear_file_selection)
        layout.addWidget(self.input_text, 2)

        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Or hash a file: None selected")
        self.file_label.setStyleSheet("color: #888888; font-style: italic; font-weight: normal;")
        self.select_file_btn = QPushButton("Select File...")
        self.select_file_btn.clicked.connect(self.select_file)
        self.clear_file_btn = QPushButton("Clear File")
        self.clear_file_btn.clicked.connect(self.clear_file)
        self.clear_file_btn.setEnabled(False)
        
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        file_layout.addWidget(self.select_file_btn)
        file_layout.addWidget(self.clear_file_btn)
        layout.addLayout(file_layout)

        # Hashing config row
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Hash Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems([
            "MD5 (Custom - Simplified)",
            "MD5 (Library - Standard)",
            "SHA-256",
            "SHA-3 (SHA3_256)",
            "BLAKE2 (Blake2b)"
        ])
        config_layout.addWidget(self.algo_combo)
        
        self.hash_btn = QPushButton("Generate Hash")
        self.hash_btn.clicked.connect(self.generate_hash)
        config_layout.addWidget(self.hash_btn)
        layout.addLayout(config_layout)

        # Output hex digest
        layout.addWidget(QLabel("Hex Digest Output:"))
        self.output_hash = QTextEdit()
        self.output_hash.setReadOnly(True)
        self.output_hash.setFont(QFont("Consolas", 12))
        layout.addWidget(self.output_hash, 1)

        # Metadata output
        self.meta_label = QLabel("Hash Details: (character length, bit strength will appear here)")
        self.meta_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.meta_label)

    def init_perf_tab(self):
        layout = QVBoxLayout(self.tab_perf)

        layout.addWidget(QLabel("Benchmark Parameters:"))
        desc_label = QLabel("Compare execution speeds between our Custom Simplified MD5 algorithm (toy MD5) and Python's native optimized hashlib.md5 library.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888; font-weight: normal; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Loop iterations selection
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("Iterations:"))
        self.iter_combo = QComboBox()
        self.iter_combo.addItems(["1,000", "5,000", "10,000", "50,000"])
        self.iter_combo.setCurrentText("10,000")
        iter_layout.addWidget(self.iter_combo)
        
        self.compare_btn = QPushButton("Run Speed Test")
        self.compare_btn.setObjectName("compare_btn")
        self.compare_btn.clicked.connect(self.run_benchmark)
        iter_layout.addWidget(self.compare_btn)
        iter_layout.addStretch()
        layout.addLayout(iter_layout)

        # Results visualization using custom ProgressBars as horizontal bar graph
        layout.addWidget(QLabel("Performance Results:"))
        
        self.custom_bar_label = QLabel("Custom Simplified MD5: -- seconds")
        layout.addWidget(self.custom_bar_label)
        self.custom_bar = QProgressBar()
        self.custom_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 4px;
                background-color: #1e1e1e;
                text-align: right;
                color: transparent;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #bb86fc;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.custom_bar)

        self.lib_bar_label = QLabel("Library Standard MD5: -- seconds")
        layout.addWidget(self.lib_bar_label)
        self.lib_bar = QProgressBar()
        self.lib_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 4px;
                background-color: #1e1e1e;
                text-align: right;
                color: transparent;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #03dac6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.lib_bar)

        # Conclusion Text
        self.conclusion_txt = QTextEdit()
        self.conclusion_txt.setReadOnly(True)
        self.conclusion_txt.setStyleSheet("background-color: #1a1a1a; border: 1px solid #292929;")
        layout.addWidget(self.conclusion_txt)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Hash")
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(f"File selected: {file_path.split('/')[-1]}")
            self.input_text.clear()
            self.input_text.setEnabled(False)
            self.clear_file_btn.setEnabled(True)

    def clear_file(self):
        self.selected_file_path = None
        self.file_label.setText("Or hash a file: None selected")
        self.input_text.setEnabled(True)
        self.clear_file_btn.setEnabled(False)

    def clear_file_selection(self):
        if self.input_text.toPlainText() and self.selected_file_path:
            self.clear_file()

    def generate_hash(self):
        algo = self.algo_combo.currentText()
        
        # Get data bytes
        if self.selected_file_path:
            try:
                with open(self.selected_file_path, 'rb') as f:
                    data = f.read()
            except Exception as e:
                self.output_hash.setPlainText(f"Error reading file: {e}")
                return
        else:
            data = self.input_text.toPlainText().encode('utf-8')

        # Hashing logic
        start_time = time.perf_counter()
        if algo == "MD5 (Custom - Simplified)":
            hashed = custom_md5(data)
            bit_len = 128
        elif algo == "MD5 (Library - Standard)":
            hashed = hashlib.md5(data).hexdigest()
            bit_len = 128
        elif algo == "SHA-256":
            hashed = hashlib.sha256(data).hexdigest()
            bit_len = 256
        elif algo == "SHA-3 (SHA3_256)":
            h = SHA3_256.new(data)
            hashed = h.hexdigest()
            bit_len = 256
        elif algo == "BLAKE2 (Blake2b)":
            hashed = hashlib.blake2b(data, digest_size=64).hexdigest()
            bit_len = 512
        else:
            hashed = "Invalid algorithm selection"
            bit_len = 0
        end_time = time.perf_counter()

        self.output_hash.setPlainText(hashed)
        
        # Display details
        char_len = len(hashed)
        elapsed_ms = (end_time - start_time) * 1000
        self.meta_label.setText(
            f"Hash Details: Algorithm: {algo} | Output Length: {char_len} hex characters ({bit_len} bits) | "
            f"Execution Time: {elapsed_ms:.4f} ms"
        )

    def run_benchmark(self):
        iterations_str = self.iter_combo.currentText().replace(",", "")
        iterations = int(iterations_str)

        test_data = b"benchmark test string for md5 hashing algorithms"
        
        self.conclusion_txt.setPlainText("Running performance tests... Please wait...")
        self.compare_btn.setEnabled(False)
        QApplication.processEvents()

        # Benchmarking custom MD5
        start = time.perf_counter()
        for _ in range(iterations):
            _ = custom_md5(test_data)
        custom_time = time.perf_counter() - start

        # Benchmarking library MD5
        start = time.perf_counter()
        for _ in range(iterations):
            m = hashlib.md5()
            m.update(test_data)
            _ = m.hexdigest()
        lib_time = time.perf_counter() - start

        self.compare_btn.setEnabled(True)

        # Update bars & labels
        self.custom_bar_label.setText(f"Custom Simplified MD5: {custom_time:.5f} seconds")
        self.lib_bar_label.setText(f"Library Standard MD5: {lib_time:.5f} seconds")
        
        # Normalize bar values (max time = 100%)
        max_time = max(custom_time, lib_time)
        if max_time > 0:
            custom_val = int((custom_time / max_time) * 100)
            lib_val = int((lib_time / max_time) * 100)
        else:
            custom_val, lib_val = 0, 0
            
        self.custom_bar.setValue(custom_val)
        self.lib_bar.setValue(lib_val)

        # Print conclusion
        speedup = custom_time / lib_time if lib_time > 0 else 0
        conclusion = (
            f"--- Benchmark Conclusion ---\n"
            f"Tested input size: {len(test_data)} bytes\n"
            f"Iterations run: {iterations:,}\n\n"
            f"1. Library MD5 is written in highly optimized native C wrapper, completing in {lib_time*1000:.2f} ms.\n"
            f"2. Custom MD5 is written in interpreted pure Python, completing in {custom_time*1000:.2f} ms.\n\n"
            f"➡ The native C library version is approximately {speedup:.1f}x FASTER than the pure Python version!\n"
            f"This clearly illustrates the efficiency of C compiled libraries for intensive cryptographic operations."
        )
        self.conclusion_txt.setPlainText(conclusion)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashMainWindow()
    window.show()
    sys.exit(app.exec())
