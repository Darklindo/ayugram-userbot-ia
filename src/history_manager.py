"""
Gerenciador de histórico de conversa com suporte a LRU cache
Mantém contexto das últimas mensagens por usuário em cada chat
"""

import logging
import asyncio
from collections import deque, OrderedDict
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HistoryManager:
    """
    Gerencia histórico de mensagens por (chat_id, sender_id)
    Implementa LRU cache com limpeza automática de chats inativos
    """
    
    def __init__(self, max_messages: int = 5, max_chats: int = 100, ttl_minutes: int = 60):
        """
        Inicializa o gerenciador com LRU cache
        
        max_messages: Número máximo de mensagens a manter por (chat_id, sender_id)
        max_chats: Número máximo de chats a manter em memória (LRU)
        ttl_minutes: Tempo de vida em minutos antes de limpar um chat inativo
        """
        self.max_messages = max_messages
        self.max_chats = max_chats
        self.ttl_minutes = ttl_minutes
        
        # Usar OrderedDict para LRU: {(chat_id, sender_id): {"messages": deque, "last_access": datetime}}
        self.history: OrderedDict = OrderedDict()
        self.lock = asyncio.Lock()
        
        logger.info(
            f"HistoryManager inicializado (max {max_messages} msgs/conversa, "
            f"{max_chats} chats, TTL {ttl_minutes}min)"
        )
    
    async def add_message(self, chat_id: int, sender_id: int, sender_name: str, text: str):
        """
        Adiciona mensagem ao histórico com thread-safety
        Usa (chat_id, sender_id) como chave para evitar mistura de contextos
        """
        async with self.lock:
            key = (chat_id, sender_id)
            
            # Criar entrada se não existir
            if key not in self.history:
                self.history[key] = {
                    "messages": deque(maxlen=self.max_messages),
                    "last_access": datetime.now(),
                    "sender_name": sender_name
                }
            
            # Adicionar mensagem (deque automaticamente remove a mais antiga se necessário)
            self.history[key]["messages"].append({
                "sender": sender_name,
                "text": text[:200],  # Limitar tamanho
                "timestamp": datetime.now()
            })
            
            # Atualizar last_access para LRU
            self.history[key]["last_access"] = datetime.now()
            
            # Mover para o final (mais recente)
            self.history.move_to_end(key)
            
            # Limpar chats inativos se exceder limite
            if len(self.history) > self.max_chats:
                await self._cleanup_inactive_chats()
            
            logger.debug(
                f"Mensagem adicionada ao histórico de {chat_id}/{sender_id} "
                f"({len(self.history[key]['messages'])} mensagens)"
            )
    
    async def get_context(self, chat_id: int, sender_id: int) -> str:
        """
        Retorna contexto das últimas mensagens para um (chat_id, sender_id)
        Apenas o próprio usuário vê seu contexto
        """
        async with self.lock:
            key = (chat_id, sender_id)
            
            if key not in self.history or len(self.history[key]["messages"]) == 0:
                return ""
            
            # Atualizar last_access
            self.history[key]["last_access"] = datetime.now()
            self.history.move_to_end(key)
            
            context_lines = []
            for msg in self.history[key]["messages"]:
                context_lines.append(f"{msg['sender']}: {msg['text']}")
            
            context = "\n".join(context_lines)
            logger.debug(
                f"Contexto retornado para {chat_id}/{sender_id}: {len(context)} caracteres"
            )
            return context
    
    async def clear_conversation(self, chat_id: int, sender_id: int):
        """Limpa histórico de uma conversa específica (chat_id, sender_id)"""
        async with self.lock:
            key = (chat_id, sender_id)
            if key in self.history:
                del self.history[key]
                logger.info(f"Histórico da conversa {chat_id}/{sender_id} limpo")
    
    async def clear_chat(self, chat_id: int):
        """Limpa histórico de TODOS os usuários em um chat"""
        async with self.lock:
            keys_to_delete = [key for key in self.history if key[0] == chat_id]
            for key in keys_to_delete:
                del self.history[key]
            logger.info(f"Histórico de todos os usuários no chat {chat_id} limpo ({len(keys_to_delete)} conversas)")
    
    async def clear_all(self):
        """Limpa todo o histórico"""
        async with self.lock:
            self.history.clear()
            logger.info("Histórico completo limpo")
    
    async def _cleanup_inactive_chats(self):
        """
        Remove chats inativos por mais de TTL
        Chamado automaticamente quando excede max_chats
        """
        now = datetime.now()
        ttl = timedelta(minutes=self.ttl_minutes)
        
        keys_to_delete = []
        for key, data in self.history.items():
            if now - data["last_access"] > ttl:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.history[key]
        
        if keys_to_delete:
            logger.info(f"Limpeza automática: {len(keys_to_delete)} chats inativos removidos")
    
    async def get_stats(self, chat_id: int = None) -> Dict:
        """
        Retorna estatísticas do histórico
        Se chat_id for None, retorna estatísticas globais
        """
        async with self.lock:
            if chat_id is None:
                # Estatísticas globais
                total_conversations = len(self.history)
                total_messages = sum(
                    len(data["messages"]) for data in self.history.values()
                )
                return {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "max_chats": self.max_chats,
                    "max_messages_per_conversation": self.max_messages,
                    "memory_usage_mb": total_messages * 0.0002  # Estimativa aproximada
                }
            else:
                # Estatísticas de um chat específico
                conversations = [
                    (key, len(data["messages"])) 
                    for key, data in self.history.items() 
                    if key[0] == chat_id
                ]
                total_messages = sum(count for _, count in conversations)
                return {
                    "chat_id": chat_id,
                    "conversations": len(conversations),
                    "total_messages": total_messages,
                    "details": conversations
                }
    
    async def get_memory_usage(self) -> Dict:
        """Retorna informações sobre uso de memória"""
        async with self.lock:
            total_conversations = len(self.history)
            total_messages = sum(
                len(data["messages"]) for data in self.history.values()
            )
            
            # Estimativa: cada mensagem ~200 chars + overhead
            estimated_mb = (total_messages * 250) / (1024 * 1024)
            
            return {
                "conversations": total_conversations,
                "messages": total_messages,
                "estimated_mb": round(estimated_mb, 2),
                "max_capacity": self.max_chats
            }
