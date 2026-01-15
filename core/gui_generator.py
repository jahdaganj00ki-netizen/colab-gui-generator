"""
=============================================================================
GUI GENERATOR - Verbesserte Version mit Theme-Unterstützung
=============================================================================
Generiert automatisch eine grafische Benutzeroberfläche basierend auf
der Notebook-Analyse. Unterstützt automatischen Hell-/Dunkel-Modus.
=============================================================================
"""

from typing import List, Optional
from .notebook_parser import NotebookAnalysis, Parameter, Output, ParameterType, OutputType
from .theme_manager import get_theme_manager, ThemeMode


class GUIGenerator:
    """Generiert HTML/CSS/JS für die Desktop-GUI mit Theme-Unterstützung"""
    
    def __init__(self, analysis: NotebookAnalysis):
        self.analysis = analysis
        self.theme_manager = get_theme_manager()
    
    def generate_html(self) -> str:
        """Generiert das komplette HTML für die GUI"""
        theme_css = self.theme_manager.generate_base_css()
        is_dark = self.theme_manager.get_current_theme() == ThemeMode.DARK
        theme_icon = "☀️" if is_dark else "🌙"
        
        return f'''<!DOCTYPE html>
<html lang="de" data-theme="{'dark' if is_dark else 'light'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.analysis.title}</title>
    <style>
        {theme_css}
        {self._generate_custom_css()}
    </style>
</head>
<body>
    <!-- Theme Toggle -->
    <button class="theme-toggle" onclick="toggleTheme()" title="Theme wechseln">
        <span id="theme-icon">{theme_icon}</span>
    </button>

    <div class="container">
        <header class="header">
            <h1>🎨 {self.analysis.title}</h1>
            {f'<p class="description">{self.analysis.description}</p>' if self.analysis.description else ''}
            <div class="model-badge">{self._get_model_badge()}</div>
        </header>
        
        <!-- Verbindungsbereich -->
        <section class="section">
            <h2>🔗 Colab Verbindung</h2>
            <div class="connection-row">
                <input type="text" id="colab-url" class="input-field" 
                    placeholder="https://xxxx.ngrok-free.app">
                <button onclick="testConnection()" class="btn btn-secondary">Verbinden</button>
            </div>
            <div id="connection-status"></div>
        </section>
        
        <!-- Eingabeparameter -->
        <section class="section">
            <h2>⚙️ Einstellungen</h2>
            <form id="params-form">
                {self._generate_parameter_fields()}
            </form>
            
            <!-- KI-Funktionen -->
            <div class="ai-tools">
                <button type="button" onclick="improvePrompt()" class="btn btn-secondary btn-sm">
                    ✨ Prompt verbessern
                </button>
                <button type="button" onclick="generateNegativePrompt()" class="btn btn-secondary btn-sm">
                    🚫 Negative Prompt generieren
                </button>
                <button type="button" onclick="suggestSettings()" class="btn btn-secondary btn-sm">
                    💡 Einstellungen vorschlagen
                </button>
            </div>
        </section>
        
        <!-- Aktions-Buttons -->
        <section class="section button-section">
            <button onclick="generate()" class="btn btn-primary btn-lg" id="generate-btn">
                🎨 Generieren
            </button>
            <button onclick="loadImage()" class="btn btn-secondary">
                📁 Bild laden
            </button>
            <button onclick="saveImage()" class="btn btn-success">
                💾 Speichern
            </button>
        </section>
        
        <!-- Ladeindikator -->
        <div id="loading" class="loading hidden">
            <div class="spinner"></div>
            <p id="loading-text">Generiere...</p>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>
        
        <!-- Ergebnis -->
        <section class="section">
            <h2>🖼️ Ergebnis</h2>
            <div id="result-container" class="result-container">
                <p class="placeholder">Hier erscheint das generierte Bild</p>
            </div>
            <div id="result-status"></div>
        </section>
        
        <!-- Footer -->
        <footer class="footer">
            <p>Colab GUI Generator • Powered by OpenAI</p>
        </footer>
    </div>
    
    {self._generate_javascript()}
</body>
</html>'''
    
    def _generate_custom_css(self) -> str:
        """Generiert zusätzliches CSS"""
        return '''
        .header {
            text-align: center;
            margin-bottom: 25px;
        }
        
        .header h1 {
            color: var(--accent-primary);
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .description {
            color: var(--text-secondary);
            font-size: 1em;
            max-width: 600px;
            margin: 0 auto 15px;
        }
        
        .model-badge {
            display: inline-block;
            background: var(--accent-primary);
            color: #000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .connection-row {
            display: flex;
            gap: 10px;
        }
        
        .connection-row .input-field {
            flex: 1;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .form-group .hint {
            font-size: 0.8em;
            color: var(--text-muted);
            margin-top: 5px;
        }
        
        .form-group .required {
            color: var(--error);
        }
        
        .ai-tools {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid var(--border-light);
            flex-wrap: wrap;
        }
        
        .btn-sm {
            padding: 8px 16px;
            font-size: 13px;
        }
        
        .btn-lg {
            padding: 16px 32px;
            font-size: 16px;
            flex: 1;
        }
        
        .button-section {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .progress-bar {
            width: 200px;
            height: 4px;
            background: var(--border-color);
            border-radius: 2px;
            margin: 15px auto 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--accent-primary);
            width: 0%;
            transition: width 0.3s ease;
            animation: progress-pulse 2s ease-in-out infinite;
        }
        
        @keyframes progress-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .image-upload-container {
            border: 2px dashed var(--border-color);
            border-radius: var(--radius-lg);
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: all var(--transition-fast);
            background: var(--bg-tertiary);
        }
        
        .image-upload-container:hover {
            border-color: var(--accent-primary);
            background: var(--input-bg);
        }
        
        .image-upload-container .icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .image-upload-container img {
            max-width: 100%;
            max-height: 150px;
            margin-top: 15px;
            border-radius: var(--radius-md);
        }
        
        .image-upload-container input[type="file"] {
            display: none;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 0.85em;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            cursor: help;
        }
        
        .tooltip::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all var(--transition-fast);
            z-index: 100;
            box-shadow: 0 4px 15px var(--shadow-color);
        }
        
        .tooltip:hover::after {
            opacity: 1;
            visibility: visible;
        }
        '''
    
    def _get_model_badge(self) -> str:
        """Gibt ein Badge für den Modell-Typ zurück"""
        badges = {
            'stable_diffusion': 'Stable Diffusion',
            'sdxl': 'SDXL',
            'flux': 'FLUX',
            'controlnet': 'ControlNet',
            'diffusers': 'Diffusers',
            'transformers': 'Transformers',
        }
        return badges.get(self.analysis.model_type, 'KI-Modell')
    
    def _generate_parameter_fields(self) -> str:
        """Generiert die Eingabefelder für alle Parameter"""
        fields = []
        
        # Gruppiere Parameter nach Typ
        text_params = [p for p in self.analysis.parameters if p.param_type in [ParameterType.TEXT, ParameterType.TEXTAREA]]
        slider_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.SLIDER]
        number_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.NUMBER]
        checkbox_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.CHECKBOX]
        dropdown_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.DROPDOWN]
        image_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.IMAGE]
        file_params = [p for p in self.analysis.parameters if p.param_type == ParameterType.FILE]
        
        # Text-Eingaben (volle Breite)
        for param in text_params:
            fields.append(self._generate_text_field(param))
        
        # Bild-Upload
        for param in image_params:
            fields.append(self._generate_image_field(param))
        
        # Datei-Upload
        for param in file_params:
            fields.append(self._generate_file_field(param))
        
        # Slider in 2er-Grid
        if slider_params:
            slider_html = '<div class="grid-2">'
            for param in slider_params:
                slider_html += self._generate_slider_field(param)
            slider_html += '</div>'
            fields.append(slider_html)
        
        # Zahlen in 3er-Grid
        if number_params:
            number_html = '<div class="grid-3">'
            for param in number_params:
                number_html += self._generate_number_field(param)
            number_html += '</div>'
            fields.append(number_html)
        
        # Dropdowns
        for param in dropdown_params:
            fields.append(self._generate_dropdown_field(param))
        
        # Checkboxen
        for param in checkbox_params:
            fields.append(self._generate_checkbox_field(param))
        
        return '\n'.join(fields)
    
    def _generate_text_field(self, param: Parameter) -> str:
        """Generiert ein Textfeld"""
        required_mark = '<span class="required">*</span>' if param.required else ''
        
        if param.param_type == ParameterType.TEXTAREA:
            return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label} {required_mark}</label>
                <textarea id="{param.name}" name="{param.name}" 
                    placeholder="{param.description or f'{param.label} eingeben...'}"
                    {'required' if param.required else ''}>{param.default_value or ''}</textarea>
                {f'<p class="hint">{param.description}</p>' if param.description else ''}
            </div>'''
        else:
            return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label} {required_mark}</label>
                <input type="text" id="{param.name}" name="{param.name}" 
                    class="input-field"
                    value="{param.default_value or ''}"
                    placeholder="{param.description or f'{param.label} eingeben...'}"
                    {'required' if param.required else ''}>
            </div>'''
    
    def _generate_slider_field(self, param: Parameter) -> str:
        """Generiert einen Slider"""
        min_val = param.min_value if param.min_value is not None else 0
        max_val = param.max_value if param.max_value is not None else 100
        step = param.step if param.step is not None else 1
        default = param.default_value if param.default_value is not None else min_val
        
        return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label}</label>
                <div class="slider-container">
                    <input type="range" id="{param.name}" name="{param.name}"
                        min="{min_val}" max="{max_val}" step="{step}" value="{default}"
                        oninput="document.getElementById('{param.name}_value').textContent = this.value">
                    <span id="{param.name}_value" class="slider-value">{default}</span>
                </div>
            </div>'''
    
    def _generate_number_field(self, param: Parameter) -> str:
        """Generiert ein Zahlenfeld"""
        return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label}</label>
                <input type="number" id="{param.name}" name="{param.name}"
                    class="input-field"
                    value="{param.default_value if param.default_value is not None else 0}"
                    {f'min="{param.min_value}"' if param.min_value is not None else ''}
                    {f'max="{param.max_value}"' if param.max_value is not None else ''}
                    {f'step="{param.step}"' if param.step else ''}>
            </div>'''
    
    def _generate_checkbox_field(self, param: Parameter) -> str:
        """Generiert eine Checkbox"""
        checked = 'checked' if param.default_value else ''
        return f'''
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="{param.name}" name="{param.name}" {checked}>
                    <span>{param.label}</span>
                </label>
            </div>'''
    
    def _generate_dropdown_field(self, param: Parameter) -> str:
        """Generiert ein Dropdown"""
        options = ''.join([
            f'<option value="{opt}" {"selected" if opt == param.default_value else ""}>{opt}</option>'
            for opt in param.options
        ])
        return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label}</label>
                <select id="{param.name}" name="{param.name}" class="input-field">
                    {options}
                </select>
            </div>'''
    
    def _generate_image_field(self, param: Parameter) -> str:
        """Generiert ein Bild-Upload-Feld"""
        return f'''
            <div class="form-group">
                <label>{param.label}</label>
                <div class="image-upload-container" onclick="document.getElementById('{param.name}_input').click()">
                    <div class="icon">📷</div>
                    <p>Klicken zum Hochladen oder Bild hierher ziehen</p>
                    <input type="file" id="{param.name}_input" accept="image/*" 
                        onchange="previewImage(this, '{param.name}_preview')">
                    <img id="{param.name}_preview" style="display:none;">
                </div>
            </div>'''
    
    def _generate_file_field(self, param: Parameter) -> str:
        """Generiert ein Datei-Upload-Feld"""
        return f'''
            <div class="form-group">
                <label for="{param.name}">{param.label}</label>
                <input type="file" id="{param.name}" name="{param.name}" class="input-field">
            </div>'''
    
    def _generate_javascript(self) -> str:
        """Generiert das JavaScript"""
        return f'''<script>
        let colabUrl = '';
        let lastImageData = null;
        let isGenerating = false;
        
        // Theme-Funktionen
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            document.getElementById('theme-icon').textContent = newTheme === 'dark' ? '☀️' : '🌙';
            
            // An Python senden
            if (window.pywebview) {{
                pywebview.api.set_theme(newTheme);
            }}
            
            // CSS-Variablen aktualisieren
            updateThemeColors(newTheme);
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
        
        // Verbindung testen
        async function testConnection() {{
            const url = document.getElementById('colab-url').value.trim().replace(/\\/$/, '');
            
            if (!url) {{
                showStatus('connection-status', 'Bitte URL eingeben', 'error');
                return;
            }}
            
            showStatus('connection-status', '⏳ Verbinde...', 'loading');
            
            try {{
                const result = await pywebview.api.set_colab_url(url);
                const check = await pywebview.api.check_connection();
                
                if (check.success) {{
                    colabUrl = url;
                    showStatus('connection-status', '✓ ' + check.message, 'success');
                }} else {{
                    showStatus('connection-status', '✗ ' + check.message, 'error');
                }}
            }} catch (error) {{
                showStatus('connection-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        // Bild generieren
        async function generate() {{
            if (isGenerating) return;
            
            if (!colabUrl) {{
                showStatus('result-status', 'Bitte zuerst mit Colab verbinden!', 'error');
                return;
            }}
            
            // Parameter sammeln
            const params = {{}};
            {self._generate_param_collection_js()}
            
            // UI aktualisieren
            isGenerating = true;
            document.getElementById('generate-btn').disabled = true;
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('result-container').innerHTML = '';
            showStatus('result-status', '', '');
            
            // Progress-Animation
            let progress = 0;
            const progressInterval = setInterval(() => {{
                progress = Math.min(progress + Math.random() * 10, 90);
                document.getElementById('progress-fill').style.width = progress + '%';
            }}, 500);
            
            try {{
                const result = await pywebview.api.generate(params);
                
                clearInterval(progressInterval);
                document.getElementById('progress-fill').style.width = '100%';
                
                setTimeout(() => {{
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('generate-btn').disabled = false;
                    isGenerating = false;
                    
                    if (result.success) {{
                        lastImageData = result.image;
                        document.getElementById('result-container').innerHTML = 
                            '<img src="data:image/png;base64,' + result.image + '" alt="Generiertes Bild">';
                        showStatus('result-status', '✓ ' + (result.message || 'Erfolgreich generiert!'), 'success');
                    }} else {{
                        document.getElementById('result-container').innerHTML = 
                            '<p class="placeholder">Fehler bei der Generierung</p>';
                        showStatus('result-status', '✗ ' + result.message, 'error');
                    }}
                }}, 300);
                
            }} catch (error) {{
                clearInterval(progressInterval);
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('generate-btn').disabled = false;
                isGenerating = false;
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        // KI-Funktionen
        async function improvePrompt() {{
            const promptEl = document.getElementById('prompt');
            if (!promptEl || !promptEl.value.trim()) {{
                showStatus('result-status', 'Bitte zuerst einen Prompt eingeben', 'error');
                return;
            }}
            
            showStatus('result-status', '✨ Verbessere Prompt...', 'loading');
            
            try {{
                const result = await pywebview.api.improve_prompt(promptEl.value);
                if (result.success) {{
                    promptEl.value = result.improved_prompt;
                    showStatus('result-status', '✓ Prompt verbessert!', 'success');
                }} else {{
                    showStatus('result-status', '✗ ' + result.message, 'error');
                }}
            }} catch (error) {{
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        async function generateNegativePrompt() {{
            const promptEl = document.getElementById('prompt');
            const negPromptEl = document.getElementById('negative_prompt');
            
            if (!promptEl || !promptEl.value.trim()) {{
                showStatus('result-status', 'Bitte zuerst einen Prompt eingeben', 'error');
                return;
            }}
            
            if (!negPromptEl) {{
                showStatus('result-status', 'Kein Negative Prompt Feld gefunden', 'error');
                return;
            }}
            
            showStatus('result-status', '🚫 Generiere Negative Prompt...', 'loading');
            
            try {{
                const result = await pywebview.api.generate_negative_prompt(promptEl.value);
                if (result.success) {{
                    negPromptEl.value = result.negative_prompt;
                    showStatus('result-status', '✓ Negative Prompt generiert!', 'success');
                }} else {{
                    showStatus('result-status', '✗ ' + result.message, 'error');
                }}
            }} catch (error) {{
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        async function suggestSettings() {{
            const promptEl = document.getElementById('prompt');
            if (!promptEl || !promptEl.value.trim()) {{
                showStatus('result-status', 'Bitte zuerst einen Prompt eingeben', 'error');
                return;
            }}
            
            showStatus('result-status', '💡 Analysiere Prompt...', 'loading');
            
            try {{
                const result = await pywebview.api.suggest_settings(promptEl.value);
                if (result.success) {{
                    // Einstellungen anwenden
                    const settings = result.settings;
                    for (const [key, value] of Object.entries(settings)) {{
                        const el = document.getElementById(key);
                        if (el) {{
                            el.value = value;
                            // Slider-Wert aktualisieren
                            const valueEl = document.getElementById(key + '_value');
                            if (valueEl) valueEl.textContent = value;
                        }}
                    }}
                    showStatus('result-status', '✓ Einstellungen angewendet!' + 
                        (settings.reason ? ' (' + settings.reason + ')' : ''), 'success');
                }} else {{
                    showStatus('result-status', '✗ ' + result.message, 'error');
                }}
            }} catch (error) {{
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        // Bild laden
        async function loadImage() {{
            try {{
                const result = await pywebview.api.load_image();
                if (result.success) {{
                    lastImageData = result.image;
                    document.getElementById('result-container').innerHTML = 
                        '<img src="data:image/png;base64,' + result.image + '" alt="Geladenes Bild">';
                    showStatus('result-status', '✓ Bild geladen: ' + result.filename, 'success');
                }}
            }} catch (error) {{
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        // Bild speichern
        async function saveImage() {{
            if (!lastImageData) {{
                showStatus('result-status', 'Kein Bild zum Speichern vorhanden', 'error');
                return;
            }}
            
            try {{
                const result = await pywebview.api.save_image();
                showStatus('result-status', result.success ? '✓ ' + result.message : '✗ ' + result.message, 
                    result.success ? 'success' : 'error');
            }} catch (error) {{
                showStatus('result-status', '✗ Fehler: ' + error, 'error');
            }}
        }}
        
        // Bild-Vorschau
        function previewImage(input, previewId) {{
            const preview = document.getElementById(previewId);
            if (input.files && input.files[0]) {{
                const reader = new FileReader();
                reader.onload = function(e) {{
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }};
                reader.readAsDataURL(input.files[0]);
            }}
        }}
        
        // Status anzeigen
        function showStatus(elementId, message, type) {{
            const el = document.getElementById(elementId);
            if (!message) {{
                el.innerHTML = '';
                return;
            }}
            el.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
        }}
        
        // Bild zu Base64 konvertieren
        async function getImageBase64(inputId) {{
            const input = document.getElementById(inputId);
            if (!input || !input.files || !input.files[0]) return null;
            
            return new Promise((resolve) => {{
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result.split(',')[1]);
                reader.readAsDataURL(input.files[0]);
            }});
        }}
        
        // Keyboard Shortcuts
        document.addEventListener('keydown', function(e) {{
            // Ctrl+Enter = Generieren
            if (e.ctrlKey && e.key === 'Enter') {{
                e.preventDefault();
                generate();
            }}
            // Ctrl+S = Speichern
            if (e.ctrlKey && e.key === 's') {{
                e.preventDefault();
                saveImage();
            }}
        }});
    </script>'''
    
    def _generate_param_collection_js(self) -> str:
        """Generiert JavaScript zum Sammeln der Parameter"""
        lines = []
        
        for param in self.analysis.parameters:
            if param.param_type == ParameterType.CHECKBOX:
                lines.append(f"params['{param.name}'] = document.getElementById('{param.name}')?.checked || false;")
            elif param.param_type == ParameterType.IMAGE:
                lines.append(f"params['{param.name}'] = await getImageBase64('{param.name}_input');")
            elif param.param_type in [ParameterType.SLIDER, ParameterType.NUMBER]:
                lines.append(f"params['{param.name}'] = parseFloat(document.getElementById('{param.name}')?.value || 0);")
            elif param.param_type == ParameterType.TEXTAREA:
                lines.append(f"params['{param.name}'] = document.getElementById('{param.name}')?.value || '';")
            else:
                lines.append(f"params['{param.name}'] = document.getElementById('{param.name}')?.value || '';")
        
        return '\n            '.join(lines)
