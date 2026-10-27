from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter

class OvertureCompleter(QCompleter):
    def __init__(self, parent=None):
        # Instruction & Register words
        isa_words = [
            "mov", "imm", "nand", "or", "and", "nor", "add", "sub", "nop", "jmp",
            "jz", "jnz", "jl", "jge", "jle", "jg", "start",
            "%r0", "%r1", "%r2", "%r3", "%r4", "%r5", "%r6", "%r7", "%in", "%out"
        ]
        super().__init__(isa_words, parent)

        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        # Theme for popup window
        self.popup().setStyleSheet("""
            QListView {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3f3f46;
                font-family: Consolas;
                font-size: 13px;
            }
            QListView::item:selected {
                background-color: #3f3f46;
            }
        """)