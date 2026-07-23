"""
Gerenciador de Personas
Permite customizar a personalidade e estilo de resposta da IA
"""

import logging
import json
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PersonasManager:
    """Gerencia personas customizáveis para a IA"""
    
    # Personas pré-definidas
    DEFAULT_PERSONAS = {
        "normal": {
            "name": "Normal",
            "prompt": "Responda de forma clara e objetiva.",
            "emoji": "🤖"
        },
        "dev": {
            "name": "Dev",
            "prompt": "Você é um desenvolvedor experiente. Responda com foco em código, arquitetura e boas práticas.",
            "emoji": "👨‍💻"
        },
        "professor": {
            "name": "Professor",
            "prompt": "Você é um professor paciente. Explique de forma didática, com exemplos e analogias.",
            "emoji": "👨‍🏫"
        },
        "piada": {
            "name": "Piada",
            "prompt": "Você é um comediante. Responda com humor e piadas sempre que possível.",
            "emoji": "🤣"
        },
        "poeta": {
            "name": "Poeta",
            "prompt": "Você é um poeta. Responda de forma lírica e poética.",
            "emoji": "✍️"
        },
        "cientista": {
            "name": "Cientista",
            "prompt": "Você é um cientista. Responda com rigor científico, dados e referências.",
            "emoji": "🔬"
        },
    }
    
    def __init__(self, personas_file: str = "personas.json"):
        """Inicializa o gerenciador de personas"""
        self.personas_file = personas_file
        self.personas = self._load_personas()
        self.current_persona = "normal"
        logger.info(f"PersonasManager inicializado com {len(self.personas)} personas")
    
    def _load_personas(self) -> Dict:
        """Carrega personas customizadas do arquivo"""
        personas = self.DEFAULT_PERSONAS.copy()
        
        if os.path.exists(self.personas_file):
            try:
                with open(self.personas_file, "r") as f:
                    custom = json.load(f)
                    personas.update(custom)
                    logger.info(f"Personas customizadas carregadas: {len(custom)}")
            except Exception as e:
                logger.warning(f"Erro ao carregar personas customizadas: {e}")
        
        return personas
    
    def _save_personas(self):
        """Salva personas customizadas em arquivo"""
        # Salva apenas as customizadas (não as padrões)
        custom = {k: v for k, v in self.personas.items() 
                  if k not in self.DEFAULT_PERSONAS}
        
        try:
            with open(self.personas_file, "w") as f:
                json.dump(custom, f, indent=2, ensure_ascii=False)
            logger.debug("Personas customizadas salvas")
        except Exception as e:
            logger.exception("Erro ao salvar personas")
    
    def get_current_persona(self) -> str:
        """Retorna a persona atual"""
        return self.current_persona
    
    def set_persona(self, persona_name: str) -> bool:
        """Define a persona atual"""
        if persona_name not in self.personas:
            logger.warning(f"Persona desconhecida: {persona_name}")
            return False
        
        self.current_persona = persona_name
        logger.info(f"Persona alterada para: {persona_name}")
        return True
    
    def get_prompt_prefix(self) -> str:
        """Retorna o prefixo de prompt para a persona atual"""
        persona = self.personas.get(self.current_persona, self.personas["normal"])
        return persona.get("prompt", "")
    
    def get_persona_emoji(self) -> str:
        """Retorna o emoji da persona atual"""
        persona = self.personas.get(self.current_persona, self.personas["normal"])
        return persona.get("emoji", "🤖")
    
    def add_persona(self, name: str, prompt: str, emoji: str = "🤖") -> bool:
        """Adiciona uma persona customizada"""
        if name in self.personas:
            logger.warning(f"Persona já existe: {name}")
            return False
        
        self.personas[name] = {
            "name": name.capitalize(),
            "prompt": prompt,
            "emoji": emoji
        }
        
        self._save_personas()
        logger.info(f"Persona adicionada: {name}")
        return True
    
    def remove_persona(self, name: str) -> bool:
        """Remove uma persona customizada"""
        if name in self.DEFAULT_PERSONAS:
            logger.warning(f"Não é possível remover persona padrão: {name}")
            return False
        
        if name not in self.personas:
            logger.warning(f"Persona não encontrada: {name}")
            return False
        
        del self.personas[name]
        
        # Se era a persona atual, volta para normal
        if self.current_persona == name:
            self.current_persona = "normal"
        
        self._save_personas()
        logger.info(f"Persona removida: {name}")
        return True
    
    def list_personas(self) -> str:
        """Retorna lista formatada de personas"""
        lines = ["📋 PERSONAS DISPONÍVEIS:\n"]
        
        for name, persona in self.personas.items():
            emoji = persona.get("emoji", "🤖")
            marker = "✅" if name == self.current_persona else "  "
            lines.append(f"{marker} {emoji} {name.capitalize()}")
        
        lines.append(f"\nAtual: {self.current_persona}")
        return "\n".join(lines)
    
    def get_persona_info(self, name: str) -> Optional[Dict]:
        """Retorna informações de uma persona"""
        return self.personas.get(name)
    
    def format_with_persona(self, text: str) -> str:
        """Formata texto com a persona atual"""
        emoji = self.get_persona_emoji()
        return f"{emoji} {text}"
