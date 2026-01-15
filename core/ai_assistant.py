"""
=============================================================================
AI ASSISTANT - OpenAI Integration
=============================================================================
Nutzt die OpenAI API für intelligente Funktionen:
- Verbesserte Notebook-Analyse
- Automatische Prompt-Optimierung
- Intelligente Parameter-Erkennung
- Benutzerfreundliche Beschreibungen
=============================================================================
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AIAnalysisResult:
    """Ergebnis der KI-gestützten Analyse"""
    title: str
    description: str
    suggested_parameters: List[Dict]
    model_type: str
    usage_instructions: str
    prompt_suggestions: List[str]


class AIAssistant:
    """
    KI-Assistent für intelligente Funktionen.
    Nutzt die OpenAI API (gpt-4.1-mini oder gpt-4.1-nano).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den AI-Assistenten.
        
        Args:
            api_key: OpenAI API Key. Falls nicht angegeben, wird aus
                     Umgebungsvariable OPENAI_API_KEY gelesen.
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', '')
        self.client = None
        self.model = "gpt-4.1-nano"  # Schnell und kosteneffizient
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI()  # API key und base_url sind vorkonfiguriert
            except ImportError:
                print("OpenAI-Paket nicht installiert. KI-Funktionen deaktiviert.")
            except Exception as e:
                print(f"OpenAI-Initialisierung fehlgeschlagen: {e}")
    
    def is_available(self) -> bool:
        """Prüft ob die KI verfügbar ist"""
        return self.client is not None and bool(self.api_key)
    
    def analyze_notebook_code(self, code: str, existing_analysis: Dict) -> AIAnalysisResult:
        """
        Analysiert Notebook-Code mit KI für bessere Ergebnisse.
        
        Args:
            code: Der gesamte Code aus dem Notebook
            existing_analysis: Bereits durch Regex erkannte Parameter
        
        Returns:
            AIAnalysisResult mit verbesserten Informationen
        """
        if not self.is_available():
            return self._fallback_analysis(existing_analysis)
        
        try:
            prompt = f"""Analysiere diesen Google Colab Notebook-Code und extrahiere Informationen für eine GUI.

CODE:
```python
{code[:8000]}  # Limitiert auf 8000 Zeichen
```

BEREITS ERKANNTE PARAMETER:
{json.dumps(existing_analysis.get('parameters', []), indent=2)}

Antworte im JSON-Format:
{{
    "title": "Benutzerfreundlicher Titel für die GUI",
    "description": "Kurze Beschreibung was das Notebook macht (max 100 Wörter)",
    "model_type": "stable_diffusion|controlnet|sdxl|flux|llm|audio|video|other",
    "suggested_parameters": [
        {{
            "name": "parameter_name",
            "type": "text|textarea|slider|number|checkbox|dropdown|image|file",
            "label": "Benutzerfreundliches Label",
            "description": "Kurze Beschreibung",
            "default": "Standardwert",
            "min": 0,
            "max": 100,
            "step": 1,
            "options": ["option1", "option2"]
        }}
    ],
    "usage_instructions": "Kurze Anleitung zur Nutzung",
    "prompt_suggestions": ["Beispiel-Prompt 1", "Beispiel-Prompt 2", "Beispiel-Prompt 3"]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für KI-Modelle und Jupyter Notebooks. Analysiere Code präzise und gib strukturierte JSON-Antworten."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # JSON aus der Antwort extrahieren
            json_match = result_text
            if "```json" in result_text:
                json_match = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                json_match = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(json_match.strip())
            
            return AIAnalysisResult(
                title=result.get('title', existing_analysis.get('title', 'Notebook')),
                description=result.get('description', ''),
                suggested_parameters=result.get('suggested_parameters', []),
                model_type=result.get('model_type', 'unknown'),
                usage_instructions=result.get('usage_instructions', ''),
                prompt_suggestions=result.get('prompt_suggestions', [])
            )
            
        except Exception as e:
            print(f"KI-Analyse fehlgeschlagen: {e}")
            return self._fallback_analysis(existing_analysis)
    
    def improve_prompt(self, prompt: str, model_type: str = "stable_diffusion") -> str:
        """
        Verbessert einen Benutzer-Prompt für bessere Ergebnisse.
        
        Args:
            prompt: Der ursprüngliche Prompt
            model_type: Der Typ des KI-Modells
        
        Returns:
            Verbesserter Prompt
        """
        if not self.is_available() or not prompt.strip():
            return prompt
        
        try:
            system_prompts = {
                "stable_diffusion": "Du bist ein Experte für Stable Diffusion Prompts. Verbessere den Prompt für fotorealistische, detaillierte Bilder.",
                "sdxl": "Du bist ein Experte für SDXL Prompts. Verbessere den Prompt für hochauflösende, künstlerische Bilder.",
                "flux": "Du bist ein Experte für FLUX Prompts. Verbessere den Prompt für moderne, kreative Bildgenerierung.",
                "controlnet": "Du bist ein Experte für ControlNet. Verbessere den Prompt für präzise, kontrollierte Bildgenerierung.",
            }
            
            system_prompt = system_prompts.get(model_type, system_prompts["stable_diffusion"])
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Verbessere diesen Prompt für bessere Bildgenerierung. Antworte NUR mit dem verbesserten Prompt, ohne Erklärungen:\n\n{prompt}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            improved = response.choices[0].message.content.strip()
            # Entferne eventuelle Anführungszeichen
            improved = improved.strip('"\'')
            return improved
            
        except Exception as e:
            print(f"Prompt-Verbesserung fehlgeschlagen: {e}")
            return prompt
    
    def generate_negative_prompt(self, prompt: str, model_type: str = "stable_diffusion") -> str:
        """
        Generiert einen passenden Negative Prompt.
        
        Args:
            prompt: Der Haupt-Prompt
            model_type: Der Typ des KI-Modells
        
        Returns:
            Generierter Negative Prompt
        """
        if not self.is_available():
            return "ugly, blurry, low quality, distorted, deformed"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für Bildgenerierung. Erstelle passende Negative Prompts."
                    },
                    {
                        "role": "user",
                        "content": f"Erstelle einen Negative Prompt für diesen Prompt. Antworte NUR mit dem Negative Prompt:\n\n{prompt}"
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip().strip('"\'')
            
        except Exception as e:
            print(f"Negative Prompt Generierung fehlgeschlagen: {e}")
            return "ugly, blurry, low quality, distorted, deformed"
    
    def suggest_settings(self, prompt: str, model_type: str = "stable_diffusion") -> Dict[str, Any]:
        """
        Schlägt optimale Einstellungen basierend auf dem Prompt vor.
        
        Args:
            prompt: Der Benutzer-Prompt
            model_type: Der Typ des KI-Modells
        
        Returns:
            Dictionary mit empfohlenen Einstellungen
        """
        if not self.is_available():
            return {
                "width": 512,
                "height": 512,
                "steps": 50,
                "cfg_scale": 7.5
            }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für Bildgenerierung. Empfehle optimale Einstellungen."
                    },
                    {
                        "role": "user",
                        "content": f"""Empfehle optimale Einstellungen für diesen Prompt und Modelltyp.
