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
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'

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

interface DynamicPosition {
  position_id: string;
  symbol: string;
  entry_price: number;
  current_price: number;
  position_size: number;
  original_size: number;
  status: string;
  stop_loss?: number;
  take_profit?: number;
  unrealized_pnl: number;
  risk_amount: number;
  risk_percentage: number;
  confidence_score: number;
  market_sentiment: number;
  volatility_forecast: number;
  trend_strength: number;
  entry_time: string;
  last_update: string;
  adjustments: any[];
}

interface PortfolioAnalysis {
  analysis_time: string;
  total_value: number;
  unrealized_pnl: number;
  daily_pnl: number;
  win_rate: number;
  portfolio_beta: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  market_regime: string;
  regime_confidence: number;
  portfolio_score: number;
  optimization_suggestions: string[];
}

interface ManagerStatus {
  status: string;
  total_positions: number;
  active_adjustments: number;
  total_alerts: number;
  performance_score: number;
  risk_score: number;
  last_optimization?: string;
  uptime_hours: number;
  cpu_usage: number;
  memory_usage: number;
  latency_ms: number;
  error_count: number;
}

export default function AdaptiveTradeManagerPage() {
  const [positions, setPositions] = useState<DynamicPosition[]>([])
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null)
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<PortfolioAnalysis | null>(null)
  const [managerStatus, setManagerStatus] = useState<ManagerStatus | null>(null)
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
  const [selectedSymbol, setSelectedSymbol] = useState<string>('')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [monitoringActive, setMonitoringActive] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
        setPositions(mockPositions.map(pos => ({
          position_id: pos.id,
          symbol: pos.symbol,
          entry_price: pos.entry_price,
          current_price: pos.current_price,
          position_size: pos.volume,
          original_size: pos.volume,
          status: 'active',
          stop_loss: pos.stop_loss,
          take_profit: pos.take_profit,
          unrealized_pnl: pos.profit_loss,
          risk_amount: pos.risk_score,
          risk_percentage: pos.profit_loss_percent,
          confidence_score: pos.confidence,
          market_sentiment: pos.profit_loss > 0 ? 1 : -1,
          volatility_forecast: 0,
          trend_strength: 0,
          entry_time: pos.time_in_trade,
          last_update: pos.last_update,
          adjustments: []
        })));
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

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'text-green-500';
      case 'monitoring': return 'text-blue-500';
      case 'adjusting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const refreshAllData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchData(),
        fetchManagerStatus()
      ]);
    } catch (error) {
      setError('Failed to fetch data');
      console.error('Error refreshing data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchManagerStatus = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/adaptive-trade-manager/status');
      if (response.ok) {
        const data = await response.json();
        setManagerStatus(data);
      }
    } catch (error) {
      console.error('Error fetching manager status:', error);
    }
  };

  if (isLoading && !managerStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <RefreshCw className="h-12 w-12 animate-spin text-blue-400 mx-auto mb-4" />
              <p className="text-white text-lg">Loading Adaptive Trade Manager...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              🧠 Adaptive Trade Manager
            </h1>
            <p className="text-gray-300">
              AI-Powered Dynamic Position Management & Risk Optimization
            </p>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={refreshAllData}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            <Button
              onClick={() => setAutoRefresh(!autoRefresh)}
              variant={autoRefresh ? "default" : "outline"}
              className={autoRefresh ? "bg-green-600 hover:bg-green-700" : ""}
            >
              <Activity className="h-4 w-4 mr-2" />
              Auto Refresh
            </Button>
            
            <Button
              onClick={() => setMonitoringActive(!monitoringActive)}
              disabled={monitoringActive}
              className="bg-purple-600 hover:bg-purple-700 text-white"
            >
              <Eye className="h-4 w-4 mr-2" />
              {monitoringActive ? 'Monitoring Active' : 'Start Monitoring'}
            </Button>
          </div>
        </div>

        {/* Status Overview */}
        {managerStatus && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card className="bg-black/40 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Status</p>
                    <p className={`text-lg font-semibold ${getStatusColor(managerStatus.status)}`}>
                      {managerStatus.status.toUpperCase()}
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Positions</p>
                    <p className="text-2xl font-bold text-white">
                      {managerStatus.total_positions}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Performance</p>
                    <p className="text-2xl font-bold text-white">
                      {managerStatus.performance_score.toFixed(1)}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Risk Score</p>
                    <p className="text-2xl font-bold text-white">
                      {managerStatus.risk_score.toFixed(1)}%
                    </p>
                  </div>
                  <Shield className="h-8 w-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Alerts</p>
                    <p className="text-2xl font-bold text-white">
                      {managerStatus.total_alerts}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* System Health */}
        {managerStatus && (
          <Card className="bg-black/40 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Gauge className="h-5 w-5" />
                System Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-gray-400 text-sm mb-2">CPU Usage</p>
                  <Progress value={managerStatus.cpu_usage} className="h-2" />
                  <p className="text-white text-sm mt-1">{managerStatus.cpu_usage.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-2">Memory Usage</p>
                  <Progress value={managerStatus.memory_usage} className="h-2" />
                  <p className="text-white text-sm mt-1">{managerStatus.memory_usage.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-2">Latency</p>
                  <p className="text-white text-lg font-semibold">{managerStatus.latency_ms.toFixed(1)}ms</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-2">Uptime</p>
                  <p className="text-white text-lg font-semibold">{managerStatus.uptime_hours.toFixed(1)}h</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-black/40 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600">
              Overview
            </TabsTrigger>
            <TabsTrigger value="positions" className="data-[state=active]:bg-blue-600">
              Positions
            </TabsTrigger>
            <TabsTrigger value="risk" className="data-[state=active]:bg-blue-600">
              Risk Analysis
            </TabsTrigger>
            <TabsTrigger value="portfolio" className="data-[state=active]:bg-blue-600">
              Portfolio
            </TabsTrigger>
            <TabsTrigger value="alerts" className="data-[state=active]:bg-blue-600">
              Alerts
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {portfolioAnalysis && riskMetrics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Portfolio Summary */}
                <Card className="bg-black/40 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Portfolio Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm">Total Value</p>
                        <p className="text-2xl font-bold text-white">
                          ${portfolioAnalysis.total_value.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Unrealized P&L</p>
                        <p className={`text-2xl font-bold ${portfolioAnalysis.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ${portfolioAnalysis.unrealized_pnl.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Win Rate</p>
                        <p className="text-xl font-bold text-white">
                          {portfolioAnalysis.win_rate.toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Portfolio Score</p>
                        <p className="text-xl font-bold text-blue-400">
                          {portfolioAnalysis.portfolio_score.toFixed(0)}/100
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Risk Overview */}
                <Card className="bg-black/40 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Risk Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-gray-400 text-sm">Overall Risk Level</p>
                      <Badge className={`${getRiskLevelColor(riskMetrics.overall_risk_level)} bg-transparent border`}>
                        {riskMetrics.overall_risk_level.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm">Portfolio Risk</p>
                        <p className="text-xl font-bold text-white">
                          {riskMetrics.risk_percentage.toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Max Drawdown</p>
                        <p className="text-xl font-bold text-red-400">
                          {riskMetrics.max_drawdown.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Recommendation</p>
                      <p className="text-white text-sm">{riskMetrics.recommendation}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Insights */}
            {portfolioAnalysis && portfolioAnalysis.optimization_suggestions.length > 0 && (
              <Card className="bg-black/40 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    AI Optimization Suggestions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {portfolioAnalysis.optimization_suggestions.map((suggestion, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <Zap className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                        <p className="text-white text-sm">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Positions Tab */}
          <TabsContent value="positions">
            <TradeMonitor 
              positions={positions} 
              onSymbolFilter={setSelectedSymbol}
              selectedSymbol={selectedSymbol}
            />
          </TabsContent>

          {/* Risk Tab */}
          <TabsContent value="risk">
            <RiskDashboard 
              riskMetrics={riskMetrics}
              positions={positions}
            />
          </TabsContent>

          {/* Portfolio Tab */}
          <TabsContent value="portfolio">
            <AdaptiveControls 
              portfolioAnalysis={portfolioAnalysis}
              managerStatus={managerStatus}
            />
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts">
            <AlertCenter 
              alerts={alerts}
              onRefresh={fetchAlerts}
            />
          </TabsContent>
        </Tabs>

        {/* Error Display */}
        {error && (
          <Card className="bg-red-900/20 border-red-500/50">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-400" />
                <p className="text-red-400">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
} 