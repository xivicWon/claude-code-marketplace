---
name: gitlab-init
description: Initialize GitLab workflow with interactive environment setup
version: 1.0.0
updated: 2026-01-27
triggers:
  - User mentions "initialize gitlab", "setup gitlab", "gitlab init", "configure gitlab workflow"
  - User asks to create .env file for GitLab
  - User wants to set up GitLab credentials
  - New user setting up the plugin for the first time
---

# GitLab Workflow Initialization Skill

Guide users through interactive GitLab workflow environment setup by creating `.claude/.env.gitlab-workflow` configuration file.

## When to Use This Skill

This skill should be invoked when:
- User explicitly runs `/gitlab-init` command
- User mentions initializing or setting up GitLab workflow
- User asks how to configure GitLab credentials
- User needs to create or update `.env.gitlab-workflow` file
- User is setting up the plugin for the first time
- User wants to change GitLab project or credentials

## Core Workflow

### Step 1: Check Existing Configuration

First, check if configuration file already exists:

```bash
ls -la .claude/.env.gitlab-workflow
```

If file exists:
- Inform user that configuration already exists
- Ask if they want to:
  - **Backup and create new** (recommended)
  - **Overwrite** existing file
  - **Cancel** and keep current configuration

If backing up, create backup:
```bash
cp .claude/.env.gitlab-workflow .claude/.env.gitlab-workflow.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 2: Run Python Init Script

Execute the initialization script which handles interactive prompts:

```bash
${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py init
```

**Important**: The Python script handles:
- Interactive prompts for all configuration values
- Input validation
- File creation with secure permissions
- Automatic validation via doctor command

### Step 3: Script Interaction Flow

The Python script will interactively collect:

**Required Fields:**
1. **GITLAB_URL**
   - Example: `https://gitlab.com` or `http://192.168.210.103:90`
   - Validation: Must be valid URL format
   - Help text: "GitLab instance URL (e.g., https://gitlab.com)"

2. **GITLAB_TOKEN**
   - Example: `glpat-xxxxxxxxxxxxxxxxxxxx`
   - Validation: Must start with `glpat-` for GitLab tokens
   - Help text: "Personal Access Token (get from: GitLab → Settings → Access Tokens, scope: 'api')"
   - Security: Input is masked/hidden

3. **GITLAB_PROJECT**
   - Example: `withvtm_2.0/withvtm-fe` or `namespace/project-name`
   - Validation: Must contain namespace/project format
   - Help text: "Project path (format: namespace/project-name)"

**Optional Fields** (press Enter for defaults):
4. **GITLAB_REMOTE**
   - Default: auto-detect from 'gitlab' or 'origin'
   - Example: `gitlab`, `origin`
   - Help text: "Git remote name [default: auto-detect]"

5. **ISSUE_DIR**
   - Default: `docs/requirements`
   - Example: `docs/requirements`, `docs/issues`
   - Help text: "Directory to save issue.json files [default: docs/requirements]"

6. **BASE_BRANCH**
   - Default: `main`
   - Example: `main`, `develop`, `master`
   - Help text: "Base branch for creating new branches [default: main]"

### Step 4: Post-Creation Actions

After the Python script creates the configuration file:

1. **Verify File Creation**
   ```bash
   ls -la .claude/.env.gitlab-workflow
   ```
   - Check file exists
   - Verify permissions are 600 (owner read/write only)

2. **Display Configuration Summary**
   Show user what was configured (without exposing token):
   ```
   ✅ Configuration saved to: .claude/.env.gitlab-workflow

   Settings:
   - GitLab URL: http://192.168.210.103:90
   - Project: withvtm_2.0/withvtm-fe
   - Token: glpat-*********************xxx (last 3 chars shown)
   - Remote: gitlab
   - Issue Dir: docs/requirements
   - Base Branch: main
   ```

3. **Auto-Run Doctor Validation**
   The Python script automatically runs doctor validation.
   If it doesn't, manually trigger:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py doctor
   ```

4. **Show Next Steps**
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✨ Setup Complete!

   Next Steps:
     1. Try: /gitlab-doctor         # Verify setup anytime
     2. Try: /gitlab-issue-create   # Create first issue
     3. Read: plugins/gitlab-collaboration/README.md

   💡 Tip: Your token is securely stored with 600 permissions
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

## Getting Personal Access Token

When user asks how to get token, guide them:

1. **Navigate to GitLab:**
   - Go to your GitLab instance (e.g., http://192.168.210.103:90)
   - Click your avatar (top-right) → **Settings**

2. **Access Tokens Page:**
   - Left sidebar → **Access Tokens**

3. **Create New Token:**
   - Click **Add new token**
   - **Token name**: `claude-gitlab-workflow` (or any descriptive name)
   - **Scopes**: Check ✅ **api** (required for full API access)
   - **Expiration date**: Set as needed (optional but recommended)

4. **Generate and Copy:**
   - Click **Create personal access token**
   - **IMPORTANT**: Copy the token immediately (shown only once!)
   - Token format: `glpat-xxxxxxxxxxxxxxxxxxxx`

5. **Use in Init:**
   - Paste the token when prompted by `/gitlab-init`

## Security Best Practices

### File Permissions
The Python script automatically sets:
```bash
chmod 600 .claude/.env.gitlab-workflow
```
This ensures only the owner can read/write the file.

### .gitignore
Ensure `.claude/.env.gitlab-workflow` is gitignored:

```bash
# Check if .gitignore exists
if grep -q ".env.gitlab-workflow" .gitignore 2>/dev/null; then
    echo "✅ Already in .gitignore"
else
    echo ".claude/.env.gitlab-workflow" >> .gitignore
    echo "✅ Added to .gitignore"
fi
```

### Token Rotation
When token expires or needs rotation:
1. Generate new token in GitLab
2. Run `/gitlab-init` again
3. Old backup is automatically created
4. Enter new token when prompted

## Troubleshooting

### Issue: .claude directory doesn't exist
**Solution**: The Python script automatically creates it:
```bash
mkdir -p .claude
chmod 700 .claude
```

### Issue: Permission denied when creating file
**Solution**: Check directory permissions:
```bash
ls -la .claude
chmod 700 .claude
```

### Issue: Want to manually edit configuration
**Solution**: User can edit directly:
```bash
# Use example as template
cp plugins/gitlab-collaboration/.env.gitlab-workflow.example .claude/.env.gitlab-workflow

# Edit the file
# Then validate
/gitlab-doctor
```

### Issue: Script not executable
**Solution**: Make script executable:
```bash
chmod +x plugins/gitlab-collaboration/shared/scripts/gitlab_workflow.py
```

### Issue: Python not found
**Solution**: Check Python installation:
```bash
which python3
# or
which python
```

### Issue: Want to reset configuration
**Solution**:
```bash
rm .claude/.env.gitlab-workflow
/gitlab-init
```

## Configuration File Format

The generated `.claude/.env.gitlab-workflow` follows this format:

```bash
# GitLab Workflow Environment Configuration
# Generated by: /gitlab-init on 2026-01-27

# Required - GitLab instance URL
GITLAB_URL=http://192.168.210.103:90

# Required - Personal Access Token (must have 'api' scope)
# Get from: GitLab → Settings → Access Tokens
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx

# Required - Project ID or path (format: namespace/project-name)
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional - Git remote name (default: auto-detect from 'gitlab' or 'origin')
GITLAB_REMOTE=gitlab

# Optional - Directory to save issue.json files (default: docs/requirements)
ISSUE_DIR=docs/requirements

# Optional - Base branch for creating new branches (default: main)
# Can be branch name only or include remote name
# Examples:
#   BASE_BRANCH=main              # Uses default remote (gitlab or origin)
#   BASE_BRANCH=develop           # Uses default remote
#   BASE_BRANCH=origin/main       # Explicitly use origin remote
#   BASE_BRANCH=gitlab/develop    # Explicitly use gitlab remote
BASE_BRANCH=main
```

## Validation After Init

After successful initialization, the Python script automatically runs validation.
If manual validation needed:

```bash
${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py doctor
```

Doctor checks:
- ✅ All required environment variables are set
- ✅ Git repository exists
- ✅ Git remote is configured
- ✅ GitLab API is accessible
- ✅ Token has valid permissions
- ✅ Project exists and is accessible
- ✅ Issue directory is valid (if set)

## Integration with Other Commands

After successful init, users can immediately use:

1. **`/gitlab-doctor`**
   - Verify configuration anytime
   - Diagnose issues
   - Check connectivity

2. **`/gitlab-issue-create`**
   - Create new GitLab issue
   - Generate branch from issue
   - Save issue.json to ISSUE_DIR

3. **`/gitlab-issue-update`**
   - Update issue description from commits
   - Auto-extract issue number from branch

4. **`/gitlab-mr`**
   - Create merge request
   - Auto-generate description
   - Link to issues

## Example Usage Flow

### First Time Setup
```
User: "I need to set up GitLab workflow"
Assistant: [Invokes gitlab-init skill]
  → Runs: /gitlab-init command
  → Script prompts for configuration
  → Creates .claude/.env.gitlab-workflow
  → Auto-validates with doctor
  → Shows next steps
```

### Updating Configuration
```
User: "I need to update my GitLab token"
Assistant: [Invokes gitlab-init skill]
  → Detects existing configuration
  → Backs up to .env.gitlab-workflow.backup.20260127_143022
  → Runs: /gitlab-init
  → Prompts for new values (can press Enter to keep existing)
  → Validates new configuration
```

### Manual Configuration Check
```
User: "Is my GitLab setup correct?"
Assistant: [Invokes gitlab-doctor skill]
  → Runs: /gitlab-doctor
  → Shows validation results
  → Suggests running /gitlab-init if issues found
```

## Progressive Disclosure

This skill provides:
- **Level 1**: Basic command execution for simple init
- **Level 2**: Guidance on getting access tokens
- **Level 3**: Security best practices and troubleshooting
- **Level 4**: Manual configuration and advanced scenarios

Only expose deeper levels when user asks or encounters issues.

## Related Skills

- **gitlab-doctor**: Validate configuration after init
- **gitlab-issue-create**: First workflow command to try after init
- **gitlab-issue-update**: Update existing issues
- **gitlab-mr**: Create merge requests

## Command Reference

Primary command invocation:
```bash
${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py init
```

Related commands:
```bash
# Validate after init
${CLAUDE_PLUGIN_ROOT}/shared/scripts/gitlab_workflow.py doctor

# Check if file exists
ls -la .claude/.env.gitlab-workflow

# Backup existing configuration
cp .claude/.env.gitlab-workflow .claude/.env.gitlab-workflow.backup.$(date +%Y%m%d_%H%M%S)

# View configuration (be careful with token!)
cat .claude/.env.gitlab-workflow
```

## Success Criteria

Initialization is successful when:
1. ✅ `.claude/.env.gitlab-workflow` file created
2. ✅ File has 600 permissions (owner only)
3. ✅ All required fields are populated
4. ✅ Doctor validation passes all checks
5. ✅ User can proceed with other GitLab commands

## References

- Command documentation: `../commands/gitlab-init.md`
- Configuration example: `../.env.gitlab-workflow.example`
- Doctor guide: `../shared/references/DOCTOR_GUIDE.md`
- Quick reference: `../shared/references/QUICK_REFERENCE.md`
