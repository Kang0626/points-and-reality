# ui/tabs/tab_webgl.py
import os
import shutil
import json
import base64
import socket
import threading
import time
import subprocess
import http.server
import socketserver
import webbrowser
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QLineEdit, QFileDialog, QFrame, 
                             QProgressBar, QApplication, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QAbstractItemView, QCheckBox, QScrollArea,
                             QInputDialog, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from ui.ui_components import ModernStepCard, StatusPill, ElideLeftDelegate
from ui.tabs.dialog_web_publish import WebPublishManagerDialog

class VercelUploadThread(QThread):
    upload_progress = pyqtSignal(str)
    upload_success = pyqtSignal(str)
    upload_error = pyqtSignal(str)

    def __init__(self, src_web_dir, repo_dir):
        super().__init__()
        self.src_web_dir = os.path.normpath(src_web_dir)
        self.repo_dir = os.path.normpath(repo_dir)

    def run(self):
        try:
            self.upload_progress.emit("Syncing 05_web_build assets to repository...")
            target_web_dir = os.path.normpath(os.path.join(self.repo_dir, "05_web_build"))
            os.makedirs(target_web_dir, exist_ok=True)
            
            # If source directory is different from repo's 05_web_build, copy/sync files
            if os.path.abspath(self.src_web_dir) != os.path.abspath(target_web_dir):
                for item in os.listdir(self.src_web_dir):
                    s = os.path.join(self.src_web_dir, item)
                    d = os.path.join(target_web_dir, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d, ignore_errors=True)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)

            # Generate/update models.json manifest in target_web_dir
            html_files = [f for f in os.listdir(target_web_dir) if f.lower().endswith('.html')]
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(html_files),
                "models": []
            }
            for html_file in sorted(html_files):
                base_name = os.path.splitext(html_file)[0]
                manifest["models"].append({
                    "title": base_name,
                    "filename": html_file,
                    "path": f"05_web_build/{html_file}",
                    "is_index": (html_file.lower() == "index.html")
                })
            
            manifest_path = os.path.join(target_web_dir, "models.json")
            with open(manifest_path, 'w', encoding='utf-8') as mf:
                json.dump(manifest, mf, indent=2)

            self.upload_progress.emit(f"Prepared {len(html_files)} model(s). Staging Git files...")
            
            # Git add
            subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True, text=True, check=True)
            
            # Git commit
            commit_res = subprocess.run(
                ["git", "commit", "-m", f"deploy: Update 05_web_build models ({len(html_files)} items) for Vercel"],
                cwd=self.repo_dir, capture_output=True, text=True
            )
            
            # Git push
            self.upload_progress.emit("Pushing to GitHub (origin/main)...")
            push_res = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_dir, capture_output=True, text=True, check=True
            )
            
            self.upload_success.emit(f"Pushed {len(html_files)} WebGL model(s) to GitHub! Vercel is now building and deploying live.")
        except subprocess.CalledProcessError as cpe:
            err_msg = cpe.stderr.strip() if (cpe.stderr and cpe.stderr.strip()) else (cpe.stdout.strip() if cpe.stdout else str(cpe))
            self.upload_error.emit(f"Git operation failed: {err_msg}")
        except Exception as ex:
            self.upload_error.emit(f"Upload error: {str(ex)}")

class HTTPServerThread(QThread):
    server_started = pyqtSignal(int)
    server_stopped = pyqtSignal()
    server_error = pyqtSignal(str)

    def __init__(self, serve_dir, preferred_port=8080):
        super().__init__()
        self.serve_dir = os.path.normpath(serve_dir)
        self.preferred_port = preferred_port
        self.httpd = None
        self.port = preferred_port
        self.running = False

    def run(self):
        serve_dir = self.serve_dir

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=serve_dir, **kwargs)
            def log_message(self, format, *args):
                pass

        for port in range(self.preferred_port, self.preferred_port + 20):
            try:
                self.httpd = socketserver.TCPServer(("127.0.0.1", port), CustomHandler)
                self.port = port
                break
            except OSError:
                continue

        if not self.httpd:
            self.server_error.emit("Could not bind local HTTP server to any port.")
            return

        self.running = True
        self.server_started.emit(self.port)
        try:
            self.httpd.serve_forever()
        except Exception:
            pass
        finally:
            self.running = False
            self.server_stopped.emit()

    def stop(self):
        if self.httpd:
            threading.Thread(target=self.httpd.shutdown).start()
            self.running = False