Prompt: {prompt}
Modell: {model_type}

Antworte im JSON-Format:
{{"width": 512, "height": 512, "steps": 50, "cfg_scale": 7.5, "reason": "Kurze Begründung"}}"""
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content
            if "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            return json.loads(result_text.strip())
            
        except Exception as e:
            print(f"Einstellungsvorschläge fehlgeschlagen: {e}")
            return {
                "width": 512,
                "height": 512,
                "steps": 50,
                "cfg_scale": 7.5
            }
    
    def _fallback_analysis(self, existing_analysis: Dict) -> AIAnalysisResult:
        """Fallback wenn KI nicht verfügbar"""
        return AIAnalysisResult(
            title=existing_analysis.get('title', 'Notebook'),
            description=existing_analysis.get('description', ''),
            suggested_parameters=[],
            model_type=existing_analysis.get('model_type', 'unknown'),
            usage_instructions='',
            prompt_suggestions=[]
        )


# Globale Instanz
_ai_assistant: Optional[AIAssistant] = None


def get_ai_assistant() -> AIAssistant:
    """Gibt die globale AI-Assistenten-Instanz zurück"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = AIAssistant()
    return _ai_assistant


# Test
if __name__ == '__main__':
    assistant = get_ai_assistant()
    print(f"KI verfügbar: {assistant.is_available()}")
    
    if assistant.is_available():
        # Test Prompt-Verbesserung
        original = "ein Hund"
        improved = assistant.improve_prompt(original)
        print(f"Original: {original}")
        print(f"Verbessert: {improved}")
