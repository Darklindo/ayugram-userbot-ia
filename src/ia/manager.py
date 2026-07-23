"""
Gerenciador de provedores de IA
"""

import logging
from typing import Optional, Dict
from .base import IAProvider
from .gemini import GeminiProvider
from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider

logger = logging.getLogger(__name__)

class IAManager:
    """Gerencia multiplos provedores de IA"""
    
    PROVIDERS = {
        "gemini": GeminiProvider,
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,  # Alias para OpenAI
        "deep": DeepSeekProvider,  # Alias para DeepSeek
    }
    
    def __init__(self, default_provider: str, api_keys: Dict[str, str]):
        """
        Inicializa o gerenciador
        
        default_provider: 'gemini', 'deepseek' ou 'openai'
        api_keys: {'gemini': 'chave', 'deepseek': 'chave', 'openai': 'chave'}
        """
        self.default_provider = default_provider.lower()
        self.api_keys = api_keys
        self.providers: Dict[str, IAProvider] = {}
        self.current_provider = None
        
        if self.default_provider not in self.PROVIDERS:
            raise ValueError(f"Provider desconhecido: {default_provider}")
        
        logger.info(f"IAManager: Provider padrao = {self.default_provider}")
    
    async def init(self):
        """Inicializa o provider padrao"""
        if not self.current_provider:
            await self.switch_provider(self.default_provider)
    
    async def switch_provider(self, provider_name: str) -> bool:
        """Muda para um provider diferente"""
        provider_name = provider_name.lower()
        
        if provider_name not in self.PROVIDERS:
            logger.error(f"Provider desconhecido: {provider_name}")
            return False
        
        if provider_name not in self.api_keys:
            logger.error(f"API key nao configurada para {provider_name}")
            return False
        
        try:
            if provider_name not in self.providers:
                provider_class = self.PROVIDERS[provider_name]
                self.providers[provider_name] = provider_class(self.api_keys[provider_name])
                await self.providers[provider_name].init_session()
                logger.info(f"IAManager: {provider_name} inicializado")
            
            self.current_provider = self.providers[provider_name]
            self.default_provider = provider_name
            logger.info(f"IAManager: Mudou para {provider_name}")
            return True
        
        except Exception as e:
            logger.exception(f"Erro ao mudar para {provider_name}")
            return False
    
    async def process(self, prompt: str, provider: Optional[str] = None) -> str:
        """
        Processa uma pergunta
        
        prompt: A pergunta
        provider: Provider especifico (opcional, usa o padrao se nao informado)
        """
        if provider:
            provider = provider.lower()
            if provider not in self.PROVIDERS:
                return f"Erro: Provider desconhecido '{provider}'. Use: gemini, deepseek, openai"
            
            if provider not in self.api_keys:
                return f"Erro: API key nao configurada para {provider}"
            
            if provider not in self.providers:
                try:
                    provider_class = self.PROVIDERS[provider]
                    self.providers[provider] = provider_class(self.api_keys[provider])
                    await self.providers[provider].init_session()
                except Exception as e:
                    logger.exception(f"Erro ao inicializar {provider}")
                    return f"Erro ao inicializar {provider}"
            
            return await self.providers[provider].process(prompt)
        
        if not self.current_provider:
            await self.init()
        
        return await self.current_provider.process(prompt)
    
    async def close_all(self):
        """Fecha todas as sessoes"""
        for provider in self.providers.values():
            try:
                await provider.close_session()
            except Exception as e:
                logger.exception(f"Erro ao fechar provider")
        
        logger.info("IAManager: Todas as sessoes fechadas")
    
    def get_current_provider(self) -> str:
        """Retorna o provider atual"""
        return self.default_provider
    
    def get_available_providers(self) -> list:
        """Retorna lista de providers disponiveis"""
        available = []
        for name in self.PROVIDERS.keys():
            if name in self.api_keys:
                available.append(name)
        return available
