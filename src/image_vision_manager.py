"""
Gerenciador de Visão de Imagens
Analisa e descreve imagens usando Vision API
"""

import logging
import aiohttp
import asyncio
import base64
import os
from typing import Optional

logger = logging.getLogger(__name__)

class ImageVisionManager:
    """Gerencia análise de imagens com Vision"""
    
    def __init__(self, groq_api_key: str = None, openrouter_api_key: str = None):
        """Inicializa o gerenciador de visão"""
        self.groq_api_key = groq_api_key
        self.openrouter_api_key = openrouter_api_key
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("ImageVisionManager inicializado")
    
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
    
    async def analyze_image_from_file(self, file_path: str, prompt: str = "Descreva esta imagem em detalhes") -> str:
        """
        Analisa imagem de um arquivo local
        
        file_path: Caminho do arquivo de imagem
        prompt: Pergunta/instrução para a IA
        """
        if not os.path.exists(file_path):
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return "Erro: Arquivo não encontrado"
        
        try:
            # Ler e codificar imagem em base64
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Detectar tipo de imagem
            ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }
            mime_type = mime_types.get(ext, "image/jpeg")
            
            # Usar OpenRouter para análise de imagem
            return await self._analyze_with_openrouter(image_data, mime_type, prompt)
        
        except Exception as e:
            logger.exception(f"Erro ao analisar imagem: {e}")
            return f"Erro ao analisar imagem: {str(e)}"
    
    async def analyze_image_from_url(self, image_url: str, prompt: str = "Descreva esta imagem em detalhes") -> str:
        """
        Analisa imagem de uma URL
        
        image_url: URL da imagem
        prompt: Pergunta/instrução para a IA
        """
        try:
            await self.init_session()
            
            # Baixar imagem
            async with self.session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    logger.warning(f"Erro ao baixar imagem: {resp.status}")
                    return "Erro ao baixar imagem"
                
                image_data = base64.b64encode(await resp.read()).decode("utf-8")
            
            # Detectar tipo de imagem pela URL
            mime_type = "image/jpeg"
            if ".png" in image_url:
                mime_type = "image/png"
            elif ".gif" in image_url:
                mime_type = "image/gif"
            elif ".webp" in image_url:
                mime_type = "image/webp"
            
            return await self._analyze_with_openrouter(image_data, mime_type, prompt)
        
        except Exception as e:
            logger.exception(f"Erro ao analisar URL: {e}")
            return f"Erro ao analisar imagem: {str(e)}"
    
    async def _analyze_with_openrouter(self, image_data: str, mime_type: str, prompt: str) -> str:
        """Analisa imagem usando OpenRouter Vision"""
        try:
            await self.init_session()
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            payload = {
                "model": "google/gemini-2-flash-exp:free",  # Modelo com visão gratuito
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.warning(f"Erro na análise: {resp.status} - {error_text}")
                    return f"Erro {resp.status}: Falha ao analisar imagem"
                
                result = await resp.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not text:
                    return "Nenhuma análise disponível"
                
                logger.info(f"Imagem analisada com sucesso")
                return text
        
        except asyncio.TimeoutError:
            logger.warning("Timeout na análise de imagem")
            return "Timeout: Análise demorou muito"
        except Exception as e:
            logger.exception(f"Erro ao analisar com OpenRouter: {e}")
            return f"Erro ao analisar: {str(e)}"
    
    def format_analysis(self, text: str) -> str:
        """Formata análise de imagem para exibição"""
        return f"🖼️ Análise da imagem:\n\n{text}"
