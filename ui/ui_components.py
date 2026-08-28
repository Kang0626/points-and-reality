# ui/ui_components.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QTextBrowser, QStyledItemDelegate, QLabel, 
                             QTableWidget)
from PyQt5.QtCore import Qt, pyqtSignal

class ElideLeftDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        if option.text:
            option.text = option.fontMetrics.elidedText(option.text, Qt.ElideLeft, option.rect.width() - 8)
        super().paint(painter, option, index)

class StatusPill(QFrame):
    """A sleek status badge component with colored indicator dot."""
    def __init__(self, text="IDLE", status_type="idle", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 2, 8, 2)
        self.layout.setSpacing(6)

        self.dot = QLabel("●")
        self.lbl_text = QLabel(text)
        self.lbl_text.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        self.layout.addWidget(self.dot)
        self.layout.addWidget(self.lbl_text)
        self.set_status(text, status_type)

    def set_status(self, text, status_type="idle"):
        self.lbl_text.setText(text)
        
        colors = {
            "idle": ("#64748b", "#334155", "#0f172a"),
            "running": ("#38bdf8", "#0284c7", "#0c4a6e"),
            "success": ("#34d399", "#059669", "#064e3b"),
            "warning": ("#fbbf24", "#d97706", "#78350f"),
            "error": ("#f87171", "#dc2626", "#7f1d1d"),
            "ready": ("#38bdf8", "#0369a1", "#082f49")
        }
        dot_color, border_color, bg_color = colors.get(status_type, colors["idle"])
        
        self.dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        self.lbl_text.setStyleSheet(f"color: {dot_color}; font-weight: bold; font-size: 11px;")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
        """)

class DragDropTableWidget(QTableWidget):
    """Table widget with native Drag & Drop support for video files and directories."""
    files_dropped = pyqtSignal(list)

    def __init__(self, rows=0, cols=0, parent=None):
        super().__init__(rows, cols, parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableWidget.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                local_path = url.toLocalFile()
                if local_path:
                    file_paths.append(local_path)
            if file_paths:
                self.files_dropped.emit(file_paths)
                event.acceptProposedAction()
        else:
            super().dropEvent(event)

class ModernStepCard(QFrame):
    """A sleek, modern card with Step Badge, Title, Status, and Collapsible/Action header."""
    def __init__(self, step_num="1", title="Step Title", subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("ModernStepCard")
        self.is_expanded = True
        self.step_num = step_num
        self.title_text = title
        self.subtitle_text = subtitle
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 10, 12, 12)
        self.main_layout.setSpacing(10)

        # Header Bar
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)

        # Title Label
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #f1f5f9;")

        # Subtitle
        self.lbl_subtitle = QLabel(subtitle)
        self.lbl_subtitle.setStyleSheet("font-size: 11px; color: #94a3b8;")

        self.header_layout.addWidget(self.lbl_title)
        if subtitle:
            self.header_layout.addWidget(self.lbl_subtitle)
        self.header_layout.addStretch()

        # Header Right Actions Area
        self.header_actions_layout = QHBoxLayout()
        self.header_actions_layout.setSpacing(6)
        self.header_layout.addLayout(self.header_actions_layout)

        # Toggle Button
        self.btn_toggle = QPushButton("▾")
        self.btn_toggle.setFixedSize(24, 24)
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; color: #94a3b8; font-size: 14px; font-weight: bold; padding: 0px;
            }
            QPushButton:hover { color: #38bdf8; }
        """)
        self.btn_toggle.clicked.connect(self.toggle)
        self.header_layout.addWidget(self.btn_toggle)

        self.main_layout.addLayout(self.header_layout)

        # Content Container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 4, 0, 0)
        self.content_layout.setSpacing(8)
        self.main_layout.addWidget(self.content_widget)

        self.setStyleSheet("""
            #ModernStepCard {
                background-color: #1e2025;
                border: 1px solid #2d3139;
                border-radius: 8px;
            }
        """)

    def setTitle(self, title, subtitle=None):
        self.title_text = title
        self.lbl_title.setText(title)
        if subtitle is not None:
            self.subtitle_text = subtitle
            self.lbl_subtitle.setText(subtitle)

    def setContentLayout(self, layout):
        self.content_layout.addLayout(layout)

    def add_header_action(self, widget):
        self.header_actions_layout.addWidget(widget)

    def toggle(self):
        self.set_expanded(not self.is_expanded)

    def set_expanded(self, state: bool):
        self.is_expanded = state
        self.content_widget.setVisible(self.is_expanded)
        self.btn_toggle.setText("▾" if self.is_expanded else "▸")

class AutoScrollTextBrowser(QTextBrowser):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())