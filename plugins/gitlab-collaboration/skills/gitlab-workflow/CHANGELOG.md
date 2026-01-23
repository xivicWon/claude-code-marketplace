# Changelog

All notable changes to the GitLab Workflow skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-22

### Added
- ✨ **JSON File Support**: New `--from-file` option for `create` command
  - Read issue configuration from JSON files
  - Version control issue definitions
  - Reproducible workflows
  - Template reuse
- 📄 **JSON Schema**: Added `issue-template.json` for validation
  - IDE auto-completion support
  - Field validation
  - Type checking
- 📚 **Comprehensive Documentation**:
  - Complete rewrite of SKILL.md with better structure
  - New README.md with JSON file usage guide
  - Example files in `docs/requirements/`
  - Troubleshooting section expanded
- 🎯 **Field Overrides**: CLI arguments can override JSON file values
- 🔍 **Better Validation**: Improved error messages for missing/invalid fields

### Changed
- 📝 Updated all documentation to reflect new features
- 🔧 Improved CLI help text and examples
- 📦 Better organized file structure
- ⚡ Enhanced error handling and user feedback

### Fixed
- 🐛 Fixed branch name validation edge cases
- 🐛 Improved JSON parsing error messages
- 🐛 Better handling of Unicode characters in titles

### Documentation
- SKILL.md: Complete rewrite with better organization
- README.md: New detailed guide for JSON file usage
- CHANGELOG.md: This file
- issue-template.json: JSON Schema for validation
- .env.gitlab-workflow.sample: Updated with better comments

### Examples
- docs/requirements/vtm-1372/342/issue.json: Sample JSON file
- docs/requirements/vtm-1372/342/README.md: Feature documentation

## [1.0.0] - 2025-12-01

### Added
- 🎉 Initial release
- ✅ Interactive workflow with guided questions
- ✅ GitLab issue creation via API
- ✅ Automatic branch creation with naming conventions
- ✅ Git push with confirmation
- ✅ Merge request creation
- ✅ Branch validation
- ✅ Environment configuration via .env file
- 📝 Basic documentation

### Features
- Interactive question flow for issue creation
- Branch naming format: `{asana}/{gitlab}-{summary}`
- Auto-sanitization of non-ASCII characters
- Remote detection (origin/gitlab)
- Merge request linking to issues
- Auto-close issues on MR merge

---

## Upgrade Guide

### From v1.x to v2.0

#### No Breaking Changes
Version 2.0 is fully backward compatible with v1.x. All existing workflows continue to work.

#### New Features Available
1. **JSON File Support**: Optionally use JSON files for issue definitions
   ```bash
   /gitlab-workflow create --from-file issue.json
   ```

2. **JSON Schema**: Enable IDE validation by configuring your editor
   ```json
   {
     "json.schemas": [{
       "fileMatch": ["**/requirements/**/issue.json"],
       "url": "./.claude/skills/gitlab-workflow/issue-template.json"
     }]
   }
   ```

3. **Field Overrides**: Mix JSON files with CLI arguments
   ```bash
   /gitlab-workflow create --from-file issue.json --labels "urgent"
   ```

#### Recommended Actions
1. ✅ Read new SKILL.md for comprehensive documentation
2. ✅ Check README.md for JSON file usage examples
3. ✅ Update .env file using new .sample as reference
4. ✅ Try JSON file workflow for your next planned feature

---

## Future Plans

### v2.1.0 (Planned)
- [ ] Support for multiple issue templates
- [ ] Issue template generator command
- [ ] Batch issue creation from multiple JSON files
- [ ] Integration with project management tools

### v2.2.0 (Planned)
- [ ] GitLab CI/CD integration
- [ ] Automatic changelog generation
- [ ] Issue status tracking
- [ ] Smart branch cleanup

### v3.0.0 (Future)
- [ ] GitHub support
- [ ] Custom workflow definitions
- [ ] Plugin system
- [ ] Web UI for workflow management

---

## Contributing

Contributions are welcome! Please:
1. Check existing issues/features
2. Follow existing code style
3. Add tests for new features
4. Update documentation
5. Submit pull request

---

## Support

- Documentation: `.claude/skills/gitlab-workflow/SKILL.md`
- Detailed Guide: `.claude/skills/gitlab-workflow/README.md`
- Issues: Report to project repository

---

## License

This skill is part of the withVTM project and follows the project's license terms.
