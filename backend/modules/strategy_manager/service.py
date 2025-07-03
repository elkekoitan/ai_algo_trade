"""
Strategy Manager Service

MQL4/5 stratejilerini yöneten ana servis.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json

from .models import (
    StrategyMetadata, StrategyType, StrategyInstance, 
    ExecutionMode, TradingSignal, StrategyParameter,
    CreateInstanceRequest, UpdateInstanceRequest,
    ManualTradeRequest, BacktestRequest, BacktestResult,
    StrategyListRequest, StrategyUploadRequest
)
from .repository import StrategyRepository
from .parser import MQLParameterParser
from .executor import StrategyExecutor
from ..mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

class StrategyManagerService:
    """Strategy Manager ana servisi"""
    
    def __init__(self, mt5_service: MT5Service):
        self.mt5_service = mt5_service
        self.repository = StrategyRepository()
        self.parser = MQLParameterParser()
        self.executor = StrategyExecutor(mt5_service)
        
        # Instance storage (DB'ye taşınacak)
        self.instances: Dict[str, StrategyInstance] = {}
        
        # Signal storage (DB'ye taşınacak)
        self.signals: Dict[str, List[TradingSignal]] = {}
        
        # Config storage (DB'ye taşınacak)
        self.saved_configs: Dict[str, Dict] = {}
    
    async def upload_strategy(self, request: StrategyUploadRequest) -> Dict[str, Any]:
        """Yeni strateji yükle"""
        try:
            # Stratejiyi kaydet
            success, result, metadata = self.repository.save_strategy(
                name=request.name,
                display_name=request.display_name,
                type=request.type,
                main_file_content=request.main_file_content,
                platform=request.platform,
                include_files=request.include_files,
                description=request.description,
                author=request.author,
                supported_symbols=request.supported_symbols,
                recommended_timeframes=request.recommended_timeframes,
                categories=request.categories,
                tags=request.tags
            )
            
            if not success:
                return {
                    'success': False,
                    'error': result
                }
            
            # Parametreleri parse et
            parameters, parse_metadata = self.parser.parse_file(request.main_file_content)
            
            return {
                'success': True,
                'strategy_id': result,
                'metadata': metadata.dict() if metadata else None,
                'parameters': [p.dict() for p in parameters],
                'parameter_groups': parse_metadata.get('groups', [])
            }
            
        except Exception as e:
            logger.error(f"Strateji yükleme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_strategies(self, request: StrategyListRequest) -> Dict[str, Any]:
        """Strateji listesi"""
        try:
            # Repository'den stratejileri al
            strategies = self.repository.list_strategies(
                type=request.type,
                platform=request.platform,
                search=request.search
            )
            
            # Filtreleme - categories ve tags
            if request.categories:
                strategies = [s for s in strategies 
                             if any(cat in s.categories for cat in request.categories)]
            
            if request.tags:
                strategies = [s for s in strategies 
                             if any(tag in s.tags for tag in request.tags)]
            
            # Pagination
            total = len(strategies)
            start = (request.page - 1) * request.page_size
            end = start + request.page_size
            
            # Sıralama
            if request.sort_by == 'name':
                strategies.sort(key=lambda x: x.name, reverse=(request.sort_order == 'desc'))
            elif request.sort_by == 'created_at':
                strategies.sort(key=lambda x: x.created_at, reverse=(request.sort_order == 'desc'))
            elif request.sort_by == 'rating':
                strategies.sort(key=lambda x: x.average_rating, reverse=(request.sort_order == 'desc'))
            
            paginated = strategies[start:end]
            
            return {
                'success': True,
                'strategies': [s.dict() for s in paginated],
                'total': total,
                'page': request.page,
                'page_size': request.page_size,
                'total_pages': (total + request.page_size - 1) // request.page_size
            }
            
        except Exception as e:
            logger.error(f"Strateji listeleme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Strateji detaylarını getir"""
        try:
            # Metadata
            metadata = self.repository.get_strategy(strategy_id)
            if not metadata:
                return {
                    'success': False,
                    'error': 'Strateji bulunamadı'
                }
            
            # Parametreler
            parameters, groups = self.repository.get_strategy_parameters(strategy_id)
            
            # Dosyalar
            files = self.repository.get_strategy_files(strategy_id)
            
            # Instance sayısı
            active_instances = sum(1 for inst in self.instances.values() 
                                 if inst.strategy_id == strategy_id and inst.is_active)
            
            return {
                'success': True,
                'metadata': metadata.dict(),
                'parameters': parameters,
                'parameter_groups': groups,
                'files': files,
                'active_instances': active_instances
            }
            
        except Exception as e:
            logger.error(f"Strateji getirme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_instance(self, request: CreateInstanceRequest) -> Dict[str, Any]:
        """Yeni strateji instance'ı oluştur"""
        try:
            # Stratejiyi kontrol et
            metadata = self.repository.get_strategy(request.strategy_id)
            if not metadata:
                return {
                    'success': False,
                    'error': 'Strateji bulunamadı'
                }
            
            # Instance oluştur
            instance_id = str(uuid.uuid4())
            instance = StrategyInstance(
                instance_id=instance_id,
                strategy_id=request.strategy_id,
                user_id="current_user",  # TODO: Auth'dan al
                account_login=request.account_login,
                execution_mode=request.execution_mode,
                parameters=request.parameters,
                is_active=False,
                status="idle",
                created_at=datetime.now()
            )
            
            # Kaydet
            self.instances[instance_id] = instance
            
            # Auto-start
            if request.auto_start:
                await self.start_instance(instance_id)
            
            return {
                'success': True,
                'instance_id': instance_id,
                'instance': instance.dict()
            }
            
        except Exception as e:
            logger.error(f"Instance oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_instance(self, instance_id: str, request: UpdateInstanceRequest) -> Dict[str, Any]:
        """Instance güncelle"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            # Çalışıyorsa durdur
            was_running = instance.is_active
            if was_running:
                await self.stop_instance(instance_id)
            
            # Güncelle
            if request.execution_mode is not None:
                instance.execution_mode = request.execution_mode
            
            if request.parameters is not None:
                instance.parameters.update(request.parameters)
            
            if request.is_active is not None:
                instance.is_active = request.is_active
            
            instance.updated_at = datetime.now()
            
            # Tekrar başlat
            if was_running and instance.is_active:
                await self.start_instance(instance_id)
            
            return {
                'success': True,
                'instance': instance.dict()
            }
            
        except Exception as e:
            logger.error(f"Instance güncelleme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """Instance'ı başlat"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            if instance.is_active:
                return {
                    'success': False,
                    'error': 'Instance zaten çalışıyor'
                }
            
            # Executor'da başlat
            await self.executor.start_instance(instance)
            
            # Durumu güncelle
            instance.is_active = True
            
            return {
                'success': True,
                'message': 'Instance başlatıldı'
            }
            
        except Exception as e:
            logger.error(f"Instance başlatma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Instance'ı durdur"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            if not instance.is_active:
                return {
                    'success': False,
                    'error': 'Instance zaten durmuş'
                }
            
            # Executor'da durdur
            await self.executor.stop_instance(instance_id)
            
            # Durumu güncelle
            instance.is_active = False
            
            return {
                'success': True,
                'message': 'Instance durduruldu'
            }
            
        except Exception as e:
            logger.error(f"Instance durdurma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """Instance detayları"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            # Strateji metadata
            metadata = self.repository.get_strategy(instance.strategy_id)
            
            # Sinyaller
            signals = self.executor.get_instance_signals(instance_id)
            signal_history = self.executor.get_signal_history(instance_id, limit=50)
            
            return {
                'success': True,
                'instance': instance.dict(),
                'strategy': metadata.dict() if metadata else None,
                'pending_signals': [s.dict() for s in signals],
                'signal_history': [s.dict() for s in signal_history]
            }
            
        except Exception as e:
            logger.error(f"Instance getirme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_instances(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Instance listesi"""
        try:
            instances = list(self.instances.values())
            
            # Kullanıcıya göre filtrele
            if user_id:
                instances = [i for i in instances if i.user_id == user_id]
            
            # Strateji bilgilerini ekle
            result = []
            for instance in instances:
                metadata = self.repository.get_strategy(instance.strategy_id)
                result.append({
                    'instance': instance.dict(),
                    'strategy_name': metadata.display_name if metadata else 'Unknown',
                    'strategy_type': metadata.type.value if metadata else 'unknown'
                })
            
            return {
                'success': True,
                'instances': result,
                'total': len(result)
            }
            
        except Exception as e:
            logger.error(f"Instance listeleme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_manual_trade(self, request: ManualTradeRequest) -> Dict[str, Any]:
        """Manuel işlem aç"""
        try:
            result = await self.executor.execute_manual_trade(request)
            return result
            
        except Exception as e:
            logger.error(f"Manuel trade hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_signals(self, instance_id: str) -> Dict[str, Any]:
        """Instance sinyallerini getir"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            # Bekleyen sinyaller
            pending = self.executor.get_instance_signals(instance_id)
            
            # Sinyal geçmişi
            history = self.executor.get_signal_history(instance_id)
            
            return {
                'success': True,
                'pending_signals': [s.dict() for s in pending],
                'signal_history': [s.dict() for s in history],
                'total_signals': instance.total_signals
            }
            
        except Exception as e:
            logger.error(f"Sinyal getirme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_signal(self, instance_id: str, signal_id: str) -> Dict[str, Any]:
        """Bekleyen sinyali execute et"""
        try:
            # Instance ve sinyali bul
            signals = self.executor.get_instance_signals(instance_id)
            signal = next((s for s in signals if s.signal_id == signal_id), None)
            
            if not signal:
                return {
                    'success': False,
                    'error': 'Sinyal bulunamadı'
                }
            
            instance = self.instances.get(instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': 'Instance bulunamadı'
                }
            
            # Sinyali execute et
            await self.executor._execute_signal(instance, signal)
            
            # Kuyruktan kaldır
            signals.remove(signal)
            
            return {
                'success': True,
                'message': 'Sinyal execute edildi',
                'signal': signal.dict()
            }
            
        except Exception as e:
            logger.error(f"Sinyal execution hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def save_config(self, strategy_id: str, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Parametre konfigürasyonunu kaydet"""
        try:
            config_id = str(uuid.uuid4())
            
            config = {
                'id': config_id,
                'strategy_id': strategy_id,
                'name': name,
                'parameters': parameters,
                'created_by': 'current_user',  # TODO: Auth'dan al
                'created_at': datetime.now().isoformat()
            }
            
            self.saved_configs[config_id] = config
            
            return {
                'success': True,
                'config_id': config_id,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Config kaydetme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_configs(self, strategy_id: str) -> Dict[str, Any]:
        """Kaydedilmiş konfigürasyonları listele"""
        try:
            configs = [c for c in self.saved_configs.values() 
                      if c['strategy_id'] == strategy_id]
            
            return {
                'success': True,
                'configs': configs
            }
            
        except Exception as e:
            logger.error(f"Config listeleme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def run_backtest(self, request: BacktestRequest) -> Dict[str, Any]:
        """Backtest çalıştır"""
        try:
            # TODO: Gerçek backtest implementasyonu
            # Şimdilik mock sonuç döndür
            
            result = BacktestResult(
                strategy_id=request.strategy_id,
                parameters=request.parameters,
                symbol=request.symbol,
                timeframe=request.timeframe,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_balance=request.initial_balance,
                final_balance=request.initial_balance * 1.25,  # %25 kar
                total_trades=150,
                winning_trades=90,
                losing_trades=60,
                win_rate=60.0,
                profit_factor=1.8,
                sharpe_ratio=1.2,
                max_drawdown=1500.0,
                max_drawdown_percent=15.0,
                average_win=50.0,
                average_loss=30.0,
                largest_win=200.0,
                largest_loss=100.0,
                average_trade_duration=4.5,
                equity_curve=[],
                trade_history=[],
                monthly_returns={},
                execution_time=2.5
            )
            
            return {
                'success': True,
                'result': result.dict()
            }
            
        except Exception as e:
            logger.error(f"Backtest hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Stratejiyi sil"""
        try:
            # Aktif instance var mı kontrol et
            active_instances = [i for i in self.instances.values() 
                              if i.strategy_id == strategy_id and i.is_active]
            
            if active_instances:
                return {
                    'success': False,
                    'error': 'Bu stratejiyi kullanan aktif instance var'
                }
            
            # Repository'den sil
            success = self.repository.delete_strategy(strategy_id)
            
            if not success:
                return {
                    'success': False,
                    'error': 'Strateji silinemedi'
                }
            
            # İlgili instance'ları sil
            for instance_id in list(self.instances.keys()):
                if self.instances[instance_id].strategy_id == strategy_id:
                    del self.instances[instance_id]
            
            return {
                'success': True,
                'message': 'Strateji silindi'
            }
            
        except Exception as e:
            logger.error(f"Strateji silme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_category_stats(self) -> Dict[str, Any]:
        """Kategori istatistikleri"""
        try:
            stats = self.repository.get_category_stats()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"İstatistik hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
 