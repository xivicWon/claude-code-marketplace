---
name: gitlab-issue-create
description: FORCED automated workflow for GitLab issue creation. Requires JSON file input, automatically handles all dirty state, creates branch, pushes, and AI-updates issue. No user interaction required. Trigger when user provides JSON file or wants fully automated issue workflow.
version: 2.0.0
updated: 2026-01-28
---

# GitLab Issue Create (Version 2.0: FORCED Workflow)

**🆕 Version 2.0**: Fully automated, zero-choice workflow with AI-powered updates

## 🎯 What This Does

This is a **FORCED automated workflow** that handles everything from issue creation to branch setup without user interaction:

1. ✅ **Validates** environment and JSON input
2. ✅ **Creates** GitLab issue
3. ✅ **Stashes** uncommitted changes (if any)
4. ✅ **Switches** to base branch
5. ✅ **Pulls** latest changes
6. ✅ **Creates** new branch
7. ✅ **Pushes** to remote
8. ✅ **Restores** stashed changes
9. 🤖 **AI analyzes** changes and updates issue
10. ✅ **Saves** issue.json metadata

**On failure**: Automatic atomic rollback to clean state

## 🚀 Quick Usage

```bash
/gitlab-issue-create
```

**REQUIRED**: You must provide a JSON file with issue data.

Claude will:
1. Ask for JSON file path (or you can provide it upfront)
2. Execute the entire workflow automatically
3. Report results

## 📝 JSON File Format (Required)

Create a JSON file with issue data:

**File**: `docs/requirements/vtm-1372/issue-draft.json`

```json
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Add logout functionality to navigation bar",
  "labels": ["feature", "ui"]
}
```

### Required Fields

- `issueCode` (string): 이슈코드 (e.g., "VTM-1372" or "1372")
- `title` (string): Issue title

### Optional Fields

- `description` (string): Initial description (AI will enhance it)
- `labels` (array): Issue labels

### ❌ Removed Fields (Now Forced)

The following fields are **no longer supported** because they're now forced:
- ~~`createBranch`~~ - Always `true` (forced)
- ~~`push`~~ - Always `true` (forced)
- ~~`baseBranch`~~ - Always from `.env` (forced)

## 🔄 Forced Workflow Details

### Phase 0: Pre-flight Validation

```
🔍 Checking:
   ✅ JSON file exists and valid
   ✅ Required fields present
   ✅ Git repository exists
   ✅ Remote configured
   ✅ Base branch exists on remote
   ✅ GitLab API connected
```

### Phase 1: Issue Creation

```
📝 Creating GitLab issue...
   ✅ Created issue #342: Add logout button
   URL: http://gitlab.com/project/issues/342
```

### Phase 2: Dirty State Handling (FORCED)

**If you have uncommitted changes:**

```
🔄 Preparing working directory

   ⚠️  Found 3 uncommitted change(s)
      - src/App.tsx
      - src/components/Nav.tsx
      - package.json

   📦 Auto-stashing changes...
   ✅ Stashed: Auto-stash for issue #342

   🔀 Switching to main...
   ✅ Now on main

   ⬇️  Pulling latest changes from gitlab/main...
   ✅ Updated to latest
```

**No user choice** - this happens automatically!

### Phase 3: Branch Creation

```
🌿 Creating new branch

   Branch: vtm-1372/342-add-logout-button
   ✅ Created and checked out: vtm-1372/342-add-logout-button
```

### Phase 4: Forced Push

```
📤 Pushing to remote

   ✅ Pushed: gitlab/vtm-1372/342-add-logout-button
```

### Phase 5: Stash Restoration

```
📦 Restoring stashed changes

   ✅ Applied stashed changes to new branch
```

### Phase 6: AI Auto-Update (FORCED)

```
🤖 AI analyzing and updating issue

   📊 Analyzing 3 changed files...
   ✅ Updated issue #342 with requirements summary
```

**What AI does:**
- Analyzes stashed files (what you were working on)
- Generates structured requirements summary
- Updates GitLab issue description automatically

### Phase 7: Save Metadata

```
💾 Saving metadata

   ✅ Saved: docs/requirements/vtm-1372/342-add-logout-button/issue.json
```

### Success!

```
══════════════════════════════════════════════════════════
✅ Workflow completed successfully!
══════════════════════════════════════════════════════════
Issue:  #342 - Add logout button
Branch: vtm-1372/342-add-logout-button
Status: Pushed to gitlab/vtm-1372/342-add-logout-button
URL:    http://gitlab.com/project/issues/342
AI:     Issue updated with requirements summary
══════════════════════════════════════════════════════════
```

## 🔄 Automatic Rollback on Failure

If **any step fails**, the workflow automatically rolls back:

```
❌ Error: Failed to push branch

🔄 Rolling back changes...
   ✅ Re-stashed changes
   ✅ Deleted remote branch: gitlab/vtm-1372/342-add-logout-button
   ✅ Deleted local branch: vtm-1372/342-add-logout-button
   ✅ Switched back to: feature/dashboard
   ✅ Restored stashed changes
   Rollback completed

══════════════════════════════════════════════════════════
❌ Workflow failed and rolled back
⚠️  Issue #342 was created but workflow failed
   You may need to manually close it in GitLab
══════════════════════════════════════════════════════════
```

