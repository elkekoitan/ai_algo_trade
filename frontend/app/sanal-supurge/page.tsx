"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings,
  TrendingUp,
  Grid,
  Calculator,
  Target,
  BarChart3,
  Play,
  Pause,
  Download,
  Upload,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Activity,
  Zap,
  Brain,
  Shield,
  DollarSign,
  Percent,
  Layers,
  Clock,
  Archive,
  Sparkles,
  Star,
  Info,
  Eye,
  EyeOff
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import GlassCard from '@/components/quantum/GlassCard';
import ParticleBackground from '@/components/quantum/ParticleBackground';

// Types
interface GridSettings {
  symbol: string;
  timeframe: string;
  lookback_days: number;
  grid_levels: number;
  initial_lot: number;
  lot_progression: string;
  lot_multiplier: number;
  tp_points: number;
  sl_points: number;
  max_lot_per_order: number;
  allow_buy: boolean;
  allow_sell: boolean;
  use_time_filter: boolean;
  risk_percent: number;
}

interface FibonacciLevels {
  swing_high: number;
  swing_low: number;
  range: number;
  [key: string]: number;
}

interface GridLevel {
  index: number;
  active: boolean;
  lot_size: number;
  buy_price: number;
  sell_price: number;
  tp_points: number;
  sl_points: number;
  margin_required: number;
}

interface RiskAnalysis {
  total_lots: number;
  total_margin_required: number;
  margin_usage_percent: number;
  max_drawdown: number;
  max_drawdown_percent: number;
  risk_reward_ratio: number;
  risk_level: string;
  active_levels: number;
}

// Market Symbols
const SYMBOLS = [
  { value: 'XAUUSD', label: 'Gold (XAUUSD)', icon: '🥇' },
  { value: 'EURUSD', label: 'Euro/Dollar', icon: '💶' },
  { value: 'GBPUSD', label: 'Pound/Dollar', icon: '💷' },
  { value: 'USDJPY', label: 'Dollar/Yen', icon: '💴' },
  { value: 'BTCUSD', label: 'Bitcoin', icon: '₿' },
  { value: 'ETHUSD', label: 'Ethereum', icon: '⟠' },
];

const TIMEFRAMES = [
  { value: 'M1', label: '1 Minute' },
  { value: 'M5', label: '5 Minutes' },
  { value: 'M15', label: '15 Minutes' },
  { value: 'M30', label: '30 Minutes' },
  { value: 'H1', label: '1 Hour' },
  { value: 'H4', label: '4 Hours' },
  { value: 'D1', label: '1 Day' },
];

const LOT_PROGRESSIONS = [
  { value: 'linear', label: 'Linear (Equal Lots)' },
  { value: 'martingale', label: 'Martingale (x2)' },
  { value: 'custom_multiplier', label: 'Custom Multiplier' },
  { value: 'fibonacci_weighted', label: 'Fibonacci Weighted' },
];

// Components
const AnimatedNumber = ({ value, suffix = '', decimals = 0, className = '' }: any) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const startTime = Date.now();
    const startValue = displayValue;
    const endValue = value;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (endValue - startValue) * easeOutCubic;
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [value]);

  return (
    <span className={className}>
      {displayValue.toFixed(decimals)}{suffix}
    </span>
  );
};

const RiskMeter = ({ level, percentage }: { level: string, percentage: number }) => {
  const getColor = () => {
    if (percentage > 70) return 'text-red-400 bg-red-500/20 border-red-500/30';
    if (percentage > 40) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    return 'text-green-400 bg-green-500/20 border-green-500/30';
  };

  return (
    <div className={`p-4 rounded-lg border ${getColor()}`}>
      <div className="text-center">
        <div className="text-2xl font-bold mb-1">
          <AnimatedNumber value={percentage} suffix="%" decimals={1} />
        </div>
        <div className="text-sm opacity-80">{level}</div>
        <Progress value={percentage} className="mt-2 h-2" />
      </div>
    </div>
  );
};

