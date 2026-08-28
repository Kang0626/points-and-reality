# ui/tabs/capture_sections/section_launcher.py
import os
import subprocess
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QFileDialog, QStackedWidget, QWidget, QFrame, QApplication)
from PyQt5.QtCore import pyqtSignal, QTimer, QSettings, Qt
from ui.ui_components import ModernStepCard, StatusPill

class LauncherWidget(ModernStepCard):
    log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__(step_num="", title="Camera Alignment & Trainer Bridge", subtitle="Align cameras and launch 3DGS training engine")
        self.settings = QSettings("PointsAndReality", "3DGSController")
        self.proj_dir = ""
        self.init_ui()

    def init_ui(self):
        self.status_pill = StatusPill("Idle", "idle")
        self.add_header_action(self.status_pill)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # --------------------------------------------------
        # Part 1: RealityCapture Launch & Guide
        # --------------------------------------------------
        rc_card = QFrame()
        rc_card.setObjectName("rcCard")
        rc_card.setStyleSheet("QFrame#rcCard { background-color: #15181f; border: 1px solid #232732; border-radius: 6px; }")
        rc_layout = QHBoxLayout(rc_card)
        rc_layout.setContentsMargins(10, 6, 10, 6)
        rc_layout.setSpacing(10)

        self.btn_launch_rc = QPushButton("Launch RealityCapture")
        self.btn_launch_rc.setObjectName("PrimaryBtn")
        self.btn_launch_rc.setCursor(Qt.PointingHandCursor)
        self.btn_launch_rc.clicked.connect(self.launch_realitycapture)

        self.lbl_rc_desc = QLabel("Perform Camera Alignment & Export Dataset")
        self.lbl_rc_desc.setStyleSheet("color: #64748b; font-size: 11.5px;")

        self.btn_copy_frames_path = QPushButton("Copy Frames Path")
        self.btn_copy_frames_path.setCursor(Qt.PointingHandCursor)
        self.btn_copy_frames_path.clicked.connect(lambda: self.copy_to_clipboard("extracted_frames", "Extracted Frames", parent_dir="01_extracted_frames"))

        rc_layout.addWidget(self.btn_launch_rc)
        rc_layout.addWidget(self.lbl_rc_desc)
        rc_layout.addStretch()
        rc_layout.addWidget(self.btn_copy_frames_path)
        main_layout.addWidget(rc_card)

        # --------------------------------------------------
        # Part 2: Trainer Selection & Inspector
        # --------------------------------------------------
        trainer_card = QFrame()
        trainer_card.setObjectName("trainerCard")
        trainer_card.setStyleSheet("QFrame#trainerCard { background-color: #15181f; border: 1px solid #232732; border-radius: 6px; }")
        trainer_card_layout = QVBoxLayout(trainer_card)
        trainer_card_layout.setContentsMargins(10, 8, 10, 8)
        trainer_card_layout.setSpacing(8)

        # Trainer selector top row
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.lbl_target = QLabel("Target Trainer:")
        self.lbl_target.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        
        self.combo_trainer = QComboBox()
        self.combo_trainer.addItems(["Postshot (Jawset)", "Lichtfeld Studio"])
        self.combo_trainer.setCurrentText(self.settings.value("selected_trainer", "Postshot (Jawset)"))
        self.combo_trainer.currentTextChanged.connect(self.on_trainer_changed)
        self.combo_trainer.setMinimumWidth(180)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_status)

        top_row.addWidget(self.lbl_target)
        top_row.addWidget(self.combo_trainer)
        top_row.addStretch()
        top_row.addWidget(self.btn_refresh)
        trainer_card_layout.addLayout(top_row)

        # Dynamic Stacked Inspector
        self.stack = QStackedWidget()
        self.stack.setObjectName("trainerStack")
        self.stack.setStyleSheet("QStackedWidget#trainerStack { background-color: #111318; border: 1px solid #1e222c; border-radius: 4px; }")

        # --- 1) Postshot Widget ---
        ps_widget = QWidget()
        ps_layout = QVBoxLayout(ps_widget)
        ps_layout.setContentsMargins(10, 8, 10, 8)
        ps_layout.setSpacing(6)

        ps_guide = QLabel("<b>[ Postshot Mode ]</b> Export <b>XMP Metadata</b> or ABC/CSV from RealityCapture to the Alignment folder.")
        ps_guide.setStyleSheet("color: #f59e0b; font-size: 11px;")

        ps_actions = QHBoxLayout()
        self.btn_copy_ps_align = QPushButton("Copy Alignment Path")
        self.btn_copy_ps_align.setCursor(Qt.PointingHandCursor)
        self.btn_copy_ps_align.clicked.connect(lambda: self.copy_to_clipboard("", "Alignment Folder"))
        
        self.lbl_status_ps = QLabel("Waiting for Project...")
        self.lbl_status_ps.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 11px;")

        self.btn_open_align = QPushButton("Open Alignment Folder")
        self.btn_open_align.setCursor(Qt.PointingHandCursor)
        self.btn_open_align.clicked.connect(lambda: self.open_subfolder(""))

        ps_actions.addWidget(self.btn_copy_ps_align)
        ps_actions.addSpacing(10)
        ps_actions.addWidget(QLabel("Status:"))
        ps_actions.addWidget(self.lbl_status_ps)
        ps_actions.addStretch()
        ps_actions.addWidget(self.btn_open_align)

        ps_layout.addWidget(ps_guide)
        ps_layout.addLayout(ps_actions)
        self.stack.addWidget(ps_widget) # Index 0

        # --- 2) Lichtfeld Widget ---
        lf_widget = QWidget()
        lf_layout = QVBoxLayout(lf_widget)
        lf_layout.setContentsMargins(10, 8, 10, 8)
        lf_layout.setSpacing(6)

        lf_guide = QLabel("<b>[ Lichtfeld Mode ]</b> Export <b>COLMAP Registration (sparse/0)</b> and <b>Undistorted Images</b>.")
        lf_guide.setStyleSheet("color: #38bdf8; font-size: 11px;")

        lf_row1 = QHBoxLayout()
        btn_copy_sparse = QPushButton("Copy Sparse Path")
        btn_copy_sparse.setCursor(Qt.PointingHandCursor)
        btn_copy_sparse.clicked.connect(lambda: self.copy_to_clipboard("colmap/sparse/0", "Sparse Data"))
        self.lbl_status_lf_sparse = QLabel("Sparse: Waiting...")
        self.lbl_status_lf_sparse.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 11px;")
        btn_open_sparse = QPushButton("Open Sparse")
        btn_open_sparse.setCursor(Qt.PointingHandCursor)
        btn_open_sparse.clicked.connect(lambda: self.open_subfolder("colmap/sparse/0"))

        lf_row1.addWidget(btn_copy_sparse)
        lf_row1.addSpacing(10)
        lf_row1.addWidget(self.lbl_status_lf_sparse)
        lf_row1.addStretch()
        lf_row1.addWidget(btn_open_sparse)

        lf_row2 = QHBoxLayout()
        btn_copy_images = QPushButton("Copy Images Path")
        btn_copy_images.setCursor(Qt.PointingHandCursor)
        btn_copy_images.clicked.connect(lambda: self.copy_to_clipboard("colmap/images", "Images Data"))
        self.lbl_status_lf_images = QLabel("Images: Waiting...")
        self.lbl_status_lf_images.setStyleSheet("font-weight: 600; color: #cbd5e1; font-size: 11px;")
        btn_open_images = QPushButton("Open Images")
        btn_open_images.setCursor(Qt.PointingHandCursor)
        btn_open_images.clicked.connect(lambda: self.open_subfolder("colmap/images"))

        lf_row2.addWidget(btn_copy_images)
        lf_row2.addSpacing(10)
        lf_row2.addWidget(self.lbl_status_lf_images)
        lf_row2.addStretch()
        lf_row2.addWidget(btn_open_images)

        lf_layout.addWidget(lf_guide)
        lf_layout.addLayout(lf_row1)
        lf_layout.addLayout(lf_row2)
        self.stack.addWidget(lf_widget) # Index 1

        trainer_card_layout.addWidget(self.stack)

        # Launch Trainer Button Row
        bottom_launch_row = QHBoxLayout()
        self.btn_launch_trainer = QPushButton("Auto-Load & Launch Trainer")
        self.btn_launch_trainer.setObjectName("SuccessBtn")
        self.btn_launch_trainer.setCursor(Qt.PointingHandCursor)
        self.btn_launch_trainer.clicked.connect(self.launch_selected_trainer)

        self.btn_open_exports = QPushButton("Open Exports Folder")
        self.btn_open_exports.setCursor(Qt.PointingHandCursor)
        self.btn_open_exports.setToolTip("Open folder where trained 3DGS splats (.ply/.sog) are saved")
        self.btn_open_exports.clicked.connect(self.open_exports_folder)

        lbl_export_hint = QLabel("➔ Target: [ 03_splats_exports ]")
        lbl_export_hint.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")

        bottom_launch_row.addWidget(self.btn_launch_trainer)
        bottom_launch_row.addWidget(self.btn_open_exports)
        bottom_launch_row.addWidget(lbl_export_hint)
        bottom_launch_row.addStretch()
        trainer_card_layout.addLayout(bottom_launch_row)

        main_layout.addWidget(trainer_card)
        self.setContentLayout(main_layout)
        self._sync_stack_index()

    def set_proj_dir(self, directory):
        self.proj_dir = directory
        self.scaffold_folders()
        self.refresh_status()

    def on_trainer_changed(self, txt):
        self.settings.setValue("selected_trainer", txt)
        self._sync_stack_index()
        self.scaffold_folders()
        self.refresh_status()

    def _sync_stack_index(self):
        idx = 1 if "Lichtfeld" in self.combo_trainer.currentText() else 0
        self.stack.setCurrentIndex(idx)

    def scaffold_folders(self):
        if not self.proj_dir: return
        align_dir = os.path.join(self.proj_dir, "02_camera_alignment")
        if "Lichtfeld" in self.combo_trainer.currentText():
            os.makedirs(os.path.join(align_dir, "colmap", "sparse", "0"), exist_ok=True)
            os.makedirs(os.path.join(align_dir, "colmap", "images"), exist_ok=True)
        else:
            os.makedirs(align_dir, exist_ok=True)

    def refresh_status(self):
        if not hasattr(self, 'proj_dir') or not self.proj_dir:
            self.status_pill.set_status("Idle", "idle")
            return
        align_dir = os.path.join(self.proj_dir, "02_camera_alignment")
        if not os.path.exists(align_dir): return

        if self.stack.currentIndex() == 1:
            sparse_dir = os.path.join(align_dir, "colmap", "sparse", "0")
            images_dir = os.path.join(align_dir, "colmap", "images")
            
            h_cam = os.path.exists(os.path.join(sparse_dir, "cameras.bin")) or os.path.exists(os.path.join(sparse_dir, "cameras.txt"))
            h_img = os.path.exists(os.path.join(sparse_dir, "images.bin")) or os.path.exists(os.path.join(sparse_dir, "images.txt"))
            h_pts = os.path.exists(os.path.join(sparse_dir, "points3D.bin")) or os.path.exists(os.path.join(sparse_dir, "points3D.txt"))
            
            ready_sparse = h_cam and h_img and h_pts
            ready_img = os.path.exists(images_dir) and any(f.endswith(('.png', '.jpg', '.jpeg')) for f in os.listdir(images_dir))
            
            self.lbl_status_lf_sparse.setText("🟢 Ready (3/3 Meta Files)" if ready_sparse else "🔴 Missing (cameras/images/points3D)")
            self.lbl_status_lf_images.setText("🟢 Ready (Images Found)" if ready_img else "🔴 Missing (No Images)")
            
            if ready_sparse and ready_img:
                self.status_pill.set_status("Ready to Train", "success")
            else:
                self.status_pill.set_status("Need Alignment", "warning")
        else:
            has_meta = any(f.endswith(('.xmp', '.abc', '.csv')) for f in os.listdir(align_dir))
            if has_meta:
                self.lbl_status_ps.setText("🟢 Ready (Meta Found)")
                self.status_pill.set_status("Ready to Train", "success")
            else:
                self.lbl_status_ps.setText("🔴 Missing (XMP/ABC/CSV Meta)")
                self.status_pill.set_status("Need Alignment", "warning")

    def copy_to_clipboard(self, sub_path, name, parent_dir="02_camera_alignment"):
        if not self.proj_dir:
            self.log_signal.emit("[WARNING] Project directory not set.", "warning")
            return
        target_path = os.path.normpath(os.path.join(self.proj_dir, parent_dir, sub_path))
        QApplication.clipboard().setText(target_path)
        self.log_signal.emit(f"📋 Copied {name} path to clipboard: {target_path}", "info")

    def open_subfolder(self, sub_path, parent_dir="02_camera_alignment"):
        if not self.proj_dir: return
        target_path = os.path.normpath(os.path.join(self.proj_dir, parent_dir, sub_path))
        if os.path.exists(target_path):
            os.startfile(target_path)
        else:
            self.log_signal.emit(f"[ERROR] Directory not found: {target_path}", "error")

    def _debounce_btn(self):
        btn = self.sender()
        if hasattr(self, 'sender') and btn:
            btn.setEnabled(False)
            QTimer.singleShot(2000, lambda: btn.setEnabled(True))

    def _launch_app(self, key, paths, dialog_title):
        self._debounce_btn()
        saved = self.settings.value(key, "")
        if saved and os.path.exists(saved):
            subprocess.Popen([saved])
            self.log_signal.emit(f"Launched from saved path: {saved}", "info")
            return

        for p in paths:
            if os.path.exists(p):
                subprocess.Popen([p])
                self.log_signal.emit("Launched successfully.", "info")
                return

        self.log_signal.emit(f"[WARNING] Executable not found. Please locate it manually.", "warning")
        file_path, _ = QFileDialog.getOpenFileName(self, dialog_title, "C:\\", "Executable (*.exe)")
        if file_path:
            self.settings.setValue(key, file_path)
            subprocess.Popen([file_path])
            self.log_signal.emit(f"Path saved & Launched: {file_path}", "success")

    def launch_realitycapture(self):
        paths = [r"C:\Program Files\Capturing Reality\RealityCapture\RealityCapture.exe"]
        epic_dir = r"C:\Program Files\Epic Games"
        if os.path.exists(epic_dir):
            for d in os.listdir(epic_dir):
                if "reality" in d.lower():
                    for exe in ["RealityCapture.exe", "RealityScan.exe"]:
                        p = os.path.join(epic_dir, d, exe)
                        if os.path.exists(p): paths.insert(0, p)
        self._launch_app("path_realitycapture", paths, "Locate RealityCapture.exe")

    def launch_selected_trainer(self):
        if "Postshot" in self.combo_trainer.currentText():
            paths = [r"C:\Program Files\Jawset Postshot\bin\postshot.exe", 
                     os.path.expandvars(r"%LocalAppData%\Programs\Postshot\postshot.exe"),
                     r"C:\Program Files\Postshot\postshot.exe"]
            self._launch_app("path_postshot", paths, "Locate postshot.exe")
        else:
            paths = [r"D:\LichtFeld-Studio\bin\LichtFeld-Studio.exe",
                     r"D:\LichtFeld-Studio\LichtFeld-Studio.exe",
                     r"C:\Program Files\Lichtfeld\Lichtfeld.exe", 
                     os.path.expandvars(r"%LocalAppData%\Programs\Lichtfeld\Lichtfeld.exe")]
            self._launch_app("path_lichtfeld", paths, "Locate Lichtfeld-Studio.exe")

    def open_exports_folder(self):
        if not self.proj_dir:
            self.log_signal.emit("[ERROR] Project directory not set.", "error")
            return
        export_dir = os.path.join(self.proj_dir, "03_splats_exports")
        os.makedirs(export_dir, exist_ok=True)
        os.startfile(export_dir)

    def update_language(self, t):
        self.setTitle(t.get("group_launcher", "Camera Alignment & Trainer Bridge"), t.get("sub_launcher", "Align camera positions and bridge to 3DGS training engines"))
        self.btn_launch_rc.setText(t.get("btn_launch_rc", "Launch RealityCapture"))
        self.lbl_rc_desc.setText(t.get("lbl_rc_desc", "Perform Camera Alignment & Export Dataset"))
        self.btn_copy_frames_path.setText(t.get("btn_copy_frames_path", "Copy Frames Path"))
        self.lbl_target.setText(t.get("lbl_target", "Target Trainer:"))
        self.btn_refresh.setText(t.get("btn_refresh", "Refresh"))
        self.btn_launch_trainer.setText(t.get("btn_launch_trainer", "Auto-Load & Launch Trainer"))
        if hasattr(self, 'btn_open_exports') and self.btn_open_exports is not None:
            self.btn_open_exports.setText(t.get("btn_open_exports", "Open Exports (03_splats_exports)"))

    def get_preset_data(self):
        return {"trainer": self.combo_trainer.currentIndex()}

    def set_preset_data(self, data):
        if "trainer" in data: self.combo_trainer.setCurrentIndex(data["trainer"])