# utils.py
import os
import time
import json
import shutil
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

def create_project_structure(base_dir, subfolders):
    for folder in subfolders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

def get_video_metadata(file_path):
    """
    Extracts real duration, resolution, codec, and fps from video using ffprobe.
    Returns a dict with parsed metadata.
    """
    if not shutil.which("ffprobe") or not os.path.exists(file_path):
        return {
            "duration_str": "--:--",
            "duration_sec": 0,
            "resolution": "Unknown",
            "codec": os.path.splitext(file_path)[1].upper().replace(".", ""),
            "fps": 0
        }

    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", file_path
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        if proc.returncode != 0 or not proc.stdout:
            return {
                "duration_str": "--:--",
                "duration_sec": 0,
                "resolution": "Unknown",
                "codec": os.path.splitext(file_path)[1].upper().replace(".", ""),
                "fps": 0
            }

        data = json.loads(proc.stdout)
        video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
        
        # Duration
        duration_sec = 0.0
        if "format" in data and "duration" in data["format"]:
            try:
                duration_sec = float(data["format"]["duration"])
            except ValueError:
                duration_sec = 0.0
        elif video_stream and "duration" in video_stream:
            try:
                duration_sec = float(video_stream["duration"])
            except ValueError:
                duration_sec = 0.0

        mins, secs = divmod(int(duration_sec), 60)
        dur_str = f"{mins:02d}:{secs:02d}"

        # Resolution
        width = video_stream.get("width", 0) if video_stream else 0
        height = video_stream.get("height", 0) if video_stream else 0
        res_label = f"{width}x{height}"
        if width == 3840 or height == 2160:
            res_label = "4K UHD (3840x2160)"
        elif width == 1920 or height == 1080:
            res_label = "FHD (1920x1080)"
        elif width > 0:
            res_label = f"{width}x{height}"

        # Codec
        codec_name = video_stream.get("codec_name", "").upper() if video_stream else ""
        if codec_name == "H264":
            codec_name = "H.264 / AVC"
        elif codec_name in ("HEVC", "H265"):
            codec_name = "H.265 / HEVC"
        elif "PRORES" in codec_name:
            codec_name = "Apple ProRes"
        elif not codec_name:
            codec_name = os.path.splitext(file_path)[1].upper().replace(".", "")

        # FPS
        fps_val = 0.0
        if video_stream and "r_frame_rate" in video_stream:
            try:
                num, den = video_stream["r_frame_rate"].split("/")
                fps_val = round(float(num) / float(den), 2)
            except Exception:
                fps_val = 0.0

        return {
            "duration_str": dur_str,
            "duration_sec": duration_sec,
            "resolution": res_label,
            "codec": codec_name,
            "fps": fps_val
        }
    except Exception:
        return {
            "duration_str": "--:--",
            "duration_sec": 0,
            "resolution": "Unknown",
            "codec": os.path.splitext(file_path)[1].upper().replace(".", ""),
            "fps": 0
        }

