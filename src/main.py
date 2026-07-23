#!/usr/bin/env python3
"""
JT IA UserBot para Telegram
Bot profissional com múltiplos provedores de IA
Arquitetura refatorada com handlers modulares
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
from personas_manager import PersonasManager
from web_search_manager import WebSearchManager
from audio_transcription_manager import AudioTranscriptionManager
from image_vision_manager import ImageVisionManager
from cooldown import CooldownManager
from history_manager import HistoryManager
from token_limiter import TokenLimiter
from stats_manager import StatsManager
from utils import edit_long_message, split_message
from security import SecurityManager

# Importar handlers modulares
from handlers import (
    register_ia_handlers,
    register_admin_handlers,
    register_search_handlers,
    register_persona_handlers,
    register_stats_handlers,
    register_help_handlers,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Variáveis globais
CONFIG = None
client = None
perm_manager = None
ia_manager = None
personas_manager = None
web_search_manager = None
audio_transcription_manager = None
image_vision_manager = None
history_manager = HistoryManager(max_messages=5)
token_limiter = TokenLimiter(default_limit="medium")
stats_manager = StatsManager()
cooldown_manager = CooldownManager(default_cooldown=5)
security_manager = SecurityManager(max_prompt_length=2000, max_requests_per_minute=10)
reconnect_task = None


async def load_configuration():
    """Carrega e valida configuração"""
    global CONFIG
    try:
        CONFIG = load_config()
        validate_config(CONFIG)
        logger.info("Configuração carregada com sucesso")
        return True
    except Exception as e:
        logger.exception("Erro ao carregar configuração")
        return False


async def init_managers():
    """Inicializa gerenciadores"""
    global perm_manager, ia_manager, personas_manager, web_search_manager
    global audio_transcription_manager, image_vision_manager
    
    try:
        perm_manager = PermissionManager(
            file_path="permissions.json",
            owner_id=CONFIG["OWNER_ID"]
        )
        logger.info(f"PermissionManager inicializado (dono: {CONFIG['OWNER_ID']})")
        
        ia_manager = IAManager(CONFIG["AI_PROVIDER"], CONFIG["AI_KEYS"])
        await ia_manager.init()
        logger.info(f"IAManager inicializado com {CONFIG['AI_PROVIDER']}")
        
        personas_manager = PersonasManager()
        logger.info("PersonasManager inicializado")
        
        web_search_manager = WebSearchManager()
        logger.info("WebSearchManager inicializado")
        
        audio_transcription_manager = AudioTranscriptionManager(
            groq_api_key=CONFIG["AI_KEYS"].get("groq")
        )
        logger.info("AudioTranscriptionManager inicializado")
        
        image_vision_manager = ImageVisionManager(
            groq_api_key=CONFIG["AI_KEYS"].get("groq"),
            openrouter_api_key=CONFIG["AI_KEYS"].get("openrouter")
        )
        logger.info("ImageVisionManager inicializado")
        
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
            logger.info(f"Já autenticado como: {me.first_name}")
            return True
        
        logger.info(f"Enviando código para {CONFIG['PHONE_NUMBER']}...")
        await client.send_code_request(CONFIG["PHONE_NUMBER"])
        
        try:
            code = getpass.getpass("[*] Digite o código: ")
        except:
            code = input("[*] Digite o código: ")
        
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
        logger.error("Número de telefone inválido")
        return False
    except FloodWaitError as e:
        logger.error(f"Muitas tentativas. Aguarde {e.seconds}s")
        return False
    except Exception as e:
        logger.exception("Erro na autenticação")
        return False


async def handle_ia_command(event, provider: str = None):
    """
    Handler unificado para todos os comandos de IA
    Reduz duplicação de código
    """
    sender = await event.get_sender()
    
    if not await perm_manager.is_allowed(sender.id):
        await event.reply("Você não tem permissão")
        return
    
    # Verificar cooldown ANTES de processar
    if await cooldown_manager.is_on_cooldown(sender.id):
        remaining = await cooldown_manager.get_remaining(sender.id)
        await event.reply(f"Aguarde {remaining}s antes de fazer outra pergunta")
        return
    
    # Extrair prompt: divide em comando e resto
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        if provider:
            await event.reply(f".ia{provider} [pergunta]")
        else:
            await event.reply(".ia [pergunta]")
        return
    
    prompt = parts[1]
    
    # Validar tamanho do prompt (segurança)
    valid, error_msg = await security_manager.validate_prompt(prompt)
    if not valid:
        await event.reply(f"❌ {error_msg}")
        return
    
    # Verificar rate limit por minuto (segurança)
    allowed, error_msg = await security_manager.check_rate_limit(sender.id)
    if not allowed:
        await event.reply(f"❌ {error_msg}")
        return
    
    # Sanitizar prompt
    prompt = SecurityManager.sanitize_prompt(prompt)
    
    # Parse de flags de limite de tokens e modo privado
    prompt, token_limit, private_mode = token_limiter.parse_flags(prompt)
    
    # Adicionar histórico de conversa para melhor contexto
    # Usar (chat_id, sender_id) para evitar mistura de contextos
    chat_id = event.chat_id
    context = await history_manager.get_context(chat_id, sender.id)
    if context:
        prompt = f"Contexto anterior:\n{context}\n\nNova pergunta: {prompt}"
    
    # Se for resposta a mensagem, usar o texto da mensagem original como contexto
    if event.reply_to_msg_id:
        try:
            replied_msg = await event.get_reply_message()
            if replied_msg and replied_msg.text:
                prompt = f"{replied_msg.text}\n\nPergunta: {prompt}"
        except Exception as e:
            logger.warning(f"Erro ao obter mensagem respondida: {e}")
    
    # Nota: Cooldown será definido APÓS sucesso da IA
    
    try:
        provider_name = provider or "padrão"
        processing_msg = await event.reply(f"⏳ Processando com {provider_name}...")
        
        # Obter timeout dinâmico
        timeout = ia_manager.get_timeout(provider)
        
        # Processar com timeout
        try:
            response = await asyncio.wait_for(
                ia_manager.process(prompt, provider=provider),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            response = f"Timeout: {provider_name} demorou mais de {timeout}s"
        
        # Validar resposta antes de processar
        if response is None:
            response = "Erro: Resposta vazia da IA"
            await event.reply(response)
            return
        
        # Aplicar limite de tokens
        response = token_limiter.truncate(response, token_limit)
        
        # Se modo privado, enviar em DM
        if private_mode:
            try:
                await sender.send_message(response)
                await processing_msg.delete()
                await event.reply("✅ Resposta enviada em privado!")
                logger.info(f"Resposta privada enviada para {sender.id}")
            except Exception as e:
                logger.warning(f"Erro ao enviar DM: {e}")
                # Fallback: editar mensagem no grupo
                try:
                    await edit_long_message(processing_msg, response)
                except Exception as e2:
                    logger.error(f"Erro ao editar mensagem: {e2}")
                    await event.reply("❌ Erro ao enviar resposta")
        else:
            # Editar mensagem com suporte a mensagens longas
            try:
                await edit_long_message(processing_msg, response)
            except Exception as e:
                logger.error(f"Erro ao editar mensagem longa: {e}")
                await event.reply("❌ Erro ao enviar resposta")
        
        # Adicionar pergunta e resposta ao histórico com (chat_id, sender_id)
        sender_name = sender.first_name or "Usuário"
        await history_manager.add_message(chat_id, sender.id, sender_name, parts[1])
        await history_manager.add_message(chat_id, sender.id, "Bot", response[:200])
        
        # Registrar nas estatísticas
        await stats_manager.record_query(sender.id, provider or "padrão", success=True)
        
        # Registrar requisição para rate limiting
        await security_manager.record_request(sender.id)
        
        # ✅ APLICAR COOLDOWN APÓS SUCESSO (não antes)
        await cooldown_manager.set_cooldown(sender.id)
    
    except FloodWaitError as e:
        user_hash = SecurityManager.hash_user_id(sender.id)
        logger.warning(f"FloodWait do usuário {user_hash}: aguardando {e.seconds}s")
        await stats_manager.record_query(sender.id, provider or "padrão", success=False)
        await event.reply(f"⏸️ Muitas requisições. Aguarde {e.seconds}s")
    except Exception as e:
        user_hash = SecurityManager.hash_user_id(sender.id)
        logger.exception(f"Erro ao processar pergunta do usuário {user_hash}")
        await stats_manager.record_query(sender.id, provider or "padrão", success=False)
        await event.reply("❌ Erro ao processar pergunta")


async def register_all_handlers():
    """Registra todos os handlers de eventos"""
    logger.info("Registrando handlers...")
    
    await register_ia_handlers(
        client, CONFIG, perm_manager, ia_manager,
        cooldown_manager, history_manager, token_limiter,
        stats_manager, security_manager, edit_long_message
    )
    
    await register_admin_handlers(client, CONFIG, perm_manager)
    await register_search_handlers(client, perm_manager, web_search_manager, edit_long_message)
    await register_persona_handlers(client, CONFIG, personas_manager)
    await register_stats_handlers(client, CONFIG, stats_manager, ia_manager, perm_manager)
    await register_help_handlers(client)
    
    logger.info("✅ Todos os handlers registrados com sucesso")


async def reconnect_loop():
    """Loop de reconexão automática com verificação de autorização"""
    while True:
        try:
            if not client.is_connected():
                logger.warning("Conexão perdida, tentando reconectar...")
                try:
                    await client.connect()
                    
                    # Verificar se ainda está autorizado
                    if not await client.is_user_authorized():
                        logger.error("Sessão expirou, reautenticando...")
                        logger.error("Sessão não autorizada após reconexão")
                    else:
                        logger.info("Reconectado com sucesso")
                
                except FloodWaitError as e:
                    logger.warning(f"FloodWait durante reconexão: aguardando {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except AuthKeyUnregisteredError:
                    logger.error("Sessão inválida, bot precisa fazer login novamente")
                except Exception as e:
                    logger.exception("Erro durante reconexão")
        except Exception as e:
            logger.exception("Erro no loop de reconexão")
        
        await asyncio.sleep(30)


async def main():
    """Função principal"""
    global reconnect_task
    
    logger.info("Iniciando JT IA Bot...")
    
    if not await load_configuration():
        logger.error("Falha ao carregar configuração")
        return
    
    if not await init_managers():
        logger.error("Falha ao inicializar gerenciadores")
        return
    
    if not await authenticate_client():
        logger.error("Falha na autenticação")
        return
    
    await register_all_handlers()
    
    logger.info("[+] Bot rodando com sucesso!")
    logger.info(f"[+] IA Padrão: {CONFIG['AI_PROVIDER']}")
    logger.info(f"[+] IAs Disponíveis: {', '.join(ia_manager.get_available_providers())}")
    logger.info(f"[+] Dono: {CONFIG['OWNER_ID']}")
    logger.info(f"[+] Usuários com permissão: {len(await perm_manager.get_all())}")
    logger.info("[+] Segurança ativada (validação, sanitização, rate limiting)")
    logger.info(f"[+] Max prompt: {security_manager.max_prompt_length} chars")
    logger.info(f"[+] Rate limit: {security_manager.max_requests_per_minute}/min")
    logger.info("[+] Aguardando comandos...")
    logger.info("[+] Use .help para ver os comandos disponíveis")
    logger.info("[+] Pressione Ctrl+C para parar")
    logger.info("")
    
    reconnect_task = asyncio.create_task(reconnect_loop())
    
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Bot desconectado pelo usuário")
    except Exception as e:
        logger.exception("Erro durante execução do bot")
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
                if hasattr(ia_manager, 'close_all'):
                    await ia_manager.close_all()
                elif hasattr(ia_manager, 'close_session'):
                    await ia_manager.close_session()
            except Exception as e:
                logger.exception("Erro ao fechar sessões de IA")
        
        if client:
            try:
                await client.disconnect()
            except Exception as e:
                logger.exception("Erro ao desconectar cliente")
        
        # Fechar sessões dos novos managers
        if web_search_manager:
            try:
                await web_search_manager.close_session()
            except Exception as e:
                logger.debug(f"Erro ao fechar WebSearchManager: {e}")
        
        if audio_transcription_manager:
            try:
                await audio_transcription_manager.close_session()
            except Exception as e:
                logger.debug(f"Erro ao fechar AudioTranscriptionManager: {e}")
        
        if image_vision_manager:
            try:
                await image_vision_manager.close_session()
            except Exception as e:
                logger.debug(f"Erro ao fechar ImageVisionManager: {e}")
        
        logger.info("Bot finalizado")


if __name__ == "__main__":
    asyncio.run(main())
