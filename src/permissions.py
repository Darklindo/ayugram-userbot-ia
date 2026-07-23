"""
Sistema de permissões com thread-safety
Usa asyncio.Lock para evitar race conditions
"""

import os
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class PermissionManager:
    """
    Gerencia permissões de usuários com thread-safety
    Suporta operações concorrentes com asyncio.Lock
    """
    
    def __init__(self, file_path="permissions.json", owner_id=None):
        self.file_path = file_path
        self.owner_id = owner_id
        self.permissions = self._load_sync()
        self.lock = asyncio.Lock()
        logger.info(f"PermissionManager inicializado com lock (dono: {owner_id})")
    
    def _load_sync(self):
        """Carrega permissões do arquivo (versão síncrona para __init__)"""
        if not os.path.exists(self.file_path):
            logger.info(f"Arquivo {self.file_path} não encontrado, criando novo")
            return {"allowed_users": [], "banned_users": []}
        
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict) or "allowed_users" not in data:
                    logger.warning("Formato inválido em permissions.json, reiniciando")
                    return {"allowed_users": [], "banned_users": []}
                # Garantir que banned_users existe
                if "banned_users" not in data:
                    data["banned_users"] = []
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar {self.file_path}: {e}")
            return {"allowed_users": [], "banned_users": []}
        except OSError as e:
            logger.error(f"Erro ao ler {self.file_path}: {e}")
            return {"allowed_users": [], "banned_users": []}
    
    def _save_sync(self):
        """Salva permissões no arquivo (versão síncrona)"""
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.permissions, f, indent=2)
            logger.debug(f"Permissões salvas em {self.file_path}")
        except OSError as e:
            logger.exception(f"Erro ao salvar {self.file_path}")
        except Exception as e:
            logger.exception("Erro inesperado ao salvar permissões")
    
    async def add_user(self, user_id):
        """Adiciona usuário com permissão (thread-safe)"""
        async with self.lock:
            try:
                user_id = int(user_id)
                if user_id not in self.permissions["allowed_users"]:
                    self.permissions["allowed_users"].append(user_id)
                    self._save_sync()
                    logger.info(f"Permissão concedida para {user_id}")
                    return True
                return False
            except (ValueError, TypeError) as e:
                logger.error(f"ID inválido: {e}")
                return False
    
    async def remove_user(self, user_id):
        """Remove usuário com permissão (thread-safe)"""
        async with self.lock:
            try:
                user_id = int(user_id)
                if user_id in self.permissions["allowed_users"]:
                    self.permissions["allowed_users"].remove(user_id)
                    self._save_sync()
                    logger.info(f"Permissão removida de {user_id}")
                    return True
                return False
            except (ValueError, TypeError) as e:
                logger.error(f"ID inválido: {e}")
                return False
    
    async def is_allowed(self, user_id):
        """Verifica se usuário tem permissão (thread-safe)"""
        async with self.lock:
            try:
                user_id = int(user_id)
                # Dono sempre tem permissão
                if user_id == self.owner_id:
                    return True
                # Usuário banido não tem permissão
                if await self._is_banned_internal(user_id):
                    return False
                return user_id in self.permissions["allowed_users"]
            except (ValueError, TypeError):
                return False
    
    async def _is_banned_internal(self, user_id):
        """Versão interna de is_banned (sem lock, para uso dentro de métodos com lock)"""
        try:
            user_id = int(user_id)
            return user_id in self.permissions.get("banned_users", [])
        except (ValueError, TypeError):
            return False
    
    async def get_all(self):
        """Retorna lista de usuários com permissão (thread-safe)"""
        async with self.lock:
            return self.permissions.get("allowed_users", []).copy()
    
    async def ban_user(self, user_id):
        """Bane um usuário (thread-safe)"""
        async with self.lock:
            try:
                user_id = int(user_id)
                if user_id == self.owner_id:
                    logger.warning(f"Tentativa de banir o dono: {user_id}")
                    return False
                
                if user_id not in self.permissions.get("banned_users", []):
                    self.permissions["banned_users"].append(user_id)
                    self._save_sync()
                    logger.info(f"Usuário banido: {user_id}")
                    return True
                return False
            except (ValueError, TypeError) as e:
                logger.error(f"ID inválido: {e}")
                return False
    
    async def unban_user(self, user_id):
        """Remove banimento de um usuário (thread-safe)"""
        async with self.lock:
            try:
                user_id = int(user_id)
                if user_id in self.permissions.get("banned_users", []):
                    self.permissions["banned_users"].remove(user_id)
                    self._save_sync()
                    logger.info(f"Banimento removido de {user_id}")
                    return True
                return False
            except (ValueError, TypeError) as e:
                logger.error(f"ID inválido: {e}")
                return False
    
    async def is_banned(self, user_id):
        """Verifica se usuário está banido (thread-safe)"""
        async with self.lock:
            return await self._is_banned_internal(user_id)
    
    async def get_banned(self):
        """Retorna lista de usuários banidos (thread-safe)"""
        async with self.lock:
            return self.permissions.get("banned_users", []).copy()
