# Obsidian Headless (ob) CLI Reference

Commands for managing vault synchronization in a headless (server) environment.

## Connection & Diagnostics
- `ob sync-list-local`: Lists vaults configured on the local machine and their associated Obsidian Sync IDs.
- `ob sync-list-remote`: Lists vaults available on the remote Obsidian Sync server.
- `ob sync-status`: Checks the current sync state (Note: may return "No sync configuration found" if the environment variables/config are not correctly mapped to the current directory).

## Data Movement
- `ob sync-push`: Forces local changes to be uploaded to the Obsidian Sync cloud.
- `ob sync-pull`: Forces remote changes to be downloaded to the local filesystem.

## Critical Context
In server environments, the native File System Watcher is absent. Reliance on `sync-push` and scheduled cronjobs is mandatory to prevent data silos.
