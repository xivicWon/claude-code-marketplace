# GitLab Workflow - AI Assistant Guide

**Purpose**: This document helps AI assistants understand and effectively use the GitLab workflow automation skill.

## Skill Overview

**Name**: `gitlab-workflow`
**Domain**: Git/GitLab workflow automation
**Primary Functions**: Issue creation, branch management, merge requests, workflow automation
**Target Users**: Developers working with GitLab repositories

## When to Use This Skill

### Trigger Patterns

Use this skill when the user mentions:
- ✅ "Create GitLab issue"
- ✅ "Start workflow"
- ✅ "Create branch for issue"
- ✅ "Update issue from commits"
- ✅ "Create merge request" / "Create MR"
- ✅ "GitLab workflow"
- ✅ "Check GitLab setup"
- ✅ "Validate environment"

### Don't Use When

❌ User is asking about GitHub (different platform)
❌ User wants to read/view existing issues (use GitLab API or web interface)
❌ User needs to modify GitLab settings (use GitLab web interface)
❌ User wants to merge an existing MR (use GitLab web interface)

## Available Commands

### 1. doctor - Environment Validation ⭐ RECOMMENDED FIRST

**Purpose**: Validate all environment setup before using workflow

**When to use**:
- Before first use
- When experiencing errors
- After changing configuration
- Troubleshooting

**How to call**:
```bash
/gitlab-workflow doctor
```

**What it checks**:
1. Environment variables (GITLAB_URL, GITLAB_TOKEN, GITLAB_PROJECT)
2. Git repository status
3. Git remote configuration
4. GitLab API connectivity
5. Token permissions
6. Issue directory (optional)

**Expected output**:
- ✅ All checks passed → Ready to use
- ❌ Some checks failed → Actionable fixes provided

**AI Response Template**:
```
Let me validate your GitLab workflow setup...

[Run /gitlab-workflow doctor]

[If all passed]:
✅ Your GitLab workflow is properly configured! You can now:
- Create issues: /gitlab-workflow create
- Update issues: /gitlab-workflow update
- Create MRs: /gitlab-workflow mr

[If failed]:
❌ Found some issues with your setup:
[List specific issues]

Please fix these issues:
[Provide specific commands from doctor output]
```

### 2. create - Create Issue and Branch

**Purpose**: Create GitLab issue and corresponding Git branch

**Two Modes**:

#### Mode A: Interactive (Questions)
```bash
/gitlab-workflow create
```

**AI asks**:
1. Asana issue number? (e.g., "VTM-1372" or "1372")
2. Issue title?
3. Description? (optional)
4. Labels? (optional, comma-separated)
5. Auto-push to remote? (yes/no)

**AI Response Flow**:
```
I'll help you create a GitLab issue and branch.

Q1: What's the Asana issue identifier? (e.g., VTM-1372)
[User answers: VTM-1372]

Q2: What's the issue title?
[User answers: Add user logout button]

Q3: Issue description? (optional, press Enter to skip)
[User answers or skips]

Q4: Labels? (e.g., "feature,enhancement")
[User answers or skips]

Q5: Auto-push to remote? (yes/no)
[User answers: yes]

Creating issue and branch...
[Run command]

✅ Done!
- Issue: #342 - Add user logout button
  URL: http://gitlab.example.com/project/issues/342
- Branch: vtm-1372/342-add-user-logout-button
- Status: Pushed to remote

Next steps:
1. Make your changes
2. Commit: git commit -m "Implement logout button"
3. Update issue: /gitlab-workflow update
4. Create MR: /gitlab-workflow mr
```

#### Mode B: From JSON File
```bash
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json
```

**When to suggest JSON mode**:
- User has planned features documented
- User mentions existing requirements file
- User wants reproducible workflow
- User is creating multiple similar issues

**JSON File Structure**:
```json
{
  "asana": "VTM-1372",
  "title": "Issue title here",
  "description": "Detailed description with markdown support",
  "labels": ["feature", "enhancement"],
  "push": true
}
```

