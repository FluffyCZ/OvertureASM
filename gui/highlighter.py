from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp

class OvertureHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self.highlightingRules = []

        # Color options

        # Instructions (mov, imm, add...) -> Purple/Pink
        instruction_format = QTextCharFormat()
        instruction_format.setForeground(QColor("#C586C0"))
        instruction_format.setFontWeight(QFont.Bold)

        # Registers (%r1, %in, %out) -> Cyan
        register_format = QTextCharFormat()
        register_format.setForeground(QColor("#9CDCFE"))

        # Numbers (15, 0x0F) -> Lime
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))

        # Labels (start:) -> Yellow
        label_format = QTextCharFormat()
        label_format.setForeground(QColor("#DCDCAA"))

        # Comments (; text) -> Gray
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6D6D6D"))

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

    def highlightBlock(self, text) -> None:
        for pattern, text_format in self.highlightingRules:
            expression = pattern
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, text_format)
                index = expression.indexIn(text, index + length)

        
