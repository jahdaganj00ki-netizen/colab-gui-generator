"""
=============================================================================
NOTEBOOK PARSER
=============================================================================
Analysiert Jupyter/Colab Notebooks (.ipynb) und extrahiert:
- Eingabeparameter (Prompts, Einstellungen, Datei-Uploads)
- Ausgabetypen (Bilder, Text, Dateien)
- Erforderliche Installationen
- API-Endpunkte (falls vorhanden)
=============================================================================
"""

import json
import re
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ParameterType(Enum):
    """Typen von erkannten Parametern"""
    TEXT = "text"           # Einfacher Text (Prompt)
    TEXTAREA = "textarea"   # Mehrzeiliger Text
    NUMBER = "number"       # Numerischer Wert
    SLIDER = "slider"       # Slider mit Min/Max
    CHECKBOX = "checkbox"   # Boolean
    DROPDOWN = "dropdown"   # Auswahl aus Optionen
    FILE = "file"           # Datei-Upload
    IMAGE = "image"         # Bild-Upload
    COLOR = "color"         # Farbauswahl


class OutputType(Enum):
    """Typen von erkannten Ausgaben"""
    IMAGE = "image"         # Generiertes Bild
    TEXT = "text"           # Textausgabe
    FILE = "file"           # Datei-Download
    AUDIO = "audio"         # Audio-Ausgabe
    VIDEO = "video"         # Video-Ausgabe


@dataclass
class Parameter:
    """Repräsentiert einen erkannten Eingabeparameter"""
    name: str
    param_type: ParameterType
    label: str
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: List[str] = field(default_factory=list)
    description: str = ""
    required: bool = True


@dataclass
class Output:
    """Repräsentiert eine erkannte Ausgabe"""
    name: str
    output_type: OutputType
    description: str = ""


@dataclass
class NotebookAnalysis:
    """Ergebnis der Notebook-Analyse"""
    title: str
    description: str
    parameters: List[Parameter]
    outputs: List[Output]
    required_packages: List[str]
    has_gradio: bool
    has_flask: bool
    has_fastapi: bool
    model_type: str  # z.B. "stable_diffusion", "controlnet", "unknown"
    raw_cells: List[Dict]
    api_code: str  # Generierter API-Code


