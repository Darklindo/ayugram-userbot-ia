#!/usr/bin/env python3
"""
JT IA UserBot para Telegram
Bot profissional com multiplos provedores de IA
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
    AuthKeyUnregisteredError
)

from config import load_config, validate_config
from permissions import PermissionManager
from ia.manager import IAManager
from cooldown import CooldownManager
from history_manager import HistoryManager
from token_limiter import TokenLimiter
from stats_manager import StatsManager
from utils import edit_long_message, split_message

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

CONFIG = None
client = None
perm_manager = None
ia_manager = None
history_manager = HistoryManager(max_messages=5)
token_limiter = TokenLimiter(default_limit="medium")
stats_manager = StatsManager()
cooldown_manager = CooldownManager(default_cooldown=5)
reconnect_task = None

async def load_configuration():
    """Carrega e valida configuracao"""
    global CONFIG
    try:
        CONFIG = load_config()
        validate_config(CONFIG)
        logger.info("Configuracao carregada com sucesso")
        return True
    except Exception as e:
        logger.exception("Erro ao carregar configuracao")
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
        
        ia_manager = IAManager(CONFIG["AI_PROVIDER"], CONFIG["AI_KEYS"])
        await ia_manager.init()
        logger.info(f"IAManager inicializado com {CONFIG['AI_PROVIDER']}")
        
        return True
    except Exception as e:
        logger.exception("Erro ao inicializar gerenciadores")
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
    except Exception as e:
        logger.exception("Erro na autenticacao")
        return False

async def handle_ia_command(event, provider: str = None):
    """
    Handler unificado para todos os comandos de IA
    Reduz duplicacao de codigo
    """
    sender = await event.get_sender()
    
    if not perm_manager.is_allowed(sender.id):
        await event.reply("Voce nao tem permissao")
        return
    
    # Aplicar cooldown ANTES de processar
    if cooldown_manager.is_on_cooldown(sender.id):
        remaining = cooldown_manager.get_remaining(sender.id)
        await event.reply(f"Aguarde {remaining}s antes de fazer outra pergunta")
        return
    
    # Extrair prompt: divide em comando e resto
    # Mais seguro que str.replace() que remove todas as ocorrências
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        if provider:
            await event.reply(f".ia{provider} [pergunta]")
        else:
            await event.reply(".ia [pergunta]")
        return
    
    prompt = parts[1]
    
    # Parse de flags de limite de tokens e modo privado
    prompt, token_limit, private_mode = token_limiter.parse_flags(prompt)
    
    # Adicionar histórico de conversa para melhor contexto
    chat_id = event.chat_id
    context = history_manager.get_context(chat_id)
    if context:
        prompt = f"Contexto anterior:\n{context}\n\nNova pergunta: {prompt}"
    
    # Se for resposta a mensagem, usar o texto da mensagem original como contexto
    if event.reply_to_msg_id:
        try:
            replied_msg = await event.get_reply_message()
            if replied_msg and replied_msg.text:
                # Combinar texto da mensagem original com a pergunta
                prompt = f"{replied_msg.text}\n\nPergunta: {prompt}"
        except Exception as e:
            logger.warning(f"Erro ao obter mensagem respondida: {e}")
    
    # Definir cooldown ANTES de processar
    cooldown_manager.set_cooldown(sender.id)
    
    try:
        provider_name = provider or "padrao"
        processing_msg = await event.reply(f"⏳ Processando com {provider_name}...")
        
        # Adicionar reação de processamento
        try:
            await event.react("⏳")
        except:
            pass  # Alguns clientes não suportam reações
        
        # Obter timeout dinamico
        timeout = ia_manager.get_timeout(provider)
        
        # Processar com timeout
        try:
            response = await asyncio.wait_for(
                ia_manager.process(prompt, provider=provider),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            response = f"Timeout: {provider_name} demorou mais de {timeout}s"
        
        # Aplicar limite de tokens
        response = token_limiter.truncate(response, token_limit)
        
        # Se modo privado, enviar em DM
        if private_mode:
            try:
                await sender.send_message(response)
                await processing_msg.delete()
                await event.reply("✅ Resposta enviada em privado!")
                logger.info(f"Resposta privada enviada para {sender.id}")
                # Reação de sucesso
                try:
                    await event.react("✅")
                except:
                    pass
            except Exception as e:
                logger.warning(f"Erro ao enviar DM: {e}")
                await edit_long_message(processing_msg, response)
                try:
                    await event.react("❌")
                except:
                    pass
        else:
            # Editar mensagem com suporte a mensagens longas
            await edit_long_message(processing_msg, response)
            # Reação de sucesso
            try:
                await event.react("✅")
            except:
                pass
        
        # Adicionar pergunta e resposta ao histórico
        sender_name = sender.first_name or "Usuario"
        history_manager.add_message(chat_id, sender_name, parts[1])  # Pergunta original
        history_manager.add_message(chat_id, "Bot", response[:200])  # Resposta (limitada)
        
        # Registrar nas estatísticas
        stats_manager.record_query(sender.id, provider or "padrao", success=True)
    
    except FloodWaitError as e:
        logger.warning(f"FloodWait ao processar IA: aguardando {e.seconds}s")
        stats_manager.record_query(sender.id, provider or "padrao", success=False)
        await event.reply(f"⏸️ Muitas requisicoes. Aguarde {e.seconds}s")
        try:
            await event.react("❌")
        except:
            pass
    except Exception as e:
        logger.exception("Erro ao processar comando de IA")
        stats_manager.record_query(sender.id, provider or "padrao", success=False)
        await event.reply("❌ Erro ao processar pergunta")
        try:
            await event.react("❌")
        except:
            pass

def register_handlers():
    """Registra handlers de eventos"""
    
    @client.on(events.NewMessage(pattern=r"^\.ia(?:\s|$)"))
    async def handle_ia(event):
        """Comando .ia [pergunta] - usa IA padrao"""
        await handle_ia_command(event, provider=None)
    

    @client.on(events.NewMessage(pattern=r"^\.iagroq(?:\s|$)"))
    async def handle_ia_groq(event):
        """Comando .iagroq [pergunta] - força Groq"""
        await handle_ia_command(event, provider="groq")
    
    @client.on(events.NewMessage(pattern=r"^\.iarouter(?:\s|$)"))
    async def handle_ia_openrouter(event):
        """Comando .iarouter [pergunta] - força OpenRouter"""
        await handle_ia_command(event, provider="openrouter")
    
    @client.on(events.NewMessage(pattern=r"^\.ai(?:\s|$)"))
    async def handle_ai_config(event):
        """Comando .ai [gemini|groq|openrouter] - define IA padrao"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        parts = event.raw_text.split(maxsplit=1)
        
        if len(parts) < 2:
            current = ia_manager.get_current_provider()
            available = ", ".join(ia_manager.get_available_providers())
            msg = f"IA padrao: {current}\n"
            msg += f"Disponiveis: {available}\n\n"
            msg += ".ai groq\n"
            msg += ".ai openrouter"
            await event.reply(msg)
            return
        
        provider = parts[1].split()[0].lower()  # Pega primeira palavra
        success = await ia_manager.switch_provider(provider)
        
        if success:
            await event.reply(f"IA padrao mudou para: {provider}")
        else:
            await event.reply(f"Erro ao mudar para {provider}")
            logger.warning(f"Falha ao mudar para {provider}")
    
    @client.on(events.NewMessage(pattern=r"^\.perm(?:\s|$)"))
    async def handle_perm(event):
        """Comando .perm para gerenciar permissoes"""
        sender = await event.get_sender()
        
        if sender.id != CONFIG["OWNER_ID"]:
            await event.reply("Apenas o dono pode usar este comando")
            return
        
        try:
            parts = event.raw_text.split(maxsplit=1)
            
            if len(parts) < 2:
                msg = ".perm [ID] - Dar permissao\n"
                msg += ".perm remove [ID] - Remover permissao\n"
                msg += ".perm list - Listar usuarios"
                await event.reply(msg)
                return
            
            # Parse argumentos: .perm [ID|remove|list]
            args = parts[1].split()
            
            if args[0].lower() == "list":
                users = perm_manager.get_all()
                if not users:
                    await event.reply("Nenhum usuario com permissao")
                else:
                    msg = "Usuarios com permissao:\n"
                    for uid in users:
                        msg += f"• {uid}\n"
                    await event.reply(msg)
            
            elif args[0].lower() == "remove" and len(args) > 1:
                user_id = int(args[1])
                if perm_manager.remove_user(user_id):
                    await event.reply(f"Permissao removida de {user_id}")
                else:
                    await event.reply(f"Usuario {user_id} nao tinha permissao")
            
            else:
                user_id = int(args[0])
                if perm_manager.add_user(user_id):
                    await event.reply(f"Permissao concedida para {user_id}")
                else:
                    await event.reply(f"Usuario {user_id} ja tem permissao")
        
        except (ValueError, IndexError):
            await event.reply("Erro: Formato invalido")
        except Exception as e:
            logger.exception("Erro em .perm")
            await event.reply("Erro ao processar comando")
    
    @client.on(events.NewMessage(pattern=r"^\.help(?:\s|$)"))
    async def handle_help(event):
        """Comando .help"""
        help_text = """JT IA Bot

Comandos de IA:
.ia [pergunta] - Usa IA padrao
.iagroq [pergunta] - Força Groq
.iarouter [pergunta] - Força OpenRouter
.ai [groq|openrouter] - Define IA padrao

RESPOSTA A MENSAGENS:
Responda uma mensagem com .ia [pergunta] para usar a IA nela

LIMITES DE TOKENS:
.ia -short [pergunta]   (150 chars)
.ia -medium [pergunta]  (500 chars - padrao)
.ia -long [pergunta]    (2000 chars)
.ia -full [pergunta]    (4000 chars)

MODO PRIVADO:
.ia -private [pergunta] (resposta em DM)
.ia -short -private [pergunta] (combina flags)

Permissoes (dono):
.perm [ID] - Dar permissao
.perm remove [ID] - Remover permissao
.perm list - Listar usuarios

Info:
.status - Ver status
.stats - Ver estatísticas gerais (dono)
.mystats - Ver suas estatísticas
.help - Este menu

Exemplo:
.ia Qual eh a capital do Brasil?
.iagroq Como criar uma API?
.ai groq

Responder mensagem:
Responda: .ia Qual eh a capital?"""
        await event.reply(help_text)
    
    @client.on(events.NewMessage(pattern=r"^\.status(?:\s|$)"))
    async def handle_status(event):
        """Comando .status"""
        sender = await event.get_sender()
        current_ia = ia_manager.get_current_provider()
        
        status_text = f"""Status:
Usuario: {sender.first_name}
ID: {sender.id}
Permissao: {'SIM' if perm_manager.is_allowed(sender.id) else 'NAO'}
IA Padrao: {current_ia}
Hora: {datetime.now().strftime('%H:%M:%S')}"""
        await event.reply(status_text)
    
    @client.on(events.NewMessage(pattern=r"^\.(stats|mystats)(?:\s|$)"))
    async def handle_stats(event):
        """Comando .stats ou .mystats"""
        sender = await event.get_sender()
        
        if event.raw_text.startswith(".mystats"):
            # Estatísticas do usuário
            stats_text = stats_manager.format_user_stats(sender.id)
        else:
            # Estatísticas gerais (apenas dono)
            if sender.id != CONFIG["OWNER_ID"]:
                await event.reply("Apenas o dono pode ver estatísticas gerais")
                return
            stats_text = stats_manager.format_stats()
        
        await event.reply(stats_text)
    
    logger.info("Handlers registrados com sucesso")

