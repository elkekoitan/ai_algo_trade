'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Brain, 
  Eye, 
  Shield, 
  Zap, 
  MessageSquare,
  RefreshCw,
  AlertTriangle,
  Cpu,
  Server,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';

interface ModuleMetrics {
  shadow_mode: {
    active: boolean;
    whale_detected: boolean;
    last_whale_volume: number;
    institutional_sentiment: string;
    dark_pool_activity: number;
  };
  god_mode: {
    active: boolean;
    prediction_confidence: number;
    market_direction: string;
    quantum_probability: number;
    next_move_prediction: string;
  };
  market_narrator: {
    active: boolean;
    current_story: string;
    market_sentiment: string;
    influence_score: number;
    narrative_confidence: number;
  };
  adaptive_tm: {
    active: boolean;
    risk_level: string;
    portfolio_exposure: number;
    active_positions: number;
    profit_factor: number;
  };
  strategy_whisperer: {
    active: boolean;
    active_strategies: number;
    total_backtests: number;
    best_strategy_performance: number;
    generated_signals: number;
  };
}

interface SystemHealth {
  mt5_connection: boolean;
  api_latency: number;
  data_freshness: number;
  system_load: number;
  error_count: number;
}

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const RealTimeMetrics: React.FC = () => {
  const { data, error } = useSWR(API_ENDPOINTS.health, fetcher, { refreshInterval: 2000 });

  const metrics = data?.performance || {};
  const apiLatency = metrics.avg_response_time?.toFixed(0) || 'N/A';
  const reqPerMin = metrics.trades_per_minute?.toFixed(1) || 0; // Assuming trades_per_minute is a good proxy for requests
  const errorRate = (metrics.failed_trades / (metrics.successful_trades + metrics.failed_trades + 1) * 100).toFixed(1) || 0;

  const [metricsData, setMetricsData] = useState<ModuleMetrics | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchMetrics = async () => {
    try {
      const [metricsRes, healthRes] = await Promise.all([
        fetch('http://localhost:8002/api/system/module-metrics'),
        fetch('http://localhost:8002/api/system/health')
      ]);

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetricsData(metricsData);
      }

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setSystemHealth(healthData);
      }

      setLastUpdate(new Date());
    } catch (err) {
      console.error('Metrics fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (value: number, reverse: boolean = false) => {
    if (reverse) {
      if (value > 80) return 'text-red-400';
      if (value > 50) return 'text-yellow-400';
      return 'text-green-400';
    } else {
      if (value > 80) return 'text-green-400';
      if (value > 50) return 'text-yellow-400';
      return 'text-red-400';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'text-green-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'HIGH': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-gray-900/50 border-gray-800">
        <CardContent className="flex items-center justify-center h-32">
          <RefreshCw className="h-8 w-8 animate-spin text-cyan-400" />
          <span className="ml-3 text-gray-400">Loading system metrics...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* System Health Overview */}
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-cyan-400" />
              System Health
            </span>
            <span className="text-xs text-gray-400">
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-800/50 rounded-lg flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
              <span className="text-yellow-400 text-sm">{error}</span>
            </div>
          )}
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <p className="text-xs text-gray-400">MT5 Connection</p>
              <div className={`text-lg font-bold ${systemHealth?.mt5_connection ? 'text-green-400' : 'text-red-400'}`}>
                {systemHealth?.mt5_connection ? '✓' : '✗'}
              </div>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">API Latency</p>
              <p className="text-lg font-bold text-white">
                {apiLatency} ms
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Data Age</p>
              <p className="text-lg font-bold text-white">
                {systemHealth?.data_freshness?.toFixed(1)}s
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">System Load</p>
              <p className={`text-lg font-bold ${getHealthColor(systemHealth?.system_load || 0, true)}`}>
                {systemHealth?.system_load?.toFixed(0)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Errors</p>
              <p className={`text-lg font-bold ${systemHealth?.error_count === 0 ? 'text-green-400' : 'text-red-400'}`}>
                {systemHealth?.error_count || 0}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Module Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Shadow Mode */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-purple-400" />
              Shadow Mode
              <Badge className={metricsData?.shadow_mode.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                {metricsData?.shadow_mode.active ? 'ACTIVE' : 'INACTIVE'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Whale Activity</span>
              <span className={metricsData?.shadow_mode.whale_detected ? 'text-red-400' : 'text-green-400'}>
                {metricsData?.shadow_mode.whale_detected ? 'DETECTED' : 'CLEAR'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Last Volume</span>
              <span className="text-white">${metricsData?.shadow_mode.last_whale_volume?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sentiment</span>
              <span className="text-white">{metricsData?.shadow_mode.institutional_sentiment}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Dark Pool</span>
              <span className="text-white">{metricsData?.shadow_mode.dark_pool_activity?.toFixed(1)}%</span>
            </div>
          </CardContent>
        </Card>

        {/* God Mode */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-cyan-400" />
              God Mode
              <Badge className={metricsData?.god_mode.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                {metricsData?.god_mode.active ? 'ACTIVE' : 'INACTIVE'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Confidence</span>
              <span className={`${getHealthColor(metricsData?.god_mode.prediction_confidence || 0)}`}>
                {metricsData?.god_mode.prediction_confidence?.toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Direction</span>
              <span className="text-white">{metricsData?.god_mode.market_direction}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Quantum Prob</span>
              <span className="text-white">{metricsData?.god_mode.quantum_probability?.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Next Move</span>
              <span className="text-white">{metricsData?.god_mode.next_move_prediction}</span>
            </div>
          </CardContent>
        </Card>

        {/* Market Narrator */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-yellow-400" />
              Market Narrator
              <Badge className={metricsData?.market_narrator.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                {metricsData?.market_narrator.active ? 'ACTIVE' : 'INACTIVE'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm text-gray-300">
              "{metricsData?.market_narrator.current_story}"
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sentiment</span>
              <span className="text-white">{metricsData?.market_narrator.market_sentiment}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Influence</span>
              <span className="text-white">{metricsData?.market_narrator.influence_score?.toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Confidence</span>
              <span className={`${getHealthColor(metricsData?.market_narrator.narrative_confidence || 0)}`}>
                {metricsData?.market_narrator.narrative_confidence?.toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Adaptive Trade Manager */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-400" />
              Adaptive TM
              <Badge className={metricsData?.adaptive_tm.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                {metricsData?.adaptive_tm.active ? 'ACTIVE' : 'INACTIVE'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Risk Level</span>
              <span className={`${getRiskColor(metricsData?.adaptive_tm.risk_level || '')}`}>
                {metricsData?.adaptive_tm.risk_level}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Exposure</span>
              <span className="text-white">{metricsData?.adaptive_tm.portfolio_exposure?.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Positions</span>
              <span className="text-white">{metricsData?.adaptive_tm.active_positions}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Profit Factor</span>
              <span className={`${metricsData?.adaptive_tm.profit_factor && metricsData.adaptive_tm.profit_factor > 1 ? 'text-green-400' : 'text-red-400'}`}>
                {metricsData?.adaptive_tm.profit_factor?.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Strategy Whisperer */}
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-400" />
            Strategy Whisperer
            <Badge className={metricsData?.strategy_whisperer.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
              {metricsData?.strategy_whisperer.active ? 'ACTIVE' : 'INACTIVE'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-xs text-gray-400">Active Strategies</p>
              <p className="text-lg font-bold text-white">{metricsData?.strategy_whisperer.active_strategies}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Backtests</p>
              <p className="text-lg font-bold text-white">{metricsData?.strategy_whisperer.total_backtests}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Best Performance</p>
              <p className="text-lg font-bold text-green-400">
                +{metricsData?.strategy_whisperer.best_strategy_performance?.toFixed(1)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Signals</p>
              <p className="text-lg font-bold text-white">{metricsData?.strategy_whisperer.generated_signals}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Performance Metrics</CardTitle>
          <Zap className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground">API Latency</p>
              <p className="text-lg font-bold">{apiLatency} ms</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Requests/min</p>
              <p className="text-lg font-bold">{reqPerMin}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Error Rate</p>
              <p className="text-lg font-bold">{errorRate}%</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Active Conns.</p>
              <p className="text-lg font-bold">1</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RealTimeMetrics; 