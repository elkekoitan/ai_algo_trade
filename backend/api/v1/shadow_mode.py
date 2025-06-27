"""
Shadow Mode API Endpoints
🥷 Büyük oyuncuların gölgesinde hareket et
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
import logging

from backend.modules.shadow_mode.shadow_service import ShadowModeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shadow", tags=["shadow_mode"])

# Global Shadow Mode service instance
shadow_service = ShadowModeService()

@router.post("/activate")
async def activate_shadow_mode(stealth_level: int = 5) -> Dict:
    """
    🥷 Shadow Mode'u aktifleştir
    
    Args:
        stealth_level: Gizlilik seviyesi (1-10)
    """
    try:
        if not 1 <= stealth_level <= 10:
            raise HTTPException(status_code=400, detail="Stealth level must be between 1-10")
        
        result = await shadow_service.activate_shadow_mode(stealth_level)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shadow Mode activation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate")
async def deactivate_shadow_mode() -> Dict:
    """
    🛑 Shadow Mode'u deaktifleştir
    """
    try:
        result = await shadow_service.deactivate_shadow_mode()
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('message'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shadow Mode deactivation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_shadow_status() -> Dict:
    """
    📊 Shadow Mode durumunu getir
    """
    try:
        return await shadow_service.get_shadow_state()
        
    except Exception as e:
        logger.error(f"Get shadow status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_recent_alerts() -> List[Dict]:
    """
    🚨 Son Shadow Mode alertlerini getir
    """
    try:
        return await shadow_service.get_recent_alerts()
        
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whales")
async def get_whale_detections() -> List[Dict]:
    """
    🐋 Aktif whale tespitlerini getir
    """
    try:
        return await shadow_service.get_whale_detections()
        
    except Exception as e:
        logger.error(f"Get whale detections error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dark-pools")
async def get_dark_pool_summary() -> Dict:
    """
    🌑 Dark pool aktivite özetini getir
    """
    try:
        return await shadow_service.get_dark_pool_summary()
        
    except Exception as e:
        logger.error(f"Get dark pool summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/institutional-flows")
async def get_institutional_flows() -> Dict:
    """
    🏛️ Kurumsal akış özetini getir
    """
    try:
        return await shadow_service.get_institutional_flow_summary()
        
    except Exception as e:
        logger.error(f"Get institutional flows error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stealth-order")
async def create_stealth_order(
    symbol: str,
    side: str,
    quantity: float
) -> Dict:
    """
    🥷 Gizli emir oluştur
    
    Args:
        symbol: İşlem çifti (örn: EURUSD)
        side: BUY veya SELL
        quantity: Miktar
    """
    try:
        if side not in ['BUY', 'SELL']:
            raise HTTPException(status_code=400, detail="Side must be BUY or SELL")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        result = await shadow_service.create_stealth_order(symbol, side, quantity)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stealth order creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/arbitrage-opportunities")
async def get_arbitrage_opportunities() -> List[Dict]:
    """
    💰 Dark pool arbitraj fırsatlarını getir
    """
    try:
        return await shadow_service.dark_pool_monitor.get_arbitrage_opportunities()
        
    except Exception as e:
        logger.error(f"Get arbitrage opportunities error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manipulation-patterns")
async def get_manipulation_patterns() -> List[Dict]:
    """
    🔍 Tespit edilen manipulation pattern'lerini getir
    """
    try:
        return await shadow_service.pattern_analyzer.get_recent_patterns()
        
    except Exception as e:
        logger.error(f"Get manipulation patterns error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stealth-orders")
async def get_stealth_orders() -> List[Dict]:
    """
    📋 Aktif gizli emirleri getir
    """
    try:
        return await shadow_service.stealth_executor.get_active_stealth_orders()
        
    except Exception as e:
        logger.error(f"Get stealth orders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 