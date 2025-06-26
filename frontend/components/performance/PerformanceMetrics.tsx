"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart, 
  BadgeDollarSign, 
  TrendingUp, 
  TrendingDown, 
  Percent, 
  AlertTriangle,
  Target,
  Activity,
  Calculator,
  Award
} from 'lucide-react';

interface PerformanceData {
  total_return: number;
  total_return_pct: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  win_rate: number;
  profit_factor: number;
  average_win: number;
  average_loss: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  largest_win: number;
  largest_loss: number;
  consecutive_wins: number;
  consecutive_losses: number;
  calmar_ratio: number;
  sortino_ratio: number;
  recovery_factor: number;
  expectancy: number;
  kelly_criterion: number;
}

interface PerformanceMetricsProps {
  data: PerformanceData;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ data }) => {
  if (!data || data.total_trades === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <AlertTriangle className="mx-auto text-yellow-500 mb-2" size={32} />
          <h3 className="text-lg font-semibold mb-2">No Trading Data</h3>
          <p className="text-gray-600 text-sm">No trades have been executed yet.</p>
        </CardContent>
      </Card>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const getRiskLevel = (sharpe: number) => {
    if (sharpe > 2) return { label: 'Excellent', color: 'bg-green-500' };
    if (sharpe > 1) return { label: 'Good', color: 'bg-blue-500' };
    if (sharpe > 0) return { label: 'Fair', color: 'bg-yellow-500' };
    return { label: 'Poor', color: 'bg-red-500' };
  };

  const tradingMetrics = [
    {
      name: 'Total Trades',
      value: data.total_trades,
      icon: BarChart,
      color: 'text-blue-600',
      description: 'Total number of executed trades'
    },
    {
      name: 'Win Rate',
      value: formatPercentage(data.win_rate),
      icon: Target,
      color: 'text-purple-600',
      description: `${data.winning_trades} wins / ${data.losing_trades} losses`
    },
    {
      name: 'Profit Factor',
      value: data.profit_factor.toFixed(2),
      icon: TrendingUp,
      color: 'text-green-600',
      description: 'Gross profit / Gross loss ratio'
    },
    {
      name: 'Average Win',
      value: formatCurrency(data.average_win),
      icon: Award,
      color: 'text-emerald-600',
      description: 'Average profit per winning trade'
    },
    {
      name: 'Average Loss',
      value: formatCurrency(Math.abs(data.average_loss)),
      icon: TrendingDown,
      color: 'text-red-600',
      description: 'Average loss per losing trade'
    },
    {
      name: 'Expectancy',
      value: formatCurrency(data.expectancy),
      icon: Calculator,
      color: 'text-indigo-600',
      description: 'Expected return per trade'
    }
  ];

  const riskMetrics = [
    {
      name: 'Sharpe Ratio',
      value: data.sharpe_ratio.toFixed(2),
      badge: getRiskLevel(data.sharpe_ratio),
      description: 'Risk-adjusted return measure'
    },
    {
      name: 'Sortino Ratio',
      value: data.sortino_ratio.toFixed(2),
      description: 'Downside risk-adjusted return'
    },
    {
      name: 'Calmar Ratio',
      value: data.calmar_ratio.toFixed(2),
      description: 'Annual return / Max drawdown'
    },
    {
      name: 'Recovery Factor',
      value: data.recovery_factor.toFixed(2),
      description: 'Net profit / Max drawdown'
    },
    {
      name: 'Kelly Criterion',
      value: formatPercentage(data.kelly_criterion * 100),
      description: 'Optimal position sizing percentage'
    }
  ];

  const streakMetrics = [
    {
      name: 'Largest Win',
      value: formatCurrency(data.largest_win),
      color: 'text-green-600'
    },
    {
      name: 'Largest Loss',
      value: formatCurrency(Math.abs(data.largest_loss)),
      color: 'text-red-600'
    },
    {
      name: 'Max Consecutive Wins',
      value: data.consecutive_wins,
      color: 'text-emerald-600'
    },
    {
      name: 'Max Consecutive Losses',
      value: data.consecutive_losses,
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Trading Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Trading Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {tradingMetrics.map((metric) => (
              <div key={metric.name} className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <metric.icon className={`h-5 w-5 ${metric.color}`} />
                  <span className="font-medium text-sm">{metric.name}</span>
                </div>
                <div className="text-2xl font-bold mb-1">{metric.value}</div>
                <div className="text-xs text-gray-500">{metric.description}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Risk Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {riskMetrics.map((metric) => (
              <div key={metric.name} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{metric.name}</span>
                  {metric.badge && (
                    <Badge className={metric.badge.color}>
                      {metric.badge.label}
                    </Badge>
                  )}
                </div>
                <div className="text-xl font-bold mb-1">{metric.value}</div>
                <div className="text-xs text-gray-500">{metric.description}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Extremes and Streaks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Extremes & Streaks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {streakMetrics.map((metric) => (
              <div key={metric.name} className="p-4 border rounded-lg text-center">
                <div className="text-sm font-medium text-gray-600 mb-1">
                  {metric.name}
                </div>
                <div className={`text-xl font-bold ${metric.color}`}>
                  {metric.value}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">Trading Statistics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Return:</span>
                  <span className={`font-medium ${data.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(data.total_return)} ({formatPercentage(data.total_return_pct)})
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Win/Loss Ratio:</span>
                  <span className="font-medium">
                    {data.average_loss !== 0 ? (data.average_win / Math.abs(data.average_loss)).toFixed(2) : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Trades per Day:</span>
                  <span className="font-medium">
                    {(data.total_trades / 30).toFixed(1)} (avg)
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Risk Assessment</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Max Drawdown:</span>
                  <span className="font-medium text-red-600">
                    {formatCurrency(data.max_drawdown)} ({formatPercentage(data.max_drawdown_pct)})
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Score:</span>
                  <Badge className={getRiskLevel(data.sharpe_ratio).color}>
                    {getRiskLevel(data.sharpe_ratio).label}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Recommended Position Size:</span>
                  <span className="font-medium">
                    {formatPercentage(Math.min(data.kelly_criterion * 100, 25))} (Kelly)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformanceMetrics; 