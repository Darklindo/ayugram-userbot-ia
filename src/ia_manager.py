"""
Gerenciador de IA com suporte a DeepSeek e Google Gemini
"""

import asyncio
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class IAManager:
    def __init__(self, provider: str, api_key: str):
        """
        provider: 'deepseek' ou 'gemini'
        api_key: Chave da API
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
        if self.provider == "deepseek":
            self.api_url = "https://api.deepseek.com/chat/completions"
        elif self.provider == "gemini":
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        else:
            raise ValueError(f"Provider desconhecido: {provider}")
        
        logger.info(f"IAManager inicializado com provider: {self.provider}")
    
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
    
    async def _process_deepseek(self, prompt: str) -> str:
        """Processa com DeepSeek API"""
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
            
            logger.info(f"Enviando para DeepSeek: {self.api_url}")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.info(f"DeepSeek respondeu com status: {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        result = data.get("choices", [{}])[0].get("message", {}).get("content", "Sem resposta")
                        if not result or not isinstance(result, str):
                            logger.warning("Resposta invalida do DeepSeek")
                            return "Erro: Resposta invalida"
                        return result.strip()
                    except Exception as e:
                        logger.exception("Erro ao decodificar resposta DeepSeek")
                        text = await resp.text()
                        logger.error(f"Resposta bruta: {text}")
                        return "Erro: Resposta invalida"
                
                elif resp.status == 429:
                    logger.warning("Rate limit DeepSeek (429)")
                    return "Limite de requisicoes atingido. Tente mais tarde."
                
                elif resp.status == 401:
                    logger.error("Chave DeepSeek invalida (401)")
                    return "Erro: Chave de API invalida"
                
                elif resp.status == 500:
                    logger.warning("Erro interno DeepSeek (500)")
                    return "Servidor DeepSeek indisponivel. Tente mais tarde."
                
                else:
                    text = await resp.text()
                    logger.error(f"DeepSeek erro {resp.status}: {text}")
                    return f"Erro {resp.status}: {text[:100]}"
        
        except asyncio.TimeoutError:
            logger.exception("Timeout na requisicao DeepSeek")
            return "Timeout: Requisicao muito lenta. Tente novamente."
        
        except aiohttp.ClientError as e:
            logger.exception("Erro de conexao com DeepSeek")
            return "Erro de conexao com a IA"
        
        except Exception as e:
            logger.exception("Erro inesperado no DeepSeek")
            return "Erro ao processar sua pergunta"
    
    async def _process_gemini(self, prompt: str) -> str:
        """Processa com Google Gemini API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
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
            
            logger.info(f"Enviando para Gemini: {self.api_url}")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.info(f"Gemini respondeu com status: {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sem resposta")
                        if not result or not isinstance(result, str):
                            logger.warning("Resposta invalida do Gemini")
                            return "Erro: Resposta invalida"
                        return result.strip()
                    except Exception as e:
                        logger.exception("Erro ao decodificar resposta Gemini")
                        text = await resp.text()
                        logger.error(f"Resposta bruta: {text}")
                        return "Erro: Resposta invalida"
                
                elif resp.status == 429:
                    logger.warning("Rate limit Gemini (429)")
                    return "Limite de requisicoes atingido. Tente mais tarde."
                
                elif resp.status == 401:
                    logger.error("Chave Gemini invalida (401)")
                    return "Erro: Chave de API invalida"
                
                elif resp.status == 500:
                    logger.warning("Erro interno Gemini (500)")
                    return "Servidor Gemini indisponivel. Tente mais tarde."
                
                else:
                    text = await resp.text()
                    logger.error(f"Gemini erro {resp.status}: {text}")
                    return f"Erro {resp.status}: {text[:100]}"
        
        except asyncio.TimeoutError:
            logger.exception("Timeout na requisicao Gemini")
            return "Timeout: Requisicao muito lenta. Tente novamente."
        
        except aiohttp.ClientError as e:
            logger.exception("Erro de conexao com Gemini")
            return "Erro de conexao com a IA"
        
        except Exception as e:
            logger.exception("Erro inesperado no Gemini")
            return "Erro ao processar sua pergunta"
    
    async def process(self, prompt: str) -> str:
        """Processa pergunta com IA (DeepSeek ou Gemini)"""
        if not self.api_key:
            return "Erro: API key nao configurada"
        
        if not self.session:
            await self.init_session()
        
        if self.provider == "deepseek":
            return await self._process_deepseek(prompt)
        elif self.provider == "gemini":
            return await self._process_gemini(prompt)
        else:
            return f"Erro: Provider desconhecido: {self.provider}"
