"""
Testes para SecurityManager
"""

import pytest
import asyncio
from src.security import SecurityManager


@pytest.fixture
def security_manager():
    """Fixture para SecurityManager"""
    return SecurityManager(max_prompt_length=100, max_requests_per_minute=5)


def test_hash_user_id():
    """Testa hash de user_id"""
    user_id = 12345
    hash1 = SecurityManager.hash_user_id(user_id)
    hash2 = SecurityManager.hash_user_id(user_id)
    
    # Deve ser consistente
    assert hash1 == hash2
    
    # Deve ser diferente para IDs diferentes
    hash3 = SecurityManager.hash_user_id(54321)
    assert hash1 != hash3
    
    # Deve ter 8 caracteres
    assert len(hash1) == 8


def test_sanitize_prompt():
    """Testa sanitização de prompt"""
    # Remover caracteres de controle
    prompt = "Olá\x00\x1fMundo"
    sanitized = SecurityManager.sanitize_prompt(prompt)
    assert "\x00" not in sanitized
    assert "\x1f" not in sanitized
    
    # Normalizar espaços múltiplos
    prompt = "Olá    Mundo"
    sanitized = SecurityManager.sanitize_prompt(prompt)
    assert sanitized == "Olá Mundo"
    
    # Remover espaços nas extremidades
    prompt = "  Olá Mundo  "
    sanitized = SecurityManager.sanitize_prompt(prompt)
    assert sanitized == "Olá Mundo"


@pytest.mark.asyncio
async def test_validate_prompt_empty(security_manager):
    """Testa validação de prompt vazio"""
    valid, error = await security_manager.validate_prompt("")
    assert not valid
    assert "vazio" in error.lower()


@pytest.mark.asyncio
async def test_validate_prompt_too_long(security_manager):
    """Testa validação de prompt muito longo"""
    prompt = "A" * 200  # Maior que max_prompt_length (100)
    valid, error = await security_manager.validate_prompt(prompt)
    assert not valid
    assert "longo" in error.lower()


@pytest.mark.asyncio
async def test_validate_prompt_spam(security_manager):
    """Testa deteccao de spam"""
    # Mais de 70% do texto eh o mesmo caractere
    prompt = "AAAAAAAAAAAAAAAA"  # 16 caracteres (>10)
    valid, error = await security_manager.validate_prompt(prompt)
    assert not valid
    assert "spam" in error.lower()


@pytest.mark.asyncio
async def test_validate_prompt_valid(security_manager):
    """Testa validação de prompt válido"""
    prompt = "Qual é a capital do Brasil?"
    valid, error = await security_manager.validate_prompt(prompt)
    assert valid
    assert error == ""


@pytest.mark.asyncio
async def test_rate_limit_first_request(security_manager):
    """Testa que primeira requisição é permitida"""
    allowed, error = await security_manager.check_rate_limit(12345)
    assert allowed
    assert error == ""


@pytest.mark.asyncio
async def test_rate_limit_exceeded(security_manager):
    """Testa que limite eh respeitado"""
    user_id = 12345
    
    # Fazer 5 requisicoes (limite)
    for i in range(5):
        allowed, error = await security_manager.check_rate_limit(user_id)
        assert allowed
        # Registrar a requisicao
        await security_manager.record_request(user_id)
    
    # 6a requisicao deve ser bloqueada
    allowed, error = await security_manager.check_rate_limit(user_id)
    assert not allowed
    assert "limite" in error.lower()


@pytest.mark.asyncio
async def test_rate_limit_per_user(security_manager):
    """Testa que rate limit é por usuário"""
    # User 1 faz 5 requisições
    for i in range(5):
        await security_manager.check_rate_limit(111)
    
    # User 2 deve conseguir fazer requisições
    allowed, error = await security_manager.check_rate_limit(222)
    assert allowed


@pytest.mark.asyncio
async def test_record_request(security_manager):
    """Testa registro de requisição"""
    user_id = 12345
    
    # Registrar 3 requisições
    for i in range(3):
        await security_manager.record_request(user_id)
    
    # Verificar stats
    stats = await security_manager.get_rate_limit_stats(user_id)
    assert stats["requests_this_minute"] == 3


@pytest.mark.asyncio
async def test_clear_user_history(security_manager):
    """Testa limpeza de histórico de usuário"""
    user_id = 12345
    
    # Fazer requisições
    for i in range(3):
        await security_manager.record_request(user_id)
    
    # Limpar histórico
    await security_manager.clear_user_history(user_id)
    
    # Verificar que foi limpo
    stats = await security_manager.get_rate_limit_stats(user_id)
    assert stats["requests_this_minute"] == 0


@pytest.mark.asyncio
async def test_security_thread_safety(security_manager):
    """Testa thread-safety do security manager"""
    user_id = 12345
    
    # Executar múltiplas operações concorrentes
    tasks = []
    for i in range(10):
        tasks.append(security_manager.check_rate_limit(user_id))
        tasks.append(security_manager.record_request(user_id))
    
    # Não deve lançar exceção
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verificar que não houve erros
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 0
