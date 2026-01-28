#!/usr/bin/env python3
"""
GitLab Workflow Automation
Automates issue creation -> branch creation -> merge request workflow

Version 2.0: Forced Workflow Edition
- JSON-only input (no interactive prompts)
- Automatic dirty state handling (stash → switch → pull → branch → push → pop)
- AI-powered issue updates
- Rollback on failure
"""

import argparse
import getpass
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote_plus
import urllib.request
import urllib.error


# ═══════════════════════════════════════════════════════════════
# Workflow State Management
# ═══════════════════════════════════════════════════════════════

@dataclass
class WorkflowState:
    """Track workflow state for atomic rollback on failure"""

    completed_steps: List[str] = field(default_factory=list)
    issue_iid: Optional[int] = None
    branch_name: Optional[str] = None
    original_branch: Optional[str] = None
    stashed: bool = False
    stashed_files: List[str] = field(default_factory=list)
    stash_ref: Optional[str] = None  # stash reference for rollback

    def mark(self, step: str) -> None:
        """Mark a step as completed"""
        self.completed_steps.append(step)

    def has(self, step: str) -> bool:
        """Check if a step was completed"""
        return step in self.completed_steps


@dataclass
class WorkflowResult:
    """Result of workflow execution"""

    success: bool
    issue_iid: Optional[int] = None
    issue_title: Optional[str] = None
    issue_url: Optional[str] = None
    branch_name: Optional[str] = None
    pushed: bool = False
    ai_updated: bool = False
    error: Optional[str] = None


class WorkflowError(Exception):
    """Raised when forced workflow fails"""
    pass


