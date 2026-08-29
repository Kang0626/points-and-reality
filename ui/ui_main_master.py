# ui/ui_main_master.py
import os
import json
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QLabel, QPushButton, QSplitter, 
                             QSizePolicy, QComboBox, QLineEdit, QFileDialog, 
                             QInputDialog, QMessageBox, QScrollArea, QFrame, 
                             QButtonGroup, QStackedWidget)
from PyQt5.QtCore import Qt, QSettings
from config import DARK_THEME_CSS, APP_VERSION
from ui.ui_translations import TRANSLATIONS
from ui.ui_components import AutoScrollTextBrowser
from ui.tabs.capture_sections.section_project import ProjectConfigWidget
from ui.tabs.capture_sections.section_ingest import IngestWidget
from ui.tabs.capture_sections.section_launcher import LauncherWidget
from ui.tabs.tab_cleanup import CleanupTab
from ui.tabs.tab_webgl import WebGLTab
from ui.tabs.tab_showroom import ShowroomTab

class PointsAndRealityController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Points & Reality 3DGS Controller - {APP_VERSION}")
        
        self.resize(1120, 880)
        self.setMinimumSize(850, 650)
        self.setStyleSheet(DARK_THEME_CSS)
        
        self.settings = QSettings("PointsAndReality", "3DGSController")
        # Migrate legacy settings if available
        legacy_settings = QSettings("SplatialPipeline", "3DGSController")
        if not self.settings.allKeys() and legacy_settings.allKeys():
            for key in legacy_settings.allKeys():
                self.settings.setValue(key, legacy_settings.value(key))
                
        self.current_lang = self.settings.value("ui_language", "KO")
        
        self.init_ui()
        self.load_presets()
        self.apply_language(self.current_lang)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # ----------------------------------------------------
        # 1. Top Global Header (2-Tier Vertical Layout)
        # ----------------------------------------------------
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_card.setStyleSheet("""
            QFrame#headerCard {
                background-color: #15181f;
                border: 1px solid #232732;
                border-radius: 6px;
            }
        """)
        header_vlayout = QVBoxLayout(header_card)
        header_vlayout.setContentsMargins(12, 8, 12, 8)
        header_vlayout.setSpacing(8)

        # ----------------------------------------------------
        # Tier 1: Brand Title & Utility Controls (Presets + Language)
        # ----------------------------------------------------
        top_tier = QHBoxLayout()
        top_tier.setSpacing(10)

        # App Brand Title
        title_box = QHBoxLayout()
        title_box.setSpacing(8)
        
        lbl_logo = QLabel("POINTS & REALITY")
        lbl_logo.setStyleSheet("color: #ffffff; font-size: 13.5px; font-weight: 800; letter-spacing: 0.8px;")
        
        lbl_ver = QLabel("3DGS Pipeline Controller")
        lbl_ver.setStyleSheet("color: #64748b; font-size: 11.5px; font-weight: 500;")
        
        title_box.addWidget(lbl_logo)
        title_box.addWidget(lbl_ver)
        top_tier.addLayout(title_box)
        top_tier.addStretch()

        # Right Controls: Preset & Language
        controls_box = QHBoxLayout()
        controls_box.setSpacing(6)

        self.lbl_preset = QLabel("Preset:")
        self.lbl_preset.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
        
        self.combo_preset = QComboBox()
        self.combo_preset.setMinimumWidth(130)
        self.combo_preset.currentIndexChanged.connect(self.apply_preset)

        self.btn_preset_browse = QPushButton("Folder")
        self.btn_preset_browse.setToolTip("Set Preset Directory")
        self.btn_preset_browse.clicked.connect(self.browse_preset_dir)

        self.btn_preset_save = QPushButton("Save")
        self.btn_preset_save.setToolTip("Save Current Preset")
        self.btn_preset_save.clicked.connect(self.save_preset)

        self.btn_preset_del = QPushButton("Delete")
        self.btn_preset_del.setToolTip("Delete Selected Preset")
        self.btn_preset_del.clicked.connect(self.delete_preset)

        self.btn_lang = QPushButton(self.current_lang)
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setFixedWidth(56)
        self.btn_lang.clicked.connect(self.toggle_language)

        controls_box.addWidget(self.lbl_preset)
        controls_box.addWidget(self.combo_preset)
        controls_box.addWidget(self.btn_preset_browse)
        controls_box.addWidget(self.btn_preset_save)
        controls_box.addWidget(self.btn_preset_del)
        controls_box.addSpacing(4)
        controls_box.addWidget(self.btn_lang)

        top_tier.addLayout(controls_box)
        header_vlayout.addLayout(top_tier)

        # Subtle separator line between Tier 1 and Tier 2
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Plain)
        sep.setStyleSheet("color: #232732; background-color: #232732; height: 1px; border: none; margin: 0px;")
        sep.setFixedHeight(1)
        header_vlayout.addWidget(sep)

        # ----------------------------------------------------
        # Tier 2: Pipeline Step Navigation Tabs (Segmented Button Group)
        # ----------------------------------------------------
        tier2_layout = QHBoxLayout()
        tier2_layout.setContentsMargins(0, 2, 0, 2)
        tier2_layout.setSpacing(6)

        self.tab_btn_group = QButtonGroup(self)
        self.tab_btn_group.setExclusive(True)

        self.btn_tab_capture = QPushButton("Capture && Ingest")
        self.btn_tab_capture.setCheckable(True)
        self.btn_tab_capture.setChecked(True)
        self.btn_tab_capture.setCursor(Qt.PointingHandCursor)

        self.btn_tab_cleanup = QPushButton("Splat Cleanup")
        self.btn_tab_cleanup.setCheckable(True)
        self.btn_tab_cleanup.setCursor(Qt.PointingHandCursor)

        self.btn_tab_webgl = QPushButton("WebGL Build")
        self.btn_tab_webgl.setCheckable(True)
        self.btn_tab_webgl.setCursor(Qt.PointingHandCursor)

        self.btn_tab_showroom = QPushButton("Cloud Showroom")
        self.btn_tab_showroom.setCheckable(True)
        self.btn_tab_showroom.setCursor(Qt.PointingHandCursor)

        self.tab_buttons = [self.btn_tab_capture, self.btn_tab_cleanup, self.btn_tab_webgl, self.btn_tab_showroom]

        nav_tab_css = """
            QPushButton {
                background-color: #171922;
                color: #94a3b8;
                border: 1px solid #282d3c;
                border-radius: 5px;
                min-height: 32px;
                height: 32px;
                padding: 2px 20px;
                font-weight: 600;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #202636;
                color: #f1f5f9;
                border-color: #3b465c;
            }
            QPushButton:checked {
                background-color: #1d4ed8;
                color: #ffffff;
                border: 1px solid #3b82f6;
                font-weight: 600;
            }
        """

        for idx, btn in enumerate(self.tab_buttons):
            btn.setStyleSheet(nav_tab_css)
            self.tab_btn_group.addButton(btn, idx)
            tier2_layout.addWidget(btn)

        self.tab_btn_group.buttonClicked[int].connect(self._on_tab_changed)
        tier2_layout.addStretch()

        header_vlayout.addLayout(tier2_layout)
        main_layout.addWidget(header_card)

        # ----------------------------------------------------
        # 2. Main Body Splitter (Tabs Stack + Log Console)
        # ----------------------------------------------------
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle:vertical {
                background-color: #2d3139;
                height: 5px;
                border-radius: 2px;
                margin: 2px 0px;
            }
            QSplitter::handle:vertical:hover {
                background-color: #38bdf8;
            }
        """)

        # Stacked Pages
        self.stacked_widget = QStackedWidget()

        # --- Tab 1: Capture & Ingest Pipeline ---
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("QWidget#scrollContent { background-color: transparent; }")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 4, 4, 4)
        scroll_layout.setSpacing(10)
        
        self.sec_proj = ProjectConfigWidget()
        self.sec_ingest = IngestWidget()
        self.sec_launch = LauncherWidget()
        
        # Connect signals
        self.sec_proj.proj_dir_changed.connect(self.sec_launch.set_proj_dir)
        self.sec_proj.proj_dir_changed.connect(self.sec_ingest.set_proj_dir)
        self.sec_proj.log_signal.connect(self.log)
        
        self.sec_ingest.log_signal.connect(self.log)
        self.sec_ingest.request_max_toggle.connect(lambda max_state: (
            self.sec_proj.set_expanded(not max_state),
            self.sec_launch.set_expanded(not max_state)
        ))
        
        self.sec_launch.log_signal.connect(self.log)

        scroll_layout.addWidget(self.sec_proj)
        scroll_layout.addWidget(self.sec_ingest)
        scroll_layout.addWidget(self.sec_launch)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab1_layout.addWidget(scroll_area)

        # Tab 2, 3 & 4 instances
        self.tab_cleanup = CleanupTab()
        self.tab_cleanup.log_signal.connect(self.log)
        
        self.tab_webgl = WebGLTab()
        self.tab_webgl.log_signal.connect(self.log)

        self.tab_showroom = ShowroomTab()
        self.tab_showroom.log_signal.connect(self.log)
        
        self.sec_proj.proj_dir_changed.connect(self.tab_cleanup.set_proj_dir)
        self.sec_proj.proj_dir_changed.connect(self.tab_webgl.set_proj_dir)
        self.sec_proj.proj_dir_changed.connect(self.tab_showroom.set_proj_dir)

        # Add to stack
        self.stacked_widget.addWidget(tab1_widget)
        self.stacked_widget.addWidget(self.tab_cleanup)
        self.stacked_widget.addWidget(self.tab_webgl)
        self.stacked_widget.addWidget(self.tab_showroom)
        
        self.main_splitter.addWidget(self.stacked_widget)

        # ----------------------------------------------------
        # 3. Bottom Log Console Dock
        # ----------------------------------------------------
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            QFrame {
                background-color: #15181f;
                border: 1px solid #232732;
                border-radius: 6px;
            }
        """)
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 8, 10, 8)
        log_layout.setSpacing(6)

        log_header = QHBoxLayout()
        self.lbl_log_title = QLabel("Console & Activity Log")
        self.lbl_log_title.setStyleSheet("font-size: 11.5px; font-weight: 600; color: #94a3b8;")

        self.btn_clear_log = QPushButton("Clear")
        self.btn_clear_log.setStyleSheet("padding: 2px 8px; font-size: 10.5px;")
        self.btn_clear_log.clicked.connect(lambda: self.log_console.clear())

        log_header.addWidget(self.lbl_log_title)
        log_header.addStretch()
        log_header.addWidget(self.btn_clear_log)
        log_layout.addLayout(log_header)

        self.log_console = AutoScrollTextBrowser()
        self.log_console.setMinimumHeight(100)
        self.log_console.setStyleSheet("""
            QTextBrowser {
                background-color: #0c0d11;
                border: 1px solid #1e222c;
                border-radius: 4px;
                color: #e2e8f0;
                font-family: Consolas, 'Cascadia Code', monospace;
                font-size: 11px;
                padding: 6px;
            }
        """)
        log_layout.addWidget(self.log_console)
        self.main_splitter.addWidget(log_frame)

        self.main_splitter.setSizes([620, 180])
        main_layout.addWidget(self.main_splitter)
        self.setCentralWidget(main_widget)
        
        self.log(f"[ READY ] Points & Reality 3DGS Controller {APP_VERSION} initialized.", level="success")

    def browse_preset_dir(self):
        saved_dir = self.settings.value("preset_dir", "")
        dir_path = QFileDialog.getExistingDirectory(self, "Select Preset Directory", saved_dir)
        if dir_path:
            self.settings.setValue("preset_dir", dir_path)
            self.load_presets()
            self.log(f"Preset directory set to: {dir_path}", "info")

    def load_presets(self):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        self.combo_preset.blockSignals(True)
        self.combo_preset.clear()
        self.combo_preset.addItem(t.get("preset_default", "--- Select Preset ---"))
        
        preset_dir = self.settings.value("preset_dir", "")
        if not preset_dir:
            preset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "presets")
            os.makedirs(preset_dir, exist_ok=True)
            self.settings.setValue("preset_dir", preset_dir)
        
        if preset_dir and os.path.exists(preset_dir):
            for f in os.listdir(preset_dir):
                if f.endswith(".json"):
                    self.combo_preset.addItem(f[:-5])
                    
        self.combo_preset.blockSignals(False)

    def save_preset(self):
        preset_dir = self.settings.value("preset_dir", "")
        if not preset_dir or not os.path.exists(preset_dir):
            preset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "presets")
            os.makedirs(preset_dir, exist_ok=True)
            self.settings.setValue("preset_dir", preset_dir)

        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        name, ok = QInputDialog.getText(self, t.get("preset_prompt_title", "Save Preset"), t.get("preset_prompt_msg", "Enter Preset Name:"))
        if ok and name.strip():
            name = name.strip()
            data = {
                "ingest": self.sec_ingest.get_preset_data(),
                "launcher": self.sec_launch.get_preset_data()
            }
            filepath = os.path.join(preset_dir, f"{name}.json")
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                self.load_presets()
                self.combo_preset.setCurrentText(name)
                self.log(f"Preset '{name}.json' saved successfully.", "success")
            except Exception as e:
                self.log(f"[ERROR] Failed to save preset: {e}", "error")

    def apply_preset(self):
        name = self.combo_preset.currentText()
        preset_dir = self.settings.value("preset_dir", "")
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        
        if name and name != t.get("preset_default") and preset_dir:
            filepath = os.path.join(preset_dir, f"{name}.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if "ingest" in data: self.sec_ingest.set_preset_data(data["ingest"])
                    if "launcher" in data: self.sec_launch.set_preset_data(data["launcher"])
                    self.log(f"Preset '{name}' applied.", "info")
                except Exception as e:
                    self.log(f"[ERROR] Failed to load preset: {e}", "error")

    def delete_preset(self):
        name = self.combo_preset.currentText()
        preset_dir = self.settings.value("preset_dir", "")
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["EN"])
        
        if name and name != t.get("preset_default") and preset_dir:
            filepath = os.path.join(preset_dir, f"{name}.json")
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.load_presets()
                    self.log(f"Preset '{name}.json' deleted.", "warning")
                except Exception as e:
                    self.log(f"[ERROR] Failed to delete preset: {e}", "error")

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "KO" else "KO"
        self.settings.setValue("ui_language", self.current_lang)
        self.apply_language(self.current_lang)
        self.log(f"UI language changed to: {self.current_lang}", level="info")

    def apply_language(self, lang):
        t = TRANSLATIONS.get(lang, TRANSLATIONS["EN"])
        self.btn_lang.setText(lang)
        
        t_capture = t.get("tab_capture", "Capture & Ingest")
        t_cleanup = t.get("tab_cleanup", "Splat Cleanup")
        t_webgl = t.get("tab_webgl", "WebGL Build")
        t_showroom = t.get("tab_showroom", "Cloud Showroom")
        
        self.btn_tab_capture.setText(t_capture.replace("&", "&&") if "&&" not in t_capture else t_capture)
        self.btn_tab_cleanup.setText(t_cleanup.replace("&", "&&") if "&&" not in t_cleanup else t_cleanup)
        self.btn_tab_webgl.setText(t_webgl.replace("&", "&&") if "&&" not in t_webgl else t_webgl)
        self.btn_tab_showroom.setText(t_showroom.replace("&", "&&") if "&&" not in t_showroom else t_showroom)
        
        self.lbl_log_title.setText(t.get('log_title', 'Console & Activity Log'))
        self.btn_clear_log.setText(t.get("btn_clear_log", "Clear"))
        self.lbl_preset.setText(t.get("lbl_preset", "Preset:"))
        self.btn_preset_browse.setText(t.get("btn_preset_browse", "Folder"))
        self.btn_preset_save.setText(t.get("btn_preset_save", "Save"))
        self.btn_preset_del.setText(t.get("btn_preset_del", "Delete"))
        
        if self.combo_preset.currentIndex() == 0:
            self.combo_preset.setItemText(0, t.get("preset_default", "--- Select Preset ---"))
        
        self.sec_proj.update_language(t)
        self.sec_ingest.update_language(t)
        self.sec_launch.update_language(t)
        if hasattr(self, 'tab_cleanup'):
            self.tab_cleanup.update_language(t)
        if hasattr(self, 'tab_webgl'):
            self.tab_webgl.update_language(t)
        if hasattr(self, 'tab_showroom'):
            self.tab_showroom.update_language(t)

    def _on_tab_changed(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if 0 <= index < len(self.tab_buttons):
            self.tab_buttons[index].setChecked(True)
        if index == 1 and hasattr(self, 'tab_cleanup'):
            self.tab_cleanup.scan_exported_splats(silent=True)
        elif index == 2 and hasattr(self, 'tab_webgl'):
            self.tab_webgl.scan_project_models()

    def log(self, text, level="info"):
        colors = {
            "error": "#f87171",
            "warning": "#fbbf24",
            "success": "#34d399",
            "info": "#94a3b8"
        }
        c = colors.get(level.lower(), "#94a3b8")
        time_str = time.strftime("%H:%M:%S")
        formatted = f'<span style="color: #64748b;">[{time_str}]</span> <span style="color: {c}; font-family: Consolas;">{text.replace(chr(10), "<br>")}</span>'
        self.log_console.append(formatted)
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

# Backward compatibility alias
SplatialController = PointsAndRealityController