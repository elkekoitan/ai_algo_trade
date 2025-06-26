'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  RefreshCw,
  Settings,
  Eye,
  Play,
  Pause,
  Star,
  Activity,
  DollarSign
} from 'lucide-react';

interface MarketOpportunity {
  id: string;
  symbol: string;
  timeframe: string;
  signal_type: string;
  direction: 'bullish' | 'bearish';
  strength: number;
  confidence: number;
  entry_price: number;
  sl_price: number;
  tp_price: number;
  risk_reward: number;
  timestamp: string;
  status: 'active' | 'pending' | 'expired';
  market_structure: string;
  volume_confirmation: boolean;
  price_action_score: number;
}

interface MarketOverview {
  symbol: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  volatility: number;
  trend: 'bullish' | 'bearish' | 'sideways';
  signals_count: number;
  last_signal: string;
  market_session: string;
}

interface ScannerFilters {
  symbols: string[];
  timeframes: string[];
  signalTypes: string[];
  minStrength: number;
  minConfidence: number;
  minRiskReward: number;
  trends: string[];
  sessions: string[];
}

const MarketScanner: React.FC = () => {
  // State management
  const [opportunities, setOpportunities] = useState<MarketOpportunity[]>([]);
  const [marketOverview, setMarketOverview] = useState<MarketOverview[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(true);
  const [lastScan, setLastScan] = useState<Date>(new Date());
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(null);
  
  // Filters
  const [filters, setFilters] = useState<ScannerFilters>({
    symbols: ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'US30'],
    timeframes: ['M15', 'M30', 'H1', 'H4'],
    signalTypes: ['order_block', 'fair_value_gap', 'breaker_block'],
    minStrength: 70,
    minConfidence: 75,
    minRiskReward: 1.5,
    trends: ['bullish', 'bearish'],
    sessions: ['london', 'new_york', 'asian']
  });

  const [showFilters, setShowFilters] = useState(false);

  // Available options
  const availableSymbols = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    'XAUUSD', 'XAGUSD', 'BTCUSD', 'ETHUSD', 'US30', 'NAS100', 'SPX500', 'GER40'
  ];

  const timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'];
  const signalTypes = ['order_block', 'fair_value_gap', 'breaker_block', 'liquidity_sweep', 'imbalance'];

  // Fetch market opportunities
  const fetchOpportunities = useCallback(async () => {
    try {
      const queryParams = new URLSearchParams({
        symbols: filters.symbols.join(','),
        timeframes: filters.timeframes.join(','),
        signal_types: filters.signalTypes.join(','),
        min_strength: filters.minStrength.toString(),
        min_confidence: filters.minConfidence.toString(),
        min_risk_reward: filters.minRiskReward.toString()
      });

      const response = await fetch(`/api/v1/scanner/opportunities?${queryParams}`);
      if (response.ok) {
        const data = await response.json();
        setOpportunities(data.opportunities || []);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    }
  }, [filters]);

  // Fetch market overview
  const fetchMarketOverview = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/scanner/overview?symbols=${filters.symbols.join(',')}`);
      if (response.ok) {
        const data = await response.json();
        setMarketOverview(data.overview || []);
      }
    } catch (error) {
      console.error('Error fetching market overview:', error);
    }
  }, [filters.symbols]);

  // Auto-scan functionality
  useEffect(() => {
    if (!isScanning) return;

    const interval = setInterval(() => {
      fetchOpportunities();
      fetchMarketOverview();
      setLastScan(new Date());
    }, 30000); // Scan every 30 seconds

    return () => clearInterval(interval);
  }, [isScanning, fetchOpportunities, fetchMarketOverview]);

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true);
      await Promise.all([fetchOpportunities(), fetchMarketOverview()]);
      setIsLoading(false);
    };

    loadInitialData();
  }, [fetchOpportunities, fetchMarketOverview]);

  // Utility functions
  const getSignalColor = (type: string) => {
    const colors = {
      order_block: 'bg-blue-500',
      fair_value_gap: 'bg-purple-500',
      breaker_block: 'bg-orange-500',
      liquidity_sweep: 'bg-green-500',
      imbalance: 'bg-red-500'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-500';
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 90) return 'text-green-600';
    if (strength >= 80) return 'text-blue-600';
    if (strength >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'bullish': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'bearish': return <TrendingDown className="h-4 w-4 text-red-600" />;
      default: return <BarChart3 className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatPrice = (price: number, symbol: string) => {
    const decimals = symbol.includes('JPY') ? 3 : 5;
    return price.toFixed(decimals);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const handleManualScan = async () => {
    setIsLoading(true);
    await Promise.all([fetchOpportunities(), fetchMarketOverview()]);
    setIsLoading(false);
    setLastScan(new Date());
  };

  const handleToggleScanning = () => {
    setIsScanning(!isScanning);
  };

  const handleFilterChange = (filterType: keyof ScannerFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const filteredOpportunities = opportunities.filter(opp => {
    return opp.strength >= filters.minStrength &&
           opp.confidence >= filters.minConfidence &&
           opp.risk_reward >= filters.minRiskReward &&
           filters.trends.includes(opp.direction);
  });

  if (isLoading && opportunities.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-medium mb-2">Scanning Markets</h3>
            <p className="text-sm text-gray-600">Analyzing opportunities across {filters.symbols.length} symbols...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Scanner Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Market Scanner
              <Badge variant={isScanning ? 'default' : 'outline'}>
                {isScanning ? 'Scanning' : 'Paused'}
              </Badge>
            </CardTitle>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-1" />
                Filters
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualScan}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                Scan
              </Button>
              <Button
                variant={isScanning ? 'destructive' : 'default'}
                size="sm"
                onClick={handleToggleScanning}
              >
                {isScanning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* Scanner Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {filteredOpportunities.length}
              </div>
              <div className="text-sm text-gray-600">Active Opportunities</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {filteredOpportunities.filter(o => o.direction === 'bullish').length}
              </div>
              <div className="text-sm text-gray-600">Bullish Signals</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {filteredOpportunities.filter(o => o.direction === 'bearish').length}
              </div>
              <div className="text-sm text-gray-600">Bearish Signals</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {filters.symbols.length}
              </div>
              <div className="text-sm text-gray-600">Symbols Monitored</div>
            </div>
          </div>

          {/* Last Scan Info */}
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Last scan: {lastScan.toLocaleTimeString()}</span>
            <span>Next scan: {isScanning ? 'in 30s' : 'Manual'}</span>
          </div>
        </CardHeader>

        {/* Filters Panel */}
        {showFilters && (
          <CardContent className="border-t">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Symbol Selection */}
              <div>
                <label className="text-sm font-medium mb-2 block">Symbols</label>
                <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
                  {availableSymbols.map(symbol => (
                    <label key={symbol} className="flex items-center gap-2 text-xs">
                      <input
                        type="checkbox"
                        checked={filters.symbols.includes(symbol)}
                        onChange={(e) => {
                          const newSymbols = e.target.checked
                            ? [...filters.symbols, symbol]
                            : filters.symbols.filter(s => s !== symbol);
                          handleFilterChange('symbols', newSymbols);
                        }}
                        className="rounded"
                      />
                      {symbol}
                    </label>
                  ))}
                </div>
              </div>

              {/* Timeframes */}
              <div>
                <label className="text-sm font-medium mb-2 block">Timeframes</label>
                <div className="grid grid-cols-2 gap-1">
                  {timeframes.map(tf => (
                    <label key={tf} className="flex items-center gap-2 text-xs">
                      <input
                        type="checkbox"
                        checked={filters.timeframes.includes(tf)}
                        onChange={(e) => {
                          const newTimeframes = e.target.checked
                            ? [...filters.timeframes, tf]
                            : filters.timeframes.filter(t => t !== tf);
                          handleFilterChange('timeframes', newTimeframes);
                        }}
                        className="rounded"
                      />
                      {tf}
                    </label>
                  ))}
                </div>
              </div>

              {/* Thresholds */}
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium mb-1 block">
                    Min Strength: {filters.minStrength}%
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="100"
                    value={filters.minStrength}
                    onChange={(e) => handleFilterChange('minStrength', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">
                    Min Confidence: {filters.minConfidence}%
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="100"
                    value={filters.minConfidence}
                    onChange={(e) => handleFilterChange('minConfidence', parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">
                    Min Risk/Reward: {filters.minRiskReward}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="0.1"
                    value={filters.minRiskReward}
                    onChange={(e) => handleFilterChange('minRiskReward', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Market Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Market Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {marketOverview.map((market) => (
              <div key={market.symbol} className="border rounded-lg p-3 hover:bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{market.symbol}</span>
                    {getTrendIcon(market.trend)}
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {market.signals_count} signals
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">Price:</span>
                    <div className="font-medium">{formatPrice(market.price, market.symbol)}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Change:</span>
                    <div className={`font-medium ${market.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {market.change_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>
                
                <div className="text-xs text-gray-500 mt-2">
                  Last signal: {market.last_signal || 'None'}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Opportunities List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Trading Opportunities
            <Badge variant="outline">
              {filteredOpportunities.length} found
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredOpportunities.length > 0 ? (
            <div className="space-y-3">
              {filteredOpportunities.slice(0, 20).map((opportunity) => (
                <div
                  key={opportunity.id}
                  className={`border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                    selectedOpportunity === opportunity.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => setSelectedOpportunity(
                    selectedOpportunity === opportunity.id ? null : opportunity.id
                  )}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-lg">{opportunity.symbol}</span>
                        <Badge variant="outline" className="text-xs">
                          {opportunity.timeframe}
                        </Badge>
                      </div>
                      
                      <Badge className={getSignalColor(opportunity.signal_type)}>
                        {opportunity.signal_type.replace('_', ' ').toUpperCase()}
                      </Badge>
                      
                      <Badge variant={opportunity.direction === 'bullish' ? 'default' : 'destructive'}>
                        {opportunity.direction === 'bullish' ? '🔼 BULL' : '🔽 BEAR'}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className={`text-sm font-medium ${getStrengthColor(opportunity.strength)}`}>
                          Strength: {opportunity.strength}%
                        </div>
                        <div className="text-xs text-gray-600">
                          Confidence: {opportunity.confidence}%
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">
                          R/R: {opportunity.risk_reward.toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-600">
                          {formatTime(opportunity.timestamp)}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Entry:</span>
                      <div className="font-medium">{formatPrice(opportunity.entry_price, opportunity.symbol)}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Stop Loss:</span>
                      <div className="font-medium text-red-600">{formatPrice(opportunity.sl_price, opportunity.symbol)}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Take Profit:</span>
                      <div className="font-medium text-green-600">{formatPrice(opportunity.tp_price, opportunity.symbol)}</div>
                    </div>
                  </div>

                  {selectedOpportunity === opportunity.id && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Market Structure:</span>
                          <div className="font-medium">{opportunity.market_structure}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Volume Confirmation:</span>
                          <div className={`font-medium ${opportunity.volume_confirmation ? 'text-green-600' : 'text-red-600'}`}>
                            {opportunity.volume_confirmation ? 'Confirmed' : 'Pending'}
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-600">Price Action Score:</span>
                          <div className={`font-medium ${getStrengthColor(opportunity.price_action_score)}`}>
                            {opportunity.price_action_score}%
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-600">Status:</span>
                          <Badge variant={opportunity.status === 'active' ? 'default' : 'outline'}>
                            {opportunity.status}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 mt-4">
                        <Button size="sm" className="flex-1">
                          <DollarSign className="h-3 w-3 mr-1" />
                          Trade Now
                        </Button>
                        <Button variant="outline" size="sm">
                          <Star className="h-3 w-3 mr-1" />
                          Watch
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-3 w-3 mr-1" />
                          Chart
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Target className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium mb-2">No Opportunities Found</h3>
              <p className="text-sm">
                Try adjusting your filters or wait for new market conditions.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MarketScanner; 