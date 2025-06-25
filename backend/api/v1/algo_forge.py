"""
API endpoints for MQL5 Algo Forge integration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from backend.modules.algo_forge import (
    GitService, 
    ForgeRepository, 
    GitOperationResult,
    GitOperationStatus,
    RepoType
)

router = APIRouter(prefix="/algo-forge", tags=["algo-forge"])

# Dependency to get GitService
async def get_git_service() -> GitService:
    """Get GitService instance."""
    return GitService()


# Request and response models
class RepositoryCreate(BaseModel):
    """Repository creation request."""
    name: str = Field(..., description="Repository name")
    type: RepoType = Field(RepoType.EXPERT, description="Repository type")
    description: Optional[str] = Field(None, description="Repository description")


class RepositoryClone(BaseModel):
    """Repository clone request."""
    url: str = Field(..., description="Repository URL")
    name: Optional[str] = Field(None, description="Repository name (optional)")
    type: RepoType = Field(RepoType.EXPERT, description="Repository type")


class CommitRequest(BaseModel):
    """Commit request."""
    message: str = Field(..., description="Commit message")
    files: Optional[List[str]] = Field(None, description="Files to commit (optional)")


class PushPullRequest(BaseModel):
    """Push/pull request."""
    remote: str = Field("origin", description="Remote name")
    branch: Optional[str] = Field(None, description="Branch name (optional)")


class BranchRequest(BaseModel):
    """Branch request."""
    name: str = Field(..., description="Branch name")


# API endpoints
@router.get("/repositories", response_model=List[ForgeRepository])
async def list_repositories(
    git_service: GitService = Depends(get_git_service)
) -> List[ForgeRepository]:
    """
    List all repositories in the MQL5 Algo Forge directory.
    """
    return await git_service.list_repositories()


@router.get("/repositories/{name}", response_model=ForgeRepository)
async def get_repository(
    name: str = Path(..., description="Repository name"),
    git_service: GitService = Depends(get_git_service)
) -> ForgeRepository:
    """
    Get information about a specific repository.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
    return repo


@router.post("/repositories", response_model=GitOperationResult)
async def create_repository(
    repo: RepositoryCreate,
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Create a new repository.
    """
    result = await git_service.create_repository(
        name=repo.name,
        repo_type=repo.type,
        description=repo.description
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.post("/repositories/clone", response_model=GitOperationResult)
async def clone_repository(
    repo: RepositoryClone,
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Clone a repository from URL.
    """
    result = await git_service.clone_repository(
        url=repo.url,
        name=repo.name,
        repo_type=repo.type
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.delete("/repositories/{name}", response_model=GitOperationResult)
async def delete_repository(
    name: str = Path(..., description="Repository name"),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Delete a repository.
    """
    result = await git_service.delete_repository(name)
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.get("/repositories/{name}/commits")
async def get_commit_history(
    name: str = Path(..., description="Repository name"),
    branch: Optional[str] = Query(None, description="Branch name (optional)"),
    max_count: int = Query(50, description="Maximum number of commits to retrieve"),
    git_service: GitService = Depends(get_git_service)
):
    """
    Get commit history for a repository.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    commits = await git_service.get_commit_history(name, branch, max_count)
    return commits


@router.get("/repositories/{name}/files/{file_path:path}")
async def get_file_content(
    name: str = Path(..., description="Repository name"),
    file_path: str = Path(..., description="Path to file within repository"),
    branch: Optional[str] = Query(None, description="Branch name (optional)"),
    git_service: GitService = Depends(get_git_service)
):
    """
    Get file content from a repository.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    content = await git_service.get_file_content(name, file_path, branch)
    if content is None:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
    return {"content": content}


@router.post("/repositories/{name}/commit", response_model=GitOperationResult)
async def commit_changes(
    name: str = Path(..., description="Repository name"),
    commit: CommitRequest = Body(...),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Commit changes to a repository.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    result = await git_service.commit_changes(
        name=name,
        message=commit.message,
        files=commit.files
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.post("/repositories/{name}/push", response_model=GitOperationResult)
async def push_changes(
    name: str = Path(..., description="Repository name"),
    push: PushPullRequest = Body(...),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Push changes to remote.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    result = await git_service.push_changes(
        name=name,
        remote=push.remote,
        branch=push.branch
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.post("/repositories/{name}/pull", response_model=GitOperationResult)
async def pull_changes(
    name: str = Path(..., description="Repository name"),
    pull: PushPullRequest = Body(...),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Pull changes from remote.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    result = await git_service.pull_changes(
        name=name,
        remote=pull.remote,
        branch=pull.branch
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.post("/repositories/{name}/branches", response_model=GitOperationResult)
async def create_branch(
    name: str = Path(..., description="Repository name"),
    branch: BranchRequest = Body(...),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Create a new branch.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    result = await git_service.create_branch(
        name=name,
        branch_name=branch.name
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result


@router.post("/repositories/{name}/branches/{branch_name}/checkout", response_model=GitOperationResult)
async def checkout_branch(
    name: str = Path(..., description="Repository name"),
    branch_name: str = Path(..., description="Branch name"),
    git_service: GitService = Depends(get_git_service)
) -> GitOperationResult:
    """
    Checkout a branch.
    """
    repo = await git_service.get_repository(name)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {name} not found")
        
    result = await git_service.checkout_branch(
        name=name,
        branch_name=branch_name
    )
    
    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.message)
        
    return result 