"""
Pacote de provedores de IA
"""

from .base import IAProvider
from .gemini import GeminiProvider
from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider
from .manager import IAManager

__all__ = [
    "IAProvider",
    "GeminiProvider",
    "DeepSeekProvider",
    "OpenAIProvider",
    "IAManager",
]
