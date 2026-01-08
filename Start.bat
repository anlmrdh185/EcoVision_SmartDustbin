@echo off
title Smart Dustbin Launcher
color 0A
echo ==================================================
echo      STARTING SMART DUSTBIN SYSTEM...
echo ==================================================
echo.

:: 1. Start the AI (Camera & Arduino) in a new window
echo [1/2] Launching AI System...
start "Smart Bin AI (DO NOT CLOSE)" cmd /k "python main_yolo.py"

:: 2. Wait 3 seconds to let AI load first
timeout /t 3 >nul

:: 3. Start the Dashboard (Streamlit) in a new window
echo [2/2] Launching Dashboard...
start "Dashboard" cmd /k "python -m streamlit run dashboard.py"

echo.
echo ==================================================
echo      SYSTEM IS RUNNING! 
echo      Close the other windows to stop.
echo ==================================================
pause