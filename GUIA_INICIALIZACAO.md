# 🚀 Guia de Inicialização - JT IA Bot

## 📋 Pré-requisitos

- Python 3.8+
- pip3
- Conta Telegram
- API ID e API Hash do Telegram

---

## 1️⃣ Obter Credenciais do Telegram

### Passo 1: Acessar https://my.telegram.org/apps

1. Faça login com sua conta Telegram
2. Clique em "Create New Application"
3. Preencha os dados:
   - **App title**: "JT IA Bot"
   - **Short name**: "jtiabot"
   - **Platform**: Desktop
4. Copie:
   - **api_id** → `API_ID`
   - **api_hash** → `API_HASH`

---

## 2️⃣ Configurar o Arquivo `.env`

### Criar arquivo `config/.env`:

```bash
mkdir -p config
touch config/.env
```

### Editar `config/.env`:

```env
# Telegram API
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Seu número de telefone (com código do país)
PHONE_NUMBER=+5585987654321

# Seu ID do Telegram (obter em @userinfobot)
OWNER_ID=123456789

# Senha 2FA (deixe vazio se não tiver)
PASSWORD_2FA=

# Provedor de IA padrão (gemini, groq ou openrouter)
AI_PROVIDER=groq

# Chaves de API (adicione pelo menos uma)
GEMINI_API_KEY=sua_chave_gemini_aqui
GROQ_API_KEY=sua_chave_groq_aqui
OPENROUTER_API_KEY=sua_chave_openrouter_aqui
```

### Obter seu ID do Telegram:

1. Abra Telegram
2. Procure por `@userinfobot`
3. Envie `/start`
4. Copie o **ID** mostrado

---

## 3️⃣ Instalar Dependências

```bash
cd ~/ayugram-userbot-ia
pip3 install -r requirements.txt
```

---

## 4️⃣ Iniciar o Bot

### Comando para iniciar:

```bash
cd ~/ayugram-userbot-ia
python3 src/main.py
```

### Primeira execução:

Na primeira vez, o bot pedirá:
1. **Código de verificação** - Você receberá um código no Telegram
2. **Senha 2FA** (se tiver) - Digite sua senha de autenticação em duas etapas

---

## 5️⃣ Usar o Bot

### Comandos Disponíveis:

```
IA:
.ia [pergunta]              - Usa IA padrão
.iagroq [pergunta]          - Força Groq
.iarouter [pergunta]        - Força OpenRouter
.ai [groq|openrouter]       - Define IA padrão

BUSCA:
.search [termo]             - Buscar na web

PERSONAS:
.persona [nome]             - Mudar personalidade
.persona list               - Listar personas

PERMISSÕES (dono):
.perm [ID]                  - Dar permissão
.perm remove [ID]           - Remover permissão
.perm list                  - Listar usuários

BAN (dono):
.ban [ID]                   - Banir usuário
.unban [ID]                 - Desbanir usuário
.ban list                   - Listar banidos

ESTATÍSTICAS:
.stats                      - Ver estatísticas gerais (dono)
.mystats                    - Ver suas estatísticas

INFO:
.status                     - Ver status
.help                       - Ver todos os comandos
```

---

## ❓ Perguntas Frequentes

### P: O `.env` é o mesmo?

**R:** Sim! O arquivo `config/.env` é o mesmo que você usava antes. A estrutura é idêntica:

**Antes:**
```env
API_ID=12345678
API_HASH=abcdef...
PHONE_NUMBER=+558598...
OWNER_ID=123456789
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

**Depois:**
```env
API_ID=12345678
API_HASH=abcdef...
PHONE_NUMBER=+558598...
OWNER_ID=123456789
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

✅ **Exatamente o mesmo!** Você pode usar o `.env` anterior sem modificações.

---

### P: Preciso reconfigurar tudo?

**R:** Não! Se você já tem um arquivo `config/.env` funcionando, apenas:

```bash
cd ~/ayugram-userbot-ia
git pull origin main
python3 src/main.py
```

