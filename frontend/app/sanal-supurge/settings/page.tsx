"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, ArrowLeft, Save, RefreshCw, Play, Pause, AlertTriangle, 
  CheckCircle, Grid, Target, TrendingUp, Shield, BarChart3, 
  Sliders, Zap, Clock, DollarSign, Percent, Calculator,
  Info, Eye, EyeOff, Lock, Unlock, Sparkles, Star, Download,
  Gauge, Flame
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import QuantumLayout from '@/components/layout/QuantumLayout';
import GlassCard from '@/components/quantum/GlassCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'react-hot-toast';

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
  fibonacci_mode: boolean;
  adaptive_levels: boolean;
  auto_scaling: boolean;
  smart_tp: boolean;
  breakeven_mode: boolean;
  trailing_stop: boolean;
  max_spread: number;
  news_filter: boolean;
  volatility_filter: boolean;
}

interface RiskMetrics {
  max_drawdown: number;
  margin_usage: number;
  daily_risk: number;
  position_size: number;
  total_exposure: number;
  risk_score: number;
}

const SYMBOLS = [
  { value: 'XAUUSD', label: 'Gold (XAUUSD)', icon: '🥇', spread: 0.3 },
  { value: 'EURUSD', label: 'Euro/Dollar', icon: '💶', spread: 0.1 },
  { value: 'GBPUSD', label: 'Pound/Dollar', icon: '💷', spread: 0.2 },
  { value: 'USDJPY', label: 'Dollar/Yen', icon: '💴', spread: 0.1 },
  { value: 'BTCUSD', label: 'Bitcoin', icon: '₿', spread: 10.0 },
  { value: 'ETHUSD', label: 'Ethereum', icon: '⟠', spread: 2.0 },
];

const TIMEFRAMES = [
  { value: 'M1', label: '1 Minute', risk: 'Very High' },
  { value: 'M5', label: '5 Minutes', risk: 'High' },
  { value: 'M15', label: '15 Minutes', risk: 'Medium' },
  { value: 'M30', label: '30 Minutes', risk: 'Medium' },
  { value: 'H1', label: '1 Hour', risk: 'Low' },
  { value: 'H4', label: '4 Hours', risk: 'Very Low' },
  { value: 'D1', label: '1 Day', risk: 'Ultra Low' },
];

const LOT_PROGRESSIONS = [
  { value: 'linear', label: 'Linear (Equal Lots)', description: 'Same lot size for all levels' },
  { value: 'martingale', label: 'Martingale (x2)', description: 'Double the lot size each level' },
  { value: 'custom_multiplier', label: 'Custom Multiplier', description: 'Use custom multiplier' },
  { value: 'fibonacci_weighted', label: 'Fibonacci Weighted', description: 'Use Fibonacci sequence' },
];

