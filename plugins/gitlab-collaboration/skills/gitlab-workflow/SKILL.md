---
name: gitlab-workflow
description: Complete GitLab workflow automation with interactive questions or JSON file input. Creates issues, generates lowercase branches ({asana}/{gitlab}-{summary}), auto-saves issue.json, and updates issues from git history with auto-extracted issue numbers. Focuses on requirements (not results) for issue updates. Supports MR creation with auto-close. Includes comprehensive environment validation with doctor command. Trigger when user mentions "GitLab workflow", "create issue", "update issue", "start working", "create MR", "validate setup", or similar workflow requests.
version: 3.2.0
updated: 2026-01-22
---

# GitLab Workflow Automation

Complete automation for GitLab issue → branch → merge request workflow with support for interactive questions or JSON file input.

## Quick Start

### Method 1: Interactive (Recommended for Ad-hoc Issues)
```bash
/gitlab-workflow create
```

### Method 2: From JSON File (Recommended for Planned Features)
```bash
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json
```

### Method 3: Update Issue (Auto-extracts issue number from branch)
```bash
/gitlab-workflow update
```

### Method 4: Create MR (Auto-generates description)
```bash
/gitlab-workflow mr
```

### Method 5: Validate Setup (Check environment)
```bash
/gitlab-workflow doctor
```

## What This Skill Does

### Create Workflow
When you run `/gitlab-workflow create`, it automatically:
1. ✅ **Creates GitLab issue** with title, description, and labels
2. ✅ **Generates branch name** following `{asana}/{gitlab}-{summary}` format (lowercase)
3. ✅ **Checks out new branch** locally from main/master
4. ✅ **Pushes to remote** (with confirmation prompt)
5. ✅ **Saves issue.json** in `docs/requirements/{asana}/{gitlab}/issue.json`
6. ✅ **Provides issue/branch URLs** for quick access

