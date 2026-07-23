"""
Gerenciador de IA com suporte a multiplas APIs
"""

import asyncio
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class IAManager:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def init_session(self):
        """Inicializa a sessao aiohttp (reutilizavel)"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            logger.info("Sessao aiohttp inicializada")
    
    async def close_session(self):
        """Fecha a sessao aiohttp"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Sessao aiohttp fechada")
    
    async def process(self, prompt: str) -> str:
        """Processa pergunta com IA com tratamento robusto de erros"""
        if not self.api_key:
            return "Erro: API key nao configurada"
        
        if not self.session:
            await self.init_session()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "model": "gpt-4",
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with self.session.post(
                f"{self.api_url}/v1/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        result = data.get("choices", [{}])[0].get("text", "Sem resposta")
                        if not result or not isinstance(result, str):
                            logger.warning("Resposta invalida da API")
                            return "Erro: Resposta invalida"
                        return result.strip()
                    except Exception as e:
                        logger.exception("Erro ao decodificar resposta JSON")
                        return "Erro: Resposta invalida"
                
                elif resp.status == 429:
                    logger.warning("Rate limit atingido (429)")
                    return "Limite de requisicoes atingido. Tente mais tarde."
                
                elif resp.status == 500:
                    logger.warning("Erro interno da API (500)")
                    return "Servidor da IA indisponivel. Tente mais tarde."
                
                else:
                    logger.warning(f"API retornou status {resp.status}")
                    return f"Erro {resp.status}: Nao consegui processar"
        
        except asyncio.TimeoutError:
            logger.exception("Timeout na requisicao")
            return "Timeout: Requisicao muito lenta. Tente novamente."
        
        except aiohttp.ClientError as e:
            logger.exception("Erro de conexao")
            return "Erro de conexao com a IA"
        
        except Exception as e:
            logger.exception("Erro inesperado no processamento")
            return "Erro ao processar sua pergunta"
