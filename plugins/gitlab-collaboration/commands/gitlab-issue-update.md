---
name: gitlab-issue-update
description: Update GitLab issue description from git commit history
version: 1.0.0
updated: 2026-01-27
---

# GitLab Issue Update

Update GitLab issue description by analyzing git commit history and generating a requirements-focused summary.

## Usage

```bash
/gitlab-issue-update
```

**Auto-extracts issue number from current branch!**

Branch: `vtm-1372/342-add-feature` → Automatically updates Issue #342

## What This Command Does

This command automates issue documentation by:

1. ✅ Auto-extracts GitLab issue number from branch name pattern `{code}/{gitlab#}-{summary}`
2. ✅ Analyzes all commits since divergence from base branch (main/develop)
3. ✅ Generates requirements-focused markdown summary
4. ✅ Removes Conventional Commits prefixes (`feat:`, `fix:`, `refactor:`, etc.)
5. ✅ Updates GitLab issue description with formatted content

## Command Execution

The command invokes Claude to:

1. Extract issue number from current branch name
2. Execute `${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py update` with extracted parameters
3. Report updated issue URL

## Requirements vs Implementation

**Important distinction**:

- **Issue description** (this command): **Requirements** - what needs to be done
- **MR description** (`/gitlab-mr`): **Implementation** - what was actually done

This separation enables:
- Clear requirements tracking in issues
- Implementation details in merge requests
- Easy comparison of planned vs delivered features

## Example Workflow

```
# Current branch: vtm-1372/342-add-logout-button
# Recent commits:
git commit -m "feat: add logout API endpoint"
git commit -m "feat: add logout button UI component"
git push

You: /gitlab-issue-update

Claude: Updating GitLab issue from commit history...

        📌 Extracted issue IID from branch: #342
        📊 Analyzing branch: vtm-1372/342-add-logout-button
           Base branch: main

        Found 2 commits:
        1. add logout API endpoint
        2. add logout button UI component

        📝 Updating GitLab issue #342...
        ✅ Updated issue #342: Add logout button
           URL: http://gitlab.com/project/issues/342

        Issue description updated with requirements summary:
        # 브랜치: vtm-1372/342-add-logout-button

        ## 📋 변경 예정 사항

        ### 1. add logout API endpoint

        ---

        ### 2. add logout button UI component

        ---
```

## Update Specific Issue

Explicitly specify issue number:

```bash
/gitlab-issue-update 345
```

Or specify both issue and branch:

```bash
/gitlab-issue-update 342 --branch vtm-1372/342-feature
```

## Update Issue Title

Update both description AND title from first commit:

```bash
/gitlab-issue-update --update-title
```

The title will be extracted from the first commit subject (without conventional commit prefix).

## Custom Base Branch

Compare against a different base branch:

```bash
/gitlab-issue-update --base develop
```

Or with remote prefix:

```bash
/gitlab-issue-update --base origin/develop
```

## Branch Name Format

Branch must follow pattern: `{issue-code}/{gitlab#}-{summary}`

**Valid Examples**:
- ✅ `VTM-1372/342-add-feature`
- ✅ `1372/343-fix-bug`
- ✅ `1400/308-refactor-api`

**Invalid Examples**:
- ❌ `342-add-feature` (missing issue code)
- ❌ `add-feature` (missing numbers entirely)
- ❌ `VTM-1372-342` (wrong separator)

## Conventional Commits Support

The command automatically strips Conventional Commits prefixes for cleaner requirements:

**Commit Messages**:
```
feat: add user dashboard
fix: resolve login bug
refactor: extract validation logic
```

**Generated Issue Description**:
```
## 📋 변경 예정 사항

### 1. add user dashboard
---

### 2. resolve login bug
---

### 3. extract validation logic
---
```

Supported prefixes: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`

## When to Use

**Do use this command**:
- ✅ After making commits, before creating MR
- ✅ To keep issue description synchronized with work
- ✅ To document requirements based on actual commits
- ✅ When commits represent planned work items

**Don't use for**:
- ❌ Implementation details (use `/gitlab-mr` instead)
- ❌ After merging (issue should already be documented)

## Typical Workflow

1. **Create issue and branch**:
   ```bash
   /gitlab-issue-create
   ```

2. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: add logout functionality"
   git push
   ```

3. **Update issue description** (this command):
   ```bash
   /gitlab-issue-update
   ```

4. **Create merge request**:
   ```bash
   /gitlab-mr
   ```

## Environment Configuration

Required variables in `.claude/.env.gitlab-workflow`:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
BASE_BRANCH=main                 # Base branch for comparison (default: main)
```

Validate your setup:

```bash
/gitlab-doctor
```

## Common Errors

### ❌ Cannot Extract Issue Number

**Error**:
```
Cannot extract issue IID from branch name: feature-branch
```

**Solution**: Branch must follow `{code}/{gitlab#}-{summary}` format:
```bash
# Check current branch
git branch --show-current

# If wrong format, create proper branch
/gitlab-issue-create
```

### ❌ Issue Not Found

**Error**:
```
Project 'namespace/project' not found or issue #342 doesn't exist
```

**Solution**: Verify issue exists:
```bash
# Check GitLab web UI for issue #342
# Or create issue first:
/gitlab-issue-create
```

### ❌ No Commits Found

**Error**:
```
No commits found between main and vtm-1372/342-feature
```

**Solution**: Make commits first:
```bash
git add .
git commit -m "feat: implement feature"
git push

# Then update
/gitlab-issue-update
```

### ❌ Invalid Token Permissions

**Error**:
```
Token permissions: Insufficient
```

**Solution**: Token needs `api` scope:
1. GitLab → Settings → Access Tokens
2. Create token with **'api' scope**
3. Update GITLAB_TOKEN in `.claude/.env.gitlab-workflow`

## Related Commands

- `/gitlab-issue-create` - Create new issue and branch
- `/gitlab-mr` - Create merge request (shows implementation)
- `/gitlab-doctor` - Validate environment setup

## See Also

For detailed documentation:
- Skill version: `../skills/gitlab-issue-update/SKILL.md`
- Update summary guide: `../shared/references/UPDATE_SUMMARY.md`
- Quick reference: `../shared/references/QUICK_REFERENCE.md`
