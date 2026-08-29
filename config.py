APP_VERSION = "v2.225"

# Points & Reality 표준 프로젝트 서브폴더 구조
PROJECT_SUBFOLDERS = [
    "00_raw_footage",
    "01_extracted_frames",
    "02_camera_alignment",
    "03_splats_exports",
    "04_splats_cleaned",
    "05_web_build"
]

# Points & Reality 전문 스튜디오 다크 테마 (Low-Saturation Neutral Dark QSS)
DARK_THEME_CSS = """
QMainWindow, QWidget { 
    background-color: #101215; 
    color: #cbd5e1; 
    font-family: 'Segoe UI', 'Pretendard', -apple-system, BlinkMacSystemFont, Arial, sans-serif; 
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #14161c;
    border: 1px solid #20232b;
}

/* --- QTabWidget & QTabBar --- */
QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}

QTabBar::tab { 
    background-color: #15171d; 
    color: #8892b0; 
    padding: 6px 14px; 
    border: 1px solid #22252e;
    border-radius: 4px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 11.5px;
}

QTabBar::tab:hover { 
    background-color: #1e2129; 
    color: #e2e8f0; 
    border-color: #323846;
}

QTabBar::tab:selected { 
    background-color: #272d38; 
    color: #ffffff; 
    border: 1px solid #3c4656;
}

/* --- Standard Buttons --- */
QPushButton { 
    background-color: #191b22; 
    border: 1px solid #282c37; 
    padding: 6px 13px; 
    border-radius: 4px; 
    color: #cbd5e1; 
    font-weight: 500;
    font-size: 11.5px;
}

QPushButton:hover { 
    background-color: #232732; 
    border-color: #3b4254; 
    color: #ffffff;
}

QPushButton:pressed { 
    background-color: #14161c; 
    border-color: #282c37;
    color: #94a3b8; 
}

QPushButton:disabled {
    background-color: #121318;
    border-color: #1a1c22;
    color: #475569;
}

/* --- Primary Action Buttons (Low-Saturation Studio Slate Navy) --- */
QPushButton#PrimaryBtn, QPushButton[objectName="PrimaryBtn"] {
    background-color: #283344;
    border: 1px solid #3d4f68;
    color: #f1f5f9;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#PrimaryBtn:hover, QPushButton[objectName="PrimaryBtn"]:hover {
    background-color: #324056;
    border-color: #51698a;
    color: #ffffff;
}
QPushButton#PrimaryBtn:pressed, QPushButton[objectName="PrimaryBtn"]:pressed {
    background-color: #1e2735;
    border-color: #313f53;
    color: #cbd5e1;
}

/* --- Success Action Buttons (Low-Saturation Studio Sage Olive) --- */
QPushButton#SuccessBtn, QPushButton[objectName="SuccessBtn"] {
    background-color: #24352c;
    border: 1px solid #375344;
    color: #e6f4ea;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#SuccessBtn:hover, QPushButton[objectName="SuccessBtn"]:hover {
    background-color: #2d4237;
    border-color: #466957;
    color: #ffffff;
}
QPushButton#SuccessBtn:pressed, QPushButton[objectName="SuccessBtn"]:pressed {
    background-color: #1b2821;
    border-color: #2b3f34;
    color: #b7e1cd;
}

/* --- Danger Action Buttons (Low-Saturation Studio Muted Crimson) --- */
QPushButton#DangerBtn, QPushButton[objectName="DangerBtn"] {
    background-color: #3a2224;
    border: 1px solid #573336;
    color: #fce8e8;
    font-weight: 600;
    font-size: 11.5px;
    padding: 6px 14px;
}
QPushButton#DangerBtn:hover, QPushButton[objectName="DangerBtn"]:hover {
    background-color: #492b2d;
    border-color: #704246;
    color: #ffffff;
}
QPushButton#DangerBtn:pressed, QPushButton[objectName="DangerBtn"]:pressed {
    background-color: #2c1a1b;
    border-color: #432729;
    color: #f8b4b4;
}

/* --- Inputs & Combos --- */
QLineEdit, QComboBox, QSpinBox { 
    background-color: #0b0c0f; 
    border: 1px solid #20232c; 
    padding: 5px 8px; 
    color: #e2e8f0; 
    border-radius: 4px;
    font-size: 11.5px;
}

QLineEdit:focus, QComboBox:focus { 
    border: 1px solid #48566e; 
    background-color: #0f1015;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #20232c;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: transparent;
}

QComboBox::down-arrow {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%238892b0' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'/></svg>");
    width: 10px;
    height: 10px;
}

QComboBox::down-arrow:hover {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%23e2e8f0' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'/></svg>");
}

QComboBox QAbstractItemView {
    background-color: #14161c;
    border: 1px solid #282c37;
    selection-background-color: #283344;
    selection-color: #ffffff;
    color: #cbd5e1;
    padding: 4px;
    border-radius: 4px;
}

/* --- Tables --- */
QTableWidget { 
    background-color: #0b0c0f; 
    alternate-background-color: #101216;
    border: 1px solid #1c1e25; 
    border-radius: 4px;
    color: #cbd5e1;
    gridline-color: #15171d; 
    selection-background-color: #1e2430;
    selection-color: #ffffff;
    font-size: 11px;
    outline: none;
}

QHeaderView::section { 
    background-color: #14161c; 
    padding: 6px 8px; 
    border: none;
    border-bottom: 1px solid #20232c;
    border-right: 1px solid #181a21;
    color: #8892b0;
    font-weight: 600;
    font-size: 11px;
}

QHeaderView::section:hover {
    background-color: #1a1d25;
    color: #e2e8f0;
}

/* --- Unified CheckBoxes --- */
QCheckBox {
    margin: 0px;
    padding: 0px;
    background-color: transparent;
    outline: none;
    color: #cbd5e1;
}
QCheckBox:focus {
    outline: none;
    border: none;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    background-color: #14161c;
    border: 1px solid #333846;
    border-radius: 3px;
    outline: none;
}
QCheckBox::indicator:hover {
    border: 1px solid #4f586d;
    background-color: #1a1d25;
}
QCheckBox::indicator:checked {
    background-color: #283344;
    border: 1px solid #3d4f68;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
}
QCheckBox::indicator:checked:hover {
    background-color: #324056;
    border: 1px solid #51698a;
}

/* --- Progress Bar --- */
QProgressBar { 
    border: 1px solid #20232c; 
    border-radius: 4px; 
    text-align: center; 
    color: #e2e8f0; 
    background-color: #0b0c0f;
    font-weight: 600;
    font-size: 11px;
}

QProgressBar::chunk { 
    background-color: #283344; 
    border-radius: 3px;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    background: #0b0c0f;
    width: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #232630;
    min-height: 25px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #333846;
}
QScrollBar:horizontal {
    background: #0b0c0f;
    height: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #232630;
    min-width: 25px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #333846;
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