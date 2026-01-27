# GitLab Collaboration Plugin

Complete GitLab workflow automation plugin for team collaboration. Automates issue creation, branch management, and merge request workflows with both direct commands and AI-assisted skills.

**Version**: 1.4.0

## Features

✅ **Interactive environment setup** with step-by-step wizard
✅ **Intelligent dirty working directory handling** with context-aware options
✅ Create GitLab issues and branches automatically
✅ Update issue descriptions from git commit history
✅ Create merge requests with auto-generated comprehensive descriptions
✅ Validate environment setup with doctor command
✅ Support for both interactive commands and AI-assisted skills
✅ Auto-close issues when MR is merged
✅ Requirements vs Implementation tracking
✅ Conventional Commits support
✅ Secure token handling with automatic file permissions
✅ Safe stash/unstash mechanism for work-in-progress changes

## Quick Start

1. **Initialize environment** (first time only):
   ```bash
   /gitlab-init
   ```
   This interactive wizard will guide you through setting up your GitLab credentials and configuration.

2. **Validate environment**:
   ```bash
   /gitlab-doctor
   ```

3. **Create issue and branch**:
   ```bash
   /gitlab-issue-create
   ```

4. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: implement feature"
   git push
   ```

5. **Update issue with requirements**:
   ```bash
   /gitlab-issue-update
   ```

6. **Create merge request**:
   ```bash
   /gitlab-mr
   ```

## Commands

Direct execution commands for quick workflows:

| Command | Description |
|---------|-------------|
| `/gitlab-init` | **Initialize environment with interactive setup wizard** |
| `/gitlab-doctor` | Validate GitLab workflow environment setup |
| `/gitlab-issue-create` | Create GitLab issue and branch interactively |
| `/gitlab-issue-update` | Update issue description from git commits |
| `/gitlab-mr` | Create merge request with auto-generated description |

See `commands/` directory for detailed documentation.

## Skills

AI-assisted workflows for more complex scenarios:

| Skill | Description |
|-------|-------------|
| `gitlab-init` | **Interactive environment setup with AI guidance** |
| `gitlab-doctor` | Environment validation with AI guidance |
| `gitlab-issue-create` | Issue creation with AI-driven interactive workflow |
| `gitlab-issue-update` | Issue updates with commit analysis |
| `gitlab-mr` | MR creation with comprehensive auto-generated descriptions |

See `skills/` directory for detailed documentation.

## Environment Setup

### Option 1: Interactive Setup (Recommended)

Use the interactive wizard:
```bash
/gitlab-init
```

This will guide you through setting up all required configuration.

### Option 2: Manual Setup

Create `.claude/.env.gitlab-workflow` in your git repository root:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab              # Git remote name (default: auto-detect)
BASE_BRANCH=main                  # Base branch for new branches (default: main)
ISSUE_DIR=docs/requirements       # Where to save issue.json files (default: docs/requirements)
```

### Getting GitLab Token

1. Go to your GitLab instance
2. Click your avatar → **Settings**
3. Navigate to **Access Tokens**
4. Create token with **'api' scope**
5. Copy token to `.env.gitlab-workflow`

See `.env.gitlab-workflow.example` for a complete template.

## Complete Workflow Example

```bash
# 1. Validate setup (first time)
/gitlab-doctor

# 2. Create issue and branch
/gitlab-issue-create
# Answer questions:
# - 이슈코드: VTM-1372
# - Title: Add logout button
# - Description: (optional)
# - Labels: feature,ui
# - Create branch: yes
# - Auto-push: yes

# 3. Make changes
git add .
git commit -m "feat: implement logout button"
git push

# 4. Update issue description
/gitlab-issue-update
# → Auto-extracts issue #342 from branch "vtm-1372/342-add-logout-button"
# → Updates issue description with requirements summary

# 5. Create merge request
/gitlab-mr
# Answer questions:
# - MR title: Add logout button
# - Link to issue: 342
# - Target branch: main
# → Creates MR with comprehensive description
# → Auto-close link to issue #342
```

## Directory Structure

```
gitlab-collaboration/
├── .claude-plugin/
│   └── plugin.json                    # Plugin metadata
├── commands/                          # Direct execution commands
│   ├── gitlab-doctor.md
│   ├── gitlab-issue-create.md
│   ├── gitlab-issue-update.md
│   └── gitlab-mr.md
├── skills/                            # AI-assisted workflows
│   ├── gitlab-doctor/
│   ├── gitlab-issue-create/
│   ├── gitlab-issue-update/
│   └── gitlab-mr/
├── shared/                            # Shared resources
│   ├── scripts/
│   │   └── gitlab_workflow.py        # Core Python implementation
│   ├── references/                   # Documentation
│   │   ├── COMMANDS.md
│   │   ├── DOCTOR_GUIDE.md
│   │   ├── MR_DESCRIPTION_EXAMPLE.md
│   │   ├── UPDATE_SUMMARY.md
│   │   └── QUICK_REFERENCE.md
│   ├── issue-template.json          # Issue JSON schema
│   └── README.md
├── .env.gitlab-workflow.example     # Environment config template
└── README.md                         # This file
```

