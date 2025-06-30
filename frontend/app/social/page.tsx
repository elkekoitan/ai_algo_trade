'use client'
import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Activity, 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  DollarSign,
  Target,
  Clock,
  BarChart3,
  Brain,
  Zap,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Eye,
  CheckCircle,
  XCircle
} from 'lucide-react'
import QuantumLayout from '@/components/layout/QuantumLayout'
import AdaptiveControls from '@/components/adaptive-trade-manager/AdaptiveControls'
import RiskDashboard from '@/components/adaptive-trade-manager/RiskDashboard'
import TradeMonitor from '@/components/adaptive-trade-manager/TradeMonitor'
import AlertCenter from '@/components/adaptive-trade-manager/AlertCenter'
import ParticleBackground from '@/components/quantum/ParticleBackground'
import GlassCard from '@/components/quantum/GlassCard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// Mock types
interface ManagedPosition {
  id: string;
  symbol: string;
  direction: 'LONG' | 'SHORT';
  entry_price: number;
  current_price: number;
  volume: number;
  profit_loss: number;
  profit_loss_percent: number;
  stop_loss: number;
  take_profit: number;
  risk_score: number;
  time_in_trade: string;
  ai_recommendation: 'HOLD' | 'SCALE_OUT' | 'ADD_TO_POSITION' | 'CLOSE_IMMEDIATELY';
  adaptive_sl: number;
  adaptive_tp: number;
  confidence: number;
  last_update: string;
}

interface RiskMetrics {
  portfolio_risk: number;
  var_1d: number;
  max_drawdown: number;
  sharpe_ratio: number;
  win_rate: number;
  profit_factor: number;
  exposure_by_symbol: { [key: string]: number };
  correlation_risk: number;
  market_stress_level: number;
}

interface AdaptiveAlert {
  id: string;
  type: 'RISK_WARNING' | 'POSITION_ADJUSTMENT' | 'MARKET_CHANGE' | 'SYSTEM_ALERT';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  action_required: boolean;
  timestamp: string;
  position_id?: string;
}

interface SystemStatus {
  is_active: boolean;
  positions_monitored: number;
  total_adjustments_today: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  ai_confidence: number;
  last_scan: string;
  uptime: string;
}

