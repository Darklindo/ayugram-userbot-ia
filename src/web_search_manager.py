"""
Gerenciador de Busca na Web
Permite buscar informações atuais na internet
"""

import logging
import aiohttp
import asyncio
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class WebSearchManager:
    """Gerencia buscas na web"""
    
    def __init__(self):
        """Inicializa o gerenciador de busca"""
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("WebSearchManager inicializado")
    
    async def init_session(self):
        """Inicializa a sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.debug("Sessão HTTP criada")
    
    async def close_session(self):
        """Fecha a sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("Sessão HTTP fechada")
    
    async def search(self, query: str, max_results: int = 3) -> str:
        """
        Busca informações na web usando DuckDuckGo
        
        query: Termo de busca
        max_results: Número máximo de resultados
        """
        await self.init_session()
        
        try:
            # Usar DuckDuckGo API (sem chave necessária)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": 1
            }
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status not in (200, 202):
                    logger.warning(f"Erro na busca: status {resp.status}")
                    return "Erro ao buscar informações"
                
                # DuckDuckGo retorna application/x-javascript, nao application/json
                # Use content_type=None para ignorar a validacao do MIME Type
                try:
                    data = await resp.json(content_type=None)
                except Exception as e:
                    logger.exception(f"Erro ao fazer parse JSON: {e}")
                    return "Erro ao processar resposta da busca"
                
                # Extrair resultados
                results = []
                
                # Abstract (resumo principal)
                if data.get("AbstractText"):
                    results.append(f"📌 {data['AbstractText']}")
                
                # Related Topics
                if data.get("RelatedTopics"):
                    for topic in data["RelatedTopics"][:max_results]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(f"• {topic['Text']}")
                
                if not results:
                    return f"Nenhum resultado encontrado para: {query}"
                
                return "\n".join(results[:max_results])
        
        except asyncio.TimeoutError:
            logger.warning("Timeout na busca web")
            return "Timeout: Busca demorou muito"
        except Exception as e:
            logger.exception(f"Erro ao buscar na web: {e}")
            return f"Erro ao buscar: {str(e)}"
    
    async def search_with_context(self, query: str, context: str = "") -> str:
        """
        Busca na web com contexto
        
        query: Termo de busca
        context: Contexto adicional para melhorar a busca
        """
        full_query = f"{query} {context}".strip()
        return await self.search(full_query)
    
    def format_search_result(self, result: str) -> str:
        """Formata resultado da busca para exibição"""
        return f"🔍 Resultado da busca:\n\n{result}"
