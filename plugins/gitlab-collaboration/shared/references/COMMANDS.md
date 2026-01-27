# GitLab Workflow Commands Reference

Complete command reference for GitLab workflow automation.

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

## Command Usage Guidelines

### Interactive vs CLI Commands

**Interactive Commands** (`/gitlab-workflow ...`):
- Best for: Quick workflows, learning, guided prompts
- Claude asks questions interactively
- No need to remember syntax
- Validation and confirmation built-in

**CLI Commands** (`.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py ...`):
- Best for: Automation, scripting, advanced usage
- Requires knowing command syntax
- Full control over all parameters
- Can be integrated into shell scripts

### Common Command Patterns

#### Create Workflow
```bash
# Interactive (recommended for beginners)
/gitlab-workflow create

# From JSON file (recommended for planned features)
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json

# CLI with all options
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  --asana VTM-1372 start "Add user dashboard" \
  --description "Create analytics dashboard" \
  --labels "feature,dashboard" \
  --push
```

#### Update Workflow
```bash
# Auto-extract issue number from branch (recommended)
/gitlab-workflow update

# CLI with specific issue
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update 345

# Update with title change
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update --update-title
```

#### MR Workflow
```bash
# Interactive (recommended)
/gitlab-workflow mr

# CLI with options
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  mr "Add user dashboard" --issue 342 --target main
```

#### Validation
```bash
# Check environment setup (always run this first!)
/gitlab-workflow doctor

# Or using CLI
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py doctor
```

---

## Command Parameters

### Common Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `--asana` | string | Asana issue identifier | `VTM-1372`, `1372` |
| `--from-file` | path | JSON file path for issue definition | `docs/requirements/vtm-1372/342/issue.json` |
| `--description` | string | Issue description (markdown) | `"## Overview\nDetails..."` |
| `--labels` | string | Comma-separated labels | `"bug,feature,urgent"` |
| `--push` | flag | Auto-push to remote after creation | No value needed |
| `--update-title` | flag | Update issue title from first commit | No value needed |
| `--issue` | number | GitLab issue number | `342` |
| `--target` | string | Target branch for MR | `main`, `develop` |

### Parameter Examples

**Asana Parameter**:
```bash
# Full prefix format
--asana VTM-1372

# Numeric only
--asana 1372

# Any project code
--asana PROJ-123
```

**Labels Parameter**:
```bash
# Single label
--labels "feature"

# Multiple labels
--labels "bug,feature,urgent"

# In JSON file
"labels": ["bug", "feature", "urgent"]
```

**File Path Parameter**:
```bash
# Relative path
--from-file docs/requirements/vtm-1372/342/issue.json

# Absolute path
--from-file /Users/name/project/docs/issue.json

# In current directory
--from-file issue.json
```

---

## Command Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Command completed successfully |
| 1 | General error | Check error message for details |
| 2 | Validation error | Fix input parameters or JSON |
| 3 | Git error | Check git status and remote |
| 4 | API error | Check GitLab connection and token |
| 5 | Environment error | Run `doctor` to diagnose |

---

## Command Help

Get help for any command:

```bash
# General help
/gitlab-workflow help

# CLI help
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py --help

# Command-specific help
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py start --help
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update --help
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py mr --help
```

---

## See Also

- [Main Documentation](../SKILL.md) - Complete feature documentation
- [Quick Reference](../QUICK_REFERENCE.md) - Command cheatsheet
- [Doctor Guide](../DOCTOR_GUIDE.md) - Environment validation
- [AI Guide](../AI_GUIDE.md) - AI assistant integration