class ExtractorThread(QThread):
    progress_update = pyqtSignal(int, str)
    file_status = pyqtSignal(int, str)
    finished_extraction = pyqtSignal(str, bool)

    def __init__(self, tasks, fps, format_type, scale_opt, lut_path, target_dir):
        super().__init__()
        self.tasks = tasks
        self.fps = fps
        self.format_type = format_type
        self.scale_opt = scale_opt
        self.lut_path = lut_path
        self.target_dir = target_dir

    def run(self):
        if not shutil.which("ffmpeg"):
            self.progress_update.emit(0, "[ERROR] FFmpeg가 설치되어 있지 않거나 시스템 PATH에 없습니다.")
            self.finished_extraction.emit(self.target_dir, False)
            return

        total_tasks = len(self.tasks)
        all_success = True
        total_extracted_count = 0

        for idx, (row, file_path) in enumerate(self.tasks):
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.file_status.emit(row, "Extracting...")
            self.progress_update.emit(int((idx / total_tasks) * 100), f"Extracting [{idx+1}/{total_tasks}]: {base_name}")

            # 1. Determine Format & Extension
            ext = ".png"
            pix_fmt = "rgb24"
            extra_args = []

            if "JPG" in self.format_type or "JPEG" in self.format_type:
                ext = ".jpg"
                pix_fmt = "yuvj420p"
                extra_args = ["-q:v", "2"]
            elif "16-bit PNG" in self.format_type:
                ext = ".png"
                pix_fmt = "rgb48be"
            elif "16-bit EXR" in self.format_type:
                ext = ".exr"
                pix_fmt = "rgb48le"
            elif "10-bit WebP" in self.format_type:
                ext = ".webp"
                pix_fmt = "yuv420p10le"
            else: # 8-bit PNG (Default Lossless)
                ext = ".png"
                pix_fmt = "rgb24"

            # 2. Build Video Filter Chain
            filters = [f"fps={self.fps}"]

            if "50%" in self.scale_opt or "Half" in self.scale_opt:
                filters.append("scale=iw*0.5:ih*0.5")
            elif "1080p" in self.scale_opt:
                filters.append("scale=1920:-2")
            elif "2K" in self.scale_opt:
                filters.append("scale=2560:-2")

            if self.lut_path and os.path.exists(self.lut_path):
                clean_lut = self.lut_path.replace("\\", "/").replace(":", "\\:")
                filters.append(f"lut3d='{clean_lut}'")

            vf_string = ",".join(filters)

            sequence_dir = os.path.join(self.target_dir, base_name)
            os.makedirs(sequence_dir, exist_ok=True)
            out_pattern = os.path.join(sequence_dir, f"{base_name}_%04d{ext}")

            cmd = [
                "ffmpeg", "-y",
                "-i", file_path,
                "-vf", vf_string,
                "-pix_fmt", pix_fmt
            ] + extra_args + [out_pattern]

            try:
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
                
                if process.returncode != 0:
                    error_msg = process.stderr[-200:] if process.stderr else "Unknown FFmpeg error"
                    self.progress_update.emit(int((idx / total_tasks) * 100), f"[ERROR] FFmpeg 실패 ({base_name}): {error_msg}")
                    self.file_status.emit(row, "Error")
                    all_success = False
                    continue
                    
                extracted_files = [f for f in os.listdir(sequence_dir) if f.startswith(base_name) and f.endswith(ext)]
                if not extracted_files:
                    self.progress_update.emit(int((idx / total_tasks) * 100), f"[ERROR] 추출된 파일이 없습니다 ({base_name}). 영상 경로를 확인하세요.")
                    self.file_status.emit(row, "Error")
                    all_success = False
                    continue
                    
                count = len(extracted_files)
                total_extracted_count += count
                self.file_status.emit(row, f"Done ({count} frames)")
                
            except Exception as e:
                self.progress_update.emit(int((idx / total_tasks) * 100), f"[ERROR] 시스템 실행 오류: {str(e)}")
                self.file_status.emit(row, "Error")
                all_success = False

        final_msg = f"[SUCCESS] Total {total_extracted_count} frames extracted successfully." if all_success else "[WARNING] Extraction finished with some errors."
        self.progress_update.emit(100, final_msg)
        self.finished_extraction.emit(self.target_dir, all_success)

class FolderWatcherThread(QThread):
    file_detected = pyqtSignal(str, str, str)

    def __init__(self, watch_dir):
        super().__init__()
        self.watch_dir = watch_dir
        self.running = True
        self.seen_files = set()

    def run(self):
        if os.path.exists(self.watch_dir):
            self.seen_files = set(os.listdir(self.watch_dir))
            
        while self.running:
            if os.path.exists(self.watch_dir):
                current_files = set(os.listdir(self.watch_dir))
                new_files = current_files - self.seen_files
                
                for f in new_files:
                    filepath = os.path.join(self.watch_dir, f)
                    try:
                        size_mb = f"{os.path.getsize(filepath) / (1024*1024):.2f}"
                        time_str = time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(filepath)))
                        self.file_detected.emit(filepath, size_mb, time_str)
                    except Exception:
                        pass
                    
                self.seen_files = current_files
            time.sleep(2)

    def stop(self):
        self.running = False
        self.wait()