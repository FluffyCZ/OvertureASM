from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.highlighter import OvertureHighlighter
from assembler import assemble 

class ZoomableTextEditor(QTextEdit):
    def wheelEvent(self, event):
        # If user is holding CTRL
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
        else:
            super().wheelEvent(event)

class AssemblerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Overture ISA Assembler & Multi-Tool")
        self.resize(900, 600)
        self.setStyleSheet("QMainWindow { background-color: #262526; color: white; } QLabel { color: white; }")

        main_layout = QHBoxLayout()

        # --- LEFT SIDE ---
        left_layout = QVBoxLayout()
        
        # Header for the left side with Open Button
        left_header = QHBoxLayout()
        left_header.addWidget(QLabel("<b>Assembly Code:</b>"))
        
        self.open_btn = QPushButton("📂 Open .asm file")
        self.open_btn.setStyleSheet("padding: 4px;")
        self.open_btn.clicked.connect(self.open_file)
        left_header.addWidget(self.open_btn)
        
        left_layout.addLayout(left_header)

        self.input_editor = ZoomableTextEditor()
        self.input_editor.setPlaceholderText("Enter assembly code here...")

        editor_font = QFont("Consolas", 11)
        self.input_editor.setFont(editor_font)

        self.input_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #3f3f46;
            }
        """)

        # Syntax highlighter
        self.highlighter = OvertureHighlighter(self.input_editor.document())

        self.input_editor.setPlainText("start:\n    imm 15\n    mov %r1, %in\n    add\n    mov %out, %r3\n    jmp start")
        left_layout.addWidget(self.input_editor)

        # --- RIGHT SIDE ---
        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel("<b>Output format / Action:</b>"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Binary strings to .txt (8 bit per line)",
            "Plain binary file (.bin for EEPROM)",
            "HEX output to .txt",
            "Only show in app (Debug table)"
        ])
        right_layout.addWidget(self.format_combo)

        self.compile_btn = QPushButton("Translate and Save/Show")
        self.compile_btn.setStyleSheet("background-color: #2b5b84; color: white; font-weight: bold; padding: 8px;")
        self.compile_btn.clicked.connect(self.process_assembly)
        right_layout.addWidget(self.compile_btn)

        right_layout.addWidget(QLabel("<b>Output / Log:</b>"))
        self.output_viewer = QTextEdit()
        self.output_viewer.setReadOnly(True)
        self.output_viewer.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas;")
        right_layout.addWidget(self.output_viewer)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Assembly File", "", "Assembly files (*.asm *.txt);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_editor.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open file: {e}")

    def process_assembly(self):
        asm_code = self.input_editor.toPlainText()
        selected_mode = self.format_combo.currentIndex()

        try:
            machine_code = assemble(asm_code)
        except Exception as e:
            QMessageBox.critical(self, "Error in translation", str(e))
            self.output_viewer.setText(f"Error: {e}")
            return

        if selected_mode == 3:
            result_str = f"Translation successfull! Sum of instructions: {len(machine_code)}\n\n"
            result_str += f"{'Address':<8} | {'Hex':<8} | {'Dec':<6} | {'Binary string'}\n"
            result_str += "-" * 45 + "\n"

            for i, b in enumerate(machine_code):
                result_str += f"0x{i:02X}     | 0x{b:02X}     | {b:<6} | {b:08b}\n"
            self.output_viewer.setText(result_str)
            return

        file_filter = "Text files (*.txt)" if selected_mode != 1 else "Binary files (*.bin)"
        default_ext = ".txt" if selected_mode != 1 else ".bin"

        file_path, _ = QFileDialog.getSaveFileName(self, "Save file", f"program{default_ext}", file_filter)
        if not file_path:
            return

        try:
            if selected_mode == 0:
                with open(file_path, "w") as f:
                    for b in machine_code:
                        f.write(f"{b:08b}\n")
            elif selected_mode == 1:
                with open(file_path, "wb") as f:
                    f.write(machine_code)
            elif selected_mode == 2:
                with open(file_path, "w") as f:
                    for b in machine_code:
                        f.write(f"0x{b:02X}\n")

            self.output_viewer.setText(f"Successfully saved to:\n{file_path}\n\nTranslated {len(machine_code)} bytes.")
            QMessageBox.information(self, "Done", "File has been successfully generated!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error while saving", str(e))