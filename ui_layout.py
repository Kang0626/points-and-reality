# ui_layout.py
import os
import subprocess
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QGroupBox, QLineEdit, QPushButton, QFileDialog, 
                             QTableWidget, QTableWidgetItem, QComboBox, QProgressBar, 
                             QLabel, QTextBrowser, QHeaderView, QAbstractItemView, 
                             QInputDialog, QMessageBox, QCheckBox, QFrame, QSplitter, QSizePolicy)
from config import PROJECT_SUBFOLDERS, DARK_THEME_CSS
from utils import create_project_structure, ExtractorThread, FolderWatcherThread

# ---------------------------------------------------------
# --- 다국어 번역 사전 (UI I18N Dictionary) ---
# ---------------------------------------------------------
TRANSLATIONS = {
    "EN": {
        "tab_capture": "Capture & Ingest",
        "tab_cleanup": "Splat Cleanup",
        "tab_webgl": "WebGL Build",
        "group_project": "Project Directory Configuration",
        "lbl_project_dir": "Project Directory:",
        "placeholder_project": "Select or create project directory...",
        "btn_new_proj": "+ New Project",
        "btn_browse_proj": "Browse...",
        "btn_open_proj": "Open Folder",
        "group_ingest": "Multi-Video Source & Frame Extractor (FFmpeg)",
        "btn_add_videos": "+ Add Videos",
        "btn_remove_selected": "- Remove Selected",
        "btn_remove_all": "- Remove All",
        "btn_max": "⛶ Maximize",
        "btn_restore": "🗗 Restore",
        "tbl_col_video": "Video File Path",
        "tbl_col_duration": "Duration",
        "tbl_col_codec": "Codec",
        "tbl_col_status": "Status",
        "lbl_framerate": "Frame Rate:",
        "lbl_bitdepth": "   Bit Depth:",
        "lbl_colorspace": " Color Space:",
        "btn_run_extract": "⚡ Run Batch Frame Extraction",
        "btn_open_extracted": "📂 Open Folder",
        "group_launcher": "Alignment & 3DGS Training Launcher",
        "lbl_step1": "1. Camera Alignment:",
        "lbl_step2": "2. 3DGS Trainer:",
        "btn_launch_trainer": "🚀 Launch Trainer",
        "group_watcher": "Export Folder Watcher (Auto Pipeline)",
        "btn_start_watcher": "Start Auto Watcher",
        "btn_stop_watcher": "Stop Auto Watcher",
        "btn_send_cleanup": "Send to Cleanup ➔",
        "tbl_col_detected": "Detected File / Folder Path",
        "tbl_col_size": "Size (MB)",
        "tbl_col_time": "Time",
        "log_title": "Backend Status / Info",
        "opt_pass_log": "None (Pass-through Log)",
        "opt_rec709": "Apply Ingest Rec.709 LUT"
    },
    "KO": {
        "tab_capture": "캡처 및 영상 인제스트",
        "tab_cleanup": "스플랫 클린업",
        "tab_webgl": "WebGL 빌드",
        "group_project": "프로젝트 디렉토리 설정",
        "lbl_project_dir": "프로젝트 경로:",
        "placeholder_project": "프로젝트 폴더를 선택하거나 생성하세요...",
        "btn_new_proj": "+ 새 프로젝트",
        "btn_browse_proj": "찾아보기...",
        "btn_open_proj": "폴더 열기",
        "group_ingest": "멀티 비디오 소스 및 프레임 추출 (FFmpeg)",
        "btn_add_videos": "+ 동영상 추가",
        "btn_remove_selected": "- 선택 항목 삭제",
        "btn_remove_all": "- 전체 삭제",
        "btn_max": "⛶ 최대화",
        "btn_restore": "🗗 복원",
        "tbl_col_video": "동영상 파일 경로",
        "tbl_col_duration": "길이",
        "tbl_col_codec": "코덱",
        "tbl_col_status": "상태",
        "lbl_framerate": "추출 프레임률:",
        "lbl_bitdepth": "   비트 심도:",
        "lbl_colorspace": " 색공간 설정:",
        "btn_run_extract": "⚡ 일괄 프레임 추출 실행",
        "btn_open_extracted": "📂 추출 폴더 열기",
        "group_launcher": "카메라 얼라인먼트 및 3DGS 트레이닝 런처",
        "lbl_step1": "1. 카메라 얼라인먼트:",
        "lbl_step2": "2. 3DGS 트레이너:",
        "btn_launch_trainer": "🚀 트레이너 실행",
        "group_watcher": "익스포트 폴더 자동 감시 (Auto Pipeline)",
        "btn_start_watcher": "자동 감시 시작",
        "btn_stop_watcher": "자동 감시 중지",
        "btn_send_cleanup": "클린업으로 전송 ➔",
        "tbl_col_detected": "감지된 파일 / 폴더 경로",
        "tbl_col_size": "용량 (MB)",
        "tbl_col_time": "시간",
        "log_title": "백엔드 상태 / 정보 로그",
        "opt_pass_log": "적용 안 함 (Log 원본 유지)",
        "opt_rec709": "인제스트용 Rec.709 LUT 적용"
    }
}

# ---------------------------------------------------------
# --- 커스텀 위젯: 자동 하단 스크롤을 지원하는 콘솔 브라우저 ---
# ---------------------------------------------------------
class AutoScrollTextBrowser(QTextBrowser):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 창 크기 변경 시 항상 최신(맨 아래) 메시지로 자동 스크롤
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


