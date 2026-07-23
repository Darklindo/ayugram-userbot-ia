#!/usr/bin/env python3
"""
JT IA UserBot para Telegram
Bot robusto com IA, permissoes e reconexao automatica
"""

import os
import asyncio
import logging
import getpass
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    FloodWaitError,
    PhoneNumberInvalidError,
    InvalidSessionError
)

from config import load_config, validate_config
from permissions import PermissionManager
from ia_manager import IAManager
from cooldown import CooldownManager

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

CONFIG = None
client = None
perm_manager = None
ia_manager = None
cooldown_manager = CooldownManager(default_cooldown=5)

async def load_configuration():
    """Carrega e valida configuracao"""
    global CONFIG
    try:
        CONFIG = load_config()
        validate_config(CONFIG)
        logger.info("Configuracao carregada com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao carregar configuracao: {e}")
        return False

async def init_managers():
    """Inicializa gerenciadores"""
    global perm_manager, ia_manager
    
    try:
        perm_manager = PermissionManager(
            file_path="permissions.json",
            owner_id=CONFIG["OWNER_ID"]
        )
        logger.info(f"PermissionManager inicializado (dono: {CONFIG['OWNER_ID']})")
        
        ia_manager = IAManager(CONFIG["MANUS_API_URL"], CONFIG["MANUS_API_KEY"])
        await ia_manager.init_session()
        logger.info("IAManager inicializado")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar gerenciadores: {e}")
        return False

async def authenticate_client():
    """Autentica o cliente com tratamento de erros"""
    global client
    
    try:
        client = TelegramClient("ayugram_session", CONFIG["API_ID"], CONFIG["API_HASH"])
        await client.connect()
        logger.info("Conectado ao Telegram")
        
        if await client.is_user_authorized():
            me = await client.get_me()
            logger.info(f"Ja autenticado como: {me.first_name}")
            return True
        
        logger.info(f"Enviando codigo para {CONFIG['PHONE_NUMBER']}...")
        await client.send_code_request(CONFIG["PHONE_NUMBER"])
        
        try:
            code = getpass.getpass("[*] Digite o codigo: ")
        except:
            code = input("[*] Digite o codigo: ")
        
        try:
            await client.sign_in(CONFIG["PHONE_NUMBER"], code)
            me = await client.get_me()
            logger.info(f"Autenticado como: {me.first_name}")
            return True
        
        except SessionPasswordNeededError:
            logger.info("2FA detectado")
            
            if CONFIG["PASSWORD_2FA"]:
                await client.sign_in(password=CONFIG["PASSWORD_2FA"])
                logger.info("Autenticado com 2FA")
            else:
                try:
                    password = getpass.getpass("[*] Senha 2FA: ")
                except:
                    password = input("[*] Senha 2FA: ")
                await client.sign_in(password=password)
                logger.info("Autenticado com 2FA")
            
            return True
    
    except PhoneNumberInvalidError:
        logger.error("Numero de telefone invalido")
        return False
    except FloodWaitError as e:
        logger.error(f"Muitas tentativas. Aguarde {e.seconds}s")
        return False
    except InvalidSessionError:
        logger.error("Sessao invalida. Deletando session file...")
        if os.path.exists("ayugram_session.session"):
            os.remove("ayugram_session.session")
        return False
    except Exception as e:
        logger.error(f"Erro na autenticacao: {e}")
        return False

@client.on(events.NewMessage(pattern=r"^\.ia(?:\s|$)"))
async def handle_ia(event):
    """Comando .ia com cooldown"""
    sender = await event.get_sender()
    
    if not perm_manager.is_allowed(sender.id):
        await event.reply("Voce nao tem permissao")
        return
    
    if cooldown_manager.is_on_cooldown(sender.id):
        remaining = cooldown_manager.get_remaining(sender.id)
        await event.reply(f"Aguarde {remaining}s antes de fazer outra pergunta")
        return
    
    prompt = event.raw_text.replace(".ia", "").strip()
    
    if not prompt:
        await event.reply(".ia [pergunta]")
        return
    
    cooldown_manager.set_cooldown(sender.id)
    
    try:
        processing_msg = await event.reply("Processando...")
        response = await ia_manager.process(prompt)
        await processing_msg.edit(response)
    except Exception as e:
        logger.error(f"Erro em .ia: {e}")
        await event.reply(f"Erro: {str(e)}")

