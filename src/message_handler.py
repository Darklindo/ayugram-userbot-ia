"""
Gerenciador de Mensagens com Tratamento Robusto
Lida com edição, envio e validação de mensagens
"""

import logging
from telethon.errors import MessageNotModifiedError, MessageDeletedError, ChatSendInlineNotAllowedError
from telethon.tl.types import TypeMessageMedia
import asyncio

logger = logging.getLogger(__name__)


class MessageHandler:
    """Gerencia operações com mensagens de forma robusta"""
    
    @staticmethod
    async def get_reply_text(reply_to_msg) -> str:
        """
        Extrai texto de uma mensagem de resposta com segurança
        Lida com mídias, stickers, documentos, etc.
        """
        if not reply_to_msg:
            return ""
        
        try:
            # Tentar obter texto direto
            if hasattr(reply_to_msg, 'text') and reply_to_msg.text:
                return reply_to_msg.text.strip()
            
            # Se for mídia, tentar obter caption
            if hasattr(reply_to_msg, 'media') and reply_to_msg.media:
                if hasattr(reply_to_msg, 'caption') and reply_to_msg.caption:
                    return reply_to_msg.caption.strip()
            
            # Se for documento, tentar obter nome do arquivo
            if hasattr(reply_to_msg, 'document') and reply_to_msg.document:
                if hasattr(reply_to_msg.document, 'attributes'):
                    for attr in reply_to_msg.document.attributes:
                        if hasattr(attr, 'file_name'):
                            return f"[Documento: {attr.file_name}]"
            
            # Se for sticker, retornar indicador
            if hasattr(reply_to_msg, 'sticker') and reply_to_msg.sticker:
                return "[Sticker]"
            
            # Se for áudio, retornar indicador
            if hasattr(reply_to_msg, 'audio') and reply_to_msg.audio:
                return "[Áudio]"
            
            # Se for vídeo, retornar indicador
            if hasattr(reply_to_msg, 'video') and reply_to_msg.video:
                return "[Vídeo]"
            
            # Se for foto, retornar indicador
            if hasattr(reply_to_msg, 'photo') and reply_to_msg.photo:
                return "[Foto]"
            
            logger.warning("Mensagem de resposta sem texto identificável")
            return "[Mensagem sem texto]"
        
        except Exception as e:
            logger.exception(f"Erro ao extrair texto da resposta: {e}")
            return "[Erro ao extrair texto]"
    
    @staticmethod
    async def safe_edit_message(msg, text: str, max_retries: int = 3) -> bool:
        """
        Edita mensagem com tratamento robusto de erros
        Retorna True se sucesso, False se falha
        """
        if not msg:
            return False
        
        for attempt in range(max_retries):
            try:
                await msg.edit(text)
                logger.debug(f"Mensagem editada com sucesso (tentativa {attempt + 1})")
                return True
            
            except MessageNotModifiedError:
                logger.warning("Mensagem não foi modificada (conteúdo idêntico)")
                return True  # Não é erro, apenas não modificou
            
            except MessageDeletedError:
                logger.warning("Mensagem foi deletada, não é possível editar")
                return False
            
            except ChatSendInlineNotAllowedError:
                logger.warning("Chat não permite envio de mensagens inline")
                return False
            
            except Exception as e:
                logger.warning(f"Erro ao editar mensagem (tentativa {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    # Aguardar com backoff exponencial antes de tentar novamente
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Falha ao editar mensagem após {max_retries} tentativas")
                    return False
        
        return False
    
    @staticmethod
    async def safe_send_message(event, text: str, reply_to: int = None) -> bool:
        """
        Envia mensagem com tratamento robusto de erros
        Retorna True se sucesso, False se falha
        """
        try:
            await event.respond(text, reply_to=reply_to)
            logger.debug("Mensagem enviada com sucesso")
            return True
        
        except ChatSendInlineNotAllowedError:
            logger.warning("Chat não permite envio de mensagens")
            return False
        
        except Exception as e:
            logger.exception(f"Erro ao enviar mensagem: {e}")
            return False
    
    @staticmethod
    async def edit_or_send(msg, event, text: str) -> bool:
        """
        Tenta editar mensagem existente, se falhar, envia nova
        Útil para fallback quando edit falha
        """
        # Tentar editar
        if await MessageHandler.safe_edit_message(msg, text):
            return True
        
        # Se editar falhar, enviar nova mensagem
        logger.info("Edição falhou, enviando nova mensagem")
        return await MessageHandler.safe_send_message(event, text)


async def validate_and_extract_context(reply_to_msg) -> dict:
    """
    Valida e extrai contexto de mensagem de resposta
    Retorna dict com contexto seguro
    """
    context = {
        "text": "",
        "has_media": False,
        "media_type": None,
        "is_valid": False
    }
    
    try:
        # Extrair texto
        text = await MessageHandler.get_reply_text(reply_to_msg)
        context["text"] = text
        
        # Verificar se tem mídia
        if hasattr(reply_to_msg, 'media') and reply_to_msg.media:
            context["has_media"] = True
            
            # Identificar tipo de mídia
            if hasattr(reply_to_msg, 'photo'):
                context["media_type"] = "photo"
            elif hasattr(reply_to_msg, 'video'):
                context["media_type"] = "video"
            elif hasattr(reply_to_msg, 'audio'):
                context["media_type"] = "audio"
            elif hasattr(reply_to_msg, 'document'):
                context["media_type"] = "document"
            elif hasattr(reply_to_msg, 'sticker'):
                context["media_type"] = "sticker"
        
        context["is_valid"] = True
        return context
    
    except Exception as e:
        logger.exception(f"Erro ao validar contexto: {e}")
        context["is_valid"] = False
        return context
