"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Copy, 
  TrendingUp, 
  TrendingDown,
  Filter,
  Search,
  Star,
  DollarSign,
  Shield,
  Award,
  BarChart3,
  Settings,
  Plus,
  Zap,
  Target,
  Brain,
  CheckCircle,
  AlertTriangle,
  PlayCircle,
  Pause,
  Globe,
  Clock,
  ChevronRight,
  Sparkles,
  AlertCircle,
  Activity,
  Trophy,
  Crown,
  Medal,
  Flame,
  Timer,
  Lock,
  Unlock,
  Eye
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import useSWR from 'swr';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const fetcher = (url: string) => fetch(url).then(res => res.json());

interface TraderProfile {
  trader_id: string;
  display_name: string;
  avatar_url?: string;
  tier: string;
  total_return: number;
  monthly_return: number;
  win_rate: number;
  profit_factor: number;
  max_drawdown: number;
  sharpe_ratio: number;
  followers_count: number;
  rating: number;
  risk_level: string;
  is_premium: boolean;
  subscription_fee: number;
  min_copy_amount: number;
  last_trade_time?: string;
}

interface CopySettings {
  copy_amount: number;
  copy_ratio: number;
  max_daily_loss: number;
  max_open_positions: number;
  stop_loss_buffer: number;
  take_profit_buffer: number;
}

// Animated Counter
const AnimatedCounter = ({ value, prefix = '', suffix = '', decimals = 0, duration = 2000 }: any) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = (timestamp - startTime) / duration;
      
      if (progress < 1) {
        setCount(value * progress);
        animationFrame = requestAnimationFrame(animate);
      } else {
        setCount(value);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);
  
  return (
    <span>{prefix}{count.toFixed(decimals)}{suffix}</span>
  );
};

