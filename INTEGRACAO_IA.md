# Integração de IA - DeepSeek e Google Gemini

Guia completo para configurar o JT IA Bot com DeepSeek ou Google Gemini.

---

## 🚀 Opção 1: DeepSeek

### O que é?

**DeepSeek** é um modelo de IA open-source criado pela DeepSeek Inc., similar ao ChatGPT mas com custos muito menores.

- 📊 Modelo: DeepSeek-Chat
- 💰 Custo: Muito mais barato que OpenAI
- ⚡ Velocidade: Rápido e eficiente
- 🔓 Open-source: Código disponível

### Como configurar?

#### 1. Criar conta e gerar chave

1. Acesse: https://platform.deepseek.com
2. Crie uma conta
3. Vá para: **API Keys**
4. Clique em **Create new secret key**
5. Copie a chave (começa com `sk-`)

#### 2. Adicionar créditos

1. Vá para **Billing**
2. Clique em **Add credit**
3. Adicione pelo menos $5 para testar

#### 3. Configurar no .env

```bash
nano config/.env
```

Adicione:
```
AI_PROVIDER=deepseek
AI_API_KEY=sk-sua_chave_aqui
```

#### 4. Testar

```bash
python3 src/main.py
```

No Telegram:
```
.ia Qual eh a capital do Brasil?
```

### Preços DeepSeek

| Modelo | Input | Output |
|--------|-------|--------|
| deepseek-chat | $0.14/1M tokens | $0.28/1M tokens |

**Muito mais barato que OpenAI!**

---

## 🔮 Opção 2: Google Gemini

### O que é?

**Google Gemini** é o modelo de IA mais recente do Google, rival do GPT-4.

- 🎯 Modelo: Gemini Pro
- 💰 Custo: Gratuito até 60 requisições/minuto
- ⚡ Velocidade: Muito rápido
- 🏆 Qualidade: Excelente

### Como configurar?

#### 1. Criar chave de API

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em **Create API Key**
3. Selecione ou crie um projeto
4. Copie a chave (começa com `AIzaSy`)

#### 2. Configurar no .env

```bash
nano config/.env
```

Adicione:
```
AI_PROVIDER=gemini
AI_API_KEY=AIzaSy_sua_chave_aqui
```

#### 3. Testar

```bash
python3 src/main.py
```

No Telegram:
```
.ia Qual eh a capital do Brasil?
```

### Preços Gemini

| Tier | Input | Output | Limite |
|------|-------|--------|--------|
| Gratuito | Grátis | Grátis | 60 req/min |
| Pago | $0.075/1M | $0.3/1M | Ilimitado |

**Ótimo para começar gratuitamente!**

---

## 📊 Comparação

| Aspecto | DeepSeek | Gemini |
|--------|----------|--------|
| **Custo** | Muito barato | Gratuito + pago |
| **Velocidade** | Rápido | Muito rápido |
| **Qualidade** | Excelente | Excelente |
| **Limite Gratuito** | Pago | 60 req/min |
| **Setup** | Fácil | Muito fácil |
| **Recomendação** | Uso contínuo | Teste/Hobby |

---

## 🔧 Como Mudar de Provedor

Se você quer trocar de DeepSeek para Gemini (ou vice-versa):

```bash
# 1. Editar .env
nano config/.env

# 2. Mudar AI_PROVIDER e AI_API_KEY
AI_PROVIDER=gemini
AI_API_KEY=sua_nova_chave

# 3. Reiniciar o bot
python3 src/main.py
```

Pronto! O bot usará o novo provedor.

---

## 🐛 Troubleshooting

### "Erro: API key nao configurada"

**Solução:** Adicione `AI_API_KEY` ao `.env`:
```
AI_API_KEY=sua_chave_aqui
```

### "Erro: Chave de API invalida (401)"

**Solução:** 
- Verifique se a chave está correta
- Verifique se tem créditos (DeepSeek)
- Gere uma nova chave

### "Erro: Rate limit atingido (429)"

**Solução:**
- Aguarde alguns minutos
- Para Gemini: Limite é 60 req/min
- Para DeepSeek: Verifique saldo de créditos

### "Erro: Resposta invalida"

**Solução:**
- Verifique os logs: `tail -f .manus-logs/devserver.log`
- Tente uma pergunta mais simples
- Reinicie o bot

### "Timeout: Requisicao muito lenta"

**Solução:**
- Verifique sua conexão de internet
- Tente novamente em alguns segundos
- Mude para outro provedor

---

## 📝 Logs Detalhados

Para ver o que está acontecendo:

```bash
# Ver logs em tempo real
tail -f .manus-logs/devserver.log

# Ou no próprio terminal do bot
python3 src/main.py
```

Procure por:
- `Enviando para DeepSeek` ou `Enviando para Gemini`
- `respondeu com status: 200` (sucesso)
- `respondeu com status: 401` (chave inválida)
- `respondeu com status: 429` (rate limit)

---

## 💡 Dicas

### Para começar rápido
Use **Gemini** (gratuito, sem setup de créditos)

### Para uso contínuo
Use **DeepSeek** (muito mais barato)

### Para máxima qualidade
Ambos têm qualidade excelente, escolha por preço

### Para testar
Comece com Gemini, depois mude para DeepSeek

---

## 🔗 Links Úteis

- **DeepSeek API:** https://platform.deepseek.com
- **Google Gemini API:** https://makersuite.google.com/app/apikey
- **DeepSeek Docs:** https://api-docs.deepseek.com
- **Gemini Docs:** https://ai.google.dev/docs

---

## Próximos Passos

1. ✅ Escolha um provedor (DeepSeek ou Gemini)
2. ✅ Crie uma chave de API
3. ✅ Configure no `.env`
4. ✅ Teste com `.ia [pergunta]`
5. ✅ Aproveite! 🎉

---

**Dúvidas? Verifique os logs ou tente outro provedor!** 🚀
