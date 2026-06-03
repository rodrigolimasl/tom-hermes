# Cron jobs do Hermes - Tom
## Documentação para restauração

> ⚠️ Estes jobs vivem na state.db (que NÃO está no backup).
> Se restaurar de zero, recrie manualmente usando `hermes cron` ou o arquivo abaixo como referência.

---

## Jobs ativos

### 1. Daily Backup - Tom
| Campo | Valor |
|-------|-------|
| **Job ID** | `d9987bff6391` |
| **Nome** | `Daily Backup - Tom` |
| **Script** | `backup-tom.sh` |
| **Cron** | `0 4 * * *` (00:00 Manaus / 04:00 UTC) |
| **no_agent** | `true` |
| **workdir** | `/opt/data/scripts` |
| **Descrição** | Backup seletivo do estado operacional → GitHub (rodrigolimasl/tom-hermes) |

**Para recriar:**
```
hermes cron add --name "Daily Backup - Tom" \
  --schedule "0 4 * * *" \
  --script "backup-tom.sh" \
  --no-agent \
  --workdir /opt/data/scripts \
  "Executar backup do Hermes Agent para GitHub."
```

---

*Última atualização: 2026-06-03*
