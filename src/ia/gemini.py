"""
Provedor Google Gemini
"""

import asyncio
import aiohttp
import logging
from typing import Optional
from .base import IAProvider

logger = logging.getLogger(__name__)

class GeminiProvider(IAProvider):
    """Implementacao do Google Gemini"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._validate_api_key()
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    async def init_session(self):
        """Inicializa sessao aiohttp"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            logger.info("Gemini: Sessao inicializada")
    
    async def close_session(self):
        """Fecha sessao aiohttp"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Gemini: Sessao fechada")
    
    async def process(self, prompt: str) -> str:
        """Processa pergunta com Gemini"""
        if not self.session:
            await self.init_session()
        
        try:
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            logger.info(f"Gemini: Enviando pergunta")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.info(f"Gemini: Status {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sem resposta")
                        if not result or not isinstance(result, str):
                            logger.warning("Gemini: Resposta invalida")
                            return "Erro: Resposta invalida"
                        return result.strip()
                    except Exception as e:
                        logger.exception("Gemini: Erro ao decodificar resposta")
                        return "Erro: Resposta invalida"
                
                elif resp.status == 429:
                    logger.warning("Gemini: Rate limit (429)")
                    return "Limite de requisicoes Gemini atingido. Tente mais tarde."
                
                elif resp.status == 401:
                    logger.error("Gemini: Chave invalida (401)")
                    return "Erro: Chave Gemini invalida"
                
                elif resp.status == 500:
                    logger.warning("Gemini: Erro interno (500)")
                    return "Servidor Gemini indisponivel. Tente mais tarde."
                
                else:
                    text = await resp.text()
                    logger.error(f"Gemini: Erro {resp.status}: {text[:100]}")
                    return f"Erro Gemini {resp.status}"
        
        except asyncio.TimeoutError:
            logger.exception("Gemini: Timeout")
            return "Timeout Gemini: Requisicao muito lenta"
        
        except aiohttp.ClientError as e:
            logger.exception("Gemini: Erro de conexao")
            return "Erro de conexao com Gemini"
        
        except Exception as e:
            logger.exception("Gemini: Erro inesperado")
            return "Erro ao processar com Gemini"
