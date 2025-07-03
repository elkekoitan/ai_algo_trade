"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DollarSign, TrendingUp, Activity, Zap, Brain, Users, MessageSquare,
  Eye, Play, ChevronRight, Shield, BarChart3, Target, Bot, Copy,
  Mic, Settings, Bell, AlertTriangle, CheckCircle, ArrowUpRight,
  Layers, Sparkles, Rocket, Flame, Timer, Globe, Gauge, Award,
  Grid, Cpu, Star, Code, FileText, Sliders
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import useSWR from 'swr';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import QuantumLayout from '@/components/layout/QuantumLayout';
import GlassCard from '@/components/quantum/GlassCard';
import ParticleBackground from '@/components/quantum/ParticleBackground';

const fetcher = (url: string) => fetch(url).then(res => res.json());

// Animated Number Component
const AnimatedNumber = ({ value, prefix = '', suffix = '', decimals = 0 }: any) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 2000;
    const steps = 60;
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
  }, [value]);

  return (
    <span>{prefix}{displayValue.toFixed(decimals)}{suffix}</span>
  );
};

// Pulse Dot Component
const PulseDot = ({ color = 'green' }: { color?: string }) => {
  const colors = {
    green: 'bg-green-400',
    yellow: 'bg-yellow-400',
    red: 'bg-red-400',
    blue: 'bg-blue-400',
    purple: 'bg-purple-400'
  };

  return (
    <div className="relative">
      <motion.div
        className={`w-3 h-3 rounded-full ${colors[color as keyof typeof colors]}`}
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
        className={`absolute inset-0 rounded-full ${colors[color as keyof typeof colors]}`}
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
};

// System Status Component with Animation
const SystemStatus = () => {
  const { data, error } = useSWR('http://localhost:8002/health', fetcher, { refreshInterval: 10000 });
  const isConnected = data?.mt5_connected;
  const [statusMessage, setStatusMessage] = useState('Initializing...');

  useEffect(() => {
    const messages = [
      'Quantum cores synced',
      'Neural networks optimized',
      'Market analysis active',
      'Trading algorithms ready',
      'Real-time data flowing'
    ];
    
    const interval = setInterval(() => {
      setStatusMessage(messages[Math.floor(Math.random() * messages.length)]);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center space-x-3 px-4 py-2 rounded-xl backdrop-blur-xl bg-gradient-to-r ${
        isConnected 
          ? 'from-green-500/20 to-emerald-500/20 border border-green-500/30' 
          : 'from-yellow-500/20 to-orange-500/20 border border-yellow-500/30'
      }`}
    >
      <PulseDot color={isConnected ? 'green' : 'yellow'} />
      <div className="flex flex-col">
        <span className={`text-sm font-bold ${isConnected ? 'text-green-400' : 'text-yellow-400'}`}>
          {isConnected ? 'SYSTEM ONLINE' : 'CONNECTING...'}
        </span>
        <motion.span 
          key={statusMessage}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-gray-400"
        >
          {statusMessage}
        </motion.span>
      </div>
    </motion.div>
  );
};

// Enhanced Hero Cards Data with Quantum Design
const heroCards = [
  {
    id: 'trading',
    title: 'Live Trading Terminal',
    subtitle: 'Lightning-Fast Execution',
    description: 'Execute trades with quantum precision and institutional-grade technology',
    icon: TrendingUp,
    path: '/trading',
    gradient: 'from-blue-600 via-cyan-500 to-teal-400',
    borderGradient: 'from-blue-400 to-cyan-400',
    glowColor: 'cyan',
    features: ['0.001s Execution', 'Smart Orders', 'Risk Shield', 'Real-time Analysis'],
    metric: { label: 'Active Trades', value: 12, color: 'text-cyan-400' },
    sparkles: true,
    settingsPath: '/trading/settings'
  },
  {
    id: 'strategies',
    title: 'AI Strategy Engine',
    subtitle: 'Neural Evolution',
    description: 'Deploy self-evolving algorithms powered by advanced neural networks',
    icon: Bot,
    path: '/strategy-library',
    gradient: 'from-purple-600 via-pink-500 to-rose-400',
    borderGradient: 'from-purple-400 to-pink-400',
    glowColor: 'purple',
    features: ['Neural Networks', 'Auto-Evolution', 'Quantum Analysis', 'Backtesting'],
    metric: { label: 'Win Rate', value: 87.3, suffix: '%', color: 'text-purple-400' },
    pulse: true,
    settingsPath: '/strategy-library/settings'
  },
  {
    id: 'sanal_supurge',
    title: 'Sanal Süpürge Pro',
    subtitle: 'Fibonacci Grid Magic',
    description: 'Advanced Grid Trading with 3-account copy system - HAYALETV6 powered scalping',
    icon: Target,
    path: '/sanal-supurge',
    gradient: 'from-cyan-600 via-blue-500 to-indigo-400',
    borderGradient: 'from-cyan-400 to-blue-400',
    glowColor: 'cyan',
    features: ['Copy Trading x3', 'Grid 14-Level', 'Sub-50ms Latency', 'Fibonacci AI'],
    metric: { label: 'Copy Accounts', value: 3, color: 'text-cyan-400' },
    sparkles: true,
    pulse: true,
    special: true,
    settingsPath: '/sanal-supurge/settings'
  },
  {
    id: 'copy_trading',
    title: 'Elite Copy Network',
    subtitle: 'Mirror the Masters',
    description: 'Copy elite traders with millisecond precision and advanced risk management',
    icon: Copy,
    path: '/copy-trading',
    gradient: 'from-green-600 via-emerald-500 to-teal-400',
    borderGradient: 'from-green-400 to-emerald-400',
    glowColor: 'green',
    features: ['1,247 Pros', 'Auto-Scale', 'Risk Mirror', 'Smart Copy'],
    metric: { label: 'Copying', value: 3, color: 'text-green-400' },
    glow: true,
    settingsPath: '/copy-trading/settings'
  },
  {
    id: 'god_mode',
    title: 'God Mode Console',
    subtitle: 'Omniscient Vision',
    description: 'Prophetic market predictions with divine-level accuracy and foresight',
    icon: Brain,
    path: '/god-mode',
    gradient: 'from-yellow-600 via-orange-500 to-red-400',
    borderGradient: 'from-yellow-400 to-orange-400',
    glowColor: 'yellow',
    features: ['Future Sight', 'Quantum State', 'Divine Shield', 'Omniscient AI'],
    metric: { label: 'Accuracy', value: 94.7, suffix: '%', color: 'text-yellow-400' },
    rotate: true,
    settingsPath: '/god-mode/settings'
  },
  {
    id: 'shadow_mode',
    title: 'Shadow Mode',
    subtitle: 'Institutional Stealth',
    description: 'Track institutional movements and execute stealth trades in dark pools',
    icon: Eye,
    path: '/shadow',
    gradient: 'from-gray-600 via-slate-500 to-zinc-400',
    borderGradient: 'from-gray-400 to-slate-400',
    glowColor: 'gray',
    features: ['Dark Pool Monitor', 'Institutional Radar', 'Stealth Mode', 'Shadow Execution'],
    metric: { label: 'Tracked Institutions', value: 247, color: 'text-gray-400' },
    stealth: true,
    settingsPath: '/shadow/settings'
  },
  {
    id: 'market_narrator',
    title: 'Market Narrator',
    subtitle: 'AI Storyteller',
    description: 'Transform complex market data into compelling narratives and insights',
    icon: MessageSquare,
    path: '/market-narrator',
    gradient: 'from-indigo-600 via-purple-500 to-pink-400',
    borderGradient: 'from-indigo-400 to-purple-400',
    glowColor: 'indigo',
    features: ['Story Generation', 'Sentiment Analysis', 'Narrative Insights', 'AI Storytelling'],
    metric: { label: 'Stories Generated', value: 1247, color: 'text-indigo-400' },
    narrative: true,
    settingsPath: '/market-narrator/settings'
  },
  {
    id: 'strategy_whisperer',
    title: 'Strategy Whisperer',
    subtitle: 'Natural Language AI',
    description: 'Create trading strategies using natural language and deploy them instantly',
    icon: Sparkles,
    path: '/strategy-whisperer',
    gradient: 'from-pink-600 via-rose-500 to-orange-400',
    borderGradient: 'from-pink-400 to-rose-400',
    glowColor: 'pink',
    features: ['Natural Language', 'Code Generation', 'Auto-Deploy', 'AI Whispering'],
    metric: { label: 'Strategies Created', value: 89, color: 'text-pink-400' },
    magical: true,
    settingsPath: '/strategy-whisperer/settings'
  }
];

// Enhanced Performance Stats with Animations
const PerformanceStats = () => {
  const { data } = useSWR('http://localhost:8002/api/v1/sanal-supurge/multi-status', fetcher, { refreshInterval: 3000 });
  const { data: perfData } = useSWR('http://localhost:8002/api/v1/sanal-supurge/multi-performance', fetcher, { refreshInterval: 3000 });
  
  const strategyData = data?.data || {};
  const perfDataInfo = perfData?.data || {};
  const totalProfit = strategyData.total_profit || 0;
  const totalPositions = strategyData.total_positions || 0;
  const winRate = perfDataInfo.overall_performance?.win_rate || 0;
  const riskLevel = perfDataInfo.risk_assessment?.overall_risk || 'Unknown';

  const stats = [
    {
      icon: DollarSign,
      label: 'Total P&L',
      value: totalProfit,
      prefix: '$',
      decimals: 2,
      color: totalProfit >= 0 ? 'text-green-400' : 'text-red-400',
      bgColor: totalProfit >= 0 ? 'from-green-900/30 to-emerald-900/30' : 'from-red-900/30 to-pink-900/30',
      borderColor: totalProfit >= 0 ? 'border-green-500/30' : 'border-red-500/30',
      trend: totalProfit >= 0 ? 'up' : 'down',
      sparkline: true
    },
    {
      icon: Activity,
      label: 'Active Positions',
      value: totalPositions,
      color: 'text-blue-400',
      bgColor: 'from-blue-900/30 to-cyan-900/30',
      borderColor: 'border-blue-500/30',
      progress: (totalPositions / 20) * 100,
      maxLabel: '20 max'
    },
    {
      icon: Target,
      label: 'Win Rate',
      value: winRate,
      suffix: '%',
      decimals: 1,
      color: 'text-purple-400',
      bgColor: 'from-purple-900/30 to-pink-900/30',
      borderColor: 'border-purple-500/30',
      gauge: true
    },
    {
      icon: Shield,
      label: 'Risk Level',
      value: riskLevel,
      isText: true,
      color: riskLevel === 'Low' ? 'text-green-400' : riskLevel === 'Medium' ? 'text-yellow-400' : 'text-red-400',
      bgColor: 'from-yellow-900/30 to-orange-900/30',
      borderColor: 'border-yellow-500/30',
      pulse: riskLevel !== 'Low'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card className={`bg-gradient-to-br ${stat.bgColor} ${stat.borderColor} border relative overflow-hidden`}>
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `radial-gradient(circle at 20% 50%, ${stat.color} 0%, transparent 50%)`,
              }} />
            </div>
            
            <CardContent className="p-4 relative z-10">
              <div className="flex items-center justify-between mb-2">
          <div>
                  <p className={`${stat.color} text-sm font-medium flex items-center gap-2`}>
                    {stat.label}
                    {stat.pulse && <PulseDot color={stat.color.includes('green') ? 'green' : stat.color.includes('yellow') ? 'yellow' : 'red'} />}
                  </p>
                  <div className={`text-2xl font-bold ${stat.color} flex items-center gap-2`}>
                    {stat.isText ? (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.5 }}
                      >
                        {stat.value}
                      </motion.span>
                    ) : (
                      <AnimatedNumber 
                        value={stat.value} 
                        prefix={stat.prefix} 
                        suffix={stat.suffix} 
                        decimals={stat.decimals || 0} 
                      />
                    )}
                    {stat.trend && (
                      <motion.div
                        initial={{ rotate: stat.trend === 'up' ? -45 : 45 }}
                        animate={{ rotate: stat.trend === 'up' ? 0 : 90 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <TrendingUp className={`h-4 w-4 ${stat.trend === 'up' ? 'text-green-400' : 'text-red-400 rotate-180'}`} />
                      </motion.div>
            )}
          </div>
                </div>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                >
                  <stat.icon className={`h-8 w-8 ${stat.color}`} />
                </motion.div>
        </div>
        
              {stat.progress !== undefined && (
                <div className="mt-2">
                  <Progress value={stat.progress} className="h-1.5" />
                  <p className="text-xs text-gray-500 mt-1">{stat.maxLabel}</p>
          </div>
        )}
              
              {stat.sparkline && (
                <motion.div className="mt-2 h-8 flex items-end gap-0.5">
                  {[...Array(12)].map((_, i) => (
                    <motion.div
                      key={i}
                      className={`flex-1 ${totalProfit >= 0 ? 'bg-green-400' : 'bg-red-400'} rounded-t`}
                      initial={{ height: 0 }}
                      animate={{ height: `${20 + Math.random() * 60}%` }}
                      transition={{ delay: i * 0.05, duration: 0.5 }}
                    />
                  ))}
                </motion.div>
              )}
              
              {stat.gauge && (
                <div className="mt-2 relative h-2 bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${winRate}%` }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
        </div>
              )}
      </CardContent>
    </Card>
        </motion.div>
      ))}
    </div>
  );
};

