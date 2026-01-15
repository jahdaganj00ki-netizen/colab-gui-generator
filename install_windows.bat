@echo off
REM ============================================================================
REM COLAB GUI GENERATOR - Windows Installation
REM ============================================================================
REM Dieses Skript installiert alle Abhängigkeiten und startet die Anwendung
REM ============================================================================

echo.
echo ============================================
echo   COLAB GUI GENERATOR - Installation
echo ============================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo.
    echo Bitte installieren Sie Python 3.10 oder höher von:
    echo https://www.python.org/downloads/
    echo.
    echo WICHTIG: Aktivieren Sie "Add Python to PATH" während der Installation!
    echo.
    pause
    exit /b 1
)

echo [INFO] Python gefunden:
python --version
echo.

echo [1/3] Installiere Abhängigkeiten...
echo.

pip install --upgrade pip
pip install pywebview requests openai pillow

if errorlevel 1 (
    echo.
    echo [FEHLER] Installation fehlgeschlagen!
    echo Versuchen Sie: pip install pywebview requests openai pillow
    pause
    exit /b 1
)

echo.
echo [2/3] Installation abgeschlossen!
echo.

echo [3/3] Starte Colab GUI Generator...
echo.

python main.py

pause
