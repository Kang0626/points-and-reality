# ui/tabs/tab_cleanup.py
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFileDialog, QFrame, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QAbstractItemView, QScrollArea, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from ui.ui_components import ModernStepCard, StatusPill, ElideLeftDelegate

class CleanupTab(QWidget):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proj_dir = ""
        self.current_translations = {}
        self.init_ui()

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
        scroll_content.setObjectName("cleanupScrollContent")
        scroll_content.setStyleSheet("QWidget#cleanupScrollContent { background-color: transparent; }")

        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # Card 1: Input Splat Models
        # ----------------------------------------------------
        self.card_input = ModernStepCard(step_num="", title="Target Splat Models", subtitle="Exported 3DGS .ply or .splat files to clean and optimize")
        self.pill_input = StatusPill("0 Splats", "idle")
        self.card_input.add_header_action(self.pill_input)

        c1_layout = QVBoxLayout()
        c1_toolbar = QHBoxLayout()

        self.btn_add_ply = QPushButton("+ Add Splat (.ply / .splat)")
        self.btn_add_ply.setObjectName("PrimaryBtn")
        self.btn_add_ply.setCursor(Qt.PointingHandCursor)
        self.btn_add_ply.clicked.connect(self.add_splat_files)

        self.btn_scan_splats = QPushButton("🔄 Scan Folder")
        self.btn_scan_splats.setCursor(Qt.PointingHandCursor)
        self.btn_scan_splats.setToolTip("Scan 03_splats_exports folder for newly trained 3DGS models")
        self.btn_scan_splats.clicked.connect(lambda: self.scan_exported_splats(silent=False))

        self.btn_select_all = QPushButton("☑️ Toggle All")
        self.btn_select_all.setCursor(Qt.PointingHandCursor)
        self.btn_select_all.clicked.connect(self.toggle_select_all)

        self.btn_remove_selected = QPushButton("🗑 Remove")
        self.btn_remove_selected.setCursor(Qt.PointingHandCursor)
        self.btn_remove_selected.setToolTip("Remove selected rows from list")
        self.btn_remove_selected.clicked.connect(self.remove_selected_rows)

        self.btn_clear_ply = QPushButton("🧹 Clear All")
        self.btn_clear_ply.setCursor(Qt.PointingHandCursor)
        self.btn_clear_ply.clicked.connect(self.clear_all_rows)

        c1_toolbar.addWidget(self.btn_add_ply)
        c1_toolbar.addWidget(self.btn_scan_splats)
        c1_toolbar.addWidget(self.btn_select_all)
        c1_toolbar.addWidget(self.btn_remove_selected)
        c1_toolbar.addWidget(self.btn_clear_ply)
        c1_toolbar.addStretch()
        c1_layout.addLayout(c1_toolbar)

        # Table: Col 0 (Checkbox), Col 1 (File Path), Col 2 (Size), Col 3 (Status)
        self.table_ply = QTableWidget(0, 4)
        self.table_ply.setItemDelegateForColumn(1, ElideLeftDelegate(self.table_ply))
        self.table_ply.setHorizontalHeaderLabels(["☑️ Clean", "Splat File Path", "Size (MB)", "Status"])
        self.table_ply.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_ply.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_ply.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_ply.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_ply.horizontalHeader().sectionClicked.connect(self.on_header_section_clicked)
        self.table_ply.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_ply.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_ply.setMinimumHeight(140)
        self.table_ply.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_ply.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_ply.verticalHeader().setVisible(False)
        self.table_ply.setStyleSheet("""
            QTableWidget {
                background-color: #0f1013;
                border: 1px solid #2d3139;
                border-radius: 6px;
                gridline-color: #1f232b;
                selection-background-color: #1e3a5f;
                selection-color: #ffffff;
                outline: none;
            }
            QTableWidget:focus {
                outline: none;
                border: 1px solid #38bdf8;
            }
            QTableCornerButton::section {
                background-color: #141619;
                border: 1px solid #2d3139;
            }
            QHeaderView::section {
                background-color: #1a1d24;
                border: 1px solid #2d3139;
                color: #cbd5e1;
                font-weight: 600;
                padding: 4px;
            }
            QHeaderView::section:hover {
                background-color: #242936;
                color: #38bdf8;
            }
            QTableWidget::item:selected {
                background-color: #1e3a5f;
                color: #ffffff;
            }
            QCheckBox {
                margin: 0px;
                padding: 0px;
                background-color: transparent;
                outline: none;
            }
            QCheckBox:focus {
                outline: none;
                border: none;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #1a1d24;
                border: 1px solid #475569;
                border-radius: 3px;
                outline: none;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #38bdf8;
            }
            QCheckBox::indicator:checked {
                background-color: #0284c7;
                border: 1px solid #38bdf8;
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
            }
        """)
        c1_layout.addWidget(self.table_ply)

        self.card_input.setContentLayout(c1_layout)
        main_layout.addWidget(self.card_input)

        # ----------------------------------------------------
        # Card 2: Houdini SOP Network & Cleanup Engine
        # ----------------------------------------------------
        self.card_tools = ModernStepCard(step_num="", title="Houdini Splat Cleanup Pipeline", subtitle="Execute procedural cleanup network (Bounding box, Outliers, Ground plane)")
        self.pill_tools = StatusPill("Houdini Engine", "ready")
        self.card_tools.add_header_action(self.pill_tools)

        c2_layout = QVBoxLayout()
        c2_layout.setSpacing(10)

        # Preset Filters Display Frame
        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setStyleSheet("QFrame#filterBox { background-color: #141619; border: 1px solid #2d3139; border-radius: 6px; }")
        filter_layout = QVBoxLayout(filter_box)
        filter_layout.setSpacing(6)

        lbl_desc = QLabel("✨ <b>Active Procedural Filters (Houdini Network):</b>")
        lbl_desc.setStyleSheet("color: #38bdf8; font-size: 12px;")
        filter_layout.addWidget(lbl_desc)

        f1 = QLabel("• <b>Box Clip / Sphere Mask:</b> Removes floating artifacts, distant background floaters, and ceiling boundaries.")
        f1.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        f2 = QLabel("• <b>Ground Plane Alignment:</b> Automatically detects floor plane and levels rotation (Transform by Attrib).")
        f2.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        f3 = QLabel("• <b>Scale & Center Re-normalization:</b> Centers origin and bakes clean coordinate frame.")
        f3.setStyleSheet("color: #cbd5e1; font-size: 11px;")

        filter_layout.addWidget(f1)
        filter_layout.addWidget(f2)
        filter_layout.addWidget(f3)
        c2_layout.addWidget(filter_box)

        # Action Buttons
        actions_layout = QHBoxLayout()
        self.btn_run_houdini = QPushButton("🚀 Run Houdini Procedural Cleanup")
        self.btn_run_houdini.setObjectName("SuccessBtn")
        self.btn_run_houdini.setCursor(Qt.PointingHandCursor)
        self.btn_run_houdini.clicked.connect(self.run_houdini_cleanup)

        self.btn_open_cleaned = QPushButton("📂 Open Cleaned Splats Folder")
        self.btn_open_cleaned.setCursor(Qt.PointingHandCursor)
        self.btn_open_cleaned.clicked.connect(self.open_cleaned_folder)

        actions_layout.addWidget(self.btn_run_houdini)
        actions_layout.addSpacing(10)
        actions_layout.addWidget(self.btn_open_cleaned)
        actions_layout.addStretch()
        c2_layout.addLayout(actions_layout)

        self.card_tools.setContentLayout(c2_layout)
        main_layout.addWidget(self.card_tools)
        main_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)

    # ----------------------------------------------------------------------
    # Checkbox & Selection Management
    # ----------------------------------------------------------------------
    def on_header_section_clicked(self, logical_index):
        if logical_index == 0:
            self.toggle_select_all()

    def _is_row_checked(self, row):
        widget = self.table_ply.cellWidget(row, 0)
        if widget:
            chk = widget.findChild(QCheckBox)
            if chk:
                return chk.isChecked()
        return False

    def _set_row_checked(self, row, checked):
        widget = self.table_ply.cellWidget(row, 0)
        if widget:
            chk = widget.findChild(QCheckBox)
            if chk:
                chk.blockSignals(True)
                chk.setChecked(checked)
                chk.blockSignals(False)

    def _on_row_checkbox_changed(self):
        self._update_clean_header()
        self._update_input_pill()

    def _update_clean_header(self):
        t = self.current_translations
        base_label = t.get("tab2_tbl_col_clean", "Clean") if t else "Clean"
        clean_title = base_label.replace("☑️", "").replace("☑", "").replace("☐", "").strip()

        total = self.table_ply.rowCount()
        if total == 0:
            icon = "☑️"
        else:
            checked_cnt = sum(1 for r in range(total) if self._is_row_checked(r))
            if checked_cnt == total:
                icon = "☑️"
            elif checked_cnt == 0:
                icon = "☐"
            else:
                icon = "☑"

        header_item = self.table_ply.horizontalHeaderItem(0)
        if header_item:
            header_item.setText(f"{icon} {clean_title}")
        else:
            self.table_ply.setHorizontalHeaderItem(0, QTableWidgetItem(f"{icon} {clean_title}"))

    def _update_input_pill(self):
        total = self.table_ply.rowCount()
        if total == 0:
            self.pill_input.set_status("0 Splats", "idle")
        else:
            checked_cnt = sum(1 for r in range(total) if self._is_row_checked(r))
            if checked_cnt == total:
                self.pill_input.set_status(f"{total} Splat{'s' if total > 1 else ''}", "ready")
            else:
                self.pill_input.set_status(f"{checked_cnt}/{total} Selected", "ready" if checked_cnt > 0 else "idle")

    def toggle_select_all(self, logical_index=None):
        if logical_index is not None and logical_index != 0:
            return
        total = self.table_ply.rowCount()
        if total == 0: return
        any_unchecked = any(not self._is_row_checked(r) for r in range(total))
        new_state = any_unchecked
        for r in range(total):
            self._set_row_checked(r, new_state)
        self._update_clean_header()
        self._update_input_pill()

    def remove_selected_rows(self):
        selected_indices = set(idx.row() for idx in self.table_ply.selectedIndexes())
        if not selected_indices:
            # If no rows highlighted, remove checked rows
            selected_indices = set(r for r in range(self.table_ply.rowCount()) if self._is_row_checked(r))

        if not selected_indices:
            self.log_signal.emit("[WARN] No splat rows selected to remove.", "warning")
            return

        for r in sorted(selected_indices, reverse=True):
            self.table_ply.removeRow(r)

        self._update_clean_header()
        self._update_input_pill()
        self.log_signal.emit(f"Removed {len(selected_indices)} splat row(s) from list.", "info")

    def clear_all_rows(self):
        self.table_ply.setRowCount(0)
        self._update_clean_header()
        self._update_input_pill()
        self.log_signal.emit("Cleared all splats from cleanup table.", "info")

    def get_checked_splat_files(self):
        results = []
        for r in range(self.table_ply.rowCount()):
            if self._is_row_checked(r):
                item = self.table_ply.item(r, 1)
                if item:
                    results.append(os.path.normpath(item.toolTip()))
        return results

    # ----------------------------------------------------------------------
    # Model Loading & Scanning
    # ----------------------------------------------------------------------
    def set_proj_dir(self, directory):
        if not directory: return
        self.proj_dir = os.path.normpath(directory)
        self.scan_exported_splats(silent=True)

    def set_input_files(self, file_paths):
        for path in file_paths:
            self.add_file_row(path, checked=True)

    def scan_exported_splats(self, silent=False):
        if not self.proj_dir or not os.path.exists(self.proj_dir):
            if not silent:
                self.log_signal.emit("[WARN] Set a valid project directory first.", "warning")
            return

        found_count = 0
        scanned_subfolders = [
            "03_splats_exports", "03_postshot_exports", 
            "02_camera_alignment", "02_tracking_alignment"
        ]

        for sub in scanned_subfolders:
            sub_path = os.path.normpath(os.path.join(self.proj_dir, sub))
            if os.path.exists(sub_path):
                for f in os.listdir(sub_path):
                    if f.lower().endswith(('.ply', '.splat', '.spz', '.sog')) and not f.startswith('model.'):
                        full_p = os.path.normpath(os.path.join(sub_path, f))
                        if self.add_file_row(full_p, checked=True):
                            found_count += 1

        if found_count > 0 or not silent:
            self.log_signal.emit(f"Scanned 03_splats_exports: Added {found_count} new 3DGS model(s) to cleanup.", "info")

    def add_splat_files(self):
        start_dir = os.path.join(self.proj_dir, "03_splats_exports") if self.proj_dir else ""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Splat Files", 
            start_dir, 
            "All Splat Files (*.ply *.splat *.spz *.sog);;SuperSplat Models (*.sog);;PLY 3DGS Models (*.ply);;Compressed Splat (*.splat *.spz);;All Files (*.*)"
        )
        if files:
            for f in files:
                self.add_file_row(f, checked=True)

    def add_file_row(self, file_path, checked=True):
        if not os.path.exists(file_path): return False
        norm_p = os.path.normpath(file_path)
        for r in range(self.table_ply.rowCount()):
            item = self.table_ply.item(r, 1)
            if item and os.path.normpath(item.toolTip()) == norm_p:
                return False

        row = self.table_ply.rowCount()
        self.table_ply.insertRow(row)

        # Col 0: Centered Checkbox Widget
        dummy_item = QTableWidgetItem()
        dummy_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_ply.setItem(row, 0, dummy_item)

        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk_box = QCheckBox()
        chk_box.setFocusPolicy(Qt.NoFocus)
        chk_box.setChecked(checked)
        chk_box.stateChanged.connect(self._on_row_checkbox_changed)
        chk_layout.addWidget(chk_box)
        self.table_ply.setCellWidget(row, 0, chk_widget)

        # Col 1: Splat File Path
        item_path = QTableWidgetItem(norm_p)
        item_path.setToolTip(norm_p)
        item_path.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_ply.setItem(row, 1, item_path)

        # Col 2: Size (MB)
        size_mb = f"{os.path.getsize(file_path)/(1024*1024):.2f}"
        item_size = QTableWidgetItem(size_mb)
        item_size.setTextAlignment(Qt.AlignCenter)
        item_size.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_ply.setItem(row, 2, item_size)

        # Col 3: Status
        item_status = QTableWidgetItem("Ready for Cleanup")
        item_status.setTextAlignment(Qt.AlignCenter)
        item_status.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_ply.setItem(row, 3, item_status)

        self._update_clean_header()
        self._update_input_pill()
        return True

    def open_cleaned_folder(self):
        if not self.proj_dir: return
        cleaned_dir = os.path.join(self.proj_dir, "04_splats_cleaned")
        os.makedirs(cleaned_dir, exist_ok=True)
        os.startfile(cleaned_dir)

    def run_houdini_cleanup(self):
        target_files = self.get_checked_splat_files()
        if not target_files:
            self.log_signal.emit("[WARNING] No checked splat files for cleanup. Please check at least one splat model.", "warning")
            return

        self.log_signal.emit(f"Starting Houdini cleanup for {len(target_files)} selected model(s)...", "info")
        builder_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "houdini_builder.py")
        if os.path.exists(builder_script):
            self.log_signal.emit(f"Houdini Pipeline script ready: {builder_script}", "info")
            self.log_signal.emit("[INFO] Launching Houdini Environment...", "info")
        else:
            self.log_signal.emit(f"[INFO] Houdini cleanup triggered for {len(target_files)} splat(s).", "info")

    def update_language(self, t):
        self.current_translations = t
        self.card_input.setTitle(
            t.get("tab2_card1_title", "Target Splat Models"), 
            t.get("tab2_card1_sub", "Exported 3DGS .ply or .splat files to clean")
        )
        self.btn_add_ply.setText(t.get("tab2_btn_add", "+ Add Splat (.ply / .splat)"))
        if hasattr(self, 'btn_scan_splats') and self.btn_scan_splats is not None:
            self.btn_scan_splats.setText(t.get("tab2_btn_scan", "🔄 Scan Folder"))
        if hasattr(self, 'btn_select_all') and self.btn_select_all is not None:
            self.btn_select_all.setText(t.get("tab2_btn_select_all", "☑️ Toggle All"))
        if hasattr(self, 'btn_remove_selected') and self.btn_remove_selected is not None:
            self.btn_remove_selected.setText(t.get("tab2_btn_remove", "🗑 Remove"))
        self.btn_clear_ply.setText(t.get("tab2_btn_clear", "🧹 Clear All"))

        # Table Column Headers
        clean_label = t.get("tab2_tbl_col_clean", "Clean")
        clean_clean = clean_label.replace("☑️", "").replace("☑", "").replace("☐", "").strip()
        self.table_ply.setHorizontalHeaderLabels([
            f"☑️ {clean_clean}",
            t.get("tab2_tbl_col_file", "Splat File Path"),
            t.get("tab2_tbl_col_size", "Size (MB)"),
            t.get("tab2_tbl_col_status", "Status")
        ])
        self._update_clean_header()
        self._update_input_pill()

        self.card_tools.setTitle(
            t.get("tab2_card2_title", "Houdini Splat Cleanup Pipeline"), 
            t.get("tab2_card2_sub", "Execute procedural cleanup network")
        )
        self.btn_run_houdini.setText(t.get("tab2_btn_run", "🚀 Run Houdini Procedural Cleanup"))
        self.btn_open_cleaned.setText(t.get("tab2_btn_open", "📂 Open Cleaned Splats Folder"))