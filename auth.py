#!/usr/bin/env python3
"""
Script de Autenticacao Separado para Termux
Use este script UMA VEZ para fazer login
Depois rode o bot normalmente
"""

import os
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

# Carregar .env
load_dotenv("config/.env")

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")
PASSWORD_2FA = os.getenv("PASSWORD_2FA", "")

async def authenticate():
    """Faz autenticacao interativa"""
    
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("[-] Configure TELEGRAM_API_ID, TELEGRAM_API_HASH e PHONE_NUMBER no .env")
        return False
    
    client = TelegramClient("ayugram_session", API_ID, API_HASH)
    
    try:
        await client.connect()
        print("[*] Conectado ao Telegram")
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"[+] Ja autenticado como: {me.first_name}")
            await client.disconnect()
            return True
        
        print(f"[*] Enviando codigo para {PHONE_NUMBER}...")
        await client.send_code_request(PHONE_NUMBER)
        
        # Ler codigo do arquivo ou entrada
        code_file = "verification_code.txt"
        
        if os.path.exists(code_file):
            print(f"[*] Lendo codigo de {code_file}...")
            with open(code_file, "r") as f:
                code = f.read().strip()
            os.remove(code_file)
            print(f"[*] Codigo lido: {code}")
        else:
            print(f"\n[!] METODO 1: Digite o codigo aqui")
            code = input("[*] Codigo: ").strip()
        
        try:
            await client.sign_in(PHONE_NUMBER, code)
            me = await client.get_me()
            print(f"[+] Autenticado com sucesso como: {me.first_name}")
            await client.disconnect()
            return True
        
        except SessionPasswordNeededError:
            print("[*] 2FA detectado")
            
            if PASSWORD_2FA:
                print("[*] Usando senha do .env...")
                await client.sign_in(password=PASSWORD_2FA)
            else:
                password_file = "2fa_password.txt"
                if os.path.exists(password_file):
                    print(f"[*] Lendo senha de {password_file}...")
                    with open(password_file, "r") as f:
                        password = f.read().strip()
                    os.remove(password_file)
                else:
                    password = input("[*] Senha 2FA: ").strip()
                
                await client.sign_in(password=password)
            
            me = await client.get_me()
            print(f"[+] Autenticado com 2FA como: {me.first_name}")
            await client.disconnect()
            return True
    
    except Exception as e:
        print(f"[-] Erro: {e}")
        await client.disconnect()
        return False

if __name__ == "__main__":
    print("""
[*] Ayugram - Script de Autenticacao
[*] Este script faz login UMA VEZ
[*] Depois o bot roda automaticamente

[!] OPCOES:
1. Digite o codigo aqui
2. Crie um arquivo 'verification_code.txt' com o codigo
3. Para 2FA, crie '2fa_password.txt' com a senha

""")
    
    success = asyncio.run(authenticate())
    
    if success:
        print("\n[+] Autenticacao concluida!")
        print("[*] Agora rode: python3 src/main.py")
        sys.exit(0)
    else:
        print("\n[-] Falha na autenticacao")
        sys.exit(1)
