@echo off
title Aegis Voice Launcher
echo ========================================
echo    AEGIS VOICE - Starting Services...
echo ========================================

:: 1. Kill any existing processes on port 8765
echo Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: 2. Start Backend
echo Starting Python Backend (this takes ~10 seconds to load AI)...
start "Aegis Backend" cmd /k "D:\AegisVoice\start_backend.bat"

:: 3. Wait for backend to fully load the Whisper model
echo Waiting for AI model to load...
timeout /t 12 /nobreak >nul

:: 4. Start UI
echo Starting Electron UI...
start "Aegis UI" cmd /k "D:\AegisVoice\start_ui.bat"

echo.
echo ========================================
echo   Aegis Voice is running!
echo ========================================
echo  - Do not close the black terminal windows.
echo  - The UI window is transparent (invisible).
echo  - Play a scam video to see the red alert.
echo.
echo  Press any key to shut everything down...
pause >nul

:: 5. Cleanup on exit
echo Shutting down...
taskkill /FI "WINDOWTITLE eq Aegis Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Aegis UI*" /F >nul 2>&1
taskkill /IM node.exe /F >nul 2>&1
taskkill /IM python.exe /F >nul 2>&1