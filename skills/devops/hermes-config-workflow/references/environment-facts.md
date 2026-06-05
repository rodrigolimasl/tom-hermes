# Environment Facts (Optimized Session)

## Hermes Install Location

```
/opt/hermes/          ← install root (git clone)
/opt/hermes/.venv/    ← Python venv (active)
/opt/hermes/bin/hermes ← CLI binary
```

**Cuidado:** `hermes` CLI pode NÃO estar no `$PATH` do terminal da sessão. Usar sempre o caminho absoluto:

```bash
/opt/hermes/.venv/bin/hermes config set ...
```

## Config File

- Config YAML fica em `$HERMES_HOME/config.yaml`.
- `HERMES_HOME` pode ser `/opt/data` (sobrescrito). Não assumir `~/.hermes/config.yaml`.
- Para descobrir: `/opt/hermes/.venv/bin/hermes config path`

## Venv Sem pip

O venv do Hermes NÃO carrega `pip` (stripped para reduzir tamanho de install). Dois workarounds:

```bash
# Opção 1 — usar python3 -m pip (funciona se o módulo estiver no site-packages)
/opt/hermes/.venv/bin/python3 -m pip install <pkg>

# Opção 2 — usar ensurepip first (se nem mesmo o módulo existe)
/opt/hermes/.venv/bin/python3 -m ensurepip && /opt/hermes/.venv/bin/python3 -m pip install <pkg>
```

⚠️ **NUNCA** instale pacotes no Python do sistema para features do Hermes — o gateway roda dentro do venv, então os pacotes precisam estar lá.
