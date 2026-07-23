# 📖 GUIA COMPLETO - JT IA BOT

## 🎯 Visão Geral

**JT IA Bot** é um UserBot profissional para Telegram com suporte a múltiplas IAs, histórico de conversa, análise de imagens, transcrição de áudio e muito mais!

---

## 🚀 Como Iniciar

### 1. Clonar o Repositório
```bash
git clone https://github.com/Darklindo/ayugram-userbot-ia.git
cd ayugram-userbot-ia
```

### 2. Configurar o `.env`
```bash
nano config/.env
```

Adicione suas credenciais:
```
API_ID=seu_api_id
API_HASH=seu_api_hash
PHONE_NUMBER=+55seu_numero
PASSWORD_2FA=sua_senha_2fa_opcional
OWNER_ID=seu_id_telegram
AI_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq
OPENROUTER_API_KEY=sua_chave_openrouter
```

### 3. Rodar o Bot
```bash
python3 src/main.py
```

Na primeira vez, vai pedir o código de verificação do Telegram (fica invisível, mas digita mesmo assim).

---

## 📚 COMANDOS PRINCIPAIS

### 🤖 Comandos de IA

#### `.ia [pergunta]`
Faz uma pergunta usando a IA padrão (Groq)

**Exemplos:**
```
.ia Qual é a capital do Brasil?
.ia Explique Python em 3 linhas
.ia Como fazer um bolo de chocolate?
```

**Flags disponíveis:**
- `-short` → Resposta curta (150 caracteres)
- `-medium` → Resposta média (500 caracteres) - PADRÃO
- `-long` → Resposta longa (2000 caracteres)
- `-full` → Resposta completa (4000 caracteres)
- `-private` → Resposta em DM (privado)

**Exemplos com flags:**
```
.ia -short Qual é a capital?
.ia -long -private Explique relatividade
.ia -medium Qual é a melhor linguagem de programação?
```

---

#### `.iagroq [pergunta]`
Força o uso do Groq (muito rápido)

```
.iagroq Quanto é 8 + 9?
.iagroq -short Qual é a hora?
```

---

#### `.iarouter [pergunta]`
Força o uso do OpenRouter (múltiplos modelos)

```
.iarouter Qual é a melhor IA?
.iarouter -long Explique machine learning
```

---

### 🔍 Busca na Web

#### `.search [termo]`
Busca informações na web usando DuckDuckGo

**Exemplos:**
```
.search Python
.search Notícias sobre tecnologia
.search Como aprender programação
```

---

### 🎙️ Transcrição de Áudio

#### Responder mensagem com áudio + `.ia`
Transcreve o áudio e responde com IA

**Como usar:**
1. Seu amigo manda um áudio
2. Você responde com: `.ia Transcreva isso`
3. Bot transcreve e responde

---

### 🖼️ Análise de Imagens

#### Responder mensagem com imagem + `.ia`
Analisa a imagem e responde com IA

**Como usar:**
1. Seu amigo manda uma imagem
2. Você responde com: `.ia O que tem nessa imagem?`
3. Bot analisa e descreve

---

### 🎭 Personas Customizáveis

#### `.persona [nome]`
Muda a personalidade do bot (apenas dono)

**Personas disponíveis:**
- `normal` - Responde normalmente
- `dev` - Responde como desenvolvedor
- `professor` - Responde como professor
- `piada` - Faz piadas
- `poeta` - Responde como poeta
- `cientista` - Responde como cientista

**Exemplos:**
```
.persona dev
.persona professor
.persona piada
.persona list  (ver todas)
```

---

### 👤 Gerenciamento de Permissões

#### `.perm [ID]`
Dar permissão para um usuário usar IA

```
.perm 123456789
```

---

#### `.perm remove [ID]`
Remover permissão de um usuário

```
.perm remove 123456789
```

---

#### `.perm list`
Listar usuários com permissão

```
.perm list
```

---

### 🚫 Gerenciamento de Bans

#### `.ban [ID]`
Banir um usuário (apenas dono)

```
.ban 123456789
```

---

#### `.unban [ID]`
Desbanir um usuário (apenas dono)

```
.unban 123456789
```

---

#### `.ban list`
Listar usuários banidos

```
.ban list
```

---

### 📊 Estatísticas

#### `.stats`
Ver estatísticas gerais (apenas dono)

Mostra:
- Total de queries
- Queries por provedor
- Taxa de erro
- Usuário mais ativo

```
.stats
```

---

#### `.mystats`
Ver suas estatísticas pessoais

Mostra:
- Suas queries
- Seu provedor favorito
- Sua taxa de erro

```
.mystats
```

---

### ⚙️ Configuração

#### `.ai [provedor]`
Muda a IA padrão (apenas dono)

**Provedores:**
- `groq` - Muito rápido
- `openrouter` - Múltiplos modelos

**Exemplos:**
```
.ai groq
.ai openrouter
```

---

#### `.help`
Ver todos os comandos

