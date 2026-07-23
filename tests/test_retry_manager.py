"""
Testes para RetryManager
"""

import pytest
import asyncio
from src.cache_manager import RetryManager


@pytest.fixture
def retry_manager():
    """Fixture para RetryManager"""
    return RetryManager(max_retries=3, base_delay=0.1, max_delay=1.0)


@pytest.mark.asyncio
async def test_retry_success_first_attempt(retry_manager):
    """Testa sucesso na primeira tentativa"""
    async def successful_coro():
        return "sucesso"
    
    result = await retry_manager.execute_with_retry(successful_coro())
    assert result == "sucesso"


@pytest.mark.asyncio
async def test_retry_success_after_timeout(retry_manager):
    """Testa sucesso após timeout"""
    attempt_count = 0
    
    async def timeout_then_success():
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 2:
            raise asyncio.TimeoutError()
        
        return "sucesso"
    
    # Usar lambda para criar coroutine a cada tentativa
    result = await retry_manager.execute_with_retry(lambda: timeout_then_success())
    assert result == "sucesso"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_max_attempts_exceeded(retry_manager):
    """Testa que exceção é lançada após max_retries"""
    async def always_fails():
        raise asyncio.TimeoutError("Sempre falha")
    
    with pytest.raises(asyncio.TimeoutError):
        await retry_manager.execute_with_retry(lambda: always_fails())


@pytest.mark.asyncio
async def test_retry_exponential_backoff(retry_manager):
    """Testa exponential backoff"""
    # Calcular delays
    delays = []
    for attempt in range(3):
        delay = retry_manager._calculate_backoff(attempt)
        delays.append(delay)
    
    # Cada delay deve ser maior que o anterior (com tolerância para jitter)
    assert delays[0] < delays[1]
    assert delays[1] < delays[2]
    
    # Não deve exceder max_delay
    for delay in delays:
        assert delay <= retry_manager.max_delay


@pytest.mark.asyncio
async def test_retry_with_error_code_429(retry_manager):
    """Testa retry com erro 429 (rate limit)"""
    attempt_count = 0
    
    async def rate_limited():
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 2:
            error = Exception("Too Many Requests")
            error.code = 429
            raise error
        
        return "sucesso"
    
    result = await retry_manager.execute_with_retry(lambda: rate_limited(), error_codes=(429,))
    assert result == "sucesso"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_with_error_code_500(retry_manager):
    """Testa retry com erro 500 (server error)"""
    attempt_count = 0
    
    async def server_error():
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 2:
            error = Exception("Internal Server Error")
            error.code = 500
            raise error
        
        return "sucesso"
    
    result = await retry_manager.execute_with_retry(lambda: server_error(), error_codes=(500,))
    assert result == "sucesso"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_no_retry_for_other_errors(retry_manager):
    """Testa que outros erros não disparam retry"""
    attempt_count = 0
    
    async def other_error():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("Erro que não merece retry")
    
    with pytest.raises(ValueError):
        await retry_manager.execute_with_retry(other_error(), error_codes=(429, 500))
    
    # Deve ter tentado apenas uma vez
    assert attempt_count == 1


@pytest.mark.asyncio
async def test_retry_stats(retry_manager):
    """Testa estatísticas do retry manager"""
    stats = await retry_manager.get_stats()
    
    assert stats["max_retries"] == 3
    assert stats["base_delay"] == 0.1
    assert stats["max_delay"] == 1.0


@pytest.mark.asyncio
async def test_retry_jitter(retry_manager):
    """Testa que jitter é aplicado"""
    # Calcular múltiplos delays para verificar variação
    delays = []
    for _ in range(10):
        delay = retry_manager._calculate_backoff(1)
        delays.append(delay)
    
    # Deve haver variação (não todos iguais)
    assert len(set(delays)) > 1
    
    # Todos devem estar no intervalo válido
    for delay in delays:
        assert retry_manager.base_delay <= delay <= retry_manager.max_delay
