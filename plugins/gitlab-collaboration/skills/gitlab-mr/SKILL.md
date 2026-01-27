---
name: gitlab-mr
description: Create GitLab merge request with auto-generated comprehensive description. Analyzes git history, fetches linked issue details, generates MR description including issue summary, requirements, implementation details, change statistics, and commit history. Supports auto-close linked issues. Trigger when user mentions "create MR", "create merge request", "open MR", "submit for review", or similar merge request creation requests.
version: 1.0.0
updated: 2026-01-27
---

# GitLab Merge Request

Create merge request with auto-generated comprehensive description.

## Quick Usage

```bash
/gitlab-mr
```

This will ask you:
1. **MR title** (e.g., "Add user dashboard")
2. **Link to issue number** (optional, e.g., 342)
3. **Target branch** (default: main)

## What It Does

✅ Analyzes git history of your current branch
✅ Fetches linked issue details from GitLab
✅ Generates comprehensive MR description with:
  - **Issue summary** (title, status, labels, URL)
  - **Requirements** from issue description (요구사항)
  - **Implementation** summary from commits (구현 내용)
  - **Change statistics** (files, insertions, deletions)
  - **Detailed commit history** with authors and dates
✅ Creates merge request with auto-close link to issue
✅ Provides MR URL for quick access

## Example Workflow

```
# You've completed work on branch: vtm-1372/342-add-dashboard
# You've made commits and updated the issue
You: /gitlab-mr

Claude: Creating merge request...
        MR title: Add user dashboard
        Link to issue number (optional): 342
        Target branch (default: main): main

        📝 Generating MR description from git history...
        ✅ Fetched issue #342 details
        ✅ Analyzed 5 commits
        ✅ Generated comprehensive description

        ✅ Created MR !123
           URL: http://gitlab.com/project/merge_requests/123
           Linked to issue #342 (auto-close)
```

## MR Description Format

The auto-generated description includes:

### 1. Issue Summary
```markdown
## 📋 Related Issue
- **Issue**: #342 - Add user dashboard
- **Status**: opened
- **Labels**: feature, dashboard
- **URL**: http://gitlab.com/project/issues/342
```

### 2. Requirements (from issue)
```markdown
## 📝 Requirements (요구사항)
[Full issue description showing what was requested]
```

### 3. Implementation Summary
```markdown
## ✅ Implementation (구현 내용)
- Implement dashboard UI components
- Add analytics API endpoints
- Create dashboard routing
- Add unit tests for dashboard
- Update documentation
```

### 4. Change Statistics
```markdown
## 📊 Changes
- **Files changed**: 12
- **Insertions**: +456
- **Deletions**: -23
```

### 5. Commit History
```markdown
## 📜 Commit History
- `abc1234` feat: implement dashboard UI (John Doe, 2026-01-27)
- `def5678` feat: add analytics API (Jane Smith, 2026-01-27)
...
```

## Create MR without Interactive Mode

```bash
/gitlab-mr "Add user dashboard" --issue 342 --target main
```

## Link Issue for Auto-Close

When you provide an issue number, the MR will:
- ✅ Include `Closes #342` in description
- ✅ Auto-close the issue when MR is merged
- ✅ Fetch and display issue requirements

## Requirements vs Implementation

Perfect for code reviews - shows **what was requested** vs **what was delivered**:

- **요구사항 (Requirements)**: From the linked issue description
- **구현 내용 (Implementation)**: From your commit messages

This makes it easy for reviewers to verify:
1. All requirements were addressed
2. No scope creep occurred
3. Implementation matches expectations

## Advanced Options

**Custom source branch**:
```bash
/gitlab-mr "Title" --source my-branch --target main
```

**Keep branch after merge**:
```bash
/gitlab-mr "Title" --keep-branch
```

**Custom description**:
```bash
/gitlab-mr "Title" --description "Custom MR description"
```

## When to Use

Run this command:
- ✅ After completing your feature/fix
- ✅ After updating the issue (`/gitlab-issue-update`)
- ✅ Before requesting code review
- ✅ When ready to merge to main/develop

## Best Practices

1. **Update issue first**:
   ```bash
   /gitlab-issue-update
   /gitlab-mr
   ```
   This ensures MR description includes latest requirements.

2. **Link to issue**:
   Always provide issue number for auto-close and requirements tracking.

3. **Review before creating**:
   Check that your commits tell a clear story.

4. **Use conventional commits**:
   Clean commit messages generate better MR descriptions.

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
- `/gitlab-issue-update` - Update issue description from commits
- `/gitlab-doctor` - Validate environment

For complete documentation, see:
- `../../shared/references/COMMANDS.md` - Command reference
- `../../shared/references/MR_DESCRIPTION_EXAMPLE.md` - MR description examples

## Complete Workflow Example

```bash
# 1. Create issue and branch
/gitlab-issue-create
# → Issue #342 created, branch vtm-1372/342-add-dashboard

# 2. Make your changes
git add .
git commit -m "feat: implement dashboard UI"
git commit -m "feat: add analytics API"
git push

# 3. Update issue with requirements
/gitlab-issue-update
# → Issue #342 description updated

# 4. Create merge request
/gitlab-mr
# → MR !123 created with full description
```

Perfect workflow for clean, documented, reviewable code! 🚀
