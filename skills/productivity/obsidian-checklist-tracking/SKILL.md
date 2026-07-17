---
name: obsidian-checklist-tracking
description: Workflow for tracking progress and identifying next items in Obsidian markdown checklists.
---

# Obsidian Checklist Tracking

This skill defines how to manage and query progress in the user's Obsidian vault using markdown checkboxes (`- [ ]` and `- [x]`).

## Triggers
- User asks "What is my next [topic]?"
- User asks for a "status update" or "list" of a specific trackable project/hobby.
- User asks to "mark something as done" in a list.

## Workflow

### 1. Locate the List
- Search for files using keywords related to the topic.
- Priority search: `search_files(pattern='*lista*|*checklist*|*[topic]*', target='files')`.
- If not found, search within content: `search_files(pattern='- \[ \]', target='content')` combined with the topic keyword.

### 2. Identify the "Next" Item
- Read the file.
- Scan sequentially from the top.
- The **Next Item** is the first occurrence of `- [ ]` (unchecked box).
- If the list is categorized by headers (e.g., `## Category`), prioritize the first unchecked item in the first relevant category.

### 3. Summarize Status
- When asked to "list" or "review" the checklist:
    - Group items into **Completed** (`- [x]`) and **Pending** (`- [ ]`).
    - Maintain the relative order found in the file.
    - Present the result clearly (e.g., using bold lists) to avoid visual clutter.

## Pitfalls & Constraints
- **Multiple Lists:** A single file may contain multiple checklists. Always check for headers (e.g., `# Filmes AI` vs `# Filmes Marvel`) before reporting the "next" item.
- **False Positives:** Be careful with `search_files` pattern matches that might hit logs or configuration files; prioritize the `📚 Base-Conhecimento` or `🚀 Projetos` directories.
- **Case Sensitivity:** Search patterns should be flexible (e.g., using `*` wildcards).

## Verification
- Always confirm the file path and the exact text of the item being reported to ensure the user knows which list is being referenced.
