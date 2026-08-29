# ui/tabs/tab_showroom.py
import os
import shutil
import json
import time
import subprocess
import webbrowser
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QAbstractItemView, QCheckBox, 
                             QScrollArea, QFrame, QProgressBar, QMessageBox, 
                             QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
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

class ShowroomUploadWorker(QThread):
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
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(all_repo_htmls),
                "models": []
            }
            for h in sorted(all_repo_htmls):
                b = os.path.splitext(h)[0]
                manifest["models"].append({
                    "title": b,
                    "filename": h,
                    "path": f"05_web_build/{h}",
                    "is_index": (h.lower() == "index.html")
                })
            with open(os.path.join(target_web_dir, "models.json"), "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)

            # 4. Git Stage, Commit & Push
            self.progress_signal.emit("Staging Git files...", 80)
            subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True, text=True, check=True)

            self.progress_signal.emit("Creating deployment commit...", 88)
            commit_msg = f"deploy: Update web build models ({copied_count} items) for Vercel Showroom"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_dir, capture_output=True, text=True)

            self.progress_signal.emit("Pushing to GitHub / Vercel...", 95)
            self.log_signal.emit("Pushing changes to GitHub repository (origin/main)...", "info")
            subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_dir, capture_output=True, text=True, check=True)

            self.progress_signal.emit("Deployment Complete!", 100)
            self.success_signal.emit(f"Successfully uploaded {copied_count} model(s) to GitHub! Vercel is building live.")
        except subprocess.CalledProcessError as cpe:
            err = cpe.stderr.strip() if (cpe.stderr and cpe.stderr.strip()) else (cpe.stdout.strip() if cpe.stdout else str(cpe))
            self.error_signal.emit(f"Git operation failed: {err}")
        except Exception as ex:
            self.error_signal.emit(f"Upload error: {str(ex)}")

