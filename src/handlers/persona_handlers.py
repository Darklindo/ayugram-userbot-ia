"""
Handlers de Personas
Comandos: .persona
"""

import logging
from telethon import events

logger = logging.getLogger(__name__)


async def register_persona_handlers(client, CONFIG, personas_manager):
    """Registra handlers de personas"""
    
    @client.on(events.NewMessage(pattern=r"^\.persona(?:\s|$)"))
    async def handle_persona(event):
        """Comando .persona para gerenciar personas"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                await event.reply(await personas_manager.list_personas())
                return
            
            persona_name = parts[1].split()[0].lower()
            
            if persona_name == "list":
                await event.reply(await personas_manager.list_personas())
            elif await personas_manager.set_persona(persona_name):
                emoji = await personas_manager.get_persona_emoji()
                await event.reply(f"{emoji} Persona alterada para: {persona_name}")
            else:
                await event.reply(f"Persona desconhecida: {persona_name}")
        
        except Exception as e:
            logger.exception("Erro em .persona")
            await event.reply("Erro ao processar comando")
    
    logger.info("Persona handlers registrados")
