"""
Provider OpenRouter - Acesso a múltiplos modelos
"""

import aiohttp
import logging
from .base import IAProvider

logger = logging.getLogger(__name__)

class OpenRouterProvider(IAProvider):
    """Provider para OpenRouter API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-70b-instruct:free"  # Modelo gratuito melhor
    
    async def init_session(self):
        """Inicializa sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("OpenRouter: Sessao inicializada")
    
    async def close_session(self):
        """Fecha sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("OpenRouter: Sessao fechada")
    
    async def process(self, prompt: str) -> str:
        """Processa uma pergunta via OpenRouter"""
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
                "HTTP-Referer": "https://github.com/Darklindo/ayugram-userbot-ia",
                "X-Title": "JT IA Bot"
            }
            
            logger.info(f"OpenRouter: Enviando pergunta com modelo {self.model}")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                logger.info(f"OpenRouter: Status {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        if response:
                            logger.info("OpenRouter: Resposta recebida com sucesso")
                            return response
                        else:
                            return "Erro: Resposta vazia do OpenRouter"
                    
                    except Exception as e:
                        logger.exception("Erro ao decodificar resposta do OpenRouter")
                        return f"Erro ao processar resposta: {str(e)}"
                
                elif resp.status == 401:
                    return "Erro: Chave de API do OpenRouter inválida"
                
                elif resp.status == 429:
                    return "Erro: Limite de requisições do OpenRouter atingido. Tente mais tarde."
                
                elif resp.status == 500:
                    return "Erro: Servidor do OpenRouter indisponível"
                
                else:
                    text = await resp.text()
                    logger.error(f"OpenRouter: Status {resp.status} - {text}")
                    return f"Erro {resp.status}: Falha ao processar no OpenRouter"
        
        except asyncio.TimeoutError:
            logger.warning("OpenRouter: Timeout na requisição")
            return "Erro: Timeout ao conectar com OpenRouter"
        
        except Exception as e:
            logger.exception("Erro ao processar com OpenRouter")
            return f"Erro ao processar: {str(e)}"

import asyncio
