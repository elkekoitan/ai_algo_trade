"""
Strategy Deployment Service

MT5 stratejilerinin deployment'ını ve copy trading entegrasyonunu yönetir.
"""

import os
import uuid
import shutil
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import (
    DeploymentRequest, DeploymentResponse, DeploymentInfo, DeploymentStatus,
    StrategyConfig, StrategyParameters, MT5AccountInfo, StrategyPerformance,
    CopyTradingConfig, StrategyType
)
from ..mt5_integration.service import MT5Service
from ..copy_trading.copy_service import CopyTradingService

logger = logging.getLogger(__name__)

class StrategyDeploymentService:
    """MT5 strateji deployment servisi"""
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentInfo] = {}
        self.mt5_service = MT5Service()
        self.copy_service = CopyTradingService()
        self.strategy_files_path = Path("mql5_forge_repos/strategies")
        
    async def deploy_strategy(self, request: DeploymentRequest) -> DeploymentResponse:
        """Stratejiyi belirtilen hesaplara deploy et"""
        try:
            deployment_id = str(uuid.uuid4())
            
            # Deployment bilgisi oluştur
            deployment_info = DeploymentInfo(
                deployment_id=deployment_id,
                deployment_name=request.deployment_name,
                strategy_config=request.strategy_config,
                target_accounts=request.target_accounts,
                master_account=request.master_account,
                status=DeploymentStatus.PENDING
            )
            
            self.deployments[deployment_id] = deployment_info
            
            # Async deployment başlat
            asyncio.create_task(self._execute_deployment(deployment_id, request))
            
            return DeploymentResponse(
                success=True,
                deployment_id=deployment_id,
                message="Deployment başlatıldı",
                deployment_info=deployment_info
            )
            
        except Exception as e:
            logger.error(f"Deployment başlatma hatası: {str(e)}")
            return DeploymentResponse(
                success=False,
                message=f"Deployment başlatma hatası: {str(e)}"
            )
    
    async def _execute_deployment(self, deployment_id: str, request: DeploymentRequest):
        """Deployment'ı gerçekleştir"""
        deployment = self.deployments[deployment_id]
        
        try:
            deployment.status = DeploymentStatus.DEPLOYING
            deployment.updated_at = datetime.now()
            
            # 1. Strateji dosyalarını hazırla
            strategy_files = await self._prepare_strategy_files(request.strategy_config)
            
            # 2. Her hesaba deploy et
            for account in request.target_accounts:
                await self._deploy_to_account(account, strategy_files, request.strategy_config)
            
            # 3. Copy trading ayarla (eğer isteniyorsa)
            if request.enable_copy_trading and request.master_account:
                await self._setup_copy_trading(request.master_account, request.target_accounts)
            
            # 4. Auto start (eğer isteniyorsa)
            if request.auto_start:
                await self._start_strategy_on_accounts(request.target_accounts, request.strategy_config)
            
            deployment.status = DeploymentStatus.DEPLOYED
            deployment.deployed_at = datetime.now()
            deployment.updated_at = datetime.now()
            
            logger.info(f"Deployment {deployment_id} başarıyla tamamlandı")
            
        except Exception as e:
            logger.error(f"Deployment {deployment_id} hatası: {str(e)}")
            deployment.status = DeploymentStatus.FAILED
            deployment.error_message = str(e)
            deployment.updated_at = datetime.now()
    
    async def _prepare_strategy_files(self, strategy_config: StrategyConfig) -> Dict[str, str]:
        """Strateji dosyalarını hazırla ve parametreleri güncelle"""
        files = {}
        
        if strategy_config.strategy_type == StrategyType.SANAL_SUPURGE_V1:
            # Sanal Süpürge V1 dosyalarını oku
            strategy_path = self.strategy_files_path / "sanal_supurge_v1"
            
            # Ana EA dosyası
            main_file = strategy_path / "Sanal_SupurgeV1.mq4"
            if main_file.exists():
                content = main_file.read_text(encoding='utf-8')
                # Parametreleri güncelle
                content = self._update_strategy_parameters(content, strategy_config.parameters)
                files["Sanal_SupurgeV1.mq4"] = content
            
            # Helper dosyası
            helper_file = strategy_path / "Sanal_SupurgeV1_Functions.mqh"
            if helper_file.exists():
                files["Sanal_SupurgeV1_Functions.mqh"] = helper_file.read_text(encoding='utf-8')
        
        return files
    
    def _update_strategy_parameters(self, content: str, params: StrategyParameters) -> str:
        """MQL4 dosyasındaki parametreleri güncelle"""
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            original_line = line
            
            # Temel parametreler
            if 'extern bool BuyIslemiAc=' in line:
                line = f'extern bool BuyIslemiAc={str(params.buy_islemi_ac).lower()};'
            elif 'extern bool SellIslemiAc=' in line:
                line = f'extern bool SellIslemiAc={str(params.sell_islemi_ac).lower()};'
            elif 'extern string PositionComment=' in line:
                line = f'extern string PositionComment="{params.position_comment}";'
            elif 'extern double PivotUst=' in line:
                line = f'extern double PivotUst={params.pivot_ust};'
            elif 'extern double PivotAlt=' in line:
                line = f'extern double PivotAlt={params.pivot_alt};'
            
            # Lot boyutları güncelle
            for i in range(14):
                if f'extern double LotSize{i+1}=' in line:
                    if i < len(params.lot_sizes):
                        line = f'extern double LotSize{i+1}={params.lot_sizes[i]};//{i+1}. işlem Lot'
                    break
            
            # TP seviyeleri güncelle
            for i in range(14):
                if f'extern int tp{i+1}=' in line:
                    if i < len(params.tp_levels):
                        line = f'extern int tp{i+1}={params.tp_levels[i]};//{i+1}. işlem TP'
                    break
            
            # SL seviyeleri güncelle
            for i in range(14):
                if f'extern int sl{i+1}=' in line:
                    if i < len(params.sl_levels):
                        line = f'extern int sl{i+1}={params.sl_levels[i]};//{i+1}. işlem SL'
                    break
            
            # Zaman filtreleri
            if 'extern bool UseTimeLimit=' in line:
                line = f'extern bool UseTimeLimit={str(params.use_time_limit).lower()};'
            elif 'extern int DoNotOpenAfterHour=' in line:
                line = f'extern int DoNotOpenAfterHour={params.do_not_open_after_hour};'
            elif 'extern int DoNotOpenBeforeHour=' in line:
                line = f'extern int DoNotOpenBeforeHour={params.do_not_open_before_hour};'
            
            updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    async def _deploy_to_account(self, account: MT5AccountInfo, strategy_files: Dict[str, str], strategy_config: StrategyConfig):
        """Belirli bir hesaba strateji deploy et"""
        try:
            # MT5 bağlantısı kur
            if not await self.mt5_service.connect_to_account(account.login, account.password, account.server):
                raise Exception(f"MT5 hesabına bağlanılamadı: {account.login}")
            
            # Strateji dosyalarını MT5 experts klasörüne kopyala
            experts_path = self.mt5_service.get_experts_path()
            
            for filename, content in strategy_files.items():
                file_path = experts_path / filename
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Dosya kopyalandı: {file_path}")
            
            # MT5'i yeniden başlat (dosyaları tanıması için)
            await self.mt5_service.refresh_experts()
            
            logger.info(f"Strateji {account.login} hesabına başarıyla deploy edildi")
            
        except Exception as e:
            logger.error(f"Hesap {account.login} deployment hatası: {str(e)}")
            raise
    
    async def _setup_copy_trading(self, master_account: MT5AccountInfo, slave_accounts: List[MT5AccountInfo]):
        """Copy trading sistemini kur"""
        try:
            copy_config = CopyTradingConfig(
                master_account=master_account,
                slave_accounts=slave_accounts,
                copy_ratio=1.0,
                copy_sl_tp=True,
                delay_ms=100
            )
            
            await self.copy_service.setup_copy_trading(copy_config)
            logger.info("Copy trading sistemi başarıyla kuruldu")
            
        except Exception as e:
            logger.error(f"Copy trading kurulum hatası: {str(e)}")
            raise
    
    async def _start_strategy_on_accounts(self, accounts: List[MT5AccountInfo], strategy_config: StrategyConfig):
        """Stratejileri hesaplarda başlat"""
        for account in accounts:
            try:
                # Hesaba bağlan
                await self.mt5_service.connect_to_account(account.login, account.password, account.server)
                
                # Stratejiyi başlat
                await self.mt5_service.start_expert(
                    symbol=strategy_config.symbol,
                    expert_name="Sanal_SupurgeV1" if strategy_config.strategy_type == StrategyType.SANAL_SUPURGE_V1 else strategy_config.strategy_name
                )
                
                logger.info(f"Strateji {account.login} hesabında başlatıldı")
                
            except Exception as e:
                logger.error(f"Strateji başlatma hatası - hesap {account.login}: {str(e)}")
    
    async def stop_deployment(self, deployment_id: str) -> DeploymentResponse:
        """Deployment'ı durdur"""
        if deployment_id not in self.deployments:
            return DeploymentResponse(
                success=False,
                message="Deployment bulunamadı"
            )
        
        deployment = self.deployments[deployment_id]
        
        try:
            # Tüm hesaplarda stratejiyi durdur
            for account in deployment.target_accounts:
                await self.mt5_service.connect_to_account(account.login, account.password, account.server)
                await self.mt5_service.stop_expert("Sanal_SupurgeV1")
            
            deployment.status = DeploymentStatus.STOPPED
            deployment.stopped_at = datetime.now()
            deployment.updated_at = datetime.now()
            
            return DeploymentResponse(
                success=True,
                message="Deployment durduruldu",
                deployment_info=deployment
            )
            
        except Exception as e:
            logger.error(f"Deployment durdurma hatası: {str(e)}")
            return DeploymentResponse(
                success=False,
                message=f"Deployment durdurma hatası: {str(e)}"
            )
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentInfo]:
        """Deployment bilgilerini getir"""
        return self.deployments.get(deployment_id)
    
    def list_deployments(self, page: int = 1, page_size: int = 10) -> List[DeploymentInfo]:
        """Deployment listesi"""
        deployments = list(self.deployments.values())
        start = (page - 1) * page_size
        end = start + page_size
        return deployments[start:end]
    
    async def get_deployment_performance(self, deployment_id: str) -> Dict[str, StrategyPerformance]:
        """Deployment performansını getir"""
        if deployment_id not in self.deployments:
            return {}
        
        deployment = self.deployments[deployment_id]
        performance_data = {}
        
        for account in deployment.target_accounts:
            try:
                await self.mt5_service.connect_to_account(account.login, account.password, account.server)
                
                # Performans verilerini al
                trades = await self.mt5_service.get_expert_trades("HayaletSüpürge")
                account_info = await self.mt5_service.get_account_info()
                
                # Performans hesapla
                total_trades = len(trades)
                winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
                losing_trades = total_trades - winning_trades
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                total_profit = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) > 0])
                total_loss = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) < 0])
                net_profit = total_profit + total_loss
                
                performance = StrategyPerformance(
                    deployment_id=deployment_id,
                    account_login=account.login,
                    total_trades=total_trades,
                    winning_trades=winning_trades,
                    losing_trades=losing_trades,
                    win_rate=win_rate,
                    total_profit=total_profit,
                    total_loss=abs(total_loss),
                    net_profit=net_profit,
                    open_positions=len(await self.mt5_service.get_open_positions("HayaletSüpürge"))
                )
                
                performance_data[str(account.login)] = performance
                
            except Exception as e:
                logger.error(f"Performans verisi alma hatası - hesap {account.login}: {str(e)}")
        
        return performance_data 