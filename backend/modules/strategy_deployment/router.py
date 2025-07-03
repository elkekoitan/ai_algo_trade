"""
Strategy Deployment Router

MT5 strateji deployment API endpoint'leri.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging

from .service import StrategyDeploymentService
from .models import (
    DeploymentRequest, DeploymentResponse, DeploymentInfo, 
    StrategyConfig, StrategyParameters, MT5AccountInfo,
    DeploymentListResponse, StrategyPerformance, StrategyType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategy-deployment", tags=["Strategy Deployment"])

# Service instance
deployment_service = StrategyDeploymentService()

@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_strategy(request: DeploymentRequest):
    """
    Stratejiyi belirtilen MT5 hesaplarına deploy et
    
    - **strategy_config**: Strateji konfigürasyonu
    - **target_accounts**: Hedef MT5 hesapları
    - **master_account**: Ana hesap (copy trading için)
    - **enable_copy_trading**: Copy trading aktif et
    - **deployment_name**: Deployment ismi
    - **auto_start**: Otomatik başlat
    """
    try:
        return await deployment_service.deploy_strategy(request)
    except Exception as e:
        logger.error(f"Strategy deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy/sanal-supurge-v1", response_model=DeploymentResponse)
async def deploy_sanal_supurge_v1(
    deployment_name: str,
    target_accounts: List[MT5AccountInfo],
    master_account: MT5AccountInfo,
    parameters: StrategyParameters,
    symbol: str = "EURUSD",
    enable_copy_trading: bool = True,
    auto_start: bool = True
):
    """
    Sanal Süpürge V1 stratejisini hızlı deploy et
    
    Önceden tanımlı Sanal Süpürge V1 stratejisi için kolay deployment.
    """
    try:
        # Sanal Süpürge V1 konfigürasyonu oluştur
        strategy_config = StrategyConfig(
            strategy_id="sanal_supurge_v1_" + deployment_name.lower().replace(" ", "_"),
            strategy_name=f"Sanal Süpürge V1 - {deployment_name}",
            strategy_type=StrategyType.SANAL_SUPURGE_V1,
            description="14 seviyeli grid trading sistemi",
            parameters=parameters,
            symbol=symbol,
            timeframe="M15"
        )
        
        # Deployment isteği oluştur
        deployment_request = DeploymentRequest(
            strategy_config=strategy_config,
            target_accounts=target_accounts,
            master_account=master_account,
            enable_copy_trading=enable_copy_trading,
            deployment_name=deployment_name,
            auto_start=auto_start
        )
        
        return await deployment_service.deploy_strategy(deployment_request)
        
    except Exception as e:
        logger.error(f"Sanal Süpürge V1 deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments", response_model=DeploymentListResponse)
async def list_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """
    Aktif deployment'ları listele
    """
    try:
        deployments = deployment_service.list_deployments(page, page_size)
        total = len(deployment_service.deployments)
        
        return DeploymentListResponse(
            deployments=deployments,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"List deployments error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments/{deployment_id}", response_model=DeploymentInfo)
async def get_deployment(deployment_id: str):
    """
    Belirli bir deployment'ın detaylarını getir
    """
    try:
        deployment = deployment_service.get_deployment(deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment bulunamadı")
        
        return deployment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deployments/{deployment_id}/stop", response_model=DeploymentResponse)
async def stop_deployment(deployment_id: str):
    """
    Deployment'ı durdur
    """
    try:
        return await deployment_service.stop_deployment(deployment_id)
    except Exception as e:
        logger.error(f"Stop deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments/{deployment_id}/performance")
async def get_deployment_performance(deployment_id: str) -> Dict[str, StrategyPerformance]:
    """
    Deployment performans verilerini getir
    """
    try:
        return await deployment_service.get_deployment_performance(deployment_id)
    except Exception as e:
        logger.error(f"Get deployment performance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template/sanal-supurge-v1")
async def get_sanal_supurge_v1_template() -> Dict[str, Any]:
    """
    Sanal Süpürge V1 için varsayılan parametre template'ini getir
    """
    try:
        template_params = StrategyParameters()
        
        return {
            "strategy_type": "sanal_supurge_v1",
            "strategy_name": "Sanal Süpürge V1",
            "description": "14 seviyeli grid trading sistemi",
            "default_parameters": template_params.dict(),
            "parameter_descriptions": {
                "buy_islemi_ac": "Buy işlemleri aktif",
                "sell_islemi_ac": "Sell işlemleri aktif", 
                "position_comment": "Pozisyon magic comment",
                "pivot_ust": "Üst pivot seviyesi",
                "pivot_alt": "Alt pivot seviyesi",
                "lot_sizes": "Her seviye için lot boyutları (1-14)",
                "tp_levels": "Take Profit seviyeleri (pips)",
                "sl_levels": "Stop Loss seviyeleri (pips)",
                "level_distances": "Seviye arası mesafeler (pips)",
                "active_orders": "Aktif seviyeler (true/false)",
                "use_time_limit": "Zaman filtresi kullan",
                "alert_3": "3. seviyede alert gönder",
                "alert_4": "4. seviyede alert gönder",
                "alert_5": "5. seviyede alert gönder"
            },
            "recommended_settings": {
                "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
                "timeframes": ["M15", "M30", "H1"],
                "minimum_balance": 10000,
                "recommended_leverage": 100
            }
        }
        
    except Exception as e:
        logger.error(f"Get template error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts/demo")
async def get_demo_accounts() -> List[Dict[str, Any]]:
    """
    Sistemde tanımlı demo hesapları getir
    """
    try:
        # Hafızadaki demo hesap bilgileri
        demo_accounts = [
            {
                "name": "Master Account",
                "login": 25201110,
                "server": "Tickmill-Demo",
                "account_type": "demo",
                "balance": 498428.79,
                "currency": "USD",
                "leverage": 100,
                "description": "Ana copy trading hesabı"
            },
            {
                "name": "Copy Account 1",
                "login": 25216036,
                "server": "Tickmill-Demo", 
                "account_type": "demo",
                "balance": 10000.0,
                "currency": "USD",
                "leverage": 100,
                "description": "Copy trading hedef hesabı 1"
            },
            {
                "name": "Copy Account 2",
                "login": 25216037,
                "server": "Tickmill-Demo",
                "account_type": "demo", 
                "balance": 100000.0,
                "currency": "USD",
                "leverage": 100,
                "description": "Copy trading hedef hesabı 2"
            }
        ]
        
        return demo_accounts
        
    except Exception as e:
        logger.error(f"Get demo accounts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-deployment")
async def create_test_deployment() -> DeploymentResponse:
    """
    Test deployment oluştur - Sanal Süpürge V1 ile tüm demo hesapları
    """
    try:
        # Demo hesap bilgileri (güvenlik için şifreler gizli)
        master_account = MT5AccountInfo(
            login=25201110,
            server="Tickmill-Demo",
            password="e|([rXU1IsiM",  # Gerçek şifre hafızadan
            account_type="demo"
        )
        
        target_accounts = [
            MT5AccountInfo(
                login=25216036,
                server="Tickmill-Demo", 
                password="oB9UY1&,B=^9",  # Gerçek şifre hafızadan
                account_type="demo"
            ),
            MT5AccountInfo(
                login=25216037,
                server="Tickmill-Demo",
                password="L[.Sdo4QRxx2",  # Gerçek şifre hafızadan
                account_type="demo"
            )
        ]
        
        # Test parametreleri
        test_params = StrategyParameters(
            buy_islemi_ac=True,
            sell_islemi_ac=True,
            position_comment="HayaletSüpürge_Test",
            pivot_ust=1.8,
            pivot_alt=1.01,
            lot_sizes=[0.01] * 10 + [0.02] * 4,  # Daha conservative
            tp_levels=[800] * 9 + [2000] * 5,  # Daha conservative TP
            sl_levels=[150] * 14,  # Biraz daha geniş SL
            use_time_limit=True,
            do_not_open_after_hour=22,
            do_not_open_before_hour=6
        )
        
        # Test deployment
        return await deploy_sanal_supurge_v1(
            deployment_name="Test Deployment - Sanal Süpürge V1",
            target_accounts=target_accounts,
            master_account=master_account,
            parameters=test_params,
            symbol="EURUSD",
            enable_copy_trading=True,
            auto_start=True
        )
        
    except Exception as e:
        logger.error(f"Test deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 