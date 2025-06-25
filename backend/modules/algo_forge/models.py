"""
Data models for MQL5 Algo Forge integration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RepoType(str, Enum):
    """Repository types in MQL5 Algo Forge."""
    EXPERT = "expert"
    INDICATOR = "indicator"
    SCRIPT = "script"
    LIBRARY = "library"
    INCLUDE = "include"
    RESOURCE = "resource"
    

class GitOperationStatus(str, Enum):
    """Git operation status."""
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"
    UNAUTHORIZED = "unauthorized"
    NETWORK_ERROR = "network_error"


@dataclass
class CommitInfo:
    """Git commit information."""
    hash: str
    message: str
    author: str
    email: str
    date: datetime
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class BranchInfo:
    """Git branch information."""
    name: str
    is_current: bool
    remote_name: Optional[str] = None
    last_commit: Optional[CommitInfo] = None
    ahead_count: int = 0
    behind_count: int = 0


@dataclass
class ForgeRepository:
    """MQL5 Algo Forge repository information."""
    name: str
    path: str
    type: RepoType
    description: Optional[str] = None
    branches: List[BranchInfo] = field(default_factory=list)
    current_branch: Optional[str] = None
    last_commit: Optional[CommitInfo] = None
    is_dirty: bool = False
    remote_url: Optional[str] = None
    
    @property
    def has_remote(self) -> bool:
        """Check if repository has a remote."""
        return self.remote_url is not None


@dataclass
class GitOperationResult:
    """Result of a Git operation."""
    status: GitOperationStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    
    @property
    def is_success(self) -> bool:
        """Check if operation was successful."""
        return self.status == GitOperationStatus.SUCCESS
