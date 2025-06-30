'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, TrendingUp, TrendingDown, Brain, Target, AlertTriangle, Bitcoin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';

interface Signal {
  symbol: string;
  signal_type: string;
  direction: 'BUY' | 'SELL';
  strength: number;
  confidence: number;
  entry_price: number;
  stop_loss?: number;
  take_profit?: number;
  timeframe: string;
  ai_analysis: string;
  timestamp: string;
}

interface ScanResult {
  symbol: string;
  signals: Signal[];
  overall_score: number;
  recommendation: string;
  price: number;
  change_percent: number;
  weekend_active?: boolean;
}

const fetcher = (url: string) => fetch(url).then(res => res.json());

const MarketScanner: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('H1');
  
  // Get market status and symbols
  const { data: statusData } = useSWR(API_ENDPOINTS.status, fetcher, { refreshInterval: 10000 });
  const { data: symbolsData } = useSWR(API_ENDPOINTS.symbols_active, fetcher, { refreshInterval: 30000 });

  const isWeekendMode = statusData?.weekend_mode || false;
  const mt5Connected = statusData?.mt5_connected || false;
  const availableSymbols = symbolsData?.symbols || [];
  const totalAvailable = symbolsData?.total_available || 0;

  const fetchScanResults = async () => {
    if (!mt5Connected || availableSymbols.length === 0) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Use all available active symbols (they already have tick data)
      const symbolsToScan = availableSymbols.slice(0, 15); // Limit to first 15 active symbols
      
      const results: ScanResult[] = symbolsToScan.map((symbolInfo: any) => {
        // Since these are active symbols, they already have current prices
        const currentPrice = symbolInfo.current_bid || symbolInfo.price || 0;
        
        // Generate mock signals for now (you can replace this with real signal API)
        const mockSignal: Signal = {
          symbol: symbolInfo.name,
          signal_type: 'ICT_ORDER_BLOCK',
          direction: Math.random() > 0.5 ? 'BUY' : 'SELL',
          strength: 70 + Math.random() * 30,
          confidence: 60 + Math.random() * 40,
          entry_price: currentPrice,
          timeframe: selectedTimeframe,
          ai_analysis: isWeekendMode ? 'Weekend crypto analysis shows strong momentum' : 'Strong institutional backing detected',
          timestamp: new Date().toISOString()
        };

        const confidence = mockSignal.confidence;
        let recommendation = 'HOLD';
        if (mockSignal.direction === 'BUY' && confidence > 75) recommendation = 'STRONG BUY';
        else if (mockSignal.direction === 'BUY' && confidence > 60) recommendation = 'BUY';
        else if (mockSignal.direction === 'SELL' && confidence > 75) recommendation = 'STRONG SELL';
        else if (mockSignal.direction === 'SELL' && confidence > 60) recommendation = 'SELL';

        return {
          symbol: symbolInfo.name,
          signals: [mockSignal],
          overall_score: confidence,
          recommendation,
          price: currentPrice,
          change_percent: (Math.random() - 0.5) * 4, // Mock change
          weekend_active: symbolInfo.weekend_active || symbolInfo.is_active || false
        };
      });

      setScanResults(results.sort((a, b) => b.overall_score - a.overall_score));
      
    } catch (err) {
      console.error('Market scan error:', err);
      setError('Failed to scan markets');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (mt5Connected && availableSymbols.length > 0) {
    fetchScanResults();
      const interval = setInterval(fetchScanResults, 60000); // Update every minute
    return () => clearInterval(interval);
    }
  }, [selectedTimeframe, mt5Connected, availableSymbols.length]);

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'STRONG BUY': return 'bg-green-600 text-white';
      case 'BUY': return 'bg-green-500/20 text-green-400';
      case 'STRONG SELL': return 'bg-red-600 text-white';
      case 'SELL': return 'bg-red-500/20 text-red-400';
      default: return 'bg-yellow-500/20 text-yellow-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const isCrypto = (symbol: string) => {
    return symbol.includes('BTC') || symbol.includes('ETH') || symbol.includes('LTC') || 
           symbol.includes('XRP') || symbol.includes('ADA') || symbol.endsWith('USD') && 
           !['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD'].includes(symbol);
  };

  if (!mt5Connected) {
    return (
      <Card className="w-full bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-cyan-400" />
            AI Market Scanner
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-3" />
            <p className="text-red-400 mb-2">MT5 Not Connected</p>
            <p className="text-gray-400 text-sm">Scanner requires active MT5 connection</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full bg-gray-900/50 border-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {isWeekendMode ? (
              <Bitcoin className="h-5 w-5 text-orange-400" />
            ) : (
            <Brain className="h-5 w-5 text-cyan-400" />
            )}
            AI Market Scanner
            {isWeekendMode && (
              <Badge className="bg-orange-500/20 text-orange-400 text-xs">
                Weekend Crypto Mode
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-3">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="bg-gray-800 text-white border border-gray-700 rounded px-2 py-1 text-sm"
            >
              <option value="M15">15m</option>
              <option value="H1">1h</option>
              <option value="H4">4h</option>
              <option value="D1">1d</option>
            </select>
            <button
              onClick={fetchScanResults}
              disabled={isLoading}
              className="p-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 text-white ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-400">
          Last scan: {new Date().toLocaleTimeString()} • {scanResults.length} symbols analyzed
          {isWeekendMode && <span className="text-orange-400"> • Crypto only</span>}
          {totalAvailable > 0 && (
            <span className="text-gray-500"> • {totalAvailable} total available</span>
          )}
        </p>
      </CardHeader>
      
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-800/50 rounded-lg flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-400" />
            <span className="text-yellow-400 text-sm">{error}</span>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <RefreshCw className="h-8 w-8 animate-spin text-cyan-400" />
            <span className="ml-3 text-gray-400">
              Scanning {availableSymbols.length} active {isWeekendMode ? 'crypto ' : ''}symbols...
              {totalAvailable > availableSymbols.length && (
                <span className="text-gray-500"> ({totalAvailable} total)</span>
              )}
            </span>
          </div>
        ) : (
          <div className="space-y-3">
            {scanResults.map((result, index) => (
              <motion.div
                key={result.symbol}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-cyan-500/30 transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-white text-lg flex items-center gap-2">
                      {result.symbol}
                      {isCrypto(result.symbol) && (
                        <Bitcoin className="h-4 w-4 text-orange-400" />
                      )}
                      {result.weekend_active && (
                        <Badge className="bg-green-500/20 text-green-400 text-xs">
                          Active
                        </Badge>
                      )}
                    </span>
                    <Badge className={getRecommendationColor(result.recommendation)}>
                      {result.recommendation}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-white">
                      {result.price > 100 ? result.price.toFixed(2) : result.price.toFixed(5)}
                    </p>
                    <p className={`text-sm ${result.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {result.change_percent >= 0 ? '+' : ''}{result.change_percent.toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div className="text-center">
                    <p className="text-xs text-gray-400">AI Score</p>
                    <p className={`font-bold ${getScoreColor(result.overall_score)}`}>
                      {result.overall_score.toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-400">Signals</p>
                    <p className="font-bold text-white">{result.signals.length}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-400">Direction</p>
                    <div className="flex justify-center">
                      {result.signals.some(s => s.direction === 'BUY') && (
                        <TrendingUp className="h-4 w-4 text-green-400" />
                      )}
                      {result.signals.some(s => s.direction === 'SELL') && (
                        <TrendingDown className="h-4 w-4 text-red-400" />
                      )}
                    </div>
                  </div>
                </div>

                {result.signals.length > 0 && (
                  <div className="text-xs text-gray-400">
                    Latest: {result.signals[0]?.signal_type?.replace(/_/g, ' ')} • 
                    Confidence: {result.signals[0]?.confidence?.toFixed(0)}%
                    {isWeekendMode && ' • Weekend Crypto Analysis'}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MarketScanner; 