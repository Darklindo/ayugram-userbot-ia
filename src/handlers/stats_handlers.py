"""
Handlers de Estatísticas
Comandos: .stats, .mystats
"""

import logging
from datetime import datetime
from telethon import events

logger = logging.getLogger(__name__)


async def register_stats_handlers(client, CONFIG, stats_manager, ia_manager, perm_manager):
    """Registra handlers de estatísticas"""
    
    @client.on(events.NewMessage(pattern=r"^\.status(?:\s|$)"))
    async def handle_status(event):
        """Comando .status"""
        sender = await event.get_sender()
        current_ia = ia_manager.get_current_provider()
        
        status_text = f"""Status:
Usuário: {sender.first_name}
ID: {sender.id}
Permissão: {'SIM' if await perm_manager.is_allowed(sender.id) else 'NÃO'}
IA Padrão: {current_ia}
Hora: {datetime.now().strftime('%H:%M:%S')}"""
        await event.reply(status_text)
    
    @client.on(events.NewMessage(pattern=r"^\.(stats|mystats)(?:\s|$)"))
    async def handle_stats(event):
        """Comando .stats ou .mystats"""
        sender = await event.get_sender()
        
        if event.raw_text.startswith(".mystats"):
            # Estatísticas do usuário
            stats_text = await stats_manager.format_user_stats(sender.id)
        else:
            # Estatísticas gerais (apenas dono)
            if sender.id != CONFIG["OWNER_ID"]:
                await event.reply("Apenas o dono pode ver estatísticas gerais")
                return
            stats_text = await stats_manager.format_stats()
        
        await event.reply(stats_text)
    
    logger.info("Stats handlers registrados")