// Pulse Badge Component
const PulseBadge = ({ children, color = 'bg-green-400' }: any) => (
  <div className="relative inline-flex">
    <Badge className={`${color.replace('bg-', 'bg-opacity-20 text-')} border-0`}>
      {children}
    </Badge>
    <motion.div
      className={`absolute inset-0 rounded-full ${color} opacity-25`}
      animate={{
        scale: [1, 1.3, 1],
        opacity: [0.5, 0, 0.5]
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  </div>
);

// Trading Performance Sparkline
const Sparkline = ({ data, color = 'text-green-400' }: { data: number[], color?: string }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  return (
    <div className="flex items-end h-8 gap-0.5">
      {data.map((value, i) => (
        <motion.div
          key={i}
          className={`flex-1 ${color.replace('text-', 'bg-')} rounded-t opacity-60`}
          initial={{ height: 0 }}
          animate={{ height: `${((value - min) / range) * 100}%` }}
          transition={{ delay: i * 0.05, duration: 0.5 }}
        />
      ))}
    </div>
  );
};

// Enhanced Trader Card
const EnhancedTraderCard = ({ trader, rank }: { trader: any, rank: number }) => {
  const [isFollowing, setIsFollowing] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const getTierIcon = (tier: string) => {
    switch(tier) {
      case 'Diamond': return <Crown className="h-4 w-4 text-cyan-400" />;
      case 'Gold': return <Medal className="h-4 w-4 text-yellow-400" />;
      case 'Silver': return <Medal className="h-4 w-4 text-gray-400" />;
      default: return <Star className="h-4 w-4 text-bronze-400" />;
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return { icon: '🥇', color: 'from-yellow-500 to-amber-500' };
    if (rank === 2) return { icon: '🥈', color: 'from-gray-400 to-slate-400' };
    if (rank === 3) return { icon: '🥉', color: 'from-orange-600 to-amber-600' };
    return null;
  };

  const rankBadge = getRankBadge(rank);

    return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.1 }}
      whileHover={{ y: -5 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <Card className={`relative overflow-hidden bg-gradient-to-br ${
        trader.tier === 'Diamond' ? 'from-cyan-900/30 to-blue-900/30 border-cyan-500/30' :
        trader.tier === 'Gold' ? 'from-yellow-900/30 to-amber-900/30 border-yellow-500/30' :
        trader.tier === 'Silver' ? 'from-gray-800/30 to-slate-800/30 border-gray-500/30' :
        'from-gray-900/30 to-slate-900/30 border-gray-700'
      } group transition-all duration-300`}>
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-10">
          <motion.div
            className="absolute inset-0"
            style={{
              backgroundImage: `radial-gradient(circle at ${isHovered ? '50%' : '0%'} 0%, ${
                trader.tier === 'Diamond' ? '#06b6d4' :
                trader.tier === 'Gold' ? '#eab308' :
                trader.tier === 'Silver' ? '#9ca3af' : '#6b7280'
              } 0%, transparent 70%)`,
            }}
            animate={{ 
              opacity: isHovered ? 0.3 : 0.1,
              scale: isHovered ? 1.5 : 1
            }}
            transition={{ duration: 0.5 }}
          />
        </div>

        {/* Rank Badge */}
        {rankBadge && (
          <motion.div
            className={`absolute top-2 right-2 w-12 h-12 rounded-full bg-gradient-to-br ${rankBadge.color} flex items-center justify-center shadow-lg z-20`}
            animate={{ rotate: isHovered ? 360 : 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="text-2xl">{rankBadge.icon}</span>
          </motion.div>
        )}

        <CardHeader className="relative z-10">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                whileHover={{ scale: 1.1 }}
                className="relative"
              >
                <Avatar className="h-12 w-12 border-2 border-gray-700">
                  <AvatarImage src={trader.avatar} />
                  <AvatarFallback>{trader.name.charAt(0)}</AvatarFallback>
                </Avatar>
                {trader.isOnline && (
                  <motion.div
                    className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-gray-900"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [1, 0.8, 1]
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity
                    }}
                  />
                )}
              </motion.div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white">{trader.name}</h3>
                  {getTierIcon(trader.tier)}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className="text-xs border-gray-600">
                    {trader.strategy}
                  </Badge>
                  <span className="text-xs text-gray-400">• {trader.experience}</span>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="relative z-10 space-y-4">
          {/* Performance Stats Grid */}
          <div className="grid grid-cols-3 gap-3">
            <motion.div
              className="text-center p-3 rounded-lg bg-black/20 border border-gray-800"
              whileHover={{ scale: 1.05 }}
            >
              <p className="text-xs text-gray-400 mb-1">Total Return</p>
              <p className={`text-lg font-bold ${trader.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                <AnimatedCounter value={trader.totalReturn} suffix="%" decimals={1} />
              </p>
            </motion.div>
            <motion.div
              className="text-center p-3 rounded-lg bg-black/20 border border-gray-800"
              whileHover={{ scale: 1.05 }}
            >
              <p className="text-xs text-gray-400 mb-1">Win Rate</p>
              <p className="text-lg font-bold text-purple-400">
                <AnimatedCounter value={trader.winRate} suffix="%" />
              </p>
            </motion.div>
            <motion.div
              className="text-center p-3 rounded-lg bg-black/20 border border-gray-800"
              whileHover={{ scale: 1.05 }}
            >
              <p className="text-xs text-gray-400 mb-1">Copiers</p>
              <p className="text-lg font-bold text-blue-400">
                <AnimatedCounter value={trader.copiers} />
              </p>
            </motion.div>
          </div>

          {/* Monthly Performance Sparkline */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Monthly Performance</span>
              <span className="text-xs text-gray-500">Last 12 months</span>
            </div>
            <Sparkline 
              data={trader.monthlyReturns} 
              color={trader.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'} 
            />
              </div>
              
          {/* Risk Score */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Risk Level</span>
              <Badge className={`text-xs ${
                trader.riskScore <= 3 ? 'bg-green-500/20 text-green-400' :
                trader.riskScore <= 6 ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              } border-0`}>
                {trader.riskScore <= 3 ? 'Low' : trader.riskScore <= 6 ? 'Medium' : 'High'}
              </Badge>
            </div>
            <Progress 
              value={trader.riskScore * 10} 
              className="h-2 bg-gray-800"
            />
          </div>

          {/* Trading Stats */}
          <div className="flex items-center justify-between py-2 border-t border-gray-800">
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3 text-gray-500" />
                <span className="text-gray-400">{trader.avgHoldTime}</span>
              </div>
              <div className="flex items-center gap-1">
                <Activity className="h-3 w-3 text-gray-500" />
                <span className="text-gray-400">{trader.tradesPerWeek} trades/week</span>
              </div>
                  </div>
                </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <motion.div
              className="flex-1"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button 
                className={`w-full ${
                  isFollowing 
                    ? 'bg-gray-700 hover:bg-gray-600' 
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                } text-white border-0`}
                onClick={() => setIsFollowing(!isFollowing)}
              >
                {isFollowing ? (
                  <>
                    <Eye className="w-4 h-4 mr-2" />
                    Following
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy Trader
                  </>
                )}
              </Button>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button variant="outline" size="icon" className="border-gray-600">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </motion.div>
                </div>

          {/* Copy Settings (if following) */}
          <AnimatePresence>
            {isFollowing && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-3 pt-3 border-t border-gray-800"
              >
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Copy Amount</span>
                  <span className="text-sm font-medium text-white">$1,000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Risk Level</span>
                  <Select defaultValue="medium">
                    <SelectTrigger className="w-24 h-7 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>

        {/* Status Bar */}
        <motion.div
          className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${
            trader.tier === 'Diamond' ? 'from-cyan-400 to-blue-400' :
            trader.tier === 'Gold' ? 'from-yellow-400 to-amber-400' :
            trader.tier === 'Silver' ? 'from-gray-400 to-slate-400' :
            'from-gray-600 to-gray-700'
          }`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </Card>
    </motion.div>
  );
};

// Leaderboard Component
const Leaderboard = () => {
  const topTraders = [
    { name: 'Master Wolf', profit: 2847.50, winRate: 89, rank: 1 },
    { name: 'Golden Eagle', profit: 2234.75, winRate: 85, rank: 2 },
    { name: 'Silver Fox', profit: 1876.25, winRate: 82, rank: 3 },
    { name: 'Crypto King', profit: 1543.00, winRate: 78, rank: 4 },
    { name: 'Trend Hunter', profit: 1234.50, winRate: 75, rank: 5 }
  ];

  return (
    <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Trophy className="h-5 w-5 text-yellow-400" />
          Today's Top Performers
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {topTraders.map((trader, idx) => (
            <motion.div
              key={trader.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-center justify-between p-3 rounded-lg ${
                trader.rank <= 3 
                  ? 'bg-gradient-to-r from-yellow-900/20 to-amber-900/20 border border-yellow-500/20' 
                  : 'bg-black/20 border border-gray-800'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`text-lg font-bold ${
                  trader.rank === 1 ? 'text-yellow-400' :
                  trader.rank === 2 ? 'text-gray-400' :
                  trader.rank === 3 ? 'text-orange-400' :
                  'text-gray-500'
                }`}>
                  #{trader.rank}
                </span>
                <div>
                  <p className="font-medium text-white">{trader.name}</p>
                  <p className="text-xs text-gray-400">Win Rate: {trader.winRate}%</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-green-400">+${trader.profit}</p>
                <p className="text-xs text-gray-500">Today</p>
              </div>
            </motion.div>
          ))}
                </div>
      </CardContent>
    </Card>
  );
};

// Stats Overview
const StatsOverview = () => {
  const stats = [
    { label: 'Total Traders', value: 1247, icon: Users, color: 'from-blue-600 to-cyan-600' },
    { label: 'Active Copiers', value: 8934, icon: Copy, color: 'from-purple-600 to-pink-600' },
    { label: 'Total Profit', value: 458750, prefix: '$', icon: DollarSign, color: 'from-green-600 to-emerald-600' },
    { label: 'Avg Win Rate', value: 73.4, suffix: '%', icon: Target, color: 'from-orange-600 to-red-600' }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, idx) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          whileHover={{ scale: 1.05 }}
        >
          <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700 relative overflow-hidden">
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-10`} />
            <CardContent className="p-4 relative z-10">
              <div className="flex items-center justify-between mb-2">
                <stat.icon className="h-5 w-5 text-gray-400" />
                <motion.div
                  animate={{ 
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{ 
                    duration: 3, 
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className={`w-2 h-2 rounded-full bg-gradient-to-r ${stat.color}`}
                />
              </div>
              <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-white">
                <AnimatedCounter 
                  value={stat.value} 
                  prefix={stat.prefix} 
                  suffix={stat.suffix} 
                  decimals={stat.suffix === '%' ? 1 : 0}
                />
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
};

export default function CopyTradingPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTier, setFilterTier] = useState('all');
  const [sortBy, setSortBy] = useState('profit');

  const { data } = useSWR('http://localhost:8002/api/v1/copy-trading/status', fetcher, { refreshInterval: 10000 });
  const status = data?.data || {};

  // Mock traders data
  const traders = [
    {
      id: 1,
      name: 'Master Wolf',
      avatar: '/avatars/trader1.jpg',
      tier: 'Diamond',
      strategy: 'Trend Following',
      experience: '5 years',
      totalReturn: 2847.5,
      winRate: 89,
      copiers: 1234,
      riskScore: 3,
      avgHoldTime: '2-3 days',
      tradesPerWeek: 15,
      monthlyReturns: [12, 8, 15, -3, 22, 18, 25, 19, 14, 28, 32, 24],
      isOnline: true
    },
    {
      id: 2,
      name: 'Golden Eagle',
      avatar: '/avatars/trader2.jpg',
      tier: 'Gold',
      strategy: 'Scalping',
      experience: '3 years',
      totalReturn: 1834.2,
      winRate: 85,
      copiers: 987,
      riskScore: 5,
      avgHoldTime: '5-10 min',
      tradesPerWeek: 120,
      monthlyReturns: [8, 12, 10, 15, 18, -5, 20, 16, 22, 19, 14, 17],
      isOnline: true
    },
    {
      id: 3,
      name: 'Silver Fox',
      avatar: '/avatars/trader3.jpg',
      tier: 'Silver',
      strategy: 'Swing Trading',
      experience: '4 years',
      totalReturn: 1245.7,
      winRate: 78,
      copiers: 654,
      riskScore: 4,
      avgHoldTime: '3-5 days',
      tradesPerWeek: 8,
      monthlyReturns: [5, 8, 12, 10, -2, 15, 11, 9, 13, 16, 14, 10],
      isOnline: false
    },
    {
      id: 4,
      name: 'Crypto King',
      avatar: '/avatars/trader4.jpg',
      tier: 'Diamond',
      strategy: 'DeFi Arbitrage',
      experience: '2 years',
      totalReturn: 3256.8,
      winRate: 92,
      copiers: 2341,
      riskScore: 7,
      avgHoldTime: '1-2 hours',
      tradesPerWeek: 200,
      monthlyReturns: [25, 30, 28, 35, -10, 40, 38, 42, 35, 45, 50, 48],
      isOnline: true
    },
    {
      id: 5,
      name: 'Trend Hunter',
      avatar: '/avatars/trader5.jpg',
      tier: 'Gold',
      strategy: 'AI Pattern',
      experience: '1 year',
      totalReturn: 987.3,
      winRate: 82,
      copiers: 432,
      riskScore: 6,
      avgHoldTime: '1-2 days',
      tradesPerWeek: 25,
      monthlyReturns: [8, 6, 12, 15, 10, 18, -5, 20, 16, 14, 22, 19],
      isOnline: false
    },
    {
      id: 6,
      name: 'Wave Rider',
      avatar: '/avatars/trader6.jpg',
      tier: 'Bronze',
      strategy: 'Elliott Wave',
      experience: '6 months',
      totalReturn: 234.5,
      winRate: 72,
      copiers: 123,
      riskScore: 8,
      avgHoldTime: '4-8 hours',
      tradesPerWeek: 30,
      monthlyReturns: [3, 5, -2, 8, 6, 10, 12, -4, 15, 11, 9, 7],
      isOnline: true
    }
  ];

  // Filter and sort traders
  const filteredTraders = traders
    .filter(trader => {
      const matchesSearch = trader.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          trader.strategy.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesTier = filterTier === 'all' || trader.tier === filterTier;
      return matchesSearch && matchesTier;
    })
    .sort((a, b) => {
      switch(sortBy) {
        case 'profit': return b.totalReturn - a.totalReturn;
        case 'winRate': return b.winRate - a.winRate;
        case 'copiers': return b.copiers - a.copiers;
        case 'risk': return a.riskScore - b.riskScore;
        default: return 0;
      }
    });

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
            Elite Copy Network
          </h1>
          <p className="text-gray-400 mt-1">Mirror the masters and multiply your success</p>
        </div>
        <motion.div
          animate={{ 
            scale: [1, 1.05, 1],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 4, 
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30">
            <Globe className="h-5 w-5 text-purple-400" />
            <span className="text-sm font-medium text-purple-400">
              {status.active_traders || 0} Traders Online
            </span>
              </div>
        </motion.div>
      </motion.div>

      {/* Stats Overview */}
      <StatsOverview />

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Traders Grid - Left 3 Columns */}
        <div className="lg:col-span-3 space-y-6">
          {/* Filters */}
          <Card className="bg-gradient-to-br from-gray-900/50 to-slate-900/50 border-gray-700">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
                  <Input 
                    placeholder="Search traders or strategies..." 
                    className="pl-10 bg-black/30 border-gray-700"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Select value={filterTier} onValueChange={setFilterTier}>
                  <SelectTrigger className="w-40 bg-black/30 border-gray-700">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Filter by tier" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Tiers</SelectItem>
                    <SelectItem value="Diamond">Diamond</SelectItem>
                    <SelectItem value="Gold">Gold</SelectItem>
                    <SelectItem value="Silver">Silver</SelectItem>
                    <SelectItem value="Bronze">Bronze</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-40 bg-black/30 border-gray-700">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="profit">Highest Profit</SelectItem>
                    <SelectItem value="winRate">Win Rate</SelectItem>
                    <SelectItem value="copiers">Most Copied</SelectItem>
                    <SelectItem value="risk">Lowest Risk</SelectItem>
                  </SelectContent>
                </Select>
        </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4 bg-gray-800/50">
              <TabsTrigger value="all" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
                All Traders
              </TabsTrigger>
              <TabsTrigger value="trending" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
                <Flame className="h-4 w-4 mr-1" />
                Trending
              </TabsTrigger>
              <TabsTrigger value="new" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
                <Sparkles className="h-4 w-4 mr-1" />
                New
              </TabsTrigger>
              <TabsTrigger value="following" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600">
                <Eye className="h-4 w-4 mr-1" />
                Following
              </TabsTrigger>
            </TabsList>

            <AnimatePresence mode="wait">
              <TabsContent value={activeTab} className="mt-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-6"
                >
                  {filteredTraders.map((trader, idx) => (
                    <EnhancedTraderCard key={trader.id} trader={trader} rank={idx + 1} />
                  ))}
                </motion.div>
              </TabsContent>
            </AnimatePresence>
          </Tabs>
                  </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Leaderboard */}
          <Leaderboard />

          {/* Copy Trading Guide */}
          <Card className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border-purple-500/30">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-yellow-400" />
                Quick Start Guide
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 font-bold">1</span>
                </div>
                    <div>
                  <p className="text-sm font-medium text-white">Choose a Trader</p>
                  <p className="text-xs text-gray-400">Filter by performance and risk</p>
                    </div>
                    </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 font-bold">2</span>
                    </div>
                    <div>
                  <p className="text-sm font-medium text-white">Set Copy Amount</p>
                  <p className="text-xs text-gray-400">Start from as low as $100</p>
                    </div>
                  </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 font-bold">3</span>
                    </div>
                <div>
                  <p className="text-sm font-medium text-white">Auto-Copy Trades</p>
                  <p className="text-xs text-gray-400">Sit back and watch profits grow</p>
                    </div>
                  </div>
              <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0 mt-4">
                <Award className="h-4 w-4 mr-2" />
                Start Copying Now
              </Button>
            </CardContent>
          </Card>

          {/* Risk Warning */}
          <Card className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 border-yellow-500/30">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-400">Risk Disclaimer</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Past performance does not guarantee future results. Copy trading involves substantial risk.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 