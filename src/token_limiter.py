"""
Gerenciador de limite de tokens
Controla o tamanho das respostas da IA
"""

import logging

logger = logging.getLogger(__name__)

class TokenLimiter:
    """Gerencia limites de tokens nas respostas"""
    
    # Limites padrão (em caracteres, aproximação de tokens)
    LIMITS = {
        "short": 150,      # Resposta curta
        "medium": 500,     # Resposta média (padrão)
        "long": 2000,      # Resposta longa
        "full": 4000,      # Resposta completa
    }
    
    def __init__(self, default_limit: str = "medium"):
        """
        Inicializa o limitador
        
        default_limit: 'short', 'medium', 'long' ou 'full'
        """
        if default_limit not in self.LIMITS:
            raise ValueError(f"Limite inválido: {default_limit}")
        
        self.default_limit = default_limit
        logger.info(f"TokenLimiter inicializado (padrão: {default_limit})")
    
    def parse_flags(self, text: str) -> tuple:
        """
        Parse de flags de limite e modo no texto
        Retorna: (texto_limpo, limite, modo_privado)
        
        Exemplo: ".ia -short -private Qual eh a capital?" → ("Qual eh a capital?", "short", True)
        """
        flags = {
            "-short": "short",
            "-medium": "medium",
            "-long": "long",
            "-full": "full",
        }
        
        limit = self.default_limit
        private = False
        text_clean = text
        
        # Procurar por -private
        if "-private" in text:
            private = True
            text_clean = text_clean.replace("-private", "")
            logger.debug("Flag -private encontrada")
        
        # Procurar por limite
        for flag, limit_name in flags.items():
            if flag in text_clean:
                limit = limit_name
                text_clean = text_clean.replace(flag, "").strip()
                logger.debug(f"Flag encontrada: {flag} → limite: {limit}")
                break
        
        text_clean = text_clean.strip()
        return text_clean, limit, private
    
    def truncate(self, text: str, limit: str = None) -> str:
        """
        Trunca texto ao limite especificado
        
        text: Texto a truncar
        limit: 'short', 'medium', 'long' ou 'full' (usa padrão se None)
        """
        if limit is None:
            limit = self.default_limit
        
        if limit not in self.LIMITS:
            logger.warning(f"Limite inválido: {limit}, usando padrão")
            limit = self.default_limit
        
        max_chars = self.LIMITS[limit]
        
        if len(text) <= max_chars:
            return text
        
        # Truncar e adicionar reticências
        truncated = text[:max_chars-3] + "..."
        logger.debug(f"Texto truncado: {len(text)} → {len(truncated)} caracteres")
        
        return truncated
    
    def get_limit_chars(self, limit: str = None) -> int:
        """Retorna número de caracteres para um limite"""
        if limit is None:
            limit = self.default_limit
        
        return self.LIMITS.get(limit, self.LIMITS[self.default_limit])
    
    def get_limit_info(self) -> str:
        """Retorna informação sobre limites disponíveis"""
        lines = ["Limites de resposta disponíveis:"]
        for name, chars in self.LIMITS.items():
            lines.append(f"  -{name}: até {chars} caracteres")
        lines.append(f"\nPadrão: -{self.default_limit}")
        lines.append("\nExemplo: .ia -short Qual eh a capital?")
        
        return "\n".join(lines)
