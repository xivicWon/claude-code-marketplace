---
name: gitlab-issue-create
description: Create GitLab issue and branch automatically with interactive prompts
version: 1.0.0
updated: 2026-01-27
---

# GitLab Issue Create

Create a new GitLab issue and optionally create and push a branch in one command.

## Usage

```bash
/gitlab-issue-create
```

The command will interactively ask you for:

1. **이슈코드** (e.g., VTM-1372 or 1372)
2. **Issue title**
3. **Description** (optional)
4. **Labels** (optional, comma-separated)
5. **Create branch?** (yes/no)
6. **Auto-push to remote?** (yes/no, if branch created)

## What This Command Does

This command automates the complete workflow for starting new work:

1. ✅ Creates GitLab issue with title and description
2. ✅ **Handles uncommitted changes** (if any) with user choices
3. ✅ Generates branch name: `{issue-code}/{gitlab-issue#}-{summary}`
4. ✅ Creates and checks out new branch from base branch
5. ✅ Optionally pushes branch to remote
6. ✅ Saves issue.json for reference

### Dirty Working Directory Handling

If you have uncommitted changes when running this command, you'll be prompted with options:

**Option 1: Move changes to new branch (Recommended)**
- Stash your changes
- Create new branch from base
- Apply stashed changes to new branch
- *Use case: "These changes are for the new issue I'm creating!"*

**Option 2: Commit to current branch**
- Commit all changes to current branch
- Create clean new branch
- *Use case: "Let me save current work first, then start fresh"*

**Option 3: Cancel**
- Abort operation (issue will still be created if already created)

## Command Execution

The command invokes Claude to:

1. Ask interactive questions for issue details
2. Execute `${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py start` with provided parameters
3. Report results and next steps

## Branch Naming Format

Generated branches follow: `{issue-code}/{gitlab#}-{summary}`

**Examples**:
- Title: "Add logout button" → Branch: `vtm-1372/342-add-logout-button`
- Title: "Fix login bug" → Branch: `1372/343-fix-login-bug`
- Title: "사용자 대시보드" → Branch: `vtm-1372/344` (non-ASCII removed)

## Example Workflow

```
You: /gitlab-issue-create

Claude: Let me create a GitLab issue for you.

        이슈코드 (e.g., VTM-1372): VTM-1372
        Issue title: Add logout button
        Description (optional): Add logout functionality to navigation bar
        Labels (comma-separated, optional): feature,ui
        Create branch? (y/n, default: y): y
        Auto-push to remote? (y/n): y

        📝 Creating GitLab issue...
        ✅ Created issue #342: Add logout button
           URL: http://gitlab.com/project/issues/342

        ⚠️  Working directory has 3 uncommitted change(s)
           Current branch: main

           Modified files:
           - src/App.tsx
           - src/components/Nav.tsx
           - package.json

        📝 What would you like to do?
           1. Move changes to new branch (Recommended)
              → Stash → Create new branch → Apply stashed changes
           2. Commit to current branch (main)
              → Commit here → Create clean new branch
           3. Cancel

        👉 Choose (1/2/3): 1

        📦 Stashing changes...
        ✅ Stashed changes: Auto-stash for new issue branch

        🌿 Creating branch: vtm-1372/342-add-logout-button
        🔄 Fetching latest changes from gitlab...
        ✅ Created branch: vtm-1372/342-add-logout-button
           Based on: gitlab/main

        📦 Applying stashed changes to new branch...
        ✅ Applied stashed changes

        📤 Pushing branch to remote...
        ✅ Pushed branch: vtm-1372/342-add-logout-button

        📄 Saved issue.json: docs/requirements/vtm-1372/342-add-logout-button/issue.json

        ✅ Workflow completed!
           Issue: #342 - Add logout button
           Branch: vtm-1372/342-add-logout-button
           Status: Pushed to remote
```

## Create Issue Only (No Branch)

When asked "Create branch?", answer "no" to create only the issue:

```
Create branch? (y/n, default: y): n

📝 Creating GitLab issue...
✅ Created issue #342: Document requirements
   URL: http://gitlab.com/project/issues/342

⏸️  Branch creation skipped (issue only)

✅ Workflow completed!
   Issue: #342 - Document requirements
```

## Create from JSON File

For automated workflows, create from JSON file:

**File**: `docs/requirements/vtm-1372/342/issue.json`

```json
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Add logout functionality to navigation bar",
  "labels": ["feature", "ui"],
  "createBranch": true,
  "push": true
}
```

**Usage**:

```bash
# Claude will prompt for this during interaction:
From JSON file? (y/n): y
File path: docs/requirements/vtm-1372/342/issue.json
```

Or trigger it explicitly:

```
You: Create GitLab issue from docs/requirements/vtm-1372/342/issue.json

Claude: [Creates issue using JSON file]
```

## Environment Configuration

Required variables in `.claude/.env.gitlab-workflow`:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
BASE_BRANCH=main                 # Base branch for new branches
ISSUE_DIR=docs/requirements      # Where to save issue.json files
```

**BASE_BRANCH Options**:
- Branch name: `main`, `develop`, `master`
- With remote: `origin/main`, `gitlab/develop`
- Always creates from remote to ensure latest code

Validate your setup first:

```bash
/gitlab-doctor
```

## Next Steps After Creation

1. **Make your changes**:
   ```bash
   git add .
   git commit -m "feat: implement logout button"
   git push
   ```

2. **Update issue with requirements** (recommended):
   ```bash
   /gitlab-issue-update
   ```
   This analyzes your commits and updates the issue description with requirements.

3. **Create merge request**:
   ```bash
   /gitlab-mr
   ```
   This creates a merge request with auto-generated comprehensive description.

## Common Errors

### ❌ Working Directory Has Uncommitted Changes

**Error**:
```
Cannot create branch: Working directory has uncommitted changes

Modified/untracked files:
  - src/components/Dashboard.tsx
  - src/api/user.ts
```

**Solution**: Commit or stash your changes:
```bash
# Option 1: Commit
git add .
git commit -m "WIP: current work"

# Option 2: Stash
git stash save "WIP: dashboard work"

# Then retry
/gitlab-issue-create
```

### ❌ Remote Branch Not Found

**Error**:
```
Remote branch 'gitlab/develop' not found
```

**Solution**: Check available branches:
```bash
git branch -r
```

Update `.claude/.env.gitlab-workflow`:
```bash
BASE_BRANCH=origin/main  # Use existing remote branch
```

### ❌ Missing Environment Variables

**Error**:
```
Error: GitLab URL required (GITLAB_URL env var)
```

**Solution**: Create `.claude/.env.gitlab-workflow`:
```bash
GITLAB_URL=http://your-gitlab.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=namespace/project-name
```

Run `/gitlab-doctor` to validate.

### ❌ Invalid Token Permissions

**Error**:
```
Token permissions: Insufficient
Token missing 'api' scope
```

**Solution**:
1. Go to GitLab → Settings → Access Tokens
2. Create new token with **'api' scope**
3. Update GITLAB_TOKEN in `.claude/.env.gitlab-workflow`

## Related Commands

- `/gitlab-doctor` - Validate environment setup
- `/gitlab-issue-update` - Update issue from git commits
- `/gitlab-mr` - Create merge request

## See Also

For detailed documentation:
- Skill version: `../skills/gitlab-issue-create/SKILL.md`
- Quick reference: `../shared/references/QUICK_REFERENCE.md`
- Commands guide: `../shared/references/COMMANDS.md`
