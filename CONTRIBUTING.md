# Contributing Guide — Git Workflow

Welcome to the project! Follow this daily workflow to keep the codebase clean, reviewed, and conflict-free.

---

## Table of Contents

- [Daily Preparation](#daily-preparation)
- [Working & Committing](#working--committing)
- [Pushing to Remote](#pushing-to-remote)
- [Merging Safely](#merging-safely)
- [Quick Reference](#quick-reference)

---

## Daily Preparation

### 1. Switch to `main` and pull the latest code

Always start your day by syncing with the remote `main` branch before creating any new work.

```bash
git checkout main
git pull origin main
```

### 2. Create a feature branch

Never work directly on `main`. Create a dedicated branch for every task or feature.

```bash
git checkout -b yourname-feature-task
```

**Branch naming examples:**

```
alex-feature-login
priya-fix-navbar-bug
sam-task-api-integration
```

---

## Working & Committing

### 3. Stage, commit, and tag your work

Once you've completed a meaningful unit of work, stage and commit your changes with a clear message.

```bash
git add .
git commit -m "feat: completed login logic"
```

**Commit message conventions:**

| Prefix      | When to use                      |
| ----------- | -------------------------------- |
| `feat:`     | New feature                      |
| `fix:`      | Bug fix                          |
| `docs:`     | Documentation changes            |
| `refactor:` | Code cleanup, no behavior change |
| `chore:`    | Build process or tooling updates |

#### Tag completed milestones

After committing a significant milestone, create an annotated tag:

```bash
git tag -a v1.1-yourname -m "Version 1.1 by [YourName]"
```

---

## Pushing to Remote

### 4. Push your branch and tags

```bash
git push origin yourname-feature-task --tags
```

> The `--tags` flag ensures your version tags are pushed alongside your branch.

---

## Merging Safely

Follow these steps **in order** — do not merge your own PRs.

### Step 1 — Open a Pull Request (PR)

Go to the repository on **GitHub** and open a Pull Request from your feature branch into `main`.

- Write a clear PR title and description
- Reference any related issues if applicable

### Step 2 — Get Approval

**Maintainers** approve the PR\*\* before it can be merged. Address any review comments and push fixes to the same branch:

```bash
git add .
git commit -m "fix: address review comments"
git push origin yourname-feature-task
```

### Step 3 — Merge

Once approved, click **"Merge pull request"** on GitHub.

### Step 4 — Sync your local `main`

After the merge, both parties should update their local `main`:

```bash
git checkout main
git pull origin main
```

---

## Quick Reference

```bash
# --- Daily Start ---
git checkout main
git pull origin main
git checkout -b yourname-feature-task

# --- During Work ---
git add .
git commit -m "feat: describe what you did"

# --- Tag a Milestone ---
git tag -a v1.1-yourname -m "Version 1.1 by [YourName]"

# --- Push Everything ---
git push origin yourname-feature-task --tags

# --- After PR is Merged ---
git checkout main
git pull origin main
```

---
