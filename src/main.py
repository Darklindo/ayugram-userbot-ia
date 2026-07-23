#!/usr/bin/env python3
"""
Ayugram UserBot com IA Integrada
Sistema avançado com permissões, IA e automações
"""

import os
import json
import asyncio
import getpass
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from telethon.errors import SessionPasswordNeededError
import aiohttp
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv("config/.env")

# Configurações
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")
PASSWORD_2FA = os.getenv("PASSWORD_2FA", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
MANUS_API_URL = os.getenv("MANUS_API_URL", "https://api.manus.im")
MANUS_API_KEY = os.getenv("MANUS_API_KEY", "")

# Arquivo de permissões
PERMS_FILE = "permissions.json"

# Inicializar cliente
client = TelegramClient("ayugram_session", API_ID, API_HASH)

# Sistema de permissões
class PermissionManager:
    def __init__(self, file_path=PERMS_FILE):
        self.file_path = file_path
        self.permissions = self.load()
    
    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {"allowed_users": []}
    
    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.permissions, f, indent=2)
    
    def add_user(self, user_id):
        if user_id not in self.permissions["allowed_users"]:
            self.permissions["allowed_users"].append(user_id)
            self.save()
            return True
        return False
    
    def remove_user(self, user_id):
        if user_id in self.permissions["allowed_users"]:
            self.permissions["allowed_users"].remove(user_id)
            self.save()
            return True
        return False
    
    def is_allowed(self, user_id):
        return user_id in self.permissions["allowed_users"]
    
    def get_all(self):
        return self.permissions["allowed_users"]

perm_manager = PermissionManager()

# Sistema de IA
class IAManager:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
    
    async def process(self, prompt):
        """Processa uma mensagem com IA"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "model": "gpt-4",
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/v1/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("choices", [{}])[0].get("text", "Erro ao processar")
                    else:
                        return f"Erro {resp.status}: Nao consegui processar sua mensagem"
        except Exception as e:
            return f"Erro: {str(e)}"

ia_manager = IAManager(MANUS_API_URL, MANUS_API_KEY)

# Funcao de autenticacao melhorada para Termux
async def authenticate_client():
    """Autentica o cliente com suporte a 2FA e getpass"""
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print(f"[*] Enviando codigo para {PHONE_NUMBER}...")
            await client.send_code_request(PHONE_NUMBER)
            
            # Usar getpass para ler o codigo (funciona melhor no Termux)
            try:
                code = getpass.getpass("[*] Digite o codigo: ")
            except:
                code = input("[*] Digite o codigo: ")
            
            try:
                await client.sign_in(PHONE_NUMBER, code)
                print("[+] Conectado com sucesso!")
            except SessionPasswordNeededError:
                # Se tiver 2FA, usa a senha automaticamente
                print("[*] Usando 2FA...")
                if PASSWORD_2FA:
                    await client.sign_in(password=PASSWORD_2FA)
                    print("[+] Conectado com 2FA!")
                else:
                    try:
                        password = getpass.getpass("[*] Digite sua senha 2FA: ")
                    except:
                        password = input("[*] Digite sua senha 2FA: ")
                    await client.sign_in(password=password)
                    print("[+] Conectado com 2FA!")
        
        me = await client.get_me()
        print(f"[+] Conectado como: {me.first_name}")
        return True
    except Exception as e:
        print(f"[-] Erro na autenticacao: {e}")
        return False

# Handlers de comandos
@client.on(events.NewMessage(pattern=r"\.perm"))
async def handle_perm(event):
    """Comando para gerenciar permissoes"""
    if event.is_private:
        sender = await event.get_sender()
        
        # Apenas o dono pode usar
        if sender.id != OWNER_ID:
            await event.reply("[-] Voce nao tem permissao para usar este comando")
            return
        
        try:
            args = event.raw_text.split()
            if len(args) < 2:
                msg = "[*] Uso: `.perm (id)` ou `.perm list`\n\n"
                msg += "Exemplos:\n"
                msg += "`.perm 123456789` - Dar permissao\n"
                msg += "`.perm list` - Listar permissoes"
                await event.reply(msg)
                return
            
            if args[1].lower() == "list":
                users = perm_manager.get_all()
                if not users:
                    await event.reply("[*] Nenhum usuario com permissao")
                else:
                    msg = "[+] Usuarios com Permissao:\n"
                    for uid in users:
                        msg += f"• {uid}\n"
                    await event.reply(msg)
            else:
                user_id = int(args[1])
                if perm_manager.add_user(user_id):
                    await event.reply(f"[+] Permissao concedida para {user_id}")
                else:
                    await event.reply(f"[!] Usuario {user_id} ja tem permissao")
        except Exception as e:
            await event.reply(f"[-] Erro: {str(e)}")

@client.on(events.NewMessage(pattern=r"\.ia"))
async def handle_ia(event):
    """Comando para usar IA"""
    sender = await event.get_sender()
    
    # Verificar permissao
    if not perm_manager.is_allowed(sender.id):
        await event.reply("[-] Voce nao tem permissao para usar IA. Peça ao dono com `.perm`")
        return
    
    # Extrair prompt
    prompt = event.raw_text.replace(".ia", "").strip()
    
    if not prompt:
        await event.reply("[*] Uso: `.ia [sua pergunta]`\n\nExemplo: `.ia Qual eh a capital do Brasil?`")
        return
    
    # Mostrar que esta processando
    processing_msg = await event.reply("[*] Processando sua pergunta...")
    
    # Processar com IA
    response = await ia_manager.process(prompt)
    
    # Editar mensagem com resposta
    await processing_msg.edit(f"[+] Resposta:\n\n{response}")

@client.on(events.NewMessage(pattern=r"\.help"))
async def handle_help(event):
    """Comando de ajuda"""
    help_text = """
