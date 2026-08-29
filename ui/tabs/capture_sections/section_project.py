# ui/tabs/capture_sections/section_project.py
import os
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, 
                             QPushButton, QFileDialog, QInputDialog, QMessageBox, QFrame)
from PyQt5.QtCore import pyqtSignal, QTimer, QSettings, Qt
from ui.ui_components import ModernStepCard, StatusPill
from config import PROJECT_SUBFOLDERS
from utils import create_project_structure

class ProjectConfigWidget(ModernStepCard):
    log_signal = pyqtSignal(str, str)
    proj_dir_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__(step_num="", title="Project Setup", subtitle="Set project workspace directory and automated pipeline folders")
        self.settings = QSettings("PointsAndReality", "3DGSController")
        self.init_ui()

    def init_ui(self):
        self.status_pill = StatusPill("No Project", "idle")
        self.add_header_action(self.status_pill)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        self.lbl_proj = QLabel("Project Directory:")
        self.lbl_proj.setStyleSheet("font-weight: 600; color: #cbd5e1;")

        # Editable Combobox for Project Directory with max 5 Recent History items
        self.combo_proj_dir = QComboBox()
        self.combo_proj_dir.setEditable(True)
        self.combo_proj_dir.setInsertPolicy(QComboBox.NoInsert)
        self.combo_proj_dir.setMinimumHeight(28)
        self.combo_proj_dir.setStyleSheet("""
            QComboBox {
                background-color: #0b0c0f;
                border: 1px solid #20232c;
                border-radius: 4px;
                min-height: 28px;
                padding: 1px 6px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11.5px;
                color: #e2e8f0;
            }
            QComboBox:focus {
                border: 1px solid #48566e;
            }
        """)
        
        line_edit = self.combo_proj_dir.lineEdit()
        if line_edit:
            line_edit.setPlaceholderText("Select or enter project directory path...")
            line_edit.setStyleSheet("background: transparent; border: none; font-family: Consolas, 'Courier New', monospace; font-size: 11.5px; color: #e2e8f0; min-height: 22px; padding: 0px 2px;")
            line_edit.editingFinished.connect(self.on_proj_dir_edited)

        self.combo_proj_dir.activated.connect(self.on_recent_selected)

        self.btn_new_proj = QPushButton("New Project")
        self.btn_new_proj.setObjectName("PrimaryBtn")
        self.btn_new_proj.clicked.connect(self.create_new_project)

        self.btn_browse_proj = QPushButton("Browse...")
        self.btn_browse_proj.clicked.connect(self.browse_project)

        self.btn_open_proj = QPushButton("Open Folder")
        self.btn_open_proj.clicked.connect(self.open_project_folder)
        
        content_layout.addWidget(self.lbl_proj)
        content_layout.addWidget(self.combo_proj_dir, 1)
        content_layout.addWidget(self.btn_new_proj)
        content_layout.addWidget(self.btn_browse_proj)
        content_layout.addWidget(self.btn_open_proj)

        self.setContentLayout(content_layout)
        self.load_recent_projects()

    def get_proj_dir(self):
        return self.combo_proj_dir.currentText().strip()

    def _debounce_btn(self):
        btn = self.sender()
        if btn:
            btn.setEnabled(False)
            QTimer.singleShot(1000, lambda: btn.setEnabled(True))

    def _get_default_works_dir(self):
        saved = self.get_proj_dir()
        if saved and os.path.exists(saved):
            return saved
        # Resolve 'Works' folder (D:\Points & Reality\Works)
        current_file = os.path.abspath(__file__)
        parent_root = current_file
        for _ in range(5):
            parent_root = os.path.dirname(parent_root)
        works_dir = os.path.normpath(os.path.join(parent_root, "Works"))
        if not os.path.exists(works_dir):
            try:
                os.makedirs(works_dir, exist_ok=True)
            except Exception:
                pass
        if os.path.exists(works_dir):
            return works_dir
        return ""

    def load_recent_projects(self):
        """Load up to 5 recent projects from QSettings."""
        raw_list = self.settings.value("recent_projects", [])
        if isinstance(raw_list, str):
            raw_list = [raw_list] if raw_list else []
        elif not isinstance(raw_list, list):
            raw_list = []

        valid_list = []
        for p in raw_list:
            norm = os.path.normpath(str(p).strip())
            if norm and os.path.exists(norm) and norm not in valid_list:
                valid_list.append(norm)
            if len(valid_list) >= 5:
                break

        self.combo_proj_dir.blockSignals(True)
        self.combo_proj_dir.clear()
        for p in valid_list:
            self.combo_proj_dir.addItem(p)

        last_dir = self.settings.value("last_project_dir", "")
        if last_dir and os.path.exists(last_dir):
            idx = self.combo_proj_dir.findText(last_dir)
            if idx >= 0:
                self.combo_proj_dir.setCurrentIndex(idx)
            else:
                self.combo_proj_dir.setEditText(last_dir)
            proj_name = os.path.basename(os.path.normpath(last_dir))
            self.status_pill.set_status(f"Active: {proj_name}", "success")
            self.proj_dir_changed.emit(last_dir)
        elif valid_list:
            self.combo_proj_dir.setCurrentIndex(0)
            proj_name = os.path.basename(os.path.normpath(valid_list[0]))
            self.status_pill.set_status(f"Active: {proj_name}", "success")
            self.proj_dir_changed.emit(valid_list[0])
        else:
            self.status_pill.set_status("No Project", "idle")

        self.combo_proj_dir.blockSignals(False)

    def add_recent_project(self, directory):
        """Add a directory to recent projects list (max 5 items) and persist to QSettings."""
        if not directory or not os.path.exists(directory):
            return

        norm_dir = os.path.normpath(directory)
        raw_list = self.settings.value("recent_projects", [])
        if isinstance(raw_list, str):
            raw_list = [raw_list] if raw_list else []
        elif not isinstance(raw_list, list):
            raw_list = []

        # Remove duplicate if already present
        recent_list = [os.path.normpath(str(p)) for p in raw_list if os.path.normpath(str(p)) != norm_dir and os.path.exists(str(p))]
        recent_list.insert(0, norm_dir)
        recent_list = recent_list[:5]

        self.settings.setValue("recent_projects", recent_list)
        self.settings.setValue("last_project_dir", norm_dir)

        # Refresh combobox
        self.combo_proj_dir.blockSignals(True)
        self.combo_proj_dir.clear()
        for p in recent_list:
            self.combo_proj_dir.addItem(p)
        self.combo_proj_dir.setCurrentIndex(0)
        self.combo_proj_dir.blockSignals(False)

    def on_recent_selected(self, index):
        directory = self.combo_proj_dir.itemText(index).strip()
        if directory and os.path.exists(directory):
            self.add_recent_project(directory)
            proj_name = os.path.basename(os.path.normpath(directory))
            self.status_pill.set_status(f"Active: {proj_name}", "success")
            self.log_signal.emit(f"Switched to recent project: {directory}", "info")
            self.proj_dir_changed.emit(directory)

    def on_proj_dir_edited(self):
        directory = self.get_proj_dir()
        if directory and os.path.exists(directory):
            self.add_recent_project(directory)
            proj_name = os.path.basename(os.path.normpath(directory))
            self.status_pill.set_status(f"Active: {proj_name}", "success")
            self.proj_dir_changed.emit(directory)
        elif not directory:
            self.status_pill.set_status("No Project", "idle")

    def browse_project(self):
        self._debounce_btn()
        default_dir = self._get_default_works_dir()
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory", default_dir)
        if directory:
            self.add_recent_project(directory)
            proj_name = os.path.basename(os.path.normpath(directory))
            self.status_pill.set_status(f"Active: {proj_name}", "success")
            self.log_signal.emit(f"Project directory set: {directory}", "info")
            self.proj_dir_changed.emit(directory)

    def create_new_project(self):
        self._debounce_btn()
        default_dir = self._get_default_works_dir()
        base_dir = QFileDialog.getExistingDirectory(self, "Select Parent Workspace Directory", default_dir)
        if not base_dir: return
        
        default_name = "MyScan_01"
        while True:
            proj_name, ok = QInputDialog.getText(self, "New Project", "Enter Project Name:", text=default_name)
            if not ok or not proj_name.strip(): return
            
            target_dir = os.path.join(base_dir, proj_name.strip())
            if os.path.exists(target_dir):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Directory Already Exists")
                msg_box.setText(f"Folder '{proj_name}' already exists.")
                btn_overwrite = msg_box.addButton("Use / Overwrite", QMessageBox.AcceptRole)
                btn_rename = msg_box.addButton("Rename", QMessageBox.ActionRole)
                msg_box.addButton("Cancel", QMessageBox.RejectRole)
                msg_box.exec_()
                if msg_box.clickedButton() == btn_overwrite: break
                elif msg_box.clickedButton() == btn_rename:
                    default_name = f"{proj_name}_new"
                    continue
                else: return
            else: break
            
        try:
            os.makedirs(target_dir, exist_ok=True)
            create_project_structure(target_dir, PROJECT_SUBFOLDERS)
            self.add_recent_project(target_dir)
            self.status_pill.set_status(f"Active: {proj_name.strip()}", "success")
            self.log_signal.emit(f"[SUCCESS] Project initialized:\n➔ {target_dir}", "success")
            self.proj_dir_changed.emit(target_dir)
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed to initialize project: {str(e)}", "error")

    def open_project_folder(self):
        self._debounce_btn()
        target_dir = self.get_proj_dir()
        if not target_dir or not os.path.exists(target_dir):
            self.log_signal.emit("[ERROR] Project directory does not exist.", "error")
            return
        os.startfile(target_dir)

    def update_language(self, t):
        self.setTitle(t.get("group_project", "Project Setup"), t.get("sub_project", "Set project workspace directory and automated pipeline folders"))
        self.lbl_proj.setText(t.get("lbl_project_dir", "Project Directory:"))
        line_edit = self.combo_proj_dir.lineEdit()
        if line_edit:
            line_edit.setPlaceholderText(t.get("placeholder_project", "Select or enter project directory path..."))
        self.btn_new_proj.setText(t.get("btn_new_proj", "New Project"))
        self.btn_browse_proj.setText(t.get("btn_browse_proj", "Browse..."))
        self.btn_open_proj.setText(t.get("btn_open_proj", "Open Folder"))