@client.on(events.NewMessage(pattern=r"^\.perm(?:\s|$)"))
async def handle_perm(event):
    """Comando .perm para gerenciar permissoes"""
    sender = await event.get_sender()
    
    if sender.id != CONFIG["OWNER_ID"]:
        await event.reply("Apenas o dono pode usar este comando")
        return
    
    try:
        args = event.raw_text.split()
        
        if len(args) < 2:
            msg = ".perm [ID] - Dar permissao\n"
            msg += ".perm remove [ID] - Remover permissao\n"
            msg += ".perm list - Listar usuarios"
            await event.reply(msg)
            return
        
        if args[1].lower() == "list":
            users = perm_manager.get_all()
            if not users:
                await event.reply("Nenhum usuario com permissao")
            else:
                msg = "Usuarios com permissao:\n"
                for uid in users:
                    msg += f"• {uid}\n"
                await event.reply(msg)
        
        elif args[1].lower() == "remove" and len(args) > 2:
            user_id = int(args[2])
            if perm_manager.remove_user(user_id):
                await event.reply(f"Permissao removida de {user_id}")
            else:
                await event.reply(f"Usuario {user_id} nao tinha permissao")
        
        else:
            user_id = int(args[1])
            if perm_manager.add_user(user_id):
                await event.reply(f"Permissao concedida para {user_id}")
            else:
                await event.reply(f"Usuario {user_id} ja tem permissao")
    
    except (ValueError, IndexError) as e:
        await event.reply(f"Erro: {str(e)}")
    except Exception as e:
        logger.error(f"Erro em .perm: {e}")
        await event.reply(f"Erro: {str(e)}")

@client.on(events.NewMessage(pattern=r"^\.help(?:\s|$)"))
async def handle_help(event):
    """Comando .help"""
    help_text = """JT IA Bot

Comandos:
.ia [pergunta] - Fazer pergunta
.perm [ID] - Dar permissao (dono)
.perm remove [ID] - Remover permissao (dono)
.perm list - Listar usuarios (dono)
.status - Ver status

Exemplo:
.ia Quanto eh 8x90?
.perm 123456789
.perm remove 123456789"""
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^\.status(?:\s|$)"))
async def handle_status(event):
    """Comando .status"""
    sender = await event.get_sender()
    
    status_text = f"""Status:
Usuario: {sender.first_name}
ID: {sender.id}
Permissao: {'SIM' if perm_manager.is_allowed(sender.id) else 'NAO'}
Hora: {datetime.now().strftime('%H:%M:%S')}"""
    await event.reply(status_text)

async def reconnect_loop():
    """Loop de reconexao automatica"""
    while True:
        try:
            if not client.is_connected():
                logger.warning("Conexao perdida, reconectando...")
                await client.connect()
                logger.info("Reconectado com sucesso")
        except Exception as e:
            logger.error(f"Erro na reconexao: {e}")
        
        await asyncio.sleep(30)

async def main():
    """Funcao principal"""
    logger.info("Iniciando JT IA Bot...")
    
    if not await load_configuration():
        logger.error("Falha ao carregar configuracao")
        return
    
    if not await init_managers():
        logger.error("Falha ao inicializar gerenciadores")
        return
    
    if not await authenticate_client():
        logger.error("Falha na autenticacao")
        return
    
    logger.info("[+] Bot rodando!")
    logger.info(f"[+] Dono: {CONFIG['OWNER_ID']}")
    logger.info(f"[+] Usuarios com permissao: {len(perm_manager.get_all())}")
    
    try:
        reconnect_task = asyncio.create_task(reconnect_loop())
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Bot desconectado pelo usuario")
    except Exception as e:
        logger.error(f"Erro: {e}")
    finally:
        await ia_manager.close_session()
        await client.disconnect()
        logger.info("Bot finalizado")

if __name__ == "__main__":
    asyncio.run(main())
