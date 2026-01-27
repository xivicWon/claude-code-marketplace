# GitLab Collaboration - Shared Resources

This directory contains shared resources used by all GitLab collaboration skills.

## Directory Structure

```
shared/
├── scripts/
│   └── gitlab_workflow.py      # Core Python implementation
├── references/
│   ├── COMMANDS.md             # Command reference
│   ├── DOCTOR_GUIDE.md         # Environment validation guide
│   ├── MR_DESCRIPTION_EXAMPLE.md  # MR description examples
│   ├── UPDATE_SUMMARY.md       # Issue update guide
│   └── QUICK_REFERENCE.md      # Quick command reference
├── issue-template.json         # JSON schema for issue definitions
└── README.md                   # This file
```

## Scripts

### gitlab_workflow.py

Core Python implementation for all GitLab workflow operations:
- Issue creation
- Branch management
- Issue updates from git history
- Merge request creation
- Environment validation (doctor)

**Usage**:
```bash
python shared/scripts/gitlab_workflow.py [command] [options]
```

**Commands**:
- `start` - Create issue and branch
- `update` - Update issue from git history
- `mr` - Create merge request
- `doctor` - Validate environment
- `help` - Show help

## References

Documentation and guides for users and AI assistants:

- **COMMANDS.md** - Complete command reference with examples
- **DOCTOR_GUIDE.md** - Environment setup and troubleshooting
- **MR_DESCRIPTION_EXAMPLE.md** - Merge request description format and examples
- **UPDATE_SUMMARY.md** - Issue update feature guide
- **QUICK_REFERENCE.md** - Quick command cheatsheet

## Issue Template

**issue-template.json** - JSON schema for creating issues from files

Example:
```json
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Add logout functionality",
  "labels": ["feature", "ui"],
  "push": true
}
```

## Environment Configuration

All scripts expect environment configuration in:
```
.claude/.env.gitlab-workflow
```

Required variables:
```bash
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe
```

Optional variables:
```bash
GITLAB_REMOTE=gitlab
ISSUE_DIR=docs/requirements
BASE_BRANCH=main
```

**BASE_BRANCH**: Default base branch for creating new branches (default: `main`).
- Branch name only: `main`, `develop`, `master` (uses default remote)
- With remote: `origin/main`, `gitlab/develop` (explicit remote)
- Always fetches from remote to ensure latest code

**Important**: Working directory must be clean (no uncommitted changes) before creating branches.

See `.env.gitlab-workflow.example` for a complete template.

## Commands and Skills Using These Resources

All GitLab collaboration commands and skills use these shared resources:

### Commands (Direct Execution)

1. **gitlab-doctor** (`/gitlab-doctor`)
   - Validates environment setup
   - Uses: `gitlab_workflow.py doctor`, `DOCTOR_GUIDE.md`

2. **gitlab-issue-create** (`/gitlab-issue-create`)
   - Creates GitLab issue and branch
   - Uses: `gitlab_workflow.py start`, `issue-template.json`

3. **gitlab-issue-update** (`/gitlab-issue-update`)
   - Updates issue from git commits
   - Uses: `gitlab_workflow.py update`

4. **gitlab-mr** (`/gitlab-mr`)
   - Creates merge request
   - Uses: `gitlab_workflow.py mr`, `MR_DESCRIPTION_EXAMPLE.md`

### Skills (AI-Assisted Workflows)

All skills provide the same functionality as commands but with AI-driven interactive workflows and additional context awareness. See `../skills/` directory for skill implementations.

## Development

When modifying shared resources:

1. **Update gitlab_workflow.py**
   - Maintain backward compatibility
   - Update help text and examples
   - Test with all skills

2. **Update documentation**
   - Keep all references/ docs in sync
   - Update examples to match new features
   - Document breaking changes

3. **Update issue-template.json**
   - Follow JSON Schema standards
   - Maintain backward compatibility with `asana` field
   - Add new fields with defaults

## Notes

- All skills are independent (no dependencies between skills)
- Shared resources are read-only from skills' perspective
- Environment config is loaded from project `.claude/` directory only
- Backward compatibility maintained for legacy `asana` field
