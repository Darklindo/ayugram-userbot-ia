"""
Gerenciador de histórico de conversa
Mantém contexto das últimas mensagens para melhor qualidade de resposta
"""

import logging
from collections import deque
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class HistoryManager:
    """Gerencia histórico de mensagens por chat"""
    
    def __init__(self, max_messages: int = 5):
        """
        Inicializa o gerenciador
        
        max_messages: Número máximo de mensagens a manter por chat
        """
        self.max_messages = max_messages
        self.history: Dict[int, deque] = {}  # {chat_id: deque de mensagens}
        logger.info(f"HistoryManager inicializado (max {max_messages} mensagens por chat)")
    
    def add_message(self, chat_id: int, sender: str, text: str):
        """Adiciona mensagem ao histórico"""
        if chat_id not in self.history:
            self.history[chat_id] = deque(maxlen=self.max_messages)
        
        self.history[chat_id].append({
            "sender": sender,
            "text": text[:200]  # Limitar tamanho de cada mensagem
        })
        
        logger.debug(f"Mensagem adicionada ao histórico do chat {chat_id}")
    
    def get_context(self, chat_id: int) -> str:
        """Retorna contexto das últimas mensagens"""
        if chat_id not in self.history or len(self.history[chat_id]) == 0:
            return ""
        
        context_lines = []
        for msg in self.history[chat_id]:
            context_lines.append(f"{msg['sender']}: {msg['text']}")
        
        context = "\n".join(context_lines)
        logger.debug(f"Contexto retornado para chat {chat_id}: {len(context)} caracteres")
        return context
    
    def clear_chat(self, chat_id: int):
        """Limpa histórico de um chat"""
        if chat_id in self.history:
            self.history[chat_id].clear()
            logger.info(f"Histórico do chat {chat_id} limpo")
    
    def clear_all(self):
        """Limpa todo o histórico"""
        self.history.clear()
        logger.info("Histórico completo limpo")
    
    def get_stats(self, chat_id: int) -> Dict:
        """Retorna estatísticas do chat"""
        if chat_id not in self.history:
            return {"messages": 0, "senders": []}
        
        messages = list(self.history[chat_id])
        senders = list(set(msg["sender"] for msg in messages))
        
        return {
            "messages": len(messages),
            "senders": senders,
            "max_messages": self.max_messages
        }
