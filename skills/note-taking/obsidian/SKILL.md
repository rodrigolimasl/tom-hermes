---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Pitfall: Docker / containerized Hermes + Obsidian Cloud sync

If Hermes runs inside a Docker container (or similar containerized environment), the Obsidian vault that is synced via **Obsidian Cloud Sync** will NOT be visible inside the container — it lives on the host machine where the Obsidian desktop app syncs to a local directory.

**How to detect:** `find / -name ".obsidian" -type d` returns nothing even though the user swears they have an Obsidian vault.

**Workarounds:**
1. **Volume mount:** Ask the user to mount their vault directory into the container (e.g., `-v /path/to/vault:/opt/data/vault`) so the agent can access it
2. **Git bridge:** If the vault is tracked in Git, clone it inside the container
3. **Local vault:** Create a vault directly inside the container and let the user work with it there

**How to detect Docker environment:** Check `HERMES_S6_SUPERVISED_CHILD` env var is set, or run `ps aux | grep s6` to see s6-supervised processes, or look for `/opt/hermes/` source directory.

## Enabling web tools for Obsidian research

If the user needs web search capabilities (e.g., to verify information found in notes against the web), the `web` toolset must be enabled in `config.yaml` under `platform_toolsets`. Note: `config.yaml` is a security-sensitive file and the agent **cannot edit it directly** — use the user to edit it via `hermes config edit` or directly in their file manager. See the `hermes-agent` skill for the exact `platform_toolsets` syntax.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Troubleshooting

### No vault found on the server

If `OBSIDIAN_VAULT_PATH` is unset AND the fallback path `~/Documents/Obsidian Vault` does not exist:

1. **Search the filesystem:**
   ```
   find / -name ".obsidian" -type d 2>/dev/null | head -10
   ```
   If `.obsidian` is found, its parent directory IS the vault root.

2. **Obsidian Cloud sync scenario** — Ask the user: "Você usa Obsidian Cloud sync?" Users on Cloud sync expect the vault everywhere, but the sync only works between devices running the Obsidian app, NOT server-side directories. The server simply has no vault to access. Recommend:
   - User provides the vault path from their local machine → set `OBSIDIAN_VAULT_PATH` manually
   - Switch to Git sync → clone the vault repo onto the server
   - Create a fresh local vault on the server for agent-managed notes

3. **Vault in non-standard location** — The user may have placed it anywhere. Ask directly: "Me diz o caminho do vault na sua máquina" and configure from that.
