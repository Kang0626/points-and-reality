@echo off
:: Points & Reality 3DGS Pipeline Controller Launcher
title Points & Reality 3DGS Pipeline Controller

:: 배치 파일이 위치한 현재 디렉토리로 이동
cd /d "%~dp0"

:: 콘솔 창을 숨기고 백그라운드에서 파이썬 GUI(main.pyw) 실행
start "" pythonw main.pyw

exit
