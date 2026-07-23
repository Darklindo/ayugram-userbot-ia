"""
Tradutor para português usando Google Translate API
Traduz resultados de busca do inglês para português
"""

import logging
import asyncio

logger = logging.getLogger(__name__)

try:
    from google_trans_new import google_translator
    TRANSLATOR = google_translator()
    HAS_GOOGLE_TRANSLATE = True
except ImportError:
    HAS_GOOGLE_TRANSLATE = False
    logger.warning("google_trans_new não instalado, usando fallback")


# Dicionário de traduções comuns como fallback
TRANSLATIONS = {
    "the": "o", "a": "um", "an": "um", "and": "e", "or": "ou",
    "in": "em", "on": "em", "at": "em", "to": "para", "from": "de",
    "with": "com", "by": "por", "for": "para", "of": "de",
    "is": "é", "are": "são", "was": "foi", "were": "foram",
    "be": "ser", "been": "sido", "being": "sendo",
    "about": "sobre", "search": "busca", "result": "resultado",
    "results": "resultados", "wikipedia": "wikipedia",
    "definition": "definição", "meaning": "significado",
    "information": "informação", "page": "página", "website": "site",
    "link": "link", "article": "artigo", "news": "notícias",
    "image": "imagem", "video": "vídeo", "description": "descrição",
    "summary": "resumo", "more": "mais", "less": "menos",
    "see": "ver", "view": "visualizar", "read": "ler",
    "click": "clique", "here": "aqui", "there": "lá",
    "all": "tudo", "some": "alguns", "any": "qualquer",
    "other": "outro", "another": "outro", "such": "tal",
    "same": "mesmo", "different": "diferente", "new": "novo",
    "old": "velho", "good": "bom", "bad": "ruim", "best": "melhor",
    "worst": "pior", "first": "primeiro", "last": "último",
    "next": "próximo", "previous": "anterior", "high": "alto",
    "low": "baixo", "big": "grande", "small": "pequeno",
    "long": "longo", "short": "curto", "fast": "rápido",
    "slow": "lento", "easy": "fácil", "hard": "difícil",
    "important": "importante", "famous": "famoso", "popular": "popular",
    "common": "comum", "rare": "raro", "special": "especial",
    "general": "geral", "specific": "específico", "public": "público",
    "private": "privado", "official": "oficial", "free": "grátis",
    "paid": "pago", "available": "disponível", "online": "online",
    "offline": "offline", "active": "ativo", "inactive": "inativo",
    "open": "aberto", "closed": "fechado", "start": "começar",
    "end": "fim", "begin": "começar", "finish": "terminar",
    "continue": "continuar", "stop": "parar", "go": "ir",
    "come": "vir", "get": "obter", "make": "fazer", "take": "pegar",
    "give": "dar", "find": "encontrar", "lose": "perder",
    "keep": "manter", "leave": "sair", "stay": "ficar",
    "move": "mover", "change": "mudar", "turn": "virar",
    "use": "usar", "work": "trabalhar", "play": "jogar",
    "watch": "assistir", "listen": "ouvir", "speak": "falar",
    "talk": "conversar", "write": "escrever", "type": "digitar",
    "print": "imprimir", "copy": "copiar", "paste": "colar",
    "delete": "deletar", "create": "criar", "edit": "editar",
    "save": "salvar", "load": "carregar", "download": "baixar",
    "upload": "enviar", "share": "compartilhar", "like": "gostar",
    "love": "amar", "hate": "odiar", "enjoy": "aproveitar",
    "learn": "aprender", "teach": "ensinar", "know": "saber",
    "understand": "entender", "think": "pensar", "believe": "acreditar",
    "hope": "esperar", "want": "querer", "need": "precisar",
    "should": "deveria", "could": "poderia", "would": "seria",
    "can": "pode", "may": "pode", "must": "deve", "will": "vai",
    "do": "fazer", "does": "faz", "did": "fez", "have": "ter",
    "has": "tem", "had": "teve", "as": "como", "if": "se",
    "not": "não", "no": "não", "yes": "sim", "but": "mas",
    "this": "isto", "that": "aquilo", "these": "estes",
    "those": "aqueles", "which": "qual", "who": "quem",
    "what": "o que", "where": "onde", "when": "quando",
    "why": "por que", "how": "como",
}


def translate_text_fallback(text: str) -> str:
    """Traduz usando dicionário como fallback"""
    if not text:
        return text
    
    import re
    translated = text
    
    for en_word, pt_word in TRANSLATIONS.items():
        pattern = r'\b' + re.escape(en_word) + r'\b'
        translated = re.sub(pattern, pt_word, translated, flags=re.IGNORECASE)
    
    return translated


async def translate_text(text: str) -> str:
    """Traduz texto do inglês para português"""
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        if HAS_GOOGLE_TRANSLATE:
            # Usar Google Translate se disponível
            result = await asyncio.to_thread(
                TRANSLATOR.translate,
                text,
                lang_src='en',
                lang_tgt='pt'
            )
            return result if result else text
    except Exception as e:
        logger.warning(f"Erro ao traduzir com Google: {e}")
    
    # Fallback para dicionário
    return translate_text_fallback(text)


async def translate_search_result(result: str) -> str:
    """Traduz resultado de busca mantendo estrutura"""
    if not result:
        return result
    
    lines = result.split('\n')
    translated_lines = []
    
    for line in lines:
        # Não traduzir linhas vazias ou com apenas emojis
        if not line.strip() or line.strip() in ('📌', '•', '-', '*'):
            translated_lines.append(line)
            continue
        
        # Traduzir a linha
        translated_line = await translate_text(line)
        translated_lines.append(translated_line)
    
    return '\n'.join(translated_lines)


def translate_query(query: str) -> str:
    """Traduz query de português para inglês (se necessário)"""
    if not query:
        return query
    
    # Dicionário reverso
    pt_to_en = {v: k for k, v in TRANSLATIONS.items()}
    
    translated = query
    import re
    
    for pt_word, en_word in pt_to_en.items():
        pattern = r'\b' + re.escape(pt_word) + r'\b'
        translated = re.sub(pattern, en_word, translated, flags=re.IGNORECASE)
    
    return translated
