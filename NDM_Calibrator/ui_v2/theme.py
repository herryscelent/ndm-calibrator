from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from . import tokens as t


QSS = f"""
* {{ font-family: 'Microsoft YaHei UI'; color: {t.TEXT_PRIMARY}; }}
QMainWindow, QWidget#AppShell, QStackedWidget, QScrollArea#PageScroll {{ background: {t.BACKGROUND}; }}
QToolTip {{ background: {t.TEXT_PRIMARY}; color: white; border: 0; padding: 5px; }}
QDialog#ConfirmDialog, QDialog#AlertDialog, QDialog#UnsavedChangesDialog {{ background: {t.SURFACE}; border: 1px solid {t.BORDER}; }}
QWidget#Topbar {{ background: {t.TOPBAR}; border-bottom: 1px solid {t.BORDER}; }}
QWidget#Sidebar {{ background: {t.SIDEBAR}; border-right: 1px solid {t.BORDER}; }}
QLabel#ProductName {{ font-size: 14px; font-weight: 600; }}
QLabel#ProjectContext, QLabel#BodySecondary {{ color: {t.TEXT_SECONDARY}; font-size: 13px; }}
QLabel#Muted {{ color: {t.TEXT_MUTED}; font-size: 12px; }}
QLabel#PageTitle {{ font-size: 22px; font-weight: 700; }}
QLabel#PageDescription {{ color: {t.TEXT_SECONDARY}; font-size: 13px; }}
QLabel#SectionTitle {{ font-size: 15px; font-weight: 600; }}
QLabel#DialogTitle {{ font-size: 16px; font-weight: 600; }}
QLabel#MetricLabel {{ color: {t.TEXT_SECONDARY}; font-size: 12px; }}
QLabel#MetricValue {{ font-size: 24px; font-weight: 600; }}
QLabel#SidebarSection {{ color: {t.TEXT_MUTED}; font-size: 12px; padding: 8px 20px 4px 20px; }}
QPushButton {{ min-height: 34px; padding: 0 14px; border-radius: 6px; border: 1px solid transparent; background: transparent; font-size: 13px; }}
QPushButton:hover {{ background: {t.SURFACE_HOVER}; }}
QPushButton:focus {{ border-color: {t.ACCENT}; }}
QPushButton[variant='primary'] {{ color: white; background: {t.ACCENT}; }}
QPushButton[variant='primary']:hover {{ background: {t.ACCENT_HOVER}; }}
QPushButton[variant='secondary'] {{ background: {t.SURFACE_SECONDARY}; border-color: {t.BORDER}; }}
QPushButton[variant='danger'] {{ color: {t.DANGER}; border-color: #E3A4A4; }}
QPushButton[variant='dangerFilled'] {{ color: white; background: {t.DANGER}; border-color: {t.DANGER}; }}
QPushButton[nav='true'] {{ text-align: left; padding-left: 18px; color: {t.TEXT_SECONDARY}; border: 0; min-height: 36px; }}
QPushButton[nav='true']:checked {{ color: {t.TEXT_PRIMARY}; background: {t.ACCENT_SUBTLE}; border-left: 3px solid {t.ACCENT}; padding-left: 15px; }}
QPushButton[nav='true']:hover {{ background: {t.SURFACE_HOVER}; }}
QPushButton[algo='true'] {{ text-align: left; min-height: 54px; background: {t.SURFACE}; border-color: {t.BORDER}; }}
QPushButton[algo='true']:checked {{ background: {t.SURFACE_SELECTED}; border-color: #7DA4F2; }}
QFrame#Card, QFrame#Panel {{ background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 8px; }}
QFrame#SectionLine {{ background: transparent; border-top: 1px solid {t.BORDER}; }}
QLabel[badge='success'] {{ color: {t.SUCCESS}; background: #E9F5EF; border-radius: 6px; padding: 3px 8px; }}
QLabel[badge='info'] {{ color: {t.ACCENT}; background: {t.ACCENT_SUBTLE}; border-radius: 6px; padding: 3px 8px; }}
QLabel[badge='neutral'] {{ color: {t.TEXT_SECONDARY}; background: {t.SURFACE_SECONDARY}; border-radius: 6px; padding: 3px 8px; }}
QLabel[badge='warning'] {{ color: {t.WARNING}; background: #FBF3E6; border-radius: 6px; padding: 3px 8px; }}
QLabel[badge='danger'] {{ color: {t.DANGER}; background: #FCECEC; border-radius: 6px; padding: 3px 8px; }}
QTableView {{ background: {t.SURFACE}; alternate-background-color: {t.SURFACE_SECONDARY}; border: 1px solid {t.BORDER}; border-radius: 8px; gridline-color: #EDF0F3; selection-background-color: {t.SURFACE_SELECTED}; selection-color: {t.TEXT_PRIMARY}; font-size: 13px; }}
QTableView::item:hover {{ background: {t.SURFACE_HOVER}; }}
QHeaderView::section {{ background: {t.SURFACE_SECONDARY}; color: {t.TEXT_SECONDARY}; border: 0; border-bottom: 1px solid {t.BORDER}; padding: 7px 10px; font-weight: 500; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ min-height: 30px; background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 6px; padding: 0 8px; font-size: 13px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {t.ACCENT}; }}
QPlainTextEdit {{ background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 6px; padding: 10px; selection-background-color: {t.SURFACE_SELECTED}; }}
QPlainTextEdit:focus {{ border-color: {t.ACCENT}; }}
QCheckBox {{ spacing: 8px; min-height: 28px; }}
QCheckBox::indicator {{ width: 15px; height: 15px; border: 1px solid {t.BORDER_STRONG}; border-radius: 4px; background: {t.SURFACE}; }}
QCheckBox::indicator:checked {{ background: {t.ACCENT}; border-color: {t.ACCENT}; }}
QSplitter::handle {{ background: {t.BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; margin: 0 8px; }}
QComboBox::drop-down {{ border: 0; width: 24px; }}
QTabWidget::pane {{ border: 0; top: -1px; }}
QTabBar {{ background: {t.SURFACE_SECONDARY}; border-radius: 6px; }}
QTabBar::tab {{ min-height: 30px; padding: 0 16px; color: {t.TEXT_SECONDARY}; border: 1px solid transparent; }}
QTabBar::tab:selected {{ background: {t.SURFACE}; color: {t.TEXT_PRIMARY}; border-color: {t.BORDER}; border-radius: 5px; }}
QProgressBar {{ height: 6px; border: 0; background: {t.SURFACE_SECONDARY}; border-radius: 3px; text-align: center; }}
QProgressBar::chunk {{ background: {t.ACCENT}; border-radius: 3px; }}
QScrollBar:vertical {{ width: 8px; background: transparent; }}
QScrollBar::handle:vertical {{ background: {t.BORDER_STRONG}; border-radius: 4px; min-height: 28px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 8px; background: transparent; }}
QScrollBar::handle:horizontal {{ background: {t.BORDER_STRONG}; border-radius: 4px; min-width: 28px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""


def apply_theme(app: QApplication) -> None:
    for path in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc"):
        QFontDatabase.addApplicationFont(path)
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    app.setStyleSheet(QSS)
