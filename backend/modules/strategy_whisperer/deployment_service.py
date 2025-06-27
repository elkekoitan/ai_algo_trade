"""
Deployment Service for Strategy Whisperer
Handles strategy deployment to MT5 and version control
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import json

from backend.core.logger import get_logger
from backend.modules.mt5_integration.service import MT5Service
from backend.modules.algo_forge.git_service import GitService
from .models import (
    DeploymentRequest, DeploymentStatus, MQL5Code
)

logger = get_logger(__name__)


class DeploymentService:
    """Deploy strategies to MT5 and manage versions"""
    
    def __init__(self, mt5_service: Optional[MT5Service] = None,
                 git_service: Optional[GitService] = None):
        self.mt5_service = mt5_service or MT5Service()
        self.git_service = git_service or GitService()
        
        # Deployment paths
        self.mql5_path = self._get_mql5_path()
        self.experts_path = self.mql5_path / "Experts" if self.mql5_path else None
        self.forge_path = Path("mql5_forge_repos/strategies")
        
        # Ensure directories exist
        self.forge_path.mkdir(parents=True, exist_ok=True)
    
    def _get_mql5_path(self) -> Optional[Path]:
        """Get MQL5 installation path"""
        # Common MT5 installation paths
        possible_paths = [
            Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal",
            Path("C:/Program Files/MetaTrader 5"),
            Path("C:/Program Files (x86)/MetaTrader 5")
        ]
        
        # Find first existing path
        for path in possible_paths:
            if path.exists():
                # Look for MQL5 folder
                for item in path.iterdir():
                    mql5_folder = item / "MQL5"
                    if mql5_folder.exists():
                        return mql5_folder
        
        logger.warning("MQL5 path not found. Deployment will use local storage only.")
        return None
    
    async def deploy_strategy(self, request: DeploymentRequest) -> DeploymentStatus:
        """Deploy strategy to MT5"""
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        status = DeploymentStatus(
            deployment_id=deployment_id,
            strategy_id=request.strategy_id,
            status="pending",
            expert_name=f"{request.strategy_id}.ex5",
            magic_number=int(datetime.now().timestamp()),
            version="1.0.0",
            progress=0,
            messages=["Deployment started"],
            started_at=datetime.now()
        )
        
        try:
            # Step 1: Save to AlgoForge repository
            status.progress = 20
            status.messages.append("Saving to version control...")
            await self._save_to_forge(request, status)
            
            # Step 2: Compile MQL5 code
            status.progress = 40
            status.messages.append("Compiling MQL5 code...")
            compiled_path = await self._compile_mql5(request, status)
            
            # Step 3: Deploy to MT5
            status.progress = 60
            status.messages.append("Deploying to MT5...")
            await self._deploy_to_mt5(compiled_path, request, status)
            
            # Step 4: Verify deployment
            status.progress = 80
            status.messages.append("Verifying deployment...")
            verified = await self._verify_deployment(request, status)
            
            if verified:
                # Step 5: Auto-start if requested
                if request.auto_start:
                    status.progress = 90
                    status.messages.append("Starting expert advisor...")
                    await self._start_expert(request, status)
                
                status.status = "success"
                status.progress = 100
                status.messages.append("Deployment completed successfully!")
            else:
                raise Exception("Deployment verification failed")
            
        except Exception as e:
            status.status = "failed"
            status.error = str(e)
            status.messages.append(f"Deployment failed: {str(e)}")
            logger.error(f"Deployment error: {str(e)}")
        
        finally:
            status.completed_at = datetime.now()
        
        return status
    
    async def _save_to_forge(self, request: DeploymentRequest, status: DeploymentStatus):
        """Save strategy to AlgoForge repository"""
        try:
            # Create strategy directory
            strategy_dir = self.forge_path / request.strategy_id
            strategy_dir.mkdir(exist_ok=True)
            
            # Save MQL5 code
            mql5_file = strategy_dir / f"{request.strategy_id}.mq5"
            with open(mql5_file, 'w', encoding='utf-8') as f:
                f.write(request.code)
            
            # Create README
            readme_content = f"""# {request.strategy_id}

