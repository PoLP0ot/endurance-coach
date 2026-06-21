---
name: github-pr-review
description: Conduct a structured PR review on GitHub following the team review process. Use when the user asks to review a pull request, do a PR review, or analyze a PR. Covers fetching the diff, presenting findings for approval, posting a pending draft review with inline comments via the GitHub API.
---

> Claude Code adaptation: migrated from `skills/github-pr-review/SKILL.md`. Use as a project skill under `.claude/skills/github-pr-review/SKILL.md`.

# GitHub PR Review

## Workflow (always follow in order)

### 1. Fetch the PR

```bash
gh pr view <number> --repo <owner>/<repo> --json title,body,files,commits,additions,deletions,headRefName,baseRefName
gh pr diff <number> --repo <owner>/<repo>
```

For file contents on the branch:

```bash
git fetch origin <branch>
git show origin/<branch>:<path/to/file>
```

### 2. Analyse and prepare findings

Categorise each finding as:

| Severity     | Meaning                                    |
| ------------ | ------------------------------------------ |
| **Blocking** | Must be fixed before merge                 |
| **Warning**  | Should be addressed, not strictly blocking |
| **Nit**      | Minor polish, author's discretion          |
| **Positive** | Worth explicitly calling out               |

Always include positive findings — they are useful feedback, especially for interns and junior devs. Skip them only for client-facing project reviews where the user explicitly says so.

### 3. Present findings for approval — BEFORE touching GitHub

Show the user:

- A summary of all findings (use a canvas for large reviews)
- The **exact text** of the review body and each inline comment as they will appear on GitHub

**Do not post anything to GitHub until the user explicitly confirms.**

### 4. Post as a PENDING draft review

Use `event="PENDING"` so the review is a draft the user submits manually.

```bash
# Create the pending review with the summary body and inline comments
gh api repos/<owner>/<repo>/pulls/<number>/reviews \
  --method POST \
  --field commit_id="<head_sha>" \
  --field event="PENDING" \
  --field body="<summary body>" \
  --field "comments[][path]=<file>" \
  --field "comments[][line]=<line>" \
  --field "comments[][side]=RIGHT" \
  --field "comments[][body]=<comment text>"
```

For additional inline comments after the review is created, use:

```bash
gh api repos/<owner>/<repo>/pulls/comments \
  --method POST \
  --field commit_id="<head_sha>" \
  --field path="<file>" \
  --field line=<line> \
  --field side="RIGHT" \
  --field body="<comment text>"
```

Get the head SHA with:

```bash
gh pr view <number> --repo <owner>/<repo> --json headRefOid -q '.headRefOid'
```

The user then opens GitHub, reviews the pending draft, and clicks **Submit review** themselves.

## Inline comment format

Prefix each comment with its severity tag:

```text
**[Blocking]** <title>

<explanation>

<suggestion for fixing>
```

```text
**[Warning]** ...
**[Nit]** ...
```

Positive comments need no prefix — write them directly as encouragement.

## Review body structure

```markdown
## Overall Assessment

<2–3 sentence summary of the PR quality and direction>

---

### What works well

- **<topic>** — <why it's good>

---

### Summary of findings

| ID  | Severity | Area   | Issue                  |
| --- | -------- | ------ | ---------------------- |
| B1  | Blocking | <area> | <one-line description> |
| W1  | Warning  | <area> | <one-line description> |
| N1  | Nit      | <area> | <one-line description> |
```

## Rules

- All text on GitHub must be in **English**.
- Never submit (`event="COMMENT"`, `"APPROVE"`, `"REQUEST_CHANGES"`) without explicit user confirmation.
- Always use `event="PENDING"` — the user submits the review manually.
- Inline comments must reference an actual line that exists in the PR diff. Verify line numbers from the branch before posting.
