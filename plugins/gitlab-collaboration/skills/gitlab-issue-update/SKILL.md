---
name: gitlab-issue-update
description: Update GitLab issue description from git commit history. Auto-extracts issue number from current branch name, analyzes commits since divergence from main, generates requirements-focused summary, and updates issue description. Trigger when user mentions "update GitLab issue", "update issue description", "sync issue with commits", "update issue from commits", or similar issue update requests.
version: 1.0.1
updated: 2026-01-27
type: command
---

# GitLab Issue Update

Update GitLab issue description from your git commit history.

## Quick Usage

```bash
/gitlab-issue-update
```

**Auto-extracts issue number** from your current branch name!

- Branch: `vtm-1372/342-add-feature` → Issue: #342

## What It Does

✅ Auto-extracts GitLab issue number from branch name
✅ Analyzes all commits since divergence from main
✅ Generates requirements-focused summary (what needs to be done)
✅ Removes Conventional Commits prefixes (`feat:`, `fix:`)
✅ Updates GitLab issue description with formatted markdown

## Example Workflow

```
# You're on branch: vtm-1372/342-add-logout-button
# You've made commits:
git commit -m "feat: add logout API endpoint"
git commit -m "feat: add logout button UI component"
git push

# Update the issue description
You: /gitlab-issue-update

Claude: 📝 Analyzing git history...
        Current branch: vtm-1372/342-add-logout-button
        Extracted issue: #342

        Found 2 commits since main:
        - add logout API endpoint
        - add logout button UI component

        📝 Generated requirements summary:
        ## Requirements
        - Add logout API endpoint
        - Add logout button UI component

        ✅ Updated issue #342
           URL: http://gitlab.com/project/issues/342
```

## Update Specific Issue

If you want to update a specific issue (not auto-extracted):

```bash
/gitlab-issue-update 345
```

## Update Issue Title

To also update the issue title from the first commit:

```bash
/gitlab-issue-update --update-title
```

This updates both the description AND title.

## Requirements vs Implementation

**Important distinction**:

- **Issue description** (this command): Requirements - what needs to be done
- **MR description** (`/gitlab-mr`): Implementation - what was actually done

This separation allows:

- Clear requirements tracking in issues
- Implementation details in merge requests
- Easy comparison of requested vs delivered

## Advanced Usage

**Specify branch** (if not on the branch):

```bash
/gitlab-issue-update 342 --branch vtm-1372/342-feature
```

**Compare against different base branch**:

```bash
/gitlab-issue-update --base develop
```

## Branch Name Format

Branch must follow: `{issue-code}/{gitlab#}-{summary}`

**Examples that work**:

- ✅ `VTM-1372/342-add-feature`
- ✅ `1372/343-fix-bug`
- ✅ `1400/308-refactor`

**Won't work**:

- ❌ `342-add-feature` (missing issue code)
- ❌ `feature-name` (missing numbers)

## Conventional Commits Support

The command automatically cleans up Conventional Commits prefixes:

**Commit**:

```
feat: add user dashboard
fix: resolve login bug
```

**Issue Description**:

```
## Requirements
- Add user dashboard
- Resolve login bug
```

## When to Use

Run this command:

- ✅ After making commits (before creating MR)
- ✅ To keep issue description in sync with work
- ✅ To document requirements based on commits
- ❌ NOT for implementation details (use `/gitlab-mr` instead)

## Environment Setup

Required environment variables in `.claude/.env.gitlab-workflow`:

```bash
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe
```

To validate your setup, run:

```bash
/gitlab-doctor
```

## See Also

- `/gitlab-issue-create` - Create new issue and branch
- `/gitlab-mr` - Create merge request with implementation details
- `/gitlab-doctor` - Validate environment

For complete documentation, see: `../../shared/references/`
