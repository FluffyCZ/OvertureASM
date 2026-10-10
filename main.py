import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt

REGISTERS = {
    "r0": 0b000, "r1": 0b001, "r2": 0b010, "r3": 0b011,
    "r4": 0b100, "r5": 0b101, "in": 0b110, "out": 0b110
}

def assemble(asm_code):
    lines = asm_code.strip().split("\n")

    labels = {}
    clean_instructions = []
    pc = 0  
    
    for raw_line in lines:
        line = raw_line.split(";")[0].strip()
        if not line:
            continue
            
        if line.endswith(":"):
            label_name = line[:-1].strip().lower()
            labels[label_name] = pc
            continue
            
        clean_instructions.append((pc, line))
        pc += 1  # Every instruction has 1 byte

    binary_output = bytearray()
    
    for pc, line in clean_instructions:
        tokens = [t.strip(",%") for t in line.replace(",", " ").split()]
        if not tokens:
            continue
            
        mnemonic = tokens[0].lower()
        args = tokens[1:]
        
        byte = 0
        
        if mnemonic == "mov":
            if len(args) != 2:
                raise SyntaxError(f"Instruction 'mov' is expecting 2 arguments: {line}")
            dest = REGISTERS[args[0].lower()]
            src = REGISTERS[args[1].lower()]
            byte = (0b10 << 6) | ((dest & 0b111) << 3) | (src & 0b111)
            
        elif mnemonic == "imm":
            if len(args) != 1:
                raise SyntaxError(f"Instruction 'imm' is expecting 1 argument: {line}")
            
            val_str = args[0]
            if val_str.lower() in labels:
                val = labels[val_str.lower()]
            else:
                val = int(val_str, 0)
                
            if not (0 <= val <= 63):
                raise ValueError(f"The value for 'imm' has to be in range 0-63 (6 bits): {val}")
                
            byte = (0b00 << 6) | (val & 0x3F)
            
        elif mnemonic in ("nand", "or", "and", "nor", "add", "sub"):
            opcodes = {
                "nand": 0b01000000, "or":   0b01000001,
                "and":  0b01000010, "nor":  0b01000011,
                "add":  0b01000100, "sub":  0b01000101
            }
            byte = opcodes[mnemonic]
            
        elif mnemonic in ("nop", "jmp", "jz", "jnz", "jl", "jge", "jle", "jg"):
            opcodes = {
                "nop": 0b11000000, "jmp": 0b11000001,
                "jz":  0b11000010, "jnz": 0b11000011,
                "jl":  0b11000100, "jge": 0b11000101,
                "jle": 0b11000110, "jg":  0b11000111
            }
            byte = opcodes[mnemonic]
        else:
            raise ValueError(f"Unknown instruction: {mnemonic}")
            
        binary_output.append(byte)

    return binary_output

class AssemblerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Overture ISA Assembler & Multi-Tool")
        self.resize(900, 600)

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Assembly Code:</b>"))

        self.input_editor = QTextEdit()
        self.input_editor.setPlaceholderText("Enter assembly code here...")

        self.input_editor.setPlainText("start:\n    imm 15\n    mov %r1, %in\n    add\n    mov %out, %r3\n    jmp start")
        left_layout.addWidget(self.input_editor)

        # Settings and output
        right_layout = QVBoxLayout()

        # Output format choice
        right_layout.addWidget(QLabel("<b>Output format / Action:</b>"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Binary strings to .txt (8 bit per line)",
            "Plain binary file (.bin for EEPROM)",
            "HEX output to .txt",
            "Only show in app (Debug table)"
        ])
        right_layout.addWidget(self.format_combo)

        # Start button
        self.compile_btn = QPushButton("Translate and Save/Show")
        self.compile_btn.setStyleSheet("background-color: #2b5b84; color: white; font-weight: bold; padding: 8px;")
        self.compile_btn.clicked.connect(self.process_assembly)
        right_layout.addWidget(self.compile_btn)

        # Output textfield (preview / log)
        right_layout.addWidget(QLabel("<b>Output / Log:</b>"))
        self.output_viewer = QTextEdit()
        self.output_viewer.setReadOnly(True)
        self.output_viewer.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas;")
        right_layout.addWidget(self.output_viewer)

        # Adding rows to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralItem = self.setCentralWidget(container)

    def process_assembly(self):
        asm_code = self.input_editor.toPlainText()
        selected_mode = self.format_combo.currentIndex()

        try:
            machine_code = assemble(asm_code)
        except Exception as e:
            QMessageBox.critical(self, "Error in translation", str(e))
            self.output_viewer.setText(f"Error: {e}")
            return

        # Preview in app
        if selected_mode == 3:
            result_str = f"Translation successfull! Sum of instructions: {len(machine_code)}\n\n"
            result_str += f"{'Address':<8} | {'Hex':<8} | {'Dec':<6} | {'Binary string'}\n"
            result_str += "-" * 45 + "\n"

            for i, b in enumerate(machine_code):
                result_str += f"0x{i:02X}     | 0x{b:02X}     | {b:<6} | {b:08b}\n"
            self.output_viewer.setText(result_str)
            return

        # Saving mode to files
        file_filter = "Text files (*.txt)" if selected_mode != 1 else "Binary files (*.bin)"
        default_ext = ".txt" if selected_mode != 1 else ".bin"

        file_path, _ = QFileDialog.getSaveFileName(self, "Save file", f"program{default_ext}", file_filter)
        if not file_path:
            return

        try:
            if selected_mode == 0: # Binary string to txt
                with open(file_path, "w") as f:
                    for b in machine_code:
                        f.write(f"{b:08b}\n")
            elif selected_mode == 1: # Plain .bin
                with open(file_path, "wb") as f:
                    f.write(machine_code)
            elif selected_mode == 2: # Hex to txt
                with open(file_path, "w") as f:
                    for b in machine_code:
                        f.write(f"0x{b:02X}\n")

            self.output_viewer.setText(f"Successfully saved to:\n{file_path}\n\nTranslated {len(machine_code)} bytes.")
            QMessageBox.information(self, "Done", "File has been successfully generated!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error while saving", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AssemblerGUI()
    ex.show()
    sys.exit(app.exec_())