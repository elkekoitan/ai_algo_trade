"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Target, Shield, Activity } from 'lucide-react';

interface PerformanceMetricsProps {
  data: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    total_profit: number;
    total_loss: number;
    net_profit: number;
    profit_factor: number;
    max_drawdown: number;
    sharpe_ratio: number;
    daily_return: number;
    monthly_return: number;
    yearly_return: number;
  };
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ data }) => {
  const metrics = [
    {
      title: 'Net Profit',
      value: `$${data.net_profit.toFixed(2)}`,
      icon: DollarSign,
      color: data.net_profit >= 0 ? 'text-green-400' : 'text-red-400',
      bgColor: data.net_profit >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'
    },
    {
      title: 'Win Rate',
      value: `${data.win_rate.toFixed(1)}%`,
      icon: Target,
      color: data.win_rate >= 60 ? 'text-green-400' : data.win_rate >= 50 ? 'text-yellow-400' : 'text-red-400',
      bgColor: data.win_rate >= 60 ? 'bg-green-500/20' : data.win_rate >= 50 ? 'bg-yellow-500/20' : 'bg-red-500/20'
    },
    {
      title: 'Total Trades',
      value: data.total_trades.toString(),
      icon: Activity,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20'
    },
    {
      title: 'Profit Factor',
      value: data.profit_factor.toFixed(2),
      icon: TrendingUp,
      color: data.profit_factor >= 2 ? 'text-green-400' : data.profit_factor >= 1 ? 'text-yellow-400' : 'text-red-400',
      bgColor: data.profit_factor >= 2 ? 'bg-green-500/20' : data.profit_factor >= 1 ? 'bg-yellow-500/20' : 'bg-red-500/20'
    },
    {
      title: 'Max Drawdown',
      value: `$${Math.abs(data.max_drawdown).toFixed(2)}`,
      icon: Shield,
      color: 'text-red-400',
      bgColor: 'bg-red-500/20'
    },
    {
      title: 'Sharpe Ratio',
      value: data.sharpe_ratio.toFixed(2),
      icon: TrendingUp,
      color: data.sharpe_ratio >= 1.5 ? 'text-green-400' : data.sharpe_ratio >= 1 ? 'text-yellow-400' : 'text-red-400',
      bgColor: data.sharpe_ratio >= 1.5 ? 'bg-green-500/20' : data.sharpe_ratio >= 1 ? 'bg-yellow-500/20' : 'bg-red-500/20'
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
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.title}
          variants={itemVariants}
          className="quantum-panel p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg ${metric.bgColor}`}>
              <metric.icon className={`w-6 h-6 ${metric.color}`} />
            </div>
            <div className="text-right">
              <p className={`text-2xl font-bold ${metric.color}`}>
                {metric.value}
              </p>
            </div>
          </div>
          <h3 className="text-gray-400 text-sm font-medium">
            {metric.title}
          </h3>
        </motion.div>
      ))}
    </motion.div>
  );
};

export default PerformanceMetrics; 