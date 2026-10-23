from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp
import json

class OvertureHighlighter(QSyntaxHighlighter):
    def __init__(self, document, theme_dict) -> None:
        super().__init__(document)
        self.set_theme(theme_dict)

    def set_theme(self, theme):
        self.highlightingRules = []

        def create_format(color_hex, is_bold: bool):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color_hex))
            if is_bold:
                fmt.setFontWeight(QFont.Bold)
            return fmt

        # Instructions (mov, imm, add...) -> Purple/Pink
        instruction_format = create_format(theme["instructions-format"], theme["instructions-format-bold"])

        # Registers (%r1, %in, %out) -> Cyan
        register_format = create_format(theme["registers-format"], theme["registers-format-bold"])

        # Numbers (15, 0x0F) -> Orange
        number_format = create_format(theme["numbers-format"], theme["numbers-format-bold"])

        # Labels (start:) -> Yellow
        label_format = create_format(theme["labels-format"], theme["labels-format-bold"])

        # Comments (; text) -> Gray
        comment_format = create_format(theme["comments-format"], theme["comments-format-bold"])

        # Instructions
        instructions = [
            "\\bmov\\b", "\\bimm\\b", "\\bnand\\b", "\\bor\\b", "\\band\\b",
            "\\bnor\\b", "\\badd\\b", "\\bsub\\b", "\\bnop\\b", "\\bjmp\\b",
            "\\bjz\\b", "\\bjnz\\b", "\\bjl\\b", "\\bjge\\b", "\\bjle\\b", "\\bjg\\b"
        ]
        for pattern in instructions:
            self.highlightingRules.append((QRegExp(pattern), instruction_format))

        # Registers (including %)
        registers = ["%[rR][0-5]\\b", "%in\\b", "%out\\b"]
        for pattern in registers:
            self.highlightingRules.append((QRegExp(pattern), register_format))

        # Numbers (DEC, HEX)
        self.highlightingRules.append((QRegExp("\\b[0-9]+\\b"), number_format))
        self.highlightingRules.append((QRegExp("\\b0x[0-9a-fA-F]+\\b"), number_format))

        # Labels
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+:"), label_format))

        # Comments
        self.highlightingRules.append((QRegExp(";[^\n]*"), comment_format))

        self.rehighlight()

    def highlightBlock(self, text) -> None:
        for pattern, text_format in self.highlightingRules:
            expression = pattern
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, text_format)
                index = expression.indexIn(text, index + length)

        
