---
name: github-toolkit
description: "Comprehensive toolkit for GitHub operations: auth, repo management, issues, PRs, and code review."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, gh-cli, Automation, API, Workflow]
---

# GitHub Toolkit

This is a class-level umbrella skill covering all aspects of interacting with GitHub via the `gh` CLI, `git`, and the REST API.

## Table of Contents
1. [Authentication](#authentication)
2. [Repository Management](#repository-management)
3. [Issue Tracking](#issue-tracking)
4. [Pull Request Lifecycle](#pull-request-lifecycle)
5. [Code Review](#code-review)

---

## Authentication
Provides setup for `git` and `gh` CLI authentication, including HTTPS tokens and SSH keys.
- **Detection:** Check `gh auth status` or `git config --global credential.helper`.
- **Methods:** 
  - Git-Only (HTTPS Token or SSH)
  - gh CLI (Browser or Token)
- **API Access:** Use `GITHUB_TOKEN` env var for `curl` fallbacks.
*Refer to `scripts/gh-env.sh` for environment setup.*

---

## Repository Management
Operations for managing the lifecycle of repositories.
- **Cloning:** HTTPS, SSH, Shallow clones.
- **Creation:** Public/Private, from templates, or existing local directories.
- **Forking:** Syncing forks with upstream.
- **Settings:** Visibility, default branches, topics, and branch protection.
- **Secrets:** Managing GitHub Actions secrets (via `gh secret` or API).
- **Releases:** Creating and managing releases and assets.
- **Actions:** Monitoring and triggering workflow runs.
*Refer to `references/github-api-cheatsheet.md` for API details.*

---

## Issue Tracking
Tools for managing the issue tracker.
- **Viewing:** Searching and filtering issues by state or labels.
- **Creation:** Using templates for bugs and features.
- **Management:** Adding/removing labels, assignees, and commenting.
- **Triage:** Workflow for categorizing and prioritizing new issues.
*Templates: `templates/bug-report.md`, `templates/feature-request.md`.*

---

## Pull Request Lifecycle
The end-to-end process of contributing code.
- **Branching:** Conventional naming (`feat/`, `fix/`, etc.).
- **Commits:** Conventional Commits standard.
- **PR Creation:** Drafts, reviewers, and body templates.
- **CI Monitoring:** Polling status, diagnosing failures, and auto-fix loops.
- **Merging:** Squash merge, auto-merge, and branch cleanup.
*Refer to `references/conventional-commits.md` and `references/ci-troubleshooting.md`. Templates: `templates/pr-body-bugfix.md`, `templates/pr-body-feature.md`.*

---

## Code Review
Strategies for high-quality reviews of local and remote changes.
- **Local Review:** Pre-push diff analysis, searching for secrets/TODOs.
- **PR Review:** Checking out PRs locally, using the Review Checklist.
- **Submission:** Providing structured feedback (Critical/Warning/Suggestion) and submitting formal reviews (Approve/Request Changes).
- **Workflow:** Set up env $\rightarrow$ Gather context $\rightarrow$ Local checkout $\rightarrow$ Diff analysis $\rightarrow$ Test $\rightarrow$ Checklist $\rightarrow$ Submit.
*Refer to `references/review-output-template.md` for feedback formatting.*

---

## Quick Reference Table

| Action | gh CLI | git + curl |
|--------|--------|-------------|
| Auth | `gh auth login` | `git config ...` |
| Clone | `gh repo clone` | `git clone` |
| Create Repo | `gh repo create` | `POST /user/repos` |
| Issue List | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| PR Create | `gh pr create` | `POST /repos/{o}/{r}/pulls` |
| PR Review | `gh pr review` | `POST /repos/{o}/{r}/pulls/N/reviews` |
| Secrets | `gh secret set` | `PUT /repos/{o}/{r}/actions/secrets/K` |
| Releases | `gh release create` | `POST /repos/{o}/{r}/releases` |
