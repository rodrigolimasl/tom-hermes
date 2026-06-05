# Lições: Operações Git em Scripts de Backup

## Problema: Detached HEAD ao usar `origin/HEAD`

Ao usar `git reset --hard origin/HEAD`, o checkout fica em *detached HEAD*. Quando isso acontece, `git push origin HEAD` falha porque Git não sabe para qual branch remota enviar.

**Solução:** Usar o nome do branch explicitamente:
```bash
git checkout -B main origin/main        # cria/atualiza branch local apontando pro remote
git pull --rebase origin main           # sincroniza antes do push
git push -f origin main                 # push explícito para branch
```

## Problema: Erro de `non-fast-forward`

Causado quando o repositório local e remoto divergem (ex: backup anterior criou commit local antes de estar sincronizado).

**Solução:**
1. Sempre fazer `git pull --rebase origin main` antes do push
2. Usar `git push -f` (force push) para repositórios unilaterais de backup — o Tom é o único escritor

## Problema: Escaping em scripts bash com Git + credential helpers

Bash escaping quebrava repetidamente ao tentar criar Git credential askpass helpers inline. Strings com `case/esac`, `printf` e múltiplas camadas de aspas geravam syntax errors.

**Solução preferida:** Escrever a lógica de Git em Python dentro do script, chamando `subprocess.run(..., shell=True)` com dicts de ambiente bem-formados. O bash funciona como wrapper fino:
```bash
#!/usr/bin/env bash
set -euo pipefail
exec python3 /opt/data/scripts/backup-tom.py "$@"
```

## Checklist para scripts que operam repositórios Git

- [ ] Usar branch name explícito, nunca `HEAD`
- [ ] `git config --global --add safe.directory <workdir>` antes de operações
- [ ] `git fetch -q origin` antes de qualquer operação de sync
- [ ] `git pull --rebase -q origin main` antes do push para evitar divergência
- [ ] Forçar push em repositórios unilaterais de backup
- [ ] Usar Python para lógica complexa de Git ao invés de bash fragile
