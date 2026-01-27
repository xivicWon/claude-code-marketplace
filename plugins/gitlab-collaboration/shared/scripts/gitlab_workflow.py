#!/usr/bin/env python3
"""
GitLab Workflow Automation
Automates issue creation -> branch creation -> merge request workflow
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import quote_plus
import urllib.request
import urllib.error


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

    def create_branch(self, branch_name: str, ref: str = 'main') -> bool:
        """
        Create Git branch locally from remote reference

        Args:
            branch_name: Name of the branch to create
            ref: Reference branch to create from (default: main)
                 Can be: 'main', 'develop', 'origin/main', 'gitlab/develop'

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

        # Check if working directory is clean
        if not self.is_working_directory_clean():
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

        # Step 2-4: Optionally create branch
        pushed = False
        if create_branch:
            # Step 2: Generate or validate branch name
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

            # Step 3: Create branch
            print(f"\n🌿 Creating branch: {branch_name}")
            self.create_branch(branch_name, ref=base_branch)

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

    # Start workflow
    start_parser = subparsers.add_parser('start', help='Start full workflow (issue + optionally branch)')
    start_parser.add_argument('title', nargs='?', help='Issue title (or use --from-file)')
    start_parser.add_argument('--from-file', help='Read issue information from JSON file')
    start_parser.add_argument('--description', help='Issue description')
    start_parser.add_argument('--labels', help='Issue labels (comma-separated)')
    start_parser.add_argument('--branch', help='Custom branch name (must follow {issue-code}/{gitlab}-{summary})')
    start_parser.add_argument('--base', help='Base branch (default: from BASE_BRANCH env var or "main")')
    start_parser.add_argument('--push', action='store_true', help='Auto-push branch to remote')
    start_parser.add_argument('--no-branch', action='store_true', help='Create issue only, skip branch creation')

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
    mr_parser.add_argument('title', help='MR title')
    mr_parser.add_argument('--description', help='MR description')
    mr_parser.add_argument('--issue', type=int, help='Issue IID to link (auto-close)')
    mr_parser.add_argument('--source', help='Source branch (default: current branch)')
    mr_parser.add_argument('--target', default='main', help='Target branch (default: main)')
    mr_parser.add_argument('--keep-branch', action='store_true',
                          help='Keep source branch after merge')

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
📚 GitLab Workflow - Complete Usage Guide

═══════════════════════════════════════════════════════════════

## Available Commands

1. **doctor** - Validate Environment (⭐ Run First!)
   /gitlab-workflow doctor

   Checks:
   • Environment variables
   • Git repository status
   • Git remote configuration
   • GitLab API connectivity
   • Token permissions
   • Issue directory setup

2. **create** - Create Issue + Branch

   Interactive mode:
   /gitlab-workflow create

   From JSON file:
   /gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json

   CLI mode:
   gitlab_workflow.py start "Fix bug" --issue-code VTM-1372 --labels "bug"

