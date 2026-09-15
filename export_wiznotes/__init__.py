"""
WizNote Export Toolkit

Основные модули:
- wiz_client: Базовый класс клиента WizNote
- collaboration_parser: Модуль для разбора заметок, предназначенных для совместной работы
- note_exporter: Модуль для экспорта заметок
- utils: Модуль вспомогательных функций
"""

from .wiz_client import WizNoteClient
from .collaboration_parser import CollaborationParser
from .note_exporter import NoteExporter
from .utils import setup_logging, list_folders_and_notes

__version__ = "1.0.0"
__author__ = "WizNotes Export Tool"

__all__ = [
    'WizNoteClient',
    'CollaborationParser',
    'NoteExporter',
    'setup_logging',
    'list_folders_and_notes'
]
