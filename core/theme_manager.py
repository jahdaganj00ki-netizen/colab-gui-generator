"""
=============================================================================
THEME MANAGER - Automatischer Hell-/Dunkel-Modus
=============================================================================
Erkennt den Windows-Systemtheme und passt die GUI automatisch an.
Unterstützt:
- Automatische Windows-Theme-Erkennung
- Manuelles Umschalten
- CSS-Variablen für konsistentes Styling
=============================================================================
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Callable, List
from enum import Enum
from dataclasses import dataclass


class ThemeMode(Enum):
    """Verfügbare Theme-Modi"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Folgt dem System


@dataclass
class ThemeColors:
    """Farbschema für ein Theme"""
    # Hintergrund
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    
    # Text
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # Akzent
    accent_primary: str
    accent_secondary: str
    accent_hover: str
    
    # Status
    success: str
    error: str
    warning: str
    info: str
    
    # Borders
    border_color: str
    border_light: str
    
    # Shadows
    shadow_color: str
    
    # Inputs
    input_bg: str
    input_border: str
    input_focus: str


# Vordefinierte Themes
DARK_THEME = ThemeColors(
    bg_primary="#1a1a2e",
    bg_secondary="#16213e",
    bg_tertiary="#0f0f1a",
    text_primary="#ffffff",
    text_secondary="#e0e0e0",
    text_muted="#888888",
    accent_primary="#00d4ff",
    accent_secondary="#0099cc",
    accent_hover="#00a8cc",
    success="#00ff88",
    error="#ff4444",
    warning="#ffaa00",
    info="#00d4ff",
    border_color="#444444",
    border_light="#333333",
    shadow_color="rgba(0, 0, 0, 0.3)",
    input_bg="rgba(0, 0, 0, 0.3)",
    input_border="#444444",
    input_focus="#00d4ff"
)

LIGHT_THEME = ThemeColors(
    bg_primary="#f5f5f7",
    bg_secondary="#ffffff",
    bg_tertiary="#e8e8ed",
    text_primary="#1d1d1f",
    text_secondary="#424245",
    text_muted="#86868b",
    accent_primary="#0071e3",
    accent_secondary="#0077ed",
    accent_hover="#0068d0",
    success="#34c759",
    error="#ff3b30",
    warning="#ff9500",
    info="#007aff",
    border_color="#d2d2d7",
    border_light="#e5e5ea",
    shadow_color="rgba(0, 0, 0, 0.1)",
    input_bg="#ffffff",
    input_border="#d2d2d7",
    input_focus="#0071e3"
)


