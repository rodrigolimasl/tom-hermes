---
name: ai-first-vault-architecture
description: Guidelines for designing and optimizing Obsidian/Markdown vaults specifically for LLM retrieval performance (AI-First), prioritizing locality of context over human taxonomy.
---

# AI-First Vault Architecture

When organizing knowledge bases for an AI assistant, the primary goal is to minimize the number of tool calls (search/read) and reduce token noise. Human-centric taxonomies (e.g., "Decisions", "Meeting Notes") are inefficient for AI because they fragment a single entity's context across multiple directories.

## 🛠️ Core Principles

### 1. Locality of Context (Entity-Centric)
Organize data by **Entity** (Project, Client, Topic) rather than **Document Type**.
- **❌ Human-Centric:** `/Decisions/ProjectA.md`, `/Notes/ProjectA.md`, `/Tasks/ProjectA.md`
- **✅ AI-First:** `/Projects/ProjectA/decisions.md`, `/Projects/ProjectA/notes.md`, `/Projects/ProjectA/tasks.md`

**Reasoning:** Allows the AI to identify the entity and perform a single directory listing/read operation to capture the full context of that entity.

### 2. Context Routers (`_index.md`)
Every entity folder must contain a `_index.md` (or `manifest.md`) that acts as a map for the AI.
- **Contents:**
    - **Summary:** High-level purpose of the entity.
    - **File Map:** Explicit pointers to key files (e.g., "For financial goals, see `metas.md`").
    - **Status:** Current state (Active, On Hold, Archive).
    - **Key Dates:** Last significant update.

### 3. Global Map of Content (MOC)
Maintain a root-level `MOC.md` that lists all high-level entities. This prevents the AI from having to run expensive recursive directory searches.

### 4. Sync & Delivery (Headless Operation)
When operating a vault via CLI (e.g., `obsidian-headless`), be aware that the native File System Watcher is typically absent.
- **Manual Push:** Every significant write operation should be followed by an explicit push command (e.g., `ob sync-push`) to ensure changes propagate to the user's devices.
- **Stability Pattern:** Implement a recurring cronjob (e.g., every 15-30 mins) that executes the sync-push. This prevents "silent desync" where the AI updates the disk but the user doesn't see the changes in the Obsidian App.


---

## 🪜 Implementation Workflow

1. **Audit:** Identify fragmented data (e.g., a "Decisions" folder containing files for 10 different projects).
2. **Cluster:** Create one folder per Entity.
3. **Migrate:** Move all related files into the Entity folder.
4. **Route:** Create the `_index.md` for each folder.
5. **Map:** Update the root `MOC.md` with links to all Entity indices.
6. **Isolate:** Place global, non-entity-specific facts into a `Base-Knowledge` or `Reference` directory.

## ⚠️ Pitfalls
- **Taxonomy Trap:** Do not create folders like "Drafts" or "Finals" if they split the context of a single project. Keep versions inside the entity folder.
- **Over-Indexing:** Do not make indices too verbose. They should be pointers, not clones of the underlying data.
- **Deep Nesting:** Avoid folders deeper than 3 levels. Every level of nesting increases the risk of path errors and retrieval latency.

## ✅ Verification
A vault is AI-optimized if:
- An agent can answer a complex question about a project by reading $\le 3$ files (MOC $\rightarrow$ Index $\rightarrow$ Target File).
- No `search_files` call is required to find the "main" file of a project.
