"""
Handlers de Admin
Comandos: .perm, .ban, .unban
"""

import logging
from telethon import events

logger = logging.getLogger(__name__)


async def register_admin_handlers(client, CONFIG, perm_manager):
    """Registra todos os handlers de admin"""
    
    @client.on(events.NewMessage(pattern=r"^\.perm(?:\s|$)"))
    async def handle_perm(event):
        """Comando .perm para gerenciar permissões"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                msg = ".perm [ID] - Dar permissão\n"
                msg += ".perm remove [ID] - Remover permissão\n"
                msg += ".perm list - Listar usuários"
                await event.reply(msg)
                return
            
            args = parts[1].split()
            
            if args[0].lower() == "list":
                users = await perm_manager.get_all()
                if not users:
                    await event.reply("Nenhum usuário com permissão")
                else:
                    msg = "Usuários com permissão:\n"
                    for uid in users:
                        msg += f"• {uid}\n"
                    await event.reply(msg)
            
            elif args[0].lower() == "remove" and len(args) > 1:
                user_id = int(args[1])
                if await perm_manager.remove_user(user_id):
                    await event.reply(f"Permissão removida de {user_id}")
                else:
                    await event.reply(f"Usuário {user_id} não tinha permissão")
            
            else:
                user_id = int(args[0])
                if await perm_manager.add_user(user_id):
                    await event.reply(f"Permissão concedida para {user_id}")
                else:
                    await event.reply(f"Usuário {user_id} já tem permissão")
        
        except (ValueError, IndexError):
            await event.reply("Erro: Formato inválido")
        except Exception as e:
            logger.exception("Erro em .perm")
            await event.reply("Erro ao processar comando")
    
    @client.on(events.NewMessage(pattern=r"^\.ban(?:\s|$)"))
    async def handle_ban(event):
        """Comando .ban para banir usuários"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                msg = ".ban [ID] - Banir usuário\n"
                msg += ".ban list - Listar banidos"
                await event.reply(msg)
                return
            
            args = parts[1].split()
            
            if args[0].lower() == "list":
                banned = await perm_manager.get_banned()
                if not banned:
                    await event.reply("Nenhum usuário banido")
                else:
                    msg = "Usuários banidos:\n"
                    for uid in banned:
                        msg += f"• {uid}\n"
                    await event.reply(msg)
            else:
                user_id = int(args[0])
                if await perm_manager.ban_user(user_id):
                    await event.reply(f"✅ Usuário {user_id} banido")
                else:
                    await event.reply(f"❌ Erro ao banir {user_id}")
        
        except (ValueError, IndexError):
            await event.reply("Erro: Formato inválido")
        except Exception as e:
            logger.exception("Erro em .ban")
            await event.reply("Erro ao processar comando")
    
    @client.on(events.NewMessage(pattern=r"^\.unban(?:\s|$)"))
    async def handle_unban(event):
        """Comando .unban para desbanir usuários"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                await event.reply(".unban [ID] - Desbanir usuário")
                return
            
            user_id = int(parts[1].split()[0])
            if await perm_manager.unban_user(user_id):
                await event.reply(f"✅ Banimento removido de {user_id}")
            else:
                await event.reply(f"❌ Erro ao desbanir {user_id}")
        
        except (ValueError, IndexError):
            await event.reply("Erro: Formato inválido")
        except Exception as e:
            logger.exception("Erro em .unban")
            await event.reply("Erro ao processar comando")
    
    logger.info("Admin handlers registrados")