[*] Ayugram UserBot com IA

[+] Comandos Disponiveis:

Permissoes:
`.perm (id)` - Dar permissao para usar IA
`.perm list` - Listar usuarios com permissao

IA:
`.ia [pergunta]` - Fazer uma pergunta para a IA

Informacoes:
`.help` - Mostrar este menu
`.status` - Status do bot

Exemplo de uso:
.ia Qual eh a capital do Brasil?
.perm 123456789
.perm list

[!] Apenas usuarios com permissao podem usar `.ia`
"""
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"\.status"))
async def handle_status(event):
    """Status do bot"""
    sender = await event.get_sender()
    
    status_text = f"""
[+] Status do Bot

Usuario: {sender.first_name}
ID: {sender.id}
Permissao IA: {'SIM' if perm_manager.is_allowed(sender.id) else 'NAO'}
Horario: {datetime.now().strftime('%H:%M:%S')}
Zona: Brazil/Sao Paulo
"""
    await event.reply(status_text)

async def main():
    """Funcao principal"""
    print("[*] Iniciando Ayugram UserBot com IA...")
    
    # Verificar configuracoes
    if not API_ID or not API_HASH:
        print("[-] Erro: Configure TELEGRAM_API_ID e TELEGRAM_API_HASH")
        return
    
    if not PHONE_NUMBER:
        print("[-] Erro: Configure PHONE_NUMBER")
        return
    
    if not MANUS_API_KEY:
        print("[!] Aviso: MANUS_API_KEY nao configurada. IA pode nao funcionar")
    
    # Autenticar
    if not await authenticate_client():
        print("[-] Falha na autenticacao")
        return
    
    print(f"[+] Bot conectado com sucesso!")
    print(f"[+] Usuarios com permissao: {len(perm_manager.get_all())}")
    print("\n[*] Bot aguardando comandos...")
    print("[*] Comandos: .ia, .perm, .help, .status")
    
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n[*] Bot desconectado")
    except Exception as e:
        print(f"[-] Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
