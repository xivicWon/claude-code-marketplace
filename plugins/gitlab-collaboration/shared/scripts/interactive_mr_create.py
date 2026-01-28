#!/usr/bin/env python3
"""
Interactive MR Creator for GitLab Workflow
Auto-detects MR details and allows user to confirm or edit

Usage:
    python interactive_mr_create.py

Output:
    Prints JSON file path to stdout (for piping)
    Creates JSON file in /tmp/gitlab-mr-{timestamp}.json
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_banner():
    """Print interactive mode banner"""
    print("\n" + "━" * 70)
    print("🔍 GitLab MR Create - Auto-detect Mode")
    print("━" * 70)
    print()


def get_current_branch() -> str:
    """Get current git branch"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository", file=sys.stderr)
        sys.exit(1)


def extract_issue_iid(branch_name: str) -> int:
    """
    Extract issue IID from branch name

    Args:
        branch_name: Branch name (e.g., vtm-1372/342-feature)

    Returns:
        Issue IID or None
    """
    match = re.search(r'/(\d+)', branch_name)
    return int(match.group(1)) if match else None


def get_first_commit_subject(branch_name: str, target_branch: str = 'main') -> str:
    """
    Get first commit subject from branch

    Args:
        branch_name: Source branch
        target_branch: Target branch

    Returns:
        First commit subject or None
    """
    try:
        # Get first commit in branch (compared to target)
        result = subprocess.run(
            ['git', 'log', f'{target_branch}..{branch_name}', '--format=%s', '--reverse'],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.strip().split('\n')
        if commits and commits[0]:
            subject = commits[0]
            # Remove conventional commit prefix
            subject = re.sub(r'^(feat|fix|refactor|docs|style|test|chore):\s*', '', subject)
            return subject
    except:
        pass
    return None


def auto_detect_mr_details() -> dict:
    """
    Auto-detect MR details from current state

    Returns:
        Dictionary with auto-detected details
    """
    # Source branch (current)
    source_branch = get_current_branch()

    # Target branch (from env or default)
    target_branch = os.getenv('BASE_BRANCH', 'main')

    # Issue IID (from branch name)
    issue_iid = extract_issue_iid(source_branch)

    # Title (from first commit or branch name)
    title = get_first_commit_subject(source_branch, target_branch)
    if not title:
        # Fallback: use branch name
        title = source_branch.split('/')[-1].replace('-', ' ').title()

    return {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'issue_iid': issue_iid,
        'title': title
    }


def display_detected_details(details: dict) -> None:
    """
    Display auto-detected details

    Args:
        details: Detected MR details
    """
    print("━" * 70)
    print("📋 Auto-detected MR details:")
    print("━" * 70)
    print(f"  Source Branch: {details['source_branch']}")
    print(f"  Target Branch: {details['target_branch']} (from .env)")

    if details['issue_iid']:
        print(f"  Issue Number:  #{details['issue_iid']} (from branch name)")
    else:
        print(f"  Issue Number:  (none)")

    print(f"  MR Title:      {details['title']}")
    print("━" * 70)


def prompt_menu() -> str:
    """
    Display menu and get user choice

    Returns:
        User choice (1-5)
    """
    print("\n👉 Options:")
    print("  1. Proceed with these details (Recommended)")
    print("  2. Edit MR title")
    print("  3. Change target branch")
    print("  4. Skip issue linking")
    print("  5. Cancel")

    while True:
        try:
            choice = input("\nChoose (1-5): ").strip()

            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("   Please enter 1, 2, 3, 4, or 5")

        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Cancelled by user")
            return '5'


def edit_title(current_title: str) -> str:
    """
    Edit MR title

    Args:
        current_title: Current title

    Returns:
        New title
    """
    print(f"\nCurrent title: {current_title}")
    new_title = input("New title: ").strip()

    if not new_title:
        print("   ⚠️  Title cannot be empty, keeping current title")
        return current_title

    return new_title


def edit_target_branch(current_target: str) -> str:
    """
    Edit target branch

    Args:
        current_target: Current target branch

    Returns:
        New target branch
    """
    print(f"\nCurrent target: {current_target}")
    new_target = input("New target branch: ").strip()

    if not new_target:
        print("   ⚠️  Target cannot be empty, keeping current target")
        return current_target

    return new_target


def interactive_menu(details: dict) -> dict:
    """
    Interactive menu for editing details

    Args:
        details: Initial detected details

    Returns:
        Final MR details (possibly edited)
    """
    while True:
        display_detected_details(details)
        choice = prompt_menu()

        if choice == '1':
            # Proceed
            return details

        elif choice == '2':
            # Edit title
            details['title'] = edit_title(details['title'])

        elif choice == '3':
            # Change target branch
            details['target_branch'] = edit_target_branch(details['target_branch'])

        elif choice == '4':
            # Skip issue linking
            details['issue_iid'] = None
            print("   ✅ Issue linking disabled")

        elif choice == '5':
            # Cancel
            print("\n❌ Cancelled by user\n")
            sys.exit(1)


def save_to_json(mr_details: dict) -> str:
    """
    Save MR details to temporary JSON file

    Args:
        mr_details: MR details to save

    Returns:
        Path to created JSON file
    """
    # Create temp directory if not exists
    temp_dir = Path("/tmp")
    temp_dir.mkdir(exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gitlab-mr-{timestamp}.json"
    filepath = temp_dir / filename

    # Prepare JSON data (only include what's needed)
    json_data = {
        "title": mr_details['title'],
        "targetBranch": mr_details['target_branch']
    }

    # Only include issue if set
    if mr_details.get('issue_iid'):
        json_data["issueIID"] = mr_details['issue_iid']

    # Write JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return str(filepath)


def main():
    """Main interactive flow"""
    try:
        print_banner()

        # Auto-detect details
        print("⏳ Detecting MR details from current branch...\n")
        details = auto_detect_mr_details()

        # Interactive menu
        final_details = interactive_menu(details)

        # Save to JSON
        json_path = save_to_json(final_details)

        print(f"\n✅ JSON file created: {json_path}")

        # Output JSON path to stdout (for piping)
        print(f"\nJSON_PATH={json_path}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
