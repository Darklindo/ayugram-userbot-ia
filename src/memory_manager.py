"""
Gerenciador de Memória
Salva e recupera informações sobre pessoas
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Gerencia memória do bot
    Salva informações sobre pessoas e contexto
    """
    
    def __init__(self, memory_file: str = "bot_memory.json"):
        """
        Inicializa o gerenciador de memória
        
        memory_file: Arquivo JSON para salvar memória
        """
        self.memory_file = memory_file
        self.memory: Dict = {}
        self.load_memory()
        logger.info(f"MemoryManager inicializado ({len(self.memory)} pessoas na memória)")
    
    def load_memory(self):
        """Carrega memória do arquivo"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info(f"Memória carregada: {len(self.memory)} entradas")
            else:
                self.memory = {}
                logger.info("Arquivo de memória não encontrado, criando novo")
        except Exception as e:
            logger.exception(f"Erro ao carregar memória: {e}")
            self.memory = {}
    
    def save_memory(self):
        """Salva memória no arquivo"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            logger.debug(f"Memória salva: {len(self.memory)} entradas")
        except Exception as e:
            logger.exception(f"Erro ao salvar memória: {e}")
    
    def add_memory(self, person_id: str, info: str, source: str = "manual") -> bool:
        """
        Adiciona informação sobre uma pessoa
        
        person_id: ID ou nome da pessoa
        info: Informação a adicionar
        source: Fonte da informação (manual, auto)
        """
        try:
            if person_id not in self.memory:
                self.memory[person_id] = {
                    "infos": [],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
            # Evitar duplicatas
            if info not in [i["text"] for i in self.memory[person_id]["infos"]]:
                self.memory[person_id]["infos"].append({
                    "text": info,
                    "source": source,
                    "added_at": datetime.now().isoformat()
                })
                self.memory[person_id]["updated_at"] = datetime.now().isoformat()
                self.save_memory()
                logger.info(f"Memória adicionada para {person_id}: {info}")
                return True
            else:
                logger.debug(f"Informação duplicada para {person_id}")
                return False
        except Exception as e:
            logger.exception(f"Erro ao adicionar memória: {e}")
            return False
    
    def get_memory(self, person_id: str) -> Optional[Dict]:
        """
        Retorna informações sobre uma pessoa
        
        person_id: ID ou nome da pessoa
        """
        return self.memory.get(person_id)
    
    def get_memory_text(self, person_id: str) -> str:
        """
        Retorna informações formatadas sobre uma pessoa
        """
        mem = self.get_memory(person_id)
        if not mem:
            return ""
        
        infos = [i["text"] for i in mem["infos"]]
        return "\n".join(infos)
    
    def list_memory(self) -> str:
        """Lista todas as pessoas na memória"""
        if not self.memory:
            return "Memória vazia"
        
        lines = ["📚 Memória do Bot:\n"]
        for person_id, data in self.memory.items():
            infos_count = len(data["infos"])
            lines.append(f"👤 {person_id} ({infos_count} info{'s' if infos_count != 1 else ''})")
            for info in data["infos"]:
                lines.append(f"  • {info['text']}")
        
        return "\n".join(lines)
    
    def clear_memory(self, person_id: str) -> bool:
        """Remove todas as informações sobre uma pessoa"""
        try:
            if person_id in self.memory:
                del self.memory[person_id]
                self.save_memory()
                logger.info(f"Memória limpa para {person_id}")
                return True
            else:
                logger.warning(f"Pessoa {person_id} não encontrada na memória")
                return False
        except Exception as e:
            logger.exception(f"Erro ao limpar memória: {e}")
            return False
    
    def extract_person_info(self, text: str) -> Optional[tuple]:
        """
        Extrai automaticamente informações sobre pessoas do texto
        Procura por padrões como "X é Y", "X é um/uma Y"
        
        Retorna: (person_id, info) ou None
        """
        try:
            # Padrões: "X é Y", "X é um/uma Y", "X é tipo Y"
            patterns = [
                r'(\w+(?:\s+\w+)?)\s+é\s+(.+?)(?:\.|,|$)',  # "X é Y"
                r'(\w+(?:\s+\w+)?)\s+é\s+um(?:a)?\s+(.+?)(?:\.|,|$)',  # "X é um Y"
                r'(\w+(?:\s+\w+)?)\s+é\s+tipo\s+(.+?)(?:\.|,|$)',  # "X é tipo Y"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    person = match.group(1).strip()
                    info = match.group(2).strip()
                    
                    # Filtrar informações muito curtas ou genéricas
                    if len(info) > 3 and len(person) > 2:
                        return (person, info)
            
            return None
        except Exception as e:
            logger.debug(f"Erro ao extrair info: {e}")
            return None
    
    def get_all_memory_context(self) -> str:
        """
        Retorna TODA a memória formatada para usar no prompt
        """
        if not self.memory:
            return ""
        
        lines = ["[MEMÓRIA DO BOT:"]
        for person_id, data in self.memory.items():
            infos = [i["text"] for i in data["infos"]]
            for info in infos:
                lines.append(f"{person_id}: {info}")
        lines.append("]")
        
        return "\n".join(lines)
    
    def get_context_for_prompt(self, person_id: str) -> str:
        """
        Retorna contexto de memória para usar no prompt da IA
        """
        mem_text = self.get_memory_text(person_id)
        if mem_text:
            return f"\n[Contexto sobre {person_id}: {mem_text}]"
        return ""
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da memória"""
        total_people = len(self.memory)
        total_infos = sum(len(data["infos"]) for data in self.memory.values())
        
        return {
            "total_people": total_people,
            "total_infos": total_infos,
            "file": self.memory_file
        }
