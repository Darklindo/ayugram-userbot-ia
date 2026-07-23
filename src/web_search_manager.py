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
    
    def __init__(self, brave_api_key: str = None):
        """
        Inicializa o gerenciador de busca
        
        brave_api_key: Chave da API Brave Search (opcional)
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.brave_api_key = brave_api_key
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
    
    async def search_brave(self, query: str, max_results: int = 3) -> str:
        """
        Busca usando Brave Search API
        
        query: Termo de busca
        max_results: Número máximo de resultados
        """
        if not self.brave_api_key:
            logger.warning("Brave API key não configurada, usando fallback")
            return await self.search_duckduckgo(query, max_results)
        
        await self.init_session()
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            params = {
                "q": query,
                "count": max_results
            }
            
            async with self.session.get(url, headers=headers, params=params, 
                                       timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning(f"Erro na busca Brave: status {resp.status}")
                    return await self.search_duckduckgo(query, max_results)
                
                data = await resp.json()
                results = []
                
                # Processar resultados
                if data.get("web", {}).get("results"):
                    for result in data["web"]["results"][:max_results]:
                        title = result.get("title", "")
                        description = result.get("description", "")
                        url = result.get("url", "")
                        
                        if title and description:
                            results.append(f"📌 {title}\n{description}\n🔗 {url}")
                
                if not results:
                    return f"Nenhum resultado encontrado para: {query}"
                
                return "\n\n".join(results)
        
        except asyncio.TimeoutError:
            logger.warning("Timeout na busca Brave")
            return await self.search_duckduckgo(query, max_results)
        except Exception as e:
            logger.exception(f"Erro ao buscar com Brave: {e}")
            return await self.search_duckduckgo(query, max_results)
    
    async def search_duckduckgo(self, query: str, max_results: int = 3) -> str:
        """
        Busca usando DuckDuckGo (fallback)
        
        query: Termo de busca
        max_results: Número máximo de resultados
        """
        await self.init_session()
        
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": 1
            }
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status not in (200, 202):
                    logger.warning(f"Erro na busca DuckDuckGo: status {resp.status}")
                    return "Erro ao buscar informações"
                
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
            logger.warning("Timeout na busca DuckDuckGo")
            return "Timeout: Busca demorou muito"
        except Exception as e:
            logger.exception(f"Erro ao buscar na web: {e}")
            return f"Erro ao buscar: {str(e)}"
    
    async def search(self, query: str, max_results: int = 3) -> str:
        """
        Busca informações na web (tenta Brave primeiro, depois DuckDuckGo)
        
        query: Termo de busca
        max_results: Número máximo de resultados
        """
        if self.brave_api_key:
            return await self.search_brave(query, max_results)
        else:
            return await self.search_duckduckgo(query, max_results)
    
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
