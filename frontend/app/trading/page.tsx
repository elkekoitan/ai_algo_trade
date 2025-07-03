"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  TrendingUp, PlayCircle, PauseCircle, BarChart3, Activity, 
  Shield, Settings, Info, Zap, Target, TrendingDown, Clock,
  DollarSign, AlertCircle, ChevronRight, Sparkles, Bot,
  Gauge, RefreshCw, LineChart, CandlestickChart
} from 'lucide-react';
import useSWR from 'swr';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import QuantumLayout from '@/components/layout/QuantumLayout';

const TradingViewChart = dynamic(() => import('@/components/charts/TradingViewChart'), { ssr: false });
const OrderPanel = dynamic(() => import('@/components/trading/OrderPanel'), { ssr: false });
const PositionsTable = dynamic(() => import('@/components/trading/PositionsTable'), { ssr: false });

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Animated Number Component
const AnimatedNumber = ({ value, prefix = '', suffix = '', decimals = 0 }: any) => {
  const [displayValue, setDisplayValue] = useState(0);

  useState(() => {
    const duration = 1500;
    const steps = 50;
    const stepValue = value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += stepValue;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(current);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  });

  return (
    <span>{prefix}{displayValue.toFixed(decimals)}{suffix}</span>
  );
};

// Pulse Indicator
const PulseIndicator = ({ color = 'bg-green-400' }: { color?: string }) => (
  <div className="relative">
    <motion.div
      className={`w-2 h-2 rounded-full ${color}`}
      animate={{
        scale: [1, 1.2, 1],
        opacity: [1, 0.8, 1]
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
    <motion.div
      className={`absolute inset-0 rounded-full ${color}`}
      animate={{
        scale: [1, 2, 2.5],
        opacity: [0.7, 0.3, 0]
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeOut"
      }}
    />
  </div>
);

// Strategy Status Card
const StrategyStatusCard = ({ strategy }: any) => {
  const isActive = strategy.status === 'active';
  const isProfitable = strategy.profit >= 0;

    return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Card className={`relative overflow-hidden bg-gradient-to-br ${
        isActive 
          ? 'from-purple-900/50 to-blue-900/50 border-purple-500/50' 
          : 'from-gray-900/50 to-slate-900/50 border-gray-700'
      }`}>
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <motion.div
            className="absolute inset-0"
            style={{
              backgroundImage: `radial-gradient(circle, ${isActive ? '#8b5cf6' : '#6b7280'} 1px, transparent 1px)`,
              backgroundSize: '20px 20px'
            }}
            animate={{ 
              x: isActive ? [0, 20, 0] : 0,
              y: isActive ? [0, -20, 0] : 0
            }}
            transition={{ 
              duration: 20, 
              repeat: Infinity, 
              ease: "linear" 
            }}
          />
        </div>

        <CardContent className="p-4 relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Bot className={`h-5 w-5 ${isActive ? 'text-purple-400' : 'text-gray-500'}`} />
              <h3 className="font-semibold text-white">{strategy.name}</h3>
              {isActive && <PulseIndicator />}
            </div>
            <Badge className={isActive ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
              {strategy.status}
            </Badge>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-400">P&L</p>
              <p className={`text-lg font-bold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
                <AnimatedNumber value={strategy.profit} prefix="$" decimals={2} />
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Positions</p>
              <p className="text-lg font-bold text-blue-400">{strategy.positions}</p>
            </div>
          </div>

          {/* Symbol Grid */}
          <div className="flex flex-wrap gap-1 mb-4">
            {strategy.symbols.map((symbol: string, idx: number) => (
              <motion.span
                key={symbol}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
                className="px-2 py-1 bg-black/30 rounded text-xs text-gray-300 border border-gray-700"
              >
                {symbol}
              </motion.span>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            {isActive ? (
              <>
                <Button 
                  size="sm" 
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0"
                >
                  <Settings className="w-3 h-3 mr-1" />
                  Configure
                </Button>
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                >
                  Stop
                </Button>
              </>
            ) : (
              <Button 
                size="sm" 
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white border-0"
              >
                <PlayCircle className="w-3 h-3 mr-1" />
                Activate
              </Button>
            )}
          </div>
        </CardContent>

        {/* Status Indicator Bar */}
        <motion.div
          className={`absolute bottom-0 left-0 right-0 h-1 ${
            isActive ? 'bg-gradient-to-r from-purple-400 to-blue-400' : 'bg-gray-700'
          }`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </Card>
    </motion.div>
  );
};

// Market Overview Card
const MarketOverviewCard = () => {
  const markets = [
    { symbol: 'EURUSD', price: 1.0854, change: 0.12, trend: 'up' },
    { symbol: 'XAUUSD', price: 1978.45, change: -0.45, trend: 'down' },
    { symbol: 'BTCUSD', price: 35420, change: 2.34, trend: 'up' },
    { symbol: 'GBPUSD', price: 1.2643, change: -0.08, trend: 'down' }
  ];

  return (
    <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LineChart className="h-5 w-5 text-cyan-400" />
            Market Overview
          </div>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          >
            <RefreshCw className="h-4 w-4 text-gray-500" />
          </motion.div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
        <div className="space-y-3">
          {markets.map((market, idx) => (
            <motion.div
              key={market.symbol}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex items-center justify-between p-2 rounded-lg bg-black/20 border border-gray-800"
            >
              <span className="font-medium text-white">{market.symbol}</span>
              <div className="flex items-center gap-3">
                <span className="text-gray-300">{market.price}</span>
                <div className={`flex items-center gap-1 ${market.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                  {market.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  <span className="text-sm">{Math.abs(market.change)}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
                    </CardContent>
                </Card>
  );
};

// Performance Metrics Card
const PerformanceMetricsCard = ({ data }: any) => {
  const metrics = [
    { 
      label: 'Total Profit', 
      value: data?.total_profit || 0, 
      prefix: '$', 
      icon: DollarSign,
      color: data?.total_profit >= 0 ? 'text-green-400' : 'text-red-400',
      bgColor: data?.total_profit >= 0 ? 'from-green-900/30 to-emerald-900/30' : 'from-red-900/30 to-pink-900/30'
    },
    { 
      label: 'Win Rate', 
      value: data?.win_rate || 0, 
      suffix: '%', 
      icon: Target,
      color: 'text-purple-400',
      bgColor: 'from-purple-900/30 to-pink-900/30'
    },
    { 
      label: 'Active Trades', 
      value: data?.active_trades || 0, 
      icon: Activity,
      color: 'text-blue-400',
      bgColor: 'from-blue-900/30 to-cyan-900/30'
    },
    { 
      label: 'Risk Score', 
      value: data?.risk_score || 0, 
      suffix: '/10', 
      icon: Shield,
      color: 'text-yellow-400',
      bgColor: 'from-yellow-900/30 to-orange-900/30'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((metric, idx) => (
        <motion.div
          key={metric.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          whileHover={{ scale: 1.05 }}
        >
          <Card className={`bg-gradient-to-br ${metric.bgColor} border-gray-700 relative overflow-hidden`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <metric.icon className={`h-5 w-5 ${metric.color}`} />
                <motion.div
                  animate={{ 
                    opacity: [0.5, 1, 0.5],
                    scale: [0.9, 1, 0.9]
                  }}
                  transition={{ 
                    duration: 3, 
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className={`w-2 h-2 rounded-full ${metric.color.replace('text-', 'bg-')}`}
                />
              </div>
              <p className="text-xs text-gray-400 mb-1">{metric.label}</p>
              <p className={`text-2xl font-bold ${metric.color}`}>
                <AnimatedNumber 
                  value={metric.value} 
                  prefix={metric.prefix} 
                  suffix={metric.suffix} 
                  decimals={metric.prefix === '$' ? 2 : 0}
                />
                        </p>
                    </CardContent>
                </Card>
        </motion.div>
      ))}
    </div>
  );
};

// Strategy Selector with Animation
const StrategySelector = ({ onSelectStrategy }: { onSelectStrategy: (strategy: string) => void }) => {
  const strategies = [
    { 
      id: 'sanal_supurge', 
      name: 'Sanal Süpürge V1', 
      description: 'Advanced Grid Trading with Fibonacci', 
      icon: '🧹',
      status: 'active',
      special: true 
    },
    { 
      id: 'neural_scalper', 
      name: 'Neural Scalper', 
      description: 'AI-Powered Scalping Bot', 
      icon: '🤖',
      status: 'coming_soon' 
    },
    { 
      id: 'quantum_trend', 
      name: 'Quantum Trend', 
      description: 'Advanced Trend Following', 
      icon: '📈',
      status: 'coming_soon' 
    },
    { 
      id: 'shadow_hunter', 
      name: 'Shadow Hunter', 
      description: 'Institutional Flow Scanner', 
      icon: '👁️',
      status: 'coming_soon' 
    }
  ];

  const handleStrategyClick = (strategyId: string) => {
    if (strategyId === 'sanal_supurge') {
      // Redirect to Sanal Süpürge page
      window.location.href = '/sanal-supurge';
    } else {
      onSelectStrategy(strategyId);
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5 text-yellow-400" />
        Select Trading Strategy
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {strategies.map((strategy, idx) => (
          <motion.button
            key={strategy.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            whileHover={{ scale: 1.02, x: 5 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleStrategyClick(strategy.id)}
            className={`p-4 rounded-lg border transition-all text-left group relative overflow-hidden ${
              strategy.special 
                ? 'bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border-cyan-500/50 hover:border-cyan-400' 
                : 'bg-gradient-to-r from-gray-800/50 to-gray-900/50 border-gray-700 hover:border-purple-500/50'
            }`}
          >
            {/* Special indicator for Sanal Süpürge */}
            {strategy.special && (
              <motion.div
                className="absolute top-2 right-2"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.7, 1, 0.7]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <span className="text-xs bg-gradient-to-r from-cyan-400 to-blue-400 text-black px-2 py-1 rounded-full font-semibold">
                  ACTIVE
                </span>
              </motion.div>
            )}

            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{strategy.icon}</span>
              <div className="flex items-center gap-2">
                {strategy.status === 'active' && (
                  <motion.button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (strategy.id === 'sanal_supurge') {
                        window.location.href = '/sanal-supurge/settings';
                      }
                    }}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-1.5 rounded-full bg-cyan-500/20 hover:bg-cyan-500/30 transition-colors"
                  >
                    <Settings className="w-3 h-3 text-cyan-400" />
                  </motion.button>
                )}
                {strategy.status === 'coming_soon' && (
                  <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                    Soon
                  </span>
                )}
                <ChevronRight className={`h-4 w-4 transition-colors ${
                  strategy.special 
                    ? 'text-cyan-400 group-hover:text-cyan-300' 
                    : 'text-gray-500 group-hover:text-purple-400'
                }`} />
              </div>
            </div>
            <h4 className="font-semibold text-white mb-1">{strategy.name}</h4>
            <p className="text-xs text-gray-400">{strategy.description}</p>
            
            {strategy.special && (
              <div className="mt-3 pt-3 border-t border-cyan-500/30">
                <div className="flex items-center gap-1 text-xs text-cyan-400">
                  <Sparkles className="w-3 h-3" />
                  <span>Fibonacci + Grid System</span>
                </div>
              </div>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default function TradingPage() {
  const [activeTab, setActiveTab] = useState("manual");
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);

  // Data fetching
  const { data: strategyData } = useSWR(
    'http://localhost:8002/api/v1/sanal-supurge/multi-status',
    fetcher,
    { refreshInterval: 3000 }
  );

  const { data: performanceData } = useSWR(
    'http://localhost:8002/api/v1/sanal-supurge/multi-performance',
    fetcher,
    { refreshInterval: 5000 }
  );

  // Strategy info from data
  const totalProfit = strategyData?.data?.total_profit || 0;
  const totalPositions = strategyData?.data?.total_positions || 0;
  const activeSymbols = Object.keys(strategyData?.data?.symbol_breakdown || {});

  const activeStrategies = [
    {
      id: 'sanal_supurge',
      name: 'Sanal Süpürge V1',
      status: 'active',
      profit: totalProfit,
      positions: totalPositions,
      symbols: activeSymbols
    }
  ];

  const performanceMetrics = {
    total_profit: totalProfit,
    win_rate: performanceData?.data?.overall_performance?.win_rate || 0,
    active_trades: totalPositions,
    risk_score: performanceData?.data?.risk_assessment?.overall_risk === 'Low' ? 3 : 
                 performanceData?.data?.risk_assessment?.overall_risk === 'Medium' ? 6 : 8
  };

  return (
    <QuantumLayout
      title="Trading Terminal"
      subtitle="Live algorithmic trading with quantum precision"
      headerActions={
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link href="/strategy-whisperer">
            <Button className="quantum-button-primary">
              <Sparkles className="w-4 h-4 mr-2" />
              Create Strategy
            </Button>
          </Link>
        </motion.div>
      }
    >
      <div className="p-6 space-y-6">
        {/* Status Indicator */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
          className="flex justify-center"
      >
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30"
          >
            <PulseIndicator />
            <span className="text-sm font-medium text-green-400">Live Trading Active</span>
          </motion.div>
      </motion.div>

      {/* Performance Metrics */}
      <PerformanceMetricsCard data={performanceMetrics} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Trading Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Chart */}
          <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <CandlestickChart className="h-5 w-5 text-cyan-400" />
                Live Chart
              </CardTitle>
                    </CardHeader>
                    <CardContent>
              <div className="h-[400px]">
                <TradingViewChart symbol="EURUSD" />
              </div>
                    </CardContent>
                </Card>

          {/* Trading Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-gray-800/50">
              <TabsTrigger value="manual" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600">
                Manual Trading
              </TabsTrigger>
              <TabsTrigger value="strategies" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600">
                Trade with Strategies
              </TabsTrigger>
              <TabsTrigger value="positions" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600">
                Active Positions
              </TabsTrigger>
            </TabsList>

            <AnimatePresence mode="wait">
              <TabsContent value="manual" className="mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <OrderPanel onPlaceOrder={() => console.log('Placing order')} />
                </motion.div>
              </TabsContent>

              <TabsContent value="strategies" className="mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
                    <CardContent className="p-6">
                      {!selectedStrategy ? (
                        <StrategySelector onSelectStrategy={setSelectedStrategy} />
                      ) : (
                        <div className="space-y-4">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-white">Configure {selectedStrategy}</h3>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedStrategy(null)}
                              className="text-gray-400 hover:text-white"
                            >
                              ← Back
                            </Button>
                          </div>
                          {/* Strategy configuration form would go here */}
                          <div className="p-4 rounded-lg bg-black/20 border border-gray-800">
                            <p className="text-gray-400">Strategy configuration interface coming soon...</p>
                          </div>
                        </div>
                      )}
                    </CardContent>
                </Card>
                </motion.div>
              </TabsContent>

              <TabsContent value="positions" className="mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <PositionsTable positions={[]} isLoading={false} />
                </motion.div>
              </TabsContent>
            </AnimatePresence>
          </Tabs>
        </div>

        {/* Right Column - Status & Info */}
        <div className="space-y-6">
          {/* Active Strategies */}
          <div>
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Bot className="h-5 w-5 text-purple-400" />
              Active Strategies
            </h2>
            <div className="space-y-4">
              {activeStrategies.map((strategy) => (
                <StrategyStatusCard key={strategy.id} strategy={strategy} />
              ))}
            </div>
          </div>

          {/* Market Overview */}
          <MarketOverviewCard />

          {/* Quick Actions */}
          <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
                    <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                Quick Actions
              </CardTitle>
                    </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white border-0">
                <PlayCircle className="w-4 h-4 mr-2" />
                Start All Strategies
              </Button>
              <Button className="w-full bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white border-0">
                <PauseCircle className="w-4 h-4 mr-2" />
                Emergency Stop
              </Button>
              <Button variant="outline" className="w-full border-gray-600 text-gray-400 hover:bg-gray-800">
                <Settings className="w-4 h-4 mr-2" />
                Risk Settings
              </Button>
                    </CardContent>
                </Card>
        </div>
            </div>
        </div>
    </QuantumLayout>
    );
} 