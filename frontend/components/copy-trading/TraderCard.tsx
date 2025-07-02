"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  TrendingUp, 
  TrendingDown, 
  Star, 
  Users, 
  Award,
  Shield,
  Eye,
  Copy,
  DollarSign,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

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

interface TraderCardProps {
  trader: TraderProfile;
  onCopy: (trader: TraderProfile) => void;
  onViewProfile: (trader: TraderProfile) => void;
}

export default function TraderCard({ trader, onCopy, onViewProfile }: TraderCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'diamond': return 'text-purple-400 bg-purple-500/20';
      case 'platinum': return 'text-gray-300 bg-gray-500/20';
      case 'gold': return 'text-yellow-400 bg-yellow-500/20';
      case 'silver': return 'text-gray-400 bg-gray-600/20';
      default: return 'text-orange-400 bg-orange-500/20';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'conservative': return 'text-green-400 bg-green-500/20';
      case 'moderate': return 'text-blue-400 bg-blue-500/20';
      case 'aggressive': return 'text-orange-400 bg-orange-500/20';
      case 'extreme': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toLocaleString('en-US', { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    });
  };

  const getReturnColor = (value: number) => {
    return value >= 0 ? 'text-green-400' : 'text-red-400';
  };

  return (
    <motion.div
      className="quantum-panel p-6 cursor-pointer border border-gray-700/50 hover:border-quantum-primary/50 transition-all duration-300"
      whileHover={{ scale: 1.02, y: -5 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            {trader.avatar_url ? (
              <img 
                src={trader.avatar_url} 
                alt={trader.display_name}
                className="w-12 h-12 rounded-full border-2 border-quantum-primary/30"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-quantum-primary to-quantum-secondary flex items-center justify-center">
                <User className="w-6 h-6 text-black" />
              </div>
            )}
            {trader.is_premium && (
              <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center">
                <Award className="w-3 h-3 text-black" />
              </div>
            )}
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-white">{trader.display_name}</h3>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 text-xs rounded-full ${getTierColor(trader.tier)}`}>
                {trader.tier}
              </span>
              <span className={`px-2 py-1 text-xs rounded-full ${getRiskColor(trader.risk_level)}`}>
                {trader.risk_level}
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="flex items-center gap-1 text-yellow-400">
            <Star className="w-4 h-4 fill-current" />
            <span className="font-semibold">{trader.rating.toFixed(1)}</span>
          </div>
          <div className="flex items-center gap-1 text-gray-400 text-sm">
            <Users className="w-3 h-3" />
            <span>{trader.followers_count}</span>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <p className="text-sm text-gray-400">Total Return</p>
          <p className={`text-xl font-bold ${getReturnColor(trader.total_return)}`}>
            {trader.total_return >= 0 ? '+' : ''}{formatNumber(trader.total_return)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-400">Monthly Return</p>
          <p className={`text-xl font-bold ${getReturnColor(trader.monthly_return)}`}>
            {trader.monthly_return >= 0 ? '+' : ''}{formatNumber(trader.monthly_return)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-400">Win Rate</p>
          <p className="text-lg font-semibold text-blue-400">
            {formatNumber(trader.win_rate)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-400">Profit Factor</p>
          <p className="text-lg font-semibold text-purple-400">
            {formatNumber(trader.profit_factor)}
          </p>
        </div>
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Max Drawdown</span>
          <span className="text-red-400">{formatNumber(trader.max_drawdown)}%</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Sharpe Ratio</span>
          <span className="text-green-400">{formatNumber(trader.sharpe_ratio)}</span>
        </div>
      </div>

      {/* Subscription Info */}
      {trader.is_premium && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-yellow-400 text-sm font-medium">Premium Trader</span>
            <span className="text-yellow-400 font-bold">
              ${formatNumber(trader.subscription_fee, 0)}/month
            </span>
          </div>
        </div>
      )}

      {/* Copy Requirements */}
      <div className="bg-gray-800/30 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Minimum Copy</span>
          <span className="text-white font-medium">
            ${formatNumber(trader.min_copy_amount, 0)}
          </span>
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-green-400 text-sm">Active</span>
        </div>
        {trader.last_trade_time && (
          <div className="flex items-center gap-1 text-gray-400 text-xs">
            <Clock className="w-3 h-3" />
            <span>Last trade: {new Date(trader.last_trade_time).toLocaleDateString()}</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <motion.div 
        className="flex gap-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: isHovered ? 1 : 0, y: isHovered ? 0 : 10 }}
        transition={{ duration: 0.2 }}
      >
        <button
          onClick={() => onViewProfile(trader)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
        >
          <Eye className="w-4 h-4" />
          <span>View Profile</span>
        </button>
        <button
          onClick={() => onCopy(trader)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-quantum-primary hover:bg-quantum-primary/80 text-black font-semibold rounded-lg transition-colors"
        >
          <Copy className="w-4 h-4" />
          <span>Copy</span>
        </button>
      </motion.div>

      {/* Performance Indicator */}
      <motion.div
        className="absolute top-2 right-2"
        initial={{ scale: 0 }}
        animate={{ scale: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      >
        {trader.monthly_return > 10 ? (
          <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-green-400" />
          </div>
        ) : trader.monthly_return < -5 ? (
          <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
            <TrendingDown className="w-4 h-4 text-red-400" />
          </div>
        ) : (
          <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
            <BarChart3 className="w-4 h-4 text-blue-400" />
          </div>
        )}
      </motion.div>
    </motion.div>
  );
} 