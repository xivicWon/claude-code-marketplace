---
name: gitlab-mr
description: Create GitLab merge request with auto-generated comprehensive description
version: 1.0.0
updated: 2026-01-27
---

# GitLab Merge Request

Create a merge request with automatically generated comprehensive description that includes issue requirements, implementation summary, change statistics, and commit history.

## Usage

```bash
/gitlab-mr
```

The command will interactively ask you for:

1. **MR title** (e.g., "Add user dashboard")
2. **Link to issue number** (optional, e.g., 342 - for auto-close)
3. **Target branch** (default: main)

## What This Command Does

This command creates a professional merge request by:

1. ✅ **Handles uncommitted changes** (if any) with user choices
2. ✅ Analyzing git history of current branch vs target branch
3. ✅ Fetching linked issue details from GitLab (if issue number provided)
4. ✅ Generating comprehensive MR description with:
   - **Issue Summary**: title, status, labels, URL
   - **Requirements (요구사항)**: From issue description
   - **Implementation (구현 내용)**: Summary from commits
   - **Change Statistics**: Files changed, insertions, deletions
   - **Detailed Commit History**: With authors and dates
5. ✅ Creating merge request with `Closes #issue` for auto-close
6. ✅ Providing MR URL for quick access

### Dirty Working Directory Handling

If you have uncommitted changes when creating MR, you'll be prompted with options:

**Option 1: Commit to current branch (Recommended)**
- Add all changes
- Commit to current branch
- Create MR including these changes
- *Use case: "These changes are part of this MR!"*

**Option 2: Move to temporary branch**
- Stash your changes
- Create temporary branch with WIP changes
- Switch back to clean source branch
- Create MR without these changes
- *Use case: "I need to separate this work for later"*

**Option 3: Cancel**
- Abort MR creation

## Command Execution

The command invokes Claude to:

1. Ask interactive questions for MR details
2. Execute `${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py mr` with provided parameters
3. Report MR URL and linked issue status

## Auto-Generated MR Description

### Example Generated Description

```markdown
# 📋 Issue Summary

**Issue**: #342 - Add user dashboard
**Status**: opened
**Labels**: feature, dashboard
**URL**: http://gitlab.com/project/issues/342

## 📝 Requirements (요구사항)

[Full issue description showing what was requested]

- Create user dashboard page
- Display user statistics
- Add data visualization charts
- Implement filtering options

## ✅ Implementation (구현 내용)

### 주요 구현 사항:

1. Implement dashboard UI components
2. Add analytics API endpoints
3. Create dashboard routing
4. Add unit tests for dashboard
5. Update documentation

## 📊 Changes Summary

- **Files changed**: 12
- **Insertions**: +456
- **Deletions**: -23
- **Total commits**: 5

## 📜 Detailed Commit History

### 1. Implement dashboard UI components
- **Commit**: `abc12345`
- **Author**: John Doe
- **Date**: Mon Jan 27 10:30:00 2026 +0900

Added React components for dashboard layout and widgets.

---

### 2. Add analytics API endpoints
- **Commit**: `def67890`
- **Author**: Jane Smith
- **Date**: Mon Jan 27 11:00:00 2026 +0900

Implemented REST API for fetching user analytics data.

---

[... more commits ...]

Closes #342
```

## Example Workflow

```
# Current branch: vtm-1372/342-add-dashboard
# Work completed and pushed

You: /gitlab-mr

Claude: Creating GitLab merge request...

        MR title: Add user dashboard
        Link to issue number (optional, for auto-close): 342
        Target branch (default: main): main

        📝 Generating MR description from git history...
        ✅ Generated description with issue #342 requirements
        ✅ Analyzed 5 commits from vtm-1372/342-add-dashboard

        📊 Changes Summary:
        - Files changed: 12
        - Insertions: +456
        - Deletions: -23
        - Total commits: 5

        ✅ Created merge request !123: Add user dashboard
           Source: vtm-1372/342-add-dashboard → Target: main
           URL: http://gitlab.com/project/merge_requests/123
           Linked to issue #342 (will auto-close on merge)
```

## Link Issue for Auto-Close

When you provide an issue number:

- ✅ MR description includes `Closes #342`
- ✅ Issue automatically closes when MR is merged
- ✅ Issue requirements are fetched and displayed in MR description
- ✅ Easy comparison of requirements vs implementation