# ---------------------------------------------------------
# --- 커스텀 위젯: 접고 펼칠 수 있는 아코디언 UI 섹션 ---
# ---------------------------------------------------------
class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 4)
        self.layout.setSpacing(0)

        self.is_expanded = True
        self.title_text = title
        
        self.toggle_button = QPushButton(f"▼  {self.title_text}")
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet("""
            #contentArea {
                border: 1px solid #444;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #222222;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.content_area)
        
        self.toggle_button.clicked.connect(self.toggle)
        self.update_toggle_style()

    def setTitle(self, title):
        self.title_text = title
        icon = "▼" if self.is_expanded else "▶"
        self.toggle_button.setText(f"{icon}  {self.title_text}")

    def update_toggle_style(self):
        if self.is_expanded:
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 7px 15px;
                    background-color: #333333;
                    color: #3498db;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #444;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                }
                QPushButton:hover { background-color: #3d3d3d; }
            """)
        else:
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 7px 15px;
                    background-color: #333333;
                    color: #3498db;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #444;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #3d3d3d; }
            """)

    def set_expanded(self, state: bool):
        self.is_expanded = state
        self.content_area.setVisible(self.is_expanded)
        icon = "▼" if self.is_expanded else "▶"
        self.toggle_button.setText(f"{icon}  {self.title_text}")
        self.update_toggle_style()

    def toggle(self):
        self.set_expanded(not self.is_expanded)

    def setContentLayout(self, layout):
        self.content_layout.addLayout(layout)


class PointsAndRealityController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Points & Reality 3DGS Controller - v2.222")
        self.resize(1200, 850)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_THEME_CSS)
        
        self.settings = QSettings("PointsAndReality", "3DGSController")
        self.current_lang = self.settings.value("ui_language", "EN")
        
        self.init_ui()
        self.apply_language(self.current_lang)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(4)

        # 상단 헤더: 타이틀 및 우측 언어 토글 버튼
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.lbl_main_title = QLabel("Points & Reality 3DGS Controller - v2.222")
        self.lbl_main_title.setAlignment(Qt.AlignCenter)
        self.lbl_main_title.setStyleSheet("color: #3498db; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.lbl_main_title)
        
        header_layout.addStretch()
        
        self.btn_lang = QPushButton("🌐 Language: EN")
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #3498db;
                color: #3498db;
            }
        """)
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        
        main_layout.addLayout(header_layout)

        # 메인 상하 분할 스플리터
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle:vertical {
                background-color: #444;
                height: 4px;
                margin: 2px 0px;
                border-radius: 2px;
            }
            QSplitter::handle:vertical:hover {
                background-color: #3498db;
            }
        """)
        # 스플리터 분할선 드래그 중에도 실시간으로 맨 아래 메시지를 추적하도록 연결
        self.main_splitter.splitterMoved.connect(self.scroll_log_to_bottom)

        # 1. 상단 탭 위젯
        self.tabs = QTabWidget()
        self.tab_capture = QWidget()
        self.tab_cleanup = QWidget()
        self.tab_webgl = QWidget()

        self.tabs.addTab(self.tab_capture, "Capture & Ingest")
        self.tabs.addTab(self.tab_cleanup, "Splat Cleanup")
        self.tabs.addTab(self.tab_webgl, "WebGL Build")

        self.setup_tab_capture()
        self.setup_tab_cleanup()
        self.setup_tab_webgl()
        
        self.main_splitter.addWidget(self.tabs)

        # 2. 하단 로그 위젯 (스크롤바 자동 표시 및 다크 스크롤바 스타일 적용)
        self.log_group = QGroupBox("Backend Status / Info")
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setContentsMargins(4, 12, 4, 4)
        
        self.log_console = AutoScrollTextBrowser()
        self.log_console.setOpenExternalLinks(False)
        self.log_console.setMinimumHeight(80)
        self.log_console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_console.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_console.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_console.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        log_layout.addWidget(self.log_console)
        self.main_splitter.addWidget(self.log_group)

        self.main_splitter.setSizes([550, 280])
        main_layout.addWidget(self.main_splitter)

        self.log("[ READY ] System initialized for Points & Reality 3DGS pipeline v2.222.", level="success")
        self.setCentralWidget(main_widget)

    def scroll_log_to_bottom(self):
        scrollbar = self.log_console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def setup_tab_capture(self):
        layout = QVBoxLayout(self.tab_capture)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 1. Project Directory Configuration
        self.group_project = CollapsibleSection("Project Directory Configuration")
        hlayout_proj = QHBoxLayout()
        self.lbl_proj = QLabel("Project Directory:")
        self.input_proj_dir = QLineEdit()
        self.input_proj_dir.setPlaceholderText("Select or create project directory...")
        self.input_proj_dir.editingFinished.connect(self.on_proj_dir_edited)
        
        self.btn_new_proj = QPushButton("+ New Project")
        self.btn_new_proj.clicked.connect(self.create_new_project)
        self.btn_browse_proj = QPushButton("Browse...")
        self.btn_browse_proj.clicked.connect(self.browse_project)
        self.btn_open_proj = QPushButton("Open Folder")
        self.btn_open_proj.clicked.connect(self.open_project_folder)
        
        hlayout_proj.addWidget(self.lbl_proj)
        hlayout_proj.addWidget(self.input_proj_dir)
        hlayout_proj.addWidget(self.btn_new_proj)
        hlayout_proj.addWidget(self.btn_browse_proj)
        hlayout_proj.addWidget(self.btn_open_proj)
        self.group_project.setContentLayout(hlayout_proj)
        layout.addWidget(self.group_project)

        # 2. Multi-Video Source & Frame Extractor
        self.group_ingest = CollapsibleSection("Multi-Video Source & Frame Extractor (FFmpeg)")
        vlayout_ingest = QVBoxLayout()

        hlayout_video_btns = QHBoxLayout()
        self.btn_add_video = QPushButton("+ Add Videos")
        self.btn_add_video.clicked.connect(self.add_videos)
        
        self.btn_remove_selected = QPushButton("- Remove Selected")
        self.btn_remove_selected.clicked.connect(self.remove_selected_videos)
        
        self.btn_remove_all = QPushButton("- Remove All")
        self.btn_remove_all.clicked.connect(self.clear_videos)
        
        self.btn_max_videos = QPushButton("⛶ Maximize")
        self.btn_max_videos.setCheckable(True)
        self.btn_max_videos.setToolTip("Toggle expand/restore table view")
        self.btn_max_videos.clicked.connect(self.toggle_maximize_video_table)

        hlayout_video_btns.addWidget(self.btn_add_video)
        hlayout_video_btns.addWidget(self.btn_remove_selected)
        hlayout_video_btns.addWidget(self.btn_remove_all)
        hlayout_video_btns.addStretch()
        hlayout_video_btns.addWidget(self.btn_max_videos)
        vlayout_ingest.addLayout(hlayout_video_btns)

        self.table_videos = QTableWidget(0, 5)
        self.table_videos.setHorizontalHeaderLabels(["☑ All", "Video File Path", "Duration", "Codec", "Status"])
        self.table_videos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_videos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_videos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_videos.setMinimumHeight(140)
        self.table_videos.verticalHeader().setVisible(False)
        
        table_style = """
        QTableWidget::item:focus { outline: none; border: none; }
        QCheckBox { margin: 0px; padding: 0px; }
        QCheckBox::indicator {
            width: 16px; height: 16px;
            background-color: #2b2b2b;
            border: 1px solid #666; border-radius: 3px;
        }
        QCheckBox::indicator:hover { border: 1px solid #999; }
        QCheckBox::indicator:checked {
            background-color: #3498db;
            border: 1px solid #2980b9;
            image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
        }
        """
        self.table_videos.setStyleSheet(table_style)
        self.table_videos.horizontalHeader().sectionClicked.connect(self.toggle_all_videos)
        self.all_videos_checked = True

        vlayout_ingest.addWidget(self.table_videos)

        hlayout_options = QHBoxLayout()
        self.lbl_fps = QLabel("Frame Rate:")
        self.input_fps = QLineEdit()
        self.input_fps.setText("4")
        self.input_fps.setFixedWidth(50)
        self.input_fps.setAlignment(Qt.AlignCenter)
        
        self.lbl_bitdepth = QLabel("   Bit Depth:")
        self.combo_bitdepth = QComboBox()
        self.combo_bitdepth.addItems(["8-bit PNG", "10-bit WebP", "16-bit PNG (Lossless)", "16-bit EXR"])
        self.combo_bitdepth.setCurrentText("16-bit PNG (Lossless)")
        
        self.lbl_colorspace = QLabel(" Color Space:")
        self.combo_color = QComboBox()
        self.combo_color.addItems(["None (Pass-through Log)", "Apply Ingest Rec.709 LUT"])
        self.combo_color.setCurrentText("Apply Ingest Rec.709 LUT")

        hlayout_options.addWidget(self.lbl_fps)
        hlayout_options.addWidget(self.input_fps)
        hlayout_options.addWidget(QLabel("FPS"))
        hlayout_options.addWidget(self.lbl_bitdepth)
        hlayout_options.addWidget(self.combo_bitdepth)
        hlayout_options.addWidget(self.lbl_colorspace)
        hlayout_options.addWidget(self.combo_color)
        hlayout_options.addStretch()
        vlayout_ingest.addLayout(hlayout_options)

        hlayout_run = QHBoxLayout()
        self.btn_run_extraction = QPushButton("⚡ Run Batch Frame Extraction")
        self.btn_run_extraction.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 6px 15px;")
        self.btn_run_extraction.clicked.connect(self.run_extraction)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.btn_open_extracted = QPushButton("📂 Open Folder")
        self.btn_open_extracted.setStyleSheet("background-color: #3c3c3c; color: #dddddd; font-weight: bold; padding: 6px 15px;")
        self.btn_open_extracted.clicked.connect(self.open_extracted_folder)
        
        hlayout_run.addWidget(self.btn_run_extraction)
        hlayout_run.addWidget(self.progress_bar)
        hlayout_run.addWidget(self.btn_open_extracted)
        vlayout_ingest.addLayout(hlayout_run)
        
        self.group_ingest.setContentLayout(vlayout_ingest)
        layout.addWidget(self.group_ingest)

        # 3. Alignment & 3DGS Training Launcher
        self.group_launcher = CollapsibleSection("Alignment & 3DGS Training Launcher")
        hlayout_launcher = QHBoxLayout()
        
        self.lbl_step1 = QLabel("1. Camera Alignment:")
        self.lbl_step1.setStyleSheet("color: #aaa; font-weight: bold;")
        self.btn_launch_rc = QPushButton("🚀 RealityCapture")
        self.btn_launch_rc.setToolTip("Export Registration & XMP (Postshot) or COLMAP (Lichtfeld) to 02_camera_alignment")
        self.btn_launch_rc.clicked.connect(self.launch_realitycapture)
        
        self.lbl_step2 = QLabel("2. 3DGS Trainer:")
        self.lbl_step2.setStyleSheet("color: #aaa; font-weight: bold;")
        
        self.combo_trainer = QComboBox()
        self.combo_trainer.addItems(["Postshot (Jawset)", "Lichtfeld Studio"])
        saved_trainer = self.settings.value("selected_trainer", "Postshot (Jawset)")
        self.combo_trainer.setCurrentText(saved_trainer)
        self.combo_trainer.currentTextChanged.connect(lambda txt: self.settings.setValue("selected_trainer", txt))
        
        self.btn_launch_trainer = QPushButton("🚀 Launch Trainer")
        self.btn_launch_trainer.setStyleSheet("background-color: #2c3e50; color: #3498db; font-weight: bold; border: 1px solid #3498db;")
        self.btn_launch_trainer.clicked.connect(self.launch_selected_trainer)

        lbl_flow_hint = QLabel("➔ [ 03_splats_exports ]")
        lbl_flow_hint.setStyleSheet("color: #aaa; font-weight: bold;")

        hlayout_launcher.addWidget(self.lbl_step1)
        hlayout_launcher.addWidget(self.btn_launch_rc)
        hlayout_launcher.addWidget(QLabel("  ➔  "))
        hlayout_launcher.addWidget(self.lbl_step2)
        hlayout_launcher.addWidget(self.combo_trainer)
        hlayout_launcher.addWidget(self.btn_launch_trainer)
        hlayout_launcher.addWidget(lbl_flow_hint)
        hlayout_launcher.addStretch()

        self.group_launcher.setContentLayout(hlayout_launcher)
        layout.addWidget(self.group_launcher)

        # 4. Export Folder Watcher (Auto Pipeline)
        self.group_watcher = CollapsibleSection("Export Folder Watcher (Auto Pipeline)")
        vlayout_watcher = QVBoxLayout()
        hlayout_watcher_btns = QHBoxLayout()
        
        self.btn_start_watcher = QPushButton("Start Auto Watcher")
        self.btn_start_watcher.clicked.connect(self.toggle_watcher)
        
        self.btn_send_cleanup = QPushButton("Send to Cleanup ➔")
        self.btn_send_cleanup.clicked.connect(self.send_to_cleanup)
        
        self.btn_clear_watcher = QPushButton("- Remove All")
        self.btn_clear_watcher.clicked.connect(self.clear_watcher_table)

        self.btn_max_watcher = QPushButton("⛶ Maximize")
        self.btn_max_watcher.setCheckable(True)
        self.btn_max_watcher.setToolTip("Toggle expand/restore watcher view")
        self.btn_max_watcher.clicked.connect(self.toggle_maximize_watcher_table)

        hlayout_watcher_btns.addWidget(self.btn_start_watcher)
        hlayout_watcher_btns.addWidget(self.btn_send_cleanup)
        hlayout_watcher_btns.addWidget(self.btn_clear_watcher)
        hlayout_watcher_btns.addStretch()
        
        self.lbl_watcher_status = QLabel("● IDLE")
        self.lbl_watcher_status.setStyleSheet("color: gray; font-weight: bold; margin-right: 10px;")
        hlayout_watcher_btns.addWidget(self.lbl_watcher_status)
        hlayout_watcher_btns.addWidget(self.btn_max_watcher)
        vlayout_watcher.addLayout(hlayout_watcher_btns)

        self.table_watcher = QTableWidget(0, 4)
        self.table_watcher.setHorizontalHeaderLabels(["Detected File / Folder Path", "Size (MB)", "Time", "Status"])
        self.table_watcher.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_watcher.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_watcher.setMinimumHeight(140)
        self.table_watcher.verticalHeader().setVisible(False)
        
        vlayout_watcher.addWidget(self.table_watcher)
        self.group_watcher.setContentLayout(vlayout_watcher)
        layout.addWidget(self.group_watcher)

        layout.addStretch()

    def setup_tab_cleanup(self):
        layout = QVBoxLayout(self.tab_cleanup)
        layout.addWidget(QLabel("Splat Cleanup (Houdini Engine) parameters will go here."))
        layout.addStretch()

    def setup_tab_webgl(self):
        layout = QVBoxLayout(self.tab_webgl)
        layout.addWidget(QLabel("WebGL Export and Three.js settings will go here."))
        layout.addStretch()

    # --- 다국어 전환 및 적용 로직 ---
    def toggle_language(self):
        self.current_lang = "KO" if self.current_lang == "EN" else "EN"
        self.settings.setValue("ui_language", self.current_lang)
        self.apply_language(self.current_lang)
        self.log(f"Language changed to: {self.current_lang}", level="info")

    def apply_language(self, lang):
        t = TRANSLATIONS.get(lang, TRANSLATIONS["EN"])
        self.btn_lang.setText(f"🌐 Language: {lang}")
        
        self.tabs.setTabText(0, t["tab_capture"])
        self.tabs.setTabText(1, t["tab_cleanup"])
        self.tabs.setTabText(2, t["tab_webgl"])
        
        self.group_project.setTitle(t["group_project"])
        self.lbl_proj.setText(t["lbl_project_dir"])
        self.input_proj_dir.setPlaceholderText(t["placeholder_project"])
        self.btn_new_proj.setText(t["btn_new_proj"])
        self.btn_browse_proj.setText(t["btn_browse_proj"])
        self.btn_open_proj.setText(t["btn_open_proj"])
        
        self.group_ingest.setTitle(t["group_ingest"])
        self.btn_add_video.setText(t["btn_add_videos"])
        self.btn_remove_selected.setText(t["btn_remove_selected"])
        self.btn_remove_all.setText(t["btn_remove_all"])
        self.btn_max_videos.setText(t["btn_restore"] if self.btn_max_videos.isChecked() else t["btn_max"])
        
        chk_label = "☑ All" if getattr(self, 'all_videos_checked', True) else "☐ All"
        self.table_videos.setHorizontalHeaderLabels([chk_label, t["tbl_col_video"], t["tbl_col_duration"], t["tbl_col_codec"], t["tbl_col_status"]])
        
        self.lbl_fps.setText(t["lbl_framerate"])
        self.lbl_bitdepth.setText(t["lbl_bitdepth"])
        self.lbl_colorspace.setText(t["lbl_colorspace"])
        
        cur_color_idx = self.combo_color.currentIndex()
        self.combo_color.setItemText(0, t["opt_pass_log"])
        self.combo_color.setItemText(1, t["opt_rec709"])
        self.combo_color.setCurrentIndex(cur_color_idx)
        
        self.btn_run_extraction.setText(t["btn_run_extract"])
        self.btn_open_extracted.setText(t["btn_open_extracted"])
        
        self.group_launcher.setTitle(t["group_launcher"])
        self.lbl_step1.setText(t["lbl_step1"])
        self.lbl_step2.setText(t["lbl_step2"])
        self.btn_launch_trainer.setText(t["btn_launch_trainer"])
        
        self.group_watcher.setTitle(t["group_watcher"])
        is_watching = hasattr(self, 'watcher_thread') and self.watcher_thread.isRunning()
        self.btn_start_watcher.setText(t["btn_stop_watcher"] if is_watching else t["btn_start_watcher"])
        self.btn_send_cleanup.setText(t["btn_send_cleanup"])
        self.btn_clear_watcher.setText(t["btn_remove_all"])
        self.btn_max_watcher.setText(t["btn_restore"] if self.btn_max_watcher.isChecked() else t["btn_max"])
        
        self.table_watcher.setHorizontalHeaderLabels([t["tbl_col_detected"], t["tbl_col_size"], t["tbl_col_time"], t["tbl_col_status"]])
        self.log_group.setTitle(t["log_title"])

    # --- 테이블 확장/축소 토글 로직 ---
    def toggle_maximize_video_table(self):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        if self.btn_max_videos.isChecked():
            self.btn_max_videos.setText(t["btn_restore"])
            self.group_project.set_expanded(False)
            self.group_launcher.set_expanded(False)
            self.group_watcher.set_expanded(False)
            self.table_videos.setMinimumHeight(380)
        else:
            self.btn_max_videos.setText(t["btn_max"])
            self.group_project.set_expanded(True)
            self.group_launcher.set_expanded(True)
            self.group_watcher.set_expanded(True)
            self.table_videos.setMinimumHeight(140)

    def toggle_maximize_watcher_table(self):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        if self.btn_max_watcher.isChecked():
            self.btn_max_watcher.setText(t["btn_restore"])
            self.group_project.set_expanded(False)
            self.group_ingest.set_expanded(False)
            self.group_launcher.set_expanded(False)
            self.table_watcher.setMinimumHeight(380)
        else:
            self.btn_max_watcher.setText(t["btn_max"])
            self.group_project.set_expanded(True)
            self.group_ingest.set_expanded(True)
            self.group_launcher.set_expanded(True)
            self.table_watcher.setMinimumHeight(140)

    # --- 공통 유틸리티 ---
    def log(self, text, level="info"):
        color_map = {
            "error": "#e74c3c",
            "warning": "#f39c12",
            "success": "#2ecc71",
            "info": "#cccccc"
        }
        color = color_map.get(level.lower(), "#cccccc")
        formatted_text = text.replace("\n", "<br>")
        html_msg = f'<span style="color: {color}; font-family: Consolas, monospace;">{formatted_text}</span>'
        self.log_console.append(html_msg)
        self.scroll_log_to_bottom()
        
    def _debounce_btn(self, ms=1500):
        btn = self.sender()
        if isinstance(btn, QPushButton):
            btn.setEnabled(False)
            QTimer.singleShot(ms, lambda b=btn: b.setEnabled(True))

    # --- Section 1 & 2 로직 ---
    def toggle_all_videos(self, index):
        if index == 0:
            self.all_videos_checked = not getattr(self, 'all_videos_checked', True)
            new_label = "☑ All" if self.all_videos_checked else "☐ All"
            
            item = self.table_videos.horizontalHeaderItem(0)
            if item:
                item.setText(new_label)
            
            for row in range(self.table_videos.rowCount()):
                widget = self.table_videos.cellWidget(row, 0)
                if widget and widget.layout():
                    chk_box = widget.layout().itemAt(0).widget()
                    if isinstance(chk_box, QCheckBox):
                        chk_box.setChecked(self.all_videos_checked)

    def browse_project(self):
        self._debounce_btn()
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.input_proj_dir.setText(directory)
            self.log(f"Project directory selected: {directory}", level="info")
            self.auto_scan_footage(directory)

    def on_proj_dir_edited(self):
        directory = self.input_proj_dir.text().strip()
        if directory and os.path.exists(directory):
            self.auto_scan_footage(directory)

    def create_new_project(self):
        self._debounce_btn()
        base_dir = QFileDialog.getExistingDirectory(self, "Select Parent Workspace Directory")
        if not base_dir:
            return
        
        default_name = "MyScan_01"
        while True:
            proj_name, ok = QInputDialog.getText(self, "New Project", "Enter Project Name:", text=default_name)
            if not ok or not proj_name.strip():
                return
            
            proj_name = proj_name.strip()
            target_dir = os.path.join(base_dir, proj_name)
            
            if os.path.exists(target_dir):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Directory Already Exists")
                msg_box.setText(f"Folder '{proj_name}' already exists in this location.")
                msg_box.setInformativeText("Would you like to use/overwrite this existing folder, or rename it?")
                btn_overwrite = msg_box.addButton("Use / Overwrite", QMessageBox.AcceptRole)
                btn_rename = msg_box.addButton("Rename", QMessageBox.ActionRole)
                msg_box.addButton("Cancel", QMessageBox.RejectRole)
                msg_box.exec_()
                
                if msg_box.clickedButton() == btn_overwrite:
                    break
                elif msg_box.clickedButton() == btn_rename:
                    default_name = f"{proj_name}_new"
                    continue
                else:
                    return
            else:
                break
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            create_project_structure(target_dir, PROJECT_SUBFOLDERS)
            self.input_proj_dir.setText(target_dir)
            self.log(f"[SUCCESS] Project ready with standard subfolders:\n➔ {target_dir}", level="success")
            self.auto_scan_footage(target_dir)
        except Exception as e:
            self.log(f"[ERROR] Failed to initialize project structure: {str(e)}", level="error")

    def auto_scan_footage(self, proj_dir):
        raw_footage_dir = os.path.join(proj_dir, "00_raw_footage")
        if not os.path.exists(raw_footage_dir):
            return
            
        valid_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.m4v')
        found_files = []
        for file_name in os.listdir(raw_footage_dir):
            if file_name.lower().endswith(valid_extensions):
                found_files.append(os.path.join(raw_footage_dir, file_name))
        
        if found_files:
            self.clear_videos_without_debounce() 
            for file_path in found_files:
                self.add_video_to_table(file_path)
            self.log(f"Auto-loaded {len(found_files)} video(s) from 00_raw_footage.", level="info")

    def add_video_to_table(self, file_path):
        norm_new_path = os.path.normcase(os.path.normpath(os.path.abspath(file_path)))
        
        for row in range(self.table_videos.rowCount()):
            existing_path = self.table_videos.item(row, 1).text()
            norm_existing = os.path.normcase(os.path.normpath(os.path.abspath(existing_path)))
            if norm_new_path == norm_existing:
                return False 

        row = self.table_videos.rowCount()
        self.table_videos.insertRow(row)
        
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_box = QCheckBox()
        chk_box.setChecked(getattr(self, 'all_videos_checked', True))
        chk_layout.addWidget(chk_box)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        self.table_videos.setCellWidget(row, 0, chk_widget)
        
        clean_path = os.path.normpath(file_path)
        
        self.table_videos.setItem(row, 1, QTableWidgetItem(clean_path))
        self.table_videos.setItem(row, 2, QTableWidgetItem("Ready"))
        self.table_videos.setItem(row, 3, QTableWidgetItem("ProRes/H264"))
        self.table_videos.setItem(row, 4, QTableWidgetItem("Queued"))
        return True

    def open_project_folder(self):
        self._debounce_btn()
        target_dir = self.input_proj_dir.text().strip()
        if not target_dir or not os.path.exists(target_dir):
            self.log("[ERROR] Project directory does not exist or is not specified.", level="error")
            return
        try:
            os.startfile(target_dir)
            self.log(f"Opened explorer: {target_dir}", level="info")
        except Exception as e:
            self.log(f"[ERROR] Could not open folder: {str(e)}", level="error")

    def open_extracted_folder(self):
        self._debounce_btn()
        proj_dir = self.input_proj_dir.text().strip()
        if not proj_dir or not os.path.exists(proj_dir):
            self.log("[ERROR] Please set a valid Project Directory first.", level="error")
            return
        extracted_dir = os.path.join(proj_dir, "01_extracted_frames")
        if not os.path.exists(extracted_dir):
            os.makedirs(extracted_dir, exist_ok=True)
        try:
            os.startfile(extracted_dir)
        except Exception as e:
            self.log(f"[ERROR] Could not open folder: {str(e)}", level="error")

    def add_videos(self):
        self._debounce_btn()
        proj_dir = self.input_proj_dir.text().strip()
        
        if not proj_dir or not os.path.exists(proj_dir):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Project Directory Not Set")
            msg_box.setText("No valid Project Directory is currently selected.")
            msg_box.setInformativeText("Would you like to select a project folder first, or import videos anyway?")
            
            btn_select = msg_box.addButton("Select Folder", QMessageBox.AcceptRole)
            btn_import = msg_box.addButton("Import Anyway", QMessageBox.ActionRole)
            btn_cancel = msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.exec_()
            
            if msg_box.clickedButton() == btn_select:
                self.browse_project()
                proj_dir = self.input_proj_dir.text().strip()
                if not proj_dir or not os.path.exists(proj_dir):
                    return
            elif msg_box.clickedButton() == btn_import:
                pass 
            else:
                return 

        if proj_dir and os.path.exists(proj_dir):
            raw_footage_dir = os.path.join(proj_dir, "00_raw_footage")
            os.makedirs(raw_footage_dir, exist_ok=True)
            start_dir = raw_footage_dir
        else:
            start_dir = ""

        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", start_dir, "Video Files (*.mov *.mp4 *.mkv *.avi *.m4v)"
        )
        if files:
            added_count = 0
            for f in files:
                if self.add_video_to_table(f):
                    added_count += 1
            if added_count > 0:
                self.log(f"Manually added {added_count} video file(s).", level="info")
            else:
                self.log("No new videos added (all selected files already exist).", level="info")

    def remove_selected_videos(self):
        self._debounce_btn()
        removed_count = 0
        for i in range(self.table_videos.rowCount() - 1, -1, -1):
            widget = self.table_videos.cellWidget(i, 0)
            if widget and widget.layout():
                chk_box = widget.layout().itemAt(0).widget()
                if isinstance(chk_box, QCheckBox) and chk_box.isChecked():
                    self.table_videos.removeRow(i)
                    removed_count += 1
        
        if removed_count > 0:
            self.log(f"Removed {removed_count} selected video(s) from the queue.", level="info")
        else:
            self.log("[WARNING] No videos selected to remove.", level="warning")

    def clear_videos(self):
        self._debounce_btn()
        self.clear_videos_without_debounce()
        self.log("All videos removed.", level="info")
        
    def clear_videos_without_debounce(self):
        self.table_videos.setRowCount(0)
        self.progress_bar.setValue(0)

    def run_extraction(self):
        if self.table_videos.rowCount() == 0:
            self.log("[WARNING] No videos in queue to extract.", level="warning")
            return
            
        proj_dir = self.input_proj_dir.text().strip()
        if not proj_dir or not os.path.exists(proj_dir):
            self.log("[ERROR] Please set a valid Project Directory to extract frames.", level="error")
            return
            
        tasks = []
        for i in range(self.table_videos.rowCount()):
            widget = self.table_videos.cellWidget(i, 0)
            if widget and widget.layout():
                chk_box = widget.layout().itemAt(0).widget()
                if isinstance(chk_box, QCheckBox) and chk_box.isChecked():
                    file_path = self.table_videos.item(i, 1).text()
                    tasks.append((i, file_path))
        
        if not tasks:
            self.log("[WARNING] No files selected. Please check at least one video.", level="warning")
            return
            
        target_dir = os.path.join(proj_dir, "01_extracted_frames")
        fps = self.input_fps.text().strip()
        bit_depth = self.combo_bitdepth.currentText()
        
        self.btn_run_extraction.setEnabled(False)
        self.log(f"Starting batch extraction for {len(tasks)} selected video(s)... [Settings: {fps} FPS, {bit_depth}]", level="info")
        
        self.extractor_thread = ExtractorThread(tasks, fps, bit_depth, target_dir)
        self.extractor_thread.progress_update.connect(self.update_progress)
        self.extractor_thread.file_status.connect(self.update_file_status)
        self.extractor_thread.finished_extraction.connect(self.extraction_finished)
        self.extractor_thread.start()

    def update_progress(self, val, msg):
        self.progress_bar.setValue(val)
        if val < 100:
            self.log(msg, level="info")

    def update_file_status(self, row, status):
        self.table_videos.setItem(row, 4, QTableWidgetItem(status))

    def extraction_finished(self, target_dir, success):
        self.btn_run_extraction.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.log("[SUCCESS] Batch extraction completed. Check '01_extracted_frames'.", level="success")
        else:
            self.log("[ERROR] Batch extraction aborted due to errors.", level="error")

    # ---------------------------------------------------------
    # --- Section 3: 런처 기능 ---
    # ---------------------------------------------------------
    def launch_realitycapture(self):
        self._debounce_btn(2500)
        
        saved_path = self.settings.value("path_realitycapture", "")
        if saved_path and os.path.exists(saved_path):
            subprocess.Popen([saved_path])
            self.log(f"Launched RealityCapture from saved path: {saved_path}", level="info")
            return

        epic_dir = r"C:\Program Files\Epic Games"
        rc_path_epic = None
        
        if os.path.exists(epic_dir):
            for folder_name in os.listdir(epic_dir):
                if "reality" in folder_name.lower():
                    for exe_name in ["RealityCapture.exe", "RealityScan.exe"]:
                        potential_path = os.path.join(epic_dir, folder_name, exe_name)
                        if os.path.exists(potential_path):
                            rc_path_epic = potential_path
                            break
                if rc_path_epic:
                    break

        rc_path_legacy = r"C:\Program Files\Capturing Reality\RealityCapture\RealityCapture.exe"
        
        if rc_path_epic and os.path.exists(rc_path_epic):
            subprocess.Popen([rc_path_epic])
            self.log("Launched RealityCapture from Epic Games successfully.", level="info")
        elif os.path.exists(rc_path_legacy):
            subprocess.Popen([rc_path_legacy])
            self.log("Launched RealityCapture (Legacy Standalone) successfully.", level="info")
        else:
            self.log("[WARNING] RealityCapture executable not found in default directories.", level="warning")
            self.log("Please locate the executable manually.", level="info")
            
            file_path, _ = QFileDialog.getOpenFileName(self, "Locate RealityCapture.exe", "C:\\", "Executable (*.exe)")
            if file_path:
                self.settings.setValue("path_realitycapture", file_path)
                subprocess.Popen([file_path])
                self.log(f"Path saved & Launched RealityCapture: {file_path}", level="success")

    def launch_selected_trainer(self):
        selected = self.combo_trainer.currentText()
        if "Postshot" in selected:
            self.launch_postshot()
        else:
            self.launch_lichtfeld()

    def launch_postshot(self):
        self._debounce_btn(2500)
        
        saved_path = self.settings.value("path_postshot", "")
        if saved_path and os.path.exists(saved_path):
            subprocess.Popen([saved_path])
            self.log(f"Launched Postshot from saved path: {saved_path}", level="info")
            return

        ps_path_jawset = r"C:\Program Files\Jawset Postshot\bin\postshot.exe"
        ps_path_local = os.path.expandvars(r"%LocalAppData%\Programs\Postshot\postshot.exe")
        ps_path_prog = r"C:\Program Files\Postshot\postshot.exe"
        
        if os.path.exists(ps_path_jawset):
            subprocess.Popen([ps_path_jawset])
            self.log("Launched Postshot (Jawset) successfully.", level="info")
        elif os.path.exists(ps_path_local):
            subprocess.Popen([ps_path_local])
            self.log("Launched Postshot (Local) successfully.", level="info")
        elif os.path.exists(ps_path_prog):
            subprocess.Popen([ps_path_prog])
            self.log("Launched Postshot (Program Files) successfully.", level="info")
        else:
            self.log("[WARNING] Postshot executable not found in default directories.", level="warning")
            self.log("Please locate postshot.exe manually.", level="info")
            
            file_path, _ = QFileDialog.getOpenFileName(self, "Locate postshot.exe", "C:\\", "Executable (*.exe)")
            if file_path:
                self.settings.setValue("path_postshot", file_path)
                subprocess.Popen([file_path])
                self.log(f"Path saved & Launched Postshot: {file_path}", level="success")

    def launch_lichtfeld(self):
        self._debounce_btn(2500)
        
        saved_path = self.settings.value("path_lichtfeld", "")
        if saved_path and os.path.exists(saved_path):
            subprocess.Popen([saved_path])
            self.log(f"Launched Lichtfeld Studio from saved path: {saved_path}", level="info")
            return

        lf_path_d1 = r"D:\LichtFeld-Studio\bin\LichtFeld-Studio.exe"
        lf_path_d2 = r"D:\LichtFeld-Studio\LichtFeld-Studio.exe"
        lf_path_prog = r"C:\Program Files\Lichtfeld\Lichtfeld.exe"
        lf_path_local = os.path.expandvars(r"%LocalAppData%\Programs\Lichtfeld\Lichtfeld.exe")
        
        if os.path.exists(lf_path_d1):
            subprocess.Popen([lf_path_d1], cwd=os.path.dirname(lf_path_d1))
            self.log(f"Launched Lichtfeld Studio successfully: {lf_path_d1}", level="info")
        elif os.path.exists(lf_path_d2):
            subprocess.Popen([lf_path_d2], cwd=os.path.dirname(lf_path_d2))
            self.log(f"Launched Lichtfeld Studio successfully: {lf_path_d2}", level="info")
        elif os.path.exists(lf_path_prog):
            subprocess.Popen([lf_path_prog])
            self.log("Launched Lichtfeld Studio successfully.", level="info")
        elif os.path.exists(lf_path_local):
            subprocess.Popen([lf_path_local])
            self.log("Launched Lichtfeld Studio successfully.", level="info")
        else:
            self.log("[WARNING] Lichtfeld Studio executable not found in default directories.", level="warning")
            self.log("Please locate the executable manually (e.g. Lichtfeld.exe / LichtFeld-Studio.exe).", level="info")
            
            file_path, _ = QFileDialog.getOpenFileName(self, "Locate Lichtfeld Studio", "C:\\", "Executable (*.exe)")
            if file_path:
                self.settings.setValue("path_lichtfeld", file_path)
                subprocess.Popen([file_path])
                self.log(f"Path saved & Launched Lichtfeld Studio: {file_path}", level="success")

    # ---------------------------------------------------------
    # --- Section 4: Folder Watcher 기능 ---
    # ---------------------------------------------------------
    def toggle_watcher(self):
        self._debounce_btn()
        proj_dir = self.input_proj_dir.text().strip()
        if not proj_dir or not os.path.exists(proj_dir):
            self.log("[ERROR] Please set a valid Project Directory first.", level="error")
            return

        watch_dir = os.path.join(proj_dir, "03_splats_exports")
        os.makedirs(watch_dir, exist_ok=True) 

        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])

        if hasattr(self, 'watcher_thread') and self.watcher_thread.isRunning():
            self.watcher_thread.stop()
            self.btn_start_watcher.setText(t["btn_start_watcher"])
            self.btn_start_watcher.setStyleSheet("")
            self.lbl_watcher_status.setText("● IDLE")
            self.lbl_watcher_status.setStyleSheet("color: gray; font-weight: bold; margin-right: 10px;")
            self.log("Auto Watcher stopped.", level="info")
        else:
            self.watcher_thread = FolderWatcherThread(watch_dir)
            self.watcher_thread.file_detected.connect(self.add_watcher_item)
            self.watcher_thread.start()
            self.btn_start_watcher.setText(t["btn_stop_watcher"])
            self.btn_start_watcher.setStyleSheet("background-color: #e74c3c; color: white;")
            self.lbl_watcher_status.setText("● WATCHING 03_splats_exports")
            self.lbl_watcher_status.setStyleSheet("color: #2ecc71; font-weight: bold; margin-right: 10px;")
            self.log(f"Auto Watcher started for: {watch_dir}", level="success")

    def add_watcher_item(self, path, size_mb, time_str):
        row = self.table_watcher.rowCount()
        self.table_watcher.insertRow(row)
        self.table_watcher.setItem(row, 0, QTableWidgetItem(path))
        self.table_watcher.setItem(row, 1, QTableWidgetItem(size_mb))
        self.table_watcher.setItem(row, 2, QTableWidgetItem(time_str))
        self.table_watcher.setItem(row, 3, QTableWidgetItem("Ready for Cleanup"))
        self.log(f"New splat file detected: {os.path.basename(path)}", level="info")

    def send_to_cleanup(self):
        self._debounce_btn()
        if self.table_watcher.rowCount() == 0:
            self.log("[WARNING] No detected files to send to cleanup.", level="warning")
            return
            
        selected_rows = self.table_watcher.selectionModel().selectedRows()
        rows_to_process = [index.row() for index in selected_rows] if selected_rows else range(self.table_watcher.rowCount())

        files_sent = []
        for row in rows_to_process:
            path = self.table_watcher.item(row, 0).text()
            files_sent.append(os.path.basename(path))
            self.table_watcher.setItem(row, 3, QTableWidgetItem("Sent to Tab 2"))
        
        self.log(f"Sent {len(files_sent)} file(s) to Splat Cleanup (Tab 2).", level="success")
        self.tabs.setCurrentIndex(1)

    def clear_watcher_table(self):
        self._debounce_btn()
        self.table_watcher.setRowCount(0)
        self.log("Watcher table cleared.", level="info")