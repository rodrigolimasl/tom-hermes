---
name: obsidian-sync-automation
description: "Automating synchronization for the rodrigolima-memorias vault using obsidian-headless (ob)."
version: 1.0.0
author: Tom
---

# Obsidian Sync Automation

This skill governs the synchronization of the `rodrigolima-memorias` vault from the Linux environment to the cloud, ensuring consistency with the user's MacBook.

## Tooling & Configuration
- **Binary Path:** `/opt/data/home/.npm-global/bin/ob`
- **Vault Root:** `/opt/data/Documents/Obsidian Vault`
- **Sync Command:** `/opt/data/home/.npm-global/bin/ob sync`

## Standard Sync Workflow
When performing a manual sync or verifying state:
1. **Execution:** Always run the command with the explicit `workdir` set to the vault root to avoid configuration errors.
   - Command: `ob sync`
   - Workdir: `/opt/data/Documents/Obsidian Vault`
2. **Verification:** Look for the `Fully synced` output. Any other result indicates a conflict or local/remote drift.

## Automation Pattern (The Push-Loop)
To avoid manual intervention and reduce latency between the server and the MacBook, a recurring push-loop is implemented via `cronjob`.

### Cron Configuration
- **Schedule:** Every 15 minutes (`*/15 * * * *`).
- **Prompt:** "Execute the sync command to push vault changes to the cloud: /opt/data/home/.npm-global/bin/ob sync"
- **Verification:** Check `cronjob action='list'` to ensure the job is `enabled` and running.

## Pitfalls & Troubleshooting
- **Configuration Error:** If the output says "No sync configuration found", ensure the command is being executed from the correct vault directory.
- **Conflict Strategy:** The system is configured for `bidirectional` sync with a `merge` strategy. If conflicts arise, manual intervention in a GUI editor is preferred.
