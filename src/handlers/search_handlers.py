"""
Handlers de Busca Web
Comandos: .search
"""

import logging
from telethon import events
from translator import translate_search_result

logger = logging.getLogger(__name__)


async def register_search_handlers(client, perm_manager, web_search_manager, edit_long_message):
    """Registra handlers de busca web"""
    
    @client.on(events.NewMessage(pattern=r"^\.search(?:\s|$)"))
    async def handle_search(event):
        """Comando .search para buscar na web"""
        sender = await event.get_sender()
        
        if not await perm_manager.is_allowed(sender.id):
            await event.reply("Você não tem permissão para usar IA")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                await event.reply(".search [termo] - Buscar na web")
                return
            
            query = parts[1]
            processing_msg = await event.reply("🔍 Buscando...")
            
            result = await web_search_manager.search(query)
            # Traduzir resultado para português
            result_translated = translate_search_result(result)
            response = web_search_manager.format_search_result(result_translated)
            
            # Usar edit_long_message para suportar respostas longas (>4096 chars)
            await edit_long_message(processing_msg, response)
        
        except Exception as e:
            logger.exception("Erro em .search")
            await event.reply("❌ Erro ao buscar")
            try:
                await processing_msg.delete()
            except:
                pass
    
    logger.info("Search handlers registrados")
