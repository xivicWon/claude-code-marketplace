# GitLab Issue Create - Example Usage

## Quick Start

### 1. Create JSON File

```bash
# Create your issue data file
cat > my-issue.json <<EOF
{
  "issueCode": "VTM-1372",
  "title": "Your feature title",
  "description": "Detailed description of what needs to be done",
  "labels": ["feature", "priority-high"]
}
EOF
```

### 2. Run Forced Workflow

**Via Claude Code:**
```
/gitlab-issue-create
```
Then provide the JSON file path when prompted.

**Via Python Script:**
```bash
python shared/scripts/gitlab_workflow.py start --from-file my-issue.json
```

## JSON Schema

### Required Fields
- `issueCode` (string): Your project's issue code prefix
- `title` (string): Clear, concise issue title

### Optional Fields
- `description` (string): Initial description (AI will enhance it)
- `labels` (array of strings): Issue labels

## What Happens Automatically

1. ✅ Validates environment
2. ✅ Creates GitLab issue
3. ✅ Stashes your uncommitted changes (if any)
4. ✅ Switches to main branch
5. ✅ Pulls latest changes
6. ✅ Creates new branch
7. ✅ Pushes to remote
8. ✅ Restores your changes
9. 🤖 AI analyzes and updates issue
10. ✅ Saves metadata

**No user interaction required!**

## Example Scenarios

### Scenario 1: Clean Working Directory

```json
{
  "issueCode": "PROJ-123",
  "title": "Add dark mode",
  "labels": ["feature", "ui"]
}
```

**Result:** New branch created, issue created, no stash needed.

### Scenario 2: Uncommitted Changes

You're working on something and want to start a new issue.

**Your state:**
```
Modified files:
  - src/Dashboard.tsx
  - src/api/user.ts
```

**What happens:**
1. Your changes are automatically stashed
2. Switches to main, pulls latest
3. Creates new branch
4. **Your changes are restored** to the new branch
5. You can continue where you left off!

### Scenario 3: With Detailed Description

```json
{
  "issueCode": "VTM-1400",
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication with refresh tokens",
  "labels": ["feature", "security", "backend"]
}
```

**Result:** Issue created with your description, AI may enhance it further.

## Rollback Safety

If **anything fails** during the workflow:

```
🔄 Rolling back changes...
   ✅ Re-stashed changes
   ✅ Deleted remote branch
   ✅ Deleted local branch
   ✅ Switched back to original branch
   ✅ Restored stashed changes
```

**You're always safe!** The rollback ensures you return to the exact state before running the command.

## Testing the Example

Try the included example:

```bash
cd plugins/gitlab-collaboration

# Use the example JSON
python shared/scripts/gitlab_workflow.py start \
  --from-file examples/issue-example.json
```

This will create:
- Issue: "Add user profile page"
- Branch: `vtm-1372/{issue-number}-add-user-profile-page`
- Metadata: `docs/requirements/vtm-1372/{issue-number}-add-user-profile-page/issue.json`

## Next Steps After Workflow

```bash
# Make your changes
vim src/pages/Profile.tsx

# Commit
git add .
git commit -m "feat: implement user profile page"

# Push (upstream already set)
git push

# Update issue with implementation details
/gitlab-issue-update

# Create merge request
/gitlab-mr
```

## Common Use Cases

### 1. Planning Mode
Create JSON file before implementation:
```json
{
  "issueCode": "PROJ-200",
  "title": "Research GraphQL migration",
  "description": "Evaluate GraphQL for API layer",
  "labels": ["research", "architecture"]
}
```

### 2. Bug Fix
```json
{
  "issueCode": "PROJ-201",
  "title": "Fix login redirect loop",
  "description": "Users stuck in redirect loop after OAuth",
  "labels": ["bug", "priority-high", "auth"]
}
```

### 3. Refactoring
```json
{
  "issueCode": "PROJ-202",
  "title": "Refactor API client",
  "description": "Extract common API logic to reusable hooks",
  "labels": ["refactor", "tech-debt"]
}
```

## Tips

1. **Prepare JSON files in your docs folder** for quick access
2. **Don't worry about dirty state** - it's handled automatically
3. **Trust the rollback** - if something fails, you're safe
4. **Check the issue after creation** - AI may have enhanced the description
5. **Use consistent issueCode** - maintains organization

## Troubleshooting

### "JSON file not found"
→ Use full or relative path: `docs/issues/my-issue.json`

### "Required field missing: issueCode"
→ Add `"issueCode": "YOUR-CODE"` to JSON

### "Remote branch not found: gitlab/develop"
→ Check `.env` file's `BASE_BRANCH` setting

### "GitLab API connection failed"
→ Run `/gitlab-doctor` for diagnosis

---

**Version 2.0** - FORCED Workflow Edition
*Zero choices, maximum automation*
