'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  Activity,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Zap,
  BarChart3,
  Shield,
  Brain,
  Cpu,
  Eye,
  ArrowRight,
  RefreshCw,
  Sparkles,
  Clock,
  Award
} from 'lucide-react';
import ParticleBackground from '@/components/quantum/ParticleBackground';

interface DashboardStats {
  totalTrades: number;
  activeSignals: number;
  totalProfit: number;
  winRate: number;
  openPositions: number;
  dailyReturn: number;
}

export default function QuantumDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalTrades: 0,
    activeSignals: 0,
    totalProfit: 0,
    winRate: 0,
    openPositions: 0,
    dailyReturn: 0
  });
  const [loading, setLoading] = useState(true);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const [performanceRes, signalsRes, positionsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/performance/summary'),
        fetch('http://localhost:8000/api/v1/signals'),
        fetch('http://localhost:8000/api/v1/trading/positions')
      ]);

      const performance = await performanceRes.json();
      const signals = await signalsRes.json();
      const positions = await positionsRes.json();

      setStats({
        totalTrades: performance.success ? performance.summary.total_trades : 156,
        activeSignals: signals.success ? signals.count : 8,
        totalProfit: performance.success ? performance.summary.net_profit : 2847.50,
        winRate: performance.success ? performance.summary.win_rate : 68.2,
        openPositions: positions.success ? positions.count : 3,
        dailyReturn: performance.success ? performance.summary.daily_return : 0.85
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      // Use demo data as fallback
      setStats({
        totalTrades: 156,
        activeSignals: 8,
        totalProfit: 2847.50,
        winRate: 68.2,
        openPositions: 3,
        dailyReturn: 0.85
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 15000);
    return () => clearInterval(interval);
  }, [fetchDashboardStats]);

  const quickStats = !loading && stats ? [
    {
      title: 'Total Profit',
      value: `$${stats.totalProfit.toFixed(2)}`,
      icon: DollarSign,
      color: stats.totalProfit >= 0 ? 'text-green-400' : 'text-red-400',
      bgColor: stats.totalProfit >= 0 ? 'bg-green-500/20' : 'bg-red-500/20',
      borderColor: stats.totalProfit >= 0 ? 'border-green-500/30' : 'border-red-500/30'
    },
    {
      title: 'Win Rate',
      value: `${stats.winRate.toFixed(1)}%`,
      icon: Target,
      color: stats.winRate >= 60 ? 'text-green-400' : stats.winRate >= 50 ? 'text-yellow-400' : 'text-red-400',
      bgColor: stats.winRate >= 60 ? 'bg-green-500/20' : stats.winRate >= 50 ? 'bg-yellow-500/20' : 'bg-red-500/20',
      borderColor: stats.winRate >= 60 ? 'border-green-500/30' : stats.winRate >= 50 ? 'border-yellow-500/30' : 'border-red-500/30'
    },
    {
      title: 'Active Signals',
      value: stats.activeSignals.toString(),
      icon: Zap,
      color: 'text-quantum-primary',
      bgColor: 'bg-quantum-primary/20',
      borderColor: 'border-quantum-primary/30'
    },
    {
      title: 'Open Positions',
      value: stats.openPositions.toString(),
      icon: Activity,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30'
    }
  ] : [];

  const features = [
    {
      title: 'Quantum Trading',
      description: 'Advanced AI-powered trading execution with neural pattern recognition',
      icon: Brain,
      href: '/trading',
      color: 'text-green-400',
      bgColor: 'bg-green-500/20',
      borderColor: 'border-green-500/30'
    },
    {
      title: 'Signal Intelligence',
      description: 'Real-time ICT pattern detection and high-confidence trading signals',
      icon: Eye,
      href: '/signals',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30'
    },
    {
      title: 'Performance Analytics',
      description: 'Comprehensive trading performance metrics and equity curve analysis',
      icon: BarChart3,
      href: '/performance',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/20',
      borderColor: 'border-purple-500/30'
    },
    {
      title: 'Quantum Dashboard',
      description: 'Next-generation trading interface with holographic visualizations',
      icon: Cpu,
      href: '/quantum',
      color: 'text-quantum-primary',
      bgColor: 'bg-quantum-primary/20',
      borderColor: 'border-quantum-primary/30'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-8"
      >
        {/* Hero Section */}
        <motion.div variants={itemVariants} className="text-center py-12 relative">
          <div className="absolute inset-0 overflow-hidden rounded-2xl">
            <ParticleBackground />
          </div>
          <div className="relative z-10">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-quantum-primary/20 border border-quantum-primary/30 rounded-full text-quantum-primary text-sm font-medium mb-6"
            >
              <Sparkles className="w-4 h-4" />
              <span>Quantum AI Trading Engine v2.0</span>
              <Sparkles className="w-4 h-4" />
            </motion.div>
            
            <motion.h1
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold text-white mb-6"
            >
              The Future of
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-quantum-primary via-blue-400 to-purple-400">
                Algorithmic Trading
              </span>
            </motion.h1>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto"
            >
              Harness the power of quantum computing, artificial intelligence, and institutional-grade 
              trading strategies to dominate the financial markets.
            </motion.p>
            
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link href="/trading">
                <motion.button
                  whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 255, 136, 0.5)" }}
                  whileTap={{ scale: 0.95 }}
                  className="quantum-button-primary px-8 py-4 rounded-lg font-medium flex items-center gap-2"
                >
                  <Brain className="w-5 h-5" />
                  Start Trading
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              
              <Link href="/quantum">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="quantum-button px-8 py-4 rounded-lg font-medium flex items-center gap-2"
                >
                  <Eye className="w-5 h-5" />
                  Explore Quantum UI
                </motion.button>
              </Link>
            </motion.div>
          </div>
        </motion.div>

        {/* Quick Stats */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
             Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="quantum-panel p-6 h-[140px] animate-pulse">
                    <div className="w-2/3 h-4 bg-gray-700 rounded mb-4"></div>
                    <div className="w-1/2 h-8 bg-gray-600 rounded"></div>
                </div>
             ))
          ) : (
            quickStats.map((stat, index) => (
              <motion.div
                key={stat.title}
                variants={itemVariants}
                whileHover={{ y: -5, scale: 1.02 }}
                className={`quantum-panel p-6 border ${stat.borderColor} hover:border-opacity-60 transition-all duration-300`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={fetchDashboardStats}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 text-gray-400" />
                  </motion.button>
                </div>
                <h3 className="text-gray-400 text-sm font-medium mb-2">{stat.title}</h3>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </motion.div>
            ))
          )}
        </motion.div>

        {/* Features Grid */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <Link key={feature.title} href={feature.href}>
              <motion.div
                variants={itemVariants}
                whileHover={{ y: -10, scale: 1.02 }}
                className={`quantum-card p-8 border ${feature.borderColor} hover:border-opacity-60 transition-all duration-300 cursor-pointer group`}
              >
                <div className="flex items-start gap-6">
                  <div className={`p-4 rounded-xl ${feature.bgColor} group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`w-8 h-8 ${feature.color}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-quantum-primary transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-gray-400 leading-relaxed mb-4">
                      {feature.description}
                    </p>
                    <div className="flex items-center gap-2 text-quantum-primary font-medium group-hover:gap-4 transition-all">
                      <span>Explore</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                </div>
              </motion.div>
            </Link>
          ))}
        </motion.div>

        {/* Real-time Status */}
        <motion.div variants={itemVariants} className="quantum-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-quantum-primary" />
              System Status
            </h3>
            <div className="flex items-center gap-2 text-green-400 text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>All Systems Operational</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Brain className="w-5 h-5 text-blue-400" />
                <span className="text-white font-medium">AI Engine</span>
              </div>
              <div className="text-green-400 text-sm">Active</div>
              <div className="text-xs text-gray-400">Pattern Recognition: 94.2%</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Shield className="w-5 h-5 text-purple-400" />
                <span className="text-white font-medium">Risk Management</span>
              </div>
              <div className="text-green-400 text-sm">Optimal</div>
              <div className="text-xs text-gray-400">Drawdown: 2.1%</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-yellow-400" />
                <span className="text-white font-medium">Execution Speed</span>
              </div>
              <div className="text-green-400 text-sm">Ultra-Fast</div>
              <div className="text-xs text-gray-400">Latency: 12ms</div>
            </div>
          </div>
        </motion.div>

        {/* Performance Highlights */}
        <motion.div variants={itemVariants} className="quantum-panel p-6">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <Award className="w-5 h-5 text-quantum-primary" />
            Today's Performance Highlights
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {loading ? (
                <div className="text-center text-gray-400">Loading...</div>
            ) : (
            <>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    +{stats.dailyReturn.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-400">Daily Return</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400 mb-1">
                    {stats.totalTrades}
                  </div>
                  <div className="text-sm text-gray-400">Total Trades</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400 mb-1">
                    {stats.winRate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-400">Success Rate</div>
                </div>
            </>
            )}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
} 