# TODO - Melhorias JT IA Bot (8.5/10 → 9.7/10)

## 🔴 BUGS CRÍTICOS (Fase 1)

- [ ] **history_manager**: Implementar limpeza automática com LRU cache
- [ ] **cooldown**: Aplicar APÓS sucesso da IA, não antes
- [ ] **.search**: Usar `edit_long_message()` em vez de `processing_msg.edit()`
- [ ] **histórico**: Usar `(chat_id, sender_id)` como chave, não apenas `chat_id`
- [ ] **DM privado**: Validar se usuário aceitou DM antes de enviar
- [ ] **None response**: Adicionar validação se `ia_manager.process()` retorna None
- [ ] **Tratamento de erros**: Adicionar `MessageTooLongError`, `MessageNotModifiedError`, `RPCError`

## 🟠 SEGURANÇA (Fase 4)

- [ ] **Limite de prompt**: Máximo 2000 caracteres por pergunta
- [ ] **Rate limiting**: Implementar limite por minuto (não apenas cooldown)
- [ ] **Logs**: Remover IDs de usuários dos logs (usar hash)
- [ ] **Validação**: Sanitizar entrada de usuário

## 🟡 PERFORMANCE (Fase 3/5)

- [ ] **Cache sender**: Armazenar sender em contexto para reutilizar
- [ ] **Contexto lazy**: Reconstruir contexto apenas se necessário
- [ ] **Split cache**: Usar regex compilado para split

## 🔵 CONCORRÊNCIA (Fase 2)

- [ ] **HistoryManager**: Adicionar `asyncio.Lock`
- [ ] **StatsManager**: Adicionar `asyncio.Lock`
- [ ] **PermissionManager**: Adicionar `asyncio.Lock`
- [ ] **Provider switch**: Usar lock ao trocar provider

## 🟣 ARQUITETURA (Fase 3)

- [ ] **Separar handlers**: `ia_handlers.py`, `admin_handlers.py`, `search_handlers.py`, `persona_handlers.py`, `stats_handlers.py`
- [ ] **Reduzir main.py**: De 694 linhas para ~200 linhas
- [ ] **Cleanup com AsyncExitStack**: Melhorar finalização de recursos

## 🟢 MELHORIAS (Fase 5)

- [ ] **Cache de respostas**: Para perguntas repetidas (TTL 1 hora)
- [ ] **Fila de requisições**: `asyncio.Queue` para limitar chamadas às IAs
- [ ] **Retry automático**: Para erros 429/500 (exponential backoff)
- [ ] **Timeouts individuais**: Para web search, visão, transcrição
- [ ] **Logs estruturados**: JSON logging para melhor análise

## 📊 MÉTRICAS ESPERADAS

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Arquitetura | 9/10 | 9.5/10 |
| Segurança | 8/10 | 9/10 |
| Performance | 8/10 | 9/10 |
| Concorrência | 7/10 | 9/10 |
| Tratamento de erros | 8/10 | 9/10 |
| **GERAL** | **8.5/10** | **9.7/10** |

---

## 📋 ORDEM DE IMPLEMENTAÇÃO

1. **Fase 1**: Bugs críticos (memory leak, cooldown, .search, histórico)
2. **Fase 2**: Thread-safety (asyncio.Lock em managers)
3. **Fase 3**: Refatoração (separar handlers, reduzir main.py)
4. **Fase 4**: Segurança (rate limiting, sanitização, logs)
5. **Fase 5**: Otimizações (cache, fila, retry)
6. **Fase 6**: Testes e validação