def _detect_model_format(file_path):
    """Detect whether a file is .sog (ZIP/SuperSplat) or raw .ply"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
        if header[:2] == b'PK':
            return 'sog'
        elif header[:3] == b'ply':
            return 'ply'
        else:
            return os.path.splitext(file_path)[1].lstrip('.').lower()
    except Exception:
        return os.path.splitext(file_path)[1].lstrip('.').lower()


def _generate_watermark_html(text="Points & Reality", font_size_px=140, opacity_pct=6):
    """Generate clean giant repeating white watermark overlay with configurable size and opacity."""
    raw_text = (text.strip() if text else "") or "Points & Reality"
    opacity_val = max(0.01, min(1.0, float(opacity_pct) / 100.0))
    font_size_str = f"clamp({int(font_size_px * 0.75)}px, {font_size_px / 10:.1f}vw, {int(font_size_px * 1.35)}px)"
    gap_str = f"{int(font_size_px * 0.65)}px"
    row_gap_str = f"{int(font_size_px * 0.55)}px"
    offset_px = int(font_size_px * 1.1)

    rows_html = []
    # 12 staggered repeating rows spanning a 340vw x 340vh canvas centered on screen
    for i in range(12):
        offset = f"transform: translateX({offset_px}px);" if (i % 2 == 1) else ""
        row = (
            f'<div style="display:flex; justify-content:center; gap:{gap_str}; color:#ffffff; '
            f'font-size:{font_size_str}; font-weight:900; font-family:\'Arial Black\', \'Impact\', \'Montserrat\', -apple-system, sans-serif; '
            f'letter-spacing:-4px; text-transform:uppercase; white-space:nowrap; {offset}">'
            f'<span>{raw_text}</span><span>{raw_text}</span><span>{raw_text}</span><span>{raw_text}</span><span>{raw_text}</span><span>{raw_text}</span>'
            f'</div>'
        )
        rows_html.append(row)
    
    body = "\n        ".join(rows_html)
    return f'''
    <!-- Points & Reality Giant Repeating Watermark Overlay (Full Viewport Coverage, Centered Tiling) -->
    <div id="points-reality-watermark" style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:99990; pointer-events:none; overflow:hidden; user-select:none;">
        <div style="position:absolute; top:50%; left:50%; width:340vw; height:340vh; transform:translate(-50%, -50%) rotate(-24deg); opacity:{opacity_val:.3f}; display:flex; flex-direction:column; justify-content:center; gap:{row_gap_str}; align-items:center;">
        {body}
        </div>
    </div>'''


def _generate_ply_viewer_html(title, model_filename, cam_pos=[0, 1.2, 3.8], cam_target=[0, 0, 0], cam_fov=50, is_preview=False, enable_watermark=False, watermark_text="", watermark_size=140, watermark_opacity=6):
    """Generate a complete 100% offline 3DGS PLY viewer HTML with custom initial camera view."""
    copy_cam_btn_html = '<button class="hud-btn" id="btn-copy-cam">📷 현재 시점 복사 (Copy View)</button>' if is_preview else ''
    copy_cam_js = f'''
            const btnCopyCam = document.getElementById('btn-copy-cam');
            if (btnCopyCam) {{
                btnCopyCam.addEventListener('click', () => {{
                    if (viewer.camera && viewer.controls) {{
                        const pos = viewer.camera.position;
                        const tgt = viewer.controls.target;
                        const camData = {{
                            position: [parseFloat(pos.x.toFixed(3)), parseFloat(pos.y.toFixed(3)), parseFloat(pos.z.toFixed(3))],
                            target: [parseFloat(tgt.x.toFixed(3)), parseFloat(tgt.y.toFixed(3)), parseFloat(tgt.z.toFixed(3))],
                            fov: {cam_fov}
                        }};
                        navigator.clipboard.writeText(JSON.stringify(camData));
                        btnCopyCam.innerText = '✅ 복사 완료: [' + camData.position.join(', ') + ']';
                        setTimeout(() => btnCopyCam.innerText = '📷 현재 시점 복사 (Copy View)', 3000);
                    }}
                }});
            }}
    ''' if is_preview else ''

    watermark_html = _generate_watermark_html(watermark_text, font_size_px=watermark_size, opacity_pct=watermark_opacity) if (not is_preview and enable_watermark) else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{
            width: 100%; height: 100%; overflow: hidden;
            background: #0d0f12; color: #e2e8f0;
            font-family: 'Segoe UI', -apple-system, sans-serif;
        }}
        #hud-header {{
            position: fixed; top: 16px; left: 16px; z-index: 100;
            background: rgba(20,22,27,0.85); backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
            padding: 10px 18px; display: flex; align-items: center; gap: 14px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }}
        .brand {{ font-size: 14px; font-weight: 800; color: #38bdf8; }}
        .model-pill {{ font-size: 11px; background: rgba(56,189,248,0.15); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.3); padding: 3px 8px; border-radius: 6px; font-weight: 600; }}
        .fps-badge {{ font-size: 11px; color: #94a3b8; font-family: monospace; }}
        
        #hud-help {{
            position: fixed; top: 16px; right: 16px; z-index: 100;
            background: rgba(20,22,27,0.75); backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
            padding: 8px 14px; font-size: 11px; color: #94a3b8;
        }}
        #hud-help span {{ color: #e2e8f0; font-weight: 600; }}

        #hud-controls {{
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 100;
            background: rgba(20,22,27,0.85); backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.12); border-radius: 12px;
            padding: 6px 12px; display: flex; align-items: center; gap: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }}
        .hud-btn {{
            background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
            color: #f1f5f9; padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 600;
            cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; gap: 5px;
        }}
        .hud-btn:hover {{ background: #0284c7; border-color: #38bdf8; color: #fff; transform: translateY(-1px); }}
        .hud-btn.active {{ background: #0284c7; border-color: #38bdf8; color: #fff; }}

        #loading {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 200;
            background: radial-gradient(circle at center, #181b22, #0d0f12);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            transition: opacity 0.6s ease;
        }}
        #loading.done {{ opacity: 0; pointer-events: none; }}
        .spinner {{
            width: 48px; height: 48px;
            border: 4px solid rgba(56,189,248,0.2); border-top-color: #38bdf8;
            border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        #load-text {{ font-size: 14px; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }}
        .pbar-wrap {{ width: 220px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }}
        .pbar {{ width: 0%; height: 100%; background: linear-gradient(90deg, #0284c7, #38bdf8); transition: width 0.15s; }}
        
        #error-msg {{
            position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); z-index: 300;
            background: rgba(220,38,38,0.95); color: white; padding: 20px 30px; border-radius: 12px;
            font-size: 14px; max-width: 500px; text-align: center; display: none; line-height: 1.5;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8);
        }}
    </style>
</head>
<body>
    <div id="hud-header">
        <div class="brand">✨ Points & Reality 3DGS</div>
        <div class="model-pill">{model_filename}</div>
        <div class="fps-badge" id="lbl-fps">FPS: --</div>
    </div>
    
    <div id="hud-help">
        🖱️ <span>Left:</span> Orbit &nbsp;|&nbsp; 🖱️ <span>Right:</span> Pan &nbsp;|&nbsp; 🔍 <span>Wheel:</span> Zoom
    </div>

    <div id="hud-controls">
        {copy_cam_btn_html}
        <button class="hud-btn" id="btn-reset">🎥 Reset View</button>
        <button class="hud-btn" id="btn-orbit">🔄 Auto Orbit</button>
        <button class="hud-btn" id="btn-bg">🎨 Background</button>
        <button class="hud-btn" id="btn-fs">⛶ Fullscreen</button>
    </div>

    {watermark_html}

    <div id="loading">
        <div class="spinner"></div>
        <div id="load-text">Loading 3D Gaussian Splats...</div>
        <div class="pbar-wrap"><div class="pbar" id="pbar"></div></div>
    </div>
    
    <div id="error-msg"></div>

    <script type="importmap">
    {{
        "imports": {{
            "three": "./libs/three.module.js",
            "@mkkellogg/gaussian-splats-3d": "./libs/gaussian-splats-3d.module.min.js"
        }}
    }}
    </script>
    <script type="module">
        import * as GaussianSplats3D from '@mkkellogg/gaussian-splats-3d';
        import * as THREE from 'three';

        const loading = document.getElementById('loading');
        const loadText = document.getElementById('load-text');
        const pbar = document.getElementById('pbar');
        const errorMsg = document.getElementById('error-msg');
        const lblFps = document.getElementById('lbl-fps');
        const btnReset = document.getElementById('btn-reset');
        const btnOrbit = document.getElementById('btn-orbit');
        const btnBg = document.getElementById('btn-bg');
        const btnFs = document.getElementById('btn-fs');

        let autoOrbit = false;
        let bgMode = 0;
        const bgColors = [0x0d0f12, 0x000000, 0x1e222a, 0xffffff];

        const defaultPos = {cam_pos};
        const defaultTarget = {cam_target};

        function showError(msg) {{
            errorMsg.style.display = 'block';
            errorMsg.innerHTML = '<b>⚠️ Viewer Error</b><br><br>' + msg;
            loading.classList.add('done');
        }}

        try {{
            const viewer = new GaussianSplats3D.Viewer({{
                cameraUp: [0, -1, 0],
                initialCameraPosition: defaultPos,
                initialCameraLookAt: defaultTarget,
                sphericalHarmonicsDegree: 0,
                gpuAcceleratedSort: true,
                sharedMemoryForWorkers: false,
                dynamicScene: false
            }});

            await viewer.addSplatScene('./{model_filename}', {{
                splatAlphaRemovalThreshold: 1,
                showLoadingUI: false,
                progressiveLoad: false,
                position: [0, 0, 0],
                rotation: [0, 0, 0, 1],
                scale: [1, 1, 1],
                onProgress: (percent) => {{
                    const p = Math.min(100, Math.round(percent));
                    pbar.style.width = p + '%';
                    loadText.textContent = 'Loading Splats: ' + p + '%';
                }}
            }});

            loading.classList.add('done');
            viewer.start();

            {copy_cam_js}

            btnReset.addEventListener('click', () => {{
                viewer.camera.position.set(defaultPos[0], defaultPos[1], defaultPos[2]);
                viewer.camera.lookAt(defaultTarget[0], defaultTarget[1], defaultTarget[2]);
                if (viewer.controls) viewer.controls.target.set(defaultTarget[0], defaultTarget[1], defaultTarget[2]);
            }});

            btnOrbit.addEventListener('click', () => {{
                autoOrbit = !autoOrbit;
                btnOrbit.classList.toggle('active', autoOrbit);
            }});

            btnBg.addEventListener('click', () => {{
                bgMode = (bgMode + 1) % bgColors.length;
                viewer.renderer.setClearColor(bgColors[bgMode], 1);
            }});

            btnFs.addEventListener('click', () => {{
                if (!document.fullscreenElement) {{
                    document.documentElement.requestFullscreen();
                }} else {{
                    document.exitFullscreen();
                }}
            }});

            let lastTime = performance.now();
            let frameCount = 0;
            function animate() {{
                requestAnimationFrame(animate);
                if (autoOrbit && viewer.controls) {{
                    const angle = 0.008;
                    const x = viewer.camera.position.x;
                    const z = viewer.camera.position.z;
                    viewer.camera.position.x = x * Math.cos(angle) - z * Math.sin(angle);
                    viewer.camera.position.z = x * Math.sin(angle) + z * Math.cos(angle);
                    viewer.camera.lookAt(defaultTarget[0], defaultTarget[1], defaultTarget[2]);
                }}

                frameCount++;
                const now = performance.now();
                if (now - lastTime >= 1000) {{
                    lblFps.innerText = 'FPS: ' + frameCount;
                    frameCount = 0;
                    lastTime = now;
                }}
            }}
            animate();

        }} catch (err) {{
            console.error('Viewer Error:', err);
            showError('Failed to load model: ' + err.message);
        }}
    </script>
</body>
</html>'''


class WebGLTab(QWidget):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proj_dir = ""
        self.server_thread = None
        self.server_port = 8080
        # Model specific configuration: { file_path: { "html_name": "...", "pos": [x,y,z], "target": [tx,ty,tz], "fov": 50, "label": "..." } }
        self.model_configs = {}
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
        scroll_content.setObjectName("webglScrollContent")
        scroll_content.setStyleSheet("QWidget#webglScrollContent { background-color: transparent; }")

        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # Card 1: Model Source Queue & Output Naming Table
        # ----------------------------------------------------
        self.card_source = ModernStepCard(
            step_num="", 
            title="WebGL Models & Output Filenames", 
            subtitle="Manage splat models and customize individual HTML output filenames"
        )
        self.pill_source = StatusPill("0 Models", "idle")
        self.card_source.add_header_action(self.pill_source)

        c1_layout = QVBoxLayout()
        c1_layout.setSpacing(8)

        # Toolbar
        c1_toolbar = QHBoxLayout()
        c1_toolbar.setSpacing(8)

        self.btn_add_files = QPushButton("Add Files...")
        self.btn_add_files.setObjectName("PrimaryBtn")
        self.btn_add_files.setCursor(Qt.PointingHandCursor)
        self.btn_add_files.setToolTip("Select .ply or .sog files to package into WebGL")
        self.btn_add_files.clicked.connect(self.browse_add_files)

        self.btn_scan_proj = QPushButton("Scan Folder")
        self.btn_scan_proj.setCursor(Qt.PointingHandCursor)
        self.btn_scan_proj.setToolTip("Automatically scan standard project export/cleaned directories for models")
        self.btn_scan_proj.clicked.connect(self.scan_project_models)

        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.setCursor(Qt.PointingHandCursor)
        self.btn_select_all.setToolTip("Select or deselect all models for packaging")
        self.btn_select_all.clicked.connect(self.toggle_select_all)

        self.btn_set_index = QPushButton("Set 1st as index.html")
        self.btn_set_index.setCursor(Qt.PointingHandCursor)
        self.btn_set_index.setToolTip("Designate top model as main landing page (index.html)")
        self.btn_set_index.clicked.connect(self.set_first_as_index)

        self.btn_remove_row = QPushButton("Remove")
        self.btn_remove_row.setCursor(Qt.PointingHandCursor)
        self.btn_remove_row.setToolTip("Remove selected model(s) from packaging list")
        self.btn_remove_row.clicked.connect(self.remove_selected_rows)

        self.btn_clear_table = QPushButton("Clear All")
        self.btn_clear_table.setCursor(Qt.PointingHandCursor)
        self.btn_clear_table.setToolTip("Clear all models from packaging list")
        self.btn_clear_table.clicked.connect(self.clear_models_table)

        c1_toolbar.addWidget(self.btn_add_files)
        c1_toolbar.addWidget(self.btn_scan_proj)
        c1_toolbar.addWidget(self.btn_select_all)
        c1_toolbar.addWidget(self.btn_set_index)
        c1_toolbar.addWidget(self.btn_remove_row)
        c1_toolbar.addWidget(self.btn_clear_table)
        c1_toolbar.addStretch()
        c1_layout.addLayout(c1_toolbar)

        # Models & Naming Table (with Dark Table Corner Styling)
        self.table_models = QTableWidget(0, 5)
        self.table_models.setCornerButtonEnabled(False)
        self.table_models.setHorizontalHeaderLabels([
            "Build", 
            "Source Model", 
            "Output HTML File", 
            "Camera Viewport", 
            "Action"
        ])
        
        h_header = self.table_models.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h_header.setSectionResizeMode(1, QHeaderView.Interactive)
        h_header.setSectionResizeMode(2, QHeaderView.Stretch)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_models.setColumnWidth(1, 220)
        h_header.sectionClicked.connect(self.on_header_section_clicked)

        self.table_models.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_models.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_models.setAlternatingRowColors(True)
        self.table_models.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_models.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_models.verticalHeader().setVisible(False)
        self.table_models.verticalHeader().setDefaultSectionSize(30)
        self.table_models.setMinimumHeight(130)
        self.table_models.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.table_models.itemChanged.connect(self._on_table_item_changed)
        c1_layout.addWidget(self.table_models)

        self.card_source.setContentLayout(c1_layout)
        main_layout.addWidget(self.card_source)

        # ----------------------------------------------------
        # Card 2: Initial Camera & Viewport Setup (Per-Model)
        # ----------------------------------------------------
        self.card_camera = ModernStepCard(
            step_num="", 
            title="Selected Model Camera Viewport Setup", 
            subtitle="Interactive camera viewport configuration and clipboard sync for selected model"
        )
        self.pill_camera = StatusPill("Front View", "idle")
        self.card_camera.add_header_action(self.pill_camera)

        c2_layout = QVBoxLayout()
        c2_layout.setSpacing(10)

        # Active Model Header & Live Preview Row
        model_action_row = QHBoxLayout()
        self.lbl_active_model = QLabel("<b>Target Model:</b> <i>No model selected (select a row in list)</i>")
        self.lbl_active_model.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        
        self.btn_live_preview_cam = QPushButton("Adjust View in Browser")
        self.btn_live_preview_cam.setObjectName("PrimaryBtn")
        self.btn_live_preview_cam.setCursor(Qt.PointingHandCursor)
        self.btn_live_preview_cam.clicked.connect(self.open_active_model_in_browser)

        self.btn_paste_cam = QPushButton("Paste Camera View")
        self.btn_paste_cam.setObjectName("SuccessBtn")
        self.btn_paste_cam.setCursor(Qt.PointingHandCursor)
        self.btn_paste_cam.clicked.connect(self.paste_camera_from_clipboard)

        model_action_row.addWidget(self.lbl_active_model, 1)
        model_action_row.addWidget(self.btn_live_preview_cam)
        model_action_row.addWidget(self.btn_paste_cam)
        c2_layout.addLayout(model_action_row)

        # Quick Preset Chips & Saved Views Row
        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)

        self.lbl_presets = QLabel("Presets:")
        self.lbl_presets.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 11px;")
        preset_row.addWidget(self.lbl_presets)

        self.btn_cam_front = QPushButton("Front")
        self.btn_cam_front.setCursor(Qt.PointingHandCursor)
        self.btn_cam_front.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        self.btn_cam_front.clicked.connect(lambda: self.apply_camera_preset([0.0, 1.2, 3.8], [0.0, 0.0, 0.0], 50, "Front View"))

        self.btn_cam_quarter = QPushButton("Quarter (3/4)")
        self.btn_cam_quarter.setCursor(Qt.PointingHandCursor)
        self.btn_cam_quarter.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        self.btn_cam_quarter.clicked.connect(lambda: self.apply_camera_preset([2.5, 1.8, -2.5], [0.0, 0.0, 0.0], 50, "Quarter 3/4"))

        self.btn_cam_side = QPushButton("Side")
        self.btn_cam_side.setCursor(Qt.PointingHandCursor)
        self.btn_cam_side.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        self.btn_cam_side.clicked.connect(lambda: self.apply_camera_preset([3.8, 1.2, 0.0], [0.0, 0.0, 0.0], 50, "Side View"))

        self.btn_cam_top = QPushButton("Top-Down")
        self.btn_cam_top.setCursor(Qt.PointingHandCursor)
        self.btn_cam_top.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        self.btn_cam_top.clicked.connect(lambda: self.apply_camera_preset([0.0, 6.0, 0.1], [0.0, 0.0, 0.0], 55, "Top-Down"))

        preset_row.addWidget(self.btn_cam_front)
        preset_row.addWidget(self.btn_cam_quarter)
        preset_row.addWidget(self.btn_cam_side)
        preset_row.addWidget(self.btn_cam_top)

        preset_row.addSpacing(10)
        self.lbl_saved_views = QLabel("Saved Views:")
        self.lbl_saved_views.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 11px;")
        preset_row.addWidget(self.lbl_saved_views)

        self.combo_saved_views = QComboBox()
        self.combo_saved_views.setStyleSheet("font-size: 11px; padding: 2px 6px; min-width: 140px;")
        self.combo_saved_views.currentIndexChanged.connect(self._on_saved_view_selected)
        preset_row.addWidget(self.combo_saved_views)

        self.btn_save_cam_preset = QPushButton("Save View")
        self.btn_save_cam_preset.setCursor(Qt.PointingHandCursor)
        self.btn_save_cam_preset.setToolTip("Save current camera coordinates as a reusable preset")
        self.btn_save_cam_preset.clicked.connect(self.save_custom_camera_preset)
        preset_row.addWidget(self.btn_save_cam_preset)

        self.btn_del_cam_preset = QPushButton("Delete")
        self.btn_del_cam_preset.setCursor(Qt.PointingHandCursor)
        self.btn_del_cam_preset.setToolTip("Delete selected saved camera view")
        self.btn_del_cam_preset.setStyleSheet("font-size: 11px; padding: 3px 6px;")
        self.btn_del_cam_preset.clicked.connect(self.delete_custom_camera_preset)
        preset_row.addWidget(self.btn_del_cam_preset)

        preset_row.addStretch()
        c2_layout.addLayout(preset_row)

        # Coordinate Inputs Frame
        cam_frame = QFrame()
        cam_frame.setObjectName("camFrame")
        cam_frame.setStyleSheet("QFrame#camFrame { background-color: #15181f; border: 1px solid #232732; border-radius: 6px; }")
        cam_inputs_layout = QHBoxLayout(cam_frame)
        cam_inputs_layout.setSpacing(12)

        # Position (X, Y, Z)
        self.lbl_cam_pos_title = QLabel("Position (X,Y,Z):")
        self.lbl_cam_pos_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        cam_inputs_layout.addWidget(self.lbl_cam_pos_title)
        self.input_cam_pos = QLineEdit("0.0, 1.2, 3.8")
        self.input_cam_pos.setToolTip("Camera starting position coordinates [X, Y, Z]")
        self.input_cam_pos.textChanged.connect(self._on_cam_inputs_edited)
        cam_inputs_layout.addWidget(self.input_cam_pos, 2)

        # Target (X, Y, Z)
        self.lbl_cam_tgt_title = QLabel("Target:")
        self.lbl_cam_tgt_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        cam_inputs_layout.addWidget(self.lbl_cam_tgt_title)
        self.input_cam_target = QLineEdit("0.0, 0.0, 0.0")
        self.input_cam_target.setToolTip("Camera focal center point [X, Y, Z]")
        self.input_cam_target.textChanged.connect(self._on_cam_inputs_edited)
        cam_inputs_layout.addWidget(self.input_cam_target, 2)

        # FOV
        self.lbl_cam_fov_title = QLabel("FOV:")
        self.lbl_cam_fov_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        cam_inputs_layout.addWidget(self.lbl_cam_fov_title)
        self.input_cam_fov = QLineEdit("50")
        self.input_cam_fov.setMaximumWidth(45)
        self.input_cam_fov.setToolTip("Camera Field of View in degrees (default: 50)")
        self.input_cam_fov.textChanged.connect(self._on_cam_inputs_edited)
        cam_inputs_layout.addWidget(self.input_cam_fov)

        c2_layout.addWidget(cam_frame)
        self.card_camera.setContentLayout(c2_layout)
        main_layout.addWidget(self.card_camera)

        # ----------------------------------------------------
        # Card 3: Output Destination & Web Publishing
        # ----------------------------------------------------
        self.card_config = ModernStepCard(
            step_num="", 
            title="Output Destination & Web Publishing", 
            subtitle="Specify destination directory, build WebGL packages, and upload to cloud"
        )
        self.pill_config = StatusPill("Ready", "ready")
        self.card_config.add_header_action(self.pill_config)

        # Compact Circular Local Server Indicator & Toggle Button in Header
        self.btn_server_circle = QPushButton("⚪ Off")
        self.btn_server_circle.setCursor(Qt.PointingHandCursor)
        self.btn_server_circle.setToolTip("Local HTTP Server (Port 8080) - Click to Toggle")
        self.btn_server_circle.setStyleSheet("""
            QPushButton {
                background-color: #171922;
                border: 1px solid #282d3c;
                border-radius: 11px;
                color: #94a3b8;
                font-size: 11px;
                font-weight: 600;
                min-height: 22px;
                max-height: 22px;
                padding: 1px 10px;
            }
            QPushButton:hover {
                background-color: #202636;
                border-color: #3b465c;
                color: #ffffff;
            }
        """)
        self.btn_server_circle.clicked.connect(self.toggle_preview_server)
        self.card_config.add_header_action(self.btn_server_circle)

        c3_layout = QVBoxLayout()
        c3_layout.setSpacing(10)

        # Destination Folder Row
        dest_row = QHBoxLayout()
        self.lbl_dest_title = QLabel("Output Folder:")
        self.lbl_dest_title.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        self.input_output_dir = QLineEdit()
        self.input_output_dir.setPlaceholderText("Select output directory (default: 05_web_build)...")
        self.btn_browse_output = QPushButton("Browse...")
        self.btn_browse_output.clicked.connect(self.browse_output_dir)
        dest_row.addWidget(self.lbl_dest_title)
        dest_row.addWidget(self.input_output_dir, 1)
        dest_row.addWidget(self.btn_browse_output)
        c3_layout.addLayout(dest_row)

        # Build Options Row (Client Review Watermark with Size & Opacity controls)
        opts_row = QHBoxLayout()
        opts_row.setSpacing(10)
        
        self.chk_watermark = QCheckBox("Client Review Watermark")
        self.chk_watermark.setStyleSheet("color: #cbd5e1; font-weight: 600;")
        self.chk_watermark.setChecked(False)
        
        self.input_watermark_text = QLineEdit("Points & Reality")
        self.input_watermark_text.setPlaceholderText("Watermark text (default: Points & Reality)")
        self.input_watermark_text.setEnabled(False)
        self.input_watermark_text.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 5px 10px; color: #64748b;")
        
        self.lbl_watermark_size = QLabel("Size:")
        self.lbl_watermark_size.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11px;")
        
        self.spin_watermark_size = QSpinBox()
        self.spin_watermark_size.setRange(40, 300)
        self.spin_watermark_size.setValue(140)
        self.spin_watermark_size.setSuffix(" px")
        self.spin_watermark_size.setFixedWidth(78)
        self.spin_watermark_size.setEnabled(False)
        self.spin_watermark_size.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 4px 6px; color: #64748b; font-weight: 600;")

        self.lbl_watermark_opacity = QLabel("Opacity:")
        self.lbl_watermark_opacity.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11px;")

        self.spin_watermark_opacity = QSpinBox()
        self.spin_watermark_opacity.setRange(1, 100)
        self.spin_watermark_opacity.setValue(6)
        self.spin_watermark_opacity.setSuffix(" %")
        self.spin_watermark_opacity.setFixedWidth(68)
        self.spin_watermark_opacity.setEnabled(False)
        self.spin_watermark_opacity.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 4px 6px; color: #64748b; font-weight: 600;")

        def _on_chk_watermark_changed(state):
            is_on = (state != 0)
            self.input_watermark_text.setEnabled(is_on)
            self.spin_watermark_size.setEnabled(is_on)
            self.spin_watermark_opacity.setEnabled(is_on)
            if is_on:
                self.input_watermark_text.setStyleSheet("background: #111318; border: 1px solid #3b82f6; border-radius: 4px; padding: 5px 10px; color: #f8fafc;")
                self.spin_watermark_size.setStyleSheet("background: #111318; border: 1px solid #3b82f6; border-radius: 4px; padding: 4px 6px; color: #f8fafc; font-weight: 600;")
                self.spin_watermark_opacity.setStyleSheet("background: #111318; border: 1px solid #3b82f6; border-radius: 4px; padding: 4px 6px; color: #f8fafc; font-weight: 600;")
                self.lbl_watermark_size.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 11px;")
                self.lbl_watermark_opacity.setStyleSheet("color: #cbd5e1; font-weight: 600; font-size: 11px;")
            else:
                self.input_watermark_text.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 5px 10px; color: #64748b;")
                self.spin_watermark_size.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 4px 6px; color: #64748b; font-weight: 600;")
                self.spin_watermark_opacity.setStyleSheet("background: #0c0d11; border: 1px solid #232732; border-radius: 4px; padding: 4px 6px; color: #64748b; font-weight: 600;")
                self.lbl_watermark_size.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11px;")
                self.lbl_watermark_opacity.setStyleSheet("color: #64748b; font-weight: 600; font-size: 11px;")

        self.chk_watermark.stateChanged.connect(_on_chk_watermark_changed)
        
        opts_row.addWidget(self.chk_watermark)
        opts_row.addWidget(self.input_watermark_text, 1)
        opts_row.addWidget(self.lbl_watermark_size)
        opts_row.addWidget(self.spin_watermark_size)
        opts_row.addWidget(self.lbl_watermark_opacity)
        opts_row.addWidget(self.spin_watermark_opacity)
        c3_layout.addLayout(opts_row)

        # Action Buttons Row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        self.btn_build_web = QPushButton("Build Selected WebGL Packages")
        self.btn_build_web.setObjectName("PrimaryBtn")
        self.btn_build_web.setCursor(Qt.PointingHandCursor)
        self.btn_build_web.clicked.connect(self.build_web_package)

        self.btn_open_web = QPushButton("Open Web Build Folder")
        self.btn_open_web.setCursor(Qt.PointingHandCursor)
        self.btn_open_web.clicked.connect(self.open_web_folder)

        actions_layout.addWidget(self.btn_build_web)
        actions_layout.addWidget(self.btn_open_web)
        actions_layout.addStretch()
        c3_layout.addLayout(actions_layout)

        self.card_config.setContentLayout(c3_layout)
        main_layout.addWidget(self.card_config)
        main_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        self._refresh_saved_views_combo()

    # ----------------------------------------------------------------------
    # Model Queue Management
    # ----------------------------------------------------------------------
    def _is_row_checked(self, row):
        widget = self.table_models.cellWidget(row, 0)
        if widget and widget.layout() and widget.layout().count() > 0:
            chk = widget.layout().itemAt(0).widget()
            if isinstance(chk, QCheckBox):
                return chk.isChecked()
        item = self.table_models.item(row, 0)
        if item:
            return item.checkState() == Qt.Checked
        return False

    def _set_row_checked(self, row, checked):
        widget = self.table_models.cellWidget(row, 0)
        if widget and widget.layout() and widget.layout().count() > 0:
            chk = widget.layout().itemAt(0).widget()
            if isinstance(chk, QCheckBox):
                chk.blockSignals(True)
                chk.setChecked(checked)
                chk.blockSignals(False)
                return
        item = self.table_models.item(row, 0)
        if item:
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)

    def _on_row_checkbox_changed(self):
        self._update_build_header()

    def _update_build_header(self):
        t = self.current_translations
        total = self.table_models.rowCount()
        base_title = t.get("tab3_tbl_col_build", "Build") if t else "Build"
        clean_title = base_title.replace("☑️", "").replace("☑", "").replace("☐", "").strip()
        
        if total == 0:
            prefix = "☑️"
        else:
            checked_count = sum(1 for r in range(total) if self._is_row_checked(r))
            if checked_count == 0:
                prefix = "☐"
            else:
                prefix = "☑️"

        header_text = f"{prefix} {clean_title}"
        header_item = self.table_models.horizontalHeaderItem(0)
        tooltip = t.get("tab3_btn_select_all", "Toggle All (전체 선택/해제)") if t else "Toggle All (전체 선택/해제)"
        if header_item:
            header_item.setText(header_text)
            header_item.setToolTip(tooltip)
        else:
            new_item = QTableWidgetItem(header_text)
            new_item.setToolTip(tooltip)
            self.table_models.setHorizontalHeaderItem(0, new_item)

    def on_header_section_clicked(self, logical_index):
        if logical_index == 0:
            self.toggle_select_all()

    def add_model_file(self, file_path, checked=True, custom_html_name=None):
        if not os.path.exists(file_path): return
        norm_path = os.path.normpath(file_path)

        # Prevent duplicate entries
        for r in range(self.table_models.rowCount()):
            existing_path = self.table_models.item(r, 1).toolTip()
            if os.path.normpath(existing_path) == norm_path:
                return

        self.table_models.blockSignals(True)
        row = self.table_models.rowCount()
        self.table_models.insertRow(row)

        # Col 0: Centered Checkbox Widget (no dotted focus rect)
        dummy_item = QTableWidgetItem()
        dummy_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_models.setItem(row, 0, dummy_item)

        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk_box = QCheckBox()
        chk_box.setFocusPolicy(Qt.NoFocus)
        chk_box.setChecked(checked)
        chk_box.stateChanged.connect(self._on_row_checkbox_changed)
        chk_layout.addWidget(chk_box)
        self.table_models.setCellWidget(row, 0, chk_widget)

        # Col 1: Source Model (Filename + Format & Size)
        fname = os.path.basename(norm_path)
        fmt = _detect_model_format(norm_path).upper()
        size_mb = os.path.getsize(norm_path) / (1024 * 1024)
        item_source = QTableWidgetItem(f"{fname}  [{fmt}, {size_mb:.1f}MB]")
        item_source.setToolTip(norm_path)
        item_source.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_models.setItem(row, 1, item_source)

        # Col 2: Output HTML File (Directly Editable!)
        base_name, _ = os.path.splitext(fname)
        default_html = custom_html_name or f"{base_name}.html"
        if norm_path in self.model_configs:
            saved_html = self.model_configs[norm_path].get("html_name")
            if saved_html and not custom_html_name:
                default_html = saved_html

        item_html = QTableWidgetItem(default_html)
        item_html.setToolTip("Double-click to edit output HTML filename")
        item_html.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        self.table_models.setItem(row, 2, item_html)

        # Col 3: Camera Profile
        default_profile = {
            "html_name": default_html,
            "pos": [0.0, 1.2, 3.8], 
            "target": [0.0, 0.0, 0.0], 
            "fov": 50, 
            "label": "Front View"
        }
        if norm_path not in self.model_configs:
            self.model_configs[norm_path] = default_profile
        else:
            self.model_configs[norm_path]["html_name"] = default_html

        saved_label = self.model_configs[norm_path].get("label", "Front View")
        item_cam = QTableWidgetItem(saved_label)
        item_cam.setTextAlignment(Qt.AlignCenter)
        item_cam.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table_models.setItem(row, 3, item_cam)

        # Col 4: Action Button (Inline Preview in compact cell container)
        preview_cell = QWidget()
        preview_layout = QHBoxLayout(preview_cell)
        preview_layout.setContentsMargins(6, 2, 6, 2)
        preview_layout.setAlignment(Qt.AlignCenter)

        btn_row_preview = QPushButton(self.current_translations.get("tab3_btn_row_preview", "Preview"))
        btn_row_preview.setCursor(Qt.PointingHandCursor)
        btn_row_preview.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                border: 1px solid #38bdf8;
                border-radius: 3px;
                color: #ffffff;
                font-size: 10.5px;
                font-weight: 600;
                min-height: 20px;
                max-height: 22px;
                padding: 1px 12px;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
                border-color: #7dd3fc;
            }
            QPushButton:pressed {
                background-color: #0369a1;
            }
        """)
        btn_row_preview.clicked.connect(lambda _, p=norm_path: self.preview_single_model(p))
        preview_layout.addWidget(btn_row_preview)
        self.table_models.setCellWidget(row, 4, preview_cell)

        self.table_models.blockSignals(False)
        self._update_queue_pill()
        self._update_build_header()

    def _on_table_item_changed(self, item):
        if item.column() == 2: # HTML name edited
            row = item.row()
            src_item = self.table_models.item(row, 1)
            if src_item:
                file_path = os.path.normpath(src_item.toolTip())
                new_html_name = item.text().strip()
                if not new_html_name.lower().endswith('.html'):
                    new_html_name += '.html'
                    self.table_models.blockSignals(True)
                    item.setText(new_html_name)
                    self.table_models.blockSignals(False)

                if file_path in self.model_configs:
                    self.model_configs[file_path]["html_name"] = new_html_name
                self.on_table_selection_changed()

    def browse_add_files(self):
        start_dir = self.proj_dir if self.proj_dir else ""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select 3DGS Model Files", 
            start_dir, 
            "All Splat Files (*.ply *.splat *.spz *.sog);;SuperSplat Models (*.sog);;PLY 3DGS Models (*.ply);;Compressed Splat (*.splat *.spz);;All Files (*.*)"
        )
        if file_paths:
            for p in file_paths:
                self.add_model_file(p, checked=True)
            if self.table_models.rowCount() > 0:
                self.table_models.selectRow(0)

    def scan_project_models(self):
        if not self.proj_dir or not os.path.exists(self.proj_dir):
            self.log_signal.emit("[WARN] Set a valid project directory first.", "warning")
            return

        found_count = 0
        scanned_subfolders = [
            "04_splats_cleaned", "04_cleaned_splats", 
            "03_postshot_exports", "03_splats_exports", 
            "02_tracking_alignment", "02_camera_alignment"
        ]

        for sub in scanned_subfolders:
            sub_path = os.path.normpath(os.path.join(self.proj_dir, sub))
            if os.path.exists(sub_path):
                for f in os.listdir(sub_path):
                    if f.lower().endswith(('.ply', '.splat', '.spz', '.sog')) and not f.startswith('model.'):
                        full_p = os.path.normpath(os.path.join(sub_path, f))
                        self.add_model_file(full_p, checked=True)
                        found_count += 1

        self.log_signal.emit(f"Scanned project folders: Found {found_count} 3DGS models.", "info")
        if self.table_models.rowCount() > 0 and not self.table_models.selectedItems():
            self.table_models.selectRow(0)

    def set_first_as_index(self):
        if self.table_models.rowCount() == 0: return
        self.table_models.blockSignals(True)
        item_html = self.table_models.item(0, 2)
        if item_html:
            item_html.setText("index.html")
            src_item = self.table_models.item(0, 1)
            if src_item:
                file_path = os.path.normpath(src_item.toolTip())
                if file_path in self.model_configs:
                    self.model_configs[file_path]["html_name"] = "index.html"
        self.table_models.blockSignals(False)
        self.on_table_selection_changed()
        self.log_signal.emit("Set first model output HTML filename to 'index.html'", "info")

    def toggle_select_all(self, logical_index=None):
        if logical_index is not None and logical_index != 0:
            return
        if self.table_models.rowCount() == 0: return
        any_unchecked = False
        for r in range(self.table_models.rowCount()):
            if not self._is_row_checked(r):
                any_unchecked = True
                break

        new_state = any_unchecked
        for r in range(self.table_models.rowCount()):
            self._set_row_checked(r, new_state)

        self._update_build_header()

    def remove_selected_rows(self):
        selected_rows = sorted(set(idx.row() for idx in self.table_models.selectedIndexes()), reverse=True)
        for r in selected_rows:
            self.table_models.removeRow(r)
        self._update_queue_pill()
        self._update_build_header()
        self.on_table_selection_changed()

    def clear_models_table(self):
        self.table_models.setRowCount(0)
        self._update_queue_pill()
        self._update_build_header()
        self.on_table_selection_changed()

    def _update_queue_pill(self):
        count = self.table_models.rowCount()
        if count > 0:
            self.pill_source.set_status(f"{count} Model{'s' if count>1 else ''}", "ready")
        else:
            self.pill_source.set_status("0 Models", "idle")

    # ----------------------------------------------------------------------
    # Camera Sync with Selected Model
    # ----------------------------------------------------------------------
    def _get_active_selected_path(self):
        r = self.table_models.currentRow()
        if r < 0 or r >= self.table_models.rowCount(): return None
        src_item = self.table_models.item(r, 1)
        if not src_item: return None
        return os.path.normpath(src_item.toolTip())

    def on_table_selection_changed(self):
        t = self.current_translations
        file_path = self._get_active_selected_path()
        if not file_path:
            prefix = t.get("tab3_lbl_target_prefix", "📷 Target Model:")
            no_model = t.get("tab3_lbl_no_model", "No model selected (select a row in Step 1)")
            self.lbl_active_model.setText(f"{prefix} <i>{no_model}</i>")
            self.btn_live_preview_cam.setEnabled(False)
            return

        self.btn_live_preview_cam.setEnabled(True)
        r = self.table_models.currentRow()
        fname = os.path.basename(file_path)
        html_name = self.table_models.item(r, 2).text().strip() if self.table_models.item(r, 2) else f"{fname}.html"
        
        prefix = t.get("tab3_lbl_target_prefix", "📷 Target Model:")
        self.lbl_active_model.setText(
            f"{prefix} <span style='color:#38bdf8;'>{fname}</span> ➔ <b style='color:#7dd3fc;'>{html_name}</b>"
        )

        # Load camera profile for this model
        profile = self.model_configs.get(file_path, {
            "pos": [0.0, 1.2, 3.8], 
            "target": [0.0, 0.0, 0.0], 
            "fov": 50, 
            "label": "Front View"
        })
        p = profile.get("pos", [0.0, 1.2, 3.8])
        t_pos = profile.get("target", [0.0, 0.0, 0.0])
        fov = profile.get("fov", 50)
        label = profile.get("label", "Front View")

        self.input_cam_pos.blockSignals(True)
        self.input_cam_target.blockSignals(True)
        self.input_cam_fov.blockSignals(True)

        self.input_cam_pos.setText(f"{p[0]}, {p[1]}, {p[2]}")
        self.input_cam_target.setText(f"{t_pos[0]}, {t_pos[1]}, {t_pos[2]}")
        self.input_cam_fov.setText(str(fov))
        self.pill_camera.set_status(label, "ready")
        self._update_cam_preset_styles(label)

        self.input_cam_pos.blockSignals(False)
        self.input_cam_target.blockSignals(False)
        self.input_cam_fov.blockSignals(False)

    def _update_cam_preset_styles(self, active_label=None):
        if not hasattr(self, 'btn_cam_front') or not hasattr(self, 'btn_cam_quarter') or not hasattr(self, 'btn_cam_side') or not hasattr(self, 'btn_cam_top'):
            return
        style_active = "background-color: #1e3a5f; color: #38bdf8; border: 1px solid #0284c7; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;"
        style_inactive = "background-color: #24272f; color: #cbd5e1; border: 1px solid #333842; border-radius: 4px; padding: 3px 8px; font-size: 11px;"
        
        lbl = active_label or ""
        self.btn_cam_front.setStyleSheet(style_active if "Front" in lbl else style_inactive)
        self.btn_cam_quarter.setStyleSheet(style_active if "Quarter" in lbl else style_inactive)
        self.btn_cam_side.setStyleSheet(style_active if "Side" in lbl else style_inactive)
        self.btn_cam_top.setStyleSheet(style_active if "Top" in lbl else style_inactive)

    def apply_camera_preset(self, pos, target, fov, label):
        self.input_cam_pos.setText(f"{pos[0]}, {pos[1]}, {pos[2]}")
        self.input_cam_target.setText(f"{target[0]}, {target[1]}, {target[2]}")
        self.input_cam_fov.setText(str(fov))
        self.pill_camera.set_status(label, "ready")
        self._update_cam_preset_styles(label)
        self._save_active_model_camera(label)

    def paste_camera_from_clipboard(self):
        clip = QApplication.clipboard().text().strip()
        label = "Custom Copied View"
        try:
            data = json.loads(clip)
            if 'position' in data:
                p = data['position']
                self.input_cam_pos.setText(f"{p[0]}, {p[1]}, {p[2]}")
            if 'target' in data:
                t = data['target']
                self.input_cam_target.setText(f"{t[0]}, {t[1]}, {t[2]}")
            if 'fov' in data:
                self.input_cam_fov.setText(str(data['fov']))
            self.pill_camera.set_status(label, "success")
            self._update_cam_preset_styles(label)
            self._save_active_model_camera(label)
            self.log_signal.emit(f"Applied camera coordinates from clipboard: Pos={self.input_cam_pos.text()}", "success")
        except Exception:
            parts = [float(x.strip()) for x in clip.replace('[','').replace(']','').split(',') if x.strip()]
            if len(parts) >= 3:
                self.input_cam_pos.setText(f"{parts[0]}, {parts[1]}, {parts[2]}")
                self.pill_camera.set_status("Custom Coordinates", "success")
                self._update_cam_preset_styles("Custom Coordinates")
                self._save_active_model_camera("Custom Coordinates")

    def _on_cam_inputs_edited(self):
        self._save_active_model_camera("Custom View")
        self._update_cam_preset_styles("Custom View")

    def _save_active_model_camera(self, label="Custom View"):
        file_path = self._get_active_selected_path()
        if not file_path: return
        r = self.table_models.currentRow()

        pos, target, fov = self._get_camera_coords()
        html_name = self.table_models.item(r, 2).text().strip() if self.table_models.item(r, 2) else f"{os.path.basename(file_path)}.html"

        self.model_configs[file_path] = {
            "html_name": html_name,
            "pos": pos,
            "target": target,
            "fov": fov,
            "label": label
        }

        # Update table column 3
        cam_item = self.table_models.item(r, 3)
        if cam_item:
            cam_item.setText(label)

        self._save_project_camera_configs()

    def _get_camera_coords(self):
        try:
            pos = [float(x.strip()) for x in self.input_cam_pos.text().split(',')]
            if len(pos) < 3: pos = [0.0, 1.2, 3.8]
        except Exception:
            pos = [0.0, 1.2, 3.8]

        try:
            target = [float(x.strip()) for x in self.input_cam_target.text().split(',')]
            if len(target) < 3: target = [0.0, 0.0, 0.0]
        except Exception:
            target = [0.0, 0.0, 0.0]

        try:
            fov = float(self.input_cam_fov.text().strip())
        except Exception:
            fov = 50.0

        return pos, target, fov

    # ----------------------------------------------------------------------
    # Custom Camera View Presets & Persistent Memory
    # ----------------------------------------------------------------------
    def _get_presets_file_path(self):
        app_dir = os.path.join(os.path.expanduser("~"), ".points_and_reality")
        os.makedirs(app_dir, exist_ok=True)
        preset_file = os.path.join(app_dir, "camera_presets.json")
        legacy_file = os.path.join(os.path.expanduser("~"), ".splatial", "camera_presets.json")
        if not os.path.exists(preset_file) and os.path.exists(legacy_file):
            try:
                shutil.copyfile(legacy_file, preset_file)
            except Exception:
                pass
        return preset_file

    def _load_saved_camera_presets(self):
        path = self._get_presets_file_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {}

    def _save_saved_camera_presets(self, presets):
        path = self._get_presets_file_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(presets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed to save camera presets: {e}", "error")

    def _refresh_saved_views_combo(self, select_name=None):
        if not hasattr(self, 'combo_saved_views'):
            return
        t = self.current_translations
        default_label = t.get("tab3_combo_default_saved", "--- Saved Views ---") if t else "--- Saved Views ---"

        presets = self._load_saved_camera_presets()
        self.combo_saved_views.blockSignals(True)
        self.combo_saved_views.clear()
        self.combo_saved_views.addItem(default_label, None)

        sel_idx = 0
        for idx, (name, data) in enumerate(presets.items(), start=1):
            self.combo_saved_views.addItem(f"⭐ {name}", data)
            if select_name and (name == select_name or f"⭐ {name}" == select_name):
                sel_idx = idx

        self.combo_saved_views.setCurrentIndex(sel_idx)
        self.combo_saved_views.blockSignals(False)

    def _on_saved_view_selected(self, index):
        if index <= 0:
            return
        data = self.combo_saved_views.itemData(index)
        preset_text = self.combo_saved_views.itemText(index).replace("⭐ ", "").strip()
        if data and isinstance(data, dict):
            pos = data.get("pos", [0.0, 1.2, 3.8])
            target = data.get("target", [0.0, 0.0, 0.0])
            fov = data.get("fov", 50)
            self.apply_camera_preset(pos, target, fov, preset_text)
            self.log_signal.emit(f"Applied saved camera view '{preset_text}': Pos={pos}, Target={target}, FOV={fov}", "info")

    def save_custom_camera_preset(self):
        t = self.current_translations
        title = t.get("tab3_prompt_cam_preset_title", "Save Camera View Preset") if t else "Save Camera View Preset"
        msg = t.get("tab3_prompt_cam_preset_msg", "Enter a name for this camera view preset:") if t else "Enter a name for this camera view preset:"

        presets = self._load_saved_camera_presets()
        suggested = f"Custom View {len(presets) + 1}"

        name, ok = QInputDialog.getText(self, title, msg, text=suggested)
        if ok and name.strip():
            preset_name = name.strip()
            pos, target, fov = self._get_camera_coords()
            presets[preset_name] = {
                "pos": pos,
                "target": target,
                "fov": fov
            }
            self._save_saved_camera_presets(presets)
            self._refresh_saved_views_combo(select_name=preset_name)
            self.apply_camera_preset(pos, target, fov, preset_name)
            self.log_signal.emit(f"[SUCCESS] Saved camera view preset: '{preset_name}'", "success")

    def delete_custom_camera_preset(self):
        idx = self.combo_saved_views.currentIndex()
        if idx <= 0:
            self.log_signal.emit("[WARN] Select a saved camera view to delete.", "warning")
            return
        raw_name = self.combo_saved_views.itemText(idx).replace("⭐ ", "").strip()
        presets = self._load_saved_camera_presets()
        if raw_name in presets:
            del presets[raw_name]
            self._save_saved_camera_presets(presets)
            self._refresh_saved_views_combo()
            self.log_signal.emit(f"Deleted camera view preset: '{raw_name}'", "info")

    def _get_project_camera_configs_path(self):
        if not self.proj_dir:
            return None
        return os.path.join(self.proj_dir, "05_web_build", "camera_configs.json")

    def _save_project_camera_configs(self):
        path = self._get_project_camera_configs_path()
        if not path: return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.model_configs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_project_camera_configs(self):
        path = self._get_project_camera_configs_path()
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.model_configs.update(loaded)
            except Exception:
                pass

    # ----------------------------------------------------------------------
    # Project & Output Path Management
    # ----------------------------------------------------------------------
    def set_proj_dir(self, directory):
        if not directory: return
        self.proj_dir = os.path.normpath(directory)

        # Set default output directory
        default_out = os.path.normpath(os.path.join(self.proj_dir, "05_web_build"))
        self.input_output_dir.setText(default_out)

        # Load existing camera configurations for project models
        self._load_project_camera_configs()

        # Automatically scan project for splats
        self.clear_models_table()
        self.scan_project_models()

    def browse_output_dir(self):
        start_dir = self.input_output_dir.text().strip() or self.proj_dir
        dir_path = QFileDialog.getExistingDirectory(self, "Select WebGL Output Folder", start_dir)
        if dir_path:
            norm_dir = os.path.normpath(dir_path)
            self.input_output_dir.setText(norm_dir)

    def open_web_folder(self):
        out_dir = self.input_output_dir.text().strip()
        if not out_dir and self.proj_dir:
            out_dir = os.path.join(self.proj_dir, "05_web_build")
        if out_dir:
            norm_dir = os.path.normpath(out_dir)
            os.makedirs(norm_dir, exist_ok=True)
            os.startfile(norm_dir)

    def _ensure_local_libs(self, web_dir):
        """Ensure local offline JS libraries exist in destination libs/."""
        dst_libs = os.path.normpath(os.path.join(web_dir, "libs"))
        os.makedirs(dst_libs, exist_ok=True)
        
        src_libs = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "libs"))
        if os.path.exists(src_libs):
            for f in os.listdir(src_libs):
                s = os.path.join(src_libs, f)
                d = os.path.join(dst_libs, f)
                if os.path.isfile(s) and (not os.path.exists(d) or os.path.getsize(s) != os.path.getsize(d)):
                    shutil.copyfile(s, d)

    # ----------------------------------------------------------------------
    # Live Interactive Preview (Direct & Per-Model)
    # ----------------------------------------------------------------------
    def open_active_model_in_browser(self):
        file_path = self._get_active_selected_path()
        if file_path:
            self.preview_single_model(file_path)

    def preview_single_model(self, file_path):
        out_dir = self.input_output_dir.text().strip()
        if not out_dir:
            if self.proj_dir:
                out_dir = os.path.join(self.proj_dir, "05_web_build")
                self.input_output_dir.setText(out_dir)
            else:
                self.log_signal.emit("[ERROR] Please set an Output Folder first.", "error")
                return

        out_dir = os.path.normpath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        self._ensure_local_libs(out_dir)

        # Build this single model in interactive preview mode (camera hud enabled, no watermark)
        html_filename = self._build_single_model(file_path, out_dir, is_preview=True, enable_watermark=False)

        # Ensure server is running
        if not (self.server_thread and self.server_thread.isRunning()):
            self._start_server_sync(out_dir)

        url = f"http://127.0.0.1:{self.server_port}/{html_filename}"
        self.log_signal.emit(f"Opening live preview: {url}", "info")
        webbrowser.open(url)

    def _start_server_sync(self, out_dir):
        self.server_thread = HTTPServerThread(out_dir, preferred_port=8080)
        self.server_thread.server_started.connect(self._on_server_started)
        self.server_thread.server_stopped.connect(self._on_server_stopped)
        self.server_thread.server_error.connect(lambda msg: self.log_signal.emit(f"[ERROR] {msg}", "error"))
        self.server_thread.start()
        t = self.current_translations
        self.btn_toggle_server.setText(t.get("tab3_btn_toggle_server_off", "■ Stop Web Server"))
        self.btn_toggle_server.setObjectName("DangerBtn")
        self.btn_toggle_server.setStyleSheet("background-color: #dc2626; color: white; padding: 9px 18px; font-weight: bold; font-size: 12px;")
        self.pill_config.set_status(f"Live (Port {self.server_port})", "running")

    # ----------------------------------------------------------------------
    # Batch & Custom Save WebGL Packaging Engine
    # ----------------------------------------------------------------------
    def build_web_package(self):
        t = self.current_translations
        out_dir = self.input_output_dir.text().strip()
        if not out_dir:
            if self.proj_dir:
                out_dir = os.path.join(self.proj_dir, "05_web_build")
                self.input_output_dir.setText(out_dir)
            else:
                self.log_signal.emit("[ERROR] Please specify an Output Folder.", "error")
                return

        out_dir = os.path.normpath(out_dir)

        # Collect checked models from table
        targets = []
        target_rows = []
        for r in range(self.table_models.rowCount()):
            if self._is_row_checked(r):
                src_item = self.table_models.item(r, 1)
                if src_item:
                    src_file = os.path.normpath(src_item.toolTip())
                    targets.append(src_file)
                    target_rows.append(r)

        if not targets:
            self.log_signal.emit("[ERROR] No models checked for build. Please check at least one model in Step 1.", "error")
            return

        enable_watermark = hasattr(self, 'chk_watermark') and self.chk_watermark.isChecked()
        watermark_text = self.input_watermark_text.text().strip() if hasattr(self, 'input_watermark_text') else ""
        watermark_size = self.spin_watermark_size.value() if hasattr(self, 'spin_watermark_size') else 140
        watermark_opacity = self.spin_watermark_opacity.value() if hasattr(self, 'spin_watermark_opacity') else 6

        # Case 1: Single Model checked -> Prompt Save File Dialog (Choose Name & Location)
        if len(targets) == 1:
            src_file = targets[0]
            row = target_rows[0]
            current_html_name = self.table_models.item(row, 2).text().strip() if self.table_models.item(row, 2) else f"{os.path.basename(src_file)}.html"
            default_save_path = os.path.normpath(os.path.join(out_dir, current_html_name))

            save_title = "Save WebGL Viewer HTML" if self.btn_add_files.text().startswith("➕ Add") else "WebGL 뷰어 HTML 저장 위치 및 파일명 설정"
            chosen_file, _ = QFileDialog.getSaveFileName(
                self, 
                save_title, 
                default_save_path, 
                "HTML Files (*.html);;All Files (*.*)"
            )
            if not chosen_file:
                self.log_signal.emit("Build cancelled by user.", "info")
                return

            chosen_file = os.path.normpath(chosen_file)
            out_dir = os.path.dirname(chosen_file)
            custom_html_name = os.path.basename(chosen_file)

            # Update UI
            self.input_output_dir.setText(out_dir)
            self.table_models.blockSignals(True)
            self.table_models.item(row, 2).setText(custom_html_name)
            self.table_models.blockSignals(False)

            if src_file in self.model_configs:
                self.model_configs[src_file]["html_name"] = custom_html_name

            os.makedirs(out_dir, exist_ok=True)
            self._ensure_local_libs(out_dir)

            try:
                built_name = self._build_single_model(
                    src_file, out_dir, custom_html_name, 
                    is_preview=False, enable_watermark=enable_watermark, watermark_text=watermark_text,
                    watermark_size=watermark_size, watermark_opacity=watermark_opacity
                )
                self.pill_config.set_status("1 Built", "success")
                wm_msg = f" [🛡️ Watermark: {watermark_size}px, {watermark_opacity}%]" if (enable_watermark and watermark_text) else ""
                self.log_signal.emit(f"[SUCCESS] Successfully built WebGL package{wm_msg}:\n➔ {chosen_file}", "success")
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Failed to build {os.path.basename(src_file)}: {e}", "error")
            return

        # Case 2: Multiple Models checked -> Prompt Directory Dialog (Choose Batch Location)
        batch_title = "Select Output Folder for Batch WebGL Build" if self.btn_add_files.text().startswith("➕ Add") else "일괄 WebGL 빌드 저장 폴더 선택"
        chosen_dir = QFileDialog.getExistingDirectory(self, batch_title, out_dir)
        if not chosen_dir:
            self.log_signal.emit("Batch build cancelled by user.", "info")
            return

        out_dir = os.path.normpath(chosen_dir)
        self.input_output_dir.setText(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        self._ensure_local_libs(out_dir)
        success_count = 0

        for src_file in targets:
            try:
                self._build_single_model(
                    src_file, out_dir, 
                    is_preview=False, enable_watermark=enable_watermark, watermark_text=watermark_text,
                    watermark_size=watermark_size, watermark_opacity=watermark_opacity
                )
                success_count += 1
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Failed to build {os.path.basename(src_file)}: {e}", "error")

        if success_count > 0:
            self.pill_config.set_status(f"{success_count} Built", "success")
            wm_msg = f" [🛡️ Watermark: {watermark_size}px, {watermark_opacity}%]" if (enable_watermark and watermark_text) else ""
            self.log_signal.emit(f"[SUCCESS] Successfully built {success_count} WebGL packages{wm_msg} in:\n➔ {out_dir}", "success")

    def _build_single_model(self, src_file, out_dir, override_html_name=None, is_preview=False, enable_watermark=False, watermark_text="", watermark_size=140, watermark_opacity=6):
        fmt = _detect_model_format(src_file)
        src_name = os.path.basename(src_file)
        base_name, _ = os.path.splitext(src_name)

        # Get configured HTML output filename for this model
        config = self.model_configs.get(src_file, {})
        html_filename = override_html_name or config.get("html_name", f"{base_name}.html")
        if not html_filename.lower().endswith('.html'):
            html_filename += '.html'

        display_title = f"Points & Reality 3DGS - {base_name}"

        # Get camera profile for this specific model
        cam_pos = config.get("pos", [0.0, 1.2, 3.8])
        cam_target = config.get("target", [0.0, 0.0, 0.0])
        cam_fov = config.get("fov", 50)

        # Link or copy model file into output directory
        dst_model = os.path.normpath(os.path.join(out_dir, src_name))
        if os.path.normpath(src_file) != dst_model:
            if os.path.exists(dst_model):
                os.remove(dst_model)
            try:
                os.link(src_file, dst_model)
            except Exception:
                shutil.copyfile(src_file, dst_model)

        # --- Route A: .sog (SuperSplat) Standalone Engine ---
        if fmt == 'sog':
            template_file = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "supersplat_template.html"))
            with open(template_file, 'r', encoding='utf-8', errors='ignore') as f:
                template_content = f.read()

            with open(src_file, 'rb') as bf:
                b64_data = base64.b64encode(bf.read()).decode('ascii')

            camera_settings = {
                "camera": {
                    "fov": cam_fov,
                    "position": cam_pos,
                    "target": cam_target,
                    "startAnim": "none"
                },
                "background": {"color": [0, 0, 0]},
                "animTracks": []
            }
            settings_json = json.dumps(camera_settings)

            if is_preview:
                overlays_html = '''
    <!-- Points & Reality Camera Sync Tool (Preview Only) -->
    <div id="points-reality-cam-hud" style="position:fixed; top:16px; left:16px; z-index:999999; display:flex; flex-direction:column; gap:6px; font-family:'Segoe UI',-apple-system,sans-serif;">
        <button id="btn-copy-cam" style="background:linear-gradient(135deg, #0284c7, #0369a1); color:#fff; border:1px solid #38bdf8; padding:10px 18px; border-radius:8px; font-size:13px; font-weight:700; cursor:pointer; backdrop-filter:blur(10px); box-shadow:0 8px 24px rgba(0,0,0,0.6); display:flex; align-items:center; gap:8px; transition:all 0.2s ease;">
            📷 현재 카메라 시점 복사 (Copy View)
        </button>
        <div id="cam-coords-display" style="background:rgba(15,23,42,0.92); color:#7dd3fc; border:1px solid rgba(56,189,248,0.5); border-radius:6px; padding:8px 12px; font-size:11px; font-family:monospace; backdrop-filter:blur(8px); box-shadow:0 4px 16px rgba(0,0,0,0.6); line-height:1.5;">
            <div><b>Camera Pos:</b> <span id="lbl-cam-pos">[0.000, 0.000, 0.000]</span></div>
            <div><b>Look Target:</b> <span id="lbl-cam-tgt">[0.000, 0.000, 0.000]</span></div>
            <div><b>FOV:</b> <span id="lbl-cam-fov">50</span>° &nbsp;|&nbsp; <b>Pitch/Yaw:</b> <span id="lbl-cam-rot">0°, 0°</span></div>
        </div>
    </div>
    <script>
        (function() {
            const btn = document.getElementById('btn-copy-cam');
            const lblPos = document.getElementById('lbl-cam-pos');
            const lblTgt = document.getElementById('lbl-cam-tgt');
            const lblFov = document.getElementById('lbl-cam-fov');
            const lblRot = document.getElementById('lbl-cam-rot');

            function getActiveCameraData() {
                let pos = [0.0, 1.2, 3.8];
                let target = [0.0, 0.0, 0.0];
                let fov = 50;
                let pitch = 0;
                let yaw = 0;

                try {
                    let camObj = null;
                    if (window.viewerInstance && window.viewerInstance.cameraManager && window.viewerInstance.cameraManager.camera) {
                        camObj = window.viewerInstance.cameraManager.camera;
                    }

                    if (camObj && camObj.position) {
                        pos = [
                            parseFloat(camObj.position.x.toFixed(3)),
                            parseFloat(camObj.position.y.toFixed(3)),
                            parseFloat(camObj.position.z.toFixed(3))
                        ];

                        pitch = camObj.angles.x;
                        yaw = camObj.angles.y;

                        const rad = Math.PI / 180;
                        const p_rad = pitch * rad;
                        const y_rad = yaw * rad;

                        const fwd_x = -Math.sin(y_rad) * Math.cos(p_rad);
                        const fwd_y = Math.sin(p_rad);
                        const fwd_z = -Math.cos(y_rad) * Math.cos(p_rad);
                        const dist = camObj.distance || 3.0;

                        target = [
                            parseFloat((pos[0] + fwd_x * dist).toFixed(3)),
                            parseFloat((pos[1] + fwd_y * dist).toFixed(3)),
                            parseFloat((pos[2] + fwd_z * dist).toFixed(3))
                        ];

                        fov = Math.round(camObj.fov || 50);
                    }
                } catch(e) {
                    console.warn("Camera read error:", e);
                }

                return { position: pos, target: target, fov: fov, pitch: pitch, yaw: yaw };
            }

            function updateHUDLoop() {
                const data = getActiveCameraData();
                if (lblPos) lblPos.innerText = '[' + data.position.map(n => n.toFixed(3)).join(', ') + ']';
                if (lblTgt) lblTgt.innerText = '[' + data.target.map(n => n.toFixed(3)).join(', ') + ']';
                if (lblFov) lblFov.innerText = data.fov;
                if (lblRot) lblRot.innerText = data.pitch.toFixed(1) + '°, ' + data.yaw.toFixed(1) + '°';
                requestAnimationFrame(updateHUDLoop);
            }
            requestAnimationFrame(updateHUDLoop);

            if (btn) {
                btn.addEventListener('click', function() {
                    const data = getActiveCameraData();
                    const jsonStr = JSON.stringify({
                        position: data.position,
                        target: data.target,
                        fov: data.fov
                    });

                    if (navigator.clipboard && window.isSecureContext) {
                        navigator.clipboard.writeText(jsonStr);
                    } else {
                        const el = document.createElement('textarea');
                        el.value = jsonStr;
                        el.style.position = 'fixed';
                        el.style.left = '-9999px';
                        document.body.appendChild(el);
                        el.select();
                        document.execCommand('copy');
                        document.body.removeChild(el);
                    }

                    btn.style.background = '#16a34a';
                    btn.style.borderColor = '#4ade80';
                    btn.innerHTML = '✅ 복사 완료! (Points & Reality 앱에서 [Paste] 클릭)';

                    setTimeout(function() {
                        btn.style.background = 'linear-gradient(135deg, #0284c7, #0369a1)';
                        btn.style.borderColor = '#38bdf8';
                        btn.innerHTML = '📷 현재 카메라 시점 복사 (Copy View)';
                    }, 4000);
                });
            }
        })();
    </script>
'''
            else:
                # Final Release / Delivery Mode: Brand Header + Hint (No Copy Button)
                overlays_html = f'''
    <!-- Points & Reality Final Branding Header -->
    <div id="points-reality-brand-header" style="position:fixed; top:16px; left:16px; z-index:99999; display:flex; align-items:center; gap:12px; background:rgba(15,23,42,0.85); backdrop-filter:blur(14px); border:1px solid rgba(56,189,248,0.35); border-radius:10px; padding:9px 18px; box-shadow:0 10px 32px rgba(0,0,0,0.6); pointer-events:auto; font-family:'Segoe UI',-apple-system,sans-serif; user-select:none;">
        <span style="font-weight:900; font-size:14px; color:#38bdf8; letter-spacing:0.8px; display:flex; align-items:center; gap:6px;">✨ Points & Reality 3DGS</span>
        <span style="color:#475569; font-size:13px;">|</span>
        <span style="color:#f8fafc; font-size:13px; font-weight:600; letter-spacing:0.3px;">{display_title}</span>
    </div>
    <div id="points-reality-controls-hint" style="position:fixed; top:16px; right:16px; z-index:99999; display:flex; align-items:center; gap:8px; background:rgba(15,23,42,0.75); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:8px 14px; font-size:11.5px; color:#94a3b8; font-family:'Segoe UI',-apple-system,sans-serif; pointer-events:none; user-select:none;">
        🖱️ <span style="color:#e2e8f0; font-weight:600;">Left:</span> Orbit &nbsp;|&nbsp; 🖱️ <span style="color:#e2e8f0; font-weight:600;">Right:</span> Pan &nbsp;|&nbsp; 🔍 <span style="color:#e2e8f0; font-weight:600;">Wheel:</span> Zoom
    </div>
'''
                if enable_watermark:
                    overlays_html += _generate_watermark_html(watermark_text, font_size_px=watermark_size, opacity_pct=watermark_opacity)

            contents_line = f'contents: fetch("data:application/octet-stream;base64,{b64_data}"),\n                '
            final_html = template_content.replace('{{TITLE}}', display_title)
            final_html = final_html.replace('{{MODEL_URL}}', f"./{src_name}")
            final_html = final_html.replace('{{CONTENTS_LINE}}', contents_line)
            final_html = final_html.replace('{{SETTINGS_JSON}}', settings_json)
            final_html = final_html.replace('{{POINTS_REALITY_OVERLAYS}}', overlays_html).replace('{{SPLATIAL_OVERLAYS}}', overlays_html)

            html_path = os.path.normpath(os.path.join(out_dir, html_filename))
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(final_html)

            size_mb = os.path.getsize(html_path) / (1024 * 1024)
            wm_tag = f" [🛡️ Watermark: {watermark_size}px, {watermark_opacity}%]" if (enable_watermark and watermark_text) else ""
            self.log_signal.emit(f"Built SuperSplat Standalone{wm_tag}: {html_filename} ({size_mb:.1f} MB) [Cam: {cam_pos}]", "info")
            return html_filename

        # --- Route B: .ply / .splat / .spz Offline GaussianSplats3D Viewer ---
        html_content = _generate_ply_viewer_html(
            display_title, src_name, cam_pos, cam_target, cam_fov, 
            is_preview=is_preview, enable_watermark=enable_watermark, watermark_text=watermark_text,
            watermark_size=watermark_size, watermark_opacity=watermark_opacity
        )
        html_path = os.path.normpath(os.path.join(out_dir, html_filename))
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        size_kb = os.path.getsize(html_path) / 1024
        wm_tag = " [🛡️ Watermark]" if (enable_watermark and watermark_text) else ""
        self.log_signal.emit(f"Built 3DGS Viewer{wm_tag}: {html_filename} ({size_kb:.1f} KB) [Cam: {cam_pos}]", "info")
        self._update_models_manifest(out_dir)
        return html_filename

    def _update_models_manifest(self, out_dir):
        """Automatically create/update models.json manifest in the output folder."""
        try:
            out_dir = os.path.normpath(out_dir)
            if not os.path.exists(out_dir):
                return
            html_files = [f for f in os.listdir(out_dir) if f.lower().endswith('.html')]
            manifest = {
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_models": len(html_files),
                "models": []
            }
            for h in sorted(html_files):
                base = os.path.splitext(h)[0]
                manifest["models"].append({
                    "title": base,
                    "filename": h,
                    "path": f"05_web_build/{h}",
                    "is_index": (h.lower() == "index.html")
                })
            manifest_file = os.path.join(out_dir, "models.json")
            with open(manifest_file, 'w', encoding='utf-8') as mf:
                json.dump(manifest, mf, indent=2)
        except Exception:
            pass

    # ----------------------------------------------------------------------
    # Vercel / GitHub Web Viewer Upload & Sync Dialog
    # ----------------------------------------------------------------------
    def upload_to_web(self):
        out_dir = self.input_output_dir.text().strip()
        if not out_dir and self.proj_dir:
            out_dir = os.path.join(self.proj_dir, "05_web_build")
        if not out_dir:
            repo_root = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            out_dir = os.path.join(repo_root, "05_web_build")

        os.makedirs(out_dir, exist_ok=True)
        dlg = WebPublishManagerDialog(out_dir, self, getattr(self, 'current_translations', {}))
        dlg.exec_()

    def _on_upload_success(self, msg):
        t = getattr(self, 'current_translations', {})
        if hasattr(self, 'btn_upload_web') and self.btn_upload_web is not None:
            self.btn_upload_web.setEnabled(True)
            self.btn_upload_web.setText(t.get("tab3_btn_upload_web", "Upload & Cloud Showroom (Vercel)"))
        self.pill_config.set_status("Live (Vercel)", "success")
        self.log_signal.emit(f"[SUCCESS] 🚀 {msg}", "success")

    def _on_upload_error(self, err_msg):
        t = getattr(self, 'current_translations', {})
        if hasattr(self, 'btn_upload_web') and self.btn_upload_web is not None:
            self.btn_upload_web.setEnabled(True)
            self.btn_upload_web.setText(t.get("tab3_btn_upload_web", "Upload & Cloud Showroom (Vercel)"))
        self.pill_config.set_status("Upload Error", "error")
        self.log_signal.emit(f"[ERROR] {err_msg}", "error")

    # ----------------------------------------------------------------------
    # Local Server Control
    # ----------------------------------------------------------------------
    def toggle_preview_server(self):
        try:
            out_dir = self.input_output_dir.text().strip()
            if not out_dir and self.proj_dir:
                out_dir = os.path.join(self.proj_dir, "05_web_build")
            if not out_dir:
                repo_root = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                out_dir = os.path.join(repo_root, "05_web_build")

            out_dir = os.path.normpath(out_dir)
            os.makedirs(out_dir, exist_ok=True)

            if self.server_thread and self.server_thread.isRunning():
                self.server_thread.stop()
                if hasattr(self, 'btn_server_circle') and self.btn_server_circle is not None:
                    self.btn_server_circle.setText("⚪ Off")
                    self.btn_server_circle.setStyleSheet("""
                        QPushButton {
                            background-color: #171922;
                            border: 1px solid #282d3c;
                            border-radius: 11px;
                            color: #94a3b8;
                            font-size: 11px;
                            font-weight: 600;
                            min-height: 22px;
                            max-height: 22px;
                            padding: 1px 10px;
                        }
                        QPushButton:hover {
                            background-color: #202636;
                            border-color: #3b465c;
                            color: #ffffff;
                        }
                    """)
                self.pill_config.set_status("Server Stopped", "idle")
                self.log_signal.emit("Local Web Server stopped.", "info")
                return

            self._start_server_sync(out_dir)
        except Exception as ex:
            self.log_signal.emit(f"[ERROR] Server toggle error: {str(ex)}", "error")

    def _start_server_sync(self, out_dir):
        try:
            out_dir = os.path.normpath(out_dir)
            os.makedirs(out_dir, exist_ok=True)
            if self.server_thread and self.server_thread.isRunning():
                return
            self.server_thread = HTTPServerThread(out_dir, preferred_port=8080)
            self.server_thread.server_started.connect(self._on_server_started)
            self.server_thread.server_stopped.connect(self._on_server_stopped)
            self.server_thread.server_error.connect(lambda err: self.log_signal.emit(f"[SERVER ERROR] {err}", "error"))
            self.server_thread.start()
        except Exception as ex:
            self.log_signal.emit(f"[ERROR] Failed to start local server: {str(ex)}", "error")

    def _on_server_started(self, port):
        self.server_port = port
        url = f"http://127.0.0.1:{port}/"
        if hasattr(self, 'btn_server_circle') and self.btn_server_circle is not None:
            self.btn_server_circle.setText(f"🟢 {port}")
            self.btn_server_circle.setStyleSheet("""
                QPushButton {
                    background-color: #14281e;
                    border: 1px solid #235438;
                    border-radius: 11px;
                    color: #4ade80;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 22px;
                    max-height: 22px;
                    padding: 1px 10px;
                }
                QPushButton:hover {
                    background-color: #1a3829;
                    border-color: #34d399;
                }
            """)
        self.pill_config.set_status(f"Live (Port {port})", "running")
        self.log_signal.emit(f"[SUCCESS] WebGL Server running:\n➔ {url}", "success")

    def _on_server_stopped(self):
        if hasattr(self, 'btn_server_circle') and self.btn_server_circle is not None:
            self.btn_server_circle.setText("⚪ Off")
            self.btn_server_circle.setStyleSheet("""
                QPushButton {
                    background-color: #171922;
                    border: 1px solid #282d3c;
                    border-radius: 11px;
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: 600;
                    min-height: 22px;
                    max-height: 22px;
                    padding: 1px 10px;
                }
                QPushButton:hover {
                    background-color: #202636;
                    border-color: #3b465c;
                    color: #ffffff;
                }
            """)
        self.pill_config.set_status("Server Stopped", "idle")

    def update_language(self, t):
        self.current_translations = t

        # Card Titles
        self.card_source.setTitle(
            t.get("tab3_card1_title", "WebGL Models & Output Filenames"), 
            t.get("tab3_card1_sub", "Manage splat assets and configure individual HTML output filenames")
        )
        self.card_camera.setTitle(
            t.get("tab3_card2_title", "Camera Viewport Configuration"), 
            t.get("tab3_card2_sub", "Configure initial camera angle and synchronize viewpoint coordinates")
        )
        self.card_config.setTitle(
            t.get("tab3_card3_title", "Output Destination & Web Publishing"), 
            t.get("tab3_card3_sub", "Specify destination directory, build WebGL packages, and upload to cloud")
        )

        # Toolbar Buttons
        self.btn_add_files.setText(t.get("tab3_btn_add_files", "Add Files..."))
        self.btn_scan_proj.setText(t.get("tab3_btn_scan_proj", "Scan Folder"))
        if hasattr(self, 'btn_select_all') and self.btn_select_all is not None:
            self.btn_select_all.setText(t.get("tab3_btn_select_all", "Select All"))
        self.btn_set_index.setText(t.get("tab3_btn_set_index", "Set 1st as index.html"))
        self.btn_remove_row.setText(t.get("tab3_btn_remove", "Remove"))
        self.btn_clear_table.setText(t.get("tab3_btn_clear", "Clear All"))

        # Table Column Headers
        build_label = t.get("tab3_tbl_col_build", "Build")
        clean_build = build_label.replace("☑️", "").replace("☑", "").replace("☐", "").strip()
        self.table_models.setHorizontalHeaderLabels([
            f"{clean_build}",
            t.get("tab3_tbl_col_model", "Source Model"),
            t.get("tab3_tbl_col_output", "Output HTML File"),
            t.get("tab3_tbl_col_cam", "Camera Viewport"),
            t.get("tab3_tbl_col_action", "Action")
        ])
        self._update_build_header()

        # Step 2 Widgets
        self.btn_live_preview_cam.setText(t.get("tab3_btn_open_viewer", "Adjust View in Browser"))
        self.btn_paste_cam.setText(t.get("tab3_btn_paste_cam", "Paste Camera View"))
        self.lbl_presets.setText(t.get("tab3_lbl_presets", "Presets:"))
        self.btn_cam_front.setText(t.get("tab3_btn_cam_front", "Front"))
        self.btn_cam_quarter.setText(t.get("tab3_btn_cam_quarter", "Quarter (3/4)"))
        self.btn_cam_side.setText(t.get("tab3_btn_cam_side", "Side"))
        self.btn_cam_top.setText(t.get("tab3_btn_cam_top", "Top-Down"))
        if hasattr(self, 'lbl_saved_views') and self.lbl_saved_views is not None:
            self.lbl_saved_views.setText(t.get("tab3_lbl_saved_views", "Saved Views:"))
        if hasattr(self, 'btn_save_cam_preset') and self.btn_save_cam_preset is not None:
            self.btn_save_cam_preset.setText(t.get("tab3_btn_save_cam_preset", "Save View"))
        if hasattr(self, 'btn_del_cam_preset') and self.btn_del_cam_preset is not None:
            self.btn_del_cam_preset.setText(t.get("tab3_btn_del_cam_preset", "Delete"))
        self._refresh_saved_views_combo()
        self.lbl_cam_pos_title.setText(t.get('tab3_lbl_cam_pos', 'Position (X,Y,Z):'))
        self.lbl_cam_tgt_title.setText(t.get('tab3_lbl_cam_tgt', 'Target:'))
        self.lbl_cam_fov_title.setText(t.get('tab3_lbl_cam_fov', 'FOV:'))

        # Step 3 Widgets
        self.lbl_dest_title.setText(t.get("tab3_lbl_output_folder", "Output Folder:"))
        self.btn_browse_output.setText(t.get("tab3_btn_browse_output", "Browse..."))
        if hasattr(self, 'chk_watermark') and self.chk_watermark is not None:
            self.chk_watermark.setText(t.get("tab3_chk_watermark", "Client Review Watermark"))
        if hasattr(self, 'input_watermark_text') and self.input_watermark_text is not None:
            self.input_watermark_text.setPlaceholderText(t.get("tab3_placeholder_watermark", "Watermark Text (e.g. Points & Reality)"))
        if hasattr(self, 'lbl_watermark_size') and self.lbl_watermark_size is not None:
            self.lbl_watermark_size.setText(t.get("tab3_lbl_watermark_size", "Size:"))
        if hasattr(self, 'lbl_watermark_opacity') and self.lbl_watermark_opacity is not None:
            self.lbl_watermark_opacity.setText(t.get("tab3_lbl_watermark_opacity", "Opacity:"))
        self.btn_build_web.setText(t.get("tab3_btn_build", "Build Selected WebGL Packages"))
        if hasattr(self, 'btn_upload_web') and self.btn_upload_web is not None:
            self.btn_upload_web.setText(t.get("tab3_btn_upload_web", "Upload & Cloud Showroom (Vercel)"))
        if hasattr(self, 'btn_toggle_server') and self.btn_toggle_server is not None:
            is_running = self.server_thread and self.server_thread.isRunning()
            self.btn_toggle_server.setText(
                t.get("tab3_btn_toggle_server_off", "Stop Local Server") if is_running else t.get("tab3_btn_toggle_server_on", "Start Local Server")
            )
        self.btn_open_web.setText(t.get("tab3_btn_open_folder", "Open Web Build Folder"))

        # Row Action buttons in table
        for r in range(self.table_models.rowCount()):
            cell_widget = self.table_models.cellWidget(r, 4)
            if isinstance(cell_widget, QPushButton):
                cell_widget.setText(t.get("tab3_btn_row_preview", "Preview"))
            elif cell_widget:
                btn = cell_widget.findChild(QPushButton)
                if btn:
                    btn.setText(t.get("tab3_btn_row_preview", "Preview"))

        self.on_table_selection_changed()