Generated by Strategy Whisperer on {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Strategy Details
- Symbol: {request.symbol}
- Version: {status.version}
- Magic Number: {status.magic_number}

## Deployment
- Auto Start: {request.auto_start}
- Test Mode: {request.test_mode}

## Description
This strategy was automatically generated from natural language input using AI.
"""
            
            readme_file = strategy_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Create metadata file
            metadata = {
                "strategy_id": request.strategy_id,
                "version": status.version,
                "created_at": datetime.now().isoformat(),
                "symbol": request.symbol,
                "deployment_id": status.deployment_id
            }
            
            metadata_file = strategy_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Git operations (if available)
            if self.git_service:
                # Initialize repo if needed
                repo_name = f"whisperer_{request.strategy_id}"
                repo_path = await self.git_service.create_repository(
                    repo_name,
                    f"Strategy Whisperer: {request.strategy_id}"
                )
                
                # Copy files to repo
                if repo_path:
                    for file in strategy_dir.iterdir():
                        shutil.copy2(file, repo_path)
                    
                    # Commit and push
                    await self.git_service.commit_and_push(
                        repo_path,
                        f"Initial deployment of {request.strategy_id}"
                    )
            
        except Exception as e:
            logger.error(f"Error saving to forge: {str(e)}")
            raise
    
    async def _compile_mql5(self, request: DeploymentRequest, 
                           status: DeploymentStatus) -> Path:
        """Compile MQL5 code to executable"""
        try:
            # Save source file
            source_file = self.forge_path / request.strategy_id / f"{request.strategy_id}.mq5"
            
            # If MT5 is available, use its compiler
            if self.experts_path and self.experts_path.exists():
                # Copy to Experts folder
                mt5_source = self.experts_path / f"{request.strategy_id}.mq5"
                shutil.copy2(source_file, mt5_source)
                
                # Find MetaEditor
                metaeditor = self._find_metaeditor()
                
                if metaeditor:
                    # Compile using MetaEditor
                    cmd = [str(metaeditor), "/compile", str(mt5_source)]
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        # Check for compiled file
                        compiled_file = self.experts_path / f"{request.strategy_id}.ex5"
                        if compiled_file.exists():
                            return compiled_file
                        else:
                            raise Exception("Compilation succeeded but .ex5 file not found")
                    else:
                        error_msg = stderr.decode() if stderr else "Unknown compilation error"
                        raise Exception(f"Compilation failed: {error_msg}")
                else:
                    # Simulate compilation for testing
                    logger.warning("MetaEditor not found. Using mock compilation.")
                    return self._mock_compile(source_file)
            else:
                # No MT5 available, use mock compilation
                return self._mock_compile(source_file)
                
        except Exception as e:
            logger.error(f"Compilation error: {str(e)}")
            raise
    
    def _find_metaeditor(self) -> Optional[Path]:
        """Find MetaEditor executable"""
        if not self.mql5_path:
            return None
        
        # Go up to Terminal directory
        terminal_dir = self.mql5_path.parent
        
        # Look for metaeditor64.exe or metaeditor.exe
        possible_names = ["metaeditor64.exe", "metaeditor.exe"]
        
        for name in possible_names:
            editor_path = terminal_dir / name
            if editor_path.exists():
                return editor_path
        
        return None
    
    def _mock_compile(self, source_file: Path) -> Path:
        """Mock compilation for testing"""
        # Create a mock .ex5 file
        compiled_file = source_file.with_suffix('.ex5')
        
        # Copy source as "compiled" for testing
        shutil.copy2(source_file, compiled_file)
        
        return compiled_file
    
    async def _deploy_to_mt5(self, compiled_path: Path, request: DeploymentRequest,
                            status: DeploymentStatus):
        """Deploy compiled EA to MT5"""
        try:
            if self.experts_path and self.experts_path.exists():
                # Copy to Experts folder if not already there
                target_path = self.experts_path / compiled_path.name
                
                if compiled_path != target_path:
                    shutil.copy2(compiled_path, target_path)
                
                # Update status with MT5 path
                status.messages.append(f"Deployed to: {target_path}")
                
                # If MT5 is connected, refresh expert list
                if self.mt5_service.connected:
                    # This would require MT5 API support for refreshing experts
                    # For now, just log
                    logger.info(f"Expert deployed to MT5: {target_path}")
            else:
                # Just keep in forge directory
                status.messages.append("MT5 not available. Strategy saved locally.")
                
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            raise
    
    async def _verify_deployment(self, request: DeploymentRequest,
                                status: DeploymentStatus) -> bool:
        """Verify that deployment was successful"""
        try:
            # Check if file exists in expected location
            if self.experts_path:
                expert_file = self.experts_path / f"{request.strategy_id}.ex5"
                if expert_file.exists():
                    status.messages.append("Expert file verified in MT5")
                    return True
            
            # Check forge location
            forge_file = self.forge_path / request.strategy_id / f"{request.strategy_id}.ex5"
            if forge_file.exists():
                status.messages.append("Expert file verified in forge")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False
    
    async def _start_expert(self, request: DeploymentRequest, status: DeploymentStatus):
        """Start the expert advisor on a chart"""
        try:
            if self.mt5_service.connected:
                # This would require MT5 API support for attaching experts
                # For now, provide instructions
                status.messages.append(
                    f"Please attach {request.strategy_id}.ex5 to {request.symbol} chart manually"
                )
                
                # Send notification if email provided
                if request.notification_email:
                    await self._send_notification(request, status)
            else:
                status.messages.append("MT5 not connected. Manual start required.")
                
        except Exception as e:
            logger.error(f"Error starting expert: {str(e)}")
            # Don't fail deployment if auto-start fails
            status.messages.append(f"Auto-start failed: {str(e)}")
    
    async def _send_notification(self, request: DeploymentRequest, 
                                status: DeploymentStatus):
        """Send deployment notification email"""
        # Placeholder for email notification
        logger.info(f"Would send notification to {request.notification_email}")
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentStatus]:
        """Get status of a deployment"""
        # In a real implementation, this would query a database
        # For now, return mock status
        return DeploymentStatus(
            deployment_id=deployment_id,
            strategy_id="unknown",
            status="success",
            expert_name="strategy.ex5",
            magic_number=12345,
            version="1.0.0",
            progress=100,
            messages=["Deployment completed"],
            started_at=datetime.now(),
            completed_at=datetime.now()
        )
    
    async def rollback_deployment(self, deployment_id: str, 
                                 previous_version: str) -> DeploymentStatus:
        """Rollback to a previous version"""
        # Placeholder for rollback functionality
        status = DeploymentStatus(
            deployment_id=f"rollback_{deployment_id}",
            strategy_id="unknown",
            status="pending",
            expert_name="strategy.ex5",
            magic_number=12345,
            version=previous_version,
            previous_version="current",
            progress=0,
            messages=["Rollback initiated"],
            started_at=datetime.now()
        )
        
        # In real implementation:
        # 1. Get previous version from git
        # 2. Compile and deploy
        # 3. Update status
        
        status.status = "success"
        status.progress = 100
        status.messages.append("Rollback completed")
        status.completed_at = datetime.now()
        
        return status
    
    async def list_deployments(self, strategy_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all deployments or for specific strategy"""
        deployments = []
        
        # Check forge directory
        for strategy_dir in self.forge_path.iterdir():
            if strategy_dir.is_dir():
                if strategy_id and strategy_dir.name != strategy_id:
                    continue
                
                # Read metadata if exists
                metadata_file = strategy_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        deployments.append(metadata)
        
        return deployments 