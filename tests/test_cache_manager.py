"""
Testes para CacheManager
"""

import pytest
import asyncio
from src.cache_manager import CacheManager


@pytest.fixture
def cache_manager():
    """Fixture para CacheManager"""
    return CacheManager(ttl_minutes=1, max_cache_size=10)


@pytest.mark.asyncio
async def test_cache_set_and_get(cache_manager):
    """Testa armazenar e recuperar do cache"""
    prompt = "Qual é a capital do Brasil?"
    response = "Brasília"
    
    # Armazenar
    await cache_manager.set(prompt, response)
    
    # Recuperar
    cached = await cache_manager.get(prompt)
    assert cached == response


@pytest.mark.asyncio
async def test_cache_miss(cache_manager):
    """Testa cache miss (prompt não existe)"""
    prompt = "Pergunta que não existe"
    cached = await cache_manager.get(prompt)
    assert cached is None


@pytest.mark.asyncio
async def test_cache_expiration(cache_manager):
    """Testa expiração do cache (TTL)"""
    # Criar cache com TTL muito curto
    short_ttl_cache = CacheManager(ttl_minutes=0, max_cache_size=10)
    
    prompt = "Pergunta"
    response = "Resposta"
    
    await short_ttl_cache.set(prompt, response)
    
    # Aguardar um pouco
    await asyncio.sleep(0.1)
    
    # Deve estar expirado
    cached = await short_ttl_cache.get(prompt)
    assert cached is None


@pytest.mark.asyncio
async def test_cache_hits_counter(cache_manager):
    """Testa contador de hits"""
    prompt = "Pergunta"
    response = "Resposta"
    
    await cache_manager.set(prompt, response)
    
    # Primeiro acesso
    await cache_manager.get(prompt)
    
    # Segundo acesso
    await cache_manager.get(prompt)
    
    # Verificar stats
    stats = await cache_manager.get_stats()
    assert stats["total_hits"] == 2


@pytest.mark.asyncio
async def test_cache_lru_cleanup(cache_manager):
    """Testa limpeza LRU quando cache fica cheio"""
    # Preencher cache até o limite
    for i in range(10):
        await cache_manager.set(f"prompt_{i}", f"response_{i}")
    
    # Adicionar mais um (deve disparar LRU cleanup)
    await cache_manager.set("prompt_11", "response_11")
    
    stats = await cache_manager.get_stats()
    # Deve ter removido alguns itens
    assert stats["valid_items"] <= 10


@pytest.mark.asyncio
async def test_cache_clear(cache_manager):
    """Testa limpeza completa do cache"""
    await cache_manager.set("prompt_1", "response_1")
    await cache_manager.set("prompt_2", "response_2")
    
    await cache_manager.clear()
    
    stats = await cache_manager.get_stats()
    assert stats["valid_items"] == 0


@pytest.mark.asyncio
async def test_hash_prompt_consistency(cache_manager):
    """Testa consistência do hash de prompts"""
    prompt = "Pergunta importante"
    
    hash1 = CacheManager.hash_prompt(prompt)
    hash2 = CacheManager.hash_prompt(prompt)
    
    assert hash1 == hash2


@pytest.mark.asyncio
async def test_cache_thread_safety(cache_manager):
    """Testa thread-safety do cache"""
    prompt = "Pergunta"
    response = "Resposta"
    
    # Executar múltiplas operações concorrentes
    tasks = []
    for i in range(10):
        if i % 2 == 0:
            tasks.append(cache_manager.set(f"{prompt}_{i}", f"{response}_{i}"))
        else:
            tasks.append(cache_manager.get(f"{prompt}_{i-1}"))
    
    # Não deve lançar exceção
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verificar que não houve erros
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 0
