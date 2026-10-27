from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QFontComboBox, QSpinBox, QListWidget, QStackedWidget, QWidget, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import json

class SettingsDialog(QDialog):
    def __init__(self, parent_gui, current_theme, themes_dict):
        super().__init__(parent_gui)
        self.parent_gui = parent_gui
        self.themes_dict = themes_dict
        self.setWindowTitle("Settings")
        self.resize(600, 400)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel (Navigation)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        self.sidebar.addItem("Appearance")
        self.sidebar.addItem("Editor")
        self.sidebar.addItem("Build & Run")
        self.sidebar.setCurrentRow(0)

        self.sidebar.currentRowChanged.connect(self.switch_page)

        # Right panel (Options)
        self.pages = QStackedWidget()

        self.pages.addWidget(self.create_appearance_page(current_theme))
        self.pages.addWidget(self.create_editor_page())
        self.pages.addWidget(self.create_build_page())

        # Bottom panel (Buttons)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.close_btn = QPushButton("Apply & Close")
        self.close_btn.clicked.connect(self.save_and_close)

        bottom_layout.addWidget(self.cancel_btn)
        bottom_layout.addWidget(self.close_btn)

        # Right container
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.addWidget(self.pages)
        right_layout.addLayout(bottom_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_container)

        self.apply_dialog_theme()

    def create_appearance_page(self, current_theme):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("<b>Appearance Settings</b>")
        title.setFont(QFont("Arial", 14))
        layout.addWidget(title)
        layout.addSpacing(20)

        self.theme_label = QLabel("<b>Select Theme:</b>")
        layout.addWidget(self.theme_label)

        self.theme_combo = QComboBox()
        # Filter app-settings
        valid_themes = [t for t in self.themes_dict.keys() if t != "app-settings"]
        self.theme_combo.addItems(valid_themes)
        self.theme_combo.setCurrentText(current_theme)

        self.theme_combo.currentTextChanged.connect(self.on_theme_change)

        layout.addWidget(self.theme_combo)
        layout.addStretch()
        return page

    def create_editor_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("<b>Editor Settings</b>")
        title.setFont(QFont("Arial", 14))
        layout.addWidget(title)
        layout.addSpacing(20)

        # Load current font from settings (or default)
        app_settings = self.themes_dict.get("app-settings", {"font-family": "Consolas", "font-size": 11})

        layout.addWidget(QLabel("<b>Font Family:</b>"))
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(app_settings.get("font-family", "Consolas")))
        layout.addWidget(self.font_combo)

        layout.addSpacing(10)

        layout.addWidget(QLabel("<b>Font Size:</b>"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(app_settings.get("font-size", 11))
        layout.addWidget(self.size_spin)

        layout.addStretch()
        return page

    def create_build_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("<b>Build & Run</b>")
        title.setFont(QFont("Arial", 14))
        layout.addWidget(title)
        layout.addSpacing(20)

        layout.addWidget(QLabel("<i>Compiler options will be added here...</i>"))
        layout.addStretch()
        return page

    def switch_page(self, index) -> None:
        self.pages.setCurrentIndex(index)

    def save_and_close(self):
        family = self.font_combo.currentFont().family()
        size = self.size_spin.value()

        if hasattr(self.parent_gui, 'apply-font'):
            self.parent_gui.apply_font(family, size)

        # Enter the values to settings.json
        if "app-settings" not in self.parent_gui.themes:
            self.parent_gui.themes["app-settings"] = {}

        self.parent_gui.themes["app-settings"]["font-family"] = family
        self.parent_gui.themes["app-settings"]["font-size"] = size
        self.parent_gui.themes["app-settings"]["current-theme"] = self.theme_combo.currentText()

        try:
            with open("settings.json", "w") as f:
                json.dump(self.parent_gui.themes, f, indent=4)
        except Exception as e:
            try:
                from utils.logger import Logger
                Logger.error(f"Cannot save settings.json {e}")
            except:
                print(f"[ERROR] Cannot save settings.json {e}")

        self.accept()

    def on_theme_change(self, theme_name):
        self.parent_gui.apply_theme(theme_name)
        self.apply_dialog_theme()

    def apply_dialog_theme(self):
        theme = self.parent_gui.current_theme
        if not theme:
            return

        bg = theme['background-color']
        fg = theme['foreground-color']
        surface = theme.get('ui-surface', bg)
        border = theme.get('ui-border', '#3f3f46')
        btn_bg = theme.get('ui-button','#2b5b84')
        btn_fg = theme.get('ui-button-text', '#FFFFFF')
        hover = theme.get('ui-hover', '#3f3f46')

        self.setStyleSheet(f"""
            QDialog, QStackedWidget {{
                background-color: {surface};
                color: {fg};
            }}
            QLabel {{
                color: {fg};
            }}
            QComboBox, QFontComboBox, QSpinBox {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 4px;
            }}
            QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {hover};
            }}
            QComboBox::drop-down, QFontComboBox::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                padding: 6px 12px;
                border: 1px solid {border};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            /* Styly pro nový levý panel */
            QListWidget {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-right: 1px solid {border};
                padding-top: 10px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px 15px;
            }}
            QListWidget::item:selected {{
                background-color: {btn_bg};
                color: {btn_fg};
                border-left: 3px solid {hover};
            }}
        """)        