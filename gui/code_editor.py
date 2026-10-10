from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.update_selections)
        self.textChanged.connect(self.update_selections)

        self.updateLineNumberAreaWidth(0)
        self.update_selections()

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        try:
            char_width = self.fontMetrics().horizontalAdvance('9')
        except AttributeError:
            char_width = self.fontMetrics().width('9')
            
        space = 15 + char_width * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        width = self.lineNumberAreaWidth()
        self.setViewportMargins(width, 0, 0, 0)
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), width, cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#252526")) 

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def update_selections(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#282828")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        valid_mnemonics = {
            "mov", "imm", "nand", "or", "and", "nor", 
            "add", "sub", "nop", "jmp", "jz", "jnz", 
            "jl", "jge", "jle", "jg"
        }
        
        error_format = QTextCharFormat()
        error_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        error_format.setUnderlineColor(Qt.red)

        block = self.document().begin()
        while block.isValid():
            text = block.text().split(";")[0].strip()
            
            if text and not text.endswith(":"):
                tokens = [t.strip(",%") for t in text.replace(",", " ").split()]
                if tokens:
                    mnemonic = tokens[0].lower()
                    if mnemonic not in valid_mnemonics:
                        sel = QTextEdit.ExtraSelection()
                        sel.format = error_format
                        cursor = QTextCursor(block)
                        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                        sel.cursor = cursor
                        extraSelections.append(sel)
            
            block = block.next()

        self.setExtraSelections(extraSelections)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            self.updateLineNumberAreaWidth(0)
        else:
            super().wheelEvent(event)