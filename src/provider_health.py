"""
Circuit Breaker e Health Check para Provedores de IA
Monitora disponibilidade e performance dos provedores
"""

import logging
import asyncio
import time
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Estados possíveis de um provedor"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderMetrics:
    """Métricas de um provedor"""
    name: str
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_check: float = 0
    response_time: float = 0
    error_count: int = 0
    success_count: int = 0
    consecutive_errors: int = 0
    last_error: Optional[str] = None
    tokens_used: int = 0
    requests_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calcula taxa de sucesso"""
        total = self.success_count + self.error_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100
    
    @property
    def avg_response_time(self) -> float:
        """Calcula tempo médio de resposta"""
        if self.requests_count == 0:
            return 0.0
        return self.response_time / self.requests_count


class CircuitBreaker:
    """Circuit Breaker para provedores"""
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 success_threshold: int = 2):
        """
        Inicializa circuit breaker
        
        failure_threshold: Número de falhas para abrir circuito
        recovery_timeout: Segundos para tentar recuperação
        success_threshold: Sucessos para fechar circuito
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.metrics = ProviderMetrics(name=name)
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.opened_at = 0
    
    async def call(self, coro):
        """
        Executa chamada com proteção de circuit breaker
        """
        if self.state == "OPEN":
            if time.time() - self.opened_at > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"[{self.name}] Circuit breaker em HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker OPEN para {self.name}")
        
        try:
            start_time = time.time()
            result = await coro
            response_time = time.time() - start_time
            
            self.record_success(response_time)
            return result
        
        except Exception as e:
            self.record_failure(str(e))
            raise
    
    def record_success(self, response_time: float):
        """Registra sucesso"""
        self.metrics.success_count += 1
        self.metrics.consecutive_errors = 0
        self.metrics.response_time += response_time
        self.metrics.requests_count += 1
        self.metrics.last_check = time.time()
        
        if self.state == "HALF_OPEN":
            if self.metrics.success_count >= self.success_threshold:
                self.state = "CLOSED"
                logger.info(f"[{self.name}] Circuit breaker FECHADO")
                self.metrics.success_count = 0
        
        self.update_status()
    
    def record_failure(self, error: str):
        """Registra falha"""
        self.metrics.error_count += 1
        self.metrics.consecutive_errors += 1
        self.metrics.last_error = error
        self.metrics.last_check = time.time()
        
        if self.metrics.consecutive_errors >= self.failure_threshold:
            if self.state != "OPEN":
                self.state = "OPEN"
                self.opened_at = time.time()
                logger.warning(f"[{self.name}] Circuit breaker ABERTO após {self.metrics.consecutive_errors} falhas")
        
        self.update_status()
    
    def update_status(self):
        """Atualiza status do provedor"""
        if self.metrics.success_rate >= 90:
            self.metrics.status = ProviderStatus.HEALTHY
        elif self.metrics.success_rate >= 70:
            self.metrics.status = ProviderStatus.DEGRADED
        else:
            self.metrics.status = ProviderStatus.UNHEALTHY


class ProviderHealthMonitor:
    """Monitora saúde de múltiplos provedores"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.metrics: Dict[str, ProviderMetrics] = {}
    
    def register_provider(self, name: str) -> CircuitBreaker:
        """Registra novo provedor"""
        breaker = CircuitBreaker(name)
        self.breakers[name] = breaker
        self.metrics[name] = breaker.metrics
        logger.info(f"Provedor {name} registrado")
        return breaker
    
    def get_best_provider(self) -> Optional[str]:
        """Retorna provedor com melhor performance"""
        if not self.metrics:
            return None
        
        # Filtrar provedores saudáveis
        healthy = {
            name: metrics for name, metrics in self.metrics.items()
            if metrics.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]
        }
        
        if not healthy:
            logger.warning("Nenhum provedor saudável disponível")
            return None
        
        # Retornar com melhor tempo de resposta
        best = min(healthy.items(), key=lambda x: x[1].avg_response_time)
        return best[0]
    
    def get_fallback_provider(self, exclude: str = None) -> Optional[str]:
        """Retorna provedor de fallback (excluindo um específico)"""
        available = [
            name for name, metrics in self.metrics.items()
            if metrics.status != ProviderStatus.UNHEALTHY and name != exclude
        ]
        
        if available:
            return available[0]
        return None
    
    def get_status_report(self) -> Dict:
        """Retorna relatório de status de todos os provedores"""
        report = {}
        for name, metrics in self.metrics.items():
            report[name] = {
                "status": metrics.status.value,
                "success_rate": f"{metrics.success_rate:.1f}%",
                "avg_response_time": f"{metrics.avg_response_time:.2f}s",
                "consecutive_errors": metrics.consecutive_errors,
                "last_error": metrics.last_error,
                "requests": metrics.requests_count
            }
        return report


# Instância global
health_monitor = ProviderHealthMonitor()


async def health_check_loop(interval: int = 300):
    """
    Loop de health check periódico
    Verifica saúde dos provedores a cada `interval` segundos
    """
    while True:
        try:
            await asyncio.sleep(interval)
            logger.info("Executando health check dos provedores...")
            
            # Aqui você pode adicionar verificações específicas
            # Por exemplo, fazer uma chamada leve para cada provedor
            
            report = health_monitor.get_status_report()
            logger.info(f"Health check completo: {report}")
        
        except Exception as e:
            logger.exception(f"Erro no health check: {e}")
