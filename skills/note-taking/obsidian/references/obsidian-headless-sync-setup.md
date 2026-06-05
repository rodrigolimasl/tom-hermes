# Obsidian Headless Sync — Setup neste ambiente

## Fatos do ambiente (rodado em 2026-06-03)

- **Hermes home:** `/opt/data`
- **Node.js:** 22.22.3, npm 10.9.8 ✅ (requisito ≥ Node 22)
- **Sem sudo:** `npm install -g` falha com EACCES
- **npm prefix:** usar `--prefix /opt/data/home/.npm-global` para instalações globais sem sudo
- **Binário `ob`:** symlink em `/opt/data/home/.npm-global/bin/ob` → resolve para `../lib/node_modules/obsidian-headless/cli.js`
- **PATH:** precisa incluir `/opt/data/home/.npm-global/bin` (add ao `.bashrc`)

## Comandos de instalação

```bash
npm install -g obsidian-headless --prefix /opt/data/home/.npm-global
# binário em: /opt/data/home/.npm-global/bin/ob
```

## Fluxo de setup do Sync (pendente)

1. `ob login` — login interativo no Obsidian Cloud (requires PTY)
2. `ob sync-list-remote` — lista vaults remotos disponíveis
3. `ob sync-setup --vault "NOME" --path "/opt/data/Documents/Obsidian Vault" --device-name "TOM"`
4. `ob sync --path "/opt/data/Documents/Obsidian Vault"` — teste manual
5. `ob sync --path "/opt/data/Documents/Obsidian Vault" --continuous` — quando estável

## Pitfall encontrado em sessão (2026-06-03)

O usuário Rodrigo quer **apenas acesso local filesystem-first por enquanto**. Sync remoto será configurado em sessão futura. A skill `obsidian` já funciona perfeitamente para leitura/escrita local.