export default function SanalSupurgeSettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<GridSettings>({
    symbol: 'XAUUSD',
    timeframe: 'M15',
    lookback_days: 30,
    grid_levels: 10,
    initial_lot: 0.01,
    lot_progression: 'fibonacci_weighted',
    lot_multiplier: 1.5,
    tp_points: 100,
    sl_points: 1000,
    max_lot_per_order: 1.0,
    allow_buy: true,
    allow_sell: true,
    use_time_filter: true,
    risk_percent: 2.0,
    fibonacci_mode: true,
    adaptive_levels: true,
    auto_scaling: true,
    smart_tp: true,
    breakeven_mode: true,
    trailing_stop: false,
    max_spread: 3.0,
    news_filter: true,
    volatility_filter: true,
  });

  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics>({
    max_drawdown: 12.5,
    margin_usage: 35.2,
    daily_risk: 1.8,
    position_size: 0.15,
    total_exposure: 2450.0,
    risk_score: 25
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isDeployed, setIsDeployed] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [presetMode, setPresetMode] = useState('custom');

  const presets = {
    conservative: {
      grid_levels: 8,
      initial_lot: 0.01,
      lot_progression: 'linear',
      risk_percent: 1.0,
      tp_points: 50,
      sl_points: 200
    },
    balanced: {
      grid_levels: 12,
      initial_lot: 0.02,
      lot_progression: 'fibonacci_weighted',
      risk_percent: 2.0,
      tp_points: 100,
      sl_points: 500
    },
    aggressive: {
      grid_levels: 16,
      initial_lot: 0.05,
      lot_progression: 'martingale',
      risk_percent: 5.0,
      tp_points: 200,
      sl_points: 1000
    }
  };

  const calculateRisk = () => {
    const totalLots = settings.initial_lot * settings.grid_levels;
    const marginRequired = totalLots * 1000; // Simplified calculation
    const maxDrawdown = (totalLots * settings.sl_points * 0.1) / 100;
    
    setRiskMetrics({
      max_drawdown: maxDrawdown,
      margin_usage: (marginRequired / 10000) * 100,
      daily_risk: settings.risk_percent,
      position_size: totalLots,
      total_exposure: totalLots * 1000,
      risk_score: Math.min(100, (settings.risk_percent * 10) + (settings.grid_levels * 2))
    });
  };

  useEffect(() => {
    calculateRisk();
  }, [settings]);

  const handlePresetChange = (preset: string) => {
    setPresetMode(preset);
    if (preset !== 'custom') {
      setSettings(prev => ({
        ...prev,
        ...presets[preset as keyof typeof presets]
      }));
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeploy = async () => {
    setIsLoading(true);
    try {
      // Simulate deployment
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsDeployed(true);
      toast.success('Strategy deployed successfully!');
    } catch (error) {
      toast.error('Failed to deploy strategy');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-400';
    if (score < 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskLevel = (score: number) => {
    if (score < 30) return 'Low Risk';
    if (score < 60) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <QuantumLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => router.back()}
              className="p-2 hover:bg-white/10"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Target className="w-8 h-8 text-cyan-400" />
                Sanal Süpürge Pro Settings
              </h1>
              <p className="text-gray-400 mt-1">
                Configure your advanced grid trading strategy
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Badge className={`${isDeployed ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
              {isDeployed ? 'DEPLOYED' : 'INACTIVE'}
            </Badge>
            <Button
              onClick={handleDeploy}
              disabled={isLoading}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              {isDeployed ? 'Redeploy' : 'Deploy Strategy'}
            </Button>
          </div>
        </motion.div>

        {/* Risk Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <GlassCard variant="neon" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Shield className="w-6 h-6 text-cyan-400" />
                Risk Assessment
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">Risk Score:</span>
                <span className={`text-2xl font-bold ${getRiskColor(riskMetrics.risk_score)}`}>
                  {riskMetrics.risk_score}
                </span>
                <Badge className={`${getRiskColor(riskMetrics.risk_score)} bg-opacity-20`}>
                  {getRiskLevel(riskMetrics.risk_score)}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-cyan-400 mb-1">
                  {riskMetrics.max_drawdown.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-400">Max Drawdown</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400 mb-1">
                  {riskMetrics.margin_usage.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-400">Margin Usage</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400 mb-1">
                  {riskMetrics.daily_risk.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-400">Daily Risk</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400 mb-1">
                  {riskMetrics.position_size.toFixed(2)}
                </div>
                <p className="text-sm text-gray-400">Position Size</p>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Settings Tabs */}
        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-black/20 backdrop-blur-xl">
            <TabsTrigger value="basic">Basic Settings</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
            <TabsTrigger value="risk">Risk Management</TabsTrigger>
            <TabsTrigger value="calculator">Grid Calculator</TabsTrigger>
            <TabsTrigger value="presets">Presets</TabsTrigger>
          </TabsList>

          {/* Basic Settings */}
          <TabsContent value="basic" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Grid className="w-5 h-5 text-cyan-400" />
                  Market Configuration
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="symbol" className="text-sm font-medium text-gray-300">
                      Trading Symbol
                    </Label>
                    <Select value={settings.symbol} onValueChange={(value) => setSettings(prev => ({ ...prev, symbol: value }))}>
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {SYMBOLS.map(symbol => (
                          <SelectItem key={symbol.value} value={symbol.value}>
                            <div className="flex items-center gap-2">
                              <span>{symbol.icon}</span>
                              <span>{symbol.label}</span>
                              <Badge variant="outline" className="ml-auto">
                                {symbol.spread} pips
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="timeframe" className="text-sm font-medium text-gray-300">
                      Timeframe
                    </Label>
                    <Select value={settings.timeframe} onValueChange={(value) => setSettings(prev => ({ ...prev, timeframe: value }))}>
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {TIMEFRAMES.map(tf => (
                          <SelectItem key={tf.value} value={tf.value}>
                            <div className="flex items-center justify-between w-full">
                              <span>{tf.label}</span>
                              <Badge variant="outline" className="ml-auto">
                                {tf.risk}
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="lookback" className="text-sm font-medium text-gray-300">
                      Lookback Period (Days)
                    </Label>
                    <Input
                      id="lookback"
                      type="number"
                      value={settings.lookback_days}
                      onChange={(e) => setSettings(prev => ({ ...prev, lookback_days: parseInt(e.target.value) }))}
                      className="mt-2"
                    />
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Calculator className="w-5 h-5 text-purple-400" />
                  Grid Parameters
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-300">
                      Grid Levels: {settings.grid_levels}
                    </Label>
                    <Slider
                      value={[settings.grid_levels]}
                      onValueChange={(value) => setSettings(prev => ({ ...prev, grid_levels: value[0] }))}
                      max={20}
                      min={3}
                      step={1}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="initial_lot" className="text-sm font-medium text-gray-300">
                      Initial Lot Size
                    </Label>
                    <Input
                      id="initial_lot"
                      type="number"
                      step="0.01"
                      value={settings.initial_lot}
                      onChange={(e) => setSettings(prev => ({ ...prev, initial_lot: parseFloat(e.target.value) }))}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="lot_progression" className="text-sm font-medium text-gray-300">
                      Lot Progression
                    </Label>
                    <Select value={settings.lot_progression} onValueChange={(value) => setSettings(prev => ({ ...prev, lot_progression: value }))}>
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {LOT_PROGRESSIONS.map(prog => (
                          <SelectItem key={prog.value} value={prog.value}>
                            <div className="flex flex-col">
                              <span>{prog.label}</span>
                              <span className="text-xs text-gray-400">{prog.description}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {settings.lot_progression === 'custom_multiplier' && (
                    <div>
                      <Label htmlFor="multiplier" className="text-sm font-medium text-gray-300">
                        Lot Multiplier
                      </Label>
                      <Input
                        id="multiplier"
                        type="number"
                        step="0.1"
                        value={settings.lot_multiplier}
                        onChange={(e) => setSettings(prev => ({ ...prev, lot_multiplier: parseFloat(e.target.value) }))}
                        className="mt-2"
                      />
                    </div>
                  )}
                </div>
              </GlassCard>
            </motion.div>
          </TabsContent>

          {/* Advanced Settings */}
          <TabsContent value="advanced" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-400" />
                  Smart Features
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Fibonacci Mode</Label>
                      <p className="text-xs text-gray-400">Use Fibonacci levels for grid placement</p>
                    </div>
                    <Switch
                      checked={settings.fibonacci_mode}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, fibonacci_mode: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Adaptive Levels</Label>
                      <p className="text-xs text-gray-400">Automatically adjust grid levels</p>
                    </div>
                    <Switch
                      checked={settings.adaptive_levels}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, adaptive_levels: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Auto Scaling</Label>
                      <p className="text-xs text-gray-400">Scale position size with volatility</p>
                    </div>
                    <Switch
                      checked={settings.auto_scaling}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, auto_scaling: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Smart Take Profit</Label>
                      <p className="text-xs text-gray-400">Dynamic TP based on market conditions</p>
                    </div>
                    <Switch
                      checked={settings.smart_tp}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, smart_tp: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Breakeven Mode</Label>
                      <p className="text-xs text-gray-400">Move SL to breakeven when profitable</p>
                    </div>
                    <Switch
                      checked={settings.breakeven_mode}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, breakeven_mode: checked }))}
                    />
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-red-400" />
                  Filters & Protection
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">News Filter</Label>
                      <p className="text-xs text-gray-400">Stop trading during news events</p>
                    </div>
                    <Switch
                      checked={settings.news_filter}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, news_filter: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">Volatility Filter</Label>
                      <p className="text-xs text-gray-400">Adjust based on market volatility</p>
                    </div>
                    <Switch
                      checked={settings.volatility_filter}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, volatility_filter: checked }))}
                    />
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-gray-300">
                      Max Spread: {settings.max_spread} pips
                    </Label>
                    <Slider
                      value={[settings.max_spread]}
                      onValueChange={(value) => setSettings(prev => ({ ...prev, max_spread: value[0] }))}
                      max={10}
                      min={0.5}
                      step={0.1}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="tp_points" className="text-sm font-medium text-gray-300">
                      Take Profit (Points)
                    </Label>
                    <Input
                      id="tp_points"
                      type="number"
                      value={settings.tp_points}
                      onChange={(e) => setSettings(prev => ({ ...prev, tp_points: parseInt(e.target.value) }))}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="sl_points" className="text-sm font-medium text-gray-300">
                      Stop Loss (Points)
                    </Label>
                    <Input
                      id="sl_points"
                      type="number"
                      value={settings.sl_points}
                      onChange={(e) => setSettings(prev => ({ ...prev, sl_points: parseInt(e.target.value) }))}
                      className="mt-2"
                    />
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          </TabsContent>

          {/* Risk Management */}
          <TabsContent value="risk" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  Risk Management Settings
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-300">
                        Risk Per Trade: {settings.risk_percent}%
                      </Label>
                      <Slider
                        value={[settings.risk_percent]}
                        onValueChange={(value) => setSettings(prev => ({ ...prev, risk_percent: value[0] }))}
                        max={10}
                        min={0.5}
                        step={0.1}
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label htmlFor="max_lot" className="text-sm font-medium text-gray-300">
                        Max Lot Per Order
                      </Label>
                      <Input
                        id="max_lot"
                        type="number"
                        step="0.01"
                        value={settings.max_lot_per_order}
                        onChange={(e) => setSettings(prev => ({ ...prev, max_lot_per_order: parseFloat(e.target.value) }))}
                        className="mt-2"
                      />
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          checked={settings.allow_buy}
                          onCheckedChange={(checked) => setSettings(prev => ({ ...prev, allow_buy: checked }))}
                        />
                        <Label className="text-sm text-gray-300">Allow Buy</Label>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Switch
                          checked={settings.allow_sell}
                          onCheckedChange={(checked) => setSettings(prev => ({ ...prev, allow_sell: checked }))}
                        />
                        <Label className="text-sm text-gray-300">Allow Sell</Label>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                      <h4 className="font-medium text-red-400 mb-2">Risk Warning</h4>
                      <p className="text-sm text-gray-300">
                        Grid trading can lead to significant losses during trending markets. 
                        Always use proper risk management and never risk more than you can afford to lose.
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                      <h4 className="font-medium text-yellow-400 mb-2">Margin Requirements</h4>
                      <p className="text-sm text-gray-300">
                        Ensure you have sufficient margin to cover all grid levels. 
                        Current estimated margin usage: {riskMetrics.margin_usage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          </TabsContent>

          {/* Grid Calculator */}
          <TabsContent value="calculator" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 xl:grid-cols-3 gap-6"
            >
              {/* Calculator Main Panel */}
              <div className="xl:col-span-2">
                <GlassCard className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <Calculator className="w-5 h-5 text-purple-400" />
                      Pro Grid Calculator
                    </h3>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        .set Export
                      </Button>
                      <Button size="sm" className="bg-purple-500 hover:bg-purple-600">
                        <Calculator className="w-4 h-4 mr-2" />
                        Hesapla
                      </Button>
                    </div>
                  </div>

                  <Tabs defaultValue="config">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="config">Konfigürasyon</TabsTrigger>
                      <TabsTrigger value="grid">Grid Seviyeleri</TabsTrigger>
                      <TabsTrigger value="results">Sonuçlar</TabsTrigger>
                    </TabsList>

                    <TabsContent value="config" className="space-y-4 mt-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm font-medium text-gray-300">Enstrüman</Label>
                          <Select defaultValue="XAUUSD">
                            <SelectTrigger className="mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="XAUUSD">XAUUSD - Gold vs USD</SelectItem>
                              <SelectItem value="EURUSD">EURUSD - Euro vs USD</SelectItem>
                              <SelectItem value="BTCUSD">BTCUSD - Bitcoin vs USD</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">Başlangıç Fiyatı</Label>
                          <Input 
                            type="number" 
                            placeholder="2300.00" 
                            step="any" 
                            defaultValue="2300.00"
                            className="mt-1"
                          />
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">Hesap Bakiyesi</Label>
                          <Input 
                            type="number" 
                            placeholder="10000" 
                            defaultValue="10000"
                            className="mt-1"
                          />
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">Kaldıraç (1:X)</Label>
                          <Input 
                            type="number" 
                            placeholder="100" 
                            defaultValue="100"
                            className="mt-1"
                          />
                        </div>
                      </div>

                      <div>
                        <Label className="text-sm font-medium text-gray-300">Lot Artış Modeli</Label>
                        <Select defaultValue="martingale">
                          <SelectTrigger className="mt-1">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="linear">Lineer (Eşit Lotlar)</SelectItem>
                            <SelectItem value="martingale">Martingale (x2 Katı)</SelectItem>
                            <SelectItem value="fibonacci">Fibonacci Ağırlıklı</SelectItem>
                            <SelectItem value="custom">Özel Çarpan</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label className="text-sm font-medium text-gray-300">
                          Volatilite (ATR Puan): 3500
                        </Label>
                        <Slider
                          defaultValue={[3500]}
                          max={10000}
                          min={100}
                          step={100}
                          className="mt-2"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>100</span>
                          <span>Düşük</span>
                          <span>Orta</span>
                          <span>Yüksek</span>
                          <span>10000</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm font-medium text-gray-300">
                            Risk Yüzdesi: {settings.risk_percent}%
                          </Label>
                          <Slider
                            value={[settings.risk_percent]}
                            onValueChange={(value) => setSettings(prev => ({ ...prev, risk_percent: value[0] }))}
                            max={10}
                            min={0.5}
                            step={0.1}
                            className="mt-2"
                          />
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">
                            Grid Seviyesi: {settings.grid_levels}
                          </Label>
                          <Slider
                            value={[settings.grid_levels]}
                            onValueChange={(value) => setSettings(prev => ({ ...prev, grid_levels: value[0] }))}
                            max={14}
                            min={3}
                            step={1}
                            className="mt-2"
                          />
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="grid" className="space-y-4 mt-4">
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div>
                          <Label className="text-sm font-medium text-gray-300">
                            Varsayılan Mesafe: 3500
                          </Label>
                          <Slider
                            defaultValue={[3500]}
                            max={10000}
                            min={100}
                            step={100}
                            className="mt-2"
                          />
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">
                            Varsayılan TP: 7000
                          </Label>
                          <Slider
                            defaultValue={[7000]}
                            max={20000}
                            min={100}
                            step={100}
                            className="mt-2"
                          />
                        </div>

                        <div>
                          <Label className="text-sm font-medium text-gray-300">
                            Varsayılan SL: 60000
                          </Label>
                          <Slider
                            defaultValue={[60000]}
                            max={100000}
                            min={1000}
                            step={1000}
                            className="mt-2"
                          />
                        </div>
                      </div>

                      <div className="border border-border rounded-lg p-4 max-h-80 overflow-y-auto">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-white">Grid Seviyeleri (14 Kademe)</h4>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm">
                              <RefreshCw className="w-3 h-3 mr-1" />
                              Reset
                            </Button>
                            <Button variant="outline" size="sm">
                              <Sparkles className="w-3 h-3 mr-1" />
                              Auto Fill
                            </Button>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="grid grid-cols-6 gap-2 text-xs text-gray-400 mb-2">
                            <div>Seviye</div>
                            <div>Aktif</div>
                            <div>Lot</div>
                            <div>Mesafe (P)</div>
                            <div>TP (P)</div>
                            <div>SL (P)</div>
                          </div>
                          
                          {Array.from({length: 14}, (_, i) => i + 1).map(level => (
                            <div key={level} className="grid grid-cols-6 gap-2 items-center text-sm">
                              <div className="text-center font-medium text-gray-300">{level}</div>
                              <div className="flex justify-center">
                                <Switch defaultChecked />
                              </div>
                              <Input 
                                type="number" 
                                defaultValue={level <= 9 ? (level * 0.01).toFixed(2) : "0.10"} 
                                className="h-8 text-xs" 
                                step="0.01"
                              />
                              <Input 
                                type="number" 
                                defaultValue={level === 1 ? "0" : "3500"} 
                                className="h-8 text-xs"
                                disabled={level === 1}
                              />
                              <Input 
                                type="number" 
                                defaultValue={level <= 9 ? "1000" : "2500"} 
                                className="h-8 text-xs"
                              />
                              <Input 
                                type="number" 
                                defaultValue="100" 
                                className="h-8 text-xs"
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="results" className="space-y-4 mt-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                          <div className="flex items-center gap-2 mb-2">
                            <TrendingUp className="w-5 h-5 text-green-400" />
                            <span className="font-medium text-green-400">Toplam Lot</span>
                          </div>
                          <div className="text-2xl font-bold text-white">1.47</div>
                          <div className="text-sm text-gray-400">Buy: 0.74 | Sell: 0.73</div>
                        </div>

                        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-red-400" />
                            <span className="font-medium text-red-400">Max Drawdown</span>
                          </div>
                          <div className="text-2xl font-bold text-white">$2,340</div>
                          <div className="text-sm text-gray-400">Buy: $1,200 | Sell: $1,140</div>
                        </div>

                        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                          <div className="flex items-center gap-2 mb-2">
                            <BarChart3 className="w-5 h-5 text-blue-400" />
                            <span className="font-medium text-blue-400">Marjin Kullanımı</span>
                          </div>
                          <div className="text-2xl font-bold text-white">15.3%</div>
                          <div className="text-sm text-gray-400">$1,530 / $10,000</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="border border-border rounded-lg p-4">
                          <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                            <Target className="w-4 h-4 text-cyan-400" />
                            Fibonacci Seviyeleri
                          </h4>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-400">23.6%:</span>
                              <span className="text-white font-mono">2285.40</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">38.2%:</span>
                              <span className="text-white font-mono">2275.80</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">50.0%:</span>
                              <span className="text-white font-mono">2265.00</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">61.8%:</span>
                              <span className="text-white font-mono">2254.20</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">78.6%:</span>
                              <span className="text-white font-mono">2243.60</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">100%:</span>
                              <span className="text-white font-mono">2230.00</span>
                            </div>
                          </div>
                        </div>

                        <div className="border border-border rounded-lg p-4">
                          <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                            <BarChart3 className="w-4 h-4 text-purple-400" />
                            P&L Projeksiyonu
                          </h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-400">Best Case:</span>
                              <span className="text-green-400 font-mono">+$4,580</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Expected:</span>
                              <span className="text-cyan-400 font-mono">+$2,290</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-400">Worst Case:</span>
                              <span className="text-red-400 font-mono">-$2,340</span>
                            </div>
                            <div className="flex justify-between border-t border-border pt-2 mt-2">
                              <span className="text-gray-400">Risk/Reward:</span>
                              <span className="text-white font-mono">1:1.96</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </GlassCard>
              </div>

              {/* Calculator Side Panel */}
              <div className="space-y-6">
                <GlassCard className="p-6">
                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-400" />
                    Hazır Presetler
                  </h4>
                  
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start">
                      <Target className="w-4 h-4 mr-2 text-yellow-400" />
                      Altın Scalping
                      <Badge variant="outline" className="ml-auto text-xs">
                        Agresif
                      </Badge>
                    </Button>
                    
                    <Button variant="outline" className="w-full justify-start">
                      <Gauge className="w-4 h-4 mr-2 text-green-400" />
                      Forex Konservatif
                      <Badge variant="outline" className="ml-auto text-xs">
                        Güvenli
                      </Badge>
                    </Button>
                    
                    <Button variant="outline" className="w-full justify-start">
                      <Flame className="w-4 h-4 mr-2 text-red-400" />
                      Kripto Agresif
                      <Badge variant="outline" className="ml-auto text-xs">
                        Yüksek Risk
                      </Badge>
                    </Button>

                    <Button variant="outline" className="w-full justify-start">
                      <Shield className="w-4 h-4 mr-2 text-blue-400" />
                      Güvenli Grid
                      <Badge variant="outline" className="ml-auto text-xs">
                        Düşük Risk
                      </Badge>
                    </Button>
                  </div>
                </GlassCard>

                <GlassCard className="p-6">
                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <Gauge className="w-4 h-4 text-cyan-400" />
                    Risk Göstergeleri
                  </h4>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Marjin Kullanımı</span>
                        <span className="text-white font-medium">15.3%</span>
                      </div>
                      <Progress value={15.3} className="h-2" />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Güvenli</span>
                        <span>Riskli</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Risk Seviyesi</span>
                        <span className="text-green-400 font-medium">Düşük</span>
                      </div>
                      <Progress value={25} className="h-2" />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Profit Potansiyeli</span>
                        <span className="text-cyan-400 font-medium">Yüksek</span>
                      </div>
                      <Progress value={78} className="h-2" />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Volatilite Uyumu</span>
                        <span className="text-yellow-400 font-medium">İyi</span>
                      </div>
                      <Progress value={65} className="h-2" />
                    </div>
                  </div>
                </GlassCard>

                <GlassCard className="p-6">
                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <Info className="w-4 h-4 text-blue-400" />
                    Sistem Durumu
                  </h4>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">MT5 Bağlantısı</span>
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Aktif
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Copy Trading</span>
                      <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        3 Hesap
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Grid Hesaplama</span>
                      <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Hazır
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">Market Verisi</span>
                      <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Canlı
                      </Badge>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          </TabsContent>

          {/* Presets */}
          <TabsContent value="presets" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              {Object.entries(presets).map(([key, preset]) => (
                <div 
                  key={key}
                  className="cursor-pointer"
                  onClick={() => handlePresetChange(key)}
                >
                  <GlassCard 
                    className={`p-6 transition-all ${
                      presetMode === key ? 'ring-2 ring-cyan-400' : 'hover:ring-1 hover:ring-gray-500'
                    }`}
                  >
                  <div className="text-center space-y-3">
                    <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                      <Star className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-white capitalize">{key}</h3>
                    <div className="space-y-2 text-sm text-gray-400">
                      <p>Grid Levels: {preset.grid_levels}</p>
                      <p>Initial Lot: {preset.initial_lot}</p>
                      <p>Risk: {preset.risk_percent}%</p>
                      <p>TP: {preset.tp_points} points</p>
                    </div>
                  </div>
                  </GlassCard>
                </div>
              ))}
            </motion.div>
          </TabsContent>
        </Tabs>

        {/* Save Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center"
        >
          <Button
            onClick={handleSave}
            disabled={isLoading}
            className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 px-8 py-3 text-lg"
          >
            {isLoading ? (
              <RefreshCw className="w-5 h-5 animate-spin mr-2" />
            ) : (
              <Save className="w-5 h-5 mr-2" />
            )}
            Save Settings
          </Button>
        </motion.div>
      </div>
    </QuantumLayout>
  );
} 