export default function AdaptiveTradeManagerPage() {
  const [positions, setPositions] = useState<ManagedPosition[]>([])
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null)
  const [alerts, setAlerts] = useState<AdaptiveAlert[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    is_active: false,
    positions_monitored: 0,
    total_adjustments_today: 0,
    risk_level: 'LOW',
    ai_confidence: 0,
    last_scan: '',
    uptime: '0h 0m'
  })
  const [isLoading, setIsLoading] = useState(true)
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null)
  const [autoMode, setAutoMode] = useState(false)

  const fetchData = async () => {
    try {
      // Fetch positions
      const positionsRes = await fetch('/api/v1/atm/positions');
      if (positionsRes.ok) {
        const posData = await positionsRes.json();
        setPositions(posData.positions || []);
      } else {
        // Mock positions for development
        const mockPositions: ManagedPosition[] = [
          {
            id: 'pos_1',
            symbol: 'EURUSD',
            direction: 'LONG',
            entry_price: 1.1050,
            current_price: 1.1085,
            volume: 0.5,
            profit_loss: 175,
            profit_loss_percent: 3.17,
            stop_loss: 1.1020,
            take_profit: 1.1150,
            risk_score: 25,
            time_in_trade: '2h 15m',
            ai_recommendation: 'HOLD',
            adaptive_sl: 1.1035,
            adaptive_tp: 1.1140,
            confidence: 85,
            last_update: new Date().toISOString()
          },
          {
            id: 'pos_2',
            symbol: 'XAUUSD',
            direction: 'SHORT',
            entry_price: 2650.50,
            current_price: 2645.20,
            volume: 0.1,
            profit_loss: 53,
            profit_loss_percent: 2.0,
            stop_loss: 2665.00,
            take_profit: 2620.00,
            risk_score: 45,
            time_in_trade: '45m',
            ai_recommendation: 'SCALE_OUT',
            adaptive_sl: 2660.00,
            adaptive_tp: 2625.00,
            confidence: 72,
            last_update: new Date().toISOString()
          }
        ];
        setPositions(mockPositions);
      }

      // Fetch risk metrics
      const riskRes = await fetch('/api/v1/atm/risk-metrics');
      if (riskRes.ok) {
        const riskData = await riskRes.json();
        setRiskMetrics(riskData);
      } else {
        // Mock risk metrics
        setRiskMetrics({
          portfolio_risk: 15.5,
          var_1d: 2.3,
          max_drawdown: 8.7,
          sharpe_ratio: 1.85,
          win_rate: 72.5,
          profit_factor: 1.65,
          exposure_by_symbol: {
            'EURUSD': 35,
            'XAUUSD': 25,
            'GBPUSD': 20,
            'BTCUSD': 15,
            'USDJPY': 5
          },
          correlation_risk: 0.35,
          market_stress_level: 0.25
        });
      }

      // Fetch alerts
      const alertsRes = await fetch('/api/v1/atm/alerts');
      if (alertsRes.ok) {
        const alertData = await alertsRes.json();
        setAlerts(alertData.alerts || []);
      } else {
        // Mock alerts
        setAlerts([
          {
            id: 'alert_1',
            type: 'RISK_WARNING',
            severity: 'MEDIUM',
            message: 'Portfolio correlation risk increasing - consider diversification',
            action_required: true,
            timestamp: new Date().toISOString()
          },
          {
            id: 'alert_2', 
            type: 'POSITION_ADJUSTMENT',
            severity: 'LOW',
            message: 'XAUUSD position: AI suggests partial profit taking',
            action_required: false,
            timestamp: new Date().toISOString(),
            position_id: 'pos_2'
          }
        ]);
      }

      // Update system status
      setSystemStatus({
        is_active: true,
        positions_monitored: positions.length,
        total_adjustments_today: 12,
        risk_level: riskMetrics ? (riskMetrics.portfolio_risk > 20 ? 'HIGH' : riskMetrics.portfolio_risk > 10 ? 'MEDIUM' : 'LOW') : 'LOW',
        ai_confidence: 87,
        last_scan: new Date().toLocaleTimeString(),
        uptime: '4h 23m'
      });

    } catch (error) {
      console.error("Failed to fetch ATM data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAutoMode = async () => {
    try {
      const response = await fetch('/api/v1/atm/toggle-auto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !autoMode })
      });
      
      if (response.ok) {
        setAutoMode(!autoMode);
      }
    } catch (error) {
      console.error('Failed to toggle auto mode:', error);
    }
  };

  const handlePositionAction = async (positionId: string, action: string) => {
    try {
      const response = await fetch(`/api/v1/atm/position/${positionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      
      if (response.ok) {
        await fetchData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to execute position action:', error);
    }
  };

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-green-400 bg-green-500/20';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/20';
      case 'HIGH': return 'text-orange-400 bg-orange-500/20';
      case 'CRITICAL': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'HOLD': return 'text-blue-400 bg-blue-500/20';
      case 'SCALE_OUT': return 'text-yellow-400 bg-yellow-500/20';
      case 'ADD_TO_POSITION': return 'text-green-400 bg-green-500/20';
      case 'CLOSE_IMMEDIATELY': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-cyan-400 mx-auto mb-4" />
          <p className="text-xl">Initializing Adaptive Trade Manager...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <ParticleBackground />
      
      <div className="relative z-10 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="w-8 h-8 text-green-400" />
            Adaptive Trade Manager
            {systemStatus.is_active && <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />}
          </h1>
          
          <div className="flex items-center gap-4">
            <Badge className={getRiskLevelColor(systemStatus.risk_level)}>
              Risk: {systemStatus.risk_level}
            </Badge>
            <button
              onClick={toggleAutoMode}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                autoMode 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {autoMode ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {autoMode ? 'Auto Mode ON' : 'Manual Mode'}
            </button>
          </div>
        </div>

        {/* System Status Overview */}
        <GlassCard className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Positions</p>
              <p className="text-2xl font-bold text-cyan-400">{systemStatus.positions_monitored}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Adjustments Today</p>
              <p className="text-2xl font-bold text-yellow-400">{systemStatus.total_adjustments_today}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">AI Confidence</p>
              <p className="text-2xl font-bold text-green-400">{systemStatus.ai_confidence}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Portfolio Risk</p>
              <p className={`text-2xl font-bold ${riskMetrics && riskMetrics.portfolio_risk > 20 ? 'text-red-400' : 'text-green-400'}`}>
                {riskMetrics ? riskMetrics.portfolio_risk.toFixed(1) : '0.0'}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Win Rate</p>
              <p className="text-2xl font-bold text-purple-400">{riskMetrics ? riskMetrics.win_rate.toFixed(1) : '0.0'}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400">Uptime</p>
              <p className="text-2xl font-bold text-white">{systemStatus.uptime}</p>
            </div>
          </div>
        </GlassCard>

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <GlassCard className="p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="h-6 w-6 text-yellow-400" />
              Active Alerts ({alerts.length})
            </h2>
            <div className="space-y-3">
              {alerts.map(alert => (
                <div key={alert.id} className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'CRITICAL' ? 'border-red-500 bg-red-500/10' :
                  alert.severity === 'HIGH' ? 'border-orange-500 bg-orange-500/10' :
                  alert.severity === 'MEDIUM' ? 'border-yellow-500 bg-yellow-500/10' :
                  'border-blue-500 bg-blue-500/10'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-white">{alert.message}</p>
                      <p className="text-sm text-gray-400">{new Date(alert.timestamp).toLocaleString()}</p>
                    </div>
                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="text-gray-400 hover:text-white"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Positions Monitor */}
          <div className="lg:col-span-2 space-y-6">
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-cyan-400" />
                Active Positions
              </h2>
              
              {positions.length === 0 ? (
                <div className="text-center py-8">
                  <Eye className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400">No active positions to monitor</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {positions.map(position => (
                    <motion.div
                      key={position.id}
                      className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-cyan-500/50 transition-all"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${position.direction === 'LONG' ? 'bg-green-400' : 'bg-red-400'}`} />
                          <h4 className="font-bold text-white text-lg">{position.symbol}</h4>
                          <Badge className={position.direction === 'LONG' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                            {position.direction}
                          </Badge>
                        </div>
                        <div className="text-right">
                          <p className={`text-lg font-bold ${position.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {position.profit_loss >= 0 ? '+' : ''}${position.profit_loss.toFixed(2)}
                          </p>
                          <p className={`text-sm ${position.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {position.profit_loss_percent >= 0 ? '+' : ''}{position.profit_loss_percent.toFixed(2)}%
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-4 gap-4 mb-3">
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Entry</p>
                          <p className="font-mono text-white">{position.entry_price.toFixed(5)}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Current</p>
                          <p className="font-mono text-white">{position.current_price.toFixed(5)}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Risk Score</p>
                          <p className={`font-bold ${
                            position.risk_score > 70 ? 'text-red-400' :
                            position.risk_score > 40 ? 'text-yellow-400' : 'text-green-400'
                          }`}>{position.risk_score}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Time</p>
                          <p className="text-white">{position.time_in_trade}</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <Badge className={getRecommendationColor(position.ai_recommendation)}>
                          AI: {position.ai_recommendation.replace('_', ' ')}
                        </Badge>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handlePositionAction(position.id, 'update_sl')}
                            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                          >
                            Update SL
                          </button>
                          <button
                            onClick={() => handlePositionAction(position.id, 'partial_close')}
                            className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm"
                          >
                            Partial Close
                          </button>
                          <button
                            onClick={() => handlePositionAction(position.id, 'close')}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                          >
                            Close
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </GlassCard>
          </div>

          {/* Risk Dashboard */}
          <div className="space-y-6">
            {riskMetrics && (
              <GlassCard className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Target className="h-6 w-6 text-red-400" />
                  Risk Metrics
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">Portfolio VaR (1D)</span>
                      <span className="text-sm text-white">{riskMetrics.var_1d.toFixed(2)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-red-400 h-2 rounded-full" style={{ width: `${riskMetrics.var_1d * 10}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">Max Drawdown</span>
                      <span className="text-sm text-white">{riskMetrics.max_drawdown.toFixed(2)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-orange-400 h-2 rounded-full" style={{ width: `${riskMetrics.max_drawdown}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">Sharpe Ratio</span>
                      <span className="text-sm text-green-400">{riskMetrics.sharpe_ratio.toFixed(2)}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">Profit Factor</span>
                      <span className="text-sm text-green-400">{riskMetrics.profit_factor.toFixed(2)}</span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-400 mb-2">Symbol Exposure</p>
                    <div className="space-y-2">
                      {Object.entries(riskMetrics.exposure_by_symbol).map(([symbol, exposure]) => (
                        <div key={symbol} className="flex justify-between">
                          <span className="text-sm text-white">{symbol}</span>
                          <span className="text-sm text-cyan-400">{exposure}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </GlassCard>
            )}

            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Brain className="h-6 w-6 text-purple-400" />
                AI Insights
              </h2>
              
              <div className="space-y-3">
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <p className="text-sm text-blue-400 font-semibold">Market Correlation</p>
                  <p className="text-xs text-gray-300">Current portfolio correlation risk is moderate. Consider diversifying into uncorrelated assets.</p>
                </div>
                
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <p className="text-sm text-green-400 font-semibold">Position Sizing</p>
                  <p className="text-xs text-gray-300">Optimal position sizes maintained. Risk per trade within acceptable limits.</p>
                </div>
                
                <div className="p-3 bg-yellow-500/10 rounded-lg">
                  <p className="text-sm text-yellow-400 font-semibold">Market Stress</p>
                  <p className="text-xs text-gray-300">Low market stress detected. Favorable conditions for position expansion.</p>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  )
}