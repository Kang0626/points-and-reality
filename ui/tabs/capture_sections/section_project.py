# ui/tabs/capture_sections/section_project.py
import os
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFileDialog, QInputDialog, QMessageBox, QFrame)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from ui.ui_components import ModernStepCard, StatusPill
from config import PROJECT_SUBFOLDERS
from utils import create_project_structure

class ProjectConfigWidget(ModernStepCard):
    log_signal = pyqtSignal(str, str)
    proj_dir_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__(step_num="", title="Project Setup", subtitle="Select or create project workspace")
        self.init_ui()

    def init_ui(self):
        self.status_pill = StatusPill("No Project", "idle")
        self.add_header_action(self.status_pill)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        self.lbl_proj = QLabel("Project Folder:")
        self.lbl_proj.setStyleSheet("font-weight: 600; color: #cbd5e1;")

        self.input_proj_dir = QLineEdit()
        self.input_proj_dir.setPlaceholderText("Select or create a project directory...")
        self.input_proj_dir.setStyleSheet("background-color: #141619; border: 1px solid #333842; font-family: Consolas, monospace; font-size: 11px;")
        self.input_proj_dir.editingFinished.connect(self.on_proj_dir_edited)
        
        self.btn_new_proj = QPushButton("New Project")
        self.btn_new_proj.setObjectName("PrimaryBtn")
        self.btn_new_proj.clicked.connect(self.create_new_project)

        self.btn_browse_proj = QPushButton("Browse...")
        self.btn_browse_proj.clicked.connect(self.browse_project)

        self.btn_open_proj = QPushButton("Open Folder")
        self.btn_open_proj.clicked.connect(self.open_project_folder)
        
        content_layout.addWidget(self.lbl_proj)
        content_layout.addWidget(self.input_proj_dir, 1)
        content_layout.addWidget(self.btn_new_proj)
        content_layout.addWidget(self.btn_browse_proj)
        content_layout.addWidget(self.btn_open_proj)

        self.setContentLayout(content_layout)

    def get_proj_dir(self):
        return self.input_proj_dir.text().strip()

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
        # From ui/tabs/capture_sections/section_project.py -> 5 levels up to Points & Reality parent root
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

    def on_proj_dir_edited(self):
        directory = self.get_proj_dir()
        if directory and os.path.exists(directory):
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
            self.input_proj_dir.setText(directory)
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
            self.input_proj_dir.setText(target_dir)
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
        self.input_proj_dir.setPlaceholderText(t.get("placeholder_project", "Select or enter project directory path..."))
        self.btn_new_proj.setText(t.get("btn_new_proj", "New Project"))
        self.btn_browse_proj.setText(t.get("btn_browse_proj", "Browse..."))
        self.btn_open_proj.setText(t.get("btn_open_proj", "Open Folder"))