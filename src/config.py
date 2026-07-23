"""
Configuracao e validacao do JT IA Bot
"""

import os
from dotenv import load_dotenv

def load_config():
    """Carrega e valida configuracoes do .env"""
    
    env_file = "config/.env"
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Arquivo {env_file} nao encontrado")
    
    if not load_dotenv(env_file):
        raise RuntimeError(f"Falha ao carregar {env_file}")
    
    config = {}
    
    try:
        config["API_ID"] = int(os.getenv("TELEGRAM_API_ID", "0"))
        if config["API_ID"] == 0:
            raise ValueError("TELEGRAM_API_ID nao configurado")
    except ValueError as e:
        raise ValueError(f"TELEGRAM_API_ID invalido: {e}")
    
    config["API_HASH"] = os.getenv("TELEGRAM_API_HASH", "").strip()
    if not config["API_HASH"]:
        raise ValueError("TELEGRAM_API_HASH nao configurado")
    
    config["PHONE_NUMBER"] = os.getenv("PHONE_NUMBER", "").strip()
    if not config["PHONE_NUMBER"]:
        raise ValueError("PHONE_NUMBER nao configurado")
    
    try:
        config["OWNER_ID"] = int(os.getenv("OWNER_ID", "0"))
        if config["OWNER_ID"] == 0:
            raise ValueError("OWNER_ID nao configurado")
    except ValueError as e:
        raise ValueError(f"OWNER_ID invalido: {e}")
    
    config["PASSWORD_2FA"] = os.getenv("PASSWORD_2FA", "").strip()
    config["MANUS_API_URL"] = os.getenv("MANUS_API_URL", "https://api.manus.im").strip()
    config["MANUS_API_KEY"] = os.getenv("MANUS_API_KEY", "").strip()
    
    return config

def validate_config(config):
    """Valida a configuracao carregada"""
    required = ["API_ID", "API_HASH", "PHONE_NUMBER", "OWNER_ID"]
    
    for key in required:
        if key not in config or not config[key]:
            raise ValueError(f"Configuracao obrigatoria ausente: {key}")
    
    if config["API_ID"] <= 0:
        raise ValueError("API_ID deve ser um numero positivo")
    
    if config["OWNER_ID"] <= 0:
        raise ValueError("OWNER_ID deve ser um numero positivo")
    
    return True
