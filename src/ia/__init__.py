"""
Pacote de provedores de IA
"""

from .base import IAProvider
from .groq import GroqProvider
from .openrouter import OpenRouterProvider
from .manager import IAManager

__all__ = [
    "IAProvider",
    "GroqProvider",
    "OpenRouterProvider",
    "IAManager",
]
