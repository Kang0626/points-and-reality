# ui/tabs/capture_sections/section_watcher.py
import os
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from ui.ui_components import ModernStepCard, ElideLeftDelegate, StatusPill
from utils import FolderWatcherThread

class WatcherWidget(ModernStepCard):
    log_signal = pyqtSignal(str, str)
    send_to_cleanup_signal = pyqtSignal(list)
    request_max_toggle = pyqtSignal(bool)
    request_lang_update = pyqtSignal()

    def __init__(self):
        super().__init__(step_num="4", title="Export Watcher & Auto Pipeline", subtitle="Detect trained splats and forward to cleanup")
        self.proj_dir = ""
        self.watcher_thread = None
        self.init_ui()

    def init_ui(self):
        self.status_pill = StatusPill("IDLE", "idle")
        self.add_header_action(self.status_pill)

        vlayout = QVBoxLayout()
        vlayout.setSpacing(8)

        # Toolbar
        hlayout = QHBoxLayout()
        hlayout.setSpacing(8)
        
        self.btn_start = QPushButton("▶ Start Auto Watcher")
        self.btn_start.setObjectName("PrimaryBtn")
        self.btn_start.clicked.connect(self.toggle_watcher)

        self.btn_send = QPushButton("Send to Cleanup ➔")
        self.btn_send.setObjectName("SuccessBtn")
        self.btn_send.clicked.connect(self.send_to_cleanup)

        self.btn_clear = QPushButton("🗑 Clear List")
        self.btn_clear.clicked.connect(lambda: self.table.setRowCount(0))

        hlayout.addWidget(self.btn_start)
        hlayout.addWidget(self.btn_send)
        hlayout.addWidget(self.btn_clear)
        hlayout.addStretch()

        self.btn_max = QPushButton("⛶")
        self.btn_max.setToolTip("Expand / Minimize Table")
        self.btn_max.setCheckable(True)
        self.btn_max.setFixedWidth(32)
        self.btn_max.clicked.connect(self.toggle_maximize)
        hlayout.addWidget(self.btn_max)

        vlayout.addLayout(hlayout)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setItemDelegateForColumn(0, ElideLeftDelegate(self.table))
        self.table.setHorizontalHeaderLabels(["Detected File / Folder Path", "Size (MB)", "Time", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setMinimumHeight(110)
        self.table.verticalHeader().setVisible(False)
        vlayout.addWidget(self.table)

        self.setContentLayout(vlayout)

    def set_proj_dir(self, directory):
        self.proj_dir = directory

    def toggle_maximize(self):
        is_max = self.btn_max.isChecked()
        self.table.setMinimumHeight(300 if is_max else 110)
        self.request_max_toggle.emit(is_max)

    def toggle_watcher(self):
        if not self.proj_dir:
            self.log_signal.emit("[ERROR] Set Project Directory first.", "error")
            return
        watch_dir = os.path.join(self.proj_dir, "03_splats_exports")
        os.makedirs(watch_dir, exist_ok=True)
        
        if self.watcher_thread and self.watcher_thread.isRunning():
            self.watcher_thread.stop()
            self.btn_start.setText("▶ Start Auto Watcher")
            self.btn_start.setObjectName("PrimaryBtn")
            self.btn_start.setStyleSheet("")
            self.status_pill.set_status("IDLE", "idle")
            self.log_signal.emit("Auto Watcher stopped.", "info")
        else:
            self.watcher_thread = FolderWatcherThread(watch_dir)
            self.watcher_thread.file_detected.connect(self.add_item)
            self.watcher_thread.start()
            self.btn_start.setText("■ Stop Auto Watcher")
            self.btn_start.setObjectName("DangerBtn")
            self.btn_start.setStyleSheet("background-color: #dc2626; color: white;")
            self.status_pill.set_status("WATCHING", "running")
            self.log_signal.emit(f"Watching folder: {watch_dir}", "success")
            
        self.request_lang_update.emit()

    def add_item(self, path, size, time_str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        item_path = QTableWidgetItem(path)
        item_path.setToolTip(path)
        
        self.table.setItem(row, 0, item_path)
        self.table.setItem(row, 1, QTableWidgetItem(size))
        self.table.setItem(row, 2, QTableWidgetItem(time_str))
        self.table.setItem(row, 3, QTableWidgetItem("Ready for Cleanup"))
        self.status_pill.set_status(f"{row+1} Splats", "success")
        self.log_signal.emit(f"⚡ Detected new export: {os.path.basename(path)}", "success")

    def send_to_cleanup(self):
        if self.table.rowCount() == 0:
            self.log_signal.emit("[WARNING] No exported splats to send.", "warning")
            return
        rows = [i.row() for i in self.table.selectionModel().selectedRows()] or range(self.table.rowCount())
        sent = []
        for r in rows:
            path = self.table.item(r, 0).text()
            sent.append(path)
            self.table.setItem(r, 3, QTableWidgetItem("Sent to Cleanup"))
        self.send_to_cleanup_signal.emit(sent)
        self.log_signal.emit(f"Sent {len(sent)} splat file(s) to Splat Cleanup (Tab 2).", "success")

    def update_language(self, t):
        self.setTitle(t.get("group_watcher", "Export Watcher & Auto Pipeline"), t.get("sub_watcher", "Detect trained splats and forward to cleanup"))
        is_watching = self.watcher_thread and self.watcher_thread.isRunning()
        self.btn_start.setText(t.get("btn_stop_watcher", "■ Stop Auto Watcher") if is_watching else t.get("btn_start_watcher", "▶ Start Auto Watcher"))
        self.btn_send.setText(t.get("btn_send_cleanup", "Send to Cleanup ➔"))
        self.btn_clear.setText(t.get("btn_remove_all", "🗑 Clear List"))
        self.table.setHorizontalHeaderLabels([
            t.get("tbl_col_detected", "Detected File / Folder Path"),
            t.get("tbl_col_size", "Size (MB)"),
            t.get("tbl_col_time", "Time"),
            t.get("tbl_col_status", "Status")
        ])