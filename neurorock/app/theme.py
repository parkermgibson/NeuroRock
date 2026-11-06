"""Dark theme for the app's widgets."""

from __future__ import annotations

import sys

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

BG = "#111318"
SIDEBAR = "#0c0e12"
PANEL = "#181b22"
RAISED = "#222632"
BORDER = "#2a2f3c"
TEXT = "#e8eaf0"
MUTED = "#8b92a5"
FAINT = "#5a6072"
ACCENT = "#ff7a45"
ACCENT_SOFT = "#3a2419"
OK = "#4cc38a"
WARN = "#f0b429"
BAD = "#f25c54"


STYLESHEET = f"""
QWidget {{ color: {TEXT}; }}
QMainWindow, QStackedWidget > QWidget {{ background: {BG}; }}
QToolTip {{ background: {RAISED}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px; }}

/* Sidebar */
QFrame#sidebar {{ background: {SIDEBAR}; border-right: 1px solid #1b1e26; }}
QLabel#brand {{ font-size: 17pt; font-weight: 700; padding: 18px 18px 14px 18px; }}
QListWidget#nav {{ background: transparent; border: none; outline: none; font-size: 10.5pt; }}
QListWidget#nav::item {{ padding: 9px 14px; border-radius: 7px; margin: 1px 10px; color: {MUTED}; }}
QListWidget#nav::item:hover {{ background: #161920; color: {TEXT}; }}
QListWidget#nav::item:selected {{ background: {RAISED}; color: {TEXT}; border-left: 3px solid {ACCENT}; }}
QLabel#chip {{ color: {MUTED}; padding: 2px 18px; font-size: 9pt; }}

/* Page header */
QLabel#pageTitle {{ font-size: 18pt; font-weight: 700; }}
QLabel#pageSubtitle {{ color: {MUTED}; }}

/* Cards: group boxes and plain card frames */
QGroupBox, QFrame#card {{
    background: {PANEL}; border: 1px solid #20242e; border-radius: 10px;
}}
QGroupBox {{ margin-top: 0px; padding: 34px 12px 12px 12px; }}
QGroupBox::title {{
    subcontrol-origin: padding; subcontrol-position: top left; left: 14px; top: 11px;
    color: {MUTED}; font-size: 8.5pt; font-weight: 600;
}}
QLabel#cardTitle {{ color: {MUTED}; font-size: 8.5pt; font-weight: 600; }}
QLabel#hint {{ color: {MUTED}; }}
QLabel#faint {{ color: {FAINT}; }}
QLabel#warning {{ color: {WARN}; }}
QLabel#error {{ color: {BAD}; }}
QLabel#banner {{ background: {ACCENT_SOFT}; color: {TEXT}; border: 1px solid #5a3322;
                 border-radius: 8px; padding: 8px 12px; }}
QLabel#bigValue {{ font-size: 34pt; font-weight: 700; }}
QLabel#mediumValue {{ font-size: 15pt; font-weight: 600; }}
QLabel#keys {{ color: {MUTED}; font-family: Consolas, 'Cascadia Mono', monospace; font-size: 9pt; }}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit, QTextEdit {{
    background: {BG}; border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 8px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {PANEL}; border: 1px solid {BORDER}; selection-background-color: {RAISED};
}}
QCheckBox {{ spacing: 8px; }}

/* Buttons */
QPushButton {{ background: {RAISED}; border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 12px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:pressed {{ background: #2b3040; }}
QPushButton:disabled {{ color: #4d5263; border-color: #22252e; background: #1b1e25; }}
QPushButton:checked {{ background: {ACCENT_SOFT}; border-color: {ACCENT}; color: {ACCENT}; }}
QPushButton#primary {{
    background: {ACCENT}; color: #14100e; font-weight: 700; border: none; padding: 8px 14px;
}}
QPushButton#primary:hover {{ background: #ff8f62; }}
QPushButton#primary:disabled {{ background: #3a2a22; color: #6d5a50; }}
QPushButton#danger {{ background: {BAD}; color: #160d0c; font-weight: 700; border: none; padding: 8px 14px; }}
QPushButton#ghost {{ background: transparent; border: 1px solid {BORDER}; }}

/* Lists, tables, progress, sliders */
QListWidget {{ background: {BG}; border: 1px solid {BORDER}; border-radius: 8px; outline: none; }}
QListWidget::item {{ padding: 8px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {RAISED}; color: {TEXT}; }}
QTableWidget {{ background: transparent; gridline-color: {RAISED}; border: none; }}
QHeaderView::section {{ background: transparent; color: {MUTED}; border: none; padding: 3px; }}
QProgressBar {{
    background: {BG}; border: 1px solid {BORDER}; border-radius: 5px; height: 10px; text-align: center;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QSlider::groove:horizontal {{ height: 4px; background: {RAISED}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {TEXT}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
}}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {RAISED}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QStatusBar {{ background: {SIDEBAR}; color: {MUTED}; border-top: 1px solid #1b1e26; }}
QSplitter::handle {{ background: transparent; }}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    if sys.platform == "win32":
        app.setFont(QFont("Segoe UI", 10))
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: BG,
        QPalette.ColorRole.WindowText: TEXT,
        QPalette.ColorRole.Base: BG,
        QPalette.ColorRole.AlternateBase: PANEL,
        QPalette.ColorRole.Text: TEXT,
        QPalette.ColorRole.Button: RAISED,
        QPalette.ColorRole.ButtonText: TEXT,
        QPalette.ColorRole.Highlight: ACCENT,
        QPalette.ColorRole.HighlightedText: "#111111",
        QPalette.ColorRole.ToolTipBase: PANEL,
        QPalette.ColorRole.ToolTipText: TEXT,
        QPalette.ColorRole.PlaceholderText: FAINT,
    }
    for role, color in roles.items():
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)


def restyle(widget, object_name: str) -> None:
    """Change a widget's style class (object name) and make Qt re-apply the stylesheet."""
    widget.setObjectName(object_name)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