3. **update** - Update Issue from Git History (⭐ Auto-extracts issue #)

   Simple (auto-extracts issue number from branch):
   /gitlab-workflow update

   With specific issue:
   /gitlab-workflow update 345

   With title update:
   /gitlab-workflow update --update-title

4. **mr** - Create Merge Request (⭐ Auto-generates description with issue requirements)

   Interactive:
   /gitlab-workflow mr

   Auto-generated MR description includes:
   • Issue summary (title, status, labels)
   • Requirements from issue description
   • Implementation summary from commits
   • Change statistics and detailed commit history

   CLI:
   gitlab_workflow.py mr "Fix bug" --issue 345 --target main

5. **help** - Show This Help
   /gitlab-workflow help

═══════════════════════════════════════════════════════════════

## Complete Workflow Example

# Step 1: Validate setup (first time)
/gitlab-workflow doctor

# Step 2: Create issue and branch
/gitlab-workflow create
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
/gitlab-workflow update
# → Auto-extracts issue #342 from branch "vtm-1372/342-add-logout-button"
# → Updates issue description with requirements summary

# Step 5: Create merge request
/gitlab-workflow mr
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
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json

═══════════════════════════════════════════════════════════════

## Key Features

✨ **Auto-Extract Issue Number**
   /gitlab-workflow update automatically finds issue # from branch name
   Branch: vtm-1372/345-feature → Issue #345 (no manual input!)

✨ **Auto-Generate MR Description with Issue Requirements**
   /gitlab-workflow mr creates comprehensive description with:
   • Issue summary (title, status, labels, URL)
   • Requirements from issue description (요구사항)
   • Implementation summary from commits (구현 내용)
   • Change statistics and detailed commit history
   Perfect for code reviews - shows what was requested vs. what was delivered!

✨ **Requirements vs Implementation**
   • Issue update (/gitlab-workflow update): Requirements (what to do)
   • MR creation (/gitlab-workflow mr): Implementation (what was done) + Requirements mapping

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
            # Load from JSON file if --from-file is provided
            if args.from_file:
                try:
                    with open(args.from_file, 'r', encoding='utf-8') as f:
                        issue_data = json.load(f)

                    # Extract data from JSON with fallbacks
                    title = issue_data.get('title', args.title)
                    # Support both new (issueCode) and legacy (asana) fields
                    issue_code = issue_data.get('issueCode') or issue_data.get('asana') or issue_code
                    description = issue_data.get('description', args.description)
                    labels = issue_data.get('labels')
                    push = issue_data.get('push', args.push)
                    # Support createBranch field in JSON (default: True)
                    create_branch_from_json = issue_data.get('createBranch', True)
                    create_branch = create_branch_from_json and not args.no_branch

                    # Handle labels (can be list or comma-separated string)
                    if isinstance(labels, list):
                        labels = ','.join(labels)
                    elif labels is None:
                        labels = args.labels

                    # Validate required fields
                    if not title:
                        print("Error: Issue title is required (in JSON file or as argument)", file=sys.stderr)
                        sys.exit(1)
                    if not issue_code:
                        print("Error: 이슈코드 is required (in JSON file or --issue-code)", file=sys.stderr)
                        sys.exit(1)

                    print(f"📄 Loaded issue data from: {args.from_file}")
                    print(f"   이슈코드: {issue_code}")
                    print(f"   Title: {title}")
                    if labels:
                        print(f"   Labels: {labels}")

                except FileNotFoundError:
                    print(f"Error: File not found: {args.from_file}", file=sys.stderr)
                    sys.exit(1)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in {args.from_file}: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Use command-line arguments
                title = args.title
                description = args.description
                labels = args.labels
                push = args.push
                # Default: create branch unless --no-branch is specified
                create_branch = not args.no_branch

                if not title:
                    print("Error: Issue title is required (provide title or use --from-file)", file=sys.stderr)
                    sys.exit(1)

            result = workflow.full_workflow(
                title,
                issue_code,
                issue_description=description,
                branch_name=args.branch,
                labels=labels,
                base_branch=args.base or base_branch_default,
                auto_push=push,
                create_branch=create_branch
            )
            print(f"\n✅ Workflow completed!")
            print(f"   Issue: #{result['issue']['iid']} - {result['issue']['title']}")
            print(f"   Branch: {result['branch']}")
            if result['pushed']:
                print(f"   Status: Pushed to remote")
            else:
                print(f"   Next: Make your changes and run 'git push' or use 'gitlab_workflow.py push'")

        elif args.command == 'branch':
            workflow.create_branch(args.branch_name, ref=args.base or base_branch_default)
            if args.push:
                workflow.push_branch(args.branch_name)

        elif args.command == 'push':
            branch_name = args.branch_name or workflow.get_current_branch()
            workflow.push_branch(branch_name)

        elif args.command == 'mr':
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
