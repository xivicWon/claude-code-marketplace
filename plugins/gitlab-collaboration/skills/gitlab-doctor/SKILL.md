---
name: gitlab-doctor
description: Validate GitLab workflow environment setup and configuration. Checks environment variables, git repository status, git remote configuration, GitLab API connectivity, token permissions, and issue directory. Provides actionable fixes for any issues found. Trigger when user mentions "validate gitlab setup", "check gitlab config", "gitlab troubleshoot", "test gitlab connection", or similar validation/troubleshooting requests.
version: 1.0.1
updated: 2026-01-27
type: command
---

# GitLab Workflow Doctor

Validate your GitLab workflow environment setup.

## Quick Usage

```bash
/gitlab-doctor
```

**Run this first** before using any GitLab workflow commands!

## What It Checks

### ✅ 1. Environment Variables

- `GITLAB_URL` - GitLab instance URL
- `GITLAB_TOKEN` - Personal Access Token
- `GITLAB_PROJECT` - Project ID or path
- `GITLAB_REMOTE` (optional) - Git remote name
- `ISSUE_DIR` (optional) - Issue JSON save directory

### ✅ 2. Git Repository

- Is current directory a git repository?
- Is git installed and accessible?

### ✅ 3. Git Remote

- Is remote configured?
- Is remote URL accessible?
- Does GITLAB_REMOTE match actual remotes?

### ✅ 4. GitLab API

- Can connect to GitLab instance?
- Is the URL correct?
- Is network accessible?

### ✅ 5. Project Access

- Does project exist?
- Does token have access to project?
- Is project path correct?

### ✅ 6. Token Permissions

- Does token have required `api` scope?
- Is token valid and not expired?

### ✅ 7. Issue Directory (optional)

- Is ISSUE_DIR path valid?
- Is directory writable?

## Example Output

```
You: /gitlab-doctor

Claude: Running GitLab Workflow diagnostics...

        ══════════════════════════════════════════════════════════════
        GitLab Workflow - Environment Doctor
        ══════════════════════════════════════════════════════════════

        ✅ Environment variables
           GITLAB_URL: http://192.168.210.103:90
           GITLAB_TOKEN: glpat-******* (configured)
           GITLAB_PROJECT: withvtm_2.0/withvtm-fe

        ✅ Git repository
           Current directory is a git repository
           Git version: 2.39.0

        ✅ Git remote
           Remote 'gitlab' found
           URL: http://192.168.210.103:90/withvtm_2.0/withvtm-fe.git

        ✅ GitLab API connectivity
           Successfully connected to GitLab
           API version: v4

        ✅ Project access
           Project found: withvtm_2.0/withvtm-fe
           Project ID: 123

        ✅ Token permissions
           Token has required 'api' scope

        ✅ Issue directory (optional)
           ISSUE_DIR: docs/requirements (writable)

        ══════════════════════════════════════════════════════════════
        ✅ All checks passed! Your environment is ready.
        ══════════════════════════════════════════════════════════════
```

## When Checks Fail

Doctor provides **actionable fixes** for each failure:

### ❌ Missing Environment Variable

```
❌ Environment variables
   Missing: GITLAB_TOKEN

Fix:
1. Create file: .claude/.env.gitlab-workflow
2. Add: GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
3. Get token from: GitLab → Settings → Access Tokens
```

### ❌ Not in Git Repository

```
❌ Git repository
   Not a git repository

Fix:
1. Run: git init
2. Or: cd to your git repository directory
```

### ❌ Missing Git Remote

```
❌ Git remote
   No remote named 'gitlab' found

Fix:
1. Add remote: git remote add gitlab http://192.168.210.103:90/project.git
2. Or set GITLAB_REMOTE=origin in .env.gitlab-workflow
```

### ❌ GitLab API Connection Failed

```
❌ GitLab API connectivity
   Connection refused to http://192.168.210.103:90

Fix:
1. Check GITLAB_URL is correct
2. Verify GitLab server is running
3. Check network connectivity: ping 192.168.210.103
```

### ❌ Project Not Found

```
❌ Project access
   Project 'withvtm_2.0/withvtm-fe' not found

Fix:
1. Verify project path is correct
2. Check project visibility (must be accessible to token user)
3. Format: namespace/project-name
```

### ❌ Insufficient Token Permissions

```
❌ Token permissions
   Token missing 'api' scope

Fix:
1. Go to GitLab → Settings → Access Tokens
2. Create new token with 'api' scope
3. Update GITLAB_TOKEN in .env.gitlab-workflow
```

## When to Run

Run doctor:

- ✅ **Before first use** - validate setup
- ✅ **After changing config** - verify changes
- ✅ **When errors occur** - diagnose issues
- ✅ **New environment** - initial setup check
- ✅ **Token expired** - verify credentials

## Environment File Location

Doctor looks for:

```
.claude/.env.gitlab-workflow
```

In your git repository root.

**Example file**:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
ISSUE_DIR=docs/requirements
```

## Getting GitLab Token

1. Go to your GitLab instance
2. Click your avatar → **Settings**
3. Navigate to **Access Tokens**
4. Create token:
   - **Name**: Claude GitLab Workflow
   - **Scopes**: Select `api`
   - **Expiration**: Set expiration date
5. Click **Create personal access token**
6. Copy the token immediately (won't be shown again)
7. Add to `.claude/.env.gitlab-workflow`:
   ```bash
   GITLAB_TOKEN=glpat-your-token-here
   ```

## Common Issues

### Issue: "git: command not found"

**Solution**: Install git

- macOS: `brew install git`
- Ubuntu: `sudo apt-get install git`

### Issue: "Permission denied"

**Solution**: Check token has access to project

- Token must have `api` scope
- User must have access to the project
- Project must be visible to token user

### Issue: "Network unreachable"

**Solution**: Check network and GitLab URL

- Verify GitLab server is running
- Check firewall settings
- Confirm GITLAB_URL format (include http:// or https://)

## Troubleshooting Workflow

```bash
# 1. Run doctor
/gitlab-doctor

# 2. Fix identified issues
# (Follow specific fixes from doctor output)

# 3. Run doctor again to verify
/gitlab-doctor

# 4. Proceed with workflow
/gitlab-issue-create
```

## See Also

- `/gitlab-issue-create` - Create new issue and branch
- `/gitlab-issue-update` - Update issue from commits
- `/gitlab-mr` - Create merge request

For complete documentation, see:

- `../../shared/references/COMMANDS.md` - Command reference
- `../../shared/references/DOCTOR_GUIDE.md` - Detailed doctor guide

## Quick Start

**First time setup**:

```bash
# 1. Create environment file
cat > .claude/.env.gitlab-workflow <<'EOF'
GITLAB_URL=http://your-gitlab.com
GITLAB_TOKEN=glpat-your-token-here
GITLAB_PROJECT=namespace/project-name
EOF

# 2. Validate setup
/gitlab-doctor

# 3. Start using workflow
/gitlab-issue-create
```

Doctor makes setup easy and catches issues early! 🏥
