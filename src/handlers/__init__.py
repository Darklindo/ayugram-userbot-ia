"""
Pacote de handlers para o JT IA Bot
Organiza handlers de eventos em módulos separados
"""

from .ia_handlers import register_ia_handlers
from .admin_handlers import register_admin_handlers
from .search_handlers import register_search_handlers
from .persona_handlers import register_persona_handlers
from .stats_handlers import register_stats_handlers
from .help_handlers import register_help_handlers

__all__ = [
    "register_ia_handlers",
    "register_admin_handlers",
    "register_search_handlers",
    "register_persona_handlers",
    "register_stats_handlers",
    "register_help_handlers",
]
