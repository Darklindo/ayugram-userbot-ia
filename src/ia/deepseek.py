"""
Provedor DeepSeek
"""

import asyncio
import aiohttp
import logging
from typing import Optional
from .base import IAProvider

logger = logging.getLogger(__name__)

class DeepSeekProvider(IAProvider):
    """Implementacao do DeepSeek"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._validate_api_key()
        self.api_url = "https://api.deepseek.com/chat/completions"
    
    async def init_session(self):
        """Inicializa sessao aiohttp"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            logger.info("DeepSeek: Sessao inicializada")
    
    async def close_session(self):
        """Fecha sessao aiohttp"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("DeepSeek: Sessao fechada")
    
    async def process(self, prompt: str) -> str:
        """Processa pergunta com DeepSeek"""
        if not self.session:
            await self.init_session()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            logger.info(f"DeepSeek: Enviando pergunta")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.info(f"DeepSeek: Status {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        result = data.get("choices", [{}])[0].get("message", {}).get("content", "Sem resposta")
                        if not result or not isinstance(result, str):
                            logger.warning("DeepSeek: Resposta invalida")
                            return "Erro: Resposta invalida"
                        return result.strip()
                    except Exception as e:
                        logger.exception("DeepSeek: Erro ao decodificar resposta")
                        return "Erro: Resposta invalida"
                
                elif resp.status == 429:
                    logger.warning("DeepSeek: Rate limit (429)")
                    return "Limite de requisicoes DeepSeek atingido. Tente mais tarde."
                
                elif resp.status == 401:
                    logger.error("DeepSeek: Chave invalida (401)")
                    return "Erro: Chave DeepSeek invalida"
                
                elif resp.status == 500:
                    logger.warning("DeepSeek: Erro interno (500)")
                    return "Servidor DeepSeek indisponivel. Tente mais tarde."
                
                else:
                    text = await resp.text()
                    logger.error(f"DeepSeek: Erro {resp.status}: {text[:100]}")
                    return f"Erro DeepSeek {resp.status}"
        
        except asyncio.TimeoutError:
            logger.exception("DeepSeek: Timeout")
            return "Timeout DeepSeek: Requisicao muito lenta"
        
        except aiohttp.ClientError as e:
            logger.exception("DeepSeek: Erro de conexao")
            return "Erro de conexao com DeepSeek"
        
        except Exception as e:
            logger.exception("DeepSeek: Erro inesperado")
            return "Erro ao processar com DeepSeek"