## Requirements vs Implementation

Perfect for code reviews - shows **what was requested** vs **what was delivered**:

**Section 1: Requirements (요구사항)**
- Extracted from the linked issue description
- Shows what the stakeholder requested

**Section 2: Implementation (구현 내용)**
- Extracted from commit messages
- Shows what the developer delivered

This helps reviewers verify:
1. ✅ All requirements were addressed
2. ✅ No scope creep occurred
3. ✅ Implementation matches expectations

## Create MR from Another Branch

If not on the source branch:

```bash
/gitlab-mr --source feature-branch --target main
```

Or let Claude know:

```
You: Create MR from feature-branch to main
```

## Keep Branch After Merge

By default, source branch is deleted after merge. To keep it:

```
You: Create MR and keep the branch after merge
```

Or:

```bash
/gitlab-mr --keep-branch
```

## Custom Description

To use custom description instead of auto-generated:

```
You: Create MR with custom description: "This MR fixes the login bug"
```

Or:

```bash
/gitlab-mr "Fix login" --description "Custom description here"
```

## When to Use

**Do use this command**:
- ✅ After completing your feature/fix
- ✅ After updating the issue (`/gitlab-issue-update`)
- ✅ Before requesting code review
- ✅ When ready to merge to main/develop

**Best Practice Workflow**:
```bash
# 1. Update issue with requirements
/gitlab-issue-update

# 2. Create MR with comprehensive description
/gitlab-mr
```

This ensures the MR description includes the latest issue requirements.

## Branch Name Validation

Source branch must follow format: `{issue-code}/{gitlab#}-{summary}`

**Valid Examples**:
- ✅ `VTM-1372/342-add-feature`
- ✅ `1372/343-fix-bug`

**Invalid Examples**:
- ❌ `342-feature` (missing issue code)
- ❌ `feature` (missing numbers)

## Conventional Commits Support

The command automatically cleans up Conventional Commits prefixes for better readability:

**Commit Messages**:
```
feat: implement dashboard UI
fix: resolve data loading issue
refactor: extract analytics logic
```

**Generated Implementation Section**:
```
## ✅ Implementation (구현 내용)

### 주요 구현 사항:

1. implement dashboard UI
2. resolve data loading issue
3. extract analytics logic
```

Supported prefixes: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`

## Environment Configuration

Required variables in `.claude/.env.gitlab-workflow`:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
BASE_BRANCH=main                 # Default target branch
```

Validate your setup:

```bash
/gitlab-doctor
```

## Common Errors

### ❌ Invalid Source Branch Name

**Error**:
```
Invalid source branch name: feature-branch
Branch name must follow format: [이슈코드]/[GitLab#]-[summary]
```

**Solution**: Branch must follow naming convention:
```bash
# Create properly named branch
/gitlab-issue-create
```

### ❌ No Commits Found

**Error**:
```
No commits found between main and vtm-1372/342-feature
```

**Solution**: Make sure you've made commits:
```bash
git add .
git commit -m "feat: implement feature"
git push

# Then create MR
/gitlab-mr
```

### ❌ Branch Not Pushed

**Error**:
```
Branch vtm-1372/342-feature not found on remote
```

**Solution**: Push your branch first:
```bash
git push -u origin vtm-1372/342-feature

# Then create MR
/gitlab-mr
```

### ❌ Issue Not Found

**Error**:
```
Could not fetch issue #342: Not found
```

**Solution**: Verify issue exists or create MR without linking:
```
MR title: Add feature
Link to issue number (optional): [leave empty]
```

## Complete Workflow Example

```bash
# 1. Create issue and branch
/gitlab-issue-create

# 2. Make changes
git add .
git commit -m "feat: implement feature"
git push

# 3. Update issue with requirements
/gitlab-issue-update

# 4. Create merge request
/gitlab-mr
```

## Related Commands

- `/gitlab-issue-create` - Create new issue and branch
- `/gitlab-issue-update` - Update issue description from commits
- `/gitlab-doctor` - Validate environment setup

## See Also

For detailed documentation:
- Skill version: `../skills/gitlab-mr/SKILL.md`
- MR description example: `../shared/references/MR_DESCRIPTION_EXAMPLE.md`
- Quick reference: `../shared/references/QUICK_REFERENCE.md`
