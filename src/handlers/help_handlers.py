"""
Handlers de Ajuda
Comandos: .help
"""

import logging
from telethon import events

logger = logging.getLogger(__name__)


async def register_help_handlers(client):
    """Registra handlers de ajuda"""
    
    @client.on(events.NewMessage(pattern=r"^\.help(?:\s|$)"))
    async def handle_help(event):
        """Comando .help"""
        help_text = """JT IA Bot - Comandos Completos

IA:
.ia [pergunta] - Usa IA padrão
.iagroq [pergunta] - Força Groq
.iarouter [pergunta] - Força OpenRouter
.ai [groq|openrouter] - Define IA padrão

BUSCA:
.search [termo] - Buscar na web

PERSONAS:
.persona [nome] - Mudar personalidade
.persona list - Listar personas

PERMISSÕES (dono):
.perm [ID] - Dar permissão
.perm remove [ID] - Remover permissão
.perm list - Listar usuários

BAN (dono):
.ban [ID] - Banir usuário
.unban [ID] - Desbanir usuário
.ban list - Listar banidos

ESTATÍSTICAS:
.stats - Ver estatísticas gerais (dono)
.mystats - Ver suas estatísticas

FLAGS:
.ia -short [pergunta]   (150 chars)
.ia -medium [pergunta]  (500 chars)
.ia -long [pergunta]    (2000 chars)
.ia -full [pergunta]    (4000 chars)
.ia -private [pergunta] (resposta em DM)

RESPONDER MENSAGENS:
Responda com .ia [pergunta]
Funciona com: texto, audio, imagens

INFO:
.status - Ver status
.help - Este menu

Exemplos:
.ia Qual é a capital?
.search Python
.persona dev
.ia -private Teste
.ia -short -private Pergunta"""
        await event.reply(help_text)
    
    logger.info("Help handlers registrados")
