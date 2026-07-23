"""
Utilitarios do bot
"""

import logging
from telethon.errors import FloodWaitError

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096

def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
    """
    Divide uma mensagem longa em multiplas partes
    
    Tenta quebrar em paragrafos para manter legibilidade
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = ""
    
    paragraphs = text.split("\n\n")
    
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_length:
            if current:
                current += "\n\n"
            current += para
        else:
            if current:
                parts.append(current)
            current = para
    
    if current:
        parts.append(current)
    
    # Se ainda houver partes muito longas, quebra por linhas
    final_parts = []
    for part in parts:
        if len(part) <= max_length:
            final_parts.append(part)
        else:
            lines = part.split("\n")
            current_part = ""
            for line in lines:
                if len(current_part) + len(line) + 1 <= max_length:
                    if current_part:
                        current_part += "\n"
                    current_part += line
                else:
                    if current_part:
                        final_parts.append(current_part)
                    current_part = line
            if current_part:
                final_parts.append(current_part)
    
    return final_parts if final_parts else [text[:max_length]]

async def send_long_message(event, text: str):
    """
    Envia uma mensagem longa, dividindo se necessario
    """
    parts = split_message(text)
    
    if len(parts) == 1:
        await event.reply(parts[0])
    else:
        for i, part in enumerate(parts):
            try:
                await event.reply(f"{part}\n\n[Parte {i+1}/{len(parts)}]")
            except FloodWaitError as e:
                logger.warning(f"FloodWait ao enviar parte {i+1}: aguardando {e.seconds}s")
                import asyncio
                await asyncio.sleep(e.seconds)
                await event.reply(f"{part}\n\n[Parte {i+1}/{len(parts)}]")
            except Exception as e:
                logger.exception(f"Erro ao enviar parte {i+1}")
                raise

async def edit_long_message(msg, text: str):
    """
    Edita uma mensagem longa, dividindo se necessario
    """
    parts = split_message(text)
    
    if len(parts) == 1:
        try:
            await msg.edit(parts[0])
        except FloodWaitError as e:
            logger.warning(f"FloodWait ao editar mensagem: aguardando {e.seconds}s")
            import asyncio
            await asyncio.sleep(e.seconds)
            await msg.edit(parts[0])
    else:
        # Se houver multiplas partes, edita a primeira e envia as demais
        try:
            await msg.edit(f"{parts[0]}\n\n[Parte 1/{len(parts)}]")
        except FloodWaitError as e:
            logger.warning(f"FloodWait ao editar primeira parte: aguardando {e.seconds}s")
            import asyncio
            await asyncio.sleep(e.seconds)
            await msg.edit(f"{parts[0]}\n\n[Parte 1/{len(parts)}]")
        
        # Enviar partes restantes
        for i in range(1, len(parts)):
            try:
                await msg.respond(f"{parts[i]}\n\n[Parte {i+1}/{len(parts)}]")
            except FloodWaitError as e:
                logger.warning(f"FloodWait ao enviar parte {i+1}: aguardando {e.seconds}s")
                import asyncio
                await asyncio.sleep(e.seconds)
                await msg.respond(f"{parts[i]}\n\n[Parte {i+1}/{len(parts)}]")
            except Exception as e:
                logger.exception(f"Erro ao enviar parte {i+1}")
