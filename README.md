# 🤖 Ayugram UserBot com IA

Um **UserBot avançado** para Telegram/Ayugram com integração de IA, sistema de permissões e automações inteligentes.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)

---

## ✨ Características

- 🧠 **IA Integrada** - Respostas inteligentes com Manus AI
- 🔐 **Sistema de Permissões** - Controle quem pode usar
- 🎯 **Comandos Personalizados** - `.ia`, `.perm`, `.help`, `.status`
- 🔄 **Execução 24/7** - Roda continuamente no Termux
- 📱 **Compatível com Ayugram** - Funciona em qualquer cliente Telegram
- ⚡ **Assíncrono** - Performance otimizada com asyncio

---

## 🚀 Quick Start

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/ayugram-userbot-ia.git
cd ayugram-userbot-ia
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Credenciais

```bash
cp config/.env.example config/.env
nano config/.env
```

Preencha com seus dados:
```
TELEGRAM_API_ID=123456789
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+5585987654321
OWNER_ID=123456789
MANUS_API_KEY=seu_token_aqui
```

### 4. Executar

```bash
python3 src/main.py
```

---

## 📋 Comandos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `.ia` | Fazer pergunta para IA | `.ia Qual é a capital do Brasil?` |
| `.perm` | Gerenciar permissões | `.perm 123456789` |
| `.perm list` | Listar usuários | `.perm list` |
| `.help` | Menu de ajuda | `.help` |
| `.status` | Status do bot | `.status` |

---

## 🔧 Instalação no Termux

### Passo 1: Atualizar Termux

```bash
pkg update && pkg upgrade -y
```

### Passo 2: Instalar Python

```bash
pkg install python3 git -y
```

### Passo 3: Clonar e Instalar

```bash
git clone https://github.com/seu-usuario/ayugram-userbot-ia.git
cd ayugram-userbot-ia
pip install -r requirements.txt
```

### Passo 4: Configurar e Rodar

```bash
cp config/.env.example config/.env
nano config/.env
python3 src/main.py
```

### Passo 5: Rodar 24/7

```bash
# Instalar screen
pkg install screen -y

# Criar sessão
screen -S userbot -d -m python3 src/main.py

# Ver logs
screen -r userbot

# Parar
screen -r userbot  # Ctrl + C
```

---

## 🔐 Sistema de Permissões

- **Apenas você** (dono) pode usar `.perm`
- **Apenas usuários permitidos** podem usar `.ia`
- Permissões salvas em `permissions.json`

### Exemplo:

```
Você: .perm 987654321
Bot: ✅ Permissão concedida para 987654321

Você: .perm list
Bot: 👥 Usuários com Permissão:
     • 987654321
     • 123456789
```

---

## 📁 Estrutura do Projeto

```
ayugram-userbot-ia/
├── src/
│   └── main.py              # Código principal do bot
├── config/
│   └── .env.example         # Template de configuração
├── docs/
│   └── INSTALACAO.md        # Guia de instalação
├── scripts/
│   └── startup.sh           # Script de inicialização
├── requirements.txt         # Dependências Python
├── .gitignore              # Arquivos ignorados
└── README.md               # Este arquivo
```

---

## 🛠️ Configuração Avançada

### Variáveis de Ambiente

```bash
# Nível de log
LOG_LEVEL=INFO              # INFO, DEBUG, WARNING, ERROR

# Modo debug
DEBUG=False                 # True para mais informações

# URL da IA
MANUS_API_URL=https://api.manus.im
```

### Arquivo de Permissões

```json
{
  "allowed_users": [
    123456789,
    987654321,
    555555555
  ]
}
```

---

## 🐛 Troubleshooting

### "Erro de autenticação"
```bash
# Verifique o PHONE_NUMBER (com código do país)
# Insira o código de verificação que recebeu
```

### "Permissão negada"
```bash
# Use .perm (seu_id) para se dar permissão
# Verifique se OWNER_ID está correto
```

### "IA não responde"
```bash
# Verifique MANUS_API_KEY
# Teste a conexão com internet
# Verifique os logs
```

---

## 📊 Monitoramento

### Ver Logs
```bash
screen -r userbot
```

### Ver Uso de Recursos
```bash
ps aux | grep python3
free -h
df -h
```

### Reiniciar Bot
```bash
screen -r userbot
# Ctrl + C para parar
screen -S userbot -d -m python3 src/main.py
```

---

## 🔒 Segurança

⚠️ **IMPORTANTE:**

1. **Nunca compartilhe seu `.env`**
2. **Guarde bem seu `MANUS_API_KEY`**
3. **Use permissões com cuidado**
4. **Monitore o bot regularmente**

---

## 📝 Exemplos de Uso

### Fazer Perguntas para IA

```
.ia Me explique Python em 3 linhas
.ia Qual é a fórmula de Bhaskara?
.ia Traduza "Hello World" para português
.ia Crie um poema sobre programação
```

### Gerenciar Permissões

```
.perm 123456789           # Dar permissão
.perm list                # Ver todos
```

### Verificar Status

```
.status                   # Ver informações
.help                     # Ver comandos
```

---

## 🤝 Contribuindo

Encontrou um bug? Tem uma ideia? Abra uma **Issue** ou **Pull Request**!

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja `LICENSE` para mais detalhes.

---

## 🎯 Roadmap

- [ ] Suporte a múltiplas contas
- [ ] Banco de dados para histórico
- [ ] Mais comandos automáticos
- [ ] Interface web para gerenciar
- [ ] Integração com mais APIs

---

## 📞 Suporte

Dúvidas? Problemas? Entre em contato!

- 📧 Email: seu-email@example.com
- 💬 Telegram: @seu-usuario
- 🐛 Issues: GitHub Issues

---

**Desenvolvido com ❤️ usando Python e Telethon**

⭐ Se gostou, deixe uma estrela!