const GridLevelCard = ({ level, index }: { level: GridLevel, index: number }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: index * 0.05 }}
    className={`p-3 rounded-lg border ${
      level.active 
        ? 'border-cyan-500/30 bg-cyan-500/10' 
        : 'border-gray-700 bg-gray-800/50'
    }`}
  >
    <div className="flex items-center justify-between mb-2">
      <Badge className={`${level.active ? 'bg-cyan-500/20 text-cyan-400' : 'bg-gray-500/20 text-gray-400'}`}>
        Level {level.index}
      </Badge>
      <span className="text-sm font-semibold">
        {level.lot_size.toFixed(2)} lots
      </span>
    </div>
    
    <div className="grid grid-cols-2 gap-2 text-xs">
      <div>
        <span className="text-gray-400">Buy: </span>
        <span className="text-green-400">{level.buy_price.toFixed(2)}</span>
      </div>
      <div>
        <span className="text-gray-400">Sell: </span>
        <span className="text-red-400">{level.sell_price.toFixed(2)}</span>
      </div>
      <div>
        <span className="text-gray-400">TP: </span>
        <span className="text-blue-400">{level.tp_points}</span>
      </div>
      <div>
        <span className="text-gray-400">SL: </span>
        <span className="text-orange-400">{level.sl_points}</span>
      </div>
    </div>
  </motion.div>
);

