"""
Provider Groq - Muito rápido e gratuito
"""

import aiohttp
import asyncio
import logging
from .base import IAProvider

logger = logging.getLogger(__name__)

class GroqProvider(IAProvider):
    """Provider para Groq API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-20b"  # Modelo atual e gratuito
    
    async def init_session(self):
        """Inicializa sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("Groq: Sessao inicializada")
    
    async def close_session(self):
        """Fecha sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Groq: Sessao fechada")
    
    async def process(self, prompt: str) -> str:
        """Processa uma pergunta via Groq"""
        if not self.session:
            await self.init_session()
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Groq: Enviando pergunta com modelo {self.model}")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.info(f"Groq: Status {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        if response:
                            logger.info("Groq: Resposta recebida com sucesso")
                            return response
                        else:
                            return "Erro: Resposta vazia do Groq"
                    
                    except Exception as e:
                        logger.exception("Erro ao decodificar resposta do Groq")
                        return f"Erro ao processar resposta: {str(e)}"
                
                elif resp.status == 401:
                    return "Erro: Chave de API do Groq inválida"
                
                elif resp.status == 429:
                    return "Erro: Limite de requisições do Groq atingido. Tente mais tarde."
                
                elif resp.status == 500:
                    return "Erro: Servidor do Groq indisponível"
                
                else:
                    text = await resp.text()
                    logger.error(f"Groq: Status {resp.status} - {text}")
                    return f"Erro {resp.status}: Falha ao processar no Groq"
        
        except asyncio.TimeoutError:
            logger.warning("Groq: Timeout na requisição")
            return "Erro: Timeout ao conectar com Groq"
        
        except Exception as e:
            logger.exception("Erro ao processar com Groq")
            return f"Erro ao processar: {str(e)}"
