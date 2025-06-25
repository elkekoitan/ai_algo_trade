"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Send, Repeat } from 'lucide-react';

interface TickData {
  time: string;
  bid: number;
  ask: number;
  last: number;
}

const QuickTrade = () => {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSD');
  const [tick, setTick] = useState<TickData | null>(null);
  const [volume, setVolume] = useState('0.01');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastOrder, setLastOrder] = useState<any>(null);

  // Fetch all available symbols on component mount
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const response = await axios.get('http://localhost:8001/api/v1/market/symbols');
        setSymbols(response.data);
      } catch (error) {
        console.error("Error fetching symbols:", error);
      }
    };
    fetchSymbols();
  }, []);

  // Fetch tick data for the selected symbol periodically
  useEffect(() => {
    if (!selectedSymbol) return;

    const fetchTick = async () => {
      try {
        const response = await axios.get(`http://localhost:8001/api/v1/market/tick/${selectedSymbol}`);
        setTick(response.data);
      } catch (error) {
        console.error(`Error fetching tick for ${selectedSymbol}:`, error);
        setTick(null);
      }
    };

    fetchTick();
    const interval = setInterval(fetchTick, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleTrade = async (orderType: 'BUY' | 'SELL') => {
    setIsSubmitting(true);
    setLastOrder(null);

    try {
      const response = await axios.post('http://localhost:8001/api/v1/trading/trade', {
        symbol: selectedSymbol,
        order_type: orderType,
        volume: parseFloat(volume),
        comment: `QuickTrade via ICT Ultra v2`
      });

      setLastOrder({ success: response.data.success, ...response.data });
    } catch (error: any) {
      console.error("Error placing trade:", error);
      const message = error.response?.data?.detail || 'Failed to place trade.';
      setLastOrder({ success: false, message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentPrice = tick?.ask ?? 0;
  const priceColor = tick && tick.last > 0 ? (tick.ask > tick.last ? 'text-green-400' : 'text-red-400') : 'text-white';

  return (
    <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl border border-gray-800 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Quick Trade</h3>
      
      {/* Symbol Selector */}
      <div className="mb-4">
        <label htmlFor="symbol-select" className="block text-sm font-medium text-gray-400 mb-2">Instrument</label>
        <select
          id="symbol-select"
          value={selectedSymbol}
          onChange={(e) => setSelectedSymbol(e.target.value)}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
        >
          {symbols.map((symbol) => (
            <option key={symbol} value={symbol}>{symbol}</option>
          ))}
        </select>
      </div>
      
      {/* Price Display */}
      <div className="text-center mb-4">
        <p className={`text-4xl font-bold transition-colors duration-300 ${priceColor}`}>
          {currentPrice > 0 ? currentPrice.toFixed(4) : 'Loading...'}
        </p>
        <p className="text-xs text-gray-500">{tick ? new Date(tick.time).toLocaleTimeString() : '...'}</p>
      </div>

      {/* Trade Controls */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Volume (Lots)</label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
            step="0.01"
            min="0.01"
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => handleTrade('BUY')}
            disabled={isSubmitting || !tick}
            className="w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white disabled:bg-gray-700 disabled:cursor-not-allowed"
          >
            <TrendingUp size={18} />
            <span>BUY</span>
          </button>
          <button
            onClick={() => handleTrade('SELL')}
            disabled={isSubmitting || !tick}
            className="w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-700 text-white disabled:bg-gray-700 disabled:cursor-not-allowed"
          >
            <TrendingDown size={18} />
            <span>SELL</span>
          </button>
        </div>
      </div>
      
      {/* Last Order Status */}
      {lastOrder && (
        <div className={`mt-4 p-3 rounded-lg text-sm ${
          lastOrder.success ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'
        }`}>
          <p><strong>{lastOrder.success ? 'Success' : 'Failed'}:</strong> {lastOrder.message}</p>
          {lastOrder.order_id && <p>Order ID: {lastOrder.order_id}</p>}
        </div>
      )}
    </div>
  );
};

export default QuickTrade; 