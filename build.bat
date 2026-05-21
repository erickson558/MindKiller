@echo off
:: MindKiller - Build script for Windows EXE
:: Generates dist\process_killer_gui.exe in the project folder
:: Usage: double-click or run from terminal

setlocal

set APP=process_killer_gui
set ICO=task_update_folder_progress_icon_142270.ico

echo.
echo ========================================
echo  MindKiller - Building EXE
echo ========================================
echo.

:: Check for pyinstaller
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing requirements...
    pip install -r requirements.txt
)

:: Build single-file exe, no console, with icon
pyinstaller ^
    --onefile ^
    --windowed ^
    --name %APP% ^
    --icon=%ICO% ^
    --add-data "%ICO%;." ^
    %APP%.py

:: Move the exe to the project root
if exist dist\%APP%.exe (
    move /Y dist\%APP%.exe .
    echo.
    echo [OK] Build complete: %APP%.exe is ready in this folder.
) else (
    echo.
    echo [ERROR] Build failed. Check the output above.
    exit /b 1
)

:: Cleanup build artifacts
rmdir /s /q build
del /f /q %APP%.spec

echo.
pause
