#!/usr/bin/env python3
"""
Interactive Issue Creator for GitLab Workflow
Collects user input and generates JSON file for forced workflow

Usage:
    python interactive_issue_create.py

Output:
    Prints JSON file path to stdout (for piping)
    Creates JSON file in /tmp/gitlab-issue-{timestamp}.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def print_banner():
    """Print interactive mode banner"""
    print("\n" + "━" * 70)
    print("🚀 GitLab Issue Create - Interactive Mode")
    print("━" * 70)
    print()


def print_separator():
    """Print separator line"""
    print("━" * 70)


def prompt_with_label(label: str, default: str = None, required: bool = True) -> str:
    """
    Prompt user with label and optional default

    Args:
        label: Display label
        default: Default value if user presses Enter
        required: Whether field is required

    Returns:
        User input or default value
    """
    if default:
        prompt = f"{label} [default: {default}]: "
    else:
        prompt = f"{label}: "

    while True:
        try:
            value = input(prompt).strip()

            # Use default if provided and user pressed Enter
            if not value and default:
                return default

            # Check required
            if required and not value:
                print(f"   ❌ This field is required. Please enter a value.")
                continue

            return value

        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Cancelled by user")
            sys.exit(1)


def prompt_labels() -> list:
    """
    Prompt for labels (comma-separated)

    Returns:
        List of labels
    """
    labels_str = prompt_with_label(
        "🏷️  Labels (comma-separated, optional, press Enter to skip)",
        required=False
    )

    if not labels_str:
        return []

    # Split by comma and strip whitespace
    labels = [label.strip() for label in labels_str.split(',')]
    return [label for label in labels if label]  # Remove empty strings


def validate_issue_code(issue_code: str) -> bool:
    """
    Validate issue code format

    Args:
        issue_code: Issue code to validate

    Returns:
        True if valid, False otherwise
    """
    # Accept formats: VTM-1372, 1372, PROJ-123, etc.
    import re
    pattern = r'^[A-Z0-9]+-?\d*$|^\d+$'
    return bool(re.match(pattern, issue_code.upper()))


def prompt_issue_code() -> str:
    """
    Prompt for issue code with validation

    Returns:
        Valid issue code
    """
    while True:
        issue_code = prompt_with_label(
            "📌 Issue Code (e.g., VTM-1372 or 1372)",
            required=True
        )

        if validate_issue_code(issue_code):
            return issue_code.upper()
        else:
            print("   ❌ Invalid format. Use: VTM-1372, 1372, or similar")


def collect_issue_data() -> dict:
    """
    Collect issue data from user interactively

    Returns:
        Dictionary with issue data
    """
    print_banner()

    # Collect required fields
    issue_code = prompt_issue_code()
    title = prompt_with_label("📝 Title", required=True)

    # Collect optional fields
    description = prompt_with_label(
        "📄 Description (optional, press Enter to skip)",
        required=False
    )

    labels = prompt_labels()

    # Build issue data
    issue_data = {
        "issueCode": issue_code,
        "title": title
    }

    if description:
        issue_data["description"] = description

    if labels:
        issue_data["labels"] = labels

    return issue_data


def display_review(issue_data: dict) -> None:
    """
    Display collected data for review

    Args:
        issue_data: Issue data to display
    """
    print("\n" + "━" * 70)
    print("📋 Review your input:")
    print("━" * 70)
    print(f"  Issue Code:  {issue_data['issueCode']}")
    print(f"  Title:       {issue_data['title']}")

    if 'description' in issue_data:
        desc = issue_data['description']
        # Truncate long descriptions
        if len(desc) > 60:
            desc = desc[:57] + "..."
        print(f"  Description: {desc}")
    else:
        print(f"  Description: (none)")

    if 'labels' in issue_data and issue_data['labels']:
        print(f"  Labels:      {', '.join(issue_data['labels'])}")
    else:
        print(f"  Labels:      (none)")

    print("━" * 70)


def confirm_proceed() -> bool:
    """
    Ask user to confirm proceeding

    Returns:
        True if user confirms, False otherwise
    """
    while True:
        try:
            response = input("\n👉 Create GitLab issue and branch with these details? (Y/n): ").strip().lower()

            if response in ['', 'y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("   Please enter 'y' or 'n'")

        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Cancelled by user")
            return False


def save_to_json(issue_data: dict) -> str:
    """
    Save issue data to temporary JSON file

    Args:
        issue_data: Issue data to save

    Returns:
        Path to created JSON file
    """
    # Create temp directory if not exists
    temp_dir = Path("/tmp")
    temp_dir.mkdir(exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gitlab-issue-{timestamp}.json"
    filepath = temp_dir / filename

    # Write JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(issue_data, f, ensure_ascii=False, indent=2)

    return str(filepath)


def main():
    """Main interactive flow"""
    try:
        # Collect data
        issue_data = collect_issue_data()

        # Display for review
        display_review(issue_data)

        # Confirm
        if not confirm_proceed():
            print("\n❌ Cancelled by user\n")
            sys.exit(1)

        # Save to JSON
        json_path = save_to_json(issue_data)

        print(f"\n✅ JSON file created: {json_path}")

        # Output JSON path to stdout (for piping)
        # This is what the calling script will capture
        print(f"\nJSON_PATH={json_path}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
