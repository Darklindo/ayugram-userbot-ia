"""
Gerenciador de estatísticas com thread-safety
Rastreia uso do bot e dos provedores de IA
"""

import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class StatsManager:
    """
    Gerencia estatísticas de uso do bot com thread-safety
    Usa asyncio.Lock para evitar race conditions
    """
    
    def __init__(self, stats_file: str = "stats.json"):
        """Inicializa o gerenciador de estatísticas"""
        self.stats_file = stats_file
        self.stats = self._load_stats_sync()
        self.lock = asyncio.Lock()
        logger.info("StatsManager inicializado com lock")
    
    def _load_stats_sync(self) -> Dict:
        """Carrega estatísticas do arquivo (versão síncrona para __init__)"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar stats: {e}")
        
        return {
            "total_queries": 0,
            "total_errors": 0,
            "providers": {},
            "users": {},
            "created_at": datetime.now().isoformat()
        }
    
    def _save_stats_sync(self):
        """Salva estatísticas em arquivo (versão síncrona)"""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
            logger.debug("Stats salvos")
        except Exception as e:
            logger.exception("Erro ao salvar stats")
    
    async def record_query(self, user_id: int, provider: str, success: bool = True):
        """Registra uma query (thread-safe)"""
        async with self.lock:
            self.stats["total_queries"] += 1
            
            if not success:
                self.stats["total_errors"] += 1
            
            # Provider stats
            if provider not in self.stats["providers"]:
                self.stats["providers"][provider] = {
                    "queries": 0,
                    "errors": 0
                }
            
            self.stats["providers"][provider]["queries"] += 1
            if not success:
                self.stats["providers"][provider]["errors"] += 1
            
            # User stats
            user_id_str = str(user_id)
            if user_id_str not in self.stats["users"]:
                self.stats["users"][user_id_str] = {
                    "queries": 0,
                    "errors": 0,
                    "favorite_provider": None
                }
            
            self.stats["users"][user_id_str]["queries"] += 1
            if not success:
                self.stats["users"][user_id_str]["errors"] += 1
            
            # Atualizar provider favorito
            if self.stats["users"][user_id_str]["favorite_provider"] is None:
                self.stats["users"][user_id_str]["favorite_provider"] = provider
            
            self._save_stats_sync()
            logger.debug(f"Query registrada: user={user_id}, provider={provider}, success={success}")
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas gerais (thread-safe)"""
        async with self.lock:
            return {
                "total_queries": self.stats["total_queries"],
                "total_errors": self.stats["total_errors"],
                "error_rate": f"{(self.stats['total_errors'] / max(1, self.stats['total_queries']) * 100):.1f}%",
                "providers": self.stats["providers"].copy(),
                "total_users": len(self.stats["users"]),
                "created_at": self.stats["created_at"]
            }
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Retorna estatísticas de um usuário (thread-safe)"""
        async with self.lock:
            user_id_str = str(user_id)
            if user_id_str not in self.stats["users"]:
                return None
            
            user_stats = self.stats["users"][user_id_str]
            return {
                "queries": user_stats["queries"],
                "errors": user_stats["errors"],
                "error_rate": f"{(user_stats['errors'] / max(1, user_stats['queries']) * 100):.1f}%",
                "favorite_provider": user_stats["favorite_provider"]
            }
    
    async def get_provider_stats(self, provider: str) -> Dict:
        """Retorna estatísticas de um provedor (thread-safe)"""
        async with self.lock:
            if provider not in self.stats["providers"]:
                return None
            
            prov_stats = self.stats["providers"][provider]
            return {
                "queries": prov_stats["queries"],
                "errors": prov_stats["errors"],
                "error_rate": f"{(prov_stats['errors'] / max(1, prov_stats['queries']) * 100):.1f}%",
                "percentage": f"{(prov_stats['queries'] / max(1, self.stats['total_queries']) * 100):.1f}%"
            }
    
    async def format_stats(self) -> str:
        """Formata estatísticas para exibição (thread-safe)"""
        stats = await self.get_stats()
        lines = [
            "📊 ESTATÍSTICAS DO BOT",
            f"Total de queries: {stats['total_queries']}",
            f"Total de erros: {stats['total_errors']}",
            f"Taxa de erro: {stats['error_rate']}",
            f"Usuários únicos: {stats['total_users']}",
            "",
            "Provedores:"
        ]
        
        for provider, prov_stats in stats["providers"].items():
            prov_info = await self.get_provider_stats(provider)
            lines.append(f"  {provider}: {prov_stats['queries']} queries ({prov_info['percentage']})")
        
        return "\n".join(lines)
    
    async def format_user_stats(self, user_id: int) -> str:
        """Formata estatísticas de um usuário (thread-safe)"""
        user_stats = await self.get_user_stats(user_id)
        if not user_stats:
            return "Nenhuma estatística para este usuário"
        
        lines = [
            f"📊 SUAS ESTATÍSTICAS",
            f"Total de queries: {user_stats['queries']}",
            f"Total de erros: {user_stats['errors']}",
            f"Taxa de erro: {user_stats['error_rate']}",
            f"Provedor favorito: {user_stats['favorite_provider']}"
        ]
        
        return "\n".join(lines)
