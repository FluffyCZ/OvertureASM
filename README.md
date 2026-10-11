# OvertureASM

- A modern desktop assembler and multi-tool designed for the 8-bit **Overture** Instruction Set Architecture (ISA). Built with **Python** and **PyQt5**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features
- **Advanced Code Editor:** Custom-built IDE experience featuring line numbering, active line highlighting, and smooth zoom control (Ctrl + Scroll).
- **Rich Syntax Highlighting:** Clear visual differentiation for instructions, registers, immediate values, labels, and comments based on modern dark themes.
- **Real-Time Linter:** Instant error detection with spellcheck-style red underlining for invalid mnemonics and typos while you type.
- **Two-Pass Assembly:** Full support for automatic forward and backward label resolution (e.g., `start:`, `jmp start`).
- **Multi-Format Export:** 
  - Raw binary (`.bin`) for hardware EEPROM programmers.
  - 8-bit binary strings per line (`.txt`) for HDL simulators (Verilog/VHDL).
  - Hexadecimal format (`.txt`).
  - Live in-app debug table view.

## Installation & Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/FluffyCZ/OvertureASM.git
    cd OvertureASM
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**
    ```bash
    python main.py
    ```

## Example Code (Overture ISA)
```bash
start:
    imm 15
    mov %r1, %in
    add
    mov %out, %r3
    jmp start
```

**Made by FluffyCZ <3**