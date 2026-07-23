"""
Gerenciador de Cache e Retry
Cache de respostas com TTL e retry automático com exponential backoff
"""

import asyncio
import logging
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerencia cache de respostas com TTL
    Implementa LRU cache com limpeza automática
    """
    
    def __init__(self, ttl_minutes: int = 60, max_cache_size: int = 500):
        """
        Inicializa o gerenciador de cache
        
        ttl_minutes: Tempo de vida em minutos
        max_cache_size: Tamanho máximo do cache
        """
        self.ttl_minutes = ttl_minutes
        self.max_cache_size = max_cache_size
        
        # Cache: {hash_prompt: {"response": str, "timestamp": datetime, "hits": int}}
        self.cache: Dict = {}
        self.lock = asyncio.Lock()
        
        logger.info(f"CacheManager inicializado (TTL {ttl_minutes}min, max {max_cache_size} itens)")
    
    @staticmethod
    def hash_prompt(prompt: str) -> str:
        """Cria hash do prompt para chave de cache"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    async def get(self, prompt: str) -> Optional[str]:
        """Retorna resposta em cache se existir e ainda válida"""
        async with self.lock:
            key = self.hash_prompt(prompt)
            
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Verificar se expirou
            if datetime.now() - entry["timestamp"] > timedelta(minutes=self.ttl_minutes):
                del self.cache[key]
                logger.debug(f"Cache expirado para prompt {key}")
                return None
            
            # Incrementar hits
            entry["hits"] += 1
            logger.debug(f"Cache hit para prompt {key} (hits: {entry['hits']})")
            
            return entry["response"]
    
    async def set(self, prompt: str, response: str) -> bool:
        """Armazena resposta em cache"""
        async with self.lock:
            # Limpar cache se exceder tamanho máximo
            if len(self.cache) >= self.max_cache_size:
                await self._cleanup_lru()
            
            key = self.hash_prompt(prompt)
            self.cache[key] = {
                "response": response,
                "timestamp": datetime.now(),
                "hits": 0
            }
            
            logger.debug(f"Cache armazenado para prompt {key}")
            return True
    
    async def _cleanup_lru(self):
        """Remove 20% dos itens menos acessados (LRU)"""
        # Ordenar por hits (menos acessados primeiro)
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1]["hits"]
        )
        
        # Remover 20% dos itens
        remove_count = max(1, len(sorted_items) // 5)
        for key, _ in sorted_items[:remove_count]:
            del self.cache[key]
        
        logger.info(f"Cache LRU cleanup: removidos {remove_count} itens")
    
    async def clear(self):
        """Limpa todo o cache"""
        async with self.lock:
            self.cache.clear()
            logger.info("Cache completamente limpo")
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        async with self.lock:
            now = datetime.now()
            
            # Contar itens válidos e expirados
            valid_items = 0
            expired_items = 0
            total_hits = 0
            
            for entry in self.cache.values():
                if now - entry["timestamp"] > timedelta(minutes=self.ttl_minutes):
                    expired_items += 1
                else:
                    valid_items += 1
                    total_hits += entry["hits"]
            
            return {
                "valid_items": valid_items,
                "expired_items": expired_items,
                "total_hits": total_hits,
                "max_size": self.max_cache_size,
                "ttl_minutes": self.ttl_minutes
            }


class RetryManager:
    """
    Gerencia retry automático com exponential backoff
    Ideal para erros transitórios (429, 500, timeout)
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        """
        Inicializa o gerenciador de retry
        
        max_retries: Número máximo de tentativas
        base_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        logger.info(
            f"RetryManager inicializado "
            f"(max_retries={max_retries}, base_delay={base_delay}s, max_delay={max_delay}s)"
        )
    
    async def execute_with_retry(self, coro, error_codes: tuple = (429, 500, 502, 503, 504)):
        """
        Executa coroutine com retry automático
        
        coro: Coroutine a executar
        error_codes: Códigos de erro que disparam retry
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await coro
                
                if attempt > 0:
                    logger.info(f"Sucesso na tentativa {attempt + 1}/{self.max_retries + 1}")
                
                return result
            
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Timeout na tentativa {attempt + 1}/{self.max_retries + 1}, "
                        f"aguardando {delay}s..."
                    )
                    await asyncio.sleep(delay)
            
            except Exception as e:
                last_exception = e
                
                # Verificar se é erro que merece retry
                error_code = getattr(e, 'code', None)
                should_retry = error_code in error_codes if error_code else False
                
                if should_retry and attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Erro {error_code} na tentativa {attempt + 1}/{self.max_retries + 1}, "
                        f"aguardando {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    # Não é erro que merece retry ou já excedeu tentativas
                    raise
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"Falha após {self.max_retries + 1} tentativas")
        raise last_exception
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calcula delay com exponential backoff"""
        # Exponential backoff: base_delay * 2^attempt
        delay = self.base_delay * (2 ** attempt)
        
        # Limitar ao máximo
        delay = min(delay, self.max_delay)
        
        # Adicionar jitter (±10%)
        import random
        jitter = delay * random.uniform(-0.1, 0.1)
        delay = delay + jitter
        
        return max(self.base_delay, delay)
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas do retry manager"""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay
        }


class RequestQueue:
    """
    Fila de requisições para limitar chamadas às IAs
    Processa requisições sequencialmente para evitar sobrecarga
    """
    
    def __init__(self, max_concurrent: int = 3):
        """
        Inicializa a fila de requisições
        
        max_concurrent: Número máximo de requisições simultâneas
        """
        self.max_concurrent = max_concurrent
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks = 0
        self.lock = asyncio.Lock()
        self.processed = 0
        self.failed = 0
        
        logger.info(f"RequestQueue inicializada (max_concurrent={max_concurrent})")
    
    async def add_request(self, coro, priority: int = 0) -> any:
        """
        Adiciona requisição à fila
        
        coro: Coroutine a executar
        priority: Prioridade (maior = mais importante)
        """
        await self.queue.put((priority, coro))
        logger.debug(f"Requisição adicionada à fila (prioridade: {priority})")
    
    async def process_queue(self):
        """Processa fila de requisições"""
        while True:
            try:
                # Aguardar se já há max_concurrent requisições ativas
                async with self.lock:
                    while self.active_tasks >= self.max_concurrent:
                        await asyncio.sleep(0.1)
                    
                    self.active_tasks += 1
                
                # Obter próxima requisição (ordenada por prioridade)
                priority, coro = await self.queue.get()
                
                try:
                    result = await coro
                    async with self.lock:
                        self.processed += 1
                    logger.debug(f"Requisição processada (total: {self.processed})")
                    
                except Exception as e:
                    async with self.lock:
                        self.failed += 1
                    logger.exception(f"Erro ao processar requisição (falhas: {self.failed})")
                
                finally:
                    async with self.lock:
                        self.active_tasks -= 1
                    self.queue.task_done()
            
            except asyncio.CancelledError:
                logger.info("Fila de requisições cancelada")
                break
            except Exception as e:
                logger.exception("Erro no processamento da fila")
                await asyncio.sleep(1)
    
    async def get_stats(self) -> Dict:
        """Retorna estatísticas da fila"""
        async with self.lock:
            return {
                "queue_size": self.queue.qsize(),
                "active_tasks": self.active_tasks,
                "max_concurrent": self.max_concurrent,
                "processed": self.processed,
                "failed": self.failed
            }
