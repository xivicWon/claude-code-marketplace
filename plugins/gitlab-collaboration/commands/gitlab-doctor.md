---
name: gitlab-doctor
description: Validate GitLab workflow environment setup and configuration
version: 1.0.0
updated: 2026-01-27
---

# GitLab Workflow Doctor

Run comprehensive environment validation for GitLab workflow.

## Usage

```bash
/gitlab-doctor
```

## What This Command Does

Executes the `gitlab_workflow.py doctor` command to validate your GitLab workflow environment setup.

### Checks Performed

1. **Environment Variables**
   - GITLAB_URL
   - GITLAB_TOKEN
   - GITLAB_PROJECT
   - GITLAB_REMOTE (optional)
   - ISSUE_DIR (optional)

2. **Git Repository**
   - Checks if current directory is a git repository
   - Verifies git is installed

3. **Git Remote**
   - Validates remote configuration
   - Checks remote URL accessibility

4. **GitLab API**
   - Tests connection to GitLab instance
   - Verifies API accessibility

5. **Project Access**
   - Confirms project exists
   - Validates token has access

6. **Token Permissions**
   - Verifies token has required 'api' scope

7. **Issue Directory**
   - Checks if ISSUE_DIR path is valid (optional)

8. **Working Directory**
   - Reports if there are uncommitted changes

## Command Execution

```bash
${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py doctor
```

The command will display a detailed report with:
- ✅ Passed checks
- ❌ Failed checks with actionable fixes
- ⚠️ Warnings for optional configurations

## Example Output

```
🏥 Running GitLab Workflow Doctor...

📋 Checking environment variables...
   ✅ GITLAB_URL: Set
   ✅ GITLAB_TOKEN: Set
   ✅ GITLAB_PROJECT: Set

📦 Checking Git repository...
   ✅ Git repository: Found

🌐 Checking Git remote...
   ✅ Git remote 'gitlab': http://192.168.210.103:90/project.git

🔌 Checking GitLab API connectivity...
   ✅ GitLab API: Connected
   ✅ Project: withvtm_2.0/withvtm-fe
   ✅ URL: http://192.168.210.103:90/withvtm_2.0/withvtm-fe

🔑 Checking GitLab token permissions...
   ✅ Token permissions: Valid (can read issues)
   ✅ Token user: your-username

📁 Checking issue directory...
   ✅ Issue directory: docs/requirements

🔍 Checking working directory status...
   ✅ Working directory: Clean (no uncommitted changes)

============================================================
✅ All checks passed! GitLab workflow is ready to use.

💡 Try: /gitlab-workflow create
============================================================
```

## When to Run

- **Before first use** - Validate initial setup
- **After configuration changes** - Verify new settings
- **When errors occur** - Diagnose issues
- **New environment** - Initial setup check
- **Token expired** - Verify credentials

## Environment Configuration

Doctor checks for configuration in:

```
.claude/.env.gitlab-workflow
```

Example configuration file:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
ISSUE_DIR=docs/requirements
BASE_BRANCH=main
```

## Troubleshooting

If checks fail, the doctor provides specific fixes for each issue:

### Missing Environment Variable
```
Fix:
1. Create file: .claude/.env.gitlab-workflow
2. Add: GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
3. Get token from: GitLab → Settings → Access Tokens
```

### Not in Git Repository
```
Fix:
1. Run: git init
2. Or: cd to your git repository directory
```

### GitLab API Connection Failed
```
Fix:
1. Check GITLAB_URL is correct
2. Verify GitLab server is running
3. Check network connectivity
```

## Related Commands

- `/gitlab-issue-create` - Create new issue and branch
- `/gitlab-issue-update` - Update issue from commits
- `/gitlab-mr` - Create merge request

## See Also

For detailed documentation:
- Skill version: `../skills/gitlab-doctor/SKILL.md`
- Doctor guide: `../shared/references/DOCTOR_GUIDE.md`
- Quick reference: `../shared/references/QUICK_REFERENCE.md`
