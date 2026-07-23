"""
Configuração de testes
"""

import sys
import os

# Adicionar src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Fixture para event loop"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
