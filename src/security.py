"""
Módulo de Segurança
Validação, sanitização e rate limiting
"""

import asyncio
import logging
import hashlib
import re
from typing import Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Gerencia segurança do bot
    - Validação de entrada
    - Sanitização
    - Rate limiting por minuto
    - Proteção contra spam
    """
    
    def __init__(self, max_prompt_length: int = 2000, max_requests_per_minute: int = 10):
        """
        Inicializa o gerenciador de segurança
        
        max_prompt_length: Tamanho máximo de prompt em caracteres
        max_requests_per_minute: Máximo de requisições por minuto por usuário
        """
        self.max_prompt_length = max_prompt_length
        self.max_requests_per_minute = max_requests_per_minute
        
        # Rate limiting: {user_id: [(timestamp, count), ...]}
        self.rate_limit_history: Dict[int, list] = {}
        self.lock = asyncio.Lock()
        
        logger.info(
            f"SecurityManager inicializado "
            f"(max_prompt={max_prompt_length}, max_req/min={max_requests_per_minute})"
        )
    
    @staticmethod
    def hash_user_id(user_id: int) -> str:
        """Converte ID de usuário em hash para logs seguros"""
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """
        Sanitiza prompt removendo caracteres perigosos
        Mantém caracteres alfanuméricos, espaços e pontuação comum
        """
        # Remover caracteres de controle
        prompt = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
        
        # Remover múltiplos espaços
        prompt = re.sub(r'\s+', ' ', prompt)
        
        # Remover espaços nas extremidades
        prompt = prompt.strip()
        
        return prompt
    
    async def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Valida prompt
        Retorna (válido, mensagem)
        """
        if not prompt or len(prompt.strip()) == 0:
            return False, "Prompt vazio"
        
        if len(prompt) > self.max_prompt_length:
            return False, f"Prompt muito longo (máx {self.max_prompt_length} caracteres)"
        
        # Detectar spam (muitos caracteres repetidos)
        if self._is_spam_pattern(prompt):
            return False, "Padrão de spam detectado"
        
        return True, ""
    
    @staticmethod
    def _is_spam_pattern(text: str) -> bool:
        """Detecta padrões de spam"""
        # Mais de 70% do texto é o mesmo caractere
        if len(text) > 10:
            char_counts = {}
            for char in text:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            max_count = max(char_counts.values())
            if max_count / len(text) > 0.7:
                return True
        
        return False
    
    async def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """
        Verifica rate limit por minuto
        Retorna (permitido, mensagem)
        """
        async with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            # Inicializar se não existe
            if user_id not in self.rate_limit_history:
                self.rate_limit_history[user_id] = []
            
            # Remover entradas antigas (>1 minuto)
            self.rate_limit_history[user_id] = [
                (timestamp, count)
                for timestamp, count in self.rate_limit_history[user_id]
                if timestamp > one_minute_ago
            ]
            
            # Contar requisições no último minuto
            total_requests = sum(count for _, count in self.rate_limit_history[user_id])
            
            if total_requests >= self.max_requests_per_minute:
                user_hash = self.hash_user_id(user_id)
                logger.warning(
                    f"Rate limit excedido para usuário {user_hash}: "
                    f"{total_requests}/{self.max_requests_per_minute} req/min"
                )
                return False, f"Limite de requisições atingido ({self.max_requests_per_minute}/min)"
            
            return True, ""
    
    async def record_request(self, user_id: int):
        """Registra uma requisição para rate limiting"""
        async with self.lock:
            now = datetime.now()
            
            if user_id not in self.rate_limit_history:
                self.rate_limit_history[user_id] = []
            
            self.rate_limit_history[user_id].append((now, 1))
    
    async def get_rate_limit_stats(self, user_id: int) -> Dict:
        """Retorna estatísticas de rate limit para um usuário"""
        async with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            if user_id not in self.rate_limit_history:
                return {"requests_this_minute": 0, "limit": self.max_requests_per_minute}
            
            # Contar requisições no último minuto
            recent = [
                (timestamp, count)
                for timestamp, count in self.rate_limit_history[user_id]
                if timestamp > one_minute_ago
            ]
            
            total = sum(count for _, count in recent)
            
            return {
                "requests_this_minute": total,
                "limit": self.max_requests_per_minute,
                "remaining": max(0, self.max_requests_per_minute - total)
            }
    
    async def clear_user_history(self, user_id: int):
        """Limpa histórico de rate limit de um usuário"""
        async with self.lock:
            if user_id in self.rate_limit_history:
                del self.rate_limit_history[user_id]
                logger.info(f"Histórico de rate limit limpo para usuário {self.hash_user_id(user_id)}")
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas gerais de segurança"""
        async with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            total_users = len(self.rate_limit_history)
            total_requests_now = 0
            
            for user_id, history in self.rate_limit_history.items():
                recent = [
                    (timestamp, count)
                    for timestamp, count in history
                    if timestamp > one_minute_ago
                ]
                total_requests_now += sum(count for _, count in recent)
            
            return {
                "tracked_users": total_users,
                "requests_last_minute": total_requests_now,
                "max_requests_per_minute": self.max_requests_per_minute,
                "max_prompt_length": self.max_prompt_length
            }
