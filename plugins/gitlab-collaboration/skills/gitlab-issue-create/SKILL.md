---
name: gitlab-issue-create
description: Create GitLab issue and branch automatically. Asks for issue code, title, description, and labels interactively, then creates GitLab issue, generates branch name, checks out branch, and optionally pushes to remote. Trigger when user mentions "create GitLab issue", "new GitLab issue", "start new feature", "create issue and branch", or similar issue creation requests.
version: 1.0.1
updated: 2026-01-27
type: command
---

# GitLab Issue Create

Create GitLab issue and branch in one command.

## Quick Usage

```bash
/gitlab-issue-create
```

This will ask you:

1. **이슈코드** (e.g., VTM-1372 or 1372)
2. **Issue title** (e.g., "Add user dashboard")
3. **Description** (optional, supports markdown)
4. **Labels** (optional, comma-separated)
5. **Create branch?** (yes/no, default: yes)
6. **Auto-push to remote?** (yes/no, only if creating branch)

## What It Does

✅ Creates GitLab issue with your title and description
✅ **Optionally** generates branch name: `{issue-code}/{gitlab-issue#}-{summary}`
✅ **Optionally** checks out new branch from main/master (or custom BASE_BRANCH)
✅ **Optionally** pushes branch to remote
✅ Saves issue.json for reference (if branch created)

## Example Workflow

```
You: /gitlab-issue-create

Claude: Creating new GitLab issue...
        이슈코드 (e.g., VTM-1372): VTM-1372
        Issue title: Add logout button
        Description (optional): Add logout functionality to navigation bar
        Labels (comma-separated, optional): feature,ui
        Create branch? (y/n, default: y): y
        Auto-push to remote? (y/n): y

        📝 Creating GitLab issue...
        ✅ Created issue #342: Add logout button
           URL: http://gitlab.com/project/issues/342

        🌿 Creating branch: vtm-1372/342-add-logout-button
        ✅ Created branch: vtm-1372/342-add-logout-button

        📤 Pushing branch to remote...
        ✅ Pushed branch: vtm-1372/342-add-logout-button

        📄 Saved issue.json: docs/requirements/vtm-1372/342/issue.json

        ✅ Workflow completed!
           Issue: #342 - Add logout button
           Branch: vtm-1372/342-add-logout-button
           Status: Pushed to remote
```

## Create from JSON File

If you have a pre-defined issue in JSON format:

```bash
/gitlab-issue-create --from-file docs/requirements/vtm-1372/342/issue.json
```

**JSON Format**:

```json
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Add logout functionality",
  "labels": ["feature", "ui"],
  "createBranch": true,
  "push": true
}
```

**Create issue only (no branch)**:

```json
{
  "issueCode": "VTM-1372",
  "title": "Document requirements",
  "description": "Gather and document requirements",
  "createBranch": false
}
```

## Branch Naming

Generated branches follow the format: `{issue-code}/{gitlab#}-{summary}`

**Examples**:

- `VTM-1372/342-add-logout-button`
- `1372/343-fix-login-bug`
- `1400/308-refactor-api`

## Next Steps

After creating issue and branch:

1. **Make your changes**

   ```bash
   git add .
   git commit -m "Implement logout button"
   ```

2. **Push commits**

   ```bash
   git push
   ```

3. **Update issue description** (recommended)

   ```bash
   /gitlab-issue-update
   ```

   This updates the issue description with requirements from your commits.

4. **Create merge request**
   ```bash
   /gitlab-mr
   ```
   This creates a merge request with auto-generated description.

## Environment Setup

Required environment variables in `.claude/.env.gitlab-workflow`:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
BASE_BRANCH=main                 # or: develop, origin/main, gitlab/develop
ISSUE_DIR=docs/requirements
```

**BASE_BRANCH**: Set the default base branch for creating new branches (default: `main`)

- Can be branch name only: `main`, `develop`, `master`
- Can include remote: `origin/main`, `gitlab/develop`
- Always creates from **remote** to ensure latest code

To validate your setup, run:

```bash
/gitlab-doctor
```

## Common Errors

### ❌ Working Directory Has Uncommitted Changes

```
Cannot create branch: Working directory has uncommitted changes

Modified/untracked files:
  - src/components/Dashboard.tsx
  - src/api/user.ts

Please commit or stash your changes first:
  git add .
  git commit -m 'Your message'
Or:
  git stash
```

**Solution**: Commit or stash your changes before creating a new branch:

```bash
# Option 1: Commit changes
git add .
git commit -m "WIP: current work"

# Option 2: Stash changes
git stash save "WIP: dashboard work"

# Then retry
/gitlab-issue-create
```

### ❌ Remote Branch Not Found

```
Remote branch 'gitlab/develop' not found
```

**Solution**: Check available remote branches and fix BASE_BRANCH:

```bash
# List remote branches
git branch -r

# Update .env with correct branch
# .claude/.env.gitlab-workflow
BASE_BRANCH=origin/main  # or whatever exists
```

### ❌ Invalid Branch Name

```
Invalid branch name: 342-feature
Branch name must follow format: [이슈코드]/[GitLab#]-[summary]
```

**Solution**: This shouldn't happen with auto-generated names, but if using custom branch name, follow the format: `VTM-1372/342-feature-name`

## See Also

- `/gitlab-issue-update` - Update issue from git history
- `/gitlab-mr` - Create merge request
- `/gitlab-doctor` - Validate environment

For complete documentation, see: `../../shared/references/`
