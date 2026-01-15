#!/usr/bin/env python3
"""
=============================================================================
COLAB GUI GENERATOR - Komplettes Installer-Build-Skript
=============================================================================
Dieses Skript erstellt einen vollständigen Windows-Installer:
1. Baut die Anwendung mit PyInstaller
2. Erstellt den Installer mit Inno Setup oder NSIS

VERWENDUNG:
    python create_installer.py

VORAUSSETZUNGEN:
    - Python 3.10+
    - pip install pyinstaller pywebview requests openai pillow
    - Inno Setup 6+ ODER NSIS 3+ installiert
=============================================================================
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path


class InstallerBuilder:
    """Erstellt den Windows-Installer"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / 'dist'
        self.installer_dir = self.project_dir / 'installer'
        self.assets_dir = self.project_dir / 'assets'
        
    def run(self):
        """Führt den kompletten Build-Prozess aus"""
        print("\n" + "="*70)
        print("   COLAB GUI GENERATOR - INSTALLER ERSTELLEN")
        print("="*70 + "\n")
        
        # Schritt 1: Vorbereitung
        print("[1/5] Vorbereitung...")
        self.prepare_directories()
        self.create_icon()
        self.create_license()
        
        # Schritt 2: Abhängigkeiten prüfen
        print("\n[2/5] Prüfe Abhängigkeiten...")
        if not self.check_dependencies():
            return False
        
        # Schritt 3: PyInstaller Build
        print("\n[3/5] Erstelle Executable mit PyInstaller...")
        if not self.build_exe():
            return False
        
        # Schritt 4: Installer erstellen
        print("\n[4/5] Erstelle Installer...")
        installer_tool = self.find_installer_tool()
        
        if installer_tool == 'inno':
            success = self.build_inno_installer()
        elif installer_tool == 'nsis':
            success = self.build_nsis_installer()
        else:
            print("⚠ Kein Installer-Tool gefunden!")
            print("  Installieren Sie Inno Setup oder NSIS:")
            print("  - Inno Setup: https://jrsoftware.org/isinfo.php")
            print("  - NSIS: https://nsis.sourceforge.io/Download")
            print("\n  Die .exe wurde trotzdem erstellt:")
            print(f"  {self.dist_dir / 'ColabGUIGenerator.exe'}")
            return True
        
        # Schritt 5: Abschluss
        print("\n[5/5] Abschluss...")
        self.show_result()
        
        return success
    
    def prepare_directories(self):
        """Erstellt benötigte Verzeichnisse"""
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        print("  ✓ Verzeichnisse erstellt")
    
    def create_icon(self):
        """Erstellt ein einfaches Icon (Platzhalter)"""
        icon_path = self.assets_dir / 'icon.ico'
        
        if not icon_path.exists():
            # Erstelle ein minimales ICO-File (1x1 Pixel, transparent)
            # In der Praxis sollte hier ein richtiges Icon verwendet werden
            ico_data = bytes([
                0x00, 0x00,  # Reserved
                0x01, 0x00,  # Type (1 = ICO)
                0x01, 0x00,  # Number of images
                # Image entry
                0x10,        # Width (16)
                0x10,        # Height (16)
                0x00,        # Color palette
                0x00,        # Reserved
                0x01, 0x00,  # Color planes
                0x20, 0x00,  # Bits per pixel (32)
                0x68, 0x04, 0x00, 0x00,  # Size of image data
                0x16, 0x00, 0x00, 0x00,  # Offset to image data
            ])
            
            # Füge BMP-Header und Pixeldaten hinzu (16x16, 32-bit)
            bmp_header = bytes([
                0x28, 0x00, 0x00, 0x00,  # Header size
                0x10, 0x00, 0x00, 0x00,  # Width
                0x20, 0x00, 0x00, 0x00,  # Height (doubled for mask)
                0x01, 0x00,              # Planes
                0x20, 0x00,              # Bits per pixel
                0x00, 0x00, 0x00, 0x00,  # Compression
                0x00, 0x04, 0x00, 0x00,  # Image size
                0x00, 0x00, 0x00, 0x00,  # X pixels per meter
                0x00, 0x00, 0x00, 0x00,  # Y pixels per meter
                0x00, 0x00, 0x00, 0x00,  # Colors used
                0x00, 0x00, 0x00, 0x00,  # Important colors
            ])
            
            # Blaue Pixel für das Icon (16x16)
            pixels = bytes([0xFF, 0xD4, 0x00, 0xFF] * 256)  # Cyan/Blau
            mask = bytes([0x00] * 64)  # Keine Transparenz-Maske
            
            with open(icon_path, 'wb') as f:
                f.write(ico_data + bmp_header + pixels + mask)
            
            print("  ✓ Standard-Icon erstellt")
        else:
            print("  ✓ Icon vorhanden")
    
    def create_license(self):
        """Erstellt eine Lizenzdatei"""
        license_path = self.project_dir / 'LICENSE.txt'
        
        if not license_path.exists():
            license_text = """MIT License

Copyright (c) 2024 Colab GUI Generator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
            with open(license_path, 'w') as f:
                f.write(license_text)
            print("  ✓ Lizenzdatei erstellt")
        else:
            print("  ✓ Lizenzdatei vorhanden")
    
    def check_dependencies(self):
        """Prüft alle Abhängigkeiten"""
        required = {
            'pyinstaller': 'PyInstaller',
            'webview': 'pywebview',
            'requests': 'requests',
            'openai': 'openai',
            'PIL': 'Pillow'
        }
        
        missing = []
        for module, package in required.items():
            try:
                __import__(module)
                print(f"  ✓ {package}")
            except ImportError:
                missing.append(package)
                print(f"  ✗ {package} fehlt")
        
        if missing:
            print(f"\n  Installieren mit: pip install {' '.join(missing)}")
            return False
        
        return True
    
    def build_exe(self):
        """Erstellt die .exe mit PyInstaller"""
        os.chdir(self.project_dir)
        
        # Bereinige alte Builds
        for d in ['build', '__pycache__']:
            path = self.project_dir / d
            if path.exists():
                shutil.rmtree(path)
        
        # PyInstaller Befehl
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--noconfirm',
            '--clean',
            '--name=ColabGUIGenerator',
            '--onefile',
            '--windowed',
            f'--add-data=core{os.pathsep}core',
            f'--icon={self.assets_dir / "icon.ico"}',
            '--hidden-import=webview',
            '--hidden-import=webview.platforms.winforms',
            '--hidden-import=webview.platforms.edgechromium',
            '--hidden-import=clr',
            '--hidden-import=pythonnet',
            '--hidden-import=requests',
            '--hidden-import=openai',
            '--hidden-import=PIL',
            '--hidden-import=PIL.Image',
            '--exclude-module=tkinter',
            '--exclude-module=matplotlib',
            '--exclude-module=numpy',
            '--exclude-module=pandas',
            'main.py'
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode != 0:
            print("  ✗ PyInstaller Build fehlgeschlagen!")
            return False
        
        exe_path = self.dist_dir / 'ColabGUIGenerator.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Executable erstellt ({size_mb:.1f} MB)")
            return True
        
        return False
    
    def find_installer_tool(self):
        """Findet verfügbares Installer-Tool"""
        # Prüfe Inno Setup
        inno_paths = [
            r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
            r'C:\Program Files\Inno Setup 6\ISCC.exe',
        ]
        for path in inno_paths:
            if os.path.exists(path):
                self.inno_path = path
                print("  ✓ Inno Setup gefunden")
                return 'inno'
        
        # Prüfe NSIS
        nsis_paths = [
            r'C:\Program Files (x86)\NSIS\makensis.exe',
            r'C:\Program Files\NSIS\makensis.exe',
        ]
        for path in nsis_paths:
            if os.path.exists(path):
                self.nsis_path = path
                print("  ✓ NSIS gefunden")
                return 'nsis'
        
        return None
    
    def build_inno_installer(self):
        """Erstellt Installer mit Inno Setup"""
        script_path = self.installer_dir / 'ColabGUIGenerator_Setup.iss'
        
        if not script_path.exists():
            print(f"  ✗ Inno Setup Skript nicht gefunden: {script_path}")
            return False
        
        cmd = [self.inno_path, str(script_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ✗ Inno Setup fehlgeschlagen: {result.stderr}")
            return False
        
        print("  ✓ Installer mit Inno Setup erstellt")
        return True
    
    def build_nsis_installer(self):
        """Erstellt Installer mit NSIS"""
        script_path = self.installer_dir / 'ColabGUIGenerator_Setup.nsi'
        
        if not script_path.exists():
            print(f"  ✗ NSIS Skript nicht gefunden: {script_path}")
            return False
        
        cmd = [self.nsis_path, str(script_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ✗ NSIS fehlgeschlagen: {result.stderr}")
            return False
        
        print("  ✓ Installer mit NSIS erstellt")
        return True
    
    def show_result(self):
        """Zeigt das Ergebnis an"""
        print("\n" + "="*70)
        print("   BUILD ABGESCHLOSSEN")
        print("="*70)
        
        # Suche nach erstellten Dateien
        files = list(self.dist_dir.glob('*.exe'))
        
        if files:
            print("\nErstellte Dateien:")
            for f in files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  • {f.name} ({size_mb:.1f} MB)")
        
        print("\nNächste Schritte:")
        print("  1. Testen Sie die Installation auf einem anderen PC")
        print("  2. Verteilen Sie die Setup-Datei an Ihre Nutzer")
        print()


def main():
    builder = InstallerBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
