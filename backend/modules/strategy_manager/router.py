"""
Strategy Manager Router

MQL4/5 strateji yönetimi API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Dict, Optional, Any
import json
import logging

from .models import (
    StrategyListRequest, StrategyUploadRequest,
    CreateInstanceRequest, UpdateInstanceRequest,
    ManualTradeRequest, BacktestRequest,
    ExecutionMode, StrategyType
)
from .service import StrategyManagerService
from ..mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/strategy-manager", tags=["Strategy Manager"])

# Dependency injection
async def get_service() -> StrategyManagerService:
    """Service instance'ı getir"""
    # TODO: Proper dependency injection
    mt5_service = MT5Service()
    return StrategyManagerService(mt5_service)

# ===== STRATEGY ENDPOINTS =====

@router.post("/strategies/upload")
async def upload_strategy(
    name: str = Form(...),
    display_name: str = Form(...),
    type: StrategyType = Form(...),
    main_file: UploadFile = File(...),
    platform: str = Form("MT5"),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    include_files: Optional[List[UploadFile]] = File(None),
    supported_symbols: Optional[str] = Form("*"),
    recommended_timeframes: Optional[str] = Form(""),
    categories: Optional[str] = Form(""),
    tags: Optional[str] = Form(""),
    service: StrategyManagerService = Depends(get_service)
):
    """Yeni strateji yükle"""
    try:
        # Ana dosya içeriğini oku
        main_content = await main_file.read()
        main_content_str = main_content.decode('utf-8')
        
        # Include dosyalarını oku
        include_dict = {}
        if include_files:
            for file in include_files:
                content = await file.read()
                include_dict[file.filename] = content.decode('utf-8')
        
        # Request oluştur
        request = StrategyUploadRequest(
            name=name,
            display_name=display_name,
            type=type,
            main_file_content=main_content_str,
            platform=platform,
            description=description,
            author=author,
            include_files=include_dict if include_dict else None,
            supported_symbols=supported_symbols.split(',') if supported_symbols else ["*"],
            recommended_timeframes=recommended_timeframes.split(',') if recommended_timeframes else [],
            categories=categories.split(',') if categories else [],
            tags=tags.split(',') if tags else []
        )
        
        result = await service.upload_strategy(request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Strategy upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/list")
async def list_strategies(
    request: StrategyListRequest,
    service: StrategyManagerService = Depends(get_service)
):
    """Strateji listesi"""
    try:
        result = await service.list_strategies(request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Strategy list error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Strateji detayları"""
    try:
        result = await service.get_strategy(strategy_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Get strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Stratejiyi sil"""
    try:
        result = await service.delete_strategy(strategy_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Delete strategy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/stats/categories")
async def get_category_stats(
    service: StrategyManagerService = Depends(get_service)
):
    """Kategori istatistikleri"""
    try:
        result = await service.get_category_stats()
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Category stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== INSTANCE ENDPOINTS =====

@router.post("/instances/create")
async def create_instance(
    request: CreateInstanceRequest,
    service: StrategyManagerService = Depends(get_service)
):
    """Yeni strateji instance'ı oluştur"""
    try:
        result = await service.create_instance(request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Create instance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances")
async def list_instances(
    user_id: Optional[str] = None,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance listesi"""
    try:
        result = await service.list_instances(user_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"List instances error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance detayları"""
    try:
        result = await service.get_instance(instance_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Get instance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/instances/{instance_id}")
async def update_instance(
    instance_id: str,
    request: UpdateInstanceRequest,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance güncelle"""
    try:
        result = await service.update_instance(instance_id, request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Update instance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/start")
async def start_instance(
    instance_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance'ı başlat"""
    try:
        result = await service.start_instance(instance_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Start instance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/stop")
async def stop_instance(
    instance_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance'ı durdur"""
    try:
        result = await service.stop_instance(instance_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Stop instance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SIGNAL ENDPOINTS =====

@router.get("/instances/{instance_id}/signals")
async def get_signals(
    instance_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Instance sinyallerini getir"""
    try:
        result = await service.get_signals(instance_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Get signals error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/signals/{signal_id}/execute")
async def execute_signal(
    instance_id: str,
    signal_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Bekleyen sinyali execute et"""
    try:
        result = await service.execute_signal(instance_id, signal_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Execute signal error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TRADING ENDPOINTS =====

@router.post("/instances/manual-trade")
async def manual_trade(
    request: ManualTradeRequest,
    service: StrategyManagerService = Depends(get_service)
):
    """Manuel işlem aç"""
    try:
        result = await service.execute_manual_trade(request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Manual trade error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CONFIG ENDPOINTS =====

@router.post("/strategies/{strategy_id}/configs")
async def save_config(
    strategy_id: str,
    name: str,
    parameters: Dict[str, Any],
    service: StrategyManagerService = Depends(get_service)
):
    """Parametre konfigürasyonu kaydet"""
    try:
        result = await service.save_config(strategy_id, name, parameters)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Save config error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}/configs")
async def list_configs(
    strategy_id: str,
    service: StrategyManagerService = Depends(get_service)
):
    """Kaydedilmiş konfigürasyonları listele"""
    try:
        result = await service.list_configs(strategy_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"List configs error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== BACKTEST ENDPOINTS =====

@router.post("/backtest")
async def run_backtest(
    request: BacktestRequest,
    service: StrategyManagerService = Depends(get_service)
):
    """Backtest çalıştır"""
    try:
        result = await service.run_backtest(request)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== HELPER ENDPOINTS =====

@router.get("/execution-modes")
async def get_execution_modes():
    """Execution mode listesi"""
    return {
        'success': True,
        'modes': [
            {
                'value': ExecutionMode.ROBOT.value,
                'label': 'Robot Mode',
                'description': 'Tam otomatik trading - Sinyaller otomatik execute edilir'
            },
            {
                'value': ExecutionMode.SIGNAL.value,
                'label': 'Signal Mode',
                'description': 'Sadece sinyal üretir - Manuel onay gerekir'
            },
            {
                'value': ExecutionMode.MANUAL.value,
                'label': 'Manual Mode',
                'description': 'Sadece analiz sağlar - Tüm işlemler manuel'
            },
            {
                'value': ExecutionMode.HYBRID.value,
                'label': 'Hybrid Mode',
                'description': 'Yüksek güvenlikli sinyaller otomatik, diğerleri manuel'
            }
        ]
    }

@router.get("/strategy-types")
async def get_strategy_types():
    """Strateji türleri listesi"""
    return {
        'success': True,
        'types': [
            {
                'value': StrategyType.GRID_TRADING.value,
                'label': 'Grid Trading',
                'description': 'Fiyat gridleri ile trading'
            },
            {
                'value': StrategyType.SCALPING.value,
                'label': 'Scalping',
                'description': 'Kısa vadeli hızlı işlemler'
            },
            {
                'value': StrategyType.TREND_FOLLOWING.value,
                'label': 'Trend Following',
                'description': 'Trend takip stratejileri'
            },
            {
                'value': StrategyType.BREAKOUT.value,
                'label': 'Breakout',
                'description': 'Kırılım bazlı stratejiler'
            },
            {
                'value': StrategyType.ARBITRAGE.value,
                'label': 'Arbitrage',
                'description': 'Arbitraj fırsatları'
            },
            {
                'value': StrategyType.HEDGING.value,
                'label': 'Hedging',
                'description': 'Risk hedge stratejileri'
            },
            {
                'value': StrategyType.CUSTOM.value,
                'label': 'Custom',
                'description': 'Özel stratejiler'
            }
        ]
    } 