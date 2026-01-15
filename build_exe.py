#!/usr/bin/env python3
"""
=============================================================================
COLAB GUI GENERATOR - Build Script für Windows .exe
=============================================================================
Dieses Skript erstellt eine eigenständige Windows-Executable mit PyInstaller.
Führen Sie es auf Ihrem Windows-PC aus.

VERWENDUNG:
    python build_exe.py

VORAUSSETZUNGEN:
    pip install pyinstaller pywebview requests openai pillow
=============================================================================
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """Prüft ob PyInstaller installiert ist"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} gefunden")
        return True
    except ImportError:
        print("✗ PyInstaller nicht gefunden")
        print("  Installiere mit: pip install pyinstaller")
        return False


def check_dependencies():
    """Prüft alle Abhängigkeiten"""
    required = ['webview', 'requests', 'openai', 'PIL']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg} gefunden")
        except ImportError:
            missing.append(pkg)
            print(f"✗ {pkg} fehlt")
    
    if missing:
        print("\nFehlende Pakete installieren:")
        print("pip install pywebview requests openai pillow")
        return False
    
    return True


def clean_build():
    """Bereinigt alte Build-Dateien"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['ColabGUIGenerator.spec']
    
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"✓ {d}/ entfernt")
    
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"✓ {f} entfernt")


def build_exe():
    """Erstellt die Windows .exe"""
    
    # PyInstaller Optionen
    options = [
        'pyinstaller',
        '--noconfirm',
        '--clean',
        '--name=ColabGUIGenerator',
        '--onefile',           # Alles in einer Datei
        '--windowed',          # Kein Konsolenfenster
        '--add-data=core;core',  # Core-Module einbinden
        
        # Versteckte Imports für pywebview
        '--hidden-import=webview',
        '--hidden-import=webview.platforms.winforms',
        '--hidden-import=webview.platforms.edgechromium',
        '--hidden-import=webview.platforms.cef',
        '--hidden-import=clr',
        '--hidden-import=pythonnet',
        
        # Weitere Imports
        '--hidden-import=requests',
        '--hidden-import=openai',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=json',
        '--hidden-import=base64',
        '--hidden-import=threading',
        
        # Ausschlüsse (reduziert Dateigröße)
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=pytest',
        '--exclude-module=unittest',
        
        # Hauptdatei
        'main.py'
    ]
    
    print("\n" + "="*60)
    print("ERSTELLE WINDOWS EXECUTABLE")
    print("="*60 + "\n")
    
    result = subprocess.run(options, capture_output=False)
    
    return result.returncode == 0


def main():
    print("\n" + "="*60)
    print("COLAB GUI GENERATOR - Build für Windows")
    print("="*60 + "\n")
    
    # Ins Projektverzeichnis wechseln
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Arbeitsverzeichnis: {script_dir}\n")
    
    # Prüfungen
    print("[1/4] Prüfe Abhängigkeiten...")
    if not check_pyinstaller():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Bereinigen
    print("\n[2/4] Bereinige alte Builds...")
    clean_build()
    
    # Build
    print("\n[3/4] Erstelle Executable...")
    if not build_exe():
        print("\n✗ Build fehlgeschlagen!")
        sys.exit(1)
    
    # Ergebnis
    print("\n[4/4] Build abgeschlossen!")
    
    exe_path = script_dir / 'dist' / 'ColabGUIGenerator.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"✓ ERFOLG!")
        print(f"{'='*60}")
        print(f"\nDatei: {exe_path}")
        print(f"Größe: {size_mb:.1f} MB")
        print(f"\nSie können die .exe jetzt ausführen oder")
        print(f"mit dem Installer-Skript verpacken.")
    else:
        print("\n✗ Executable nicht gefunden!")
        sys.exit(1)


if __name__ == '__main__':
    main()
