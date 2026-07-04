# Obsidian Auto PR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows-scheduled Obsidian automation that commits vault changes to `obsidian/auto-sync`, pushes them to GitHub, and maintains one long-lived draft PR against `main`.

**Architecture:** Keep the live vault on `obsidian/auto-sync` so the automation can commit the user's working tree directly without branch switching. Use a PowerShell script for locking, commit/push, PR lookup/creation, and a Scheduled Task for 15-minute execution.

**Tech Stack:** PowerShell, Git CLI, GitHub CLI, Windows Task Scheduler, Pester

---

### Task 1: Scaffold automation files

**Files:**
- Create: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- Create: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\tests\obsidian-auto-pr.Tests.ps1`

- [ ] Step 1: Create the automation directories.
- [ ] Step 2: Add a script skeleton with a param block and helper-function placeholders.
- [ ] Step 3: Add a Pester test file that dot-sources the script and exercises helper functions.

### Task 2: Build helper functions with TDD

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\tests\obsidian-auto-pr.Tests.ps1`

- [ ] Step 1: Write a failing test for lock acquisition and release.
- [ ] Step 2: Implement the minimal lock helpers to make the test pass.
- [ ] Step 3: Write a failing test for branch-name detection and commit-message formatting.
- [ ] Step 4: Implement the minimal git-state helpers to make the tests pass.
- [ ] Step 5: Run the focused Pester suite and keep it green.

### Task 3: Implement the GitHub automation flow

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- Modify: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\tests\obsidian-auto-pr.Tests.ps1`

- [ ] Step 1: Write a failing test for PR title/body helper generation.
- [ ] Step 2: Implement the helper functions for PR metadata.
- [ ] Step 3: Implement the orchestration path for status check, add/commit, push, and draft-PR ensure.
- [ ] Step 4: Run Pester again and keep the helper-level tests green.

### Task 4: Install the live automation

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\.gitignore`
- Create: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.log`

- [ ] Step 1: Ignore runtime-only automation artifacts.
- [ ] Step 2: Switch the vault repository to `obsidian/auto-sync` if needed.
- [ ] Step 3: Create or update the Scheduled Task to run every 15 minutes.

### Task 5: Verify end-to-end behavior

**Files:**
- Modify: `C:\Users\User\Documents\Obsidian Vault\...` as part of manual verification only

- [ ] Step 1: Run the Pester suite and confirm green.
- [ ] Step 2: Run the script manually with no vault changes and confirm it exits cleanly.
- [ ] Step 3: Make a note change, run the script manually, and confirm commit/push plus draft PR creation or reuse.
- [ ] Step 4: Restore the verification note edit or leave it intentionally if it represents a desired content change.
