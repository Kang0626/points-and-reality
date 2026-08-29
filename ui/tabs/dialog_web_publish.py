# ui/tabs/dialog_web_publish.py
import os
import shutil
import json
import time
import subprocess
import webbrowser
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, 
                             QWidget, QProgressBar, QTextBrowser, QMessageBox, 
                             QTabWidget, QAbstractItemView, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ui.ui_components import ModernStepCard, StatusPill

def _format_size(bytes_val):
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"

class SelectiveVercelUploadWorker(QThread):
    progress_signal = pyqtSignal(str, int)
    log_signal = pyqtSignal(str, str)
    success_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, src_web_dir, repo_dir, selected_html_files):
        super().__init__()
        self.src_web_dir = os.path.normpath(src_web_dir)
        self.repo_dir = os.path.normpath(repo_dir)
        self.selected_html_files = selected_html_files

    def run(self):
        try:
            self.progress_signal.emit("Preparing selective sync...", 10)
            self.log_signal.emit(f"Staging {len(self.selected_html_files)} selected HTML model(s)...", "info")

            target_web_dir = os.path.normpath(os.path.join(self.repo_dir, "05_web_build"))
            os.makedirs(target_web_dir, exist_ok=True)

            # 1. Sync libs folder if present
            src_libs = os.path.join(self.src_web_dir, "libs")
            dst_libs = os.path.join(target_web_dir, "libs")
            if os.path.exists(src_libs):
                if not os.path.exists(dst_libs):
                    shutil.copytree(src_libs, dst_libs)

            # 2. Copy selected HTML files and associated assets
            copied_count = 0
            for idx, html_name in enumerate(self.selected_html_files):
                pct = 15 + int(50 * (idx + 1) / max(1, len(self.selected_html_files)))
                self.progress_signal.emit(f"Copying {html_name}...", pct)

                src_html = os.path.join(self.src_web_dir, html_name)
                dst_html = os.path.join(target_web_dir, html_name)
                if os.path.exists(src_html):
                    shutil.copy2(src_html, dst_html)
                    copied_count += 1

                # Copy corresponding .sog or .ply if it exists in local output
                base_name = os.path.splitext(html_name)[0]
                for ext in [".sog", ".ply"]:
                    model_candidate = os.path.join(self.src_web_dir, base_name + ext)
                    if os.path.exists(model_candidate):
                        dst_model = os.path.join(target_web_dir, base_name + ext)
                        if not os.path.exists(dst_model) or os.path.getsize(model_candidate) != os.path.getsize(dst_model):
                            shutil.copy2(model_candidate, dst_model)

            # 3. Update models.json manifest in repo
            self.progress_signal.emit("Updating cloud models manifest...", 70)
            all_repo_htmls = [f for f in os.listdir(target_web_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
            all_repo_htmls.sort(key=lambda f: os.path.getmtime(os.path.join(target_web_dir, f)) if os.path.exists(os.path.join(target_web_dir, f)) else 0, reverse=True)
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(all_repo_htmls),
                "models": []
            }
            for h in all_repo_htmls:
                b = os.path.splitext(h)[0]
                fpath = os.path.join(target_web_dir, h)
                mtime_val = os.path.getmtime(fpath) if os.path.exists(fpath) else time.time()
                manifest["models"].append({
                    "title": b,
                    "filename": h,
                    "path": f"05_web_build/{h}",
                    "is_index": (h.lower() == "index.html"),
                    "mtime": mtime_val,
                    "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime_val))
                })
            with open(os.path.join(target_web_dir, "models.json"), "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)

            # 4. Git Stage, Commit & Push
            self.progress_signal.emit("Staging Git files...", 80)
            subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True, text=True, check=True)

            self.progress_signal.emit("Creating deployment commit...", 88)
            commit_msg = f"deploy: Selective web build update ({copied_count} models) for Vercel"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_dir, capture_output=True, text=True)

            self.progress_signal.emit("Pushing to GitHub / Vercel...", 95)
            self.log_signal.emit("Pushing changes to GitHub repository (origin/main)...", "info")
            subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_dir, capture_output=True, text=True, check=True)

            self.progress_signal.emit("Deployment Complete!", 100)
            self.success_signal.emit(f"Successfully uploaded {copied_count} model(s) to GitHub! Vercel is now building live.")
        except subprocess.CalledProcessError as cpe:
            err = cpe.stderr.strip() if (cpe.stderr and cpe.stderr.strip()) else (cpe.stdout.strip() if cpe.stdout else str(cpe))
            self.error_signal.emit(f"Git command failed: {err}")
        except Exception as ex:
            self.error_signal.emit(f"Upload error: {str(ex)}")