class ThemeManager:
    """Verwaltet das Anwendungs-Theme"""
    
    def __init__(self):
        self.current_mode = ThemeMode.AUTO
        self._listeners: List[Callable] = []
        self._cached_system_theme: Optional[ThemeMode] = None
        self._load_preferences()
    
    def _load_preferences(self):
        """Lädt gespeicherte Theme-Einstellungen"""
        config_path = Path.home() / '.colab_gui_generator' / 'theme.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    mode = data.get('mode', 'auto')
                    self.current_mode = ThemeMode(mode)
            except Exception:
                pass
    
    def _save_preferences(self):
        """Speichert Theme-Einstellungen"""
        config_dir = Path.home() / '.colab_gui_generator'
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / 'theme.json'
        
        try:
            with open(config_path, 'w') as f:
                json.dump({'mode': self.current_mode.value}, f)
        except Exception:
            pass
    
    def detect_system_theme(self) -> ThemeMode:
        """
        Erkennt das aktuelle Windows-System-Theme.
        
        Returns:
            ThemeMode.DARK oder ThemeMode.LIGHT
        """
        if sys.platform != 'win32':
            return ThemeMode.DARK  # Standard für Nicht-Windows
        
        try:
            import winreg
            
            # Windows Registry auslesen
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            
            # AppsUseLightTheme: 0 = Dark, 1 = Light
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            
            self._cached_system_theme = ThemeMode.LIGHT if value == 1 else ThemeMode.DARK
            return self._cached_system_theme
            
        except Exception as e:
            print(f"Konnte Windows-Theme nicht erkennen: {e}")
            return ThemeMode.DARK  # Fallback
    
    def get_current_theme(self) -> ThemeMode:
        """
        Gibt das aktuelle effektive Theme zurück.
        
        Returns:
            ThemeMode.DARK oder ThemeMode.LIGHT (nie AUTO)
        """
        if self.current_mode == ThemeMode.AUTO:
            return self.detect_system_theme()
        return self.current_mode
    
    def get_colors(self) -> ThemeColors:
        """
        Gibt die Farben für das aktuelle Theme zurück.
        
        Returns:
            ThemeColors Objekt
        """
        theme = self.get_current_theme()
        return DARK_THEME if theme == ThemeMode.DARK else LIGHT_THEME
    
    def set_mode(self, mode: ThemeMode):
        """
        Setzt den Theme-Modus.
        
        Args:
            mode: ThemeMode (LIGHT, DARK, AUTO)
        """
        self.current_mode = mode
        self._save_preferences()
        self._notify_listeners()
    
    def toggle(self):
        """Wechselt zwischen Hell und Dunkel"""
        current = self.get_current_theme()
        if current == ThemeMode.DARK:
            self.set_mode(ThemeMode.LIGHT)
        else:
            self.set_mode(ThemeMode.DARK)
    
    def add_listener(self, callback: Callable):
        """Fügt einen Listener für Theme-Änderungen hinzu"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Entfernt einen Listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self):
        """Benachrichtigt alle Listener über Theme-Änderung"""
        for listener in self._listeners:
            try:
                listener(self.get_current_theme())
            except Exception as e:
                print(f"Listener-Fehler: {e}")
    
    def generate_css_variables(self) -> str:
        """
        Generiert CSS-Variablen für das aktuelle Theme.
        
        Returns:
            CSS-String mit :root Variablen
        """
        colors = self.get_colors()
        
        return f"""
        :root {{
            /* Hintergrund */
            --bg-primary: {colors.bg_primary};
            --bg-secondary: {colors.bg_secondary};
            --bg-tertiary: {colors.bg_tertiary};
            
            /* Text */
            --text-primary: {colors.text_primary};
            --text-secondary: {colors.text_secondary};
            --text-muted: {colors.text_muted};
            
            /* Akzent */
            --accent-primary: {colors.accent_primary};
            --accent-secondary: {colors.accent_secondary};
            --accent-hover: {colors.accent_hover};
            
            /* Status */
            --success: {colors.success};
            --error: {colors.error};
            --warning: {colors.warning};
            --info: {colors.info};
            
            /* Borders */
            --border-color: {colors.border_color};
            --border-light: {colors.border_light};
            
            /* Shadows */
            --shadow-color: {colors.shadow_color};
            
            /* Inputs */
            --input-bg: {colors.input_bg};
            --input-border: {colors.input_border};
            --input-focus: {colors.input_focus};
            
            /* Transitions */
            --transition-fast: 0.15s ease;
            --transition-normal: 0.3s ease;
            
            /* Border Radius */
            --radius-sm: 4px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
        }}
        """
    
    def generate_base_css(self) -> str:
        """
        Generiert das komplette Basis-CSS mit Theme-Unterstützung.
        
        Returns:
            Vollständiges CSS für die Anwendung
        """
        css_vars = self.generate_css_variables()
        
        return f"""
        {css_vars}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color var(--transition-normal),
                        color var(--transition-normal),
                        border-color var(--transition-normal);
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 950px;
            margin: 0 auto;
        }}
        
        /* Karten/Sektionen */
        .section, .card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-lg);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px var(--shadow-color);
        }}
        
        .section h2, .card h2 {{
            color: var(--accent-primary);
            font-size: 1.1em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        /* Eingabefelder */
        .input-field, textarea, select {{
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--input-border);
            border-radius: var(--radius-md);
            background: var(--input-bg);
            color: var(--text-primary);
            font-size: 14px;
            transition: all var(--transition-fast);
        }}
        
        .input-field:focus, textarea:focus, select:focus {{
            outline: none;
            border-color: var(--input-focus);
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15);
        }}
        
        .input-field::placeholder, textarea::placeholder {{
            color: var(--text-muted);
        }}
        
        textarea {{
            min-height: 80px;
            resize: vertical;
            font-family: inherit;
        }}
        
        /* Buttons */
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: var(--radius-md);
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all var(--transition-fast);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            color: #000000;
        }}
        
        .btn-primary:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
        }}
        
        .btn-secondary {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }}
        
        .btn-secondary:hover:not(:disabled) {{
            background: var(--border-color);
        }}
        
        .btn-success {{
            background: linear-gradient(135deg, var(--success) 0%, #00cc6a 100%);
            color: #000000;
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, var(--error) 0%, #cc0000 100%);
            color: #ffffff;
        }}
        
        /* Slider */
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .slider-container input[type="range"] {{
            flex: 1;
            height: 6px;
            -webkit-appearance: none;
            background: var(--border-color);
            border-radius: 3px;
            outline: none;
        }}
        
        .slider-container input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            background: var(--accent-primary);
            border-radius: 50%;
            cursor: pointer;
            transition: transform var(--transition-fast);
        }}
        
        .slider-container input[type="range"]::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
        }}
        
        .slider-value {{
            min-width: 50px;
            text-align: center;
            background: var(--bg-tertiary);
            padding: 5px 10px;
            border-radius: var(--radius-sm);
            font-family: 'Consolas', monospace;
            font-size: 13px;
        }}
        
        /* Status-Meldungen */
        .status {{
            padding: 12px 16px;
            border-radius: var(--radius-md);
            margin-top: 10px;
            text-align: center;
            font-weight: 500;
        }}
        
        .status.success {{
            background: rgba(0, 255, 136, 0.15);
            color: var(--success);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }}
        
        .status.error {{
            background: rgba(255, 68, 68, 0.15);
            color: var(--error);
            border: 1px solid rgba(255, 68, 68, 0.3);
        }}
        
        .status.loading, .status.info {{
            background: rgba(0, 212, 255, 0.15);
            color: var(--info);
            border: 1px solid rgba(0, 212, 255, 0.3);
        }}
        
        /* Bild-Container */
        .result-container, .image-container {{
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-tertiary);
            border-radius: var(--radius-lg);
            border: 2px dashed var(--border-color);
            overflow: hidden;
        }}
        
        .result-container img, .image-container img {{
            max-width: 100%;
            max-height: 500px;
            border-radius: var(--radius-md);
        }}
        
        .placeholder {{
            color: var(--text-muted);
            font-size: 1.1em;
        }}
        
        /* Loading Spinner */
        .loading {{
            text-align: center;
            padding: 20px;
        }}
        
        .loading.hidden {{
            display: none;
        }}
        
        .spinner {{
            border: 4px solid var(--border-color);
            border-left-color: var(--accent-primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Grid Layouts */
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        
        /* Theme Toggle Button */
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: all var(--transition-fast);
            z-index: 1000;
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 15px var(--shadow-color);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .grid-2, .grid-3 {{
                grid-template-columns: 1fr;
            }}
            
            body {{
                padding: 15px;
            }}
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-tertiary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}
        """


# Globale Instanz
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Gibt die globale Theme-Manager-Instanz zurück"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


# Test
if __name__ == '__main__':
    manager = get_theme_manager()
    print(f"System-Theme: {manager.detect_system_theme().value}")
    print(f"Aktuelles Theme: {manager.get_current_theme().value}")
    print(f"Modus: {manager.current_mode.value}")
