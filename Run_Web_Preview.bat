@echo off
:: Points & Reality 3D Web Showroom Local Preview Launcher
title Points & Reality Web Showroom
cd /d "%~dp0"

echo [INFO] Starting local Web Showroom on http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080/showroom.html
python -m http.server 8080

pause
