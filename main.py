#!/usr/bin/env python3
"""
=============================================================================
COLAB GUI GENERATOR - HAUPTANWENDUNG v2.0
=============================================================================
Eine Desktop-Anwendung für Windows, die:
1. Google Colab Notebooks (.ipynb) analysiert
2. Automatisch eine passende GUI generiert
3. OpenAI für intelligente Funktionen nutzt
4. Automatischen Hell-/Dunkel-Modus unterstützt
5. Google Account-Auswahl ermöglicht

VERWENDUNG:
    python main.py                    # Startet die Anwendung
    python main.py notebook.ipynb     # Öffnet direkt ein Notebook
    python main.py https://github.com/user/repo/blob/main/notebook.ipynb
=============================================================================
"""

import sys
import os
import json
import base64
import argparse
import tempfile
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Prüfe Abhängigkeiten
def check_dependencies():
    """Prüft und installiert fehlende Abhängigkeiten"""
    missing = []
    
    try:
        import webview
    except ImportError:
        missing.append('pywebview')
    
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    if missing:
        print(f"Fehlende Pakete: {', '.join(missing)}")
        print("Installiere mit: pip install " + ' '.join(missing))
        sys.exit(1)

check_dependencies()

import webview
import requests

from core.notebook_parser import NotebookParser, NotebookAnalysis
from core.gui_generator import GUIGenerator
from core.colab_manager import ColabManager
from core.theme_manager import get_theme_manager, ThemeMode
from core.ai_assistant import get_ai_assistant