O bot usará o mesmo `.env` anterior.

---

### P: Como obter as chaves de API?

#### Groq (Recomendado - Rápido e Grátis):
1. Acesse https://console.groq.com
2. Faça login/cadastro
3. Vá para "API Keys"
4. Clique "Create API Key"
5. Copie a chave para `GROQ_API_KEY`

#### OpenRouter:
1. Acesse https://openrouter.ai
2. Faça login/cadastro
3. Vá para "Keys"
4. Clique "Create Key"
5. Copie a chave para `OPENROUTER_API_KEY`

#### Gemini:
1. Acesse https://makersuite.google.com/app/apikey
2. Faça login com Google
3. Clique "Create API Key"
4. Copie a chave para `GEMINI_API_KEY`

---

### P: O bot não conecta. O que fazer?

**R:** Verifique:

1. ✅ Arquivo `config/.env` existe?
   ```bash
   ls -la config/.env
   ```

2. ✅ Variáveis estão preenchidas?
   ```bash
   cat config/.env
   ```

3. ✅ Telefone tem formato correto (+55...)?

4. ✅ Código de verificação foi enviado?

5. ✅ Você tem internet?

Se ainda não funcionar, verifique os logs:
```bash
python3 src/main.py 2>&1 | head -50
```

---

### P: Como parar o bot?

**R:** Pressione `Ctrl+C` no terminal:

```
[+] Bot rodando com sucesso!
[+] Aguardando comandos...
^C
Bot desconectado pelo usuário
```

---

### P: Posso usar em múltiplos grupos?

**R:** Sim! O bot funciona em:
- ✅ Chats privados (1-a-1)
- ✅ Grupos
- ✅ Supergrupos
- ✅ Canais (com permissões)

Cada usuário tem seu próprio contexto e histórico.

---

### P: Como dar permissão para outros usuários?

**R:** Use o comando `.perm`:

```
.perm 123456789          - Dar permissão
.perm remove 123456789   - Remover permissão
.perm list               - Ver quem tem permissão
```

Apenas o dono (OWNER_ID) pode executar esses comandos.

---

## 🔧 Troubleshooting

### Erro: "Arquivo config/.env não encontrado"

```bash
mkdir -p config
nano config/.env
# Adicione as variáveis
```

### Erro: "API_ID inválido"

Certifique-se que `API_ID` é um número:
```env
API_ID=12345678  # ✅ Correto
API_ID=abc       # ❌ Errado
```

### Erro: "Chave de API não configurada"

Se `AI_PROVIDER=groq`, certifique-se que `GROQ_API_KEY` está preenchido:
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...  # ✅ Obrigatório
```

### Erro: "Muitas tentativas"

Aguarde alguns minutos antes de tentar conectar novamente.

---

## 📊 Monitorar o Bot

### Ver logs em tempo real:

```bash
python3 src/main.py
```

### Ver apenas erros:

```bash
python3 src/main.py 2>&1 | grep -i error
```

### Rodar em background (Linux/Mac):

```bash
nohup python3 src/main.py > bot.log 2>&1 &
```

### Ver logs do background:

```bash
tail -f bot.log
```

---

## ✅ Checklist de Inicialização

- [ ] Arquivo `config/.env` criado
- [ ] `API_ID` preenchido
- [ ] `API_HASH` preenchido
- [ ] `PHONE_NUMBER` preenchido (com +55)
- [ ] `OWNER_ID` preenchido
- [ ] `AI_PROVIDER` definido
- [ ] Chave de API do provider preenchida
- [ ] Dependências instaladas (`pip3 install -r requirements.txt`)
- [ ] Bot iniciado com `python3 src/main.py`
- [ ] Código de verificação recebido no Telegram
- [ ] Bot conectado com sucesso

---

## 🎉 Pronto!

Seu bot JT IA está pronto para usar! 🚀

Qualquer dúvida, verifique os logs ou consulte este guia.

**Divirta-se!** 😊
