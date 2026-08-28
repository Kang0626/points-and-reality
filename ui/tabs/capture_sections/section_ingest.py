# ui/tabs/capture_sections/section_ingest.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFileDialog, QTableWidgetItem, QComboBox, 
                             QProgressBar, QCheckBox, QHeaderView, QAbstractItemView, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from ui.ui_components import ModernStepCard, DragDropTableWidget, ElideLeftDelegate, StatusPill
from utils import ExtractorThread, get_video_metadata

STYLE_PRESET_ACTIVE = (
    "QPushButton { "
    "background-color: #1e3a5f; color: #38bdf8; "
    "border: 1px solid #0284c7; border-radius: 4px; "
    "padding: 3px 8px; font-size: 10px; font-weight: bold; "
    "} "
    "QPushButton:hover { background-color: #0284c7; color: #ffffff; border-color: #38bdf8; }"
)

STYLE_PRESET_INACTIVE = (
    "QPushButton { "
    "background-color: #24272f; color: #cbd5e1; "
    "border: 1px solid #333842; border-radius: 4px; "
    "padding: 3px 8px; font-size: 10px; "
    "} "
    "QPushButton:hover { background-color: #2d323c; color: #ffffff; border-color: #475569; }"
)

class IngestWidget(ModernStepCard):
    log_signal = pyqtSignal(str, str)
    request_max_toggle = pyqtSignal(bool)

    def __init__(self):
        super().__init__(step_num="", title="Video Ingest & Frame Extractor", subtitle="Drop video files and extract high-quality frames for 3DGS")
        self.proj_dir = ""
        self.all_videos_checked = True
        self.lut_path = ""
        self.init_ui()

    def init_ui(self):
        self.status_pill = StatusPill("0 Videos", "idle")
        self.add_header_action(self.status_pill)

        vlayout = QVBoxLayout()
        vlayout.setSpacing(8)

        # ----------------------------------------------------
        # 1. Quick Presets & Video Management Toolbar
        # ----------------------------------------------------
        hlayout_top = QHBoxLayout()
        hlayout_top.setSpacing(6)
        
        self.btn_add_video = QPushButton("🎬 + Add Videos")
        self.btn_add_video.setObjectName("PrimaryBtn")
        self.btn_add_video.setCursor(Qt.PointingHandCursor)
        self.btn_add_video.clicked.connect(self.add_videos)
        self.btn_add_videos = self.btn_add_video
        
        self.btn_remove_selected = QPushButton("✕ Remove Selected")
        self.btn_remove_selected.setCursor(Qt.PointingHandCursor)
        self.btn_remove_selected.clicked.connect(self.remove_selected_videos)
        self.btn_remove_video = self.btn_remove_selected
        
        self.btn_remove_all = QPushButton("🗑 Clear All")
        self.btn_remove_all.setCursor(Qt.PointingHandCursor)
        self.btn_remove_all.clicked.connect(self.clear_videos)
        self.btn_clear_videos = self.btn_remove_all
        
        hlayout_top.addWidget(self.btn_add_video)
        hlayout_top.addWidget(self.btn_remove_selected)
        hlayout_top.addWidget(self.btn_remove_all)
        hlayout_top.addSpacing(10)

        # Quick Preset Chips
        lbl_presets_title = QLabel("⚡ Quick Presets:")
        lbl_presets_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
        hlayout_top.addWidget(lbl_presets_title)

        self.chip_balanced = QPushButton("🎯 Standard (4 FPS / PNG)")
        self.chip_balanced.setToolTip("Standard balanced 3DGS dataset (4 FPS, 8-bit PNG)")
        self.chip_balanced.setStyleSheet(STYLE_PRESET_ACTIVE)
        self.chip_balanced.clicked.connect(lambda: self.apply_quick_preset(4, "8-bit PNG (Lossless - Recommended)", "100% (Original)"))

        self.chip_fast = QPushButton("⚡ Fast (2 FPS / JPG)")
        self.chip_fast.setToolTip("Fast draft training (2 FPS, High-Quality JPG, 1080p)")
        self.chip_fast.setStyleSheet(STYLE_PRESET_INACTIVE)
        self.chip_fast.clicked.connect(lambda: self.apply_quick_preset(2, "JPG (High Quality - 98%)", "1080p Max Width"))

        self.chip_ultra = QPushButton("💎 Ultra (6 FPS / 16-bit)")
        self.chip_ultra.setToolTip("VFX High-Bitdepth (6 FPS, 16-bit PNG Lossless)")
        self.chip_ultra.setStyleSheet(STYLE_PRESET_INACTIVE)
        self.chip_ultra.clicked.connect(lambda: self.apply_quick_preset(6, "16-bit PNG (ProRes/Log)", "100% (Original)"))

        hlayout_top.addWidget(self.chip_balanced)
        hlayout_top.addWidget(self.chip_fast)
        hlayout_top.addWidget(self.chip_ultra)
        hlayout_top.addStretch()

        self.btn_max_videos = QPushButton("⛶")
        self.btn_max_videos.setToolTip("Expand / Minimize Table")
        self.btn_max_videos.setCheckable(True)
        self.btn_max_videos.setFixedWidth(30)
        self.btn_max_videos.clicked.connect(self.toggle_maximize)
        hlayout_top.addWidget(self.btn_max_videos)

        vlayout.addLayout(hlayout_top)

        # ----------------------------------------------------
        # 2. Drag & Drop Videos Table
        # ----------------------------------------------------
        self.table = DragDropTableWidget(0, 6)
        self.table.setItemDelegateForColumn(1, ElideLeftDelegate(self.table))
        self.table.setHorizontalHeaderLabels(["☑ All", "Video File Path", "Duration", "Resolution / Codec", "Est. Frames", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(130)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().sectionClicked.connect(self.toggle_all_videos)
        self.table.files_dropped.connect(self.handle_files_dropped)
        self.table.setStyleSheet("""
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
        vlayout.addWidget(self.table)

        # ----------------------------------------------------
        # 3. Extraction Parameters Frame
        # ----------------------------------------------------
        opt_frame = QFrame()
        opt_frame.setObjectName("optFrame")
        opt_frame.setStyleSheet("QFrame#optFrame { background-color: #141619; border: 1px solid #2d3139; border-radius: 6px; }")
        hlayout_opt = QHBoxLayout(opt_frame)
        hlayout_opt.setContentsMargins(8, 4, 8, 4)
        hlayout_opt.setSpacing(10)

        # FPS Rate
        self.lbl_fps = QLabel("FPS Rate:")
        self.lbl_fps.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.input_fps = QLineEdit("4")
        self.input_fps.setFixedWidth(40)
        self.input_fps.setAlignment(Qt.AlignCenter)
        self.input_fps.textChanged.connect(self._on_params_changed)

        # Format / Bit Depth
        self.lbl_bitdepth = QLabel("Format:")
        self.lbl_bitdepth.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.combo_bitdepth = QComboBox()
        self.combo_bitdepth.addItems([
            "8-bit PNG (Lossless - Recommended)",
            "JPG (High Quality - 98%)",
            "16-bit PNG (ProRes/Log)",
            "16-bit EXR (VFX / Linear)",
            "10-bit WebP"
        ])
        self.combo_bitdepth.setCurrentText("8-bit PNG (Lossless - Recommended)")
        self.combo_bitdepth.currentIndexChanged.connect(self._on_params_changed)

        # Resolution Scaling
        self.lbl_scale = QLabel("Resolution Scale:")
        self.lbl_scale.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.combo_scale = QComboBox()
        self.combo_scale.addItems([
            "100% (Original)",
            "50% (Half Scale)",
            "1080p Max Width",
            "2K Max Width"
        ])
        self.combo_scale.currentIndexChanged.connect(self._on_params_changed)

        # Custom LUT File (Optional)
        self.btn_lut = QPushButton("🎨 + LUT (.cube)")
        self.btn_lut.setToolTip("Select custom 3D LUT (.cube) file to apply color conversion during extraction")
        self.btn_lut.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.btn_lut.clicked.connect(self.select_lut_file)

        hlayout_opt.addWidget(self.lbl_fps)
        hlayout_opt.addWidget(self.input_fps)
        hlayout_opt.addSpacing(10)
        hlayout_opt.addWidget(self.lbl_bitdepth)
        hlayout_opt.addWidget(self.combo_bitdepth)
        hlayout_opt.addSpacing(10)
        hlayout_opt.addWidget(self.lbl_scale)
        hlayout_opt.addWidget(self.combo_scale)
        hlayout_opt.addSpacing(10)
        hlayout_opt.addWidget(self.btn_lut)
        hlayout_opt.addStretch()

        # Total Est. Frames Summary Label
        self.lbl_total_summary = QLabel("Total Est: 0 frames")
        self.lbl_total_summary.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        hlayout_opt.addWidget(self.lbl_total_summary)

        vlayout.addWidget(opt_frame)

        # ----------------------------------------------------
        # 4. Run Extraction Action Bar
        # ----------------------------------------------------
        hlayout_run = QHBoxLayout()
        hlayout_run.setSpacing(8)

        self.btn_run_extract = QPushButton("⚡ Run Frame Extraction")
        self.btn_run_extract.setObjectName("PrimaryBtn")
        self.btn_run_extract.setCursor(Qt.PointingHandCursor)
        self.btn_run_extract.clicked.connect(self.run_extraction)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(28)

        self.btn_open_extracted = QPushButton("📂 Open Extracted Frames")
        self.btn_open_extracted.setCursor(Qt.PointingHandCursor)
        self.btn_open_extracted.clicked.connect(self.open_extracted_folder)
        
        hlayout_run.addWidget(self.btn_run_extract)
        hlayout_run.addWidget(self.progress_bar, 1)
        hlayout_run.addWidget(self.btn_open_extracted)
        vlayout.addLayout(hlayout_run)

        self.setContentLayout(vlayout)

    def _on_params_changed(self):
        self.update_estimated_frames()
        self._update_preset_chip_styles()

    def _update_preset_chip_styles(self):
        if not hasattr(self, 'chip_balanced') or not hasattr(self, 'chip_fast') or not hasattr(self, 'chip_ultra'):
            return
        fps = self.input_fps.text().strip()
        fmt = self.combo_bitdepth.currentText()
        scale = self.combo_scale.currentText()

        is_balanced = (fps == "4" and "8-bit PNG" in fmt and "100%" in scale)
        is_fast = (fps == "2" and "JPG" in fmt and "1080p" in scale)
        is_ultra = (fps == "6" and "16-bit PNG" in fmt and "100%" in scale)

        self.chip_balanced.setStyleSheet(STYLE_PRESET_ACTIVE if is_balanced else STYLE_PRESET_INACTIVE)
        self.chip_fast.setStyleSheet(STYLE_PRESET_ACTIVE if is_fast else STYLE_PRESET_INACTIVE)
        self.chip_ultra.setStyleSheet(STYLE_PRESET_ACTIVE if is_ultra else STYLE_PRESET_INACTIVE)

    def apply_quick_preset(self, fps, fmt, scale):
        self.input_fps.blockSignals(True)
        self.combo_bitdepth.blockSignals(True)
        self.combo_scale.blockSignals(True)

        self.input_fps.setText(str(fps))
        self.combo_bitdepth.setCurrentText(fmt)
        self.combo_scale.setCurrentText(scale)

        self.input_fps.blockSignals(False)
        self.combo_bitdepth.blockSignals(False)
        self.combo_scale.blockSignals(False)

        self.update_estimated_frames()
        self._update_preset_chip_styles()
        self.log_signal.emit(f"Applied preset: {fps} FPS, {fmt}, Scale={scale}", "info")

    def select_lut_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select 3D LUT File", self.proj_dir, "LUT Files (*.cube *.3dl)")
        if file_path:
            self.lut_path = file_path
            self.btn_lut.setText(f"🎨 LUT: {os.path.basename(file_path)}")
            self.btn_lut.setStyleSheet("background-color: #065f46; color: #34d399; border: 1px solid #10b981; font-size: 10px; padding: 3px 8px;")
            self.log_signal.emit(f"Custom LUT selected: {file_path}", "info")
        else:
            self.lut_path = ""
            self.btn_lut.setText("🎨 + LUT (.cube)")
            self.btn_lut.setStyleSheet("font-size: 10px; padding: 3px 8px;")

    def _debounce_btn(self):
        btn = self.sender()
        if btn:
            btn.setEnabled(False)
            QTimer.singleShot(1000, lambda: btn.setEnabled(True))

    def set_proj_dir(self, directory):
        self.proj_dir = directory
        raw_dir = os.path.join(directory, "00_raw_footage")
        if os.path.exists(raw_dir):
            valid_ext = ('.mp4', '.mov', '.mkv', '.avi', '.m4v')
            files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.lower().endswith(valid_ext)]
            if files:
                self.clear_videos()
                for f in files: self.add_video_row(f)
                self.log_signal.emit(f"Auto-loaded {len(files)} video(s) from project.", "info")

    def toggle_maximize(self):
        is_max = self.btn_max_videos.isChecked()
        self.table.setMinimumHeight(320 if is_max else 130)
        self.request_max_toggle.emit(is_max)

    def toggle_all_videos(self, index):
        if index == 0:
            self.all_videos_checked = not getattr(self, 'all_videos_checked', True)
            chk_label = "☑ All" if self.all_videos_checked else "☐ All"
            item = self.table.horizontalHeaderItem(0)
            if item: item.setText(chk_label)
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 0)
                if widget and widget.layout():
                    widget.layout().itemAt(0).widget().setChecked(self.all_videos_checked)
            self.update_estimated_frames()

    def handle_files_dropped(self, file_paths):
        valid_ext = ('.mp4', '.mov', '.mkv', '.avi', '.m4v')
        added = 0
        for path in file_paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.lower().endswith(valid_ext):
                            if self.add_video_row(os.path.join(root, f)):
                                added += 1
            elif path.lower().endswith(valid_ext):
                if self.add_video_row(path):
                    added += 1
        if added > 0:
            self.log_signal.emit(f"Added {added} video(s) via Drag & Drop.", "info")

    def add_videos(self):
        self._debounce_btn()
        start_dir = os.path.join(self.proj_dir, "00_raw_footage") if self.proj_dir else ""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Video Files", start_dir, "Video Files (*.mov *.mp4 *.mkv *.avi *.m4v)")
        if files:
            count = sum(1 for f in files if self.add_video_row(f))
            self.log_signal.emit(f"Added {count} video(s)." if count else "No new videos added.", "info")

    def add_video_row(self, file_path):
        norm_path = os.path.normcase(os.path.abspath(file_path))
        for row in range(self.table.rowCount()):
            if norm_path == os.path.normcase(os.path.abspath(self.table.item(row, 1).text())):
                return False
        
        # Real ffprobe metadata extraction
        meta = get_video_metadata(file_path)
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_box = QCheckBox()
        chk_box.setChecked(self.all_videos_checked)
        chk_box.stateChanged.connect(self.update_estimated_frames)
        chk_layout.addWidget(chk_box)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 0, chk_widget)
        
        item_path = QTableWidgetItem(os.path.normpath(file_path))
        item_path.setToolTip(os.path.normpath(file_path))
        
        self.table.setItem(row, 1, item_path)
        
        item_dur = QTableWidgetItem(meta["duration_str"])
        item_dur.setData(Qt.UserRole, meta["duration_sec"])
        self.table.setItem(row, 2, item_dur)
        
        res_codec_str = f"{meta['resolution']} • {meta['codec']}"
        self.table.setItem(row, 3, QTableWidgetItem(res_codec_str))
        
        try:
            fps_val = float(self.input_fps.text().strip())
        except Exception:
            fps_val = 4.0
        est_frames = int(meta["duration_sec"] * fps_val)
        est_str = f"~{est_frames} frames" if est_frames > 0 else "Ready"
        self.table.setItem(row, 4, QTableWidgetItem(est_str))
        
        self.table.setItem(row, 5, QTableWidgetItem("Queued"))
        
        count = self.table.rowCount()
        self.status_pill.set_status(f"{count} Video{'s' if count>1 else ''}", "ready")
        self.update_estimated_frames()
        return True

    def update_estimated_frames(self):
        try:
            fps_val = float(self.input_fps.text().strip())
        except Exception:
            fps_val = 4.0

        total_est = 0
        selected_count = 0
        for row in range(self.table.rowCount()):
            chk_widget = self.table.cellWidget(row, 0)
            is_checked = chk_widget and chk_widget.layout().itemAt(0).widget().isChecked()
            dur_item = self.table.item(row, 2)
            dur_sec = dur_item.data(Qt.UserRole) if dur_item else 0
            if dur_sec is None: dur_sec = 0.0
            
            est = int(float(dur_sec) * fps_val)
            if self.table.item(row, 4):
                self.table.item(row, 4).setText(f"~{est} frames" if est > 0 else "Ready")
            
            if is_checked:
                selected_count += 1
                total_est += est

        self.lbl_total_summary.setText(f"Selected: {selected_count} / Est: ~{total_est} frames")

    def remove_selected_videos(self):
        for i in range(self.table.rowCount() - 1, -1, -1):
            widget = self.table.cellWidget(i, 0)
            if widget and widget.layout().itemAt(0).widget().isChecked():
                self.table.removeRow(i)
        count = self.table.rowCount()
        self.status_pill.set_status(f"{count} Video{'s' if count>1 else ''}" if count else "0 Videos", "ready" if count else "idle")
        self.update_estimated_frames()

    def clear_videos(self):
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.status_pill.set_status("0 Videos", "idle")
        self.update_estimated_frames()

    def open_extracted_folder(self):
        self._debounce_btn()
        if not self.proj_dir:
            self.log_signal.emit("[ERROR] Project directory not set.", "error")
            return
        extracted_dir = os.path.join(self.proj_dir, "01_extracted_frames")
        os.makedirs(extracted_dir, exist_ok=True)
        os.startfile(extracted_dir)

    def run_extraction(self):
        if not self.proj_dir:
            self.log_signal.emit("[ERROR] Please set a valid Project Directory first.", "error")
            return
        tasks = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                tasks.append((i, self.table.item(i, 1).text()))
        if not tasks:
            self.log_signal.emit("[WARNING] No videos selected for extraction.", "warning")
            return

        target_dir = os.path.join(self.proj_dir, "01_extracted_frames")
        fps = self.input_fps.text().strip()
        format_type = self.combo_bitdepth.currentText()
        scale_opt = self.combo_scale.currentText()
        
        self.btn_run_extract.setEnabled(False)
        self.status_pill.set_status("Extracting...", "running")
        
        self.extractor = ExtractorThread(tasks, fps, format_type, scale_opt, self.lut_path, target_dir)
        self.extractor.progress_update.connect(lambda v, m: (self.progress_bar.setValue(v), self.log_signal.emit(m, "info") if v < 100 else None))
        self.extractor.file_status.connect(lambda r, s: self.table.setItem(r, 5, QTableWidgetItem(s)))
        self.extractor.finished_extraction.connect(self._extraction_done)
        self.extractor.start()

    def _extraction_done(self, target_dir, success):
        self.btn_run_extract.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.status_pill.set_status("Frames Extracted", "success")
            self.log_signal.emit("[SUCCESS] Batch frame extraction completed.", "success")
        else:
            self.status_pill.set_status("Extraction Failed", "error")
            self.log_signal.emit("[ERROR] Batch extraction finished with errors.", "error")

    def update_language(self, t):
        self.setTitle(t.get("group_ingest", "Video Ingest & Frame Extractor"), t.get("sub_ingest", "Drop video files and extract frames"))
        self.btn_add_video.setText(t.get("btn_add_videos", "🎬 + Add Videos"))
        self.btn_remove_selected.setText(t.get("btn_remove_selected", "✕ Remove Selected"))
        self.btn_remove_all.setText(t.get("btn_remove_all", "🗑 Clear All"))
        self.lbl_fps.setText(t.get("lbl_framerate", "FPS Rate:"))
        self.lbl_bitdepth.setText(t.get("lbl_bitdepth", "Format:"))
        self.lbl_scale.setText(t.get("lbl_scale", "Resolution Scale:"))
        self.btn_run_extract.setText(t.get("btn_run_extract", "⚡ Run Frame Extraction"))
        self.btn_open_extracted.setText(t.get("btn_open_extracted", "📂 Open Frames"))
        self.table.setHorizontalHeaderLabels([
            t.get("tbl_col_check", "☑ All"),
            t.get("tbl_col_video", "Video File Path"),
            t.get("tbl_col_duration", "Duration"),
            t.get("tbl_col_res_codec", "Resolution / Codec"),
            t.get("tbl_col_est", "Est. Frames"),
            t.get("tbl_col_status", "Status")
        ])

    def get_preset_data(self):
        return {
            "fps": self.input_fps.text().strip(),
            "format": self.combo_bitdepth.currentText(),
            "scale": self.combo_scale.currentText()
        }

    def set_preset_data(self, data):
        if "fps" in data: self.input_fps.setText(str(data["fps"]))
        if "format" in data: self.combo_bitdepth.setCurrentText(data["format"])
        if "scale" in data: self.combo_scale.setCurrentText(data["scale"])