```
.help
```

---

#### `.status`
Ver status do bot

```
.status
```

---

## 💡 EXEMPLOS DE USO

### Exemplo 1: Pergunta Simples
```
Você: .ia Qual é a capital da França?
Bot: Paris é a capital da França...
```

### Exemplo 2: Resposta Curta
```
Você: .ia -short O que é Python?
Bot: Python é uma linguagem de programação...
```

### Exemplo 3: Modo Privado
```
Você: .ia -private Qual é a melhor senha?
Bot: [Resposta enviada em DM]
```

### Exemplo 4: Busca na Web
```
Você: .search Inteligência Artificial
Bot: 🔍 Resultado da busca:
📌 IA é a simulação de inteligência...
```

### Exemplo 5: Análise de Imagem
```
Amigo: [Manda uma foto]
Você: .ia O que tem nessa foto?
Bot: Essa foto mostra...
```

### Exemplo 6: Transcrição de Áudio
```
Amigo: [Manda um áudio]
Você: .ia Transcreva
Bot: 🎙️ Transcrição:
[Texto do áudio]
```

### Exemplo 7: Mudança de Persona
```
Você: .persona dev
Bot: 🖥️ Persona alterada para: dev

Você: .ia Explique loops
Bot: [Resposta como desenvolvedor]
```

### Exemplo 8: Estatísticas
```
Você: .stats
Bot: 📊 Estatísticas Gerais:
Total de queries: 150
Groq: 100 (66.7%)
OpenRouter: 50 (33.3%)
Taxa de erro: 2%
Usuário mais ativo: João (45 queries)
```

---

## 🎯 DICAS E TRUQUES

### 1. Combinar Flags
```
.ia -short -private Qual é a hora?
```
Responde em privado com resposta curta

### 2. Usar Histórico
O bot lembra das últimas 5 mensagens do chat, então:
```
Você: .ia Qual é a capital do Brasil?
Bot: Brasília

Você: .ia Qual é a população?
Bot: [Usa contexto da pergunta anterior]
```

### 3. Fallback Automático
Se Groq falhar, o bot tenta OpenRouter automaticamente. Você não precisa fazer nada!

### 4. Reações Automáticas
- ⏳ Processando
- ✅ Sucesso
- ❌ Erro

### 5. Modo Privado para Dados Sensíveis
```
.ia -private Qual é minha melhor senha?
```
Resposta vai direto no DM, não fica no grupo

---

## 🔒 SEGURANÇA

### Permissões
- Apenas usuários com permissão podem usar `.ia`
- Apenas o dono pode usar comandos de admin
- Usuários banidos não conseguem usar nada

### Dados
- Histórico é armazenado apenas em memória
- Nenhum dado é enviado para servidores externos (exceto as IAs)
- Sessão do Telegram é criptografada

---

## ⚡ PERFORMANCE

### Velocidade
- **Groq:** ~1-2 segundos
- **OpenRouter:** ~2-5 segundos
- **Busca Web:** ~1-3 segundos
- **Transcrição:** ~5-10 segundos
- **Análise de Imagem:** ~3-8 segundos

### Limites
- **Groq:** Ilimitado (dentro do plano gratuito)
- **OpenRouter:** Ilimitado (modelos gratuitos)
- **Cooldown:** 5 segundos entre queries
- **Resposta máxima:** 4096 caracteres (limite do Telegram)

---

## 🐛 TROUBLESHOOTING

### Bot não conecta
```
Solução: Verifique se API_ID e API_HASH estão corretos
```

### Comando não funciona
```
Solução: Use .help para ver comandos disponíveis
```

### IA não responde
```
Solução: Verifique se você tem permissão (.perm list)
```

### Resposta muito longa
```
Solução: Use .ia -short para resposta curta
```

### Timeout na busca web
```
Solução: Tente novamente, conexão pode estar lenta
```

---

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique o arquivo `.manus-logs/devserver.log`
2. Veja a auditoria em `AUDITORIA_BUGS_ENCONTRADOS.md`
3. Consulte o `README.md` do projeto

---

## 📊 RESUMO DE FEATURES

| Feature | Status | Comando |
|---------|--------|---------|
| IA Múltipla | ✅ | `.ia`, `.iagroq`, `.iarouter` |
| Histórico | ✅ | Automático |
| Limite de Tokens | ✅ | `-short`, `-medium`, `-long`, `-full` |
| Modo Privado | ✅ | `-private` |
| Estatísticas | ✅ | `.stats`, `.mystats` |
| Reações | ✅ | Automático |
| Permissões | ✅ | `.perm`, `.ban` |
| Personas | ✅ | `.persona` |
| Busca Web | ✅ | `.search` |
| Áudio | ✅ | Responder áudio com `.ia` |
| Imagens | ✅ | Responder imagem com `.ia` |

---

**Bot versão:** 1.0.0  
**Última atualização:** Julho 2026  
**Status:** ✅ Pronto para produção