async def reconnect_loop():
    """Loop de reconexao automatica com verificacao de autorizacao"""
    while True:
        try:
            if not client.is_connected():
                logger.warning("Conexao perdida, tentando reconectar...")
                try:
                    await client.connect()
                    
                    # Verificar se ainda esta autorizado
                    if not await client.is_user_authorized():
                        logger.error("Sessao expirou, reautenticando...")
                        # Aqui o bot precisaria fazer login novamente
                        # Por enquanto, apenas registra o erro
                        logger.error("Sessao nao autorizada apos reconexao")
                    else:
                        logger.info("Reconectado com sucesso")
                
                except FloodWaitError as e:
                    logger.warning(f"FloodWait durante reconexao: aguardando {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except AuthKeyUnregisteredError:
                    logger.error("Sessao invalida, bot precisa fazer login novamente")
                except Exception as e:
                    logger.exception("Erro durante reconexao")
        except Exception as e:
            logger.exception("Erro no loop de reconexao")
        
        await asyncio.sleep(30)

async def main():
    """Funcao principal"""
    global reconnect_task
    
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
    
    register_handlers()
    
    logger.info("[+] Bot rodando com sucesso!")
    logger.info(f"[+] IA Padrao: {CONFIG['AI_PROVIDER']}")
    logger.info(f"[+] IAs Disponiveis: {', '.join(ia_manager.get_available_providers())}")
    logger.info(f"[+] Dono: {CONFIG['OWNER_ID']}")
    logger.info(f"[+] Usuarios com permissao: {len(perm_manager.get_all())}")
    logger.info("[+] Aguardando comandos...")
    logger.info("[+] Use .help para ver os comandos disponiveis")
    logger.info("[+] Pressione Ctrl+C para parar")
    logger.info("")
    
    reconnect_task = asyncio.create_task(reconnect_loop())
    
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Bot desconectado pelo usuario")
    except Exception as e:
        logger.exception("Erro durante execucao do bot")
    finally:
        logger.info("Finalizando bot...")
        
        if reconnect_task:
            reconnect_task.cancel()
            try:
                await asyncio.gather(reconnect_task, return_exceptions=True)
            except Exception as e:
                logger.exception("Erro ao cancelar reconnect_task")
        
        if ia_manager:
            try:
                await ia_manager.close_all()
            except Exception as e:
                logger.exception("Erro ao fechar sessoes de IA")
        
        if client:
            try:
                await client.disconnect()
            except Exception as e:
                logger.exception("Erro ao desconectar cliente")
        
        logger.info("Bot finalizado")

if __name__ == "__main__":
    asyncio.run(main())
