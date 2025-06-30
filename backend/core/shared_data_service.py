"""
Shared Data Service - Modüller arası veri paylaşımı ve event yönetimi
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from fastapi import WebSocket
import MetaTrader5 as mt5

class EventBus:
    """Modüller arası event yayını için event bus"""
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.websocket_clients: List[WebSocket] = []
    
    async def emit(self, event_type: str, data: dict):
        """Event yayınla"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Subscriber'lara bildir
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                await callback(event)
        
        # WebSocket client'larına yayınla
        for client in self.websocket_clients:
            try:
                await client.send_json(event)
            except:
                self.websocket_clients.remove(client)
    
    def subscribe(self, event_type: str, callback: callable):
        """Event'e abone ol"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def add_websocket(self, websocket: WebSocket):
        """WebSocket client ekle"""
        self.websocket_clients.append(websocket)

class SignalPool:
    """Tüm modüllerden gelen sinyallerin merkezi havuzu"""
    def __init__(self):
        self.signals: List[Dict[str, Any]] = []
        self.active_signals: List[Dict[str, Any]] = []
    
    async def add_signal(self, signal: Dict[str, Any]):
        """Yeni sinyal ekle"""
        signal["id"] = f"{signal['source']}_{datetime.now().timestamp()}"
        signal["created_at"] = datetime.now().isoformat()
        signal["status"] = "ACTIVE"
        
        self.signals.append(signal)
        self.active_signals.append(signal)
        
        # 100'den fazla sinyal varsa eski olanları temizle
        if len(self.signals) > 100:
            self.signals = self.signals[-100:]
        
        return signal
    
    async def get_active(self) -> List[Dict[str, Any]]:
        """Aktif sinyalleri getir"""
        # Expired sinyalleri temizle
        self.active_signals = [
            s for s in self.active_signals 
            if s.get("expires_at", datetime.max.isoformat()) > datetime.now().isoformat()
        ]
        return self.active_signals
    
    async def update_signal_status(self, signal_id: str, status: str):
        """Sinyal durumunu güncelle"""
        for signal in self.active_signals:
            if signal["id"] == signal_id:
                signal["status"] = status
                if status in ["EXECUTED", "EXPIRED", "CANCELLED"]:
                    self.active_signals.remove(signal)
                break

class RiskMetrics:
    """Sistem geneli risk metrikleri"""
    def __init__(self):
        self.current_risk_level = "NORMAL"
        self.risk_scores = {}
        self.max_drawdown = 0
        self.current_exposure = 0
    
    async def update_module_risk(self, module: str, risk_score: float):
        """Modül risk skorunu güncelle"""
        self.risk_scores[module] = risk_score
        await self._calculate_system_risk()
    
    async def _calculate_system_risk(self):
        """Sistem geneli risk seviyesini hesapla"""
        if not self.risk_scores:
            return
        
        avg_risk = sum(self.risk_scores.values()) / len(self.risk_scores)
        
        if avg_risk > 0.8:
            self.current_risk_level = "CRITICAL"
        elif avg_risk > 0.6:
            self.current_risk_level = "HIGH"
        elif avg_risk > 0.4:
            self.current_risk_level = "MEDIUM"
        else:
            self.current_risk_level = "NORMAL"
    
    async def get_current(self) -> Dict[str, Any]:
        """Güncel risk durumunu getir"""
        return {
            "level": self.current_risk_level,
            "scores": self.risk_scores,
            "max_drawdown": self.max_drawdown,
            "exposure": self.current_exposure,
            "timestamp": datetime.now().isoformat()
        }

class MT5DataStream:
    """MT5 canlı veri akışı"""
    def __init__(self):
        self.login = 25201110
        self.password = "e|([rXU1IsiM"
        self.server = "Tickmill-Demo"
    
    async def get_account(self) -> Optional[Dict[str, Any]]:
        """Hesap bilgilerini getir"""
        try:
            if not mt5.initialize(login=self.login, password=self.password, server=self.server):
                return None
            
            account = mt5.account_info()
            if not account:
                return None
            
            return {
                "balance": account.balance,
                "equity": account.equity,
                "margin": account.margin,
                "free_margin": account.margin_free,
                "profit": account.profit,
                "leverage": account.leverage,
                "currency": account.currency,
                "server": account.server,
                "company": account.company
            }
        except Exception as e:
            print(f"MT5 account error: {e}")
            return None
        finally:
            mt5.shutdown()
    
    async def get_prices(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Canlı fiyatları getir"""
        if symbols is None:
            symbols = ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "BTCUSD"]
        
        prices = {}
        try:
            if not mt5.initialize(login=self.login, password=self.password, server=self.server):
                return prices
            
            for symbol in symbols:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    prices[symbol] = {
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "time": datetime.fromtimestamp(tick.time).isoformat(),
                        "volume": tick.volume
                    }
            
            return prices
        except Exception as e:
            print(f"MT5 prices error: {e}")
            return prices
        finally:
            mt5.shutdown()

class SharedDataService:
    """Merkezi veri paylaşım servisi"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.mt5_data = MT5DataStream()
        self.signal_pool = SignalPool()
        self.risk_metrics = RiskMetrics()
        self.event_bus = EventBus()
        
        # Modül verileri
        self.module_data = {
            "shadow_mode": {},
            "god_mode": {},
            "market_narrator": {},
            "adaptive_trade_manager": {},
            "strategy_whisperer": {}
        }
        
        self._initialized = True
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Tüm modüllere event yayınla"""
        await self.event_bus.emit(event_type, data)
    
    async def get_unified_market_view(self) -> Dict[str, Any]:
        """Tüm modüllerin kullanacağı birleşik piyasa görünümü"""
        account = await self.mt5_data.get_account()
        prices = await self.mt5_data.get_prices()
        active_signals = await self.signal_pool.get_active()
        risk_status = await self.risk_metrics.get_current()
        
        return {
            "mt5_account": account,
            "live_prices": prices,
            "active_signals": active_signals,
            "risk_status": risk_status,
            "module_status": self._get_module_status(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_module_status(self) -> Dict[str, Any]:
        """Modül durumlarını getir"""
        return {
            module: {
                "active": bool(data),
                "last_update": data.get("last_update", "N/A")
            }
            for module, data in self.module_data.items()
        }
    
    async def update_module_data(self, module: str, data: Dict[str, Any]):
        """Modül verisini güncelle"""
        if module in self.module_data:
            self.module_data[module] = {
                **data,
                "last_update": datetime.now().isoformat()
            }
            
            # İlgili event'i yayınla
            await self.broadcast_event(f"{module}:data_updated", data)
    
    async def get_module_data(self, module: str) -> Optional[Dict[str, Any]]:
        """Modül verisini getir"""
        return self.module_data.get(module)
    
    async def cross_module_request(self, source: str, target: str, request_type: str, params: Dict[str, Any]) -> Any:
        """Modüller arası veri isteği"""
        event_type = f"{source}:request:{target}"
        await self.broadcast_event(event_type, {
            "request_type": request_type,
            "params": params
        })
        
        # Response bekle (basit implementasyon)
        # Gerçek sistemde promise/future pattern kullanılmalı
        await asyncio.sleep(0.1)
        return self.module_data.get(target, {}).get(request_type)

# Singleton instance
shared_data_service = SharedDataService() 