**Rollback guarantees:**
- Your working directory is restored
- No orphaned branches (local or remote)
- Original branch restored
- Stashed changes preserved

**Note**: The GitLab issue itself is **not deleted** (can't undo API calls), but everything else rolls back.

## 📋 Example Workflow

### 1. Prepare JSON File

```bash
# Create issue data file
cat > docs/requirements/vtm-1372/logout-feature.json <<EOF
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Implement logout functionality",
  "labels": ["feature", "ui"]
}
EOF
```

### 2. Run Forced Workflow

```
You: /gitlab-issue-create

Claude: I'll execute the forced automated workflow for GitLab issue creation.

        Please provide the JSON file path:

You: docs/requirements/vtm-1372/logout-feature.json

Claude: [Executes entire workflow automatically]

        🔍 Phase 0: Pre-flight validation
           ✅ Loaded JSON: docs/requirements/vtm-1372/logout-feature.json
           ✅ Base branch: main (from .env)
           ...

        ✅ All pre-flight checks passed

        📝 Phase 1: Creating GitLab issue
           ✅ Created issue #342: Add logout button

        [... continues through all phases ...]

        ✅ Workflow completed successfully!
```

### 3. Next Steps

After workflow completes, you can:

```bash
# Make your changes
vim src/components/Nav.tsx

# Commit
git add .
git commit -m "feat: implement logout button"

# Push (branch already set upstream)
git push

# Update issue with implementation details
/gitlab-issue-update

# Create merge request
/gitlab-mr
```

## ⚙️ Environment Configuration

Required in `.claude/.env.gitlab-workflow`:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
BASE_BRANCH=main                 # FORCED: Used for all issue creations
ISSUE_DIR=docs/requirements
```

**Important**: `BASE_BRANCH` is **forced** - JSON files cannot override it. This ensures consistency across all issues.

Run `/gitlab-doctor` to validate your setup.

## 🔧 Branch Naming (Automatic)

Format: `{issue-code}/{gitlab#}-{summary}`

**Examples:**
- Title: "Add logout button" → `vtm-1372/342-add-logout-button`
- Title: "Fix login bug" → `1372/343-fix-login-bug`
- Title: "사용자 대시보드" → `vtm-1372/344` (non-ASCII removed)

**Rules:**
- Lowercase
- Non-alphanumeric characters removed
- Spaces converted to hyphens
- Max 50 chars for summary

## ❌ Common Errors

### Error: JSON file not found

```
Error: JSON file not found: issue.json
```

**Solution**: Provide full path or relative path to JSON file:
```bash
/gitlab-issue-create
# Then: docs/requirements/vtm-1372/issue.json
```

### Error: Required field missing

```
Error: Required field missing in JSON: issueCode
```

**Solution**: Ensure JSON has required fields:
```json
{
  "issueCode": "VTM-1372",  // ✅ Required
  "title": "Feature name"   // ✅ Required
}
```

### Error: Remote branch not found

```
Error: Remote branch not found: gitlab/develop
```

**Solution**: Check `BASE_BRANCH` in `.env`:
```bash
# List available remote branches
git branch -r

# Update .env
BASE_BRANCH=main  # or whatever exists
```

### Error: GitLab API connection failed

```
Error: GitLab API connection failed
```

**Solution**: Run `/gitlab-doctor` for detailed diagnosis.

## 🆚 Version Comparison

### Version 1.x (Old - Interactive)

```
❓ User prompted for each choice:
   - Create branch? (y/n)
   - Auto-push? (y/n)
   - What to do with dirty state? (1/2/3)

⏱️  Slower, requires user interaction
```

### Version 2.0 (New - FORCED)

```
✅ Zero user interaction
✅ All steps forced and automated
✅ AI-powered issue updates
✅ Atomic rollback on failure

⚡ Faster, fully automated
```

## 🤖 AI Auto-Update Details

**What AI analyzes:**
1. List of changed files (from stash)
2. Original title and description
3. File organization (directories)

**What AI generates:**
- Structured requirements summary
- File categorization by directory
- Clear formatting for readability

**Example AI-generated update:**

```markdown
# Add logout button

Implement logout functionality

## 📋 변경 예정 사항

다음 3개 파일에 변경사항이 있습니다:

### src/components/
- `Nav.tsx`
- `LogoutButton.tsx`

### src/api/
- `auth.ts`

---
*이 요구사항은 변경된 파일을 기반으로 자동 생성되었습니다.*
```

**Future enhancement**: Full AI analysis with diff content and semantic understanding.

## 📚 See Also

- `/gitlab-doctor` - Validate environment setup
- `/gitlab-issue-update` - Update issue from commits
- `/gitlab-mr` - Create merge request
- Commands guide: `../../shared/references/COMMANDS.md`
- Quick reference: `../../shared/references/QUICK_REFERENCE.md`

## 💡 Tips

1. **Prepare JSON files in advance** for faster workflow execution
2. **Don't worry about dirty state** - it's handled automatically
3. **Trust the rollback** - if something fails, you're safe
4. **Check issue after creation** - AI may have enhanced the description
5. **Use consistent BASE_BRANCH** - set it once in `.env` and forget it

---

**Version 2.0** - FORCED Workflow Edition
*Zero choices, maximum automation*
