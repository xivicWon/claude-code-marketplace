#!/usr/bin/env bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the markdown file (skipping frontmatter)
CONTENT=$(awk '/^---$/{flag=!flag;next}!flag' "$SCRIPT_DIR/user-prompt-submit.md")

# Output as JSON for hook system
cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": $(echo "$CONTENT" | jq -Rs .)
  }
}
EOF

exit 0