class EnhancedColabAPI:
    """
    Erweiterte API-Klasse für pywebview.
    Enthält alle Funktionen, die von JavaScript aufgerufen werden können.
    """
    
    def __init__(self, colab_manager: ColabManager, analysis: Optional[NotebookAnalysis] = None):
        self.manager = colab_manager
        self.analysis = analysis
        self.ai = get_ai_assistant()
        self.theme = get_theme_manager()
        self.last_image_data: Optional[bytes] = None
        self._window = None
    
    def set_window(self, window):
        """Setzt das Fenster-Objekt"""
        self._window = window
    
    # === Verbindungs-Funktionen ===
    
    def set_colab_url(self, url: str) -> Dict:
        """Setzt die Colab API-URL"""
        return self.manager.set_api_url(url)
    
    def check_connection(self) -> Dict:
        """Prüft die Verbindung zum Colab-Backend"""
        return self.manager.check_connection()
    
    # === Generierungs-Funktionen ===
    
    def generate(self, params: Dict) -> Dict:
        """Generiert ein Bild über das Colab-Backend"""
        result = self.manager.generate(params)
        if result.get('success') and result.get('image'):
            self.last_image_data = base64.b64decode(result['image'])
        return result
    
    # === KI-Funktionen (OpenAI) ===
    
    def improve_prompt(self, prompt: str) -> Dict:
        """Verbessert einen Prompt mit KI"""
        if not self.ai.is_available():
            return {
                'success': False,
                'message': 'KI nicht verfügbar. Bitte OpenAI API-Key konfigurieren.'
            }
        
        try:
            model_type = self.analysis.model_type if self.analysis else 'stable_diffusion'
            improved = self.ai.improve_prompt(prompt, model_type)
            return {
                'success': True,
                'improved_prompt': improved,
                'message': 'Prompt erfolgreich verbessert'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def generate_negative_prompt(self, prompt: str) -> Dict:
        """Generiert einen Negative Prompt mit KI"""
        if not self.ai.is_available():
            return {
                'success': True,
                'negative_prompt': 'ugly, blurry, low quality, distorted, deformed',
                'message': 'Standard Negative Prompt (KI nicht verfügbar)'
            }
        
        try:
            model_type = self.analysis.model_type if self.analysis else 'stable_diffusion'
            negative = self.ai.generate_negative_prompt(prompt, model_type)
            return {
                'success': True,
                'negative_prompt': negative,
                'message': 'Negative Prompt generiert'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def suggest_settings(self, prompt: str) -> Dict:
        """Schlägt optimale Einstellungen vor"""
        if not self.ai.is_available():
            return {
                'success': True,
                'settings': {
                    'width': 512,
                    'height': 512,
                    'steps': 50,
                    'cfg_scale': 7.5
                },
                'message': 'Standard-Einstellungen (KI nicht verfügbar)'
            }
        
        try:
            model_type = self.analysis.model_type if self.analysis else 'stable_diffusion'
            settings = self.ai.suggest_settings(prompt, model_type)
            return {
                'success': True,
                'settings': settings,
                'message': 'Einstellungen vorgeschlagen'
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # === Theme-Funktionen ===
    
    def get_theme(self) -> str:
        """Gibt das aktuelle Theme zurück"""
        return self.theme.get_current_theme().value
    
    def set_theme(self, theme: str) -> Dict:
        """Setzt das Theme"""
        try:
            if theme == 'dark':
                self.theme.set_mode(ThemeMode.DARK)
            elif theme == 'light':
                self.theme.set_mode(ThemeMode.LIGHT)
            else:
                self.theme.set_mode(ThemeMode.AUTO)
            return {'success': True, 'theme': theme}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def toggle_theme(self) -> Dict:
        """Wechselt das Theme"""
        self.theme.toggle()
        return {'success': True, 'theme': self.theme.get_current_theme().value}
    
    # === Datei-Funktionen ===
    
    def load_image(self) -> Dict:
        """Lädt ein Bild von der Festplatte"""
        try:
            file_types = ('Bilder (*.png;*.jpg;*.jpeg;*.webp)', 'Alle Dateien (*.*)')
            
            if self._window:
                file_path = self._window.create_file_dialog(
                    webview.OPEN_DIALOG,
                    file_types=file_types
                )
            else:
                file_path = webview.windows[0].create_file_dialog(
                    webview.OPEN_DIALOG,
                    file_types=file_types
                )
            
            if file_path and len(file_path) > 0:
                with open(file_path[0], 'rb') as f:
                    self.last_image_data = f.read()
                image_base64 = base64.b64encode(self.last_image_data).decode('utf-8')
                return {
                    'success': True,
                    'image': image_base64,
                    'filename': os.path.basename(file_path[0])
                }
            else:
                return {'success': False, 'message': 'Keine Datei ausgewählt'}
                
        except Exception as e:
            return {'success': False, 'message': f'Fehler beim Laden: {str(e)}'}
    
    def save_image(self, filename: str = 'generated_image.png') -> Dict:
        """Speichert das letzte Bild"""
        if not self.last_image_data:
            return {'success': False, 'message': 'Kein Bild zum Speichern vorhanden'}
        
        try:
            file_types = ('PNG Bilder (*.png)', 'JPEG Bilder (*.jpg)', 'Alle Dateien (*.*)')
            
            if self._window:
                save_path = self._window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=filename,
                    file_types=file_types
                )
            else:
                save_path = webview.windows[0].create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=filename,
                    file_types=file_types
                )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(self.last_image_data)
                return {'success': True, 'message': f'Bild gespeichert: {os.path.basename(save_path)}'}
            else:
                return {'success': False, 'message': 'Speichern abgebrochen'}
                
        except Exception as e:
            return {'success': False, 'message': f'Fehler beim Speichern: {str(e)}'}
    
    # === Account-Funktionen ===
    
    def get_accounts(self) -> List[Dict]:
        """Gibt alle gespeicherten Accounts zurück"""
        return [
            {
                'email': acc.email,
                'name': acc.name,
                'is_default': acc.is_default
            }
            for acc in self.manager.get_accounts()
        ]
    
    def add_account(self, email: str, name: str = "") -> Dict:
        """Fügt einen Account hinzu"""
        self.manager.add_account(email, name)
        return {'success': True, 'message': f'Account {email} hinzugefügt'}
    
    def set_default_account(self, email: str) -> Dict:
        """Setzt den Standard-Account"""
        self.manager.set_default_account(email)
        return {'success': True, 'message': f'{email} als Standard gesetzt'}
    
    def open_colab(self, url: str, account_email: str = None) -> Dict:
        """Öffnet Colab im Browser"""
        try:
            self.manager.open_colab_in_browser(url, account_email)
            return {'success': True, 'message': 'Colab im Browser geöffnet'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


class ColabGUIApp:
    """Hauptanwendungsklasse"""
    
    APP_NAME = "Colab GUI Generator"
    APP_VERSION = "2.0.0"
    
    def __init__(self):
        self.parser = NotebookParser()
        self.colab_manager = ColabManager()
        self.theme_manager = get_theme_manager()
        self.ai_assistant = get_ai_assistant()
        self.current_analysis: Optional[NotebookAnalysis] = None
        self.window = None
        self.api = None
    
    def start(self, notebook_source: Optional[str] = None):
        """
        Startet die Anwendung.
        
        Args:
            notebook_source: Optional - Pfad oder URL zu einem Notebook
        """
        if notebook_source:
            self._start_with_notebook(notebook_source)
        else:
            self._start_launcher()
    
    def _start_launcher(self):
        """Startet das Launcher-Fenster"""
        html = self._generate_launcher_html()
        api = LauncherAPI(self)
        
        self.window = webview.create_window(
            title=f'{self.APP_NAME} v{self.APP_VERSION}',
            html=html,
            width=900,
            height=750,
            js_api=api,
            resizable=True,
            min_size=(700, 600)
        )
        
        api.set_window(self.window)
        webview.start()
    
    def _start_with_notebook(self, source: str):
        """Startet direkt mit einem Notebook"""
        try:
            if source.startswith('http'):
                self.current_analysis = self.parser.parse_url(source)
            else:
                self.current_analysis = self.parser.parse_file(source)
            
            self._start_generated_gui()
            
        except Exception as e:
            print(f"Fehler beim Laden des Notebooks: {e}")
            self._start_launcher()
    
    def _start_generated_gui(self):
        """Startet die generierte GUI"""
        if not self.current_analysis:
            return
        
        generator = GUIGenerator(self.current_analysis)
        html = generator.generate_html()
        
        self.api = EnhancedColabAPI(self.colab_manager, self.current_analysis)
        
        self.window = webview.create_window(
            title=f'{self.current_analysis.title} - {self.APP_NAME}',
            html=html,
            width=1100,
            height=850,
            js_api=self.api,
            resizable=True,
            min_size=(900, 700)
        )
        
        self.api.set_window(self.window)
        webview.start()
    
    def load_notebook(self, source: str) -> Dict[str, Any]:
        """Lädt und analysiert ein Notebook"""
        try:
            if source.startswith('http'):
                self.current_analysis = self.parser.parse_url(source)
            else:
                self.current_analysis = self.parser.parse_file(source)
            
            # KI-gestützte Analyse wenn verfügbar
            if self.ai_assistant.is_available() and self.current_analysis:
                # Hole den Code für KI-Analyse
                all_code = '\n'.join([
                    ''.join(c.get('source', [])) if isinstance(c.get('source'), list) 
                    else c.get('source', '')
                    for c in self.current_analysis.raw_cells 
                    if c.get('cell_type') == 'code'
                ])
                
                ai_result = self.ai_assistant.analyze_notebook_code(
                    all_code,
                    {
                        'title': self.current_analysis.title,
                        'description': self.current_analysis.description,
                        'model_type': self.current_analysis.model_type,
                        'parameters': [
                            {'name': p.name, 'type': p.param_type.value}
                            for p in self.current_analysis.parameters
                        ]
                    }
                )
                
                # Aktualisiere Analyse mit KI-Ergebnissen
                if ai_result.title:
                    self.current_analysis.title = ai_result.title
                if ai_result.description:
                    self.current_analysis.description = ai_result.description
            
            return {
                'success': True,
                'title': self.current_analysis.title,
                'description': self.current_analysis.description,
                'model_type': self.current_analysis.model_type,
                'parameters': len(self.current_analysis.parameters),
                'has_gradio': self.current_analysis.has_gradio,
                'packages': self.current_analysis.required_packages[:10],
                'ai_available': self.ai_assistant.is_available()
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _generate_launcher_html(self) -> str:
        """Generiert das HTML für das Launcher-Fenster"""
        theme_css = self.theme_manager.generate_base_css()
        is_dark = self.theme_manager.get_current_theme() == ThemeMode.DARK
        theme_icon = "☀️" if is_dark else "🌙"
        accounts_html = self._generate_accounts_html()
        ai_status = "🟢 Aktiv" if self.ai_assistant.is_available() else "🔴 Nicht verfügbar"
        
        return f'''<!DOCTYPE html>
<html lang="de" data-theme="{'dark' if is_dark else 'light'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.APP_NAME}</title>
    <style>
        {theme_css}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
        }}
        
        .header h1 {{
            font-size: 2.2em;
            color: var(--accent-primary);
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1em;
        }}
        
        .version-badge {{
            display: inline-block;
            background: var(--accent-primary);
            color: #000;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.75em;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .ai-status {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 10px;
            background: var(--bg-tertiary);
        }}
        
        .file-upload {{
            border: 2px dashed var(--border-color);
            border-radius: var(--radius-lg);
            padding: 40px 30px;
            text-align: center;
            cursor: pointer;
            transition: all var(--transition-fast);
            background: var(--bg-tertiary);
        }}
        
        .file-upload:hover {{
            border-color: var(--accent-primary);
            background: var(--input-bg);
        }}
        
        .file-upload input {{
            display: none;
        }}
        
        .file-upload .icon {{
            font-size: 3em;
            margin-bottom: 15px;
        }}
        
        .or-divider {{
            text-align: center;
            margin: 25px 0;
            position: relative;
        }}
        
        .or-divider::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 100%;
            height: 1px;
            background: var(--border-color);
        }}
        
        .or-divider span {{
            background: var(--bg-secondary);
            padding: 0 20px;
            position: relative;
            color: var(--text-muted);
        }}
        
        .account-list {{
            margin-top: 15px;
        }}
        
        .account-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            background: var(--bg-tertiary);
            border-radius: var(--radius-md);
            margin-bottom: 10px;
            cursor: pointer;
            transition: all var(--transition-fast);
            border: 1px solid transparent;
        }}
        
        .account-item:hover {{
            background: var(--input-bg);
            border-color: var(--border-color);
        }}
        
        .account-item.selected {{
            background: var(--input-bg);
            border-color: var(--accent-primary);
        }}
        
        .account-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
        }}
        
        .account-info {{
            flex: 1;
        }}
        
        .account-name {{
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .account-email {{
            font-size: 0.85em;
            color: var(--text-muted);
        }}
        
        .add-account {{
            border: 1px dashed var(--border-color);
            justify-content: center;
            background: transparent;
        }}
        
        .add-account:hover {{
            border-color: var(--accent-primary);
        }}
        
        .notebook-info {{
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: var(--radius-md);
            padding: 20px;
            margin-top: 20px;
        }}
        
        .notebook-info h3 {{
            color: var(--accent-primary);
            margin-bottom: 15px;
        }}
        
        .notebook-info .detail {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }}
        
        .notebook-info .detail span:first-child {{
            color: var(--text-muted);
        }}
        
        .hidden {{
            display: none !important;
        }}
        
        .btn-full {{
            width: 100%;
        }}
        
        .start-section {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <!-- Theme Toggle -->
    <button class="theme-toggle" onclick="toggleTheme()" title="Theme wechseln">
        <span id="theme-icon">{theme_icon}</span>
    </button>

    <div class="container">
        <header class="header">
            <h1>🚀 {self.APP_NAME} <span class="version-badge">v{self.APP_VERSION}</span></h1>
            <p class="subtitle">Erstellen Sie automatisch Desktop-GUIs für Ihre Colab-Notebooks</p>
            <div class="ai-status">OpenAI: {ai_status}</div>
        </header>
        
        <!-- Notebook Auswahl -->
        <section class="section">
            <h2>📓 Notebook auswählen</h2>
            
            <div class="file-upload" onclick="document.getElementById('file-input').click()">
                <div class="icon">📁</div>
                <p><strong>Klicken</strong> oder <strong>.ipynb Datei hierher ziehen</strong></p>
                <p style="color: var(--text-muted); font-size: 0.9em; margin-top: 10px;">
                    Unterstützt: Jupyter Notebooks (.ipynb)
                </p>
                <input type="file" id="file-input" accept=".ipynb" onchange="handleFileSelect(this)">
            </div>
            
            <div class="or-divider"><span>oder URL eingeben</span></div>
            
            <div style="display: flex; gap: 10px;">
                <input type="text" id="notebook-url" class="input-field" 
                    placeholder="https://github.com/user/repo/blob/main/notebook.ipynb"
                    style="flex: 1;">
                <button class="btn btn-secondary" onclick="loadNotebook()">
                    📥 Laden
                </button>
            </div>
            
            <div id="notebook-status"></div>
            
            <div id="notebook-info" class="notebook-info hidden">
                <h3 id="notebook-title">Notebook Titel</h3>
                <div class="detail">
                    <span>Modell-Typ:</span>
                    <span id="notebook-model">-</span>
                </div>
                <div class="detail">
                    <span>Parameter:</span>
                    <span id="notebook-params">-</span>
                </div>
                <div class="detail">
                    <span>Gradio UI:</span>
                    <span id="notebook-gradio">-</span>
                </div>
                <div class="detail">
                    <span>KI-Analyse:</span>
                    <span id="notebook-ai">-</span>
                </div>
            </div>
        </section>
        
        <!-- Google Account -->
        <section class="section">
            <h2>👤 Google Account</h2>
            <p style="margin-bottom: 15px; color: var(--text-muted); font-size: 0.9em;">
                Wählen Sie den Account für Google Colab
            </p>
            
            <div class="account-list" id="account-list">
                {accounts_html}
                
                <div class="account-item add-account" onclick="addAccount()">
                    <span>➕ Account hinzufügen</span>
                </div>
            </div>
        </section>
        
        <!-- Start Button -->
        <section class="section start-section">
            <button class="btn btn-primary btn-full btn-lg" onclick="startGUI()" id="start-btn" disabled>
                🎨 GUI generieren und starten
            </button>
            <p style="margin-top: 12px; text-align: center; color: var(--text-muted); font-size: 0.85em;">
                Das Notebook wird analysiert und eine passende GUI wird automatisch erstellt
            </p>
        </section>
    </div>
    
    <script>
        let selectedAccount = null;
        let notebookLoaded = false;
        let notebookSource = null;
        
        // Theme Toggle
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            document.getElementById('theme-icon').textContent = newTheme === 'dark' ? '☀️' : '🌙';
            
            updateThemeColors(newTheme);
            
            if (window.pywebview) {{
                pywebview.api.set_theme(newTheme);
            }}
        }}
        
        function updateThemeColors(theme) {{
            const root = document.documentElement;
            if (theme === 'dark') {{
                root.style.setProperty('--bg-primary', '#1a1a2e');
                root.style.setProperty('--bg-secondary', '#16213e');
                root.style.setProperty('--bg-tertiary', '#0f0f1a');
                root.style.setProperty('--text-primary', '#ffffff');
                root.style.setProperty('--text-secondary', '#e0e0e0');
                root.style.setProperty('--text-muted', '#888888');
                root.style.setProperty('--border-color', '#444444');
                root.style.setProperty('--input-bg', 'rgba(0, 0, 0, 0.3)');
            }} else {{
                root.style.setProperty('--bg-primary', '#f5f5f7');
                root.style.setProperty('--bg-secondary', '#ffffff');
                root.style.setProperty('--bg-tertiary', '#e8e8ed');
                root.style.setProperty('--text-primary', '#1d1d1f');
                root.style.setProperty('--text-secondary', '#424245');
                root.style.setProperty('--text-muted', '#86868b');
                root.style.setProperty('--border-color', '#d2d2d7');
                root.style.setProperty('--input-bg', '#ffffff');
            }}
        }}
        
        // Datei auswählen
        async function handleFileSelect(input) {{
            if (input.files && input.files[0]) {{
                const file = input.files[0];
                notebookSource = file.name;
                
                showStatus('notebook-status', '⏳ Analysiere Notebook...', 'loading');
                
                const reader = new FileReader();
                reader.onload = async function(e) {{
                    try {{
                        const content = e.target.result;
                        const result = await pywebview.api.load_notebook_content(content, file.name);
                        handleNotebookResult(result);
                    }} catch (error) {{
                        showStatus('notebook-status', '✗ Fehler: ' + error, 'error');
                    }}
                }};
                reader.readAsText(file);
            }}
        }}
        
        // Notebook von URL laden
        async function loadNotebook() {{
            const url = document.getElementById('notebook-url').value.trim();
            if (!url) {{
                showStatus('notebook-status', '⚠️ Bitte URL eingeben', 'error');
                return;
            }}
            
            notebookSource = url;
            showStatus('notebook-status', '⏳ Lade und analysiere Notebook...', 'loading');
            
            try {{
                const result = await pywebview.api.load_notebook_url(url);
                handleNotebookResult(result);
            }} catch (error) {{
                showStatus('notebook-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        function handleNotebookResult(result) {{
            if (result.success) {{
                notebookLoaded = true;
                showStatus('notebook-status', '✓ Notebook erfolgreich analysiert!', 'success');
                
                document.getElementById('notebook-info').classList.remove('hidden');
                document.getElementById('notebook-title').textContent = result.title;
                document.getElementById('notebook-model').textContent = result.model_type;
                document.getElementById('notebook-params').textContent = result.parameters + ' erkannt';
                document.getElementById('notebook-gradio').textContent = result.has_gradio ? 'Ja' : 'Nein';
                document.getElementById('notebook-ai').textContent = result.ai_available ? 'Aktiv' : 'Nicht verfügbar';
                
                updateStartButton();
            }} else {{
                showStatus('notebook-status', '✗ ' + result.message, 'error');
            }}
        }}
        
        // Account auswählen
        function selectAccount(email) {{
            selectedAccount = email;
            
            document.querySelectorAll('.account-item:not(.add-account)').forEach(item => {{
                item.classList.remove('selected');
            }});
            event.currentTarget.classList.add('selected');
            
            updateStartButton();
        }}
        
        // Account hinzufügen
        async function addAccount() {{
            const email = prompt('Google E-Mail-Adresse eingeben:');
            if (email && email.includes('@')) {{
                const name = email.split('@')[0];
                await pywebview.api.add_account(email, name);
                location.reload();
            }}
        }}
        
        // Start-Button aktualisieren
        function updateStartButton() {{
            const btn = document.getElementById('start-btn');
            btn.disabled = !notebookLoaded;
        }}
        
        // GUI starten
        async function startGUI() {{
            if (!notebookLoaded) {{
                showStatus('notebook-status', '⚠️ Bitte zuerst ein Notebook laden', 'error');
                return;
            }}
            
            showStatus('notebook-status', '🎨 Generiere GUI...', 'loading');
            
            try {{
                await pywebview.api.start_gui(selectedAccount);
            }} catch (error) {{
                showStatus('notebook-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        function showStatus(elementId, message, type) {{
            const el = document.getElementById(elementId);
            el.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
        }}
        
        // Drag & Drop
        const fileUpload = document.querySelector('.file-upload');
        
        fileUpload.addEventListener('dragover', (e) => {{
            e.preventDefault();
            fileUpload.style.borderColor = 'var(--accent-primary)';
            fileUpload.style.background = 'var(--input-bg)';
        }});
        
        fileUpload.addEventListener('dragleave', () => {{
            fileUpload.style.borderColor = '';
            fileUpload.style.background = '';
        }});
        
        fileUpload.addEventListener('drop', (e) => {{
            e.preventDefault();
            fileUpload.style.borderColor = '';
            fileUpload.style.background = '';
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].name.endsWith('.ipynb')) {{
                document.getElementById('file-input').files = files;
                handleFileSelect(document.getElementById('file-input'));
            }}
        }});
    </script>
</body>
</html>'''
    
    def _generate_accounts_html(self) -> str:
        """Generiert HTML für die Account-Liste"""
        accounts = self.colab_manager.get_accounts()
        
        if not accounts:
            return '''
            <div class="account-item" onclick="selectAccount('default')" style="opacity: 0.7;">
                <div class="account-avatar">👤</div>
                <div class="account-info">
                    <div class="account-name">Standard-Account</div>
                    <div class="account-email">Im Browser anmelden</div>
                </div>
            </div>'''
        
        html = ''
        for acc in accounts:
            selected = 'selected' if acc.is_default else ''
            html += f'''
            <div class="account-item {selected}" onclick="selectAccount('{acc.email}')">
                <div class="account-avatar">👤</div>
                <div class="account-info">
                    <div class="account-name">{acc.name}</div>
                    <div class="account-email">{acc.email}</div>
                </div>
            </div>'''
        
        return html


class LauncherAPI:
    """API für das Launcher-Fenster"""
    
    def __init__(self, app: ColabGUIApp):
        self.app = app
        self.notebook_content = None
        self._window = None
    
    def set_window(self, window):
        """Setzt das Fenster-Objekt"""
        self._window = window
    
    def load_notebook_url(self, url: str) -> Dict:
        """Lädt ein Notebook von einer URL"""
        return self.app.load_notebook(url)
    
    def load_notebook_content(self, content: str, filename: str) -> Dict:
        """Lädt ein Notebook aus dem Inhalt"""
        try:
            notebook_json = json.loads(content)
            self.notebook_content = notebook_json
            
            analysis = self.app.parser.parse_json(notebook_json, filename)
            self.app.current_analysis = analysis
            
            # KI-Analyse wenn verfügbar
            ai_available = self.app.ai_assistant.is_available()
            
            return {
                'success': True,
                'title': analysis.title,
                'description': analysis.description,
                'model_type': analysis.model_type,
                'parameters': len(analysis.parameters),
                'has_gradio': analysis.has_gradio,
                'packages': analysis.required_packages[:10],
                'ai_available': ai_available
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_account(self, email: str, name: str = "") -> Dict:
        """Fügt einen Account hinzu"""
        self.app.colab_manager.add_account(email, name)
        return {'success': True}
    
    def get_accounts(self) -> list:
        """Gibt alle Accounts zurück"""
        return [
            {'email': acc.email, 'name': acc.name, 'is_default': acc.is_default}
            for acc in self.app.colab_manager.get_accounts()
        ]
    
    def set_theme(self, theme: str) -> Dict:
        """Setzt das Theme"""
        try:
            if theme == 'dark':
                self.app.theme_manager.set_mode(ThemeMode.DARK)
            elif theme == 'light':
                self.app.theme_manager.set_mode(ThemeMode.LIGHT)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def start_gui(self, account_email: str = None) -> Dict:
        """Startet die generierte GUI"""
        if not self.app.current_analysis:
            return {'success': False, 'message': 'Kein Notebook geladen'}
        
        try:
            # Aktuelles Fenster schließen
            if self._window:
                self._window.destroy()
            
            # GUI generieren
            generator = GUIGenerator(self.app.current_analysis)
            html = generator.generate_html()
            
            # API erstellen
            self.app.api = EnhancedColabAPI(self.app.colab_manager, self.app.current_analysis)
            
            # Neues Fenster erstellen
            self.app.window = webview.create_window(
                title=f'{self.app.current_analysis.title} - {self.app.APP_NAME}',
                html=html,
                width=1100,
                height=850,
                js_api=self.app.api,
                resizable=True,
                min_size=(900, 700)
            )
            
            self.app.api.set_window(self.app.window)
            
            # Colab im Browser öffnen (optional)
            if self.app.current_analysis.api_code:
                colab_url = self.app.colab_manager.generate_colab_url()
                self.app.colab_manager.open_colab_in_browser(colab_url, account_email)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Colab GUI Generator - Erstellt automatisch GUIs für Colab-Notebooks'
    )
    parser.add_argument(
        'notebook',
        nargs='?',
        help='Pfad oder URL zu einem Notebook (.ipynb)'
    )
    parser.add_argument(
        '--theme',
        choices=['light', 'dark', 'auto'],
        default='auto',
        help='Theme-Modus (Standard: auto)'
    )
    
    args = parser.parse_args()
    
    # Theme setzen
    theme_manager = get_theme_manager()
    if args.theme == 'light':
        theme_manager.set_mode(ThemeMode.LIGHT)
    elif args.theme == 'dark':
        theme_manager.set_mode(ThemeMode.DARK)
    else:
        theme_manager.set_mode(ThemeMode.AUTO)
    
    # App starten
    app = ColabGUIApp()
    app.start(args.notebook)


if __name__ == '__main__':
    main()
