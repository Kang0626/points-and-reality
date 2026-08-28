APP_VERSION = "v2.223"

# Points & Reality 표준 프로젝트 서브폴더 구조
PROJECT_SUBFOLDERS = [
    "00_raw_footage",
    "01_extracted_frames",
    "02_camera_alignment",
    "03_splats_exports",
    "04_splats_cleaned",
    "05_web_build"
]

# Points & Reality 모던 프리미엄 다크 테마 QSS
DARK_THEME_CSS = """
QMainWindow, QWidget { 
    background-color: #131417; 
    color: #e2e8f0; 
    font-family: 'Segoe UI', 'Pretendard', -apple-system, BlinkMacSystemFont, Arial, sans-serif; 
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #141619;
    border: 1px solid #2d3139;
}

/* --- QTabWidget & QTabBar --- */
QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}

QTabBar::tab { 
    background-color: #1e2025; 
    color: #94a3b8; 
    padding: 5px 10px; 
    border: 1px solid #2d3139;
    border-radius: 6px;
    margin-right: 3px;
    font-weight: bold;
    font-size: 11px;
}

QTabBar::tab:hover { 
    background-color: #282c35; 
    color: #f1f5f9; 
    border-color: #38bdf8;
}

QTabBar::tab:selected { 
    background-color: #0284c7; 
    color: #ffffff; 
    border: 1px solid #38bdf8;
}

/* --- Buttons --- */
QPushButton { 
    background-color: #1e222b; 
    border: 1px solid #333842; 
    padding: 6px 14px; 
    border-radius: 5px; 
    color: #e2e8f0;
    font-weight: 600;
    font-size: 11.5px;
}

QPushButton:hover { 
    background-color: #2b313e; 
    border: 1px solid #38bdf8; 
    color: #ffffff;
}

QPushButton:pressed { 
    background-color: #0284c7; 
    border-color: #38bdf8;
    color: #ffffff; 
}

QPushButton:disabled {
    background-color: #14161a;
    border-color: #24272e;
    color: #475569;
}

/* --- Primary / Accent Buttons (Vibrant Sky Blue) --- */
QPushButton#PrimaryBtn, QPushButton[objectName="PrimaryBtn"] {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
    color: #ffffff;
    font-weight: bold;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#PrimaryBtn:hover, QPushButton[objectName="PrimaryBtn"]:hover {
    background-color: #0ea5e9;
    border: 1px solid #bae6fd;
    color: #ffffff;
}
QPushButton#PrimaryBtn:pressed, QPushButton[objectName="PrimaryBtn"]:pressed {
    background-color: #0369a1;
    border-color: #38bdf8;
    color: #ffffff;
}

/* --- Success Action Buttons (Vibrant Emerald Green) --- */
QPushButton#SuccessBtn, QPushButton[objectName="SuccessBtn"] {
    background-color: #059669;
    border: 1px solid #34d399;
    color: #ffffff;
    font-weight: bold;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#SuccessBtn:hover, QPushButton[objectName="SuccessBtn"]:hover {
    background-color: #10b981;
    border: 1px solid #a7f3d0;
    color: #ffffff;
}
QPushButton#SuccessBtn:pressed, QPushButton[objectName="SuccessBtn"]:pressed {
    background-color: #047857;
    border-color: #34d399;
    color: #ffffff;
}

/* --- Danger Action Buttons (Vibrant Rose Red) --- */
QPushButton#DangerBtn, QPushButton[objectName="DangerBtn"] {
    background-color: #dc2626;
    border: 1px solid #f87171;
    color: #ffffff;
    font-weight: bold;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#DangerBtn:hover, QPushButton[objectName="DangerBtn"]:hover {
    background-color: #ef4444;
    border: 1px solid #fecaca;
    color: #ffffff;
}
QPushButton#DangerBtn:pressed, QPushButton[objectName="DangerBtn"]:pressed {
    background-color: #b91c1c;
    color: #ffffff;
}

/* --- Inputs & Combos --- */
QLineEdit, QComboBox, QSpinBox { 
    background-color: #0f1013; 
    border: 1px solid #2d3139; 
    padding: 5px 8px; 
    color: #f1f5f9; 
    border-radius: 5px;
    font-size: 11px;
}

QLineEdit:focus, QComboBox:focus { 
    border: 1px solid #38bdf8; 
    background-color: #14161a;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #2d3139;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}

QComboBox QAbstractItemView {
    background-color: #1a1c21;
    border: 1px solid #38bdf8;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    color: #e2e8f0;
    padding: 4px;
    border-radius: 4px;
}

/* --- Tables --- */
QTableWidget { 
    background-color: #0f1013; 
    alternate-background-color: #14161a;
    border: 1px solid #24272e; 
    border-radius: 6px;
    color: #e2e8f0;
    gridline-color: #1e2025; 
    selection-background-color: #1e3a5f;
    selection-color: #ffffff;
    font-size: 11px;
    outline: none;
}

QHeaderView::section { 
    background-color: #1a1c21; 
    padding: 6px 8px; 
    border: none;
    border-bottom: 1px solid #2d3139;
    border-right: 1px solid #24272e;
    color: #94a3b8;
    font-weight: bold;
    font-size: 11px;
}

QHeaderView::section:hover {
    background-color: #242936;
    color: #38bdf8;
}

/* --- Unified CheckBoxes --- */
QCheckBox {
    margin: 0px;
    padding: 0px;
    background-color: transparent;
    outline: none;
    color: #e2e8f0;
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
    background-color: #242936;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
}
QCheckBox::indicator:checked:hover {
    background-color: #0369a1;
    border: 1px solid #7dd3fc;
}

/* --- Progress Bar --- */
QProgressBar { 
    border: 1px solid #2d3139; 
    border-radius: 5px; 
    text-align: center; 
    color: #ffffff; 
    background-color: #0f1013;
    font-weight: bold;
    font-size: 11px;
}

QProgressBar::chunk { 
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8); 
    border-radius: 4px;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    background: #0f1013;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #333842;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #0284c7;
}
QScrollBar:horizontal {
    background: #0f1013;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #333842;
    min-width: 25px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #0284c7;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    height: 0px;
    width: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""