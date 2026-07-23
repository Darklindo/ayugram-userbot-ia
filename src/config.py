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
        config["API_ID"] = int(os.getenv("API_ID", "0"))
        if config["API_ID"] == 0:
            raise ValueError("API_ID nao configurado")
    except ValueError as e:
        raise ValueError(f"API_ID invalido: {e}")
    
    config["API_HASH"] = os.getenv("API_HASH", "").strip()
    if not config["API_HASH"]:
        raise ValueError("API_HASH nao configurado")
    
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
    
    # Provider padrao de IA
    config["AI_PROVIDER"] = os.getenv("AI_PROVIDER", "deepseek").strip().lower()
    if config["AI_PROVIDER"] not in ["gemini", "deepseek", "openai"]:
        raise ValueError(f"AI_PROVIDER invalido: {config['AI_PROVIDER']}. Use 'gemini', 'deepseek' ou 'openai'")
    
    # Chaves de API para cada provider
    config["AI_KEYS"] = {}
    
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        config["AI_KEYS"]["gemini"] = gemini_key
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if deepseek_key:
        config["AI_KEYS"]["deepseek"] = deepseek_key
    
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        config["AI_KEYS"]["openai"] = openai_key
    
    # Validar se o provider padrao tem chave
    if config["AI_PROVIDER"] not in config["AI_KEYS"]:
        raise ValueError(f"Chave de API nao configurada para {config['AI_PROVIDER']}")
    
    return config

def validate_config(config):
    """Valida a configuracao carregada"""
    required = ["API_ID", "API_HASH", "PHONE_NUMBER", "OWNER_ID", "AI_PROVIDER", "AI_KEYS"]
    
    for key in required:
        if key not in config or not config[key]:
            raise ValueError(f"Configuracao obrigatoria ausente: {key}")
    
    if config["API_ID"] <= 0:
        raise ValueError("API_ID deve ser um numero positivo")
    
    if config["OWNER_ID"] <= 0:
        raise ValueError("OWNER_ID deve ser um numero positivo")
    
    if not config["AI_KEYS"]:
        raise ValueError("Nenhuma chave de API configurada")
    
    return True
