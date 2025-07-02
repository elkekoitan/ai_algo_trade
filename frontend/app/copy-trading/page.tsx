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
  Brain
} from 'lucide-react';
import QuantumLayout from '@/components/layout/QuantumLayout';
import TraderCard from '@/components/copy-trading/TraderCard';
import { api } from '@/utils/api-discovery';

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

export default function CopyTradingPage() {
  const [traders, setTraders] = useState<TraderProfile[]>([]);
  const [filteredTraders, setFilteredTraders] = useState<TraderProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('all');
  const [minReturn, setMinReturn] = useState<number>(0);
  const [maxDrawdown, setMaxDrawdown] = useState<number>(100);
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [selectedTrader, setSelectedTrader] = useState<TraderProfile | null>(null);
  const [copySettings, setCopySettings] = useState<CopySettings>({
    copy_amount: 1000,
    copy_ratio: 1.0,
    max_daily_loss: 100,
    max_open_positions: 5,
    stop_loss_buffer: 0,
    take_profit_buffer: 0
  });

  useEffect(() => {
    fetchTraders();
  }, []);

  useEffect(() => {
    filterTraders();
  }, [traders, searchTerm, selectedRiskLevel, minReturn, maxDrawdown]);

  const fetchTraders = async () => {
    try {
      setLoading(true);
      // Try to fetch from real API
      const data = await api.get<TraderProfile[]>('copyTradingTraders');
      setTraders(data || generateMockTraders());
    } catch (error) {
      console.error('Failed to fetch traders:', error);
      // Use mock data as fallback
      setTraders(generateMockTraders());
    } finally {
      setLoading(false);
    }
  };

  const generateMockTraders = (): TraderProfile[] => {
    return [
      {
        trader_id: 'trader_001',
        display_name: 'Alpha Wolf Trading',
        tier: 'Diamond',
        total_return: 145.8,
        monthly_return: 12.3,
        win_rate: 78.5,
        profit_factor: 2.4,
        max_drawdown: 8.2,
        sharpe_ratio: 1.8,
        followers_count: 1250,
        rating: 4.9,
        risk_level: 'Moderate',
        is_premium: true,
        subscription_fee: 99,
        min_copy_amount: 500,
        last_trade_time: '2024-01-01T10:30:00Z'
      },
      {
        trader_id: 'trader_002',
        display_name: 'Forex Ninja',
        tier: 'Platinum',
        total_return: 89.2,
        monthly_return: 8.7,
        win_rate: 65.4,
        profit_factor: 1.9,
        max_drawdown: 12.5,
        sharpe_ratio: 1.4,
        followers_count: 890,
        rating: 4.7,
        risk_level: 'Conservative',
        is_premium: false,
        subscription_fee: 0,
        min_copy_amount: 250,
        last_trade_time: '2024-01-01T09:15:00Z'
      },
      {
        trader_id: 'trader_003',
        display_name: 'Quantum Trader',
        tier: 'Gold',
        total_return: 203.5,
        monthly_return: 18.9,
        win_rate: 72.1,
        profit_factor: 2.8,
        max_drawdown: 15.8,
        sharpe_ratio: 2.1,
        followers_count: 567,
        rating: 4.6,
        risk_level: 'Aggressive',
        is_premium: true,
        subscription_fee: 149,
        min_copy_amount: 1000,
        last_trade_time: '2024-01-01T11:45:00Z'
      }
    ];
  };

  const filterTraders = () => {
    let filtered = traders;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(trader =>
        trader.display_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Risk level filter
    if (selectedRiskLevel !== 'all') {
      filtered = filtered.filter(trader =>
        trader.risk_level.toLowerCase() === selectedRiskLevel.toLowerCase()
      );
    }

    // Return filter
    filtered = filtered.filter(trader => trader.monthly_return >= minReturn);

    // Drawdown filter
    filtered = filtered.filter(trader => trader.max_drawdown <= maxDrawdown);

    setFilteredTraders(filtered);
  };

  const handleCopyTrader = (trader: TraderProfile) => {
    setSelectedTrader(trader);
    setShowCopyModal(true);
  };

  const handleViewProfile = (trader: TraderProfile) => {
    // Navigate to trader profile page
    console.log('View profile:', trader.trader_id);
  };

  const startCopying = async () => {
    if (!selectedTrader) return;

    try {
      const result = await api.post('copyTradingStart', {
        follower_id: 'user_123', // Would come from auth
        trader_id: selectedTrader.trader_id,
        settings: copySettings
      });

      if (result.success) {
        setShowCopyModal(false);
        setSelectedTrader(null);
        // Show success notification
        alert(`Started copying ${selectedTrader.display_name}!`);
      } else {
        alert('Failed to start copying. Please try again.');
      }
    } catch (error) {
      console.error('Failed to start copying:', error);
      alert('Failed to start copying. Please try again.');
    }
  };

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

  if (loading) {
    return (
      <QuantumLayout>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Copy className="w-6 h-6 text-quantum-primary animate-pulse" />
            <span className="text-gray-400">Loading traders...</span>
          </div>
        </div>
      </QuantumLayout>
    );
  }

  return (
    <QuantumLayout>
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900">
        <div className="container mx-auto px-4 py-8">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-8"
          >
            {/* Header */}
            <motion.div variants={itemVariants} className="text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <Copy className="w-8 h-8 text-quantum-primary" />
                <h1 className="text-4xl font-bold bg-gradient-to-r from-quantum-primary to-quantum-secondary bg-clip-text text-transparent">
                  Copy Trading
                </h1>
                <Users className="w-8 h-8 text-quantum-secondary" />
              </div>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                Copy successful traders automatically with advanced risk management and real-time execution
              </p>
            </motion.div>

            {/* Stats Overview */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { label: 'Active Traders', value: '1,247', icon: Users, color: 'text-blue-400' },
                { label: 'Total Copies', value: '8,932', icon: Copy, color: 'text-green-400' },
                { label: 'Success Rate', value: '84%', icon: Target, color: 'text-purple-400' },
                { label: 'Avg. Latency', value: '12ms', icon: Zap, color: 'text-yellow-400' }
              ].map((stat, index) => (
                <div key={index} className="quantum-panel p-6 text-center">
                  <stat.icon className={`w-8 h-8 ${stat.color} mx-auto mb-2`} />
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-sm text-gray-400">{stat.label}</p>
                </div>
              ))}
            </motion.div>

            {/* Filters */}
            <motion.div variants={itemVariants} className="quantum-panel p-6">
              <div className="flex items-center gap-4 mb-4">
                <Filter className="w-5 h-5 text-quantum-primary" />
                <h2 className="text-lg font-semibold text-white">Find Traders</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                {/* Search */}
                <div className="md:col-span-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search traders..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-quantum-primary focus:outline-none"
                    />
                  </div>
                </div>

                {/* Risk Level */}
                <div>
                  <select
                    value={selectedRiskLevel}
                    onChange={(e) => setSelectedRiskLevel(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none"
                  >
                    <option value="all">All Risk Levels</option>
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>

                {/* Min Return */}
                <div>
                  <input
                    type="number"
                    placeholder="Min Return %"
                    value={minReturn}
                    onChange={(e) => setMinReturn(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-quantum-primary focus:outline-none"
                  />
                </div>

                {/* Max Drawdown */}
                <div>
                  <input
                    type="number"
                    placeholder="Max Drawdown %"
                    value={maxDrawdown}
                    onChange={(e) => setMaxDrawdown(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-quantum-primary focus:outline-none"
                  />
                </div>

                {/* Reset */}
                <div>
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setSelectedRiskLevel('all');
                      setMinReturn(0);
                      setMaxDrawdown(100);
                    }}
                    className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Traders Grid */}
            <motion.div variants={itemVariants}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  Available Traders ({filteredTraders.length})
                </h2>
                <div className="flex items-center gap-2">
                  <select className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none">
                    <option value="performance">Sort by Performance</option>
                    <option value="followers">Sort by Followers</option>
                    <option value="rating">Sort by Rating</option>
                    <option value="return">Sort by Return</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence mode="popLayout">
                  {filteredTraders.map((trader) => (
                    <TraderCard
                      key={trader.trader_id}
                      trader={trader}
                      onCopy={handleCopyTrader}
                      onViewProfile={handleViewProfile}
                    />
                  ))}
                </AnimatePresence>
              </div>

              {filteredTraders.length === 0 && (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg">No traders found matching your criteria</p>
                  <p className="text-gray-500">Try adjusting your filters</p>
                </div>
              )}
            </motion.div>
          </motion.div>
        </div>

        {/* Copy Settings Modal */}
        <AnimatePresence>
          {showCopyModal && selectedTrader && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
              onClick={() => setShowCopyModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="quantum-panel max-w-2xl w-full p-8"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Copy {selectedTrader.display_name}
                    </h2>
                    <p className="text-gray-400">Configure your copy trading settings</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Copy Amount ($)
                      </label>
                      <input
                        type="number"
                        value={copySettings.copy_amount}
                        onChange={(e) => setCopySettings({...copySettings, copy_amount: Number(e.target.value)})}
                        min={selectedTrader.min_copy_amount}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Minimum: ${selectedTrader.min_copy_amount}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Copy Ratio
                      </label>
                      <input
                        type="number"
                        value={copySettings.copy_ratio}
                        onChange={(e) => setCopySettings({...copySettings, copy_ratio: Number(e.target.value)})}
                        min="0.1"
                        max="10"
                        step="0.1"
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        1.0 = Copy exact size, 0.5 = Half size
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Max Daily Loss ($)
                      </label>
                      <input
                        type="number"
                        value={copySettings.max_daily_loss}
                        onChange={(e) => setCopySettings({...copySettings, max_daily_loss: Number(e.target.value)})}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Max Open Positions
                      </label>
                      <input
                        type="number"
                        value={copySettings.max_open_positions}
                        onChange={(e) => setCopySettings({...copySettings, max_open_positions: Number(e.target.value)})}
                        min="1"
                        max="20"
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-quantum-primary focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-6 border-t border-gray-800">
                    <div className="text-sm text-gray-400">
                      {selectedTrader.is_premium && (
                        <p>Monthly fee: ${selectedTrader.subscription_fee}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <button
                        onClick={() => setShowCopyModal(false)}
                        className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={startCopying}
                        className="px-6 py-2 bg-quantum-primary hover:bg-quantum-primary/80 text-black font-semibold rounded-lg transition-colors"
                      >
                        Start Copying
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </QuantumLayout>
  );
} 