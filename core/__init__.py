"""
=============================================================================
COLAB GUI GENERATOR - CORE MODULE
=============================================================================
Kernmodule für die automatische GUI-Generierung aus Colab-Notebooks.
=============================================================================
"""

from .notebook_parser import (
    NotebookParser,
    NotebookAnalysis,
    Parameter,
    Output,
    ParameterType,
    OutputType
)

from .gui_generator import GUIGenerator

from .colab_manager import (
    ColabManager,
    ColabAPI,
    GoogleAccount,
    ColabSession
)

from .theme_manager import (
    ThemeManager,
    ThemeMode,
    ThemeColors,
    get_theme_manager,
    DARK_THEME,
    LIGHT_THEME
)

from .ai_assistant import (
    AIAssistant,
    AIAnalysisResult,
    get_ai_assistant
)

__all__ = [
    # Parser
    'NotebookParser',
    'NotebookAnalysis',
    'Parameter',
    'Output',
    'ParameterType',
    'OutputType',
    
    # GUI Generator
    'GUIGenerator',
    
    # Colab Manager
    'ColabManager',
    'ColabAPI',
    'GoogleAccount',
    'ColabSession',
    
    # Theme Manager
    'ThemeManager',
    'ThemeMode',
    'ThemeColors',
    'get_theme_manager',
    'DARK_THEME',
    'LIGHT_THEME',
    
    # AI Assistant
    'AIAssistant',
    'AIAnalysisResult',
    'get_ai_assistant'
]

__version__ = '2.0.0'
