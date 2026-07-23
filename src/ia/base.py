"""
Classe base para provedores de IA
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class IAProvider(ABC):
    """Classe base para todos os provedores de IA"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    @abstractmethod
    async def init_session(self):
        """Inicializa a sessao"""
        pass
    
    @abstractmethod
    async def close_session(self):
        """Fecha a sessao"""
        pass
    
    @abstractmethod
    async def process(self, prompt: str) -> str:
        """Processa uma pergunta e retorna a resposta"""
        pass
    
    def _validate_api_key(self):
        """Valida se a chave de API foi configurada"""
        if not self.api_key:
            raise ValueError(f"API key nao configurada para {self.__class__.__name__}")
