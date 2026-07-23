"""
Sistema de Métricas para Rastreamento de Performance
Coleta dados de tempo de resposta, erros, tokens, etc.
"""

import logging
import time
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RequestMetric:
    """Métrica de uma requisição"""
    timestamp: float
    provider: str
    command: str
    response_time: float
    tokens_used: int
    success: bool
    error: Optional[str] = None
    user_id: int = 0
    chat_id: int = 0


class MetricsCollector:
    """Coleta e analisa métricas de performance"""
    
    def __init__(self):
        self.metrics: List[RequestMetric] = []
        self.lock = asyncio.Lock()
        
        # Agregações por período
        self.hourly_stats = defaultdict(lambda: {
            "requests": 0,
            "errors": 0,
            "total_time": 0,
            "total_tokens": 0
        })
        
        self.daily_stats = defaultdict(lambda: {
            "requests": 0,
            "errors": 0,
            "total_time": 0,
            "total_tokens": 0
        })
    
    async def record_request(self, 
                           provider: str,
                           command: str,
                           response_time: float,
                           tokens_used: int = 0,
                           success: bool = True,
                           error: Optional[str] = None,
                           user_id: int = 0,
                           chat_id: int = 0):
        """Registra métrica de requisição"""
        async with self.lock:
            metric = RequestMetric(
                timestamp=time.time(),
                provider=provider,
                command=command,
                response_time=response_time,
                tokens_used=tokens_used,
                success=success,
                error=error,
                user_id=user_id,
                chat_id=chat_id
            )
            
            self.metrics.append(metric)
            
            # Atualizar agregações
            now = datetime.now()
            hour_key = now.strftime("%Y-%m-%d %H:00")
            day_key = now.strftime("%Y-%m-%d")
            
            self.hourly_stats[hour_key]["requests"] += 1
            self.daily_stats[day_key]["requests"] += 1
            
            if not success:
                self.hourly_stats[hour_key]["errors"] += 1
                self.daily_stats[day_key]["errors"] += 1
            
            self.hourly_stats[hour_key]["total_time"] += response_time
            self.daily_stats[day_key]["total_time"] += response_time
            
            self.hourly_stats[hour_key]["total_tokens"] += tokens_used
            self.daily_stats[day_key]["total_tokens"] += tokens_used
            
            # Limpar métricas antigas (mais de 7 dias)
            await self._cleanup_old_metrics()
    
    async def _cleanup_old_metrics(self):
        """Remove métricas mais antigas que 7 dias"""
        cutoff_time = time.time() - (7 * 24 * 3600)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
    
    def get_provider_stats(self, provider: str, hours: int = 24) -> Dict:
        """Retorna estatísticas de um provedor"""
        cutoff_time = time.time() - (hours * 3600)
        
        provider_metrics = [
            m for m in self.metrics 
            if m.provider == provider and m.timestamp > cutoff_time
        ]
        
        if not provider_metrics:
            return {
                "provider": provider,
                "requests": 0,
                "errors": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "total_tokens": 0
            }
        
        total_requests = len(provider_metrics)
        total_errors = sum(1 for m in provider_metrics if not m.success)
        total_time = sum(m.response_time for m in provider_metrics)
        total_tokens = sum(m.tokens_used for m in provider_metrics)
        
        return {
            "provider": provider,
            "requests": total_requests,
            "errors": total_errors,
            "success_rate": f"{((total_requests - total_errors) / total_requests * 100):.1f}%",
            "avg_response_time": f"{(total_time / total_requests):.2f}s",
            "total_tokens": total_tokens
        }
    
    def get_command_stats(self, command: str, hours: int = 24) -> Dict:
        """Retorna estatísticas de um comando"""
        cutoff_time = time.time() - (hours * 3600)
        
        command_metrics = [
            m for m in self.metrics 
            if m.command == command and m.timestamp > cutoff_time
        ]
        
        if not command_metrics:
            return {
                "command": command,
                "requests": 0,
                "errors": 0,
                "success_rate": 0,
                "avg_response_time": 0
            }
        
        total_requests = len(command_metrics)
        total_errors = sum(1 for m in command_metrics if not m.success)
        total_time = sum(m.response_time for m in command_metrics)
        
        return {
            "command": command,
            "requests": total_requests,
            "errors": total_errors,
            "success_rate": f"{((total_requests - total_errors) / total_requests * 100):.1f}%",
            "avg_response_time": f"{(total_time / total_requests):.2f}s"
        }
    
    def get_user_stats(self, user_id: int, hours: int = 24) -> Dict:
        """Retorna estatísticas de um usuário"""
        cutoff_time = time.time() - (hours * 3600)
        
        user_metrics = [
            m for m in self.metrics 
            if m.user_id == user_id and m.timestamp > cutoff_time
        ]
        
        if not user_metrics:
            return {
                "user_id": user_id,
                "requests": 0,
                "tokens_used": 0
            }
        
        return {
            "user_id": user_id,
            "requests": len(user_metrics),
            "tokens_used": sum(m.tokens_used for m in user_metrics),
            "most_used_command": max(
                set(m.command for m in user_metrics),
                key=lambda x: sum(1 for m in user_metrics if m.command == x)
            ) if user_metrics else "N/A"
        }
    
    def get_overall_stats(self, hours: int = 24) -> Dict:
        """Retorna estatísticas gerais"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {
                "period_hours": hours,
                "total_requests": 0,
                "total_errors": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "total_tokens": 0
            }
        
        total_requests = len(recent_metrics)
        total_errors = sum(1 for m in recent_metrics if not m.success)
        total_time = sum(m.response_time for m in recent_metrics)
        total_tokens = sum(m.tokens_used for m in recent_metrics)
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "success_rate": f"{((total_requests - total_errors) / total_requests * 100):.1f}%",
            "avg_response_time": f"{(total_time / total_requests):.2f}s",
            "total_tokens": total_tokens,
            "requests_per_hour": f"{(total_requests / hours):.1f}"
        }
    
    def get_error_report(self, hours: int = 24) -> Dict:
        """Retorna relatório de erros"""
        cutoff_time = time.time() - (hours * 3600)
        
        errors = [
            m for m in self.metrics 
            if not m.success and m.timestamp > cutoff_time
        ]
        
        error_counts = defaultdict(int)
        for error in errors:
            error_counts[error.error] += 1
        
        return {
            "period_hours": hours,
            "total_errors": len(errors),
            "error_types": dict(error_counts)
        }


# Instância global
metrics_collector = MetricsCollector()
