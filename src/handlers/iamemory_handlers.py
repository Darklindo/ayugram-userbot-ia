"""
Handlers para .iamemory
Comando que usa TODA a memória no contexto
"""

import logging
from telethon import events

logger = logging.getLogger(__name__)


async def register_iamemory_handlers(client, handle_iamemory_command, memory_manager, 
                                     ia_manager, token_limiter, perm_manager, 
                                     cooldown_manager, stats_manager, security_manager, 
                                     edit_long_message, history_manager):
    """Registra handlers para .iamemory"""
    
    @client.on(events.NewMessage(pattern=r"^\.iamemory(?:\s|$)"))
    async def handle_iamemory(event):
        """Comando .iamemory [pergunta] - usa TODA a memória"""
        await handle_iamemory_command(
            event,
            memory_mgr=memory_manager,
            ia_mgr=ia_manager,
            token_lim=token_limiter,
            perm_mgr=perm_manager,
            cooldown_mgr=cooldown_manager,
            stats_mgr=stats_manager,
            security_mgr=security_manager,
            edit_long_msg=edit_long_message,
            history_mgr=history_manager
        )
    
    logger.info("iamemory handlers registrados")
