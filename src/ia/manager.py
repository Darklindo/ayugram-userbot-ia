"""
Gerenciador de provedores de IA com fallback automático
"""

import logging
import json
import os
from typing import Optional, Dict
from .base import IAProvider
from .groq import GroqProvider
from .openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

class IAManager:
    """Gerencia multiplos provedores de IA com fallback automático"""
    
    PROVIDERS = {
        "groq": GroqProvider,
        "openrouter": OpenRouterProvider,
    }
    
    # Aliases para nomes reais
    ALIASES = {
        "groq": "groq",
        "router": "openrouter",
    }
    
    # Timeout por provedor (segundos)
    TIMEOUTS = {
        "gemini": 30,
        "groq": 20,
        "openrouter": 60,
    }
    
    # Ordem de fallback: Groq (principal) -> OpenRouter
    FALLBACK_ORDER = ["groq", "openrouter"]
    
    def __init__(self, default_provider: str, api_keys: Dict[str, str]):
        """
        Inicializa o gerenciador
        
        default_provider: 'gemini', 'groq' ou 'openrouter'
        api_keys: {'gemini': 'chave', 'groq': 'chave', 'openrouter': 'chave'}
        """
        self.default_provider = self._resolve_alias(default_provider).lower()
        self.api_keys = api_keys
        self.providers: Dict[str, IAProvider] = {}
        self.current_provider = None
        self.config_file = "ia_config.json"
        
        if self.default_provider not in self.PROVIDERS:
            raise ValueError(f"Provider desconhecido: {default_provider}")
        
        logger.info(f"IAManager: Provider padrao = {self.default_provider}")
    
    def _resolve_alias(self, name: str) -> str:
        """Resolve aliases para nomes reais"""
        name = name.lower()
        return self.ALIASES.get(name, name)
    
    def _save_config(self):
        """Salva o provider atual em arquivo"""
        try:
            config = {"default_provider": self.default_provider}
            with open(self.config_file, "w") as f:
                json.dump(config, f)
            logger.debug(f"Configuracao salva: {self.default_provider}")
        except Exception as e:
            logger.exception("Erro ao salvar configuracao de IA")
    
    def _load_config(self):
        """Carrega o provider salvo do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    provider = config.get("default_provider")
                    if provider and provider in self.PROVIDERS:
                        self.default_provider = provider
                        logger.info(f"Provider carregado do arquivo: {provider}")
        except Exception as e:
            logger.exception("Erro ao carregar configuracao de IA")
    
    async def init(self):
        """Inicializa o provider padrao"""
        self._load_config()
        if not self.current_provider:
            await self.switch_provider(self.default_provider)
    
    async def switch_provider(self, provider_name: str) -> bool:
        """Muda para um provider diferente"""
        provider_name = self._resolve_alias(provider_name).lower()
        
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
            self._save_config()
            logger.info(f"IAManager: Mudou para {provider_name}")
            return True
        
        except Exception as e:
            logger.exception(f"Erro ao mudar para {provider_name}")
            return False
    
    async def process(self, prompt: str, provider: Optional[str] = None) -> str:
        """
        Processa uma pergunta com fallback automático
        
        prompt: A pergunta
        provider: Provider especifico (opcional, usa o padrao se nao informado)
        """
        if provider:
            # Usar provider especifico sem fallback
            provider = self._resolve_alias(provider).lower()
            if provider not in self.PROVIDERS:
                return f"Erro: Provider desconhecido '{provider}'. Use: gemini, groq, openrouter"
            
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
        
        # Tentar com provider padrao
        response = await self.current_provider.process(prompt)
        
        # Se falhar, tentar fallback automatico
        if response.startswith("Erro"):
            logger.warning(f"Fallback: {self.default_provider} falhou, tentando outros...")
            
            # Ordem de fallback: Groq -> OpenRouter
            current_idx = self.FALLBACK_ORDER.index(self.default_provider) if self.default_provider in self.FALLBACK_ORDER else 0
            
            for i in range(1, len(self.FALLBACK_ORDER)):
                fallback_name = self.FALLBACK_ORDER[(current_idx + i) % len(self.FALLBACK_ORDER)]
                
                if fallback_name not in self.api_keys:
                    continue
                
                try:
                    if fallback_name not in self.providers:
                        provider_class = self.PROVIDERS[fallback_name]
                        self.providers[fallback_name] = provider_class(self.api_keys[fallback_name])
                        await self.providers[fallback_name].init_session()
                    
                    logger.info(f"Tentando fallback com {fallback_name}")
                    response = await self.providers[fallback_name].process(prompt)
                    
                    if not response.startswith("Erro"):
                        logger.info(f"Fallback bem-sucedido com {fallback_name}")
                        return response
                
                except Exception as e:
                    logger.warning(f"Fallback com {fallback_name} falhou: {e}")
                    continue
        
        return response
    
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
        """Retorna lista de providers disponiveis (sem duplicatas de aliases)"""
        available = []
        for name in self.PROVIDERS.keys():
            if name in self.api_keys:
                available.append(name)
        return available
    
    def get_timeout(self, provider: Optional[str] = None) -> int:
        """Retorna timeout para um provider"""
        if not provider:
            provider = self.default_provider
        
        provider = self._resolve_alias(provider).lower()
        return self.TIMEOUTS.get(provider, 30)