class NotebookParser:
    """Hauptklasse für die Notebook-Analyse"""
    
    # Patterns für die Erkennung von Parametern
    PATTERNS = {
        # Gradio-Komponenten
        'gradio_textbox': r'gr\.Textbox\s*\([^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_slider': r'gr\.Slider\s*\([^)]*minimum\s*=\s*(\d+)[^)]*maximum\s*=\s*(\d+)[^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_number': r'gr\.Number\s*\([^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_checkbox': r'gr\.Checkbox\s*\([^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_dropdown': r'gr\.Dropdown\s*\([^)]*choices\s*=\s*\[([^\]]+)\][^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_image': r'gr\.Image\s*\([^)]*label\s*=\s*["\']([^"\']+)["\']',
        'gradio_file': r'gr\.File\s*\([^)]*label\s*=\s*["\']([^"\']+)["\']',
        
        # Einfache Variable-Zuweisungen
        'prompt_var': r'(?:prompt|text|input_text)\s*=\s*["\']([^"\']*)["\']',
        'negative_prompt': r'negative_prompt\s*=\s*["\']([^"\']*)["\']',
        'width_var': r'(?:width|w)\s*=\s*(\d+)',
        'height_var': r'(?:height|h)\s*=\s*(\d+)',
        'steps_var': r'(?:steps|num_inference_steps|inference_steps)\s*=\s*(\d+)',
        'cfg_var': r'(?:cfg_scale|guidance_scale|cfg)\s*=\s*([\d.]+)',
        'seed_var': r'seed\s*=\s*(-?\d+)',
        'strength_var': r'strength\s*=\s*([\d.]+)',
        
        # Input-Funktionen
        'input_func': r'input\s*\(\s*["\']([^"\']+)["\']\s*\)',
        
        # Widgets (ipywidgets)
        'widget_text': r'widgets\.Text\s*\([^)]*description\s*=\s*["\']([^"\']+)["\']',
        'widget_slider': r'widgets\.(?:Int|Float)Slider\s*\([^)]*min\s*=\s*(\d+)[^)]*max\s*=\s*(\d+)[^)]*description\s*=\s*["\']([^"\']+)["\']',
        'widget_dropdown': r'widgets\.Dropdown\s*\([^)]*options\s*=\s*\[([^\]]+)\][^)]*description\s*=\s*["\']([^"\']+)["\']',
        
        # Modell-Erkennung
        'stable_diffusion': r'(?:StableDiffusion|stable-diffusion|runwayml|CompVis)',
        'controlnet': r'(?:ControlNet|controlnet)',
        'sdxl': r'(?:SDXL|sdxl|stable-diffusion-xl)',
        'flux': r'(?:FLUX|flux)',
        
        # Package-Installation
        'pip_install': r'!pip\s+install\s+([^\n]+)',
        'pip3_install': r'!pip3\s+install\s+([^\n]+)',
    }
    
    def __init__(self):
        self.analysis = None
    
    def parse_file(self, file_path: str) -> NotebookAnalysis:
        """Parst eine .ipynb Datei"""
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        return self._analyze_notebook(notebook, os.path.basename(file_path))
    
    def parse_json(self, notebook_json: dict, filename: str = "notebook") -> NotebookAnalysis:
        """Parst ein Notebook aus einem JSON-Dictionary"""
        return self._analyze_notebook(notebook_json, filename)
    
    def parse_url(self, url: str) -> NotebookAnalysis:
        """Lädt und parst ein Notebook von einer URL (z.B. GitHub)"""
        import requests
        
        # GitHub Raw-URL konvertieren
        if 'github.com' in url and '/blob/' in url:
            url = url.replace('github.com', 'raw.githubusercontent.com')
            url = url.replace('/blob/', '/')
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        notebook = response.json()
        filename = url.split('/')[-1]
        return self._analyze_notebook(notebook, filename)
    
    def _analyze_notebook(self, notebook: dict, filename: str) -> NotebookAnalysis:
        """Hauptanalyse-Funktion"""
        cells = notebook.get('cells', [])
        
        # Alle Code-Zellen extrahieren
        code_cells = [c for c in cells if c.get('cell_type') == 'code']
        markdown_cells = [c for c in cells if c.get('cell_type') == 'markdown']
        
        # Gesamten Code zusammenfügen
        all_code = '\n'.join([
            ''.join(c.get('source', [])) if isinstance(c.get('source'), list) 
            else c.get('source', '')
            for c in code_cells
        ])
        
        # Titel und Beschreibung aus Markdown extrahieren
        title, description = self._extract_metadata(markdown_cells, filename)
        
        # Parameter erkennen
        parameters = self._detect_parameters(all_code)
        
        # Ausgaben erkennen
        outputs = self._detect_outputs(all_code)
        
        # Pakete erkennen
        packages = self._detect_packages(all_code)
        
        # Framework-Erkennung
        has_gradio = 'gradio' in all_code.lower() or 'import gr' in all_code
        has_flask = 'flask' in all_code.lower()
        has_fastapi = 'fastapi' in all_code.lower()
        
        # Modell-Typ erkennen
        model_type = self._detect_model_type(all_code)
        
        # API-Code generieren
        api_code = self._generate_api_code(parameters, outputs, model_type)
        
        self.analysis = NotebookAnalysis(
            title=title,
            description=description,
            parameters=parameters,
            outputs=outputs,
            required_packages=packages,
            has_gradio=has_gradio,
            has_flask=has_flask,
            has_fastapi=has_fastapi,
            model_type=model_type,
            raw_cells=cells,
            api_code=api_code
        )
        
        return self.analysis
    
    def _extract_metadata(self, markdown_cells: List[dict], filename: str) -> tuple:
        """Extrahiert Titel und Beschreibung aus Markdown-Zellen"""
        title = filename.replace('.ipynb', '').replace('_', ' ').replace('-', ' ').title()
        description = ""
        
        for cell in markdown_cells:
            source = ''.join(cell.get('source', [])) if isinstance(cell.get('source'), list) else cell.get('source', '')
            
            # Titel aus H1 extrahieren
            h1_match = re.search(r'^#\s+(.+)$', source, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            
            # Beschreibung aus erstem Absatz
            if not description:
                # Entferne Überschriften und nimm ersten Absatz
                text = re.sub(r'^#+.*$', '', source, flags=re.MULTILINE).strip()
                if text:
                    description = text[:500]  # Max 500 Zeichen
                    break
        
        return title, description
    
    def _detect_parameters(self, code: str) -> List[Parameter]:
        """Erkennt Eingabeparameter im Code"""
        parameters = []
        found_names = set()
        
        # Standard-Parameter für Bild-KI hinzufügen
        standard_params = self._detect_standard_image_params(code)
        for param in standard_params:
            if param.name not in found_names:
                parameters.append(param)
                found_names.add(param.name)
        
        # Gradio-Komponenten erkennen
        gradio_params = self._detect_gradio_params(code)
        for param in gradio_params:
            if param.name not in found_names:
                parameters.append(param)
                found_names.add(param.name)
        
        # Widget-Parameter erkennen
        widget_params = self._detect_widget_params(code)
        for param in widget_params:
            if param.name not in found_names:
                parameters.append(param)
                found_names.add(param.name)
        
        # Falls keine Parameter gefunden, Standard-Set für Bild-KI
        if not parameters:
            parameters = self._get_default_image_params()
        
        return parameters
    
    def _detect_standard_image_params(self, code: str) -> List[Parameter]:
        """Erkennt Standard-Parameter für Bildgenerierung"""
        params = []
        
        # Prompt
        if re.search(r'prompt', code, re.IGNORECASE):
            params.append(Parameter(
                name='prompt',
                param_type=ParameterType.TEXTAREA,
                label='Prompt',
                default_value='',
                description='Beschreibung des gewünschten Bildes'
            ))
        
        # Negative Prompt
        if re.search(r'negative_prompt', code, re.IGNORECASE):
            params.append(Parameter(
                name='negative_prompt',
                param_type=ParameterType.TEXTAREA,
                label='Negative Prompt',
                default_value='',
                description='Was NICHT im Bild erscheinen soll',
                required=False
            ))
        
        # Breite
        width_match = re.search(self.PATTERNS['width_var'], code)
        if width_match or re.search(r'width', code, re.IGNORECASE):
            default = int(width_match.group(1)) if width_match else 512
            params.append(Parameter(
                name='width',
                param_type=ParameterType.SLIDER,
                label='Breite',
                default_value=default,
                min_value=256,
                max_value=1024,
                step=64,
                description='Bildbreite in Pixeln'
            ))
        
        # Höhe
        height_match = re.search(self.PATTERNS['height_var'], code)
        if height_match or re.search(r'height', code, re.IGNORECASE):
            default = int(height_match.group(1)) if height_match else 512
            params.append(Parameter(
                name='height',
                param_type=ParameterType.SLIDER,
                label='Höhe',
                default_value=default,
                min_value=256,
                max_value=1024,
                step=64,
                description='Bildhöhe in Pixeln'
            ))
        
        # Steps
        steps_match = re.search(self.PATTERNS['steps_var'], code)
        if steps_match or re.search(r'steps|inference', code, re.IGNORECASE):
            default = int(steps_match.group(1)) if steps_match else 50
            params.append(Parameter(
                name='steps',
                param_type=ParameterType.SLIDER,
                label='Schritte',
                default_value=default,
                min_value=10,
                max_value=150,
                step=1,
                description='Anzahl der Inferenz-Schritte'
            ))
        
        # CFG Scale
        cfg_match = re.search(self.PATTERNS['cfg_var'], code)
        if cfg_match or re.search(r'cfg|guidance', code, re.IGNORECASE):
            default = float(cfg_match.group(1)) if cfg_match else 7.5
            params.append(Parameter(
                name='cfg_scale',
                param_type=ParameterType.SLIDER,
                label='CFG Scale',
                default_value=default,
                min_value=1.0,
                max_value=20.0,
                step=0.5,
                description='Wie stark der Prompt befolgt wird'
            ))
        
        # Seed
        if re.search(r'seed', code, re.IGNORECASE):
            params.append(Parameter(
                name='seed',
                param_type=ParameterType.NUMBER,
                label='Seed',
                default_value=-1,
                description='Zufallszahl für Reproduzierbarkeit (-1 = zufällig)'
            ))
        
        # Strength (für img2img)
        strength_match = re.search(self.PATTERNS['strength_var'], code)
        if strength_match or re.search(r'img2img|strength', code, re.IGNORECASE):
            default = float(strength_match.group(1)) if strength_match else 0.75
            params.append(Parameter(
                name='strength',
                param_type=ParameterType.SLIDER,
                label='Stärke',
                default_value=default,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                description='Stärke der Bildbearbeitung'
            ))
        
        # Input Image (für img2img)
        if re.search(r'img2img|init_image|input_image', code, re.IGNORECASE):
            params.append(Parameter(
                name='input_image',
                param_type=ParameterType.IMAGE,
                label='Eingabebild',
                description='Bild für img2img Bearbeitung',
                required=False
            ))
        
        return params
    
    def _detect_gradio_params(self, code: str) -> List[Parameter]:
        """Erkennt Gradio-Komponenten"""
        params = []
        
        # Textbox
        for match in re.finditer(self.PATTERNS['gradio_textbox'], code):
            params.append(Parameter(
                name=self._sanitize_name(match.group(1)),
                param_type=ParameterType.TEXT,
                label=match.group(1)
            ))
        
        # Slider
        for match in re.finditer(self.PATTERNS['gradio_slider'], code):
            params.append(Parameter(
                name=self._sanitize_name(match.group(3)),
                param_type=ParameterType.SLIDER,
                label=match.group(3),
                min_value=float(match.group(1)),
                max_value=float(match.group(2))
            ))
        
        # Image
        for match in re.finditer(self.PATTERNS['gradio_image'], code):
            params.append(Parameter(
                name=self._sanitize_name(match.group(1)),
                param_type=ParameterType.IMAGE,
                label=match.group(1)
            ))
        
        return params
    
    def _detect_widget_params(self, code: str) -> List[Parameter]:
        """Erkennt ipywidgets-Komponenten"""
        params = []
        
        # Text Widget
        for match in re.finditer(self.PATTERNS['widget_text'], code):
            params.append(Parameter(
                name=self._sanitize_name(match.group(1)),
                param_type=ParameterType.TEXT,
                label=match.group(1)
            ))
        
        # Slider Widget
        for match in re.finditer(self.PATTERNS['widget_slider'], code):
            params.append(Parameter(
                name=self._sanitize_name(match.group(3)),
                param_type=ParameterType.SLIDER,
                label=match.group(3),
                min_value=float(match.group(1)),
                max_value=float(match.group(2))
            ))
        
        return params
    
    def _get_default_image_params(self) -> List[Parameter]:
        """Standard-Parameter für Bild-KI"""
        return [
            Parameter(
                name='prompt',
                param_type=ParameterType.TEXTAREA,
                label='Prompt',
                default_value='',
                description='Beschreibung des gewünschten Bildes'
            ),
            Parameter(
                name='negative_prompt',
                param_type=ParameterType.TEXTAREA,
                label='Negative Prompt',
                default_value='',
                description='Was NICHT im Bild erscheinen soll',
                required=False
            ),
            Parameter(
                name='width',
                param_type=ParameterType.SLIDER,
                label='Breite',
                default_value=512,
                min_value=256,
                max_value=1024,
                step=64
            ),
            Parameter(
                name='height',
                param_type=ParameterType.SLIDER,
                label='Höhe',
                default_value=512,
                min_value=256,
                max_value=1024,
                step=64
            ),
            Parameter(
                name='steps',
                param_type=ParameterType.SLIDER,
                label='Schritte',
                default_value=50,
                min_value=10,
                max_value=150,
                step=1
            )
        ]
    
    def _detect_outputs(self, code: str) -> List[Output]:
        """Erkennt Ausgabetypen"""
        outputs = []
        
        # Bild-Ausgabe
        if re.search(r'\.save\(|Image\.|PIL|cv2|plt\.show|display\(', code, re.IGNORECASE):
            outputs.append(Output(
                name='generated_image',
                output_type=OutputType.IMAGE,
                description='Generiertes Bild'
            ))
        
        # Audio-Ausgabe
        if re.search(r'audio|wav|mp3|tts|speech', code, re.IGNORECASE):
            outputs.append(Output(
                name='generated_audio',
                output_type=OutputType.AUDIO,
                description='Generiertes Audio'
            ))
        
        # Video-Ausgabe
        if re.search(r'video|mp4|avi|animate', code, re.IGNORECASE):
            outputs.append(Output(
                name='generated_video',
                output_type=OutputType.VIDEO,
                description='Generiertes Video'
            ))
        
        # Standard: Bild-Ausgabe
        if not outputs:
            outputs.append(Output(
                name='generated_image',
                output_type=OutputType.IMAGE,
                description='Generiertes Bild'
            ))
        
        return outputs
    
    def _detect_packages(self, code: str) -> List[str]:
        """Erkennt erforderliche Pakete"""
        packages = set()
        
        # pip install Befehle
        for pattern in [self.PATTERNS['pip_install'], self.PATTERNS['pip3_install']]:
            for match in re.finditer(pattern, code):
                pkgs = match.group(1).split()
                for pkg in pkgs:
                    # Bereinigen
                    pkg = re.sub(r'[<>=!].*', '', pkg)
                    pkg = pkg.strip()
                    if pkg and not pkg.startswith('-'):
                        packages.add(pkg)
        
        # Import-Statements
        for match in re.finditer(r'^import\s+(\w+)|^from\s+(\w+)', code, re.MULTILINE):
            pkg = match.group(1) or match.group(2)
            if pkg:
                packages.add(pkg)
        
        return list(packages)
    
    def _detect_model_type(self, code: str) -> str:
        """Erkennt den Modell-Typ"""
        code_lower = code.lower()
        
        if re.search(self.PATTERNS['flux'], code, re.IGNORECASE):
            return 'flux'
        elif re.search(self.PATTERNS['sdxl'], code, re.IGNORECASE):
            return 'sdxl'
        elif re.search(self.PATTERNS['controlnet'], code, re.IGNORECASE):
            return 'controlnet'
        elif re.search(self.PATTERNS['stable_diffusion'], code, re.IGNORECASE):
            return 'stable_diffusion'
        elif 'diffusers' in code_lower:
            return 'diffusers'
        elif 'transformers' in code_lower:
            return 'transformers'
        else:
            return 'unknown'
    
    def _generate_api_code(self, parameters: List[Parameter], outputs: List[Output], model_type: str) -> str:
        """Generiert API-Code für das Backend"""
        param_names = [p.name for p in parameters]
        
        code = '''
# === AUTO-GENERIERTER API-CODE ===
# Fügen Sie diesen Code zu Ihrem Colab-Notebook hinzu

from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import base64
import io

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'online'})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        
        # Parameter extrahieren
'''
        
        for param in parameters:
            default = f"'{param.default_value}'" if isinstance(param.default_value, str) else param.default_value
            code += f"        {param.name} = data.get('{param.name}', {default})\n"
        
        code += '''
        
        # === HIER IHRE GENERIERUNGS-LOGIK EINFÜGEN ===
        # result_image = your_model.generate(...)
        
        # Bild zu Base64 konvertieren
        buffer = io.BytesIO()
        result_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': image_base64
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Server starten
public_url = ngrok.connect(5000)
print(f"\\n🌐 API URL: {public_url}\\n")
app.run(port=5000)
'''
        
        return code
    
    def _sanitize_name(self, name: str) -> str:
        """Bereinigt einen Namen für die Verwendung als Variable"""
        name = name.lower()
        name = re.sub(r'[^a-z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        return name.strip('_')


# Test
if __name__ == '__main__':
    parser = NotebookParser()
    
    # Test mit einem Beispiel-Notebook
    test_notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Stable Diffusion Image Generator\n", "Generate images using AI"]
            },
            {
                "cell_type": "code",
                "source": [
                    "!pip install diffusers transformers\n",
                    "prompt = 'a beautiful sunset'\n",
                    "negative_prompt = 'ugly, blurry'\n",
                    "width = 512\n",
                    "height = 512\n",
                    "steps = 50\n",
                    "cfg_scale = 7.5\n"
                ]
            }
        ]
    }
    
    analysis = parser.parse_json(test_notebook, "test.ipynb")
    
    print(f"Title: {analysis.title}")
    print(f"Model Type: {analysis.model_type}")
    print(f"Parameters: {len(analysis.parameters)}")
    for p in analysis.parameters:
        print(f"  - {p.name}: {p.param_type.value}")
