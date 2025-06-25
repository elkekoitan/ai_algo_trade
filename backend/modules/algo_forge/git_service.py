"""
Git service for MQL5 Algo Forge integration.
"""

import os
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import git
from git import Repo, GitCommandError

from backend.core.logger import setup_logger
from backend.core.config.settings import settings
from backend.core.events import event_bus, Event, EventTypes
from .models import (
    ForgeRepository, 
    CommitInfo, 
    BranchInfo,
    GitOperationStatus,
    GitOperationResult,
    RepoType
)

logger = setup_logger("algo_forge_git")


class GitService:
    """
    Service for handling Git operations for MQL5 Algo Forge repositories.
    """
    
    def __init__(self):
        self.base_path = Path(settings.FORGE_REPOS_PATH)
        self.base_path.mkdir(exist_ok=True, parents=True)
        
    async def list_repositories(self) -> List[ForgeRepository]:
        """
        List all repositories in the MQL5 Algo Forge directory.
        
        Returns:
            List of ForgeRepository objects
        """
        repos = []
        
        # Check for subdirectories that are git repositories
        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue
                
            # Check if this is a git repository
            git_dir = item / ".git"
            if not git_dir.exists():
                continue
                
            try:
                repo = await self._get_repository_info(item)
                repos.append(repo)
            except Exception as e:
                logger.error(f"Error processing repository {item}: {e}")
                
        return repos
        
    async def get_repository(self, name: str) -> Optional[ForgeRepository]:
        """
        Get information about a specific repository.
        
        Args:
            name: Repository name
            
        Returns:
            ForgeRepository object or None if not found
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return None
            
        try:
            return await self._get_repository_info(repo_path)
        except Exception as e:
            logger.error(f"Error getting repository info for {name}: {e}")
            return None
            
    async def clone_repository(
        self, 
        url: str, 
        name: Optional[str] = None,
        repo_type: RepoType = RepoType.EXPERT
    ) -> GitOperationResult:
        """
        Clone a repository from URL.
        
        Args:
            url: Repository URL
            name: Repository name (optional, will be extracted from URL if not provided)
            repo_type: Repository type
            
        Returns:
            GitOperationResult
        """
        # Extract name from URL if not provided
        if not name:
            name_match = re.search(r'/([^/]+)\.git$', url)
            if name_match:
                name = name_match.group(1)
            else:
                return GitOperationResult(
                    status=GitOperationStatus.FAILED,
                    message="Could not extract repository name from URL"
                )
                
        # Check if repository already exists
        repo_path = self.base_path / name
        if repo_path.exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} already exists"
            )
            
        # Clone repository
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: Repo.clone_from(url, repo_path)
            )
            
            # Get repository info
            repo_info = await self._get_repository_info(repo_path)
            
            # Emit repository cloned event
            await event_bus.emit_async(
                Event(EventTypes.REPO_CLONED, {
                    "name": name,
                    "url": url,
                    "path": str(repo_path)
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Repository {name} cloned successfully",
                data={"repository": repo_info}
            )
            
        except GitCommandError as e:
            logger.error(f"Git error cloning repository {url}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Git error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error cloning repository {url}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def create_repository(
        self, 
        name: str,
        repo_type: RepoType,
        description: Optional[str] = None
    ) -> GitOperationResult:
        """
        Create a new repository.
        
        Args:
            name: Repository name
            repo_type: Repository type
            description: Repository description
            
        Returns:
            GitOperationResult
        """
        # Check if repository already exists
        repo_path = self.base_path / name
        if repo_path.exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} already exists"
            )
            
        # Create repository
        try:
            # Create directory
            repo_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize git repository
            loop = asyncio.get_event_loop()
            repo = await loop.run_in_executor(
                None,
                lambda: Repo.init(repo_path)
            )
            
            # Create README.md
            readme_path = repo_path / "README.md"
            with open(readme_path, "w") as f:
                f.write(f"# {name}\n\n")
                if description:
                    f.write(f"{description}\n\n")
                f.write(f"Repository type: {repo_type.value}\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            # Add and commit README
            repo.git.add("README.md")
            repo.git.commit("-m", "Initial commit")
            
            # Get repository info
            repo_info = await self._get_repository_info(repo_path)
            
            # Emit repository created event
            await event_bus.emit_async(
                Event(EventTypes.REPO_CREATED, {
                    "name": name,
                    "type": repo_type.value,
                    "path": str(repo_path)
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Repository {name} created successfully",
                data={"repository": repo_info}
            )
            
        except Exception as e:
            logger.error(f"Error creating repository {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def delete_repository(self, name: str) -> GitOperationResult:
        """
        Delete a repository.
        
        Args:
            name: Repository name
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            # Remove directory recursively
            import shutil
            shutil.rmtree(repo_path)
            
            # Emit repository deleted event
            await event_bus.emit_async(
                Event(EventTypes.REPO_DELETED, {
                    "name": name
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Repository {name} deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Error deleting repository {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def get_commit_history(
        self, 
        name: str, 
        branch: Optional[str] = None,
        max_count: int = 50
    ) -> List[CommitInfo]:
        """
        Get commit history for a repository.
        
        Args:
            name: Repository name
            branch: Branch name (optional)
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of CommitInfo objects
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return []
            
        try:
            repo = Repo(repo_path)
            
            # Get commits
            if branch:
                commits = list(repo.iter_commits(branch, max_count=max_count))
            else:
                commits = list(repo.iter_commits(max_count=max_count))
                
            # Convert to CommitInfo objects
            commit_infos = []
            for commit in commits:
                # Get stats
                stats = commit.stats.total
                
                commit_info = CommitInfo(
                    hash=commit.hexsha,
                    message=commit.message.strip(),
                    author=commit.author.name,
                    email=commit.author.email,
                    date=datetime.fromtimestamp(commit.committed_date),
                    files_changed=stats.get('files', 0),
                    insertions=stats.get('insertions', 0),
                    deletions=stats.get('deletions', 0)
                )
                commit_infos.append(commit_info)
                
            return commit_infos
            
        except Exception as e:
            logger.error(f"Error getting commit history for {name}: {e}")
            return []
            
    async def get_file_content(
        self, 
        name: str, 
        file_path: str,
        branch: Optional[str] = None
    ) -> Optional[str]:
        """
        Get file content from a repository.
        
        Args:
            name: Repository name
            file_path: Path to file within repository
            branch: Branch name (optional)
            
        Returns:
            File content as string or None if not found
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return None
            
        try:
            repo = Repo(repo_path)
            
            # Get file content
            if branch:
                repo.git.checkout(branch)
                
            file_full_path = repo_path / file_path
            
            if not file_full_path.exists():
                return None
                
            with open(file_full_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            return content
            
        except Exception as e:
            logger.error(f"Error getting file content for {name}/{file_path}: {e}")
            return None
            
    async def commit_changes(
        self, 
        name: str, 
        message: str,
        files: Optional[List[str]] = None
    ) -> GitOperationResult:
        """
        Commit changes to a repository.
        
        Args:
            name: Repository name
            message: Commit message
            files: List of files to commit (optional, commits all changes if not provided)
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            repo = Repo(repo_path)
            
            # Add files
            if files:
                for file in files:
                    repo.git.add(file)
            else:
                repo.git.add(".")
                
            # Check if there are changes to commit
            if not repo.is_dirty() and not repo.untracked_files:
                return GitOperationResult(
                    status=GitOperationStatus.SUCCESS,
                    message="No changes to commit"
                )
                
            # Commit changes
            commit = repo.git.commit("-m", message)
            
            # Get commit info
            commits = list(repo.iter_commits(max_count=1))
            if commits:
                commit_hash = commits[0].hexsha
            else:
                commit_hash = "Unknown"
                
            # Emit commit event
            await event_bus.emit_async(
                Event(EventTypes.REPO_COMMITTED, {
                    "name": name,
                    "message": message,
                    "hash": commit_hash
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Changes committed successfully: {commit_hash}",
                data={"commit_hash": commit_hash}
            )
            
        except Exception as e:
            logger.error(f"Error committing changes to {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def push_changes(
        self, 
        name: str,
        remote: str = "origin",
        branch: Optional[str] = None
    ) -> GitOperationResult:
        """
        Push changes to remote.
        
        Args:
            name: Repository name
            remote: Remote name
            branch: Branch name (optional)
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            repo = Repo(repo_path)
            
            # Check if remote exists
            try:
                repo.remote(remote)
            except ValueError:
                return GitOperationResult(
                    status=GitOperationStatus.FAILED,
                    message=f"Remote {remote} does not exist"
                )
                
            # Push changes
            if branch:
                push_info = repo.git.push(remote, branch)
            else:
                push_info = repo.git.push(remote)
                
            # Emit push event
            await event_bus.emit_async(
                Event(EventTypes.REPO_PUSHED, {
                    "name": name,
                    "remote": remote,
                    "branch": branch or repo.active_branch.name
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message="Changes pushed successfully",
                data={"push_info": push_info}
            )
            
        except GitCommandError as e:
            logger.error(f"Git error pushing changes to {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Git error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error pushing changes to {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def pull_changes(
        self, 
        name: str,
        remote: str = "origin",
        branch: Optional[str] = None
    ) -> GitOperationResult:
        """
        Pull changes from remote.
        
        Args:
            name: Repository name
            remote: Remote name
            branch: Branch name (optional)
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            repo = Repo(repo_path)
            
            # Check if remote exists
            try:
                repo.remote(remote)
            except ValueError:
                return GitOperationResult(
                    status=GitOperationStatus.FAILED,
                    message=f"Remote {remote} does not exist"
                )
                
            # Pull changes
            if branch:
                pull_info = repo.git.pull(remote, branch)
            else:
                pull_info = repo.git.pull(remote)
                
            # Emit pull event
            await event_bus.emit_async(
                Event(EventTypes.REPO_PULLED, {
                    "name": name,
                    "remote": remote,
                    "branch": branch or repo.active_branch.name
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message="Changes pulled successfully",
                data={"pull_info": pull_info}
            )
            
        except GitCommandError as e:
            logger.error(f"Git error pulling changes for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Git error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error pulling changes for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def create_branch(
        self, 
        name: str,
        branch_name: str
    ) -> GitOperationResult:
        """
        Create a new branch.
        
        Args:
            name: Repository name
            branch_name: Branch name
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            repo = Repo(repo_path)
            
            # Create branch
            repo.git.branch(branch_name)
            
            # Emit branch created event
            await event_bus.emit_async(
                Event(EventTypes.BRANCH_CREATED, {
                    "name": name,
                    "branch": branch_name
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Branch {branch_name} created successfully"
            )
            
        except GitCommandError as e:
            logger.error(f"Git error creating branch {branch_name} for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Git error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error creating branch {branch_name} for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def checkout_branch(
        self, 
        name: str,
        branch_name: str
    ) -> GitOperationResult:
        """
        Checkout a branch.
        
        Args:
            name: Repository name
            branch_name: Branch name
            
        Returns:
            GitOperationResult
        """
        repo_path = self.base_path / name
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Repository {name} does not exist"
            )
            
        try:
            repo = Repo(repo_path)
            
            # Checkout branch
            repo.git.checkout(branch_name)
            
            # Emit branch checkout event
            await event_bus.emit_async(
                Event(EventTypes.BRANCH_CHECKED_OUT, {
                    "name": name,
                    "branch": branch_name
                })
            )
            
            return GitOperationResult(
                status=GitOperationStatus.SUCCESS,
                message=f"Checked out branch {branch_name} successfully"
            )
            
        except GitCommandError as e:
            logger.error(f"Git error checking out branch {branch_name} for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Git error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error checking out branch {branch_name} for {name}: {e}")
            return GitOperationResult(
                status=GitOperationStatus.FAILED,
                message=f"Error: {str(e)}"
            )
            
    async def _get_repository_info(self, path: Path) -> ForgeRepository:
        """
        Get detailed information about a repository.
        
        Args:
            path: Repository path
            
        Returns:
            ForgeRepository object
        """
        repo = Repo(path)
        
        # Get repository name
        name = path.name
        
        # Determine repository type
        repo_type = RepoType.EXPERT  # Default
        
        # Check if there's a README with type information
        readme_path = path / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Look for repository type
                type_match = re.search(r'Repository type: (\w+)', content)
                if type_match:
                    type_str = type_match.group(1).lower()
                    try:
                        repo_type = RepoType(type_str)
                    except ValueError:
                        pass
                        
                # Look for description
                description = None
                desc_match = re.search(r'# .+\n\n(.*?)(?=\n\n|$)', content, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()
        
        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except:
            current_branch = None
            
        # Get branches
        branches = []
        for branch in repo.branches:
            # Get last commit for branch
            try:
                commits = list(repo.iter_commits(branch.name, max_count=1))
                if commits:
                    commit = commits[0]
                    stats = commit.stats.total
                    
                    last_commit = CommitInfo(
                        hash=commit.hexsha,
                        message=commit.message.strip(),
                        author=commit.author.name,
                        email=commit.author.email,
                        date=datetime.fromtimestamp(commit.committed_date),
                        files_changed=stats.get('files', 0),
                        insertions=stats.get('insertions', 0),
                        deletions=stats.get('deletions', 0)
                    )
                else:
                    last_commit = None
            except:
                last_commit = None
                
            # Get remote tracking branch
            remote_name = None
            ahead_count = 0
            behind_count = 0
            
            try:
                tracking_branch = branch.tracking_branch()
                if tracking_branch:
                    remote_name = tracking_branch.name
                    
                    # Get ahead/behind counts
                    ahead, behind = repo.git.rev_list(
                        '--left-right', 
                        '--count', 
                        f'{branch.name}...{tracking_branch.name}'
                    ).split()
                    ahead_count = int(ahead)
                    behind_count = int(behind)
            except:
                pass
                
            branch_info = BranchInfo(
                name=branch.name,
                is_current=branch.name == current_branch,
                remote_name=remote_name,
                last_commit=last_commit,
                ahead_count=ahead_count,
                behind_count=behind_count
            )
            branches.append(branch_info)
            
        # Get last commit
        last_commit = None
        try:
            commits = list(repo.iter_commits(max_count=1))
            if commits:
                commit = commits[0]
                stats = commit.stats.total
                
                last_commit = CommitInfo(
                    hash=commit.hexsha,
                    message=commit.message.strip(),
                    author=commit.author.name,
                    email=commit.author.email,
                    date=datetime.fromtimestamp(commit.committed_date),
                    files_changed=stats.get('files', 0),
                    insertions=stats.get('insertions', 0),
                    deletions=stats.get('deletions', 0)
                )
        except:
            pass
            
        # Check if repo is dirty
        is_dirty = repo.is_dirty() or len(repo.untracked_files) > 0
        
        # Get remote URL
        remote_url = None
        try:
            if repo.remotes:
                remote_url = repo.remotes.origin.url
        except:
            pass
            
        return ForgeRepository(
            name=name,
            path=str(path),
            type=repo_type,
            description=description,
            branches=branches,
            current_branch=current_branch,
            last_commit=last_commit,
            is_dirty=is_dirty,
            remote_url=remote_url
        )