### Update Workflow
When you run `/gitlab-workflow update` (no issue number needed), it automatically:
1. ✅ **Extracts issue number** from current branch name (e.g., `vtm-1372/345-feature` → #345)
2. ✅ **Analyzes git commits** to understand what changes are planned
3. ✅ **Generates requirements summary** focused on what needs to be done (not results)
4. ✅ **Updates GitLab issue** description with the requirements
5. ✅ **Optionally updates title** from the first commit (use `--update-title`)

**Focus**: The summary describes **requirements and changes to be made**, not implementation results.

### MR (Merge Request) Workflow ✨ NEW
When you run `/gitlab-workflow mr`, it automatically:
1. ✅ **Analyzes git history** of your branch compared to target branch
2. ✅ **Fetches issue details** if issue number is provided
3. ✅ **Generates comprehensive MR description** with:
   - Issue summary (title, status, labels, URL)
   - Requirements from issue description (요구사항)
   - Implementation summary from commits (구현 내용)
   - Change statistics (files, insertions, deletions)
   - Detailed commit history with authors and dates
4. ✅ **Creates merge request** with auto-generated description
5. ✅ **Links to issue** (auto-closes issue when MR is merged)
6. ✅ **Provides MR URL** for quick access

**Branch Format**: `{Asana}/{GitLab#}-{summary}`
- Asana: Any format (e.g., `VTM-1372`, `1372`, `1400`)
- GitLab#: Auto-generated issue number
- Summary: Auto-generated from title (or custom)

**Examples**:
- `VTM-1372/342-add-user-dashboard`
- `1372/343-fix-login-bug`
- `1400/308-refactor-api`

### Doctor (Environment Validation) ✨ NEW
When you run `/gitlab-workflow doctor`, it automatically:
1. ✅ **Checks environment variables** (GITLAB_URL, GITLAB_TOKEN, GITLAB_PROJECT)
2. ✅ **Validates Git repository** (checks if in a git repo and git is installed)
3. ✅ **Verifies Git remote** (checks remote configuration)
4. ✅ **Tests GitLab API connectivity** (verifies connection and project access)
5. ✅ **Validates token permissions** (checks if token has required 'api' scope)
6. ✅ **Checks issue directory** (optional, verifies custom issue.json save location)
7. ✅ **Provides actionable fixes** for any issues found

**Use this before starting to ensure everything is set up correctly!**

---

## 🚀 Features

### ✨ Interactive Mode
- Guided step-by-step questions
- No need to remember syntax
- Real-time validation
- Best for quick, one-off issues

### 📄 JSON File Mode
- Version-controlled issue definitions
- Reproducible issue creation
- Template reuse
- Best for planned features with documentation

### 🔗 Automatic Branch Creation
- Follows project naming conventions
- Auto-sanitizes non-ASCII characters
- Validates format before creation
- Checkout from latest main/master

### 🎯 Smart Push Handling
- Confirmation prompt before pushing
- Auto-detects correct remote (origin/gitlab)
- Sets upstream tracking automatically
- Skippable for draft work

### 📝 Issue Update Support ✨ NEW
- **Auto-extracts issue number from branch name** - No manual input needed
- **Requirements-focused summaries** - Describes what needs to be done, not results
- **Conventional Commits support** - Automatically removes `feat:`, `fix:` prefixes
- Updates issue description with formatted markdown
- Optional title updates from first commit

### 🔄 Merge Request Support
- **Auto-generates MR description from git history** with statistics
- Links MR to issue (auto-close on merge)
- Customizable source/target branches
- Auto-removes source branch after merge
- Includes commit summary and detailed statistics

---

## 📋 Commands Reference

### Interactive Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `/gitlab-workflow doctor` | Validate environment setup and configuration | **Before first use or troubleshooting** |
| `/gitlab-workflow help` | Show comprehensive usage help and examples | **When you need command reference** |
| `/gitlab-workflow create` | Interactive: Ask questions → create issue + branch | Quick, ad-hoc issues |
| `/gitlab-workflow create --from-file <path>` | JSON: Load from file → create issue + branch | Planned features with docs |
| `/gitlab-workflow update` | Update issue from git history (auto-extracts issue #) | After making commits |
| `/gitlab-workflow mr` | Interactive: Ask questions → create merge request | After completing work |

### CLI Commands (Advanced)

```bash
# Validate environment setup
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py doctor

# Start workflow with all options
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  --asana VTM-1372 start "Issue title" \
  --description "Details here" \
  --labels "bug,feature" \
  --push

# Create from JSON file
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  start --from-file docs/requirements/vtm-1372/342/issue.json

# Create branch only (no issue)
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  branch VTM-1372/342-feature-name --push

# Push current branch
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py push

# Update issue from git history (auto-extracts issue number)
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update

# Update specific issue
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update 345

# Update with title change
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update --update-title

# Create merge request
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  mr "MR title" --issue 342 --target main
```

---

## 📝 JSON File Format

### Basic Structure

```json
{
  "asana": "VTM-1372",
  "title": "조치 담당자 해제 기능 추가",
  "description": "취약점 상세 페이지에서 조치 담당자를 해제할 수 있는 기능을 추가합니다.",
  "labels": ["enhancement", "feature"],
  "push": true
}
```

### Field Reference

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `asana` | string | ✅ | Asana issue identifier | `"VTM-1372"`, `"1372"` |
| `title` | string | ✅ | GitLab issue title | `"Add user dashboard"` |
| `description` | string | ❌ | Issue description (markdown) | `"## Overview\nDetails..."` |
| `labels` | array/string | ❌ | Issue labels | `["bug", "feature"]` or `"bug,feature"` |
| `push` | boolean | ❌ | Auto-push to remote | `true` (default: `false`) |

### JSON Examples

**Minimal**:
```json
{
  "asana": "VTM-1372",
  "title": "Fix login bug"
}
```

**With Markdown Description**:
```json
{
  "asana": "1372",
  "title": "Add user dashboard",
  "description": "Create a new dashboard for user analytics.\n\n## Features\n- Daily active users\n- Session duration",
  "labels": ["feature", "dashboard"],
  "push": true
}
```

**Template Location**:
- Schema: `.claude/skills/gitlab-workflow/issue-template.json`
- Example: `docs/requirements/vtm-1372/342/issue.json`

---

## ⚙️ Setup

### 1. Create Environment File

Create `.claude/.env.gitlab-workflow`:

```bash
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe
GITLAB_REMOTE=gitlab
```

### 2. Get GitLab Token

1. Go to GitLab → User Settings → Access Tokens
2. Create token with `api` scope
3. Copy token to `.env.gitlab-workflow`

### 3. Verify Setup

**✨ NEW: Use the doctor command to validate everything at once!**

```bash
# Recommended: Run doctor to validate all setup
/gitlab-workflow doctor

# Or manually check each component:
# Check environment
cat .claude/.env.gitlab-workflow

# Check git remote
git remote -v

# Test connection (optional)
curl -H "PRIVATE-TOKEN: your-token" \
  http://192.168.210.103:90/api/v4/projects/withvtm_2.0%2Fwithvtm-fe
```

The `doctor` command will check all of these automatically and provide actionable fixes for any issues.

---

## 🎯 Complete Workflows

### Workflow 1: Interactive Mode

```bash
# 1. Start workflow
/gitlab-workflow create

# Claude asks:
# → Asana issue? VTM-1372
# → Title? Add user dashboard
# → Description? (optional)
# → Labels? feature,dashboard
# → Auto-push? yes

# Result:
# ✅ Created issue #342
# ✅ Created branch: VTM-1372/342-add-user-dashboard
# ✅ Pushed to gitlab

# 2. Make changes
git add .
git commit -m "Implement dashboard UI"

# 3. Push changes
git push

# 4. Update issue with requirements (optional but recommended)
/gitlab-workflow update
# → Auto-extracts issue #342 from branch name
# → Updates issue description with requirements summary

# 5. Create merge request
/gitlab-workflow mr

# Claude asks:
# → MR title? Add user dashboard
# → Link to issue? 342
# → Target branch? main

# Result:
# 📝 Generating MR description from git history...
# ✅ Generated description from vtm-1372/342-add-user-dashboard commits
# ✅ Created MR !123
# ✅ Linked to issue #342 (auto-close)
# ✅ MR includes commit summary and statistics
```

### Workflow 2: JSON File Mode

```bash
# 1. Create issue definition
cat > docs/requirements/vtm-1372/342/issue.json <<'EOF'
{
  "asana": "VTM-1372",
  "title": "Add user dashboard",
  "description": "Create analytics dashboard\n\n## Features\n- DAU chart\n- Session stats",
  "labels": ["feature", "dashboard"],
  "push": true
}
EOF

# 2. Create issue and branch
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json

# Result:
# 📄 Loaded from: docs/requirements/vtm-1372/342/issue.json
# ✅ Created issue #342
# ✅ Created branch: VTM-1372/342-add-user-dashboard
# ✅ Pushed to gitlab

# 3. Make changes
git add .
git commit -m "Implement dashboard"
git push

# 4. Update issue with requirements (optional but recommended)
/gitlab-workflow update
# → Auto-extracts issue #342 from branch name
# → Updates issue description with requirements summary

# 5. Create MR (auto-generates description from commits)
/gitlab-workflow mr

# Result:
# 📝 Generating MR description from git history...
# ✅ Generated description with commit summary
# ✅ Created MR with full change details
```

### Workflow 3: Branch Only (Existing Issue)

```bash
# Create branch from existing GitLab issue
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  branch VTM-1372/342-fix-bug --push
```

---

## 🔧 Branch Naming Rules

### ✅ Valid Formats

| Format | Example | Description |
|--------|---------|-------------|
| `{prefix}/{number}-{summary}` | `VTM-1372/342-add-feature` | Full format with prefix |
| `{number}/{number}-{summary}` | `1372/342-fix-bug` | Numeric Asana ID |
| `{prefix}/{number}` | `VTM-999/342` | Minimal format |
| `{number}/{number}` | `1372/342` | Minimal numeric |

### ❌ Invalid Formats

| Format | Issue |
|--------|-------|
| `342-feature` | Missing Asana identifier |
| `feature-name` | Missing issue numbers |
| `1372-342-feature` | Wrong separator (use `/`) |
| `VTM1372/342` | Missing hyphen in Asana |

### Validation

The script validates branch names before creation:
- Must contain `/` separator
- GitLab part must be numeric
- Asana part can be any format
- Summary is optional but recommended

---

## 💡 Best Practices

### When to Use Interactive Mode
- ✅ Quick bug fixes
- ✅ Unplanned tasks
- ✅ Learning the workflow
- ✅ One-off issues

### When to Use JSON File Mode
- ✅ Planned features
- ✅ Documented requirements
- ✅ Template-based issues
- ✅ Reproducible workflows
- ✅ Team collaboration

### JSON File Organization

Recommended structure:
```
docs/
└── requirements/
    └── vtm-{asana}/
        └── {gitlab-issue}/
            ├── issue.json          # Issue definition
            ├── requirements.md     # Detailed specs
            ├── plan.md            # Implementation plan
            └── assets/            # Screenshots, diagrams
```

Example:
```
docs/requirements/
├── vtm-1372/
│   ├── 342/
│   │   ├── issue.json
│   │   ├── requirements.md
│   │   └── plan.md
│   └── 343/
│       ├── issue.json
│       └── requirements.md
└── vtm-1400/
    └── 308/
        ├── issue.json
        └── requirements.md
```

### Issue Title Guidelines
- ✅ Clear and specific: "Add user logout button"
- ✅ Action-oriented: "Fix login validation bug"
- ✅ Korean/English both supported
- ❌ Vague: "Update UI", "Fix bug"
- ❌ Too long: > 80 characters

### Label Conventions
- **Type**: `feature`, `bug`, `enhancement`, `refactoring`
- **Priority**: `critical`, `high`, `medium`, `low`
- **Area**: `frontend`, `backend`, `api`, `ui`
- **Status**: `in-progress`, `blocked`, `needs-review`

---

## 🐛 Troubleshooting

### ✨ Quick Diagnosis

**First, run the doctor command to identify issues:**

```bash
/gitlab-workflow doctor
```

The doctor will check all your setup and provide specific fixes for any problems.

---

### Issue Not Created

**Symptoms**: API error when creating issue

**Solutions**:
1. Check GitLab API access:
   ```bash
   curl http://192.168.210.103:90/api/v4/projects
   ```
2. Verify token has `api` scope
3. Confirm project path:
   - Frontend: `withvtm_2.0/withvtm-fe`
   - Backend: `withvtm_2.0/withvtm_2.0-be`
4. Check token expiration

### Branch Name Invalid

**Symptoms**: "Invalid branch name" error

**Solutions**:
1. Follow format: `{asana}/{gitlab}-{summary}`
2. Ensure GitLab part is numeric
3. Use `/` separator (not `-` or `_`)
4. Examples:
   - ✅ `VTM-1372/342-feature`
   - ✅ `1372/342-feature`
   - ❌ `1372-342-feature`

### Push Failed

**Symptoms**: "Failed to push branch" error

**Solutions**:
1. Check remote name:
   ```bash
   git remote -v
   ```
2. Verify GITLAB_REMOTE in `.env.gitlab-workflow`
3. Ensure remote exists:
   ```bash
   git remote add gitlab http://192.168.210.103:90/withvtm_2.0/withvtm-fe.git
   ```
4. Check network connectivity

### JSON File Error

**Symptoms**: "Invalid JSON" or "File not found"

**Solutions**:
1. Validate JSON syntax:
   ```bash
   python3 -m json.tool issue.json
   ```
2. Check file path (relative to current directory)
3. Ensure required fields: `asana`, `title`
4. Remove trailing commas in JSON
5. Escape special characters properly

### Git Remote Not Found

**Symptoms**: "No git remote found" error

**Solutions**:
1. Add remote:
   ```bash
   git remote add gitlab http://192.168.210.103:90/withvtm_2.0/withvtm-fe.git
   ```
2. Or set GITLAB_REMOTE=origin in `.env.gitlab-workflow`
3. Verify with: `git remote -v`

---

## 📚 Resources

### Documentation
- **This file**: `.claude/skills/gitlab-workflow/SKILL.md` - Main documentation
- **Detailed guide**: `.claude/skills/gitlab-workflow/README.md` - JSON file usage
- **AI Assistant Guide**: `.claude/skills/gitlab-workflow/AI_GUIDE.md` - AI-optimized comprehensive guide
- **JSON Schema**: `.claude/skills/gitlab-workflow/issue-template.json` - Validation schema
- **Quick Reference**: `.claude/skills/gitlab-workflow/QUICK_REFERENCE.md` - Command cheatsheet
- **Update Guide**: `.claude/skills/gitlab-workflow/UPDATE_SUMMARY.md` - Issue update feature guide
- **Doctor Guide**: `.claude/skills/gitlab-workflow/DOCTOR_GUIDE.md` - Environment validation guide
- **MR Description Example**: `.claude/skills/gitlab-workflow/MR_DESCRIPTION_EXAMPLE.md` - MR description format and examples

### Scripts
- **Main script**: `.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py`
- **Configuration**: `.claude/.env.gitlab-workflow`

### Examples
- **Sample issue**: `docs/requirements/vtm-1372/342/issue.json`
- **Feature docs**: `docs/requirements/vtm-1372/342/README.md`

### Technical Details
- **Language**: Python 3.6+
- **Dependencies**: None (uses Python standard library only)
- **Supported OS**: macOS, Linux, Windows
- **Git required**: Yes (2.0+)

---

## 🔄 Version History

### v3.3.0 (2026-01-23)
- ✨ **Enhanced MR descriptions** - Includes issue requirements and implementation mapping
- 📋 **Issue summary in MR** - Displays issue title, status, labels, and URL
- 📝 **Requirements section** - Full issue description included in MR
- ✅ **Implementation summary** - Clean commit messages showing what was implemented
- 🎯 **Requirements → Implementation mapping** - Clear view of request vs. delivery
- 📚 **MR Description Example guide** - Complete examples and best practices

### v3.2.0 (2026-01-22)
- ✨ **Doctor command** - Comprehensive environment validation and troubleshooting
- 🏥 **Health checks** - Validates environment variables, Git setup, GitLab API, and token permissions
- 💡 **Actionable fixes** - Provides specific solutions for any issues found
- 📚 Updated documentation with doctor usage throughout

### v3.1.0 (2026-01-22)
- ✨ **Auto-extract issue number from branch name** - No need to specify issue IID
- 🎯 **Requirements-focused updates** - Issue descriptions emphasize what needs to be done, not results
- 📝 **Separate MR and Issue summaries** - Issue shows requirements, MR shows implementation details
- 🔧 **Conventional Commits support** - Auto-removes `feat:`, `fix:` prefixes from titles
- 📚 Comprehensive Korean documentation for README and UPDATE_SUMMARY

### v3.0.0 (2026-01-22)
- ✨ Added update command for git history analysis
- ✨ Auto-generated MR descriptions from commits
- ✨ Auto-saved issue.json files
- 📝 Complete documentation overhaul

### v2.0.0 (2026-01-22)
- ✨ Added JSON file support (`--from-file` option)
- ✨ Added JSON Schema for validation
- 📝 Comprehensive documentation update
- 🎯 Improved error messages and validation
- 🔧 Better CLI help text

### v1.0.0 (2025-12-01)
- 🎉 Initial release
- ✅ Interactive workflow
- ✅ Branch creation and push
- ✅ Merge request support

---

## 📞 Support

### Getting Help
1. Check this documentation first
2. Review troubleshooting section
3. Check example files in `docs/requirements/`
4. Test with `--help` flag: `gitlab_workflow.py --help`

### Reporting Issues
If you find a bug or have a feature request:
1. Check existing issues in project repository
2. Provide minimal reproduction steps
3. Include error messages and logs
4. Specify your environment (OS, Python version, Git version)

### Contributing
- Source: `.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py`
- Follow existing code style
- Add tests for new features
- Update documentation

---

## 📄 License

This skill is part of the withVTM project and follows the project's license terms.
