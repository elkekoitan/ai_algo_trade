"""
High-Frequency Data Processor
Handles ultra-low latency data processing with WebSocket multiplexing, Redis streams, and edge computing.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
import redis.asyncio as redis
import websockets
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from ...core.logger import setup_logger

logger = setup_logger(__name__)

class DataStreamType(Enum):
    TICK = "tick"
    BOOK = "book" 
    TRADE = "trade"
    NEWS = "news"
    SENTIMENT = "sentiment"

@dataclass
class TickData:
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: float
    volume: float
    spread: float
    
@dataclass
class OrderBookData:
    symbol: str
    timestamp: datetime
    bids: List[tuple]  # [(price, size), ...]
    asks: List[tuple]  # [(price, size), ...]
    
@dataclass
class TradeData:
    symbol: str
    timestamp: datetime
    price: float
    size: float
    side: str  # 'buy' or 'sell'

@dataclass
class ProcessedSignal:
    signal_id: str
    symbol: str
    signal_type: str
    strength: float
    confidence: float
    timestamp: datetime
    data: Dict[str, Any]

class HighFrequencyProcessor:
    """Ultra-low latency data processor for real-time trading."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        self.active_streams: Dict[str, bool] = {}
        self.data_buffer: Dict[str, queue.Queue] = {}
        self.processors: Dict[str, Callable] = {}
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Performance metrics
        self.metrics = {
            'processed_ticks': 0,
            'avg_latency_ms': 0,
            'max_latency_ms': 0,
            'last_update': datetime.now()
        }
        
        self.is_running = False
        
    async def initialize(self):
        """Initialize high-frequency processor."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize data buffers
            for stream_type in DataStreamType:
                self.data_buffer[stream_type.value] = queue.Queue(maxsize=10000)
                
            # Register default processors
            self.processors = {
                DataStreamType.TICK.value: self._process_tick_data,
                DataStreamType.BOOK.value: self._process_book_data,
                DataStreamType.TRADE.value: self._process_trade_data,
                DataStreamType.NEWS.value: self._process_news_data,
                DataStreamType.SENTIMENT.value: self._process_sentiment_data
            }
            
            logger.info("High-frequency processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing high-frequency processor: {e}")
            raise
    
    async def start_processing(self, symbols: List[str]):
        """Start high-frequency data processing for specified symbols."""
        try:
            if not self.redis_client:
                await self.initialize()
                
            self.is_running = True
            
            # Start data streams
            tasks = []
            for symbol in symbols:
                for stream_type in DataStreamType:
                    task = asyncio.create_task(
                        self._start_data_stream(symbol, stream_type)
                    )
                    tasks.append(task)
            
            # Start processing workers
            for i in range(5):  # 5 processing workers
                task = asyncio.create_task(self._processing_worker(f"worker_{i}"))
                tasks.append(task)
                
            # Start performance monitor
            tasks.append(asyncio.create_task(self._performance_monitor()))
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error starting high-frequency processing: {e}")
            self.is_running = False
            
    async def stop_processing(self):
        """Stop all processing."""
        self.is_running = False
        for stream_id in self.active_streams:
            self.active_streams[stream_id] = False
            
    async def _start_data_stream(self, symbol: str, stream_type: DataStreamType):
        """Start individual data stream."""
        stream_id = f"{symbol}_{stream_type.value}"
        self.active_streams[stream_id] = True
        
        try:
            if stream_type == DataStreamType.TICK:
                await self._stream_tick_data(symbol)
            elif stream_type == DataStreamType.BOOK:
                await self._stream_book_data(symbol)
            elif stream_type == DataStreamType.TRADE:
                await self._stream_trade_data(symbol)
            elif stream_type == DataStreamType.NEWS:
                await self._stream_news_data(symbol)
            elif stream_type == DataStreamType.SENTIMENT:
                await self._stream_sentiment_data(symbol)
                
        except Exception as e:
            logger.error(f"Error in data stream {stream_id}: {e}")
            
    async def _stream_tick_data(self, symbol: str):
        """Stream real-time tick data."""
        while self.active_streams.get(f"{symbol}_tick", False):
            try:
                # Simulate high-frequency tick data
                tick = TickData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    bid=1.1650 + np.random.normal(0, 0.0001),
                    ask=1.1652 + np.random.normal(0, 0.0001),
                    last=1.1651 + np.random.normal(0, 0.0001),
                    volume=np.random.randint(100, 1000),
                    spread=0.0002 + np.random.normal(0, 0.00005)
                )
                
                # Add to buffer
                if not self.data_buffer[DataStreamType.TICK.value].full():
                    self.data_buffer[DataStreamType.TICK.value].put({
                        'type': DataStreamType.TICK.value,
                        'data': asdict(tick)
                    })
                
                # Store in Redis stream
                await self.redis_client.xadd(
                    f"tick_stream:{symbol}",
                    asdict(tick),
                    maxlen=1000
                )
                
                # Ultra-low latency: 1ms delay
                await asyncio.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Error streaming tick data for {symbol}: {e}")
                await asyncio.sleep(0.1)
                
    async def _stream_book_data(self, symbol: str):
        """Stream order book data."""
        while self.active_streams.get(f"{symbol}_book", False):
            try:
                # Generate realistic order book
                mid_price = 1.1651
                bids = [(mid_price - i*0.0001, np.random.randint(100, 2000)) for i in range(1, 11)]
                asks = [(mid_price + i*0.0001, np.random.randint(100, 2000)) for i in range(1, 11)]
                
                book = OrderBookData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    bids=bids,
                    asks=asks
                )
                
                if not self.data_buffer[DataStreamType.BOOK.value].full():
                    self.data_buffer[DataStreamType.BOOK.value].put({
                        'type': DataStreamType.BOOK.value,
                        'data': asdict(book)
                    })
                
                await asyncio.sleep(0.01)  # 10ms book updates
                
            except Exception as e:
                logger.error(f"Error streaming book data for {symbol}: {e}")
                await asyncio.sleep(0.1)
                
    async def _stream_trade_data(self, symbol: str):
        """Stream trade execution data."""
        while self.active_streams.get(f"{symbol}_trade", False):
            try:
                if np.random.random() > 0.8:  # 20% chance of trade
                    trade = TradeData(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        price=1.1651 + np.random.normal(0, 0.0002),
                        size=np.random.randint(100, 5000),
                        side='buy' if np.random.random() > 0.5 else 'sell'
                    )
                    
                    if not self.data_buffer[DataStreamType.TRADE.value].full():
                        self.data_buffer[DataStreamType.TRADE.value].put({
                            'type': DataStreamType.TRADE.value,
                            'data': asdict(trade)
                        })
                
                await asyncio.sleep(0.05)  # 50ms trade updates
                
            except Exception as e:
                logger.error(f"Error streaming trade data for {symbol}: {e}")
                await asyncio.sleep(0.1)
                
    async def _stream_news_data(self, symbol: str):
        """Stream news sentiment data."""
        while self.active_streams.get(f"{symbol}_news", False):
            try:
                if np.random.random() > 0.95:  # 5% chance of news
                    news_data = {
                        'symbol': symbol,
                        'timestamp': datetime.now(),
                        'headline': f"Breaking: {symbol} market update",
                        'sentiment': np.random.choice(['positive', 'negative', 'neutral']),
                        'impact_score': np.random.uniform(0.1, 1.0),
                        'source': 'Market Wire'
                    }
                    
                    if not self.data_buffer[DataStreamType.NEWS.value].full():
                        self.data_buffer[DataStreamType.NEWS.value].put({
                            'type': DataStreamType.NEWS.value,
                            'data': news_data
                        })
                
                await asyncio.sleep(5.0)  # 5s news updates
                
            except Exception as e:
                logger.error(f"Error streaming news data for {symbol}: {e}")
                await asyncio.sleep(1.0)
                
    async def _stream_sentiment_data(self, symbol: str):
        """Stream social sentiment data."""
        while self.active_streams.get(f"{symbol}_sentiment", False):
            try:
                if np.random.random() > 0.9:  # 10% chance of sentiment update
                    sentiment_data = {
                        'symbol': symbol,
                        'timestamp': datetime.now(),
                        'social_score': np.random.uniform(0, 100),
                        'mentions': np.random.randint(10, 1000),
                        'positive_ratio': np.random.uniform(0.3, 0.8),
                        'sources': ['Twitter', 'Reddit', 'StockTwits']
                    }
                    
                    if not self.data_buffer[DataStreamType.SENTIMENT.value].full():
                        self.data_buffer[DataStreamType.SENTIMENT.value].put({
                            'type': DataStreamType.SENTIMENT.value,
                            'data': sentiment_data
                        })
                
                await asyncio.sleep(10.0)  # 10s sentiment updates
                
            except Exception as e:
                logger.error(f"Error streaming sentiment data for {symbol}: {e}")
                await asyncio.sleep(1.0)
    
    async def _processing_worker(self, worker_id: str):
        """High-frequency data processing worker."""
        while self.is_running:
            try:
                processed_any = False
                
                # Process data from all buffers
                for stream_type, buffer in self.data_buffer.items():
                    if not buffer.empty():
                        try:
                            data_item = buffer.get_nowait()
                            
                            # Record processing start time
                            start_time = time.perf_counter()
                            
                            # Process the data
                            processor = self.processors.get(stream_type)
                            if processor:
                                signal = await processor(data_item['data'])
                                if signal:
                                    await self._publish_signal(signal)
                            
                            # Calculate latency
                            end_time = time.perf_counter()
                            latency_ms = (end_time - start_time) * 1000
                            
                            # Update metrics
                            self.metrics['processed_ticks'] += 1
                            self.metrics['avg_latency_ms'] = (
                                (self.metrics['avg_latency_ms'] * (self.metrics['processed_ticks'] - 1) + latency_ms) /
                                self.metrics['processed_ticks']
                            )
                            self.metrics['max_latency_ms'] = max(self.metrics['max_latency_ms'], latency_ms)
                            
                            processed_any = True
                            
                        except queue.Empty:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing data in {worker_id}: {e}")
                
                # If no data processed, sleep briefly
                if not processed_any:
                    await asyncio.sleep(0.001)  # 1ms sleep
                    
            except Exception as e:
                logger.error(f"Error in processing worker {worker_id}: {e}")
                await asyncio.sleep(0.01)
    
    async def _process_tick_data(self, tick_data: Dict[str, Any]) -> Optional[ProcessedSignal]:
        """Process tick data and generate signals."""
        try:
            # Simple momentum signal
            current_price = tick_data['last']
            spread = tick_data['spread']
            
            # Generate signal based on spread and momentum
            if spread < 0.0001:  # Tight spread
                signal_strength = min(100, 70 + np.random.random() * 25)
                
                return ProcessedSignal(
                    signal_id=f"tick_{tick_data['symbol']}_{int(time.time() * 1000)}",
                    symbol=tick_data['symbol'],
                    signal_type="momentum",
                    strength=signal_strength,
                    confidence=0.8 + np.random.random() * 0.15,
                    timestamp=datetime.now(),
                    data={
                        'price': current_price,
                        'spread': spread,
                        'reasoning': 'Tight spread momentum signal'
                    }
                )
                
        except Exception as e:
            logger.error(f"Error processing tick data: {e}")
            
        return None
    
    async def _process_book_data(self, book_data: Dict[str, Any]) -> Optional[ProcessedSignal]:
        """Process order book data."""
        try:
            bids = book_data['bids']
            asks = book_data['asks']
            
            if len(bids) > 0 and len(asks) > 0:
                # Calculate book imbalance
                total_bid_size = sum(bid[1] for bid in bids[:5])  # Top 5 levels
                total_ask_size = sum(ask[1] for ask in asks[:5])  # Top 5 levels
                
                imbalance = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
                
                if abs(imbalance) > 0.3:  # Significant imbalance
                    return ProcessedSignal(
                        signal_id=f"book_{book_data['symbol']}_{int(time.time() * 1000)}",
                        symbol=book_data['symbol'],
                        signal_type="order_flow",
                        strength=min(100, 60 + abs(imbalance) * 100),
                        confidence=0.75 + abs(imbalance) * 0.2,
                        timestamp=datetime.now(),
                        data={
                            'imbalance': imbalance,
                            'direction': 'bullish' if imbalance > 0 else 'bearish',
                            'reasoning': f'Order book imbalance: {imbalance:.3f}'
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Error processing book data: {e}")
            
        return None
    
    async def _process_trade_data(self, trade_data: Dict[str, Any]) -> Optional[ProcessedSignal]:
        """Process trade execution data."""
        try:
            # Large trade detection
            if trade_data['size'] > 2000:  # Large trade
                return ProcessedSignal(
                    signal_id=f"trade_{trade_data['symbol']}_{int(time.time() * 1000)}",
                    symbol=trade_data['symbol'],
                    signal_type="large_trade",
                    strength=70 + (trade_data['size'] / 10000) * 30,
                    confidence=0.85,
                    timestamp=datetime.now(),
                    data={
                        'trade_size': trade_data['size'],
                        'trade_side': trade_data['side'],
                        'trade_price': trade_data['price'],
                        'reasoning': f"Large {trade_data['side']} trade detected"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error processing trade data: {e}")
            
        return None
    
    async def _process_news_data(self, news_data: Dict[str, Any]) -> Optional[ProcessedSignal]:
        """Process news sentiment data."""
        try:
            impact = news_data['impact_score']
            sentiment = news_data['sentiment']
            
            if impact > 0.7:  # High impact news
                signal_type = f"news_{sentiment}"
                strength = 50 + impact * 40
                
                return ProcessedSignal(
                    signal_id=f"news_{news_data['symbol']}_{int(time.time() * 1000)}",
                    symbol=news_data['symbol'],
                    signal_type=signal_type,
                    strength=strength,
                    confidence=impact,
                    timestamp=datetime.now(),
                    data={
                        'headline': news_data['headline'],
                        'sentiment': sentiment,
                        'impact_score': impact,
                        'reasoning': f"High impact {sentiment} news"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error processing news data: {e}")
            
        return None
    
    async def _process_sentiment_data(self, sentiment_data: Dict[str, Any]) -> Optional[ProcessedSignal]:
        """Process social sentiment data."""
        try:
            score = sentiment_data['social_score']
            mentions = sentiment_data['mentions']
            positive_ratio = sentiment_data['positive_ratio']
            
            if mentions > 500 and (score > 80 or score < 20):  # High activity + extreme sentiment
                direction = 'bullish' if score > 50 else 'bearish'
                
                return ProcessedSignal(
                    signal_id=f"sentiment_{sentiment_data['symbol']}_{int(time.time() * 1000)}",
                    symbol=sentiment_data['symbol'],
                    signal_type=f"social_{direction}",
                    strength=60 + abs(score - 50),
                    confidence=min(0.9, mentions / 1000),
                    timestamp=datetime.now(),
                    data={
                        'social_score': score,
                        'mentions': mentions,
                        'positive_ratio': positive_ratio,
                        'reasoning': f"High social activity with {direction} sentiment"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error processing sentiment data: {e}")
            
        return None
    
    async def _publish_signal(self, signal: ProcessedSignal):
        """Publish processed signal to subscribers."""
        try:
            signal_data = asdict(signal)
            signal_data['timestamp'] = signal.timestamp.isoformat()
            
            # Publish to Redis pub/sub
            await self.redis_client.publish(
                f"signals:{signal.symbol}",
                json.dumps(signal_data)
            )
            
            # Store in Redis stream for history
            await self.redis_client.xadd(
                f"signal_stream:{signal.symbol}",
                signal_data,
                maxlen=10000
            )
            
        except Exception as e:
            logger.error(f"Error publishing signal: {e}")
    
    async def _performance_monitor(self):
        """Monitor system performance."""
        while self.is_running:
            try:
                self.metrics['last_update'] = datetime.now()
                
                # Log performance metrics every 10 seconds
                logger.info(f"HF Processor Metrics: "
                          f"Ticks: {self.metrics['processed_ticks']}, "
                          f"Avg Latency: {self.metrics['avg_latency_ms']:.2f}ms, "
                          f"Max Latency: {self.metrics['max_latency_ms']:.2f}ms")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.metrics,
            'active_streams': len([s for s in self.active_streams.values() if s]),
            'buffer_sizes': {k: v.qsize() for k, v in self.data_buffer.items()},
            'is_running': self.is_running
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.stop_processing()
            
            if self.redis_client:
                await self.redis_client.close()
                
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 