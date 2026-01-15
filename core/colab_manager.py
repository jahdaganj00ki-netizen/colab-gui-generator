"""
=============================================================================
COLAB MANAGER
=============================================================================
Verwaltet die Verbindung zu Google Colab:
- Google Account Auswahl
- Notebook-Upload und -Start
- API-Kommunikation
=============================================================================
"""

import os
import json
import base64
import requests
import webbrowser
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GoogleAccount:
    """Repräsentiert einen Google Account"""
    email: str
    name: str
    profile_picture: Optional[str] = None
    is_default: bool = False


@dataclass
class ColabSession:
    """Repräsentiert eine aktive Colab-Session"""
    notebook_id: str
    api_url: str
    status: str  # 'starting', 'running', 'stopped', 'error'
    runtime_type: str  # 'cpu', 'gpu', 'tpu'


class ColabManager:
    """
    Verwaltet die Interaktion mit Google Colab.
    
    Da Google Colab keine offizielle API für programmatischen Zugriff bietet,
    nutzen wir einen hybriden Ansatz:
    
    1. Der Benutzer öffnet Colab im Browser und wählt seinen Account
    2. Das Notebook wird mit API-Code modifiziert
    3. Die Desktop-App kommuniziert über die ngrok-URL
    """
    
    COLAB_BASE_URL = "https://colab.research.google.com"
    GITHUB_RAW_URL = "https://raw.githubusercontent.com"
    
    def __init__(self):
        self.current_session: Optional[ColabSession] = None
        self.api_url: str = ""
        self.accounts: List[GoogleAccount] = []
        self._load_saved_accounts()
    
    def _load_saved_accounts(self):
        """Lädt gespeicherte Account-Informationen"""
        config_path = Path.home() / '.colab_gui_generator' / 'accounts.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self.accounts = [GoogleAccount(**acc) for acc in data.get('accounts', [])]
            except Exception:
                pass
    
    def _save_accounts(self):
        """Speichert Account-Informationen"""
        config_dir = Path.home() / '.colab_gui_generator'
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / 'accounts.json'
        
        try:
            data = {
                'accounts': [
                    {
                        'email': acc.email,
                        'name': acc.name,
                        'profile_picture': acc.profile_picture,
                        'is_default': acc.is_default
                    }
                    for acc in self.accounts
                ]
            }
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def add_account(self, email: str, name: str = "", is_default: bool = False):
        """Fügt einen Account hinzu"""
        # Prüfen ob Account bereits existiert
        for acc in self.accounts:
            if acc.email == email:
                return
        
        if is_default:
            # Alle anderen als nicht-default markieren
            for acc in self.accounts:
                acc.is_default = False
        
        self.accounts.append(GoogleAccount(
            email=email,
            name=name or email.split('@')[0],
            is_default=is_default
        ))
        self._save_accounts()
    
    def get_accounts(self) -> List[GoogleAccount]:
        """Gibt alle gespeicherten Accounts zurück"""
        return self.accounts
    
    def get_default_account(self) -> Optional[GoogleAccount]:
        """Gibt den Standard-Account zurück"""
        for acc in self.accounts:
            if acc.is_default:
                return acc
        return self.accounts[0] if self.accounts else None
    
    def set_default_account(self, email: str):
        """Setzt einen Account als Standard"""
        for acc in self.accounts:
            acc.is_default = (acc.email == email)
        self._save_accounts()
    
    def generate_colab_url(self, notebook_path: Optional[str] = None, 
                           github_url: Optional[str] = None) -> str:
        """
        Generiert eine Colab-URL zum Öffnen eines Notebooks.
        
        Args:
            notebook_path: Lokaler Pfad zu einer .ipynb Datei
            github_url: GitHub-URL zu einem Notebook
        
        Returns:
            URL zum Öffnen in Colab
        """
        if github_url:
            # GitHub URL zu Colab URL konvertieren
            # Format: https://github.com/user/repo/blob/branch/path/to/notebook.ipynb
            # Wird zu: https://colab.research.google.com/github/user/repo/blob/branch/path/to/notebook.ipynb
            if 'github.com' in github_url:
                colab_url = github_url.replace(
                    'https://github.com',
                    f'{self.COLAB_BASE_URL}/github'
                )
                return colab_url
        
        # Für lokale Dateien: Colab mit Upload-Option öffnen
        return f"{self.COLAB_BASE_URL}/#create=true"
    
    def open_colab_in_browser(self, url: str, account_email: Optional[str] = None):
        """
        Öffnet Colab im Standard-Browser.
        
        Args:
            url: Die Colab-URL
            account_email: Optional - E-Mail des zu verwendenden Accounts
        """
        # Wenn ein Account angegeben ist, füge authuser Parameter hinzu
        if account_email:
            # Finde den Index des Accounts
            for i, acc in enumerate(self.accounts):
                if acc.email == account_email:
                    separator = '&' if '?' in url else '?'
                    url = f"{url}{separator}authuser={i}"
                    break
        
        webbrowser.open(url)
    
    def set_api_url(self, url: str) -> Dict[str, Any]:
        """Setzt die API-URL (ngrok-URL vom Colab)"""
        self.api_url = url.rstrip('/')
        return {'success': True, 'message': f'API-URL gesetzt: {self.api_url}'}
    
    def check_connection(self) -> Dict[str, Any]:
        """Prüft die Verbindung zum Colab-Backend"""
        if not self.api_url:
            return {'success': False, 'message': 'Keine API-URL konfiguriert'}
        
        try:
            response = requests.get(f'{self.api_url}/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', 'Verbindung erfolgreich!'),
                    'status': data.get('status', 'online')
                }
            else:
                return {
                    'success': False,
                    'message': f'Server-Fehler: Status {response.status_code}'
                }
        except requests.exceptions.Timeout:
            return {'success': False, 'message': 'Zeitüberschreitung - Server antwortet nicht'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'message': 'Verbindungsfehler - URL prüfen'}
        except Exception as e:
            return {'success': False, 'message': f'Fehler: {str(e)}'}
    
    def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sendet eine Generierungsanfrage an das Colab-Backend.
        
        Args:
            params: Dictionary mit allen Parametern
        
        Returns:
            Dictionary mit 'success', 'image' (base64), 'message'
        """
        if not self.api_url:
            return {'success': False, 'message': 'Keine API-URL konfiguriert'}
        
        try:
            response = requests.post(
                f'{self.api_url}/generate',
                json=params,
                timeout=300  # 5 Minuten Timeout für Bildgenerierung
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'message': f'Server-Fehler: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'message': 'Zeitüberschreitung bei der Generierung'}
        except Exception as e:
            return {'success': False, 'message': f'Fehler: {str(e)}'}
    
    def inject_api_code(self, notebook_json: dict, api_code: str) -> dict:
        """
        Fügt API-Code zu einem Notebook hinzu.
        
        Args:
            notebook_json: Das Notebook als JSON
            api_code: Der einzufügende API-Code
        
        Returns:
            Modifiziertes Notebook
        """
        # Neue Zelle mit API-Code erstellen
        api_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": api_code.split('\n')
        }
        
        # Am Ende des Notebooks einfügen
        notebook_json['cells'].append(api_cell)
        
        return notebook_json
    
    def download_notebook_from_github(self, github_url: str) -> dict:
        """
        Lädt ein Notebook von GitHub herunter.
        
        Args:
            github_url: GitHub-URL zum Notebook
        
        Returns:
            Notebook als JSON-Dictionary
        """
        # Konvertiere zu Raw-URL
        if 'github.com' in github_url and '/blob/' in github_url:
            raw_url = github_url.replace('github.com', 'raw.githubusercontent.com')
            raw_url = raw_url.replace('/blob/', '/')
        else:
            raw_url = github_url
        
        response = requests.get(raw_url, timeout=30)
        response.raise_for_status()
        
        return response.json()


class ColabAPI:
    """
    API-Klasse für pywebview.
    Wird von JavaScript aufgerufen.
    """
    
    def __init__(self, colab_manager: ColabManager):
        self.manager = colab_manager
        self.last_image_data: Optional[bytes] = None
    
    def get_accounts(self) -> List[Dict]:
        """Gibt alle Accounts zurück"""
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
    
    def set_colab_url(self, url: str) -> Dict:
        """Setzt die Colab API-URL"""
        return self.manager.set_api_url(url)
    
    def check_connection(self) -> Dict:
        """Prüft die Verbindung"""
        return self.manager.check_connection()
    
    def generate(self, params: Dict) -> Dict:
        """Generiert ein Bild"""
        result = self.manager.generate(params)
        if result.get('success') and result.get('image'):
            self.last_image_data = base64.b64decode(result['image'])
        return result
    
    def open_colab(self, url: str, account_email: str = None) -> Dict:
        """Öffnet Colab im Browser"""
        try:
            self.manager.open_colab_in_browser(url, account_email)
            return {'success': True, 'message': 'Colab im Browser geöffnet'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def load_image(self) -> Dict:
        """Lädt ein Bild von der Festplatte"""
        import webview
        
        try:
            file_path = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=('Bilder (*.png;*.jpg;*.jpeg)', 'Alle Dateien (*.*)')
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
        import webview
        
        if not self.last_image_data:
            return {'success': False, 'message': 'Kein Bild zum Speichern vorhanden'}
        
        try:
            save_path = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=filename,
                file_types=('PNG Bilder (*.png)', 'JPEG Bilder (*.jpg)', 'Alle Dateien (*.*)')
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(self.last_image_data)
                return {'success': True, 'message': f'Bild gespeichert: {save_path}'}
            else:
                return {'success': False, 'message': 'Speichern abgebrochen'}
                
        except Exception as e:
            return {'success': False, 'message': f'Fehler beim Speichern: {str(e)}'}
