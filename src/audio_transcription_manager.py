"""
Gerenciador de Transcrição de Áudio
Converte arquivos de áudio em texto
"""

import logging
import aiohttp
import asyncio
import os
from typing import Optional

logger = logging.getLogger(__name__)

class AudioTranscriptionManager:
    """Gerencia transcrição de áudio"""
    
    def __init__(self, groq_api_key: str = None):
        """Inicializa o gerenciador de transcrição"""
        self.groq_api_key = groq_api_key
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("AudioTranscriptionManager inicializado")
    
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
    
    async def transcribe_from_file(self, file_path: str) -> str:
        """
        Transcreve áudio de um arquivo local
        
        file_path: Caminho do arquivo de áudio
        """
        if not os.path.exists(file_path):
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return "Erro: Arquivo não encontrado"
        
        try:
            await self.init_session()
            
            # Usar Groq API para transcrição
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            
            with open(file_path, "rb") as audio_file:
                data = aiohttp.FormData()
                data.add_field("file", audio_file, filename=os.path.basename(file_path))
                data.add_field("model", "whisper-large-v3-turbo")
                data.add_field("language", "pt")  # Português
                
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}"
                }
                
                async with self.session.post(
                    url, 
                    data=data, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.warning(f"Erro na transcrição: {resp.status} - {error_text}")
                        return f"Erro {resp.status}: Falha ao transcrever"
                    
                    result = await resp.json()
                    text = result.get("text", "")
                    
                    if not text:
                        return "Nenhum áudio detectado no arquivo"
                    
                    logger.info(f"Áudio transcrito com sucesso: {len(text)} caracteres")
                    return text
        
        except asyncio.TimeoutError:
            logger.warning("Timeout na transcrição")
            return "Timeout: Transcrição demorou muito"
        except Exception as e:
            logger.exception(f"Erro ao transcrever: {e}")
            return f"Erro ao transcrever: {str(e)}"
    
    async def transcribe_from_url(self, audio_url: str) -> str:
        """
        Transcreve áudio de uma URL
        
        audio_url: URL do arquivo de áudio
        """
        try:
            await self.init_session()
            
            # Baixar arquivo temporário
            temp_file = "/tmp/audio_temp.ogg"
            
            async with self.session.get(audio_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    logger.warning(f"Erro ao baixar áudio: {resp.status}")
                    return "Erro ao baixar arquivo de áudio"
                
                with open(temp_file, "wb") as f:
                    f.write(await resp.read())
            
            # Transcrever arquivo baixado
            result = await self.transcribe_from_file(temp_file)
            
            # Limpar arquivo temporário
            try:
                os.remove(temp_file)
            except:
                pass
            
            return result
        
        except Exception as e:
            logger.exception(f"Erro ao transcrever URL: {e}")
            return f"Erro ao transcrever: {str(e)}"
    
    def format_transcription(self, text: str) -> str:
        """Formata texto transcrito para exibição"""
        return f"🎙️ Transcrição:\n\n{text}"