// Quick Actions with Enhanced Animations
const QuickActions = () => {
  const actions = [
    { icon: TrendingUp, label: 'Start Trading', path: '/trading', color: 'from-blue-600 to-cyan-600' },
    { icon: MessageSquare, label: 'Create Strategy', path: '/strategy-whisperer', color: 'from-purple-600 to-pink-600' },
    { icon: Copy, label: 'Copy Traders', path: '/copy-trading', color: 'from-green-600 to-emerald-600' },
    { icon: BarChart3, label: 'View Analytics', path: '/performance', color: 'from-orange-600 to-red-600' }
  ];

  return (
    <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700 mb-8 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-transparent to-cyan-500/5" />
      
      <CardHeader className="relative z-10">
        <CardTitle className="text-white flex items-center">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Zap className="h-5 w-5 mr-2 text-yellow-400" />
          </motion.div>
          Quick Actions
          <motion.span
            className="ml-2 text-xs text-gray-400"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            • READY
          </motion.span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {actions.map((action, index) => (
            <motion.div
              key={action.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link href={action.path}>
                <Button className={`w-full bg-gradient-to-r ${action.color} hover:opacity-90 text-white border-0 shadow-lg`}>
                  <action.icon className="w-4 h-4 mr-2" />
                  {action.label}
                </Button>
              </Link>
            </motion.div>
          ))}
          </div>
      </CardContent>
    </Card>
  );
};

// Enhanced Hero Card Component with Quantum Design
const QuantumHeroCard = ({ card, index }: { card: any; index: number }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), index * 100);
    return () => clearTimeout(timer);
  }, [index]);

  const handleCardClick = () => {
    router.push(card.path);
  };

  const handleSettingsClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (card.settingsPath) {
      router.push(card.settingsPath);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ 
        opacity: isVisible ? 1 : 0, 
        y: isVisible ? 0 : 50,
        scale: isVisible ? 1 : 0.9
      }}
      transition={{ 
        duration: 0.6,
        delay: index * 0.1,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      className="relative group cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
    >
      <GlassCard
        className={`relative h-full transition-all duration-500 ${
          isHovered 
            ? 'transform scale-105 shadow-2xl' 
            : 'transform scale-100'
        }`}
        variant="hologram"
        glow={card.glow}
      >
        {/* Glow Effect */}
        {isHovered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`absolute inset-0 rounded-2xl blur-xl bg-gradient-to-r ${card.gradient} opacity-30 -z-10`}
          />
        )}

        {/* Settings Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
            animate={{
            opacity: isHovered ? 1 : 0,
            scale: isHovered ? 1 : 0.5
          }}
          className="absolute top-4 right-4 z-20"
        >
          <Button
            variant="ghost"
            size="sm"
            className="p-2 h-8 w-8 rounded-full bg-black/20 backdrop-blur-sm hover:bg-black/30 transition-colors"
            onClick={handleSettingsClick}
          >
            <Settings size={14} />
          </Button>
        </motion.div>

        {/* Special Effects */}
          {card.sparkles && (
                <motion.div
                  animate={{
              opacity: [0.5, 1, 0.5],
              scale: [1, 1.1, 1],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
              ease: "easeInOut"
                  }}
            className="absolute top-4 left-4"
          >
            <Sparkles className="w-6 h-6 text-yellow-400" />
          </motion.div>
          )}

        {card.special && (
          <motion.div
            animate={{
              rotate: [0, 360],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "linear"
            }}
            className="absolute top-4 left-4"
          >
            <Star className="w-6 h-6 text-cyan-400" />
          </motion.div>
        )}

        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                    animate={{
                  rotate: card.rotate ? [0, 360] : 0,
                  scale: isHovered ? 1.1 : 1
                    }}
                transition={{
                  rotate: { duration: 4, repeat: Infinity, ease: "linear" },
                  scale: { duration: 0.3 }
                }}
                className={`p-3 rounded-xl bg-gradient-to-r ${card.borderGradient} bg-opacity-20`}
              >
                <card.icon className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <CardTitle className="text-xl font-bold text-white mb-1">
                  {card.title}
                </CardTitle>
                <p className={`text-sm ${card.metric.color} font-semibold`}>
                  {card.subtitle}
                </p>
                  </div>
              </div>
            
            <Badge 
              className={`bg-gradient-to-r ${card.borderGradient} bg-opacity-20 text-white border-0`}
            >
              {card.metric.label}
            </Badge>
          </div>
      </CardHeader>
        
        <CardContent className="pt-0">
          <p className="text-gray-300 text-sm mb-4 line-clamp-2">
            {card.description}
          </p>
          
          {/* Features */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            {card.features.map((feature: string, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ 
                  opacity: isVisible ? 1 : 0,
                  x: isVisible ? 0 : -20
                }}
                transition={{ delay: (index * 0.1) + (idx * 0.05) }}
                className="flex items-center space-x-2"
              >
                <CheckCircle className="w-3 h-3 text-green-400" />
                <span className="text-xs text-gray-400">{feature}</span>
              </motion.div>
            ))}
          </div>

          {/* Metric */}
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-white">
              <AnimatedNumber 
                value={card.metric.value} 
                suffix={card.metric.suffix || ''}
                decimals={card.metric.suffix ? 1 : 0}
            />
            </div>
        <motion.div
              whileHover={{ scale: 1.1 }}
              className="flex items-center space-x-2 text-gray-400"
            >
              <span className="text-sm">Launch</span>
              <ArrowUpRight className="w-4 h-4" />
            </motion.div>
          </div>
        </CardContent>
      </GlassCard>
    </motion.div>
  );
};

