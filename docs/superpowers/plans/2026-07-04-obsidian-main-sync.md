# Obsidian Main Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Obsidian draft-PR automation with a simpler main-only auto-commit and auto-push workflow.

**Architecture:** Keep the vault on `main` permanently. The scheduled PowerShell script will lock, detect changes, commit them on `main`, and push directly to `origin/main` without any GitHub PR actions. Existing `obsidian/auto-sync` history is folded into `main`, then the old PR and branch are removed.

**Tech Stack:** PowerShell, Git CLI, GitHub CLI, Windows Task Scheduler, Pester

---

### Task 1: Update script behavior

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\tests\obsidian-auto-pr.Tests.ps1`

- [ ] Add a failing test for the new main-only branch metadata helper.
- [ ] Remove PR-specific helper expectations from the tests.
- [ ] Implement the main-only orchestration so the script commits and pushes `main` only.
- [ ] Run Pester and confirm the updated helper suite is green.

### Task 2: Update documentation

**Files:**
- Modify: `C:\Users\User\git\process\docs\superpowers\specs\2026-07-04-obsidian-auto-pr-design.md`

- [ ] Rewrite the spec summary so it describes direct `main` sync instead of draft PR accumulation.

### Task 3: Migrate repository state

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault` git state

- [ ] Fast-forward or merge `obsidian/auto-sync` into `main`.
- [ ] Switch the live vault back to `main`.
- [ ] Push `main` so GitHub and local Obsidian pulls align on the same branch.

### Task 4: Remove obsolete PR flow

**Files:**
- Modify: GitHub repository state for `ChangwooHan-hub/obsidian-vault`

- [ ] Close draft PR `#1`.
- [ ] Delete remote branch `obsidian/auto-sync`.
- [ ] Delete local branch `obsidian/auto-sync`.

### Task 5: Verify end-to-end

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\...` for a temporary manual test only

- [ ] Run Pester and confirm it passes.
- [ ] Run the script once with no changes and confirm it logs `No changes detected.`
- [ ] Make a small note change on `main`, run the script, and confirm direct push to `origin/main`.
- [ ] Revert or intentionally keep the manual note change before finishing.
