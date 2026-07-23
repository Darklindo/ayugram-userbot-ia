"""
Sistema de cooldown para evitar spam
"""

import time
import logging

logger = logging.getLogger(__name__)

class CooldownManager:
    def __init__(self, default_cooldown=5):
        self.default_cooldown = default_cooldown
        self.user_cooldowns = {}
    
    def is_on_cooldown(self, user_id: int) -> bool:
        """Verifica se usuario esta em cooldown"""
        if user_id not in self.user_cooldowns:
            return False
        
        elapsed = time.time() - self.user_cooldowns[user_id]
        return elapsed < self.default_cooldown
    
    def get_remaining(self, user_id: int) -> int:
        """Retorna segundos restantes de cooldown"""
        if user_id not in self.user_cooldowns:
            return 0
        
        elapsed = time.time() - self.user_cooldowns[user_id]
        remaining = max(0, self.default_cooldown - int(elapsed))
        return remaining
    
    def set_cooldown(self, user_id: int):
        """Define cooldown para usuario"""
        self.user_cooldowns[user_id] = time.time()
        logger.debug(f"Cooldown definido para usuario {user_id}")
    
    def reset(self, user_id: int):
        """Remove cooldown do usuario"""
        if user_id in self.user_cooldowns:
            del self.user_cooldowns[user_id]
            logger.debug(f"Cooldown removido para usuario {user_id}")
