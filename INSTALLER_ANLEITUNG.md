# 🛠️ Windows-Installer erstellen - Schritt-für-Schritt Anleitung

Diese Anleitung erklärt, wie Sie einen professionellen Windows-Installer (.exe Setup-Datei) für den Colab GUI Generator erstellen.

---

## 📋 Voraussetzungen

### 1. Python 3.10+ installieren

1. Laden Sie Python von [python.org](https://www.python.org/downloads/) herunter
2. **WICHTIG**: Aktivieren Sie "Add Python to PATH" während der Installation
3. Starten Sie den PC neu

### 2. Python-Pakete installieren

Öffnen Sie die Eingabeaufforderung (cmd) und führen Sie aus:

```cmd
pip install pyinstaller pywebview requests openai pillow
```

### 3. Installer-Tool installieren (eines davon)

**Option A: Inno Setup (empfohlen)**
- Download: https://jrsoftware.org/isdl.php
- Installieren Sie die Version 6.x

**Option B: NSIS**
- Download: https://nsis.sourceforge.io/Download
- Installieren Sie die Version 3.x

---

## 🚀 Installer erstellen

### Methode 1: Automatisch (empfohlen)

1. Entpacken Sie das Projektarchiv
2. Öffnen Sie die Eingabeaufforderung im Projektordner
3. Führen Sie aus:

```cmd
python create_installer.py
```

Das Skript:
- Prüft alle Abhängigkeiten
- Erstellt die .exe mit PyInstaller
- Erstellt den Installer mit Inno Setup oder NSIS
- Zeigt das Ergebnis an

### Methode 2: Manuell

**Schritt 1: Executable erstellen**

```cmd
python build_exe.py
```

oder direkt mit PyInstaller:

```cmd
pyinstaller --noconfirm --clean --name=ColabGUIGenerator --onefile --windowed --add-data "core;core" --hidden-import=webview --hidden-import=requests --hidden-import=openai main.py
```

**Schritt 2: Installer erstellen**

*Mit Inno Setup:*
1. Öffnen Sie Inno Setup Compiler
2. Öffnen Sie `installer/ColabGUIGenerator_Setup.iss`
3. Drücken Sie F9 oder klicken Sie auf "Compile"

*Mit NSIS:*
1. Rechtsklick auf `installer/ColabGUIGenerator_Setup.nsi`
2. Wählen Sie "Compile NSIS Script"

---

## 📁 Ergebnis

Nach erfolgreichem Build finden Sie im `dist`-Ordner:

| Datei | Beschreibung |
|-------|--------------|
| `ColabGUIGenerator.exe` | Portable Version (keine Installation nötig) |
| `ColabGUIGenerator_Setup_2.0.0.exe` | Windows-Installer mit Setup-Assistent |

---

## 🔧 Anpassungen

### Icon ändern

1. Erstellen Sie eine `.ico`-Datei (256x256 Pixel empfohlen)
2. Speichern Sie sie als `assets/icon.ico`
3. Führen Sie den Build erneut aus

### Version ändern

Bearbeiten Sie diese Dateien:
- `main.py`: `APP_VERSION = "2.0.0"`
- `installer/ColabGUIGenerator_Setup.iss`: `#define MyAppVersion "2.0.0"`
- `installer/ColabGUIGenerator_Setup.nsi`: `!define PRODUCT_VERSION "2.0.0"`

### Installer-Optionen

**Inno Setup** (`ColabGUIGenerator_Setup.iss`):
- `DefaultDirName`: Installationsverzeichnis
- `OutputBaseFilename`: Name der Setup-Datei
- `Compression`: Komprimierungsmethode

**NSIS** (`ColabGUIGenerator_Setup.nsi`):
- `InstallDir`: Installationsverzeichnis
- `OutFile`: Name der Setup-Datei
- `SetCompressor`: Komprimierungsmethode

---

## ❓ Häufige Probleme

### "PyInstaller nicht gefunden"
```cmd
pip install pyinstaller
```

### "ModuleNotFoundError: No module named 'webview'"
```cmd
pip install pywebview
```

### "Inno Setup Compiler nicht gefunden"
- Stellen Sie sicher, dass Inno Setup installiert ist
- Standardpfad: `C:\Program Files (x86)\Inno Setup 6\`

### "Die .exe startet nicht"
- Installieren Sie das [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Prüfen Sie, ob alle Abhängigkeiten korrekt gebündelt wurden

### "Antivirus blockiert die .exe"
- Dies ist normal bei selbst erstellten Executables
- Fügen Sie eine Ausnahme hinzu oder signieren Sie die Datei

---

## 📞 Support

Bei Problemen:
1. Prüfen Sie die Fehlermeldungen in der Konsole
2. Stellen Sie sicher, dass alle Voraussetzungen erfüllt sind
3. Versuchen Sie einen sauberen Build (löschen Sie `build` und `dist` Ordner)
