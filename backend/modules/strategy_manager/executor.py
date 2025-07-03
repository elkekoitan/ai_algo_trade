"""
Strategy Executor

Farklı execution modlarında strateji çalıştırma.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import (
    ExecutionMode, SignalType, TradingSignal, StrategyInstance,
    ManualTradeRequest
)
from ..mt5_integration.service import MT5Service

logger = logging.getLogger(__name__)

class StrategyExecutor:
    """Strateji executor - multi-mode execution"""
    
    def __init__(self, mt5_service: MT5Service):
        self.mt5_service = mt5_service
        self.running_instances: Dict[str, StrategyInstance] = {}
        self.signal_queue: Dict[str, List[TradingSignal]] = {}
        self.signal_history: Dict[str, List[TradingSignal]] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
    
    async def start_instance(self, instance: StrategyInstance):
        """Strateji instance'ını başlat"""
        try:
            instance_id = instance.instance_id
            
            # Instance'ı kaydet
            self.running_instances[instance_id] = instance
            self.signal_queue[instance_id] = []
            self.signal_history[instance_id] = []
            
            # MT5'e bağlan
            if not await self.mt5_service.connect_to_account(
                instance.account_login,
                # Password'ü config'den al
                "password",  # TODO: Güvenli password yönetimi
                "Tickmill-Demo"
            ):
                raise Exception("MT5 bağlantısı kurulamadı")
            
            # Execution moduna göre başlat
            if instance.execution_mode == ExecutionMode.ROBOT:
                task = asyncio.create_task(self._run_robot_mode(instance))
            elif instance.execution_mode == ExecutionMode.SIGNAL:
                task = asyncio.create_task(self._run_signal_mode(instance))
            elif instance.execution_mode == ExecutionMode.MANUAL:
                task = asyncio.create_task(self._run_manual_mode(instance))
            elif instance.execution_mode == ExecutionMode.HYBRID:
                task = asyncio.create_task(self._run_hybrid_mode(instance))
            else:
                raise ValueError(f"Geçersiz execution mode: {instance.execution_mode}")
            
            self._tasks[instance_id] = task
            
            # Instance durumunu güncelle
            instance.status = "running"
            instance.started_at = datetime.now()
            
            logger.info(f"Instance başlatıldı: {instance_id} ({instance.execution_mode.value} mode)")
            
        except Exception as e:
            logger.error(f"Instance başlatma hatası: {str(e)}")
            instance.status = "error"
            raise
    
    async def stop_instance(self, instance_id: str):
        """Instance'ı durdur"""
        try:
            if instance_id in self._tasks:
                # Task'ı iptal et
                self._tasks[instance_id].cancel()
                
                try:
                    await self._tasks[instance_id]
                except asyncio.CancelledError:
                    pass
                
                del self._tasks[instance_id]
            
            if instance_id in self.running_instances:
                instance = self.running_instances[instance_id]
                instance.status = "stopped"
                instance.stopped_at = datetime.now()
                
                # Açık pozisyonları kapat (robot mode için)
                if instance.execution_mode == ExecutionMode.ROBOT:
                    await self._close_all_positions(instance)
            
            logger.info(f"Instance durduruldu: {instance_id}")
            
        except Exception as e:
            logger.error(f"Instance durdurma hatası: {str(e)}")
    
    async def _run_robot_mode(self, instance: StrategyInstance):
        """Robot mode - tam otomatik trading"""
        logger.info(f"Robot mode başlatıldı: {instance.instance_id}")
        
        while True:
            try:
                # Strateji mantığını çalıştır
                signal = await self._generate_signal(instance)
                
                if signal and signal.signal_type != SignalType.NEUTRAL:
                    # Sinyali kaydet
                    self.signal_history[instance.instance_id].append(signal)
                    
                    # Otomatik execute et
                    await self._execute_signal(instance, signal)
                    
                    # İstatistikleri güncelle
                    instance.total_signals += 1
                
                # Risk kontrolü
                await self._check_risk_limits(instance)
                
                # Bekleme süresi (strateji parametrelerine göre ayarlanabilir)
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Robot mode hatası: {str(e)}")
                await asyncio.sleep(5)
    
    async def _run_signal_mode(self, instance: StrategyInstance):
        """Signal mode - sadece sinyal üret"""
        logger.info(f"Signal mode başlatıldı: {instance.instance_id}")
        
        while True:
            try:
                # Strateji mantığını çalıştır
                signal = await self._generate_signal(instance)
                
                if signal and signal.signal_type != SignalType.NEUTRAL:
                    # Sinyali kuyruğa ekle
                    self.signal_queue[instance.instance_id].append(signal)
                    self.signal_history[instance.instance_id].append(signal)
                    
                    # İstatistikleri güncelle
                    instance.total_signals += 1
                    instance.last_signal = datetime.now()
                    
                    # Bildirim gönder (opsiyonel)
                    await self._send_signal_notification(instance, signal)
                    
                    logger.info(f"Yeni sinyal: {signal.signal_type.value} - {signal.symbol}")
                
                # Bekleme süresi
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Signal mode hatası: {str(e)}")
                await asyncio.sleep(5)
    
    async def _run_manual_mode(self, instance: StrategyInstance):
        """Manual mode - sadece analiz sağla"""
        logger.info(f"Manual mode başlatıldı: {instance.instance_id}")
        
        while True:
            try:
                # Market analizi yap
                analysis = await self._perform_market_analysis(instance)
                
                # Analizi güncelle (WebSocket veya polling ile frontend'e gönderilecek)
                instance.parameters['last_analysis'] = analysis
                instance.parameters['last_analysis_time'] = datetime.now().isoformat()
                
                # Bekleme süresi (daha uzun olabilir)
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Manual mode hatası: {str(e)}")
                await asyncio.sleep(10)
    
    async def _run_hybrid_mode(self, instance: StrategyInstance):
        """Hybrid mode - sinyal + yarı otomatik"""
        logger.info(f"Hybrid mode başlatıldı: {instance.instance_id}")
        
        while True:
            try:
                # Strateji mantığını çalıştır
                signal = await self._generate_signal(instance)
                
                if signal and signal.signal_type != SignalType.NEUTRAL:
                    # Sinyali kaydet
                    self.signal_queue[instance.instance_id].append(signal)
                    self.signal_history[instance.instance_id].append(signal)
                    
                    # Yüksek güvenlikli sinyalleri otomatik execute et
                    if signal.confidence >= 80:  # %80 ve üzeri güvenlik
                        await self._execute_signal(instance, signal)
                        logger.info(f"Yüksek güvenlikli sinyal otomatik execute edildi: {signal.signal_type.value}")
                    else:
                        # Düşük güvenlikli sinyaller için onay bekle
                        await self._send_signal_notification(instance, signal)
                        logger.info(f"Onay bekleyen sinyal: {signal.signal_type.value} (Güvenlik: {signal.confidence}%)")
                    
                    instance.total_signals += 1
                
                # Risk kontrolü
                await self._check_risk_limits(instance)
                
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Hybrid mode hatası: {str(e)}")
                await asyncio.sleep(5)
    
    async def _generate_signal(self, instance: StrategyInstance) -> Optional[TradingSignal]:
        """Strateji mantığından sinyal üret"""
        try:
            # Burada gerçek strateji mantığı çalışacak
            # Şimdilik örnek bir implementasyon
            
            # Market data al
            symbol = instance.parameters.get('symbol', 'EURUSD')
            tick = await self.mt5_service.get_symbol_tick(symbol)
            
            if not tick:
                return None
            
            # Basit bir örnek: RSI bazlı sinyal
            # TODO: Gerçek strateji mantığını buraya entegre et
            
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                instance_id=instance.instance_id,
                strategy_id=instance.strategy_id,
                signal_type=SignalType.NEUTRAL,
                symbol=symbol,
                execution_mode=instance.execution_mode,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5)
            )
            
            # Örnek sinyal üretimi (gerçek mantık buraya gelecek)
            import random
            rand = random.random()
            
            if rand < 0.01:  # %1 şans ile buy sinyali
                signal.signal_type = SignalType.BUY
                signal.direction = "buy"
                signal.entry_price = tick['ask']
                signal.stop_loss = tick['ask'] - 0.0050  # 50 pips SL
                signal.take_profit = tick['ask'] + 0.0100  # 100 pips TP
                signal.lot_size = instance.parameters.get('lot_size', 0.01)
                signal.confidence = random.randint(60, 95)
                signal.reasoning = "Test buy sinyali"
                
            elif rand > 0.99:  # %1 şans ile sell sinyali
                signal.signal_type = SignalType.SELL
                signal.direction = "sell"
                signal.entry_price = tick['bid']
                signal.stop_loss = tick['bid'] + 0.0050  # 50 pips SL
                signal.take_profit = tick['bid'] - 0.0100  # 100 pips TP
                signal.lot_size = instance.parameters.get('lot_size', 0.01)
                signal.confidence = random.randint(60, 95)
                signal.reasoning = "Test sell sinyali"
            
            return signal
            
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {str(e)}")
            return None
    
    async def _execute_signal(self, instance: StrategyInstance, signal: TradingSignal):
        """Sinyali execute et"""
        try:
            if signal.signal_type == SignalType.BUY:
                result = await self.mt5_service.place_order(
                    symbol=signal.symbol,
                    order_type="buy",
                    volume=signal.lot_size,
                    price=signal.entry_price,
                    sl=signal.stop_loss,
                    tp=signal.take_profit,
                    comment=f"AI_{instance.instance_id[:8]}"
                )
                
            elif signal.signal_type == SignalType.SELL:
                result = await self.mt5_service.place_order(
                    symbol=signal.symbol,
                    order_type="sell",
                    volume=signal.lot_size,
                    price=signal.entry_price,
                    sl=signal.stop_loss,
                    tp=signal.take_profit,
                    comment=f"AI_{instance.instance_id[:8]}"
                )
            else:
                return
            
            if result and result.get('success'):
                signal.is_executed = True
                signal.executed_at = datetime.now()
                signal.execution_price = result.get('price')
                signal.order_ticket = result.get('ticket')
                
                # İstatistikleri güncelle
                instance.open_positions += 1
                instance.total_trades += 1
                
                logger.info(f"Sinyal execute edildi: {signal.signal_type.value} - Ticket: {signal.order_ticket}")
            
        except Exception as e:
            logger.error(f"Sinyal execution hatası: {str(e)}")
    
    async def _perform_market_analysis(self, instance: StrategyInstance) -> Dict[str, Any]:
        """Market analizi yap"""
        try:
            symbol = instance.parameters.get('symbol', 'EURUSD')
            
            # Market data
            tick = await self.mt5_service.get_symbol_tick(symbol)
            
            # Basit analiz örneği
            analysis = {
                'symbol': symbol,
                'current_price': tick['last'] if tick else 0,
                'bid': tick['bid'] if tick else 0,
                'ask': tick['ask'] if tick else 0,
                'spread': (tick['ask'] - tick['bid']) * 10000 if tick else 0,  # pips
                'timestamp': datetime.now().isoformat(),
                'trend': 'neutral',  # TODO: Gerçek trend analizi
                'strength': 50,  # 0-100
                'recommendation': 'hold'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Market analizi hatası: {str(e)}")
            return {}
    
    async def _check_risk_limits(self, instance: StrategyInstance):
        """Risk limitlerini kontrol et"""
        try:
            # Hesap bilgilerini al
            account_info = await self.mt5_service.get_account_info()
            
            if not account_info:
                return
            
            # Drawdown kontrolü
            equity = account_info.get('equity', 0)
            balance = account_info.get('balance', 0)
            
            if balance > 0:
                drawdown_percent = ((balance - equity) / balance) * 100
                
                max_drawdown = instance.parameters.get('max_drawdown_percent', 20)
                
                if drawdown_percent > max_drawdown:
                    logger.warning(f"Maksimum drawdown aşıldı: {drawdown_percent:.2f}%")
                    
                    # Robot mode'da tüm pozisyonları kapat
                    if instance.execution_mode == ExecutionMode.ROBOT:
                        await self._close_all_positions(instance)
                        await self.stop_instance(instance.instance_id)
            
        except Exception as e:
            logger.error(f"Risk kontrolü hatası: {str(e)}")
    
    async def _close_all_positions(self, instance: StrategyInstance):
        """Tüm pozisyonları kapat"""
        try:
            positions = await self.mt5_service.get_positions()
            
            for position in positions:
                # Instance'a ait pozisyonları kontrol et
                if f"AI_{instance.instance_id[:8]}" in position.get('comment', ''):
                    await self.mt5_service.close_position(position['ticket'])
                    logger.info(f"Pozisyon kapatıldı: {position['ticket']}")
            
            instance.open_positions = 0
            
        except Exception as e:
            logger.error(f"Pozisyon kapatma hatası: {str(e)}")
    
    async def _send_signal_notification(self, instance: StrategyInstance, signal: TradingSignal):
        """Sinyal bildirimi gönder"""
        # TODO: WebSocket veya notification service ile bildirim gönder
        pass
    
    async def execute_manual_trade(self, request: ManualTradeRequest) -> Dict[str, Any]:
        """Manuel işlem aç"""
        try:
            instance = self.running_instances.get(request.instance_id)
            if not instance:
                raise ValueError("Instance bulunamadı")
            
            # MT5'e bağlan
            await self.mt5_service.connect_to_account(instance.account_login, "password", "Tickmill-Demo")
            
            if request.action in ['buy', 'sell']:
                result = await self.mt5_service.place_order(
                    symbol=request.symbol,
                    order_type=request.action,
                    volume=request.lot_size,
                    sl=request.stop_loss,
                    tp=request.take_profit,
                    comment=request.comment or f"Manual_{instance.instance_id[:8]}"
                )
                
                if result and result.get('success'):
                    instance.total_trades += 1
                    instance.open_positions += 1
                
                return result
                
            elif request.action == 'close':
                # Pozisyonları kapat
                positions = await self.mt5_service.get_positions()
                closed_count = 0
                
                for position in positions:
                    if position['symbol'] == request.symbol:
                        result = await self.mt5_service.close_position(position['ticket'])
                        if result and result.get('success'):
                            closed_count += 1
                
                instance.open_positions = max(0, instance.open_positions - closed_count)
                
                return {
                    'success': True,
                    'closed_positions': closed_count
                }
            
            else:
                raise ValueError(f"Geçersiz action: {request.action}")
                
        except Exception as e:
            logger.error(f"Manuel trade hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_instance_signals(self, instance_id: str) -> List[TradingSignal]:
        """Instance sinyallerini getir"""
        return self.signal_queue.get(instance_id, [])
    
    def get_signal_history(self, instance_id: str, limit: int = 100) -> List[TradingSignal]:
        """Sinyal geçmişini getir"""
        history = self.signal_history.get(instance_id, [])
        return history[-limit:]  # Son N sinyal
    
    def clear_signal_queue(self, instance_id: str):
        """Sinyal kuyruğunu temizle"""
        if instance_id in self.signal_queue:
            self.signal_queue[instance_id].clear() 