// Active Strategy Monitor Component
const ActiveStrategyMonitor = () => {
  const { data } = useSWR('http://localhost:8002/api/v1/sanal-supurge/multi-status', fetcher, { refreshInterval: 3000 });
  const strategyData = data?.data || {};
  const totalProfit = strategyData.total_profit || 0;
  const activeSymbols = Object.keys(strategyData.symbol_breakdown || {});

  const strategies = [
    {
      id: 'sanal_supurge',
      name: 'Sanal Süpürge V1',
      description: 'Multi-symbol quantum grid system',
      status: 'active',
      profit: totalProfit,
      symbols: activeSymbols,
      gridLevels: 14,
      activeGrids: strategyData.total_positions || 0,
      performance: {
        today: +2.34,
        week: +8.92,
        month: +24.67
      }
    },
    {
      id: 'neural_scalper',
      name: 'Neural Scalper Pro',
      description: 'AI-powered microsecond execution',
      status: 'preparing',
      profit: 0,
      symbols: ['GBPUSD', 'USDJPY'],
      performance: {
        today: 0,
        week: 0,
        month: 0
      }
    },
    {
      id: 'quantum_arbitrage',
      name: 'Quantum Arbitrage',
      description: 'Cross-exchange opportunity hunter',
      status: 'inactive',
      profit: 0,
      symbols: ['BTCUSD', 'ETHUSD'],
      performance: {
        today: 0,
        week: 0,
        month: 0
      }
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="mt-8"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Rocket className="h-6 w-6 mr-2 text-orange-400" />
          Strategy Command Center
        </h2>
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex items-center gap-2 text-sm text-gray-400"
        >
          <Timer className="h-4 w-4" />
          Real-time monitoring active
        </motion.div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {strategies.map((strategy, index) => (
          <motion.div
            key={strategy.id}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.15 }}
            whileHover={{ scale: 1.02 }}
          >
            <Card className={`relative overflow-hidden bg-gradient-to-br ${
              strategy.status === 'active' 
                ? 'from-purple-900/50 to-blue-900/50 border-purple-500/50' 
                : strategy.status === 'preparing'
                ? 'from-yellow-900/50 to-orange-900/50 border-yellow-500/50'
                : 'from-gray-900/50 to-slate-900/50 border-gray-700'
            }`}>
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 opacity-5">
                <motion.div
                  className="absolute inset-0"
                  style={{
                    backgroundImage: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.4"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
                  }}
                  animate={{ 
                    x: [0, 30, 0],
                    y: [0, -30, 0]
                  }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                />
              </div>

              <CardContent className="p-4 relative z-10">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-white font-bold text-lg flex items-center gap-2">
                      {strategy.name}
                      {strategy.status === 'active' && <PulseDot color="green" />}
                      {strategy.status === 'preparing' && <PulseDot color="yellow" />}
                    </h3>
                    <p className="text-gray-400 text-sm">{strategy.description}</p>
                  </div>
                  <motion.div
                    animate={strategy.status === 'active' ? { rotate: 360 } : {}}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  >
                    <Settings className={`h-5 w-5 ${
                      strategy.status === 'active' ? 'text-green-400' : 
                      strategy.status === 'preparing' ? 'text-yellow-400' : 'text-gray-500'
                    }`} />
                  </motion.div>
                </div>

                {/* Profit Display */}
                {strategy.status === 'active' && (
                  <div className="mb-4">
                    <div className={`text-2xl font-bold ${strategy.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      <AnimatedNumber value={strategy.profit} prefix="$" decimals={2} />
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-xs">
                      <span className="text-gray-400">Today:</span>
                      <span className={strategy.performance.today >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {strategy.performance.today >= 0 ? '+' : ''}{strategy.performance.today}%
                      </span>
                      <span className="text-gray-400">Week:</span>
                      <span className={strategy.performance.week >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {strategy.performance.week >= 0 ? '+' : ''}{strategy.performance.week}%
                      </span>
                    </div>
                  </div>
                )}

                {/* Grid Levels for Sanal Süpürge */}
                {strategy.id === 'sanal_supurge' && strategy.status === 'active' && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-400">Grid Status</span>
                      <span className="text-xs text-cyan-400">
                        {strategy.activeGrids}/{strategy.gridLevels} Active
                      </span>
                    </div>
                    <div className="grid grid-cols-14 gap-0.5">
                      {[...Array(14)].map((_, i) => (
                        <motion.div
                          key={i}
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: i * 0.03 }}
                          className={`h-2 rounded-sm ${
                            i < strategy.activeGrids 
                              ? 'bg-gradient-to-t from-green-500 to-emerald-400' 
                              : 'bg-gray-700'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Symbols */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {strategy.symbols.map((symbol, i) => (
                    <motion.span
                      key={symbol}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                      className="px-2 py-1 bg-black/30 rounded text-xs text-gray-300 border border-gray-700"
                    >
                      {symbol}
                    </motion.span>
                  ))}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  {strategy.status === 'active' ? (
                    <>
                      <Link href="/trading" className="flex-1">
                        <Button 
                          size="sm" 
                          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0"
                        >
                          <Gauge className="w-3 h-3 mr-1" />
                          Monitor
                        </Button>
                      </Link>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="border-red-500/50 text-red-400 hover:bg-red-500/20"
                      >
                        Stop
                      </Button>
                    </>
                  ) : strategy.status === 'preparing' ? (
                    <Button 
                      size="sm" 
                      className="w-full bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white border-0"
                    >
                      <Timer className="w-3 h-3 mr-1" />
                      Preparing...
                    </Button>
                  ) : (
                    <Link href="/strategy-whisperer" className="w-full">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="w-full border-gray-600 text-gray-400 hover:bg-gray-800"
                      >
                        <Sparkles className="w-3 h-3 mr-1" />
                        Configure
                      </Button>
                    </Link>
                  )}
                </div>
          </CardContent>

              {/* Status Indicator */}
              <motion.div
                className={`absolute top-0 left-0 right-0 h-0.5 ${
                  strategy.status === 'active' ? 'bg-gradient-to-r from-green-400 to-emerald-400' :
                  strategy.status === 'preparing' ? 'bg-gradient-to-r from-yellow-400 to-orange-400' :
                  'bg-gray-700'
                }`}
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
        </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

// Market Activity Ticker
const MarketActivityTicker = () => {
  const activities = [
    { symbol: 'EURUSD', action: 'BUY', price: '1.1768', time: 'Just now', profit: '+$0.45' },
    { symbol: 'XAUUSD', action: 'SELL', price: '3334.68', time: '2 min ago', profit: '+$1.20' },
    { symbol: 'ETHUSD', action: 'BUY', price: '2455.07', time: '5 min ago', profit: '-$0.30' },
    { symbol: 'GBPUSD', action: 'CLOSE', price: '1.3245', time: '7 min ago', profit: '+$2.85' }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 mb-6"
    >
      <Card className="bg-gradient-to-r from-gray-900/50 via-slate-900/50 to-gray-900/50 border-gray-700 overflow-hidden">
        <CardContent className="p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="h-4 w-4 text-cyan-400" />
              <span className="text-sm font-semibold text-white">Live Market Activity</span>
              <PulseDot color="green" />
      </div>

            <motion.div className="flex items-center gap-6 overflow-hidden">
              {activities.map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ x: 300, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.2 }}
                  className="flex items-center gap-3 text-sm"
                >
                  <span className="text-gray-400">{activity.symbol}</span>
                  <span className={`font-semibold ${
                    activity.action === 'BUY' ? 'text-green-400' : 
                    activity.action === 'SELL' ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {activity.action}
                  </span>
                  <span className="text-gray-300">@{activity.price}</span>
                  <span className={`font-bold ${
                    activity.profit.startsWith('+') ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {activity.profit}
                  </span>
                  <span className="text-gray-500 text-xs">{activity.time}</span>
                </motion.div>
              ))}
            </motion.div>
        </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default function Dashboard() {
  const { data, error } = useSWR('http://localhost:8002/health', fetcher, { refreshInterval: 10000 });
  const [showParticles, setShowParticles] = useState(true);

  return (
    <QuantumLayout>
      <div className="relative min-h-screen">
        {/* Particle Background */}
        {showParticles && (
          <ParticleBackground 
            className="absolute inset-0 z-0"
            particleCount={100}
            colors={["#00ffff", "#00bfff", "#4169e1"]}
        />
        )}

      {/* Main Content */}
        <div className="relative z-10 p-6 space-y-8">
          {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
        >
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              AI Algo Trade Command Center
              </h1>
            <p className="text-gray-400 text-lg">
              Next-generation algorithmic trading platform powered by quantum AI
            </p>
          <SystemStatus />
        </motion.div>

        {/* Performance Stats */}
        <PerformanceStats />

        {/* Hero Cards Grid */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
          {heroCards.map((card, index) => (
              <QuantumHeroCard key={card.id} card={card} index={index} />
          ))}
          </motion.div>

          {/* Quick Actions */}
          <QuickActions />

          {/* Strategy Monitor */}
        <ActiveStrategyMonitor />

          {/* Market Activity */}
          <MarketActivityTicker />
      </div>
    </div>
    </QuantumLayout>
  );
} 