"""
Sistema de cooldown para evitar spam
Cooldown é aplicado APÓS sucesso da IA, não antes
"""

import time
import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class CooldownManager:
    """
    Gerencia cooldown por usuário com thread-safety
    Cooldown é aplicado APÓS sucesso, não antes
    """
    
    def __init__(self, default_cooldown: int = 5):
        """
        Inicializa o gerenciador de cooldown
        
        default_cooldown: Tempo em segundos entre requisições
        """
        self.default_cooldown = default_cooldown
        self.user_cooldowns: Dict[int, float] = {}
        self.lock = asyncio.Lock()
        logger.info(f"CooldownManager inicializado (cooldown padrão: {default_cooldown}s)")
    
    async def is_on_cooldown(self, user_id: int) -> bool:
        """Verifica se usuário está em cooldown"""
        async with self.lock:
            if user_id not in self.user_cooldowns:
                return False
            
            elapsed = time.time() - self.user_cooldowns[user_id]
            on_cooldown = elapsed < self.default_cooldown
            
            if on_cooldown:
                logger.debug(f"Usuário {user_id} ainda em cooldown ({self.get_remaining_sync(user_id)}s)")
            
            return on_cooldown
    
    async def get_remaining(self, user_id: int) -> int:
        """Retorna segundos restantes de cooldown"""
        async with self.lock:
            return self.get_remaining_sync(user_id)
    
    def get_remaining_sync(self, user_id: int) -> int:
        """Versão síncrona para uso interno"""
        if user_id not in self.user_cooldowns:
            return 0
        
        elapsed = time.time() - self.user_cooldowns[user_id]
        remaining = max(0, self.default_cooldown - int(elapsed))
        return remaining
    
    async def set_cooldown(self, user_id: int):
        """
        Define cooldown para usuário
        Chamado APÓS sucesso da IA
        """
        async with self.lock:
            self.user_cooldowns[user_id] = time.time()
            logger.debug(f"Cooldown definido para usuário {user_id} ({self.default_cooldown}s)")
    
    async def reset(self, user_id: int):
        """Remove cooldown do usuário"""
        async with self.lock:
            if user_id in self.user_cooldowns:
                del self.user_cooldowns[user_id]
                logger.debug(f"Cooldown removido para usuário {user_id}")
    
    async def clear_all(self):
        """Limpa todos os cooldowns"""
        async with self.lock:
            self.user_cooldowns.clear()
            logger.info("Todos os cooldowns foram limpos")
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas de cooldowns ativos"""
        async with self.lock:
            now = time.time()
            active_cooldowns = {
                uid: self.get_remaining_sync(uid)
                for uid in self.user_cooldowns
                if now - self.user_cooldowns[uid] < self.default_cooldown
            }
            
            return {
                "active_cooldowns": len(active_cooldowns),
                "users": active_cooldowns,
                "default_cooldown": self.default_cooldown
            }