class ShowroomDeleteWorker(QThread):
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
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(all_repo_htmls),
                "models": []
            }
            for h in sorted(all_repo_htmls):
                b = os.path.splitext(h)[0]
                manifest["models"].append({
                    "title": b,
                    "filename": h,
                    "path": f"05_web_build/{h}",
                    "is_index": (h.lower() == "index.html")
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

class ShowroomTab(QWidget):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proj_dir = ""
        self.current_translations = {}
        # Find repo root
        self.repo_dir = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.repo_web_dir = os.path.normpath(os.path.join(self.repo_dir, "05_web_build"))
        self.vercel_base_url = "https://points-and-reality.vercel.app"

        self.init_ui()

    def set_proj_dir(self, path):
        self.proj_dir = os.path.normpath(path) if path else ""
        self.refresh_local_files()
        self.refresh_cloud_files()

    def init_ui(self):
        tab_layout = QVBoxLayout(self)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_content = QWidget()
        scroll_content.setObjectName("showroomScrollContent")
        scroll_content.setStyleSheet("QWidget#showroomScrollContent { background-color: transparent; }")
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(0, 4, 4, 4)
        main_layout.setSpacing(10)

        # ----------------------------------------------------
        # Card 1: Live Cloud Showroom & Remote Vercel Manager
        # ----------------------------------------------------
        self.card_cloud = ModernStepCard(
            step_num="", 
            title="Live Cloud Showroom & Vercel Resources", 
            subtitle="Manage published 3DGS models, open live browser view, and purge remote models"
        )
        self.pill_cloud = StatusPill("Live (Vercel)", "success")
        self.card_cloud.add_header_action(self.pill_cloud)

        self.btn_header_open_showroom = QPushButton("🌐 Open Showroom")
        self.btn_header_open_showroom.setCursor(Qt.PointingHandCursor)
        self.btn_header_open_showroom.setStyleSheet("""
            QPushButton {
                background-color: #0369a1;
                border: 1px solid #38bdf8;
                border-radius: 4px;
                color: #ffffff;
                font-size: 11px;
                font-weight: 600;
                min-height: 22px;
                padding: 1px 10px;
            }
            QPushButton:hover { background-color: #0284c7; }
        """)
        self.btn_header_open_showroom.clicked.connect(self.open_live_showroom)
        self.card_cloud.add_header_action(self.btn_header_open_showroom)

        c1_layout = QVBoxLayout()
        c1_layout.setSpacing(10)

        # Cloud Toolbar
        c_toolbar = QHBoxLayout()
        self.btn_refresh_cloud = QPushButton("🔄 Refresh Live List")
        self.btn_refresh_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_cloud.clicked.connect(self.refresh_cloud_files)

        self.btn_select_all_cloud = QPushButton("Select All")
        self.btn_select_all_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_select_all_cloud.clicked.connect(lambda: self._set_cloud_selection(True))

        self.btn_clear_cloud = QPushButton("Deselect All")
        self.btn_clear_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_clear_cloud.clicked.connect(lambda: self._set_cloud_selection(False))

        self.btn_delete_cloud = QPushButton("🗑️ Delete Selected from Cloud")
        self.btn_delete_cloud.setObjectName("DangerBtn")
        self.btn_delete_cloud.setCursor(Qt.PointingHandCursor)
        self.btn_delete_cloud.clicked.connect(self.delete_selected_cloud_files)

        c_toolbar.addWidget(self.btn_refresh_cloud)
        c_toolbar.addWidget(self.btn_select_all_cloud)
        c_toolbar.addWidget(self.btn_clear_cloud)
        c_toolbar.addStretch()
        c_toolbar.addWidget(self.btn_delete_cloud)
        c1_layout.addLayout(c_toolbar)

        # Cloud Files Table
        self.table_cloud = QTableWidget(0, 5)
        self.table_cloud.setHorizontalHeaderLabels([
            "Select", "Live Web Page", "3DGS Model Asset", "Cloud Size", "Actions"
        ])
        self.table_cloud.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_cloud.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_cloud.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_cloud.verticalHeader().setVisible(False)
        self.table_cloud.verticalHeader().setDefaultSectionSize(28)
        self.table_cloud.setSelectionBehavior(QAbstractItemView.SelectRows)
        c1_layout.addWidget(self.table_cloud)

        self.card_cloud.setContentLayout(c1_layout)
        main_layout.addWidget(self.card_cloud)

        # ----------------------------------------------------
        # Card 2: Selective Local Package Sync & Web Deployer
        # ----------------------------------------------------
        self.card_upload = ModernStepCard(
            step_num="", 
            title="Local Package Deployment & Selective Upload", 
            subtitle="Select built WebGL packages from 05_web_build and publish to Vercel"
        )
        self.pill_upload = StatusPill("Ready", "ready")
        self.card_upload.add_header_action(self.pill_upload)

        c2_layout = QVBoxLayout()
        c2_layout.setSpacing(10)

        # Upload Action Toolbar
        u_toolbar = QHBoxLayout()
        self.btn_refresh_local = QPushButton("🔄 Refresh Local")
        self.btn_refresh_local.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_local.clicked.connect(self.refresh_local_files)

        self.btn_select_all_upload = QPushButton("Select All")
        self.btn_select_all_upload.setCursor(Qt.PointingHandCursor)
        self.btn_select_all_upload.clicked.connect(lambda: self._set_upload_selection(True))

        self.btn_clear_upload = QPushButton("Deselect All")
        self.btn_clear_upload.setCursor(Qt.PointingHandCursor)
        self.btn_clear_upload.clicked.connect(lambda: self._set_upload_selection(False))

        self.lbl_selected_summary = QLabel("Selected: 0 files (0 MB)")
        self.lbl_selected_summary.setStyleSheet("color: #38bdf8; font-weight: 600; font-size: 11.5px;")

        u_toolbar.addWidget(self.btn_refresh_local)
        u_toolbar.addWidget(self.btn_select_all_upload)
        u_toolbar.addWidget(self.btn_clear_upload)
        u_toolbar.addStretch()
        u_toolbar.addWidget(self.lbl_selected_summary)
        c2_layout.addLayout(u_toolbar)

        # Local Files Table
        self.table_local = QTableWidget(0, 5)
        self.table_local.setHorizontalHeaderLabels([
            "Select", "HTML Package", "3DGS Model Asset", "Total Size", "Last Modified"
        ])
        self.table_local.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_local.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_local.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_local.verticalHeader().setVisible(False)
        self.table_local.verticalHeader().setDefaultSectionSize(28)
        self.table_local.setSelectionBehavior(QAbstractItemView.SelectRows)
        c2_layout.addWidget(self.table_local)

        # Upload Progress Bar
        self.progress_upload = QProgressBar()
        self.progress_upload.setVisible(False)
        self.progress_upload.setTextVisible(True)
        c2_layout.addWidget(self.progress_upload)

        # Upload Action Bottom Row
        u_bottom = QHBoxLayout()
        self.btn_start_upload = QPushButton("🚀 Upload Selected Packages to Vercel")
        self.btn_start_upload.setObjectName("SuccessBtn")
        self.btn_start_upload.setCursor(Qt.PointingHandCursor)
        self.btn_start_upload.setStyleSheet("padding: 8px 22px; font-weight: 600; font-size: 12.5px;")
        self.btn_start_upload.clicked.connect(self.start_selective_upload)

        u_bottom.addStretch()
        u_bottom.addWidget(self.btn_start_upload)
        c2_layout.addLayout(u_bottom)

        self.card_upload.setContentLayout(c2_layout)
        main_layout.addWidget(self.card_upload)
        main_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)

        self.refresh_cloud_files()
        self.refresh_local_files()

    # ----------------------------------------------------------------------
    # Cloud Showroom Actions
    # ----------------------------------------------------------------------
    def open_live_showroom(self):
        url = f"{self.vercel_base_url}/showroom.html"
        webbrowser.open(url)
        self.log_signal.emit(f"Opened Live Showroom: {url}", "info")

    def refresh_cloud_files(self):
        self.table_cloud.setRowCount(0)
        if not os.path.exists(self.repo_web_dir):
            return

        html_files = [f for f in os.listdir(self.repo_web_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
        self.table_cloud.setRowCount(len(html_files))

        for row, h in enumerate(sorted(html_files)):
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

            # Col 4: Action (Open Live URL button)
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(6)
            a_layout.setAlignment(Qt.AlignCenter)

            btn_open = QPushButton("🌐 Open")
            btn_open.setCursor(Qt.PointingHandCursor)
            btn_open.setStyleSheet("background-color: #0284c7; color: white; border: 1px solid #38bdf8; border-radius: 3px; font-size: 10.5px; padding: 2px 8px;")
            target_url = f"{self.vercel_base_url}/{h}"
            btn_open.clicked.connect(lambda _, u=target_url: webbrowser.open(u))

            btn_copy = QPushButton("📋 URL")
            btn_copy.setCursor(Qt.PointingHandCursor)
            btn_copy.setStyleSheet("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 3px; font-size: 10.5px; padding: 2px 6px;")
            def _copy_url(url=target_url, b=btn_copy):
                QApplication.clipboard().setText(url)
                b.setText("✅ Copied")
            btn_copy.clicked.connect(lambda _, u=target_url, b=btn_copy: _copy_url(u, b))

            a_layout.addWidget(btn_open)
            a_layout.addWidget(btn_copy)
            self.table_cloud.setCellWidget(row, 4, action_widget)

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
        self.pill_cloud.set_status("Purging...", "running")
        self.log_signal.emit(f"Deleting {len(selected)} model(s) from cloud repository...", "warning")

        self.delete_worker = ShowroomDeleteWorker(self.repo_dir, selected)
        self.delete_worker.log_signal.connect(lambda msg, lvl: self.log_signal.emit(msg, lvl))
        self.delete_worker.success_signal.connect(self._on_delete_success)
        self.delete_worker.error_signal.connect(self._on_delete_error)
        self.delete_worker.start()

    def _on_delete_success(self, msg):
        self.btn_delete_cloud.setEnabled(True)
        self.pill_cloud.set_status("Purged", "success")
        self.log_signal.emit(f"[SUCCESS] {msg}", "success")
        self.refresh_cloud_files()
        QMessageBox.information(self, "Deletion Complete", f"✅ {msg}")

    def _on_delete_error(self, err_msg):
        self.btn_delete_cloud.setEnabled(True)
        self.pill_cloud.set_status("Error", "error")
        self.log_signal.emit(f"[ERROR] {err_msg}", "error")
        QMessageBox.critical(self, "Delete Failed", f"❌ Failed to delete files:\n\n{err_msg}")

    # ----------------------------------------------------------------------
    # Local Package Scanning & Upload
    # ----------------------------------------------------------------------
    def get_effective_local_dir(self):
        if self.proj_dir:
            candidate = os.path.join(self.proj_dir, "05_web_build")
            if os.path.exists(candidate):
                return candidate
        return self.repo_web_dir

    def refresh_local_files(self):
        self.table_local.setRowCount(0)
        local_dir = self.get_effective_local_dir()
        if not os.path.exists(local_dir):
            return

        html_files = [f for f in os.listdir(local_dir) if f.lower().endswith('.html') and f.lower() not in ["showroom.html", "gallery.html"]]
        self.table_local.setRowCount(len(html_files))

        for row, h in enumerate(sorted(html_files)):
            h_path = os.path.join(local_dir, h)
            h_size = os.path.getsize(h_path)
            h_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(h_path)))

            base = os.path.splitext(h)[0]
            linked_asset = "Embedded"
            total_size = h_size
            for ext in [".sog", ".ply"]:
                m_path = os.path.join(local_dir, base + ext)
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

            # Col 2: Linked Asset
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
        local_dir = self.get_effective_local_dir()
        selected_files = self._get_selected_upload_files()
        total_bytes = 0
        for h in selected_files:
            hp = os.path.join(local_dir, h)
            if os.path.exists(hp):
                total_bytes += os.path.getsize(hp)
            base = os.path.splitext(h)[0]
            for ext in [".sog", ".ply"]:
                mp = os.path.join(local_dir, base + ext)
                if os.path.exists(mp):
                    total_bytes += os.path.getsize(mp)
        self.lbl_selected_summary.setText(f"Selected: {len(selected_files)} files ({_format_size(total_bytes)})")

    def start_selective_upload(self):
        local_dir = self.get_effective_local_dir()
        selected_files = self._get_selected_upload_files()
        if not selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one WebGL package to upload.")
            return

        self.btn_start_upload.setEnabled(False)
        self.progress_upload.setVisible(True)
        self.progress_upload.setValue(0)
        self.pill_upload.set_status("Uploading...", "running")

        self.upload_worker = ShowroomUploadWorker(local_dir, self.repo_dir, selected_files)
        self.upload_worker.progress_signal.connect(lambda msg, val: self._on_upload_progress(msg, val))
        self.upload_worker.log_signal.connect(lambda msg, lvl: self.log_signal.emit(msg, lvl))
        self.upload_worker.success_signal.connect(self._on_upload_success)
        self.upload_worker.error_signal.connect(self._on_upload_error)
        self.upload_worker.start()

    def _on_upload_progress(self, msg, val):
        self.progress_upload.setValue(val)
        self.progress_upload.setFormat(f"{msg} ({val}%)")

    def _on_upload_success(self, msg):
        self.btn_start_upload.setEnabled(True)
        self.progress_upload.setVisible(False)
        self.pill_upload.set_status("Uploaded", "success")
        self.pill_cloud.set_status("Live (Vercel)", "success")
        self.log_signal.emit(f"[SUCCESS] {msg}", "success")
        self.refresh_cloud_files()
        QMessageBox.information(self, "Upload Complete", f"✅ {msg}\n\nLive Showroom URL:\n{self.vercel_base_url}/showroom.html")

    def _on_upload_error(self, err_msg):
        self.btn_start_upload.setEnabled(True)
        self.progress_upload.setVisible(False)
        self.pill_upload.set_status("Upload Error", "error")
        self.log_signal.emit(f"[ERROR] {err_msg}", "error")
        QMessageBox.critical(self, "Upload Failed", f"❌ Failed to push files to Vercel/GitHub:\n\n{err_msg}")

    def update_language(self, t):
        self.current_translations = t
        if hasattr(self, 'card_cloud'):
            self.card_cloud.setTitle(
                t.get("tab4_card1_title", "Live Cloud Showroom & Vercel Resources"),
                t.get("tab4_card1_sub", "Manage published 3DGS models, open live browser view, and purge remote models")
            )
        if hasattr(self, 'card_upload'):
            self.card_upload.setTitle(
                t.get("tab4_card2_title", "Local Package Deployment & Selective Upload"),
                t.get("tab4_card2_sub", "Select built WebGL packages from 05_web_build and publish to Vercel")
            )
        if hasattr(self, 'btn_header_open_showroom'):
            self.btn_header_open_showroom.setText(t.get("tab4_btn_open_showroom", "🌐 Open Showroom"))
        if hasattr(self, 'btn_refresh_cloud'):
            self.btn_refresh_cloud.setText(t.get("tab4_btn_refresh_cloud", "🔄 Refresh Live List"))
        if hasattr(self, 'btn_delete_cloud'):
            self.btn_delete_cloud.setText(t.get("tab4_btn_delete_cloud", "🗑️ Delete Selected from Cloud"))
        if hasattr(self, 'btn_refresh_local'):
            self.btn_refresh_local.setText(t.get("tab4_btn_refresh_local", "🔄 Refresh Local"))
        if hasattr(self, 'btn_start_upload'):
            self.btn_start_upload.setText(t.get("tab4_btn_start_upload", "🚀 Upload Selected Packages to Vercel"))