**AI Response Template**:
```
I see you have a requirements file. Let me create the issue from that file.

[Run /gitlab-workflow create --from-file path/to/issue.json]

✅ Created from JSON file:
- Issue: #342 - [title from JSON]
- Branch: vtm-1372/342-[auto-generated]
- Saved: docs/requirements/vtm-1372/342/issue.json

[Rest same as interactive mode]
```

### 3. update - Update Issue from Git History ⭐ AUTO-EXTRACTS ISSUE #

**Purpose**: Automatically update GitLab issue description with requirements from commits

**Key Feature**: **Automatically extracts issue number from current branch name** - no manual input needed!

**When to use**:
- After making commits
- Before creating MR (recommended)
- When requirements change
- To document what needs to be done

**How to call**:
```bash
# Simplest - auto-extracts issue number from branch name
/gitlab-workflow update

# With options
/gitlab-workflow update --update-title
```

**Branch Name Format**:
- Branch: `vtm-1372/345-feature-name`
- Auto-extracts: Issue #345

**What it does**:
1. Extracts issue number from current branch (e.g., `vtm-1372/345-feature` → #345)
2. Analyzes git commit history
3. Generates **requirements-focused** summary (what needs to be done, not results)
4. Updates GitLab issue description
5. Optionally updates title from first commit (with `--update-title`)

**Important - Requirements vs Results**:
- ✅ Issue description: **Requirements** (what to do)
- ✅ MR description: **Results** (what was done)
- This separation helps reviewers understand both intent and implementation

**AI Response Template**:
```
Let me update your GitLab issue with the requirements from your commits.

[If not on feature branch]:
❌ You're on branch "main". Please switch to your feature branch first:
git checkout [branch-name]

[If on feature branch]:
Analyzing commits on branch vtm-1372/345-feature-name...

📌 Auto-extracted issue number: #345

[Run /gitlab-workflow update]

✅ Updated issue #345 with requirements summary
- Extracted from: vtm-1372/345-feature-name
- Base branch: main
- Commits analyzed: 3

The issue now describes what changes are needed (requirements focus).
When you create an MR, it will show implementation details (results focus).

Next: /gitlab-workflow mr
```

### 4. mr - Create Merge Request with Auto-Generated Description

**Purpose**: Create MR with description automatically generated from git history

**When to use**:
- After completing work
- Ready to merge to main/master
- Want documented change history

**How to call**:
```bash
/gitlab-workflow mr
```

**AI asks**:
1. MR title?
2. Link to issue? (optional, issue number)
3. Target branch? (default: main)

**What it does**:
1. Analyzes git history (source vs target branch)
2. Fetches issue details (if issue number provided)
3. Generates comprehensive MR description with:
   - **Issue Summary**: Issue title, status, labels, URL
   - **Requirements**: Full issue description (요구사항)
   - **Implementation**: Summary of what was implemented (구현 내용)
   - **Changes Summary**: File statistics (files changed, insertions, deletions)
   - **Detailed Commit History**: Full commit list with authors and dates
4. Creates MR
5. Links to issue (auto-close on merge)
6. Sets remove source branch after merge

**AI Response Flow**:
```
Let me create a merge request for your changes.

Q1: MR title?
[User answers: Add user logout functionality]

Q2: Link to issue number? (will auto-close on merge)
[User answers: 342]

Q3: Target branch? (default: main)
[User answers: main or Enter]

Creating merge request...

📝 Generating MR description from git history...
✅ Generated description with issue #342 requirements

[Run command]

✅ Created merge request !123
- Title: Add user logout functionality
- Source: vtm-1372/342-add-logout → Target: main
- Linked to: Issue #342 (auto-close on merge)
- URL: http://gitlab.example.com/project/merge_requests/123

The MR includes:
- Issue summary with requirements from issue description
- Implementation summary matching requirements to commits
- 5 commits analyzed
- 12 files changed (+234, -87)
- Full commit history with dates and authors

This provides a complete view of:
1. What was requested (Requirements from Issue)
2. What was implemented (Implementation summary)
3. How it was implemented (Detailed commits)
```

### 5. help - Show Usage Help ⭐ NEW

**Purpose**: Display comprehensive help information

**When to use**:
- User asks "how do I use this?"
- User asks "what commands are available?"
- User needs syntax reference
- Troubleshooting

**How to call**:
```bash
/gitlab-workflow help
```

**What it shows**:
- All available commands
- Usage examples
- Common workflows
- Quick reference

**AI Response Template**:
```
Let me show you the GitLab workflow help.

[Run /gitlab-workflow help]

Here are the key commands:

1. **Validate Setup** (recommended first):
   /gitlab-workflow doctor

2. **Create Issue + Branch**:
   /gitlab-workflow create

3. **Update Issue** (auto-extracts issue #):
   /gitlab-workflow update

4. **Create MR**:
   /gitlab-workflow mr

Would you like me to help you with any of these?
```

## Common Workflows

### Workflow 1: Complete Feature Development

**User says**: "I need to implement a new feature"

**AI Response**:
```
I'll guide you through the complete workflow:

Step 1: Validate setup (first time users)
/gitlab-workflow doctor

Step 2: Create issue and branch
/gitlab-workflow create

[Interactive questions...]

Step 3: Implement your feature
[User makes changes and commits]

Step 4: Update issue with requirements
/gitlab-workflow update

Step 5: Create merge request
/gitlab-workflow mr

Let's start with step 1. Have you used GitLab workflow before?
```

### Workflow 2: From JSON File (Planned Feature)

**User says**: "I have a feature documented in docs/requirements/vtm-1372/342/issue.json"

**AI Response**:
```
Perfect! I can create the issue and branch directly from your JSON file.

/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json

[After creation]:
✅ Created from your requirements file!

Next steps:
1. Start coding: [file suggestions based on issue title]
2. Commit changes: git commit -m "..."
3. Update issue: /gitlab-workflow update
4. Create MR: /gitlab-workflow mr
```

### Workflow 3: Update Existing Work

**User says**: "I've made some commits, how do I update the issue?"

**AI Response**:
```
I'll update your GitLab issue with a requirements summary from your commits.

First, let me check your current branch:
[Run: git branch --show-current]

Current branch: vtm-1372/345-feature-name

Great! I'll automatically extract issue #345 from your branch name.

/gitlab-workflow update

[After update]:
✅ Issue #345 updated with requirements from your commits!

The issue now shows what needs to be done (requirements focus).
When you're ready to merge, run: /gitlab-workflow mr
```

### Workflow 4: Troubleshooting

**User says**: "GitLab workflow isn't working"

**AI Response**:
```
Let me diagnose the problem:

/gitlab-workflow doctor

[After diagnosis]:

[If failures]:
I found these issues:
1. [Issue from doctor output]
2. [Issue from doctor output]

Here's how to fix them:
[Specific commands from doctor]

[If all passed]:
Your setup looks good! What specific error are you seeing?
[Continue troubleshooting based on error]
```

## Error Handling

### Environment Not Configured

**Error**: "GITLAB_URL required"

**AI Response**:
```
Your GitLab workflow isn't configured yet. Let me help you set it up.

1. Create configuration file:
   .claude/.env.gitlab-workflow

2. Add these variables:
   GITLAB_URL=http://your-gitlab-server.com
   GITLAB_TOKEN=glpat-xxxxxxxxxxxxx
   GITLAB_PROJECT=your-group/your-project
   GITLAB_REMOTE=gitlab  # or origin

3. Get GitLab token:
   - Go to GitLab → User Settings → Access Tokens
   - Create token with 'api' scope
   - Copy token to config file

4. Verify setup:
   /gitlab-workflow doctor

Need help with any of these steps?
```

### Invalid Branch Name

**Error**: "Invalid branch name"

**AI Response**:
```
The branch name must follow this format:
{asana}/{gitlab#}-{summary}

Examples:
✅ VTM-1372/342-add-feature
✅ 1372/342-fix-bug
❌ 342-feature (missing Asana identifier)
❌ VTM-1372-342 (wrong separator, use /)

Let me help you create a proper branch name.
What's your Asana issue and what feature are you working on?
```

### Not in Git Repository

**Error**: "Not in a git repository"

**AI Response**:
```
You're not in a git repository.

Are you in the correct directory? Let me check:
pwd

If this is the wrong directory, navigate to your project:
cd /path/to/your/project

If you need to initialize a git repository:
git init
git remote add gitlab http://your-gitlab-server.com/project.git
```

### API Connection Failed

**Error**: "GitLab API: Connection failed"

**AI Response**:
```
Can't connect to GitLab API. Let me help troubleshoot:

1. Check URL is correct:
   echo $GITLAB_URL
   Expected: http://192.168.210.103:90

2. Test connectivity:
   curl -I http://192.168.210.103:90

3. Verify token is valid:
   - Go to GitLab → User Settings → Access Tokens
   - Check if token exists and has 'api' scope
   - Regenerate if needed

4. Verify project path:
   echo $GITLAB_PROJECT
   Expected: withvtm_2.0/withvtm-fe

5. Run full diagnostic:
   /gitlab-workflow doctor

What does the doctor command show?
```

## Decision Tree for AI

```
User mentions GitLab workflow
├─ First time user?
│  └─ YES → Run /gitlab-workflow doctor
│     └─ Setup not complete?
│        └─ Guide through configuration
│
├─ Wants to create issue?
│  ├─ Has JSON file?
│  │  └─ YES → /gitlab-workflow create --from-file
│  └─ NO → /gitlab-workflow create (interactive)
│
├─ Made commits, needs to update issue?
│  └─ /gitlab-workflow update
│     └─ On feature branch?
│        ├─ YES → Auto-extracts issue #
│        └─ NO → Tell user to switch branch
│
├─ Ready to create MR?
│  └─ /gitlab-workflow mr (interactive)
│     └─ Suggest linking to issue
│
├─ Having issues?
│  └─ /gitlab-workflow doctor
│     └─ Provide fixes based on results
│
└─ Needs help?
   └─ /gitlab-workflow help
```

## Best Practices for AI Assistants

### 1. Always Start with Doctor

For first-time users or troubleshooting:
```
Before we begin, let me validate your setup:
/gitlab-workflow doctor
```

### 2. Guide Through Interactive Mode

Don't just run commands, explain each step:
```
I'll help you create the issue. I need to ask you 5 questions:

1. Asana issue (e.g., VTM-1372):
2. Issue title:
3. Description (optional):
4. Labels (optional):
5. Auto-push (yes/no):
```

### 3. Suggest Next Steps

After each command, tell user what's next:
```
✅ Issue created!

Next steps:
1. Make your changes
2. Commit with: git commit -m "message"
3. Update issue: /gitlab-workflow update
4. Create MR: /gitlab-workflow mr
```

### 4. Explain Auto-Extraction

When using update command, emphasize no manual input needed:
```
✨ Smart feature: I'll automatically extract the issue number from your branch name!

Current branch: vtm-1372/345-feature
Auto-detected: Issue #345

No need to remember or type the issue number!
```

### 5. Provide Context

Explain why commands are needed:
```
Why update the issue before MR?
- Issue description: Requirements (what needs to be done)
- MR description: Implementation (what was done)
- Helps reviewers understand both intent and execution
```

### 6. Use Visual Formatting

Make responses easy to scan:
```
✅ Success indicators
❌ Error indicators
📝 Info indicators
⚠️  Warning indicators
💡 Tips and suggestions
```

## Quick Reference for AI

| User Intent | Command | Notes |
|-------------|---------|-------|
| "Setup GitLab workflow" | `/gitlab-workflow doctor` | First time setup |
| "Create new issue" | `/gitlab-workflow create` | Interactive or JSON |
| "I made commits" | `/gitlab-workflow update` | Auto-extracts issue # |
| "Ready to merge" | `/gitlab-workflow mr` | Links to issue |
| "How do I...?" | `/gitlab-workflow help` | Show all commands |
| "Something's wrong" | `/gitlab-workflow doctor` | Diagnose issues |

## Environment Variables Reference

For helping users configure:

```bash
# Required
GITLAB_URL=http://192.168.210.103:90          # GitLab server URL
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx       # Personal access token (api scope)
GITLAB_PROJECT=withvtm_2.0/withvtm-fe         # Project path (group/project)

# Optional
GITLAB_REMOTE=gitlab                          # Git remote name (default: auto-detect)
ISSUE_DIR=docs/requirements                   # Where to save issue.json files
```

## Response Templates

### Template: First Time Setup

```
Welcome to GitLab workflow! Let me help you get started.

Step 1: Validate environment
/gitlab-workflow doctor

[If not configured]:
You need to set up your GitLab credentials:

1. Create: .claude/.env.gitlab-workflow
2. Add these lines:
   GITLAB_URL=http://your-gitlab-server
   GITLAB_TOKEN=your-personal-access-token
   GITLAB_PROJECT=group/project

3. Get your token:
   - GitLab → Settings → Access Tokens
   - Scope: 'api'

4. Verify:
   /gitlab-workflow doctor

[If configured]:
✅ You're all set! Let's create your first issue:
/gitlab-workflow create
```

### Template: Complete Workflow

```
I'll guide you through the complete workflow:

**Step 1: Create Issue & Branch**
/gitlab-workflow create

[User completes interactive questions]

**Step 2: Develop Feature**
[User makes changes and commits]

**Step 3: Update Issue with Requirements**
/gitlab-workflow update

This auto-extracts issue #[number] from your branch and updates
the issue with a requirements summary.

**Step 4: Create Merge Request**
/gitlab-workflow mr

This auto-generates an MR description from your commits and
links to the issue for auto-close on merge.

Let's start! Ready for step 1?
```

### Template: JSON File Workflow

```
I see you want to work with a JSON file. Great choice for reproducibility!

Your JSON should have this structure:
```json
{
  "asana": "VTM-1372",
  "title": "Feature title",
  "description": "Details...",
  "labels": ["feature"],
  "push": true
}
```

Location: docs/requirements/vtm-1372/342/issue.json

Ready to create? Run:
/gitlab-workflow create --from-file [path-to-json]
```

### Template: Troubleshooting

```
Let me diagnose the issue:

/gitlab-workflow doctor

[Review output]

Common issues and fixes:

1. **Missing token**:
   Add to .claude/.env.gitlab-workflow:
   GITLAB_TOKEN=glpat-xxxxx

2. **No git remote**:
   git remote add gitlab http://[url]

3. **Wrong branch format**:
   Use: {asana}/{gitlab#}-{summary}
   Example: VTM-1372/342-feature

Which issue are you seeing?
```

## Advanced Features

### Auto-Height in issue.json

When creating issue definitions for UI components:

```json
{
  "asana": "VTM-1372",
  "title": "Update table to use auto-height pattern",
  "description": "Migrate GenericTable to auto-height pattern\n\n## Changes\n- Add `auto-height=\"true\"`\n- Verify parent has height\n- Test in dialog/widget",
  "labels": ["refactoring", "ui"]
}
```

### Conventional Commits

The update command automatically removes conventional commit prefixes:

```
Commit: "feat: Add user dashboard"
Issue title: "Add user dashboard" (prefix removed)
```

### Requirements vs Implementation

Emphasize the difference:

```
**Issue Update** (/gitlab-workflow update):
- Focus: Requirements (what needs to be done)
- Audience: Project managers, designers
- Format: Bullet points of changes needed

**MR Creation** (/gitlab-workflow mr):
- Focus: Implementation (what was done)
- Audience: Code reviewers, developers
- Format: Commit history, statistics, technical details
```

## Summary

This skill automates the complete GitLab workflow from issue creation to merge request. As an AI assistant:

1. **Start with doctor** for new users
2. **Guide interactively** through create/update/mr
3. **Explain auto-features** (issue # extraction, description generation)
4. **Provide context** for each step
5. **Troubleshoot** with doctor command
6. **Emphasize best practices** (update before MR, requirements vs results)

Always be helpful, explain why steps are needed, and guide users through the complete workflow!