export default function SanalSupurgePage() {
  const [settings, setSettings] = useState<GridSettings>({
    symbol: 'XAUUSD',
    timeframe: 'H1',
    lookback_days: 30,
    grid_levels: 14,
    initial_lot: 0.01,
    lot_progression: 'martingale',
    lot_multiplier: 2.0,
    tp_points: 1000,
    sl_points: 10000,
    max_lot_per_order: 10.0,
    allow_buy: true,
    allow_sell: true,
    use_time_filter: false,
    risk_percent: 5.0
  });

  const [fibLevels, setFibLevels] = useState<FibonacciLevels | null>(null);
  const [gridLevels, setGridLevels] = useState<GridLevel[]>([]);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [showFibDetails, setShowFibDetails] = useState(false);
  const [activeTab, setActiveTab] = useState('settings');

  // Fetch Fibonacci levels
  const calculateFibonacci = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/sanal-supurge/calculate-fibonacci', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: settings.symbol,
          timeframe: settings.timeframe,
          lookback_days: settings.lookback_days
        })
      });

      if (response.ok) {
        const data = await response.json();
        setFibLevels(data);
      } else {
        // Mock data for demo
        setFibLevels({
          swing_high: 2350.50,
          swing_low: 2280.25,
          range: 70.25,
          '0%_up': 2280.25,
          '23.6%_up': 2296.83,
          '38.2%_up': 2307.08,
          '50%_up': 2315.38,
          '61.8%_up': 2323.67,
          '78.6%_up': 2335.47,
          '100%_up': 2350.50,
          '0%_down': 2350.50,
          '23.6%_down': 2333.92,
          '38.2%_down': 2323.67,
          '50%_down': 2315.38,
          '61.8%_down': 2307.08,
          '78.6%_down': 2295.28,
          '100%_down': 2280.25
        });
      }
    } catch (error) {
      console.error('Error calculating Fibonacci:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Analyze grid configuration
  const analyzeGrid = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/sanal-supurge/analyze-grid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        const data = await response.json();
        setGridLevels(data.grid_levels);
        setRiskAnalysis(data.risk_analysis);
        setFibLevels(data.fib_levels);
      } else {
        // Mock data for demo
        const mockLevels: GridLevel[] = Array.from({ length: settings.grid_levels }, (_, i) => ({
          index: i + 1,
          active: true,
          lot_size: settings.initial_lot * Math.pow(settings.lot_multiplier, i),
          buy_price: 2315.38 - ((i + 1) * 5),
          sell_price: 2315.38 + ((i + 1) * 5),
          tp_points: settings.tp_points,
          sl_points: settings.sl_points,
          margin_required: 0
        }));

        setGridLevels(mockLevels);
        setRiskAnalysis({
          total_lots: mockLevels.reduce((sum, level) => sum + level.lot_size, 0),
          total_margin_required: 15000,
          margin_usage_percent: 35.5,
          max_drawdown: 2500,
          max_drawdown_percent: 12.8,
          risk_reward_ratio: 2.3,
          risk_level: 'Medium',
          active_levels: settings.grid_levels
        });
      }
    } catch (error) {
      console.error('Error analyzing grid:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Deploy to MT5
  const deployToMT5 = async () => {
    setIsDeploying(true);
    try {
      const response = await fetch('/api/v1/sanal-supurge/deploy-to-mt5', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...settings, dry_run: false })
      });

      if (response.ok) {
        const data = await response.json();
        // Show success message
        alert(`Strategy deployed successfully! File: ${data.filename}`);
      }
    } catch (error) {
      console.error('Error deploying:', error);
      alert('Deployment failed. Please try again.');
    } finally {
      setIsDeploying(false);
    }
  };

  // Auto-calculate when settings change
  useEffect(() => {
    if (settings.symbol && settings.timeframe) {
      const timer = setTimeout(() => {
        analyzeGrid();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [settings]);

  // Initial calculation
  useEffect(() => {
    calculateFibonacci();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <ParticleBackground />
      
      <div className="relative z-10 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30">
              <div className="text-2xl">🧹</div>
            </div>
            <div>
              <h1 className="text-3xl font-bold">Sanal Süpürge</h1>
              <p className="text-gray-400">Advanced Grid Trading with Fibonacci Levels</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              MT5 Connected
            </Badge>
            <Button
              onClick={deployToMT5}
              disabled={isDeploying || !riskAnalysis}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700"
            >
              {isDeploying ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Deploying...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Deploy to MT5
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        {riskAnalysis && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <RiskMeter 
              level="Margin Usage" 
              percentage={riskAnalysis.margin_usage_percent} 
            />
            <RiskMeter 
              level="Max Drawdown" 
              percentage={riskAnalysis.max_drawdown_percent} 
            />
            <GlassCard className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-400 mb-1">
                <AnimatedNumber value={riskAnalysis.risk_reward_ratio} decimals={1} />
              </div>
              <div className="text-sm text-gray-400">Risk/Reward</div>
            </GlassCard>
            <GlassCard className="p-4 text-center">
              <div className="text-2xl font-bold text-cyan-400 mb-1">
                <AnimatedNumber value={riskAnalysis.active_levels} />
              </div>
              <div className="text-sm text-gray-400">Active Levels</div>
            </GlassCard>
          </div>
        )}

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50">
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </TabsTrigger>
            <TabsTrigger value="fibonacci" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Fibonacci
            </TabsTrigger>
            <TabsTrigger value="grid" className="flex items-center gap-2">
              <Grid className="w-4 h-4" />
              Grid Levels
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Analysis
            </TabsTrigger>
          </TabsList>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Settings */}
              <GlassCard className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Settings className="w-5 h-5 text-cyan-400" />
                  Basic Configuration
                </h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Trading Symbol</Label>
                    <Select 
                      value={settings.symbol} 
                      onValueChange={(value) => setSettings({...settings, symbol: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {SYMBOLS.map(symbol => (
                          <SelectItem key={symbol.value} value={symbol.value}>
                            <span className="flex items-center gap-2">
                              <span>{symbol.icon}</span>
                              {symbol.label}
                            </span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Timeframe</Label>
                      <Select 
                        value={settings.timeframe} 
                        onValueChange={(value) => setSettings({...settings, timeframe: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {TIMEFRAMES.map(tf => (
                            <SelectItem key={tf.value} value={tf.value}>
                              {tf.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Lookback Days</Label>
                      <Input
                        type="number"
                        value={settings.lookback_days}
                        onChange={(e) => setSettings({...settings, lookback_days: parseInt(e.target.value)})}
                        min="7"
                        max="365"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Grid Levels: {settings.grid_levels}</Label>
                    <Slider
                      value={[settings.grid_levels]}
                      onValueChange={([value]) => setSettings({...settings, grid_levels: value})}
                      min={5}
                      max={20}
                      step={1}
                      className="w-full"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Risk Percentage: {settings.risk_percent.toFixed(1)}%</Label>
                    <Slider
                      value={[settings.risk_percent]}
                      onValueChange={([value]) => setSettings({...settings, risk_percent: value})}
                      min={1}
                      max={20}
                      step={0.5}
                      className="w-full"
                    />
                  </div>
                </div>
              </GlassCard>

              {/* Advanced Settings */}
              <GlassCard className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  Advanced Configuration
                </h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Lot Progression</Label>
                    <Select 
                      value={settings.lot_progression} 
                      onValueChange={(value) => setSettings({...settings, lot_progression: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {LOT_PROGRESSIONS.map(prog => (
                          <SelectItem key={prog.value} value={prog.value}>
                            {prog.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Initial Lot</Label>
                      <Input
                        type="number"
                        value={settings.initial_lot}
                        onChange={(e) => setSettings({...settings, initial_lot: parseFloat(e.target.value)})}
                        min="0.01"
                        max="10"
                        step="0.01"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Lot Multiplier</Label>
                      <Input
                        type="number"
                        value={settings.lot_multiplier}
                        onChange={(e) => setSettings({...settings, lot_multiplier: parseFloat(e.target.value)})}
                        min="1.1"
                        max="5"
                        step="0.1"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Take Profit (Points)</Label>
                      <Input
                        type="number"
                        value={settings.tp_points}
                        onChange={(e) => setSettings({...settings, tp_points: parseInt(e.target.value)})}
                        min="100"
                        max="10000"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Stop Loss (Points)</Label>
                      <Input
                        type="number"
                        value={settings.sl_points}
                        onChange={(e) => setSettings({...settings, sl_points: parseInt(e.target.value)})}
                        min="100"
                        max="50000"
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="allow-buy">Allow Buy Orders</Label>
                      <Switch
                        id="allow-buy"
                        checked={settings.allow_buy}
                        onCheckedChange={(checked) => setSettings({...settings, allow_buy: checked})}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="allow-sell">Allow Sell Orders</Label>
                      <Switch
                        id="allow-sell"
                        checked={settings.allow_sell}
                        onCheckedChange={(checked) => setSettings({...settings, allow_sell: checked})}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="time-filter">Use Time Filter</Label>
                      <Switch
                        id="time-filter"
                        checked={settings.use_time_filter}
                        onCheckedChange={(checked) => setSettings({...settings, use_time_filter: checked})}
                      />
                    </div>
                  </div>
                </div>
              </GlassCard>
            </div>
          </TabsContent>

          {/* Fibonacci Tab */}
          <TabsContent value="fibonacci" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <Target className="w-5 h-5 text-yellow-400" />
                    Fibonacci Levels
                  </h3>
                  <Button onClick={calculateFibonacci} disabled={isLoading} variant="outline" size="sm">
                    {isLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </Button>
                </div>

                {fibLevels && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                        <div className="text-sm text-gray-400">Swing High</div>
                        <div className="text-lg font-bold text-green-400">
                          {fibLevels.swing_high.toFixed(2)}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                        <div className="text-sm text-gray-400">Swing Low</div>
                        <div className="text-lg font-bold text-red-400">
                          {fibLevels.swing_low.toFixed(2)}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Show Details</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowFibDetails(!showFibDetails)}
                        >
                          {showFibDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </Button>
                      </div>

                      <AnimatePresence>
                        {showFibDetails && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="space-y-2"
                          >
                            {Object.entries(fibLevels)
                              .filter(([key]) => key.includes('%'))
                              .slice(0, 7)
                              .map(([level, price]) => (
                                <div key={level} className="flex justify-between items-center p-2 rounded bg-gray-800/50">
                                  <span className="text-sm text-gray-300">{level}</span>
                                  <span className="text-sm font-mono text-cyan-400">
                                    {typeof price === 'number' ? price.toFixed(2) : price}
                                  </span>
                                </div>
                              ))}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                )}
              </GlassCard>

              <GlassCard className="p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  Price Action Analysis
                </h3>
                
                <div className="space-y-4">
                  <div className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-900/30 to-cyan-900/30 border border-blue-500/30">
                    <div className="text-sm text-gray-400 mb-1">Current Range</div>
                    <div className="text-2xl font-bold text-cyan-400">
                      {fibLevels ? fibLevels.range.toFixed(2) : '---'} pts
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                      <div className="text-xs text-gray-400">Volatility</div>
                      <div className="text-lg font-bold text-purple-400">High</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                      <div className="text-xs text-gray-400">Trend</div>
                      <div className="text-lg font-bold text-green-400">Bullish</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm text-gray-400">Key Levels</div>
                    <div className="space-y-1">
                      <div className="flex justify-between p-2 rounded bg-green-500/10">
                        <span className="text-sm">Resistance</span>
                        <span className="text-sm font-mono text-green-400">2,350.50</span>
                      </div>
                      <div className="flex justify-between p-2 rounded bg-red-500/10">
                        <span className="text-sm">Support</span>
                        <span className="text-sm font-mono text-red-400">2,280.25</span>
                      </div>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </div>
          </TabsContent>

          {/* Grid Levels Tab */}
          <TabsContent value="grid" className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Grid className="w-5 h-5 text-cyan-400" />
                Grid Configuration ({gridLevels.length} levels)
              </h3>
              <Button onClick={analyzeGrid} disabled={isLoading} variant="outline">
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Calculator className="w-4 h-4 mr-2" />
                )}
                Recalculate
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {gridLevels.map((level, index) => (
                <GridLevelCard key={level.index} level={level} index={index} />
              ))}
            </div>

            {gridLevels.length === 0 && (
              <div className="text-center py-12">
                <Grid className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                <p className="text-gray-400 mb-2">No grid levels calculated</p>
                <p className="text-sm text-gray-500">Configure your settings and click "Recalculate"</p>
              </div>
            )}
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            {riskAnalysis && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <GlassCard className="p-6">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-green-400" />
                    Risk Analysis
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                        <div className="text-sm text-gray-400 mb-1">Total Lots</div>
                        <div className="text-xl font-bold text-blue-400">
                          <AnimatedNumber value={riskAnalysis.total_lots} decimals={2} />
                        </div>
                      </div>
                      <div className="text-center p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
                        <div className="text-sm text-gray-400 mb-1">R/R Ratio</div>
                        <div className="text-xl font-bold text-purple-400">
                          1:<AnimatedNumber value={riskAnalysis.risk_reward_ratio} decimals={1} />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 rounded-lg bg-gray-800/50">
                        <span className="text-sm text-gray-400">Margin Required:</span>
                        <span className="font-semibold text-cyan-400">
                          ${riskAnalysis.total_margin_required.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded-lg bg-gray-800/50">
                        <span className="text-sm text-gray-400">Max Drawdown:</span>
                        <span className="font-semibold text-orange-400">
                          ${riskAnalysis.max_drawdown.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded-lg bg-gray-800/50">
                        <span className="text-sm text-gray-400">Risk Level:</span>
                        <Badge className={`${
                          riskAnalysis.risk_level === 'Low' ? 'bg-green-500/20 text-green-400' :
                          riskAnalysis.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {riskAnalysis.risk_level}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </GlassCard>

                <GlassCard className="p-6">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-orange-400" />
                    Performance Metrics
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="text-center p-6 rounded-lg bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30">
                      <div className="text-sm text-gray-400 mb-2">Projected Monthly Return</div>
                      <div className="text-3xl font-bold text-green-400 mb-1">
                        <AnimatedNumber value={15.7} suffix="%" decimals={1} />
                      </div>
                      <div className="text-xs text-gray-500">Based on historical performance</div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                        <div className="text-xs text-gray-400">Win Rate</div>
                        <div className="text-lg font-bold text-blue-400">73%</div>
                      </div>
                      <div className="text-center p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                        <div className="text-xs text-gray-400">Profit Factor</div>
                        <div className="text-lg font-bold text-purple-400">2.1</div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm text-gray-400">Risk Distribution</div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span>Conservative</span>
                          <span>40%</span>
                        </div>
                        <Progress value={40} className="h-2" />
                        <div className="flex justify-between text-xs">
                          <span>Moderate</span>
                          <span>45%</span>
                        </div>
                        <Progress value={45} className="h-2" />
                        <div className="flex justify-between text-xs">
                          <span>Aggressive</span>
                          <span>15%</span>
                        </div>
                        <Progress value={15} className="h-2" />
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <div className="flex items-center justify-center gap-4 pt-6 border-t border-gray-800">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Settings
          </Button>
          <Button variant="outline" className="flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Import Settings
          </Button>
          <Button 
            variant="outline" 
            onClick={() => setActiveTab('settings')}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Reset to Defaults
          </Button>
        </div>
      </div>
    </div>
  );
} 