from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QComboBox, QFileDialog, QMessageBox,
    QAction, QCompleter
)
from PyQt5.QtGui import QFont

from gui.editor.highlighter import OvertureHighlighter
from gui.editor.code_editor import CodeEditor
from assembler.assembler import assemble
from gui.dialogs.settings_dialog import SettingsDialog
from utils.logger import Logger
import json

class AssemblerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme_name = "dark"
        self.current_theme = None
        self.current_font_family = "Consolas"
        self.current_font_size = 11
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Overture ISA Assembler & Multi-Tool")
        self.resize(900, 600)
        
        try:
            with open("settings.json", "r") as f:
                self.themes = json.load(f)
        except Exception as e:
            Logger.warning(f"Couldn't load settings.json {e}\n Creating a fallback settings...")
            # Fallback
            self.themes = {"dark": {
                "background-color": "#1e1e1e", "foreground-color": "#dcdcdc",
                "ui-surface": "#252526", "ui-border": "#3f3f46",
                "ui-button": "#2b5b84", "ui-button-text": "#FFFFFF",
                "ui-hover": "#3f3f46", "ui-highlight": "#264f78",
                "ui-line-number-bg": "#252526", "ui-line-number-fg": "#858585",
                "ui-current-line": "#282828",
                "numbers-format": "#B5CEA8", "numbers-format-bold": False,
                "labels-format": "#DCDCAA", "labels-format-bold": False,
                "registers-format": "#9CDCFE", "registers-format-bold": False,
                "instructions-format": "#C586C0", "instructions-format-bold": True,
                "comments-format": "#6A9955", "comments-format-bold": False
            }}

        if "app-settings" not in self.themes:
            self.themes["app-settings"] = {
                "current-theme": "dark",
                "font-family": "Consolas",
                "font-size": 11
            }

        # Menubar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New File", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save As", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Options Menu
        options_menu = menubar.addMenu("Options")

        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+I")
        settings_action.triggered.connect(self.open_settings)
        options_menu.addAction(settings_action)

        main_layout = QHBoxLayout()

        # --- LEFT SIDE ---
        left_layout = QVBoxLayout()
        
        # Header for the left side with Open Button
        left_header = QHBoxLayout()
        self.label_assembly = QLabel("<b>Assembly Code:</b>")
        left_header.addWidget(self.label_assembly)
        
        self.open_btn = QPushButton("📂 Open .asm file")
        self.open_btn.clicked.connect(self.open_file)
        left_header.addWidget(self.open_btn)
        
        left_layout.addLayout(left_header)

        self.input_editor = CodeEditor()
        self.input_editor.setPlaceholderText("Enter assembly code here...")

        # Syntax highlighter
        self.highlighter = OvertureHighlighter(self.input_editor.document(), self.themes["dark"])

        self.input_editor.setPlainText("; ------ EXAMPLE CODE------\n; ------ THANK YOU FOR USING MY APP ------\nstart:\n    imm 15\n    mov %r1, %in\n    add\n    mov %out, %r3\n    jmp start")
        left_layout.addWidget(self.input_editor)

        # --- RIGHT SIDE ---
        right_layout = QVBoxLayout()

        self.label_output_format = QLabel("<b>Output format / Action:</b>")
        right_layout.addWidget(self.label_output_format)
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Binary strings to .txt (8 bit per line)",
            "Plain binary file (.bin for EEPROM)",
            "HEX output to .txt",
            "Only show in app (Debug table)"
        ])
        right_layout.addWidget(self.format_combo)

        self.compile_btn = QPushButton("Translate and Save/Show")
        self.compile_btn.clicked.connect(self.process_assembly)
        right_layout.addWidget(self.compile_btn)

        self.label_output_log = QLabel("<b>Output / Log:</b>")
        right_layout.addWidget(self.label_output_log)
        self.output_viewer = QTextEdit()
        self.output_viewer.setReadOnly(True)
        right_layout.addWidget(self.output_viewer)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        app_settings = self.themes.get("app-settings", {})

        saved_theme = app_settings.get("current-theme", "dark")
        saved_font_family = app_settings.get("font-family", "Consolas")
        saved_font_size = app_settings.get("font-size", 11)

        self.apply_theme(saved_theme)
        self.apply_font(saved_font_family, saved_font_size)

        Logger.system(f"Loaded configuration: Theme='{saved_theme}', Font='{saved_font_family}', Size={saved_font_size}")

    def open_settings(self):
        dlg = SettingsDialog(self, self.current_theme_name, self.themes)
        dlg.exec_()

    # File handling
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Assembly File", "", "Assembly files (*.asm *.txt);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_editor.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open file: {e}")

    def new_file(self):
        self.input_editor.clear()

    def save_file(self):
        # Save the source code to (.asm)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Source Code", "program.asm", "Assembly files (*.asm);;Text files (*.txt);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.input_editor.toPlainText())
                QMessageBox.information(self, "Success", "Source code saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot save file: {e}")

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
            Logger.info(f"Translation successfull! Sum of instructions: {len(machine_code)}")

            result_str = f"Translation successful! Sum of instructions: {len(machine_code)}\n\n"
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
            Logger.error(f"Error while saving: {e}")

    def apply_font(self, family: str, size: int):
        self.current_font_family = family
        self.current_font_size = size
        new_font = QFont(family, size)
        
        if hasattr(self, 'input_editor') and self.input_editor:
            self.input_editor.setFont(new_font)
        if hasattr(self, 'output_viewer') and self.output_viewer:
            self.output_viewer.setFont(new_font)

    def apply_theme(self, theme_name):
        theme = self.themes.get(theme_name, self.themes.get("dark"))
        self.current_theme_name = theme_name
        self.current_theme = theme

        # Extract all theme colors
        bg = theme['background-color']
        fg = theme['foreground-color']
        surface = theme.get('ui-surface', bg)
        border = theme.get('ui-border', '#3f3f46')
        btn_bg = theme.get('ui-button', '#2b5b84')
        btn_fg = theme.get('ui-button-text', '#FFFFFF')
        hover = theme.get('ui-hover', '#3f3f46')
        highlight = theme.get('ui-highlight', '#264f78')
        ln_bg = theme.get('ui-line-number-bg', surface)
        ln_fg = theme.get('ui-line-number-fg', '#858585')
        cur_line = theme.get('ui-current-line', '#282828')

        # Global application stylesheet
        self.setStyleSheet(f"""
            /* Main window */
            QMainWindow {{
                background-color: {surface};
                color: {fg};
            }}

            /* Central widget & containers */
            QWidget {{
                background-color: {surface};
                color: {fg};
            }}

            /* Labels */
            QLabel {{
                color: {fg};
                background-color: transparent;
            }}

            /* Menu bar */
            QMenuBar {{
                background-color: {bg};
                color: {fg};
            }}
            QMenuBar::item:selected {{
                background-color: {hover};
            }}

            /* Dropdown menus */
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
            }}
            QMenu::item {{
                padding: 4px 20px;
            }}
            QMenu::item:selected {{
                background-color: {hover};
            }}

            /* Buttons */
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                font-weight: bold;
                padding: 6px 12px;
                border: 1px solid {border};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {highlight};
            }}
            QPushButton:pressed {{
                background-color: {btn_bg};
            }}

            /* Combo boxes */
            QComboBox {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 4px 8px;
                border-radius: 3px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {hover};
                selection-color: {fg};
                border: 1px solid {border};
            }}
            QComboBox::drop-down {{
                border: none;
            }}

            /* Output viewer (QTextEdit) */
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
            }}

            /* Code editor (QPlainTextEdit) */
            QPlainTextEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: {surface};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border};
                min-height: 20px;
                border-radius: 3px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {surface};
                height: 12px;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {border};
                min-width: 20px;
                border-radius: 3px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {hover};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* Message boxes and dialogs */
            QMessageBox {{
                background-color: {surface};
                color: {fg};
            }}
        """)

        # Code editor specific colors 
        self.input_editor.set_theme_colors(ln_bg, ln_fg, cur_line)

        # Syntax highlighter
        if hasattr(self, 'highlighter'):
            self.highlighter.set_theme(theme)

        if hasattr(self, 'current_font_family') and hasattr(self, 'current_font_size'):
            self.apply_font(self.current_font_family, self.current_font_size)