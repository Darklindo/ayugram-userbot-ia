"""
Tradutor simples para português
Usa dicionário de traduções comuns
"""

import logging

logger = logging.getLogger(__name__)

# Dicionário de traduções comuns em buscas
TRANSLATIONS = {
    # Artigos e preposições
    "the": "o",
    "a": "um",
    "an": "um",
    "and": "e",
    "or": "ou",
    "in": "em",
    "on": "em",
    "at": "em",
    "to": "para",
    "from": "de",
    "with": "com",
    "by": "por",
    "for": "para",
    "of": "de",
    "is": "é",
    "are": "são",
    "was": "foi",
    "were": "foram",
    "be": "ser",
    "been": "sido",
    "being": "sendo",
    
    # Palavras comuns
    "about": "sobre",
    "search": "busca",
    "result": "resultado",
    "results": "resultados",
    "wikipedia": "wikipedia",
    "definition": "definição",
    "meaning": "significado",
    "information": "informação",
    "page": "página",
    "website": "site",
    "link": "link",
    "article": "artigo",
    "news": "notícias",
    "image": "imagem",
    "video": "vídeo",
    "description": "descrição",
    "summary": "resumo",
    "more": "mais",
    "less": "menos",
    "see": "ver",
    "view": "visualizar",
    "read": "ler",
    "click": "clique",
    "here": "aqui",
}


def translate_text(text: str) -> str:
    """
    Tenta traduzir texto do inglês para português
    Usa substituição simples de palavras comuns
    """
    if not text:
        return text
    
    translated = text
    
    # Traduzir palavras comuns (case-insensitive)
    for en_word, pt_word in TRANSLATIONS.items():
        # Substituir palavra inteira (com limites de palavra)
        import re
        pattern = r'\b' + re.escape(en_word) + r'\b'
        translated = re.sub(pattern, pt_word, translated, flags=re.IGNORECASE)
    
    return translated


def translate_search_result(result: str) -> str:
    """
    Traduz resultado de busca
    Mantém a estrutura, traduz o conteúdo
    """
    if not result:
        return result
    
    lines = result.split('\n')
    translated_lines = []
    
    for line in lines:
        # Não traduzir linhas que começam com emoji ou marcadores
        if line.strip().startswith(('📌', '•', '-', '*')):
            # Traduzir apenas o texto após o marcador
            marker = line[:line.find(next((c for c in line if c.isalpha()), ''))]
            content = line[len(marker):]
            translated_content = translate_text(content)
            translated_lines.append(marker + translated_content)
        else:
            translated_lines.append(translate_text(line))
    
    return '\n'.join(translated_lines)


def translate_query(query: str) -> str:
    """
    Traduz query de português para inglês para melhor busca
    (Útil se o usuário enviar em português)
    """
    # Dicionário reverso
    pt_to_en = {v: k for k, v in TRANSLATIONS.items()}
    
    translated = query
    import re
    
    for pt_word, en_word in pt_to_en.items():
        pattern = r'\b' + re.escape(pt_word) + r'\b'
        translated = re.sub(pattern, en_word, translated, flags=re.IGNORECASE)
    
    return translated