def run_interactive_script(script_name: str) -> Optional[str]:
    """
    Run interactive script and extract JSON path from output

    Args:
        script_name: Name of the interactive script to run

    Returns:
        Path to generated JSON file, or None if failed
    """
    try:
        # Get script directory (same directory as this file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, script_name)

        # Check if script exists
        if not os.path.exists(script_path):
            print(f"Error: Interactive script not found: {script_path}", file=sys.stderr)
            return None

        # Run interactive script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )

        # Check if successful
        if result.returncode != 0:
            print(f"Interactive script failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return None

        # Extract JSON_PATH from output
        for line in result.stdout.split('\n'):
            if line.startswith('JSON_PATH='):
                json_path = line.split('=', 1)[1].strip()
                return json_path

        print("Error: Could not find JSON_PATH in script output", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Error running interactive script: {e}", file=sys.stderr)
        return None


def load_env_file(env_file_path: str) -> None:
    """
    Load environment variables from .env file

    Args:
        env_file_path: Path to .env file
    """
    if not os.path.exists(env_file_path):
        return

    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key and not os.getenv(key):
                        os.environ[key] = value
    except Exception as e:
        print(f"Warning: Failed to load .env file: {e}", file=sys.stderr)


def initialize_env_file(env_file_path: str) -> bool:
    """
    Initialize GitLab workflow environment with interactive prompts

    Args:
        env_file_path: Path to .env file to create

    Returns:
        True if successful, False otherwise
    """
    print("🚀 GitLab Workflow Initialization\n")
    print("This will help you set up GitLab workflow environment.\n")

    # Check if file exists
    if os.path.exists(env_file_path):
        print(f"⚠️  Configuration file already exists: {env_file_path}\n")

        # Offer backup option
        response = input("Do you want to backup and create new configuration? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Initialization cancelled.")
            return False

        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{env_file_path}.backup.{timestamp}"
        try:
            with open(env_file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"✅ Backed up existing configuration to: {backup_path}\n")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            print("Continuing anyway...\n")

    # Collect required configuration
    print("📋 Required Configuration")
    print("━" * 60 + "\n")

    # 1. GitLab URL
    while True:
        gitlab_url = input("1. GitLab URL (e.g., https://gitlab.com or http://192.168.210.103:90)\n   > ").strip()
        if gitlab_url:
            # Validate URL format
            if gitlab_url.startswith('http://') or gitlab_url.startswith('https://'):
                gitlab_url = gitlab_url.rstrip('/')
                break
            else:
                print("   ❌ Invalid URL format. Must start with http:// or https://")
        else:
            print("   ❌ GitLab URL is required")

    # 2. GitLab Token
    while True:
        print("\n2. GitLab Personal Access Token")
        print("   Get from: GitLab → Settings → Access Tokens (scope: 'api')")
        gitlab_token = getpass.getpass("   > ").strip()
        if gitlab_token:
            # Validate token format (GitLab tokens usually start with glpat-)
            if not gitlab_token.startswith('glpat-'):
                print("   ⚠️  Token doesn't start with 'glpat-'. Are you sure it's correct? (y/n): ", end='')
                confirm = input().strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        else:
            print("   ❌ GitLab Token is required")

    # 3. GitLab Project
    while True:
        gitlab_project = input("\n3. GitLab Project (format: namespace/project-name)\n   > ").strip()
        if gitlab_project:
            # Validate project format
            if '/' in gitlab_project:
                break
            else:
                print("   ❌ Invalid format. Must be: namespace/project-name")
        else:
            print("   ❌ GitLab Project is required")

    # Collect optional configuration
    print("\n⚙️  Optional Configuration (press Enter for defaults)")
    print("━" * 60 + "\n")

    # 4. Git Remote
    gitlab_remote = input("4. Git Remote Name [default: auto-detect]\n   > ").strip()

    # 5. Issue Directory
    issue_dir = input("\n5. Issue Directory [default: docs/requirements]\n   > ").strip()
    if not issue_dir:
        issue_dir = "docs/requirements"

    # 6. Base Branch
    base_branch = input("\n6. Base Branch [default: main]\n   > ").strip()
    if not base_branch:
        base_branch = "main"

    # Create .claude directory if needed
    claude_dir = os.path.dirname(env_file_path)
    if not os.path.exists(claude_dir):
        try:
            os.makedirs(claude_dir, mode=0o700)
            print(f"\n📁 Created directory: {claude_dir}")
        except Exception as e:
            print(f"\n❌ Failed to create directory {claude_dir}: {e}", file=sys.stderr)
            return False

    # Generate .env file content
    env_content = f"""# GitLab Workflow Environment Configuration
# Generated by: /gitlab-init on {datetime.now().strftime('%Y-%m-%d')}

# Required - GitLab instance URL
GITLAB_URL={gitlab_url}

# Required - Personal Access Token (must have 'api' scope)
# Get from: GitLab → Settings → Access Tokens
GITLAB_TOKEN={gitlab_token}

# Required - Project ID or path (format: namespace/project-name)
GITLAB_PROJECT={gitlab_project}
"""

    # Add optional fields if provided
    if gitlab_remote:
        env_content += f"""
# Optional - Git remote name (default: auto-detect from 'gitlab' or 'origin')
GITLAB_REMOTE={gitlab_remote}
"""

    env_content += f"""
# Optional - Directory to save issue.json files (default: docs/requirements)
ISSUE_DIR={issue_dir}

# Optional - Base branch for creating new branches (default: main)
# Can be branch name only or include remote name
# Examples:
#   BASE_BRANCH=main              # Uses default remote (gitlab or origin)
#   BASE_BRANCH=develop           # Uses default remote
#   BASE_BRANCH=origin/main       # Explicitly use origin remote
#   BASE_BRANCH=gitlab/develop    # Explicitly use gitlab remote
BASE_BRANCH={base_branch}
"""

    # Write to file
    try:
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)

        # Set secure permissions (600 - owner read/write only)
        os.chmod(env_file_path, 0o600)

        print(f"\n✅ Configuration saved to: {env_file_path}")
        print(f"🔒 File permissions set to 600 (owner read/write only)\n")

        # Display summary (mask token)
        masked_token = gitlab_token[:7] + '*' * (len(gitlab_token) - 10) + gitlab_token[-3:]
        print("Settings:")
        print(f"  - GitLab URL: {gitlab_url}")
        print(f"  - Project: {gitlab_project}")
        print(f"  - Token: {masked_token}")
        if gitlab_remote:
            print(f"  - Remote: {gitlab_remote}")
        print(f"  - Issue Dir: {issue_dir}")
        print(f"  - Base Branch: {base_branch}")

        return True

    except Exception as e:
        print(f"\n❌ Failed to write configuration file: {e}", file=sys.stderr)
        return False


class GitLabWorkflow:
    """GitLab workflow automation for issue->branch->MR"""

    def __init__(self, gitlab_url: str, token: str, project_id: str, remote_name: Optional[str] = None, issue_dir: Optional[str] = None):
        """
        Initialize GitLab workflow

        Args:
            gitlab_url: GitLab instance URL
            token: Personal Access Token
            project_id: Project ID or path
            remote_name: Git remote name (optional, auto-detects if not provided)
            issue_dir: Directory to save issue.json files (optional)
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.api_url = f"{self.gitlab_url}/api/v4"
        self.token = token
        self.project_id = project_id
        self.remote_name = remote_name
        self.issue_dir = issue_dir
        self.headers = {
            'PRIVATE-TOKEN': token,
            'Content-Type': 'application/json'
        }

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None
    ):
        """Make HTTP request to GitLab API"""
        url = f"{self.api_url}/{endpoint}"
        req_data = json.dumps(data).encode('utf-8') if data else None
        request = urllib.request.Request(url, data=req_data, headers=self.headers, method=method)

        try:
            with urllib.request.urlopen(request) as response:
                if response.status == 204:
                    return None
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_msg)
                raise Exception(f"GitLab API Error ({e.code}): {error_data}")
            except json.JSONDecodeError:
                raise Exception(f"GitLab API Error ({e.code}): {error_msg}")

    def validate_branch_name(self, branch_name: str) -> bool:
        """
        Validate branch name follows {issue-code}/{gitlab}-{summary} format

        Args:
            branch_name: Branch name to validate

        Returns:
            True if valid, False otherwise
        """
        # Pattern: VTM-1372/307-feature-name or 1372/307-feature-name
        # Issue code part can be any string, GitLab part must be a number
        pattern = r'^.+/\d+.*$'
        return bool(re.match(pattern, branch_name, re.IGNORECASE))

    def create_issue(
        self,
        title: str,
        description: Optional[str] = None,
        labels: Optional[str] = None
    ) -> Dict:
        """Create GitLab issue"""
        data = {'title': title}
        if description:
            data['description'] = description
        if labels:
            data['labels'] = labels

        issue = self._make_request(
            f"projects/{quote_plus(self.project_id)}/issues",
            method='POST',
            data=data
        )
        return issue

    def update_issue(
        self,
        issue_iid: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Update existing GitLab issue
        
        Args:
            issue_iid: GitLab issue IID
            title: New title (optional)
            description: New description (optional)
            labels: New labels (optional)
            
        Returns:
            Updated issue data
        """
        data = {}
        if title:
            data['title'] = title
        if description:
            data['description'] = description
        if labels:
            data['labels'] = ','.join(labels) if isinstance(labels, list) else labels

        issue = self._make_request(
            f"projects/{quote_plus(self.project_id)}/issues/{issue_iid}",
            method='PUT',
            data=data
        )
        return issue

    def get_issue(self, issue_iid: int) -> Dict:
        """
        Get GitLab issue by IID
        
        Args:
            issue_iid: GitLab issue IID
            
        Returns:
            Issue data
        """
        issue = self._make_request(
            f"projects/{quote_plus(self.project_id)}/issues/{issue_iid}",
            method='GET'
        )
        return issue

    def is_working_directory_clean(self) -> bool:
        """
        Check if working directory is clean (no uncommitted changes)

        Returns:
            True if clean, False if dirty
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            # If output is empty, working directory is clean
            return len(result.stdout.strip()) == 0
        except subprocess.CalledProcessError:
            return False

    def get_dirty_files(self) -> List[str]:
        """
        Get list of modified/untracked files

        Returns:
            List of file paths with changes
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Format: "XY filename"
                    files.append(line[3:])  # Skip status code
            return files
        except subprocess.CalledProcessError:
            return []

    def commit_current_changes(self, commit_message: Optional[str] = None) -> bool:
        """
        Commit all current changes to current branch

        Args:
            commit_message: Commit message (auto-generated if not provided)

        Returns:
            True if successful
        """
        try:
            # Get current branch for context
            current_branch = self.get_current_branch()

            # Auto-generate commit message if not provided
            if not commit_message:
                dirty_files = self.get_dirty_files()
                file_count = len(dirty_files)
                commit_message = f"WIP: Auto-commit {file_count} file(s) before workflow operation"

            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)

            # Commit
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                check=True,
                capture_output=True
            )

            print(f"✅ Committed changes to {current_branch}")
            print(f"   Message: {commit_message}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"Failed to commit changes: {error_msg}")

    def stash_changes(self, stash_message: Optional[str] = None) -> bool:
        """
        Stash current changes

        Args:
            stash_message: Stash message (auto-generated if not provided)

        Returns:
            True if successful
        """
        try:
            if not stash_message:
                stash_message = "Auto-stash for workflow operation"

            subprocess.run(
                ['git', 'stash', 'push', '-m', stash_message],
                check=True,
                capture_output=True
            )

            print(f"✅ Stashed changes: {stash_message}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"Failed to stash changes: {error_msg}")

    def pop_stash(self) -> bool:
        """
        Pop most recent stash

        Returns:
            True if successful
        """
        try:
            subprocess.run(['git', 'stash', 'pop'], check=True, capture_output=True)
            print(f"✅ Applied stashed changes")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"Failed to pop stash: {error_msg}")

    def handle_dirty_working_directory_for_issue_create(self) -> str:
        """
        Handle dirty working directory when creating new issue/branch

        Returns:
            Action taken: 'move_to_new', 'commit_current', 'cancel'
        """
        dirty_files = self.get_dirty_files()
        if not dirty_files:
            return 'clean'

        current_branch = self.get_current_branch()
        file_count = len(dirty_files)

        print(f"\n⚠️  Working directory has {file_count} uncommitted change(s)")
        print(f"   Current branch: {current_branch}")
        print(f"\n   Modified files:")
        for f in dirty_files[:5]:  # Show first 5
            print(f"   - {f}")
        if len(dirty_files) > 5:
            print(f"   ... and {len(dirty_files) - 5} more files")

        print(f"\n📝 What would you like to do?")
        print(f"   1. Move changes to new branch (Recommended)")
        print(f"      → Stash → Create new branch → Apply stashed changes")
        print(f"   2. Commit to current branch ({current_branch})")
        print(f"      → Commit here → Create clean new branch")
        print(f"   3. Cancel")

        while True:
            try:
                choice = input("\n👉 Choose (1/2/3): ").strip()

                if choice == '1':
                    # Move to new branch
                    print(f"\n📦 Stashing changes...")
                    self.stash_changes(f"Auto-stash for new issue branch")
                    return 'move_to_new'

                elif choice == '2':
                    # Commit to current branch
                    print(f"\n💾 Committing to {current_branch}...")
                    commit_msg = input("   Commit message (or press Enter for auto-generated): ").strip()
                    self.commit_current_changes(commit_msg if commit_msg else None)
                    return 'commit_current'

                elif choice == '3':
                    print(f"\n❌ Cancelled")
                    return 'cancel'

                else:
                    print("   ❌ Invalid choice. Please enter 1, 2, or 3.")

            except (EOFError, KeyboardInterrupt):
                print(f"\n\n❌ Cancelled by user")
                return 'cancel'

    def handle_dirty_working_directory_for_mr(self) -> str:
        """
        Handle dirty working directory when creating MR

        Returns:
            Action taken: 'commit_current', 'move_to_temp', 'cancel'
        """
        dirty_files = self.get_dirty_files()
        if not dirty_files:
            return 'clean'

        current_branch = self.get_current_branch()
        file_count = len(dirty_files)

        print(f"\n⚠️  Working directory has {file_count} uncommitted change(s)")
        print(f"   Current branch: {current_branch}")
        print(f"\n   Modified files:")
        for f in dirty_files[:5]:  # Show first 5
            print(f"   - {f}")
        if len(dirty_files) > 5:
            print(f"   ... and {len(dirty_files) - 5} more files")

        print(f"\n📝 What would you like to do?")
        print(f"   1. Commit to current branch (Recommended)")
        print(f"      → Add all → Commit → Create MR with these changes")
        print(f"   2. Move to temporary branch")
        print(f"      → Stash → Create temp branch → Apply stash → MR without these changes")
        print(f"   3. Cancel")

        while True:
            try:
                choice = input("\n👉 Choose (1/2/3): ").strip()

                if choice == '1':
                    # Commit to current branch
                    print(f"\n💾 Committing to {current_branch}...")
                    commit_msg = input("   Commit message (or press Enter for auto-generated): ").strip()
                    self.commit_current_changes(commit_msg if commit_msg else None)
                    return 'commit_current'

                elif choice == '2':
                    # Move to temp branch
                    print(f"\n📦 Moving changes to temporary branch...")

                    # Generate temp branch name
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    temp_branch = f"temp/{current_branch}_wip_{timestamp}"

                    # Stash changes
                    self.stash_changes(f"Auto-stash for MR creation")

                    # Create temp branch from current
                    subprocess.run(
                        ['git', 'checkout', '-b', temp_branch],
                        check=True,
                        capture_output=True
                    )

                    # Apply stash
                    self.pop_stash()

                    print(f"✅ Created temporary branch: {temp_branch}")
                    print(f"   Changes are now in temp branch")

                    # Switch back to original branch
                    subprocess.run(
                        ['git', 'checkout', current_branch],
                        check=True,
                        capture_output=True
                    )

                    print(f"✅ Switched back to: {current_branch} (now clean)")
                    print(f"   Temp branch '{temp_branch}' has your WIP changes")

                    return 'move_to_temp'

                elif choice == '3':
                    print(f"\n❌ Cancelled")
                    return 'cancel'

                else:
                    print("   ❌ Invalid choice. Please enter 1, 2, or 3.")

            except (EOFError, KeyboardInterrupt):
                print(f"\n\n❌ Cancelled by user")
                return 'cancel'

    def create_branch(self, branch_name: str, ref: str = 'main', skip_dirty_check: bool = False) -> bool:
        """
        Create Git branch locally from remote reference

        Args:
            branch_name: Name of the branch to create
            ref: Reference branch to create from (default: main)
                 Can be: 'main', 'develop', 'origin/main', 'gitlab/develop'
            skip_dirty_check: Skip dirty working directory check (default: False)
                             Use when caller has already handled dirty state

        Returns:
            True if successful
        """
        # Validate branch name
        if not self.validate_branch_name(branch_name):
            raise ValueError(
                f"Invalid branch name: {branch_name}\n"
                f"Branch name must follow format: [이슈코드]/[GitLab#]-[summary]\n"
                f"Examples: VTM-999/307-feature-name, 1372/307-action-assignee-removal"
            )

        # Check if working directory is clean (unless skipped)
        if not skip_dirty_check and not self.is_working_directory_clean():
            dirty_files = self.get_dirty_files()
            file_list = '\n'.join(f"  - {f}" for f in dirty_files[:10])  # Show first 10
            if len(dirty_files) > 10:
                file_list += f"\n  ... and {len(dirty_files) - 10} more files"

            raise Exception(
                f"Cannot create branch: Working directory has uncommitted changes\n"
                f"\nModified/untracked files:\n{file_list}\n\n"
                f"Please commit or stash your changes first:\n"
                f"  git add .\n"
                f"  git commit -m 'Your message'\n"
                f"Or:\n"
                f"  git stash\n"
            )

        try:
            # Parse ref to determine if it includes remote
            if '/' in ref:
                # ref already includes remote (e.g., 'origin/main', 'gitlab/develop')
                remote_ref = ref
                remote_name = ref.split('/')[0]
            else:
                # ref is just branch name (e.g., 'main', 'develop')
                # Prepend default remote
                remote_name = self.get_remote_name()
                remote_ref = f'{remote_name}/{ref}'

            # Fetch latest changes from the remote
            print(f"🔄 Fetching latest changes from {remote_name}...")
            subprocess.run(['git', 'fetch', remote_name], check=True, capture_output=True)

            # Verify that the remote ref exists
            verify_result = subprocess.run(
                ['git', 'rev-parse', '--verify', remote_ref],
                capture_output=True,
                text=True
            )
            if verify_result.returncode != 0:
                raise Exception(
                    f"Remote branch '{remote_ref}' not found\n"
                    f"Available remote branches:\n"
                    f"  git branch -r\n"
                )

            # Create and checkout new branch from remote ref
            subprocess.run(['git', 'checkout', '-b', branch_name, remote_ref],
                         check=True, capture_output=True)

            print(f"✅ Created branch: {branch_name}")
            print(f"   Based on: {remote_ref}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"Failed to create branch: {error_msg}")

    def push_branch(self, branch_name: str, set_upstream: bool = True) -> bool:
        """
        Push branch to remote

        Args:
            branch_name: Name of the branch to push
            set_upstream: Set upstream tracking (default: True)

        Returns:
            True if successful
        """
        try:
            # Get remote name
            remote = self.get_remote_name()

            if set_upstream:
                subprocess.run(
                    ['git', 'push', '-u', remote, branch_name],
                    check=True,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ['git', 'push', remote, branch_name],
                    check=True,
                    capture_output=True
                )

            print(f"✅ Pushed branch: {branch_name}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise Exception(f"Failed to push branch: {error_msg}")

    def save_issue_json(
        self,
        issue_iid: int,
        issue_code: str,
        branch_name: str,
        issue_title: str,
        issue_description: str,
        labels: List[str],
        pushed: bool
    ) -> Optional[str]:
        """
        Save issue information to JSON file

        Args:
            issue_iid: GitLab issue IID
            issue_code: 이슈코드 (e.g., VTM-1372 or 1372)
            branch_name: Branch name
            issue_title: Issue title
            issue_description: Issue description
            labels: Issue labels
            pushed: Whether branch was pushed

        Returns:
            Path to saved JSON file, or None if issue_dir not configured
        """
        if not self.issue_dir:
            return None

        # Create directory structure: [ISSUE_DIR]/[branch-name]/
        issue_path = Path(self.issue_dir) / branch_name
        issue_path.mkdir(parents=True, exist_ok=True)

        # Prepare issue.json content
        issue_data = {
            "id": str(issue_iid),
            "issueCode": issue_code,
            "branch": branch_name,
            "title": issue_title,
            "description": issue_description,
            "labels": labels,
            "push": pushed
        }
        
        # Save to file
        json_file = issue_path / "issue.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(issue_data, f, ensure_ascii=False, indent=2)
        
        return str(json_file)

    def create_merge_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: Optional[str] = None,
        issue_iid: Optional[int] = None,
        remove_source_branch: bool = True,
        auto_generate_description: bool = True
    ) -> Dict:
        """
        Create merge request with auto-generated description from git history

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            title: MR title
            description: MR description (auto-generated from git history if None)
            issue_iid: Issue IID to link (will auto-close on merge)
            remove_source_branch: Remove source branch after merge
            auto_generate_description: Auto-generate description from commits if not provided

        Returns:
            Created merge request data
        """
        # Validate source branch name
        if not self.validate_branch_name(source_branch):
            raise ValueError(
                f"Invalid source branch name: {source_branch}\n"
                f"Branch name must follow format: [Asana#]/[GitLab#]-[summary]\n"
                f"Example: 1372/307-action-assignee-removal"
            )

        # Check current branch matches source branch
        current_branch = self.get_current_branch()
        if current_branch != source_branch:
            print(f"⚠️  Current branch ({current_branch}) differs from source branch ({source_branch})")
            print(f"   Switching to {source_branch}...")
            subprocess.run(['git', 'checkout', source_branch], check=True, capture_output=True)

        # Handle dirty working directory
        action = self.handle_dirty_working_directory_for_mr()

        if action == 'cancel':
            raise Exception("MR creation cancelled by user")

        # If action was 'move_to_temp', we're now on a clean source branch
        # If action was 'commit_current', changes are now committed
        # Either way, we can proceed with MR creation

        data = {
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'remove_source_branch': remove_source_branch
        }

        # Auto-generate description from git history if not provided
        if not description and auto_generate_description:
            print(f"\n📝 Generating MR description from git history...")
            try:
                summary = self.generate_mr_summary(source_branch, target_branch, issue_iid)
                description = summary
                if issue_iid:
                    print(f"✅ Generated description with issue #{issue_iid} requirements")
                else:
                    print(f"✅ Generated description from {source_branch} commits")
            except Exception as e:
                print(f"⚠️  Could not generate description: {e}")
                description = ""

        # Build description with issue closing keyword
        full_description = description or ""
        if issue_iid:
            # Add closing keyword for auto-close
            close_text = f"\n\nCloses #{issue_iid}"
            full_description += close_text

        if full_description:
            data['description'] = full_description

        mr = self._make_request(
            f"projects/{quote_plus(self.project_id)}/merge_requests",
            method='POST',
            data=data
        )
        return mr

    def get_remote_name(self) -> str:
        """
        Get the primary git remote name

        Returns:
            Remote name (e.g., 'origin', 'gitlab')
        """
        # If remote name is configured, use it
        if self.remote_name:
            return self.remote_name

        try:
            # Get all remotes
            result = subprocess.run(
                ['git', 'remote'],
                check=True,
                capture_output=True,
                text=True
            )
            remotes = result.stdout.strip().split('\n')

            # Prefer 'origin' if exists, otherwise use first remote
            if 'origin' in remotes:
                return 'origin'
            elif remotes:
                return remotes[0]
            else:
                raise Exception("No git remote found")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get git remote: {e}")

    def get_current_branch(self) -> str:
        """Get current Git branch name"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get current branch: {e}")

    def get_branch_commits(self, branch_name: str, base_branch: str = 'main') -> List[Dict]:
        """Get commit history for a branch compared to remote base branch"""
        try:
            # Use remote base branch to ensure we only get commits from current branch work
            remote = self.get_remote_name()
            remote_base = f'{remote}/{base_branch}'

            # Fetch latest to ensure we have up-to-date remote refs
            try:
                subprocess.run(['git', 'fetch', remote, base_branch],
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                # If fetch fails, continue with local comparison
                pass

            result = subprocess.run(
                ['git', 'log', f'{remote_base}..{branch_name}', '--format=%H%n%s%n%b%n%an%n%ae%n%ad%n---COMMIT---'],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            commit_texts = result.stdout.strip().split('---COMMIT---')
            
            for commit_text in commit_texts:
                if not commit_text.strip():
                    continue
                    
                lines = commit_text.strip().split('\n')
                if len(lines) < 6:
                    continue

                commits.append({
                    'hash': lines[0],
                    'subject': lines[1],
                    'body': '\n'.join(lines[2:-3]).strip(),
                    'author': lines[-3],
                    'email': lines[-2],
                    'date': lines[-1]
                })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get branch commits: {e}")

    def get_branch_diff_stats(self, branch_name: str, base_branch: str = 'main') -> Dict:
        """Get diff statistics for a branch compared to remote base branch"""
        try:
            # Use remote base branch to ensure we only count current branch changes
            remote = self.get_remote_name()
            remote_base = f'{remote}/{base_branch}'

            result = subprocess.run(
                ['git', 'diff', '--shortstat', f'{remote_base}...{branch_name}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            stats = {'files_changed': 0, 'insertions': 0, 'deletions': 0}
            
            if output:
                files_match = re.search(r'(\d+) files? changed', output)
                insertions_match = re.search(r'(\d+) insertions?\(\+\)', output)
                deletions_match = re.search(r'(\d+) deletions?\(-\)', output)
                
                if files_match:
                    stats['files_changed'] = int(files_match.group(1))
                if insertions_match:
                    stats['insertions'] = int(insertions_match.group(1))
                if deletions_match:
                    stats['deletions'] = int(deletions_match.group(1))
            
            return stats
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get diff stats: {e}")

    def generate_requirements_summary(self, branch_name: str, base_branch: str = 'main') -> str:
        """Generate summary focused on requirements and changes to be made (not results)"""
        commits = self.get_branch_commits(branch_name, base_branch)
        
        summary_parts = [
            f"# 브랜치: {branch_name}\n",
            "## 📋 변경 예정 사항\n"
        ]
        
        if commits:
            # 커밋 메시지에서 요구사항과 변경 사항 추출
            for i, commit in enumerate(commits, 1):
                subject = commit['subject']
                body = commit['body']
                
                # feat:, fix:, refactor: 등의 conventional commit prefix 제거
                clean_subject = subject
                if ':' in subject:
                    parts = subject.split(':', 1)
                    if len(parts) == 2:
                        clean_subject = parts[1].strip()
                
                summary_parts.append(f"### {i}. {clean_subject}")
                
                if body:
                    # 본문이 있으면 포함
                    summary_parts.append(f"{body}\n")
                
                summary_parts.append("---\n")
        
        return '\n'.join(summary_parts)
    
    def generate_mr_summary(self, branch_name: str, base_branch: str = 'main', issue_iid: Optional[int] = None) -> str:
        """
        Generate detailed summary with statistics for MR description

        Args:
            branch_name: Source branch name
            base_branch: Base branch to compare against
            issue_iid: Issue IID to include requirements summary

        Returns:
            Formatted MR description with issue summary, requirements, and implementation
        """
        commits = self.get_branch_commits(branch_name, base_branch)
        stats = self.get_branch_diff_stats(branch_name, base_branch)

        summary_parts = []

        # Add Issue Summary section if issue_iid is provided
        if issue_iid:
            try:
                issue = self.get_issue(issue_iid)
                summary_parts.extend([
                    f"# 📋 Issue Summary\n",
                    f"**Issue**: #{issue_iid} - {issue['title']}",
                    f"**Status**: {issue.get('state', 'N/A')}",
                    f"**Labels**: {', '.join(issue.get('labels', [])) or 'None'}",
                    f"**URL**: {issue['web_url']}\n"
                ])

                # Add Requirements section from issue description
                if issue.get('description'):
                    summary_parts.extend([
                        "## 📝 Requirements (요구사항)\n",
                        issue['description'],
                        "\n"
                    ])

                # Add Implementation Summary section
                summary_parts.append("## ✅ Implementation (구현 내용)\n")
                if commits:
                    summary_parts.append("### 주요 구현 사항:\n")
                    for i, commit in enumerate(commits, 1):
                        # Extract clean commit message (remove conventional commit prefix)
                        subject = commit['subject']
                        if ':' in subject:
                            parts = subject.split(':', 1)
                            if len(parts) == 2 and parts[0].strip() in ['feat', 'fix', 'refactor', 'docs', 'style', 'test', 'chore']:
                                subject = parts[1].strip()

                        summary_parts.append(f"{i}. {subject}")
                    summary_parts.append("\n")

            except Exception as e:
                # If issue fetch fails, continue without issue info
                print(f"⚠️  Could not fetch issue #{issue_iid}: {e}")

        # Add Changes Summary section
        summary_parts.extend([
            "## 📊 Changes Summary\n",
            f"- **Files changed**: {stats['files_changed']}",
            f"- **Insertions**: +{stats['insertions']}",
            f"- **Deletions**: -{stats['deletions']}",
            f"- **Total commits**: {len(commits)}\n"
        ])

        # Add detailed Commit History section
        if commits:
            summary_parts.append("## 📜 Detailed Commit History\n")
            for i, commit in enumerate(commits, 1):
                summary_parts.append(f"### {i}. {commit['subject']}")
                summary_parts.append(f"- **Commit**: `{commit['hash'][:8]}`")
                summary_parts.append(f"- **Author**: {commit['author']}")
                summary_parts.append(f"- **Date**: {commit['date']}\n")

                if commit['body']:
                    summary_parts.append(f"{commit['body']}\n")

                summary_parts.append("---\n")

        return '\n'.join(summary_parts)

    def update_issue_from_branch(
        self,
        issue_iid: Optional[int] = None,
        branch_name: Optional[str] = None,
        base_branch: str = 'main',
        update_title: bool = False
    ) -> Dict:
        """Update GitLab issue with requirements summary from git history"""
        if not branch_name:
            branch_name = self.get_current_branch()
        
        # Extract issue IID from branch name if not provided
        if not issue_iid:
            match = re.search(r'/(\d+)', branch_name)
            if match:
                issue_iid = int(match.group(1))
                print(f"📌 Extracted issue IID from branch: #{issue_iid}")
            else:
                raise Exception(f"Cannot extract issue IID from branch name: {branch_name}")
        
        print(f"📊 Analyzing branch: {branch_name}")
        print(f"   Base branch: {base_branch}")
        
        summary = self.generate_requirements_summary(branch_name, base_branch)
        current_issue = self.get_issue(issue_iid)
        
        update_data = {'description': summary}
        
        if update_title:
            commits = self.get_branch_commits(branch_name, base_branch)
            if commits:
                # Remove conventional commit prefix
                subject = commits[0]['subject']
                if ':' in subject:
                    parts = subject.split(':', 1)
                    if len(parts) == 2:
                        subject = parts[1].strip()
                update_data['title'] = subject
        
        print(f"\n📝 Updating GitLab issue #{issue_iid}...")
        updated_issue = self.update_issue(issue_iid=issue_iid, **update_data)
        
        print(f"✅ Updated issue #{issue_iid}: {updated_issue['title']}")
        print(f"   URL: {updated_issue['web_url']}")
        
        return updated_issue

    def doctor(self) -> Dict[str, bool]:
        """
        Validate environment setup and configuration
        
        Returns:
            Dictionary with validation results for each check
        """
        print("🏥 Running GitLab Workflow Doctor...\n")
        results = {}
        all_passed = True
        
        # Check 1: Environment variables
        print("📋 Checking environment variables...")
        env_checks = {
            'GITLAB_URL': bool(self.gitlab_url),
            'GITLAB_TOKEN': bool(self.token),
            'GITLAB_PROJECT': bool(self.project_id),
        }
        
        for key, value in env_checks.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {'Set' if value else 'Missing'}")
            if not value:
                all_passed = False
        
        results['environment'] = all(env_checks.values())
        
        # Check 2: Git repository
        print("\n📦 Checking Git repository...")
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=True
            )
            print("   ✅ Git repository: Found")
            results['git_repo'] = True
        except subprocess.CalledProcessError:
            print("   ❌ Git repository: Not found (not in a git repository)")
            results['git_repo'] = False
            all_passed = False
        except FileNotFoundError:
            print("   ❌ Git command: Not found (git not installed)")
            results['git_repo'] = False
            all_passed = False
        
        # Check 3: Git remote
        print("\n🌐 Checking Git remote...")
        try:
            remote_name = self.get_remote_name()
            result = subprocess.run(
                ['git', 'remote', 'get-url', remote_name],
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = result.stdout.strip()
            print(f"   ✅ Git remote '{remote_name}': {remote_url}")
            results['git_remote'] = True
        except subprocess.CalledProcessError:
            print(f"   ❌ Git remote: Not configured")
            print(f"   💡 Run: git remote add gitlab {self.gitlab_url}/{self.project_id}.git")
            results['git_remote'] = False
            all_passed = False
        except Exception as e:
            print(f"   ❌ Git remote check failed: {str(e)}")
            results['git_remote'] = False
            all_passed = False
        
        # Check 4: GitLab API connectivity
        print("\n🔌 Checking GitLab API connectivity...")
        try:
            # Try to get project info
            project = self._make_request(f"projects/{quote_plus(self.project_id)}")
            print(f"   ✅ GitLab API: Connected")
            print(f"   ✅ Project: {project.get('name_with_namespace', 'N/A')}")
            print(f"   ✅ URL: {project.get('web_url', 'N/A')}")
            results['gitlab_api'] = True
        except Exception as e:
            print(f"   ❌ GitLab API: Connection failed")
            print(f"   💡 Error: {str(e)}")
            results['gitlab_api'] = False
            all_passed = False
        
        # Check 5: GitLab token permissions
        print("\n🔑 Checking GitLab token permissions...")
        if results.get('gitlab_api', False):
            try:
                # Try to create a test issue (dry run - we won't actually create it)
                # Just check if we can access the issues endpoint
                issues = self._make_request(
                    f"projects/{quote_plus(self.project_id)}/issues?per_page=1"
                )
                print("   ✅ Token permissions: Valid (can read issues)")
                
                # Check if token has write permissions by checking user
                user = self._make_request("user")
                print(f"   ✅ Token user: {user.get('username', 'N/A')}")
                results['gitlab_token'] = True
            except Exception as e:
                print(f"   ❌ Token permissions: Insufficient")
                print(f"   💡 Error: {str(e)}")
                print(f"   💡 Ensure token has 'api' scope")
                results['gitlab_token'] = False
                all_passed = False
        else:
            print("   ⏭️  Skipped (API not connected)")
            results['gitlab_token'] = False
            all_passed = False
        
        # Check 6: Issue directory (optional)
        print("\n📁 Checking issue directory...")
        if self.issue_dir:
            issue_dir_path = os.path.expanduser(self.issue_dir)
            if os.path.exists(issue_dir_path):
                print(f"   ✅ Issue directory: {issue_dir_path}")
                results['issue_dir'] = True
            else:
                print(f"   ⚠️  Issue directory: Not found ({issue_dir_path})")
                print(f"   💡 Will be created automatically when saving issues")
                results['issue_dir'] = False
        else:
            print("   ⚠️  Issue directory: Not configured (using default: docs/requirements)")
            results['issue_dir'] = True  # Not a failure

        # Check 7: Working directory status
        print("\n🔍 Checking working directory status...")
        if results.get('git_repo', False):
            try:
                is_clean = self.is_working_directory_clean()
                if is_clean:
                    print("   ✅ Working directory: Clean (no uncommitted changes)")
                    results['working_dir_clean'] = True
                else:
                    dirty_files = self.get_dirty_files()
                    print(f"   ⚠️  Working directory: Has uncommitted changes ({len(dirty_files)} files)")
                    print("   💡 Commit or stash changes before creating new branches:")
                    print("      git add . && git commit -m 'message'")
                    print("      or: git stash")
                    results['working_dir_clean'] = False
                    # This is just a warning, not a failure for doctor
            except Exception as e:
                print(f"   ⚠️  Could not check working directory status: {str(e)}")
                results['working_dir_clean'] = None
        else:
            print("   ⏭️  Skipped (not in git repository)")
            results['working_dir_clean'] = None

        # Summary
        print("\n" + "="*60)
        if all_passed:
            print("✅ All checks passed! GitLab workflow is ready to use.")
            print("\n💡 Try: /gitlab-workflow create")
        else:
            print("❌ Some checks failed. Please fix the issues above.")
            print("\n💡 Common fixes:")
            print("   • Set environment variables in .claude/.env.gitlab-workflow")
            print("   • Run 'git init' if not in a git repository")
            print("   • Add git remote: git remote add gitlab <url>")
            print("   • Check GitLab token has 'api' scope")
        print("="*60)
        
        return results

    def rollback(self, state: WorkflowState) -> None:
        """
        Rollback workflow to previous state based on completed steps

        Rollback order (reverse of execution):
        - Pop stash back if failed
        - Delete remote branch (if pushed)
        - Delete local branch (if created)
        - Switch back to original branch
        - Restore stash (if stashed and not yet popped)
        """
        print("\n🔄 Rolling back changes...")

        # Step 5: If stash was popped, re-stash it
        if state.has('stash_popped'):
            try:
                subprocess.run(
                    ['git', 'stash', 'push', '-m', 'Rollback: re-stashing changes'],
                    check=True,
                    capture_output=True
                )
                print("   ✅ Re-stashed changes")
            except subprocess.CalledProcessError:
                print("   ⚠️  Could not re-stash changes (may have conflicts)")
                print("      Your changes may be in working directory")

        # Step 4: Delete remote branch if pushed
        if state.has('pushed') and state.branch_name:
            try:
                remote_name = self.get_remote_name()
                subprocess.run(
                    ['git', 'push', remote_name, '--delete', state.branch_name],
                    check=True,
                    capture_output=True
                )
                print(f"   ✅ Deleted remote branch: {remote_name}/{state.branch_name}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  Could not delete remote branch (may not exist)")

        # Step 3: Delete local branch if created
        if state.has('branch_created') and state.branch_name:
            try:
                # Switch away from the branch first
                current_branch = self.get_current_branch()
                if current_branch == state.branch_name:
                    switch_to = state.original_branch or 'main'
                    subprocess.run(
                        ['git', 'checkout', switch_to],
                        check=True,
                        capture_output=True
                    )

                subprocess.run(
                    ['git', 'branch', '-D', state.branch_name],
                    check=True,
                    capture_output=True
                )
                print(f"   ✅ Deleted local branch: {state.branch_name}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  Could not delete local branch")

        # Step 2: Switch back to original branch
        if state.has('switched_to_base') and state.original_branch:
            try:
                current_branch = self.get_current_branch()
                if current_branch != state.original_branch:
                    subprocess.run(
                        ['git', 'checkout', state.original_branch],
                        check=True,
                        capture_output=True
                    )
                    print(f"   ✅ Switched back to: {state.original_branch}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  Could not switch back to original branch")

        # Step 1: Pop stash if it was stashed but not yet popped
        if state.has('stashed') and not state.has('stash_popped'):
            try:
                subprocess.run(['git', 'stash', 'pop'], check=True, capture_output=True)
                print("   ✅ Restored stashed changes")
            except subprocess.CalledProcessError:
                print("   ⚠️  Could not pop stash (changes may be in stash list)")
                print("      Run 'git stash list' to see stashed changes")

        print("   Rollback completed\n")

    def forced_workflow(
        self,
        json_file_path: str,
        base_branch: Optional[str] = None
    ) -> WorkflowResult:
        """
        Execute FORCED automated workflow for issue creation

        This is version 2.0 of the workflow with:
        - JSON-only input (no interactive prompts)
        - Automatic dirty state handling
        - Forced: stash → switch base → pull → create branch → push → pop stash
        - AI-powered issue update
        - Rollback on failure

        Args:
            json_file_path: Path to JSON file with issue data
            base_branch: Base branch (from .env if not provided)

        Returns:
            WorkflowResult with success status and details

        Raises:
            WorkflowError: If workflow fails after rollback
        """
        state = WorkflowState()

        try:
            # ═══════════════════════════════════════════════════════
            # STEP 0: Validation Phase
            # ═══════════════════════════════════════════════════════
            print("🔍 Phase 0: Pre-flight validation\n")

            # 0-1. Load and validate JSON
            if not os.path.exists(json_file_path):
                raise FileNotFoundError(f"JSON file not found: {json_file_path}")

            with open(json_file_path, 'r', encoding='utf-8') as f:
                issue_data = json.load(f)

            # Validate required fields
            required_fields = ['issueCode', 'title']
            for field in required_fields:
                if field not in issue_data:
                    raise ValueError(f"Required field missing in JSON: {field}")

            print(f"   ✅ Loaded JSON: {json_file_path}")
            print(f"      Issue Code: {issue_data['issueCode']}")
            print(f"      Title: {issue_data['title']}")
            state.mark('json_loaded')

            # 0-2. Use base branch from .env (forced)
            if not base_branch:
                base_branch = os.getenv('BASE_BRANCH', 'main')
            print(f"   ✅ Base branch: {base_branch} (from .env)")

            # 0-3. Validate git repository
            try:
                subprocess.run(
                    ['git', 'rev-parse', '--git-dir'],
                    check=True,
                    capture_output=True
                )
                print("   ✅ Git repository validated")
            except subprocess.CalledProcessError:
                raise WorkflowError("Not in a git repository")

            # 0-4. Validate remote
            remote_name = self.get_remote_name()
            print(f"   ✅ Remote: {remote_name}")

            # 0-5. Validate remote base branch exists
            remote_base = f"{remote_name}/{base_branch}"
            try:
                subprocess.run(
                    ['git', 'rev-parse', '--verify', remote_base],
                    check=True,
                    capture_output=True
                )
                print(f"   ✅ Remote branch exists: {remote_base}")
            except subprocess.CalledProcessError:
                raise WorkflowError(f"Remote branch not found: {remote_base}")

            print("\n✅ All pre-flight checks passed\n")

            # ═══════════════════════════════════════════════════════
            # STEP 1: Create GitLab Issue
            # ═══════════════════════════════════════════════════════
            print("📝 Phase 1: Creating GitLab issue\n")

            issue = self.create_issue(
                title=issue_data['title'],
                description=issue_data.get('description', ''),
                labels=','.join(issue_data['labels']) if issue_data.get('labels') else None
            )
            issue_iid = issue['iid']
            state.issue_iid = issue_iid
            state.mark('issue_created')

            print(f"✅ Created issue #{issue_iid}: {issue['title']}")
            print(f"   URL: {issue['web_url']}\n")

            # ═══════════════════════════════════════════════════════
            # STEP 2: Auto-handle Dirty Working Directory (FORCED)
            # ═══════════════════════════════════════════════════════
            print("🔄 Phase 2: Preparing working directory\n")

            # 2-1. Check if dirty
            is_dirty = not self.is_working_directory_clean()

            if is_dirty:
                dirty_files = self.get_dirty_files()
                print(f"   ⚠️  Found {len(dirty_files)} uncommitted change(s)")
                for f in dirty_files[:5]:
                    print(f"      - {f}")
                if len(dirty_files) > 5:
                    print(f"      ... and {len(dirty_files) - 5} more")

                # 2-2. FORCED: Stash changes
                print("\n   📦 Auto-stashing changes...")
                stash_message = f"Auto-stash for issue #{issue_iid}"
                subprocess.run(
                    ['git', 'stash', 'push', '-m', stash_message],
                    check=True,
                    capture_output=True
                )
                state.stashed = True
                state.stashed_files = dirty_files
                state.mark('stashed')
                print(f"   ✅ Stashed: {stash_message}")
            else:
                print("   ✅ Working directory is clean")
                state.stashed = False

            # 2-3. FORCED: Switch to base branch
            current_branch = self.get_current_branch()
            state.original_branch = current_branch

            print(f"\n   🔀 Switching to {base_branch}...")
            subprocess.run(
                ['git', 'checkout', base_branch],
                check=True,
                capture_output=True
            )
            state.mark('switched_to_base')
            print(f"   ✅ Now on {base_branch}")

            # 2-4. FORCED: Pull latest changes
            print(f"\n   ⬇️  Pulling latest changes from {remote_name}/{base_branch}...")
            subprocess.run(
                ['git', 'pull', remote_name, base_branch],
                check=True,
                capture_output=True
            )
            state.mark('pulled_latest')
            print("   ✅ Updated to latest")

            # ═══════════════════════════════════════════════════════
            # STEP 3: Create New Branch
            # ═══════════════════════════════════════════════════════
            print("\n🌿 Phase 3: Creating new branch\n")

            # 3-1. Generate branch name
            sanitized_title = re.sub(r'[^a-zA-Z0-9\s-]', '', issue_data['title'])
            sanitized_title = re.sub(r'\s+', '-', sanitized_title.strip())
            sanitized_title = sanitized_title[:50].lower()

            if not sanitized_title or sanitized_title == '-':
                branch_name = f"{issue_data['issueCode'].lower()}/{issue_iid}"
            else:
                branch_name = f"{issue_data['issueCode'].lower()}/{issue_iid}-{sanitized_title}"

            state.branch_name = branch_name
            print(f"   Branch: {branch_name}")

            # 3-2. Create and checkout new branch
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                check=True,
                capture_output=True
            )
            state.mark('branch_created')
            print(f"   ✅ Created and checked out: {branch_name}")

            # ═══════════════════════════════════════════════════════
            # STEP 4: FORCED Push to Remote
            # ═══════════════════════════════════════════════════════
            print("\n📤 Phase 4: Pushing to remote\n")

            subprocess.run(
                ['git', 'push', '-u', remote_name, branch_name],
                check=True,
                capture_output=True
            )
            state.mark('pushed')
            print(f"   ✅ Pushed: {remote_name}/{branch_name}")

            # ═══════════════════════════════════════════════════════
            # STEP 5: FORCED Restore Stashed Changes
            # ═══════════════════════════════════════════════════════
            if state.stashed:
                print("\n📦 Phase 5: Restoring stashed changes\n")

                subprocess.run(
                    ['git', 'stash', 'pop'],
                    check=True,
                    capture_output=True
                )
                state.mark('stash_popped')
                print("   ✅ Applied stashed changes to new branch")

            # ═══════════════════════════════════════════════════════
            # STEP 6: AI Auto-Update Issue (FORCED)
            # ═══════════════════════════════════════════════════════
            print("\n🤖 Phase 6: AI analyzing and updating issue\n")

            ai_updated = False
            if state.stashed and state.stashed_files:
                print(f"   📊 Analyzing {len(state.stashed_files)} changed files...")

                # This is a placeholder - actual AI analysis would be done by Claude Code
                # For now, we'll update with a structured summary
                requirements_summary = self._generate_requirements_from_changes(
                    files=state.stashed_files,
                    original_title=issue_data['title'],
                    original_description=issue_data.get('description', '')
                )

                # Update issue with requirements summary
                updated_issue = self.update_issue(
                    issue_iid=issue_iid,
                    description=requirements_summary
                )

                print(f"   ✅ Updated issue #{issue_iid} with requirements summary")
                ai_updated = True
            else:
                print("   ⏭️  No changes to analyze, keeping original issue content")

            # ═══════════════════════════════════════════════════════
            # STEP 7: Save issue.json
            # ═══════════════════════════════════════════════════════
            print("\n💾 Phase 7: Saving metadata\n")

            json_path = self.save_issue_json(
                issue_iid=issue_iid,
                issue_code=issue_data['issueCode'],
                branch_name=branch_name,
                issue_title=issue_data['title'],
                issue_description=issue_data.get('description', ''),
                labels=issue_data.get('labels', []),
                pushed=True
            )

            if json_path:
                print(f"   ✅ Saved: {json_path}")

            # ═══════════════════════════════════════════════════════
            # SUCCESS
            # ═══════════════════════════════════════════════════════
            print("\n" + "="*60)
            print("✅ Workflow completed successfully!")
            print("="*60)
            print(f"Issue:  #{issue_iid} - {issue_data['title']}")
            print(f"Branch: {branch_name}")
            print(f"Status: Pushed to {remote_name}/{branch_name}")
            print(f"URL:    {issue['web_url']}")
            if ai_updated:
                print(f"AI:     Issue updated with requirements summary")
            print("="*60 + "\n")

            return WorkflowResult(
                success=True,
                issue_iid=issue_iid,
                issue_title=issue_data['title'],
                issue_url=issue['web_url'],
                branch_name=branch_name,
                pushed=True,
                ai_updated=ai_updated
            )

        except Exception as e:
            # ═══════════════════════════════════════════════════════
            # ROLLBACK on Failure
            # ═══════════════════════════════════════════════════════
            print(f"\n❌ Error: {e}")

            self.rollback(state)

            print("="*60)
            print("❌ Workflow failed and rolled back")
            if state.issue_iid:
                print(f"⚠️  Issue #{state.issue_iid} was created but workflow failed")
                print(f"   You may need to manually close it in GitLab")
            print("="*60 + "\n")

            return WorkflowResult(
                success=False,
                issue_iid=state.issue_iid,
                error=str(e)
            )

    def _generate_requirements_from_changes(
        self,
        files: List[str],
        original_title: str,
        original_description: str
    ) -> str:
        """
        Generate requirements summary from changed files

        This is a basic implementation. For full AI analysis,
        Claude Code would invoke its AI capabilities here.
        """
        summary_parts = [
            f"# {original_title}\n",
            f"{original_description}\n" if original_description else "",
            "## 📋 변경 예정 사항\n",
            f"다음 {len(files)}개 파일에 변경사항이 있습니다:\n"
        ]

        # Group files by directory
        file_groups = {}
        for f in files:
            dir_name = os.path.dirname(f) or '.'
            if dir_name not in file_groups:
                file_groups[dir_name] = []
            file_groups[dir_name].append(os.path.basename(f))

        for dir_name, file_list in sorted(file_groups.items()):
            summary_parts.append(f"\n### {dir_name}/")
            for file_name in sorted(file_list):
                summary_parts.append(f"- `{file_name}`")

        summary_parts.append("\n---\n")
        summary_parts.append("*이 요구사항은 변경된 파일을 기반으로 자동 생성되었습니다.*")

        return '\n'.join(summary_parts)

    def full_workflow(
        self,
        issue_title: str,
        issue_code: str,
        issue_description: Optional[str] = None,
        branch_name: Optional[str] = None,
        labels: Optional[str] = None,
        base_branch: str = 'main',
        auto_push: bool = False,
        create_branch: bool = True
    ) -> Dict:
        """
        Execute full workflow: create issue -> optionally create branch

        Args:
            issue_title: Title for the issue
            issue_code: 이슈코드 (e.g., "VTM-1372" or "1372")
            issue_description: Description for the issue
            branch_name: Custom branch name (must follow {issue-code}/{gitlab}-{summary} format)
            labels: Issue labels
            base_branch: Base branch to create from
            auto_push: Automatically push branch to remote
            create_branch: Create branch after issue (default: True)

        Returns:
            Dictionary with issue and branch information
        """
        # Step 1: Create issue
        print("📝 Creating GitLab issue...")
        issue = self.create_issue(issue_title, issue_description, labels)
        issue_iid = issue['iid']
        print(f"✅ Created issue #{issue_iid}: {issue['title']}")
        print(f"   URL: {issue['web_url']}")

        # Step 2-5: Optionally create branch
        pushed = False
        if create_branch:
            # Step 2: Handle dirty working directory
            action = self.handle_dirty_working_directory_for_issue_create()

            if action == 'cancel':
                # User cancelled, return with issue created but no branch
                print("\n⚠️  Branch creation cancelled. Issue was created successfully.")
                return {
                    'issue': {
                        'iid': issue_iid,
                        'title': issue['title'],
                        'url': issue['web_url']
                    },
                    'branch': None,
                    'pushed': False
                }

            # Step 3: Generate or validate branch name
            if not branch_name:
                # Auto-generate branch name from issue
                # Remove non-ASCII characters (including Korean) and convert to lowercase
                sanitized_title = re.sub(r'[^a-zA-Z0-9\s-]', '', issue_title)
                sanitized_title = re.sub(r'\s+', '-', sanitized_title.strip())
                sanitized_title = sanitized_title[:50].lower()  # Limit length and convert to lowercase

                # If title becomes empty after sanitization, use issue number only
                if not sanitized_title or sanitized_title == '-':
                    branch_name = f"{issue_code.lower()}/{issue_iid}"
                else:
                    branch_name = f"{issue_code.lower()}/{issue_iid}-{sanitized_title}"

            # Step 4: Create branch
            print(f"\n🌿 Creating branch: {branch_name}")
            # We already handled dirty state above, so skip the check in create_branch
            self.create_branch(branch_name, ref=base_branch, skip_dirty_check=True)

            # Step 5: If we stashed changes, pop them now
            if action == 'move_to_new':
                print(f"\n📦 Applying stashed changes to new branch...")
                self.pop_stash()

            # Step 4: Optionally push branch
            if auto_push:
                print(f"\n📤 Ready to push branch to remote: {branch_name}")
                print(f"   Remote: {self.get_remote_name()}")

                # Verify before push
                try:
                    response = input("\n🔍 Push to remote? (y/n): ").strip().lower()
                    if response in ['y', 'yes', '예']:
                        print(f"📤 Pushing branch to remote...")
                        self.push_branch(branch_name)
                        pushed = True
                    else:
                        print("⏸️  Push skipped. You can push manually later with: git push")
                except (EOFError, KeyboardInterrupt):
                    print("\n⏸️  Push cancelled. You can push manually later with: git push")
        else:
            # No branch created
            branch_name = None
            print("\n⏸️  Branch creation skipped (issue only)")

        # Step 5: Save issue.json file (only if branch was created)
        json_file = None
        if branch_name:
            json_file = self.save_issue_json(
                issue_iid=issue_iid,
                issue_code=issue_code,
                branch_name=branch_name,
                issue_title=issue_title,
                issue_description=issue_description or '',
                labels=labels.split(',') if labels else [],
                pushed=pushed
            )

            if json_file:
                print(f"\n📄 Saved issue.json: {json_file}")

        return {
            'issue': {
                'iid': issue_iid,
                'title': issue['title'],
                'url': issue['web_url']
            },
            'branch': branch_name,
            'pushed': pushed
        }


def main():
    # Load environment variables from .claude/.env.gitlab-workflow file ONLY (project-level config)
    # Get git root directory
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        git_root = result.stdout.strip()
        env_file_path = os.path.join(git_root, '.claude/.env.gitlab-workflow')

        if os.path.exists(env_file_path):
            load_env_file(env_file_path)
        # else: No warning if file doesn't exist - env vars can be set manually
    except subprocess.CalledProcessError:
        # Not in a git repository - skip loading env file
        pass

    parser = argparse.ArgumentParser(
        description='GitLab Workflow Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full workflow: create issue and branch
  %(prog)s start "Fix login bug" --issue-code VTM-1372 --description "Details here" --labels "bug"
  %(prog)s start "Add feature" --issue-code 1372 --labels "feature"

  # Create from JSON file
  %(prog)s start --from-file docs/requirements/vtm-1372/342/issue.json

  # Create branch from existing issue (이슈코드 can be any format)
  %(prog)s branch VTM-1372/305-fix-login
  %(prog)s branch 1372/305-fix-login

  # Create MR from current branch
  %(prog)s mr "Fix login bug" --issue 305

  # Push current branch
  %(prog)s push
        """
    )

    parser.add_argument('--url', help='GitLab URL (or set GITLAB_URL env var)')
    parser.add_argument('--token', help='Personal Access Token (or set GITLAB_TOKEN env var)')
    parser.add_argument('--project', help='Project ID or path (or set GITLAB_PROJECT env var)')
    parser.add_argument('--remote', help='Git remote name (or set GITLAB_REMOTE env var, default: auto-detect)')
    parser.add_argument('--issue-code', help='이슈코드 (e.g., VTM-1372 or 1372)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Start workflow (Version 2.0: FORCED workflow with JSON or interactive)
    start_parser = subparsers.add_parser('start', help='Start FORCED automated workflow')
    start_parser.add_argument('--from-file', help='JSON file with issue data')
    start_parser.add_argument('--interactive', '-i', action='store_true',
                             help='Interactive mode (prompt for input)')
    start_parser.add_argument('--base', help='Base branch (default: from BASE_BRANCH env var)')

    # Create branch only
    branch_parser = subparsers.add_parser('branch', help='Create branch (must follow {issue-code}/{gitlab} format)')
    branch_parser.add_argument('branch_name', help='Branch name (e.g., VTM-1372/305-feature)')
    branch_parser.add_argument('--base', help='Base branch (default: from BASE_BRANCH env var or "main")')
    branch_parser.add_argument('--push', action='store_true', help='Auto-push to remote')

    # Push branch
    push_parser = subparsers.add_parser('push', help='Push current branch to remote')
    push_parser.add_argument('branch_name', nargs='?', help='Branch name (optional, uses current branch)')

    # Create MR
    mr_parser = subparsers.add_parser('mr', help='Create merge request')
    mr_parser.add_argument('title', nargs='?', help='MR title (optional if using --interactive)')
    mr_parser.add_argument('--description', help='MR description')
    mr_parser.add_argument('--issue', type=int, help='Issue IID to link (auto-close)')
    mr_parser.add_argument('--source', help='Source branch (default: current branch)')
    mr_parser.add_argument('--target', default='main', help='Target branch (default: main)')
    mr_parser.add_argument('--keep-branch', action='store_true',
                          help='Keep source branch after merge')
    mr_parser.add_argument('--interactive', '-i', action='store_true',
                          help='Interactive mode (auto-detect and confirm)')

    # Init - initialize environment with interactive prompts
    init_parser = subparsers.add_parser('init', help='Initialize GitLab workflow environment with interactive setup')

    # Doctor - validate environment
    doctor_parser = subparsers.add_parser('doctor', help='Validate environment setup and configuration')

    # Help - show comprehensive usage help
    help_parser = subparsers.add_parser('help', help='Show comprehensive usage help and examples')

    # Update issue from git history
    update_parser = subparsers.add_parser('update', help='Update issue from git history')
    update_parser.add_argument('issue_iid', type=int, nargs='?', help='GitLab issue IID to update (optional, extracted from branch name)')
    update_parser.add_argument('--branch', help='Branch name (default: current branch)')
    update_parser.add_argument('--base', help='Base branch to compare (default: from BASE_BRANCH env var or "main")')
    update_parser.add_argument('--update-title', action='store_true',
                               help='Update issue title from first commit')

    args = parser.parse_args()

    # Get credentials and configuration
    gitlab_url = args.url or os.getenv('GITLAB_URL')
    token = args.token or os.getenv('GITLAB_TOKEN')
    project_id = args.project or os.getenv('GITLAB_PROJECT')
    remote_name = args.remote or os.getenv('GITLAB_REMOTE')
    # Support both new (ISSUE_CODE) and legacy (ASANA_ISSUE) env vars for backward compatibility
    issue_code = getattr(args, 'issue_code', None) or os.getenv('ISSUE_CODE') or os.getenv('ASANA_ISSUE')
    issue_dir = os.getenv('ISSUE_DIR')
    base_branch_default = os.getenv('BASE_BRANCH', 'main')

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Init command - initialize environment with interactive prompts
    if args.command == 'init':
        # Get git root to determine .env file path
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            git_root = result.stdout.strip()
            env_file_path = os.path.join(git_root, '.claude/.env.gitlab-workflow')
        except subprocess.CalledProcessError:
            print("❌ Error: Not in a git repository", file=sys.stderr)
            print("💡 Run 'git init' or cd to your git repository first", file=sys.stderr)
            sys.exit(1)

        # Run interactive initialization
        try:
            success = initialize_env_file(env_file_path)
            if success:
                print("\n🔍 Validating configuration...\n")

                # Load the newly created env file
                load_env_file(env_file_path)

                # Create workflow instance and run doctor
                workflow = GitLabWorkflow(
                    os.getenv('GITLAB_URL', ''),
                    os.getenv('GITLAB_TOKEN', ''),
                    os.getenv('GITLAB_PROJECT', ''),
                    os.getenv('GITLAB_REMOTE'),
                    os.getenv('ISSUE_DIR')
                )

                # Run doctor validation
                results = workflow.doctor()

                # Show next steps
                print("\n" + "━" * 60)
                print("✨ Setup Complete!")
                print("\nNext Steps:")
                print("  1. Try: /gitlab-doctor         # Verify setup anytime")
                print("  2. Try: /gitlab-issue-create   # Create first issue")
                print("  3. Read: plugins/gitlab-collaboration/README.md")
                print("\n💡 Tip: Your token is securely stored with 600 permissions")
                print("━" * 60)

                sys.exit(0)
            else:
                print("\n❌ Initialization failed", file=sys.stderr)
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n❌ Initialization cancelled by user", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Initialization failed: {str(e)}", file=sys.stderr)
            sys.exit(1)

    # Doctor command doesn't require credentials validation
    if args.command == 'doctor':
        workflow = GitLabWorkflow(
            gitlab_url or '',
            token or '',
            project_id or '',
            remote_name,
            issue_dir
        )
        try:
            workflow.doctor()
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Doctor failed: {str(e)}", file=sys.stderr)
            sys.exit(1)

    # Help command - show comprehensive usage help
    if args.command == 'help':
        print("""
📚 GitLab Workflow - Complete Usage Guide (Version 2.0: FORCED Workflow Edition)

═══════════════════════════════════════════════════════════════

## 🆕 Version 2.0 Changes

**FORCED Workflow** - Fully automated, zero-choice workflow:
✅ JSON-only input (no interactive prompts)
✅ Automatic dirty state handling (stash → switch → pull → branch → push → pop)
✅ AI-powered issue updates
✅ Atomic rollback on failure

═══════════════════════════════════════════════════════════════

## Available Commands

1. **init** - Initialize Environment (⭐ Run First!)
   /gitlab-init

   Interactive setup wizard:
   • Creates .claude/.env.gitlab-workflow
   • Prompts for GitLab URL, token, project
   • Sets secure file permissions (600)
   • Auto-validates configuration
   • Backs up existing configuration

2. **doctor** - Validate Environment
   /gitlab-doctor

   Checks:
   • Environment variables
   • Git repository status
   • Git remote configuration
   • GitLab API connectivity
   • Token permissions
   • Issue directory setup

3. **start** - FORCED Automated Workflow (⭐ Version 2.0)

   REQUIRED: JSON file with issue data

   gitlab_workflow.py start --from-file issue.json

   What it does (automatically, no user interaction):
   1. ✅ Validates environment and JSON
   2. ✅ Creates GitLab issue
   3. ✅ Stashes uncommitted changes (if any)
   4. ✅ Switches to base branch
   5. ✅ Pulls latest changes
   6. ✅ Creates new branch
   7. ✅ Pushes branch to remote
   8. ✅ Restores stashed changes
   9. 🤖 AI analyzes and updates issue
   10. ✅ Saves issue.json

   On failure: Automatic rollback to clean state

4. **update** - Update Issue from Git History (⭐ Auto-extracts issue #)

   Simple (auto-extracts issue number from branch):
   /gitlab-issue-update

   With specific issue:
   /gitlab-issue-update 345

   With title update:
   /gitlab-issue-update --update-title

5. **mr** - Create Merge Request (⭐ Auto-generates description with issue requirements)

   Interactive:
   /gitlab-mr

   Auto-generated MR description includes:
   • Issue summary (title, status, labels)
   • Requirements from issue description
   • Implementation summary from commits
   • Change statistics and detailed commit history

   CLI:
   gitlab_workflow.py mr "Fix bug" --issue 345 --target main

6. **help** - Show This Help
   gitlab_workflow.py help

═══════════════════════════════════════════════════════════════

## Complete Workflow Example

# Step 0: Initialize (first time only)
/gitlab-init

# Step 1: Validate setup
/gitlab-doctor

# Step 2: Create issue and branch
/gitlab-issue-create
# Answer questions:
# - 이슈코드: VTM-1372
# - Title: Add logout button
# - Description: (optional)
# - Labels: feature
# - Auto-push: yes

# Step 3: Make changes
git add .
git commit -m "VTM-1372 feat: implement logout button"
git push

# Step 4: Update issue with requirements
/gitlab-issue-update
# → Auto-extracts issue #342 from branch "vtm-1372/342-add-logout-button"
# → Updates issue description with requirements summary

# Step 5: Create merge request
/gitlab-mr
# Answer questions:
# - MR title: Add logout button
# - Link to issue: 342
# - Target branch: main

═══════════════════════════════════════════════════════════════

## JSON File Format

Create: docs/requirements/vtm-1372/342/issue.json

```json
{
  "issueCode": "VTM-1372",
  "title": "Add logout button",
  "description": "Add logout functionality to nav bar",
  "labels": ["feature", "ui"],
  "push": true
}
```

Then:
/gitlab-issue-create --from-file docs/requirements/vtm-1372/342/issue.json

═══════════════════════════════════════════════════════════════

## Key Features

✨ **Interactive Setup**
   /gitlab-init provides step-by-step wizard for environment setup
   Validates input and sets secure file permissions automatically

✨ **Auto-Extract Issue Number**
   /gitlab-issue-update automatically finds issue # from branch name
   Branch: vtm-1372/345-feature → Issue #345 (no manual input!)

✨ **Auto-Generate MR Description with Issue Requirements**
   /gitlab-mr creates comprehensive description with:
   • Issue summary (title, status, labels, URL)
   • Requirements from issue description (요구사항)
   • Implementation summary from commits (구현 내용)
   • Change statistics and detailed commit history
   Perfect for code reviews - shows what was requested vs. what was delivered!

✨ **Requirements vs Implementation**
   • Issue update (/gitlab-issue-update): Requirements (what to do)
   • MR creation (/gitlab-mr): Implementation (what was done) + Requirements mapping

✨ **Auto-Save issue.json**
   When creating issues, automatically saves to:
   docs/requirements/{issue-code}/{gitlab}/issue.json

═══════════════════════════════════════════════════════════════

## Branch Name Format

✅ Valid:
   VTM-1372/342-add-feature
   1372/342-fix-bug
   VTM-999/307-refactor

❌ Invalid:
   342-feature (missing 이슈코드)
   VTM-1372-342 (wrong separator)
   feature-name (missing numbers)

Format: {issue-code}/{gitlab#}-{summary}

═══════════════================================================================

## Environment Configuration

File: .claude/.env.gitlab-workflow

```bash
# Required
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe

# Optional
GITLAB_REMOTE=gitlab
ISSUE_DIR=docs/requirements
BASE_BRANCH=main              # or: develop, origin/main, gitlab/develop
```

Note: BASE_BRANCH can be:
  - Branch name only: main, develop (uses default remote)
  - With remote: origin/main, gitlab/develop (explicit remote)
  - Always fetches from remote to ensure latest code
```

Get token:
1. GitLab → User Settings → Access Tokens
2. Create token with 'api' scope
3. Copy to .env.gitlab-workflow

═══════════════════════════════════════════════════════════════

## Troubleshooting

Problem: "GITLAB_URL required"
Solution: Create .claude/.env.gitlab-workflow with required vars

Problem: "Invalid branch name"
Solution: Use format {issue-code}/{gitlab#}-{summary}

Problem: "No git remote found"
Solution: git remote add gitlab http://your-gitlab-server.com/project.git

Problem: "Connection failed"
Solution: Run /gitlab-workflow doctor for detailed diagnosis

═══════════════════════════════════════════════════════════════

## Documentation

• Full documentation: .claude/skills/gitlab-workflow/SKILL.md
• JSON guide: .claude/skills/gitlab-workflow/README.md
• AI guide: .claude/skills/gitlab-workflow/AI_GUIDE.md
• Quick reference: .claude/skills/gitlab-workflow/QUICK_REFERENCE.md
• Update guide: .claude/skills/gitlab-workflow/UPDATE_SUMMARY.md
• Doctor guide: .claude/skills/gitlab-workflow/DOCTOR_GUIDE.md

═══════════════════════════════════════════════════════════════

For detailed help on specific commands, run:
  gitlab_workflow.py <command> --help

Example:
  gitlab_workflow.py start --help
  gitlab_workflow.py update --help
  gitlab_workflow.py mr --help

═══════════════════════════════════════════════════════════════
        """)
        sys.exit(0)

    # Validate required credentials for other commands
    if not gitlab_url:
        print("Error: GitLab URL required (--url or GITLAB_URL env var)", file=sys.stderr)
        sys.exit(1)

    if not token:
        print("Error: Personal Access Token required (--token or GITLAB_TOKEN env var)", file=sys.stderr)
        sys.exit(1)

    if not project_id:
        print("Error: Project ID required (--project or GITLAB_PROJECT env var)", file=sys.stderr)
        sys.exit(1)

    # Check issue code for start command
    if args.command == 'start' and not issue_code:
        print("Error: 이슈코드 required for start command (--issue-code or ISSUE_CODE env var)", file=sys.stderr)
        sys.exit(1)

    # Initialize workflow
    workflow = GitLabWorkflow(gitlab_url, token, project_id, remote_name, issue_dir)

    try:
        if args.command == 'start':
            # Version 2.0: FORCED workflow with JSON or interactive input
            json_file = args.from_file

            # If interactive mode, run interactive script to generate JSON
            if args.interactive:
                print("🔄 Launching interactive mode...\n")
                json_file = run_interactive_script('interactive_issue_create.py')

                if not json_file:
                    print("Error: Interactive mode failed to generate JSON", file=sys.stderr)
                    sys.exit(1)

            # Require either --from-file or --interactive
            if not json_file:
                print("Error: Either --from-file or --interactive is required for start command", file=sys.stderr)
                print("Examples:", file=sys.stderr)
                print("  gitlab_workflow.py start --from-file issue.json", file=sys.stderr)
                print("  gitlab_workflow.py start --interactive", file=sys.stderr)
                sys.exit(1)

            # Execute forced workflow with JSON file
            print(f"\n🚀 Starting forced workflow with: {json_file}\n")
            result = workflow.forced_workflow(
                json_file_path=json_file,
                base_branch=args.base or base_branch_default
            )

            if not result.success:
                print(f"\n❌ Workflow failed: {result.error}", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'branch':
            workflow.create_branch(args.branch_name, ref=args.base or base_branch_default)
            if args.push:
                workflow.push_branch(args.branch_name)

        elif args.command == 'push':
            branch_name = args.branch_name or workflow.get_current_branch()
            workflow.push_branch(branch_name)

        elif args.command == 'mr':
            # Handle interactive mode
            if args.interactive:
                print("🔄 Launching interactive mode...\n")
                json_file = run_interactive_script('interactive_mr_create.py')

                if not json_file:
                    print("Error: Interactive mode failed to generate JSON", file=sys.stderr)
                    sys.exit(1)

                # Load JSON and extract values
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        mr_data = json.load(f)

                    # Override args with JSON data
                    args.title = mr_data['title']
                    args.target = mr_data.get('targetBranch', args.target)
                    args.issue = mr_data.get('issueIID', args.issue)

                    print(f"✅ Loaded MR details from: {json_file}\n")

                except Exception as e:
                    print(f"Error: Failed to load JSON: {e}", file=sys.stderr)
                    sys.exit(1)

            # Validate title
            if not args.title:
                print("Error: MR title is required", file=sys.stderr)
                print("Use: gitlab_workflow.py mr --interactive", file=sys.stderr)
                print("Or:  gitlab_workflow.py mr 'MR Title'", file=sys.stderr)
                sys.exit(1)

            # Create MR
            source_branch = args.source or workflow.get_current_branch()
            mr = workflow.create_merge_request(
                source_branch,
                args.target,
                args.title,
                description=args.description,
                issue_iid=args.issue,
                remove_source_branch=not args.keep_branch
            )
            print(f"✅ Created merge request !{mr['iid']}: {mr['title']}")
            print(f"   Source: {mr['source_branch']} → Target: {mr['target_branch']}")
            print(f"   URL: {mr['web_url']}")
            if args.issue:
                print(f"   Linked to issue #{args.issue} (will auto-close on merge)")

        elif args.command == 'update':
            # Update issue from git history
            result = workflow.update_issue_from_branch(
                issue_iid=args.issue_iid,
                branch_name=args.branch,
                base_branch=args.base or base_branch_default,
                update_title=args.update_title
            )

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