## Branch Naming Convention

All branches must follow: `{issue-code}/{gitlab#}-{summary}`

**Valid Examples**:
- ✅ `VTM-1372/342-add-logout-button`
- ✅ `1372/343-fix-login-bug`
- ✅ `1400/308-refactor-api`

**Invalid Examples**:
- ❌ `342-feature` (missing issue code)
- ❌ `add-feature` (missing numbers)
- ❌ `VTM-1372-342` (wrong separator)

## JSON File Format

Create issues from JSON files for automated workflows:

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

**Issue Only** (no branch):
```json
{
  "issueCode": "VTM-1372",
  "title": "Document requirements",
  "description": "Gather and document requirements",
  "createBranch": false
}
```

## Key Features

### Auto-Extract Issue Number

`/gitlab-issue-update` automatically extracts issue number from branch:

- Branch: `vtm-1372/342-feature` → Issue #342 (no manual input!)

### Auto-Generate MR Description

`/gitlab-mr` creates comprehensive description with:

1. **Issue Summary**: title, status, labels, URL
2. **Requirements (요구사항)**: From issue description
3. **Implementation (구현 내용)**: From commit messages
4. **Change Statistics**: Files changed, insertions, deletions
5. **Detailed Commit History**: With authors and dates

Perfect for code reviews - shows **what was requested** vs **what was delivered**!

### Requirements vs Implementation

- **Issue update** (`/gitlab-issue-update`): **Requirements** (what to do)
- **MR creation** (`/gitlab-mr`): **Implementation** (what was done) + Requirements mapping

### Conventional Commits Support

Automatically strips prefixes for cleaner descriptions:

**Commits**:
```
feat: add logout button
fix: resolve login bug
```

**Generated Descriptions**:
```
- add logout button
- resolve login bug
```

## Troubleshooting

### Run Doctor First

```bash
/gitlab-doctor
```

This validates:
- ✅ Environment variables
- ✅ Git repository
- ✅ Git remote
- ✅ GitLab API connectivity
- ✅ Project access
- ✅ Token permissions
- ✅ Issue directory
- ✅ Working directory status

### Common Issues

| Issue | Solution |
|-------|----------|
| Missing environment variables | Create `.claude/.env.gitlab-workflow` |
| Not in git repository | `git init` or `cd` to repository |
| No git remote | `git remote add gitlab <url>` |
| Connection failed | Check GITLAB_URL and network |
| Insufficient permissions | Token needs 'api' scope |
| Uncommitted changes | Commit or stash before creating branches |

See `shared/references/DOCTOR_GUIDE.md` for detailed troubleshooting.

## Documentation

### Quick References
- **Quick Reference**: `shared/references/QUICK_REFERENCE.md`
- **Commands Guide**: `shared/references/COMMANDS.md`

### Detailed Guides
- **Doctor Guide**: `shared/references/DOCTOR_GUIDE.md`
- **Issue Update Guide**: `shared/references/UPDATE_SUMMARY.md`
- **MR Description Examples**: `shared/references/MR_DESCRIPTION_EXAMPLE.md`

### Command Documentation
- `commands/gitlab-doctor.md`
- `commands/gitlab-issue-create.md`
- `commands/gitlab-issue-update.md`
- `commands/gitlab-mr.md`

### Skill Documentation
- `skills/gitlab-doctor/SKILL.md`
- `skills/gitlab-issue-create/SKILL.md`
- `skills/gitlab-issue-update/SKILL.md`
- `skills/gitlab-mr/SKILL.md`

## Development

### Python Script

Core implementation: `shared/scripts/gitlab_workflow.py`

**Commands**:
```bash
python gitlab_workflow.py doctor           # Validate environment
python gitlab_workflow.py start "Title"    # Create issue and branch
python gitlab_workflow.py update           # Update issue from commits
python gitlab_workflow.py mr "Title"       # Create merge request
python gitlab_workflow.py help             # Show help
```

### Adding Features

1. Update `shared/scripts/gitlab_workflow.py`
2. Update command documentation in `commands/`
3. Update skill documentation in `skills/`
4. Update shared references in `shared/references/`
5. Test with `/gitlab-doctor`

## Version History

### 1.2.0 (2026-01-27)
- ✅ Added direct execution commands
- ✅ Command documentation in `commands/` directory
- ✅ Improved plugin structure
- ✅ Updated README with command/skill distinction

### 1.1.1 (2026-01-27)
- ✅ Metadata improvements for skills

### 1.1.0 (2026-01-27)
- ✅ Refactored into modular skills
- ✅ Improved documentation structure

### 1.0.0
- ✅ Initial release with monolithic skill

## Support

For issues or questions:
- Check `/gitlab-doctor` for environment validation
- See `shared/references/DOCTOR_GUIDE.md` for troubleshooting
- Review `shared/references/QUICK_REFERENCE.md` for common tasks

## License

Copyright (c) 2026 xivic (dev@xivic.com)
