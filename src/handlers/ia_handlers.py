"""
Handlers de IA
Comandos: .ia, .iagroq, .iarouter, .ai
"""

import asyncio
import logging
from telethon import events
from telethon.errors import FloodWaitError

logger = logging.getLogger(__name__)


async def register_ia_handlers(client, CONFIG, perm_manager, ia_manager, 
                               cooldown_manager, history_manager, token_limiter, 
                               stats_manager, edit_long_message):
    """Registra todos os handlers de IA"""
    
    @client.on(events.NewMessage(pattern=r"^\.ia(?:\s|$)"))
    async def handle_ia(event):
        """Comando .ia [pergunta] - usa IA padrão"""
        from main import handle_ia_command
        await handle_ia_command(event, provider=None)
    
    @client.on(events.NewMessage(pattern=r"^\.iagroq(?:\s|$)"))
    async def handle_ia_groq(event):
        """Comando .iagroq [pergunta] - força Groq"""
        from main import handle_ia_command
        await handle_ia_command(event, provider="groq")
    
    @client.on(events.NewMessage(pattern=r"^\.iarouter(?:\s|$)"))
    async def handle_ia_openrouter(event):
        """Comando .iarouter [pergunta] - força OpenRouter"""
        from main import handle_ia_command
        await handle_ia_command(event, provider="openrouter")
    
    @client.on(events.NewMessage(pattern=r"^\.ai(?:\s|$)"))
    async def handle_ai_config(event):
        """Comando .ai [groq|openrouter] - define IA padrão"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        parts = event.raw_text.split(maxsplit=1)
        
        if len(parts) < 2:
            current = ia_manager.get_current_provider()
            available = ", ".join(ia_manager.get_available_providers())
            msg = f"IA padrão: {current}\n"
            msg += f"Disponíveis: {available}\n\n"
            msg += ".ai groq\n"
            msg += ".ai openrouter"
            await event.reply(msg)
            return
        
        provider = parts[1].split()[0].lower()
        success = await ia_manager.switch_provider(provider)
        
        if success:
            await event.reply(f"IA padrão mudou para: {provider}")
        else:
            await event.reply(f"Erro ao mudar para {provider}")
            logger.warning(f"Falha ao mudar para {provider}")
    
    logger.info("IA handlers registrados")
