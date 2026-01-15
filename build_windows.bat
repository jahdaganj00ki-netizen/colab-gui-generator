@echo off
REM ============================================================================
REM COLAB GUI GENERATOR - Windows Build Script
REM ============================================================================
REM Dieses Skript erstellt eine ausführbare .exe Datei für Windows
REM 
REM VORAUSSETZUNGEN:
REM   - Python 3.10+ installiert
REM   - pip install pyinstaller pywebview requests openai pillow
REM ============================================================================

echo.
echo ============================================
echo   COLAB GUI GENERATOR - Build für Windows
echo ============================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte installieren Sie Python von https://python.org
    pause
    exit /b 1
)

echo [1/4] Prüfe Abhängigkeiten...

REM Installiere Abhängigkeiten
pip install pyinstaller pywebview requests openai pillow --quiet

if errorlevel 1 (
    echo [FEHLER] Konnte Abhängigkeiten nicht installieren!
    pause
    exit /b 1
)

echo [2/4] Bereinige alte Builds...

REM Bereinige alte Builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [3/4] Erstelle Windows-Executable...

REM Erstelle .exe mit PyInstaller
pyinstaller --noconfirm --clean ^
    --name "ColabGUIGenerator" ^
    --onefile ^
    --windowed ^
    --add-data "core;core" ^
    --hidden-import webview ^
    --hidden-import webview.platforms.winforms ^
    --hidden-import webview.platforms.edgechromium ^
    --hidden-import clr ^
    --hidden-import pythonnet ^
    --hidden-import requests ^
    --hidden-import openai ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    main.py

if errorlevel 1 (
    echo [FEHLER] Build fehlgeschlagen!
    pause
    exit /b 1
)

echo [4/4] Build abgeschlossen!
echo.
echo ============================================
echo   ERFOLG! Die .exe wurde erstellt:
echo   dist\ColabGUIGenerator.exe
echo ============================================
echo.

REM Öffne den dist-Ordner
explorer dist

pause
