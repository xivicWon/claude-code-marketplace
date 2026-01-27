# Changelog

All notable changes to the GitLab Collaboration plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-27

### Added
- **Direct execution commands** for faster workflows
  - `/gitlab-doctor` - Direct command for environment validation
  - `/gitlab-issue-create` - Direct command for issue and branch creation
  - `/gitlab-issue-update` - Direct command for issue updates from commits
  - `/gitlab-mr` - Direct command for merge request creation
- **Command documentation** in `commands/` directory
  - Comprehensive usage guides for each command
  - Example workflows and troubleshooting
  - Integration with existing Python scripts
- **Root README.md** with complete plugin overview
  - Quick start guide
  - Commands vs Skills comparison
  - Complete workflow examples
  - Environment setup guide
  - Directory structure documentation

### Changed
- **Plugin version**: 1.1.1 → 1.2.0
- **Shared README**: Updated to document both commands and skills
- **Documentation structure**: Clearer distinction between commands and skills

### Technical Details
- Commands use same `gitlab_workflow.py` backend as skills
- No changes to existing skill functionality
- Backward compatible with all existing workflows
- Commands provide faster execution for simple workflows
- Skills provide AI-assisted interactive workflows for complex scenarios

## [1.1.1] - 2026-01-27

### Changed
- Improved skill metadata for better discoverability
- Enhanced skill descriptions for AI assistant

## [1.1.0] - 2026-01-27

### Added
- Modular skill structure in `skills/` directory
- Individual skill documentation (SKILL.md for each)
- Comprehensive reference documentation in `shared/references/`

### Changed
- Refactored monolithic skill into 4 independent skills:
  - `gitlab-doctor` - Environment validation
  - `gitlab-issue-create` - Issue and branch creation
  - `gitlab-issue-update` - Issue updates from git history
  - `gitlab-mr` - Merge request creation with auto-generated descriptions
- Improved documentation structure
- Better separation of concerns

### Technical Details
- Shared Python implementation in `shared/scripts/gitlab_workflow.py`
- Common resources in `shared/` directory
- Each skill is independent and self-contained

## [1.0.0] - 2026-01-26

### Added
- Initial release of GitLab Collaboration plugin
- Monolithic skill for complete GitLab workflow automation
- Features:
  - Issue creation with interactive prompts
  - Automatic branch creation and management
  - Issue updates from git commit history
  - Merge request creation with auto-generated descriptions
  - Environment validation (doctor)
- Python implementation (`gitlab_workflow.py`)
- Environment configuration support (`.env.gitlab-workflow`)
- Branch naming validation
- Conventional Commits support
- Auto-close issues on merge
- Requirements vs Implementation tracking

### Technical Details
- Python 3 backend with standard library only (no external dependencies)
- GitLab REST API integration
- Git CLI integration
- Support for both interactive and JSON file-based workflows

## Migration Guide

### From 1.1.x to 1.2.0

**No breaking changes!** All existing skills continue to work.

**New options available:**

Instead of:
```bash
# AI-assisted workflow (still works)
/gitlab-doctor
```

You can now use:
```bash
# Direct command (faster)
/gitlab-doctor
```

Both approaches work identically and use the same backend.

**When to use commands vs skills:**
- **Commands**: Quick, straightforward workflows with minimal interaction
- **Skills**: Complex scenarios requiring AI guidance and context awareness

### From 1.0.x to 1.1.0

**No breaking changes!** Update to modular structure is transparent.

**Changes:**
- Skills are now in `skills/` directory (previously in root)
- Documentation improved with individual SKILL.md files
- No changes to slash command usage

## Upcoming Features

- [ ] Support for GitLab CI/CD integration
- [ ] Milestone management
- [ ] Epic support
- [ ] Time tracking integration
- [ ] Custom MR templates
- [ ] Batch operations (multiple issues/MRs)
- [ ] GitLab webhooks integration
- [ ] Advanced filtering and search

## Support

For issues or feature requests, please contact:
- **Author**: xivic
- **Email**: dev@xivic.com

## Links

- [GitLab API Documentation](https://docs.gitlab.com/ee/api/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