class CloudFileDeleteWorker(QThread):
    log_signal = pyqtSignal(str, str)
    success_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, repo_dir, files_to_delete):
        super().__init__()
        self.repo_dir = os.path.normpath(repo_dir)
        self.files_to_delete = files_to_delete

    def run(self):
        try:
            target_web_dir = os.path.normpath(os.path.join(self.repo_dir, "05_web_build"))
            deleted_count = 0

            for fname in self.files_to_delete:
                fpath = os.path.join(target_web_dir, fname)
                if os.path.exists(fpath):
                    if os.path.isdir(fpath):
                        shutil.rmtree(fpath, ignore_errors=True)
                    else:
                        os.remove(fpath)
                    deleted_count += 1

                # Also delete associated .sog / .ply
                base_name = os.path.splitext(fname)[0]
                for ext in [".sog", ".ply"]:
                    asset = os.path.join(target_web_dir, base_name + ext)
                    if os.path.exists(asset):
                        os.remove(asset)

            # Update models.json manifest
            all_repo_htmls = [f for f in os.listdir(target_web_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
            all_repo_htmls.sort(key=lambda f: os.path.getmtime(os.path.join(target_web_dir, f)) if os.path.exists(os.path.join(target_web_dir, f)) else 0, reverse=True)
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(all_repo_htmls),
                "models": []
            }
            for h in all_repo_htmls:
                b = os.path.splitext(h)[0]
                fpath = os.path.join(target_web_dir, h)
                mtime_val = os.path.getmtime(fpath) if os.path.exists(fpath) else time.time()
                manifest["models"].append({
                    "title": b,
                    "filename": h,
                    "path": f"05_web_build/{h}",
                    "is_index": (h.lower() == "index.html"),
                    "mtime": mtime_val,
                    "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime_val))
                })
            with open(os.path.join(target_web_dir, "models.json"), "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)

            # Git commit and push deletion
            subprocess.run(["git", "add", "-u"], cwd=self.repo_dir, capture_output=True, text=True, check=True)
            commit_msg = f"purge: Delete {deleted_count} model(s) from Vercel web build"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_dir, capture_output=True, text=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_dir, capture_output=True, text=True, check=True)

            self.success_signal.emit(f"Deleted {deleted_count} file(s) from Cloud! Vercel deployment purged.")
        except subprocess.CalledProcessError as cpe:
            err = cpe.stderr.strip() if (cpe.stderr and cpe.stderr.strip()) else (cpe.stdout.strip() if cpe.stdout else str(cpe))
            self.error_signal.emit(f"Git deletion failed: {err}")
        except Exception as ex:
            self.error_signal.emit(f"Delete error: {str(ex)}")

class WebPublishManagerDialog(QDialog):
    def __init__(self, src_web_dir, parent=None, translations=None):
        super().__init__(parent)
        self.src_web_dir = os.path.normpath(src_web_dir)
        self.t = translations or {}
        # Find repo root
        self.repo_dir = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.repo_web_dir = os.path.normpath(os.path.join(self.repo_dir, "05_web_build"))
        self.vercel_base_url = "https://points-and-reality.vercel.app"

        self.setWindowTitle(self.t.get("dialog_pub_title", "☁️ Web Deployment & Cloud Showroom Manager"))
        self.resize(920, 640)
        self.setMinimumSize(820, 520)
        self.init_ui()
        self.refresh_local_files()
        self.refresh_cloud_files()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Header Info Card
        header_card = QFrame()
        header_card.setStyleSheet("background-color: #14161c; border: 1px solid #20232c; border-radius: 6px; padding: 6px 10px;")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(8, 4, 8, 4)

        lbl_title = QLabel(self.t.get("dialog_pub_header_title", "☁️ Points & Reality Cloud Web Publishing"))
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ffffff;")
        
        self.pill_status = StatusPill("Vercel Ready", "ready")

        h_layout.addWidget(lbl_title)
        h_layout.addStretch()
        h_layout.addWidget(self.pill_status)
        main_layout.addWidget(header_card)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #20232c;
                background-color: #0d0f12;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #14161c;
                color: #94a3b8;
                border: 1px solid #22252e;
                border-radius: 4px;
                padding: 6px 16px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 11.5px;
            }
            QTabBar::tab:selected {
                background-color: #1d4ed8;
                color: #ffffff;
                border: 1px solid #3b82f6;
            }
        """)

        # --- Tab 1: Selective Upload ---
        tab_upload = QWidget()
        u_layout = QVBoxLayout(tab_upload)
        u_layout.setContentsMargins(12, 12, 12, 12)
        u_layout.setSpacing(10)

        # Upload Action Toolbar
        u_toolbar = QHBoxLayout()
        self.btn_select_all_upload = QPushButton(self.t.get("dialog_btn_select_all", "Select All"))
        self.btn_select_all_upload.setCursor(Qt.PointingHandCursor)
        self.btn_select_all_upload.clicked.connect(lambda: self._set_upload_selection(True))

        self.btn_clear_upload = QPushButton(self.t.get("dialog_btn_clear_sel", "Deselect All"))
        self.btn_clear_upload.setCursor(Qt.PointingHandCursor)
        self.btn_clear_upload.clicked.connect(lambda: self._set_upload_selection(False))

        self.btn_refresh_local = QPushButton(self.t.get("dialog_btn_refresh_local", "Refresh Local"))
        self.btn_refresh_local.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_local.clicked.connect(self.refresh_local_files)

        self.lbl_selected_summary = QLabel("Selected: 0 files (0 MB)")
        self.lbl_selected_summary.setStyleSheet("color: #38bdf8; font-weight: 600; font-size: 11.5px;")

        u_toolbar.addWidget(self.btn_select_all_upload)
        u_toolbar.addWidget(self.btn_clear_upload)
        u_toolbar.addWidget(self.btn_refresh_local)
        u_toolbar.addStretch()
        u_toolbar.addWidget(self.lbl_selected_summary)
        u_layout.addLayout(u_toolbar)

        # Local Files Table
        self.table_local = QTableWidget(0, 5)
        self.table_local.setHorizontalHeaderLabels([
            self.t.get("tbl_col_check", "Select"),
            self.t.get("dialog_col_html", "HTML Package"),
            self.t.get("dialog_col_asset", "3DGS Model Asset"),
            self.t.get("dialog_col_size", "Total Size"),
            self.t.get("dialog_col_modified", "Last Modified")
        ])
        self.table_local.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_local.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_local.verticalHeader().setVisible(False)
        self.table_local.verticalHeader().setDefaultSectionSize(28)
        self.table_local.setSelectionBehavior(QAbstractItemView.SelectRows)
        u_layout.addWidget(self.table_local)

        # Upload Progress Bar
        self.progress_upload = QProgressBar()
        self.progress_upload.setVisible(False)
        self.progress_upload.setTextVisible(True)
        u_layout.addWidget(self.progress_upload)

        # Upload Action Bottom Row
        u_bottom = QHBoxLayout()
        u_bottom.addStretch()
        self.btn_start_upload = QPushButton(self.t.get("dialog_btn_start_upload", "▼ 쇼룸으로 업로드"))
        self.btn_start_upload.setObjectName("SuccessBtn")
        self.btn_start_upload.setCursor(Qt.PointingHandCursor)
        self.btn_start_upload.setStyleSheet("""
            QPushButton#SuccessBtn {
                background-color: #10b981;
                border: 1px solid #34d399;
                border-radius: 6px;
                color: #ffffff;
                font-size: 12.5px;
                font-weight: 700;
                padding: 7px 28px;
                min-width: 160px;
            }
            QPushButton#SuccessBtn:hover {
                background-color: #059669;
                border-color: #6ee7b7;
            }
        """)
        self.btn_start_upload.clicked.connect(self.start_selective_upload)
        u_bottom.addWidget(self.btn_start_upload)
        u_bottom.addStretch()
        u_layout.addLayout(u_bottom)

        self.tabs.addTab(tab_upload, self.t.get("dialog_tab_upload", "📤 Selective Upload to Cloud"))

        # --- Tab 2: Live Cloud File Manager & Delete ---
        tab_cloud = QWidget()
        c_layout = QVBoxLayout(tab_cloud)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(10)

        # Cloud Toolbar
        c_toolbar = QHBoxLayout()
        self.btn_open_showroom = QPushButton(self.t.get("dialog_btn_open_showroom", "🌐 Open Live Showroom"))
        self.btn_open_showroom.setObjectName("PrimaryBtn")
        self.btn_open_showroom.setCursor(Qt.PointingHandCursor)
        self.btn_open_showroom.clicked.connect(self.open_live_showroom)

        self.btn_refresh_cloud = QPushButton(self.t.get("dialog_btn_refresh_cloud", "Refresh Cloud List"))
        self.btn_refresh_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_cloud.clicked.connect(self.refresh_cloud_files)

        self.btn_select_all_cloud = QPushButton(self.t.get("dialog_btn_select_all", "Select All"))
        self.btn_select_all_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_select_all_cloud.clicked.connect(lambda: self._set_cloud_selection(True))

        self.btn_delete_cloud = QPushButton(self.t.get("dialog_btn_delete_cloud", "🗑️ Delete Selected from Cloud"))
        self.btn_delete_cloud.setObjectName("DangerBtn")
        self.btn_delete_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_delete_cloud.clicked.connect(self.delete_selected_cloud_files)

        c_toolbar.addWidget(self.btn_open_showroom)
        c_toolbar.addWidget(self.btn_refresh_cloud)
        c_toolbar.addWidget(self.btn_select_all_cloud)
        c_toolbar.addStretch()
        c_toolbar.addWidget(self.btn_delete_cloud)
        c_layout.addLayout(c_toolbar)

        # Cloud Files Table
        self.table_cloud = QTableWidget(0, 5)
        self.table_cloud.setHorizontalHeaderLabels([
            self.t.get("tbl_col_check", "Select"),
            self.t.get("dialog_col_live_page", "Live Web Page"),
            self.t.get("dialog_col_asset", "3DGS Asset"),
            self.t.get("dialog_col_size", "Cloud Size"),
            self.t.get("dialog_col_action", "Action")
        ])
        self.table_cloud.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_cloud.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_cloud.setColumnWidth(4, 160)
        self.table_cloud.verticalHeader().setVisible(False)
        self.table_cloud.verticalHeader().setDefaultSectionSize(36)
        self.table_cloud.setSelectionBehavior(QAbstractItemView.SelectRows)
        c_layout.addWidget(self.table_cloud)

        self.tabs.addTab(tab_cloud, self.t.get("dialog_tab_cloud", "🌐 Live Cloud Manager & Delete"))

        main_layout.addWidget(self.tabs)

        # Activity Log Console
        self.console = QTextBrowser()
        self.console.setFixedHeight(90)
        self.console.setStyleSheet("background-color: #0a0b0e; border: 1px solid #1c1e26; border-radius: 4px; color: #94a3b8; font-family: Consolas; font-size: 11px;")
        main_layout.addWidget(self.console)

        # Close button row
        bottom_row = QHBoxLayout()
        self.btn_close = QPushButton(self.t.get("dialog_btn_close", "Close"))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.accept)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_close)
        main_layout.addLayout(bottom_row)

    def log(self, text, level="info"):
        colors = {"error": "#f87171", "warning": "#fbbf24", "success": "#34d399", "info": "#94a3b8"}
        c = colors.get(level.lower(), "#94a3b8")
        time_str = time.strftime("%H:%M:%S")
        self.console.append(f'<span style="color: #64748b;">[{time_str}]</span> <span style="color: {c};">{text}</span>')

    # ----------------------------------------------------------------------
    # Local Files Scanning & Selection
    # ----------------------------------------------------------------------
    def refresh_local_files(self):
        self.table_local.setRowCount(0)
        if not os.path.exists(self.src_web_dir):
            self.log("Local 05_web_build directory not found.", "warning")
            return

        html_files = [f for f in os.listdir(self.src_web_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
        # Sort newest modified file first
        html_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.src_web_dir, f)) if os.path.exists(os.path.join(self.src_web_dir, f)) else 0, reverse=True)
        self.table_local.setRowCount(len(html_files))

        for row, h in enumerate(html_files):
            h_path = os.path.join(self.src_web_dir, h)
            h_size = os.path.getsize(h_path)
            h_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(h_path)))

            # Check for linked .sog / .ply
            base = os.path.splitext(h)[0]
            linked_asset = "Embedded / None"
            total_size = h_size
            for ext in [".sog", ".ply"]:
                m_path = os.path.join(self.src_web_dir, base + ext)
                if os.path.exists(m_path):
                    m_size = os.path.getsize(m_path)
                    linked_asset = f"{base}{ext} ({_format_size(m_size)})"
                    total_size += m_size
                    break

            # Col 0: Checkbox
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(6, 0, 6, 0)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk = QCheckBox()
            chk.setChecked(True)
            chk.stateChanged.connect(self._update_selected_summary)
            chk_layout.addWidget(chk)
            self.table_local.setCellWidget(row, 0, chk_widget)

            # Col 1: HTML Package
            item_html = QTableWidgetItem(h)
            item_html.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_local.setItem(row, 1, item_html)

            # Col 2: Linked 3DGS Asset
            item_asset = QTableWidgetItem(linked_asset)
            item_asset.setTextAlignment(Qt.AlignCenter)
            item_asset.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_local.setItem(row, 2, item_asset)

            # Col 3: Total Size
            item_size = QTableWidgetItem(_format_size(total_size))
            item_size.setTextAlignment(Qt.AlignCenter)
            item_size.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_local.setItem(row, 3, item_size)

            # Col 4: Modified Time
            item_time = QTableWidgetItem(h_time)
            item_time.setTextAlignment(Qt.AlignCenter)
            item_time.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_local.setItem(row, 4, item_time)

        self._update_selected_summary()
        self.log(f"Found {len(html_files)} WebGL package(s) in local 05_web_build.", "info")

    def _set_upload_selection(self, checked):
        for r in range(self.table_local.rowCount()):
            w = self.table_local.cellWidget(r, 0)
            if w and w.findChild(QCheckBox):
                w.findChild(QCheckBox).setChecked(checked)
        self._update_selected_summary()

    def _get_selected_upload_files(self):
        selected = []
        for r in range(self.table_local.rowCount()):
            w = self.table_local.cellWidget(r, 0)
            if w and w.findChild(QCheckBox) and w.findChild(QCheckBox).isChecked():
                item = self.table_local.item(r, 1)
                if item:
                    selected.append(item.text())
        return selected

    def _update_selected_summary(self):
        selected_files = self._get_selected_upload_files()
        total_bytes = 0
        for h in selected_files:
            hp = os.path.join(self.src_web_dir, h)
            if os.path.exists(hp):
                total_bytes += os.path.getsize(hp)
            base = os.path.splitext(h)[0]
            for ext in [".sog", ".ply"]:
                mp = os.path.join(self.src_web_dir, base + ext)
                if os.path.exists(mp):
                    total_bytes += os.path.getsize(mp)
        self.lbl_selected_summary.setText(f"Selected: {len(selected_files)} files ({_format_size(total_bytes)})")

    # ----------------------------------------------------------------------
    # Upload Execution
    # ----------------------------------------------------------------------
    def start_selective_upload(self):
        selected_files = self._get_selected_upload_files()
        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one WebGL package to upload.")
            return

        self.btn_start_upload.setEnabled(False)
        self.progress_upload.setVisible(True)
        self.progress_upload.setValue(0)
        self.pill_status.set_status("Uploading...", "running")

        self.upload_worker = SelectiveVercelUploadWorker(self.src_web_dir, self.repo_dir, selected_files)
        self.upload_worker.progress_signal.connect(lambda msg, val: self._on_upload_progress(msg, val))
        self.upload_worker.log_signal.connect(self.log)
        self.upload_worker.success_signal.connect(self._on_upload_success)
        self.upload_worker.error_signal.connect(self._on_upload_error)
        self.upload_worker.start()

    def _on_upload_progress(self, msg, val):
        self.progress_upload.setValue(val)
        self.progress_upload.setFormat(f"{msg} ({val}%)")

    def _on_upload_success(self, msg):
        self.btn_start_upload.setEnabled(True)
        self.progress_upload.setVisible(False)
        self.pill_status.set_status("Live (Vercel)", "success")
        self.log(msg, "success")
        self.refresh_cloud_files()
        QMessageBox.information(self, "Upload Complete", f"✅ {msg}\n\nLive Showroom URL:\n{self.vercel_base_url}/showroom.html")

    def _on_upload_error(self, err_msg):
        self.btn_start_upload.setEnabled(True)
        self.progress_upload.setVisible(False)
        self.pill_status.set_status("Upload Error", "error")
        self.log(f"[ERROR] {err_msg}", "error")
        QMessageBox.critical(self, "Upload Failed", f"❌ Failed to push files to Vercel/GitHub:\n\n{err_msg}")

    # ----------------------------------------------------------------------
    # Live Cloud Files Scanning & Deletion
    # ----------------------------------------------------------------------
    def refresh_cloud_files(self):
        self.table_cloud.setRowCount(0)
        if not os.path.exists(self.repo_web_dir):
            self.log("Repository 05_web_build directory not found.", "warning")
            return

        html_files = [f for f in os.listdir(self.repo_web_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
        # Sort newest modified file first
        html_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.repo_web_dir, f)) if os.path.exists(os.path.join(self.repo_web_dir, f)) else 0, reverse=True)
        self.table_cloud.setRowCount(len(html_files))

        for row, h in enumerate(html_files):
            h_path = os.path.join(self.repo_web_dir, h)
            h_size = os.path.getsize(h_path)

            base = os.path.splitext(h)[0]
            linked_asset = "Embedded"
            total_size = h_size
            for ext in [".sog", ".ply"]:
                m_path = os.path.join(self.repo_web_dir, base + ext)
                if os.path.exists(m_path):
                    m_size = os.path.getsize(m_path)
                    linked_asset = f"{base}{ext}"
                    total_size += m_size
                    break

            # Col 0: Checkbox
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(6, 0, 6, 0)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk = QCheckBox()
            chk_layout.addWidget(chk)
            self.table_cloud.setCellWidget(row, 0, chk_widget)

            # Col 1: Page Name
            item_page = QTableWidgetItem(h)
            item_page.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_cloud.setItem(row, 1, item_page)

            # Col 2: Asset
            item_asset = QTableWidgetItem(linked_asset)
            item_asset.setTextAlignment(Qt.AlignCenter)
            item_asset.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_cloud.setItem(row, 2, item_asset)

            # Col 3: Cloud Size
            item_size = QTableWidgetItem(_format_size(total_size))
            item_size.setTextAlignment(Qt.AlignCenter)
            item_size.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table_cloud.setItem(row, 3, item_size)

            # Col 4: Action (Open Live URL button & Copy URL button)
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 3, 4, 3)
            a_layout.setSpacing(6)
            a_layout.setAlignment(Qt.AlignCenter)

            btn_open_live = QPushButton("🌐 Open")
            btn_open_live.setCursor(Qt.PointingHandCursor)
            btn_open_live.setStyleSheet("""
                QPushButton {
                    background-color: #0284c7;
                    color: #ffffff;
                    border: 1px solid #38bdf8;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 24px;
                    max-height: 24px;
                    padding: 1px 8px;
                }
                QPushButton:hover { background-color: #0369a1; }
            """)
            target_url = f"{self.vercel_base_url}/{h}"
            btn_open_live.clicked.connect(lambda _, u=target_url: webbrowser.open(u))

            btn_copy = QPushButton("📋 URL")
            btn_copy.setCursor(Qt.PointingHandCursor)
            btn_copy.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #cbd5e1;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 24px;
                    max-height: 24px;
                    padding: 1px 8px;
                }
                QPushButton:hover { background-color: #334155; color: #ffffff; }
            """)
            def _copy_url(url=target_url, b=btn_copy):
                QApplication.clipboard().setText(url)
                b.setText("✅ Copied")
            btn_copy.clicked.connect(lambda _, u=target_url, b=btn_copy: _copy_url(u, b))

            a_layout.addWidget(btn_open_live)
            a_layout.addWidget(btn_copy)
            self.table_cloud.setCellWidget(row, 4, action_widget)

        self.log(f"Synced {len(html_files)} deployed model(s) from cloud repository.", "info")

    def _set_cloud_selection(self, checked):
        for r in range(self.table_cloud.rowCount()):
            w = self.table_cloud.cellWidget(r, 0)
            if w and w.findChild(QCheckBox):
                w.findChild(QCheckBox).setChecked(checked)

    def _get_selected_cloud_files(self):
        selected = []
        for r in range(self.table_cloud.rowCount()):
            w = self.table_cloud.cellWidget(r, 0)
            if w and w.findChild(QCheckBox) and w.findChild(QCheckBox).isChecked():
                item = self.table_cloud.item(r, 1)
                if item:
                    selected.append(item.text())
        return selected

    def delete_selected_cloud_files(self):
        selected = self._get_selected_cloud_files()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one cloud model to delete.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Cloud Deletion",
            f"Are you sure you want to delete {len(selected)} model(s) from Vercel web deployment?\n\n"
            f"Files to purge:\n" + "\n".join(f"• {f}" for f in selected) + "\n\nThis will remove them from GitHub and live Vercel.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        self.btn_delete_cloud.setEnabled(False)
        self.pill_status.set_status("Purging...", "running")
        self.log(f"Deleting {len(selected)} model(s) from cloud repository...", "warning")

        self.delete_worker = CloudFileDeleteWorker(self.repo_dir, selected)
        self.delete_worker.log_signal.connect(self.log)
        self.delete_worker.success_signal.connect(self._on_delete_success)
        self.delete_worker.error_signal.connect(self._on_delete_error)
        self.delete_worker.start()

    def _on_delete_success(self, msg):
        self.btn_delete_cloud.setEnabled(True)
        self.pill_status.set_status("Purged", "success")
        self.log(msg, "success")
        self.refresh_cloud_files()
        QMessageBox.information(self, "Deletion Complete", f"✅ {msg}")

    def _on_delete_error(self, err_msg):
        self.btn_delete_cloud.setEnabled(True)
        self.pill_status.set_status("Error", "error")
        self.log(f"[ERROR] {err_msg}", "error")
        QMessageBox.critical(self, "Delete Failed", f"❌ Failed to delete files:\n\n{err_msg}")

    def open_live_showroom(self):
        url = f"{self.vercel_base_url}/showroom.html"
        webbrowser.open(url)
        self.log(f"Opened Live Showroom: {url}", "info")
