@echo off
:: Points & Reality 3D Web Studio Local Preview Launcher
title Points & Reality Web Studio
cd /d "%~dp0"

echo [INFO] Starting local Web Studio on http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080/index.html
python -m http.server 8080

pause

