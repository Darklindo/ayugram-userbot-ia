"""
Handlers de Memória
Comandos: .memory add, .memory list, .memory clear
"""

import logging
from telethon import events

logger = logging.getLogger(__name__)


async def register_memory_handlers(client, CONFIG, perm_manager, memory_manager):
    """Registra handlers de memória"""
    
    @client.on(events.NewMessage(pattern=r"^\.memory(?:\s|$)"))
    async def handle_memory(event):
        """Comando .memory - mostra ajuda"""
        sender = await event.get_sender()
        
        # Apenas o dono pode usar
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        help_text = """📚 Comandos de Memória:

.memory list - Lista todas as pessoas na memória
.memory add [nome] [info] - Adiciona info sobre uma pessoa
.memory clear [nome] - Remove info sobre uma pessoa

Exemplos:
.memory add João João é gay
.memory list
.memory clear João
"""
        await event.reply(help_text)
    
    @client.on(events.NewMessage(pattern=r"^\.memory\s+list(?:\s|$)"))
    async def handle_memory_list(event):
        """Comando .memory list - lista memória"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        memory_text = memory_manager.list_memory()
        await event.reply(memory_text)
    
    @client.on(events.NewMessage(pattern=r"^\.memory\s+add(?:\s|$)"))
    async def handle_memory_add(event):
        """Comando .memory add [nome] [info] - adiciona memória"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        parts = event.raw_text.split(maxsplit=3)
        
        if len(parts) < 4:
            await event.reply("Uso: .memory add [nome] [info]\nExemplo: .memory add João João é gay")
            return
        
        person_id = parts[2]
        info = parts[3]
        
        success = memory_manager.add_memory(person_id, info, source="manual")
        
        if success:
            await event.reply(f"✅ Memória adicionada: {person_id} = {info}")
        else:
            await event.reply(f"⚠️ Informação já existe ou erro ao adicionar")
    
    @client.on(events.NewMessage(pattern=r"^\.memory\s+clear(?:\s|$)"))
    async def handle_memory_clear(event):
        """Comando .memory clear [nome] - remove memória"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        parts = event.raw_text.split(maxsplit=2)
        
        if len(parts) < 3:
            await event.reply("Uso: .memory clear [nome]\nExemplo: .memory clear João")
            return
        
        person_id = parts[2]
        
        success = memory_manager.clear_memory(person_id)
        
        if success:
            await event.reply(f"✅ Memória limpa: {person_id}")
        else:
            await event.reply(f"❌ Pessoa não encontrada: {person_id}")
    
    logger.info("Memory handlers registrados")
