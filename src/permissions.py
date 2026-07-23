"""
Sistema de permissoes com tratamento de erros
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

class PermissionManager:
    def __init__(self, file_path="permissions.json", owner_id=None):
        self.file_path = file_path
        self.owner_id = owner_id
        self.permissions = self.load()
    
    def load(self):
        """Carrega permissoes do arquivo com tratamento de erros"""
        if not os.path.exists(self.file_path):
            logger.info(f"Arquivo {self.file_path} nao encontrado, criando novo")
            return {"allowed_users": []}
        
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict) or "allowed_users" not in data:
                    logger.warning("Formato invalido em permissions.json, reiniciando")
                    return {"allowed_users": []}
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar {self.file_path}: {e}")
            return {"allowed_users": []}
        except OSError as e:
            logger.error(f"Erro ao ler {self.file_path}: {e}")
            return {"allowed_users": []}
    
    def save(self):
        """Salva permissoes no arquivo com tratamento de erros"""
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.permissions, f, indent=2)
            logger.debug(f"Permissoes salvas em {self.file_path}")
        except OSError as e:
            logger.exception(f"Erro ao salvar {self.file_path}")
        except Exception as e:
            logger.exception("Erro inesperado ao salvar permissoes")
    
    def add_user(self, user_id):
        """Adiciona usuario com permissao"""
        try:
            user_id = int(user_id)
            if user_id not in self.permissions["allowed_users"]:
                self.permissions["allowed_users"].append(user_id)
                self.save()
                logger.info(f"Permissao concedida para {user_id}")
                return True
            return False
        except (ValueError, TypeError) as e:
            logger.error(f"ID invalido: {e}")
            return False
    
    def remove_user(self, user_id):
        """Remove usuario com permissao"""
        try:
            user_id = int(user_id)
            if user_id in self.permissions["allowed_users"]:
                self.permissions["allowed_users"].remove(user_id)
                self.save()
                logger.info(f"Permissao removida de {user_id}")
                return True
            return False
        except (ValueError, TypeError) as e:
            logger.error(f"ID invalido: {e}")
            return False
    
    def is_allowed(self, user_id):
        """Verifica se usuario tem permissao (dono sempre tem)"""
        try:
            user_id = int(user_id)
            return user_id == self.owner_id or user_id in self.permissions["allowed_users"]
        except (ValueError, TypeError):
            return False
    
    def get_all(self):
        """Retorna lista de usuarios com permissao"""
        return self.permissions.get("allowed_users", [])
