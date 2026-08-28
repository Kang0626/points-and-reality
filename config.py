APP_VERSION = "v2.224"

# Points & Reality 표준 프로젝트 서브폴더 구조
PROJECT_SUBFOLDERS = [
    "00_raw_footage",
    "01_extracted_frames",
    "02_camera_alignment",
    "03_splats_exports",
    "04_splats_cleaned",
    "05_web_build"
]

# Points & Reality 전문 스튜디오 다크 테마 (Pro Studio Neutral Dark QSS)
DARK_THEME_CSS = """
QMainWindow, QWidget { 
    background-color: #101216; 
    color: #e2e8f0; 
    font-family: 'Segoe UI', 'Pretendard', -apple-system, BlinkMacSystemFont, Arial, sans-serif; 
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #15181f;
    border: 1px solid #232732;
}

/* --- QTabWidget & QTabBar --- */
QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}

QTabBar::tab { 
    background-color: #171920; 
    color: #94a3b8; 
    padding: 6px 14px; 
    border: 1px solid #232732;
    border-radius: 4px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 11.5px;
}

QTabBar::tab:hover { 
    background-color: #20242e; 
    color: #f1f5f9; 
    border-color: #3b4254;
}

QTabBar::tab:selected { 
    background-color: #2563eb; 
    color: #ffffff; 
    border: 1px solid #3b82f6;
}

/* --- Standard Buttons --- */
QPushButton { 
    background-color: #1c1f28; 
    border: 1px solid #2d3240; 
    padding: 6px 13px; 
    border-radius: 4px; 
    color: #e2e8f0; 
    font-weight: 600;
    font-size: 11.5px;
}

QPushButton:hover { 
    background-color: #262a37; 
    border-color: #434a5d; 
    color: #ffffff;
}

QPushButton:pressed { 
    background-color: #161820; 
    border-color: #2563eb;
    color: #ffffff; 
}

QPushButton:disabled {
    background-color: #121419;
    border-color: #1e2129;
    color: #4b5563;
}

/* --- Primary Action Buttons (Studio Clean Blue) --- */
QPushButton#PrimaryBtn, QPushButton[objectName="PrimaryBtn"] {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#PrimaryBtn:hover, QPushButton[objectName="PrimaryBtn"]:hover {
    background-color: #1d4ed8;
    border-color: #60a5fa;
    color: #ffffff;
}
QPushButton#PrimaryBtn:pressed, QPushButton[objectName="PrimaryBtn"]:pressed {
    background-color: #1e40af;
    color: #ffffff;
}

/* --- Success Action Buttons (Studio Clean Emerald) --- */
QPushButton#SuccessBtn, QPushButton[objectName="SuccessBtn"] {
    background-color: #059669;
    border: 1px solid #10b981;
    color: #ffffff;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#SuccessBtn:hover, QPushButton[objectName="SuccessBtn"]:hover {
    background-color: #047857;
    border-color: #34d399;
    color: #ffffff;
}
QPushButton#SuccessBtn:pressed, QPushButton[objectName="SuccessBtn"]:pressed {
    background-color: #065f46;
    color: #ffffff;
}

/* --- Danger Action Buttons (Studio Clean Red) --- */
QPushButton#DangerBtn, QPushButton[objectName="DangerBtn"] {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#DangerBtn:hover, QPushButton[objectName="DangerBtn"]:hover {
    background-color: #b91c1c;
    border-color: #f87171;
    color: #ffffff;
}
QPushButton#DangerBtn:pressed, QPushButton[objectName="DangerBtn"]:pressed {
    background-color: #991b1b;
    color: #ffffff;
}

/* --- Inputs & Combos --- */
QLineEdit, QComboBox, QSpinBox { 
    background-color: #0c0d11; 
    border: 1px solid #232732; 
    padding: 5px 8px; 
    color: #f1f5f9; 
    border-radius: 4px;
    font-size: 11.5px;
}

QLineEdit:focus, QComboBox:focus { 
    border: 1px solid #3b82f6; 
    background-color: #101217;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #232732;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox QAbstractItemView {
    background-color: #171920;
    border: 1px solid #2d3240;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    color: #e2e8f0;
    padding: 4px;
    border-radius: 4px;
}

/* --- Tables --- */
QTableWidget { 
    background-color: #0c0d11; 
    alternate-background-color: #111318;
    border: 1px solid #1e222c; 
    border-radius: 4px;
    color: #e2e8f0;
    gridline-color: #171920; 
    selection-background-color: #1e293b;
    selection-color: #ffffff;
    font-size: 11px;
    outline: none;
}

QHeaderView::section { 
    background-color: #15181f; 
    padding: 6px 8px; 
    border: none;
    border-bottom: 1px solid #232732;
    border-right: 1px solid #1a1d26;
    color: #94a3b8;
    font-weight: 600;
    font-size: 11px;
}

QHeaderView::section:hover {
    background-color: #1c202a;
    color: #f1f5f9;
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
    width: 15px;
    height: 15px;
    background-color: #151820;
    border: 1px solid #374151;
    border-radius: 3px;
    outline: none;
}
QCheckBox::indicator:hover {
    border: 1px solid #6b7280;
    background-color: #1c202a;
}
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
}
QCheckBox::indicator:checked:hover {
    background-color: #1d4ed8;
    border: 1px solid #60a5fa;
}

/* --- Progress Bar --- */
QProgressBar { 
    border: 1px solid #232732; 
    border-radius: 4px; 
    text-align: center; 
    color: #ffffff; 
    background-color: #0c0d11;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk { 
    background-color: #2563eb; 
    border-radius: 3px;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    background: #0c0d11;
    width: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #282c38;
    min-height: 25px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #3b4254;
}
QScrollBar:horizontal {
    background: #0c0d11;
    height: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #282c38;
    min-width: 25px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #3b4254;
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