"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import PerformanceMetrics from '@/components/performance/PerformanceMetrics';
import EquityCurveChart from '@/components/performance/EquityCurveChart';

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

interface SymbolPerformance {
  [symbol: string]: {
    total_profit: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    average_profit: number;
    largest_win: number;
    largest_loss: number;
    profit_factor: number;
  };
}

interface StrategyPerformance {
  [strategy: string]: {
    total_profit: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    average_profit: number;
    largest_win: number;
    largest_loss: number;
    profit_factor: number;
    average_duration: number;
  };
}

const PerformancePage: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceData | null>(null);
  const [symbolPerformance, setSymbolPerformance] = useState<SymbolPerformance>({});
  const [strategyPerformance, setStrategyPerformance] = useState<StrategyPerformance>({});
  const [monthlyPerformance, setMonthlyPerformance] = useState<any>({});
  const [equityData, setEquityData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('1M');

  useEffect(() => {
    fetchPerformanceData();
  }, [selectedPeriod]);

  const fetchPerformanceData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Calculate date range based on selected period
      const endDate = new Date();
      const startDate = new Date();
      
      switch (selectedPeriod) {
        case '1W':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case '1M':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case '3M':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case '6M':
          startDate.setMonth(endDate.getMonth() - 6);
          break;
        case '1Y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        default:
          startDate.setMonth(endDate.getMonth() - 1);
      }

      // Fetch all performance data in parallel
      const [
        metricsResponse,
        symbolResponse,
        strategyResponse,
        monthlyResponse,
        equityResponse
      ] = await Promise.all([
        fetch(`/api/v1/performance/metrics?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`),
        fetch(`/api/v1/performance/symbols?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`),
        fetch(`/api/v1/performance/strategies?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`),
        fetch(`/api/v1/performance/monthly?year=${endDate.getFullYear()}`),
        fetch(`/api/v1/performance/equity-curve?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`)
      ]);

      const [metricsData, symbolData, strategyData, monthlyData, equityDataResponse] = await Promise.all([
        metricsResponse.json(),
        symbolResponse.json(),
        strategyResponse.json(),
        monthlyResponse.json(),
        equityResponse.json()
      ]);

      setMetrics(metricsData);
      setSymbolPerformance(symbolData);
      setStrategyPerformance(strategyData);
      setMonthlyPerformance(monthlyData);
      setEquityData(equityDataResponse);

    } catch (err) {
      setError('Failed to fetch performance data');
      console.error('Performance data fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

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

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading performance data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Performance Analytics</h1>
        
        {/* Period Selector */}
        <div className="flex gap-2">
          {['1W', '1M', '3M', '6M', '1Y', 'ALL'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                selectedPeriod === period
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics Overview */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(metrics.total_return)}
              </div>
              <div className="text-sm text-gray-600">Total Return</div>
              <div className="text-xs text-gray-500">
                {formatPercentage(metrics.total_return_pct)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {metrics.sharpe_ratio.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Sharpe Ratio</div>
              <Badge className={getRiskLevel(metrics.sharpe_ratio).color}>
                {getRiskLevel(metrics.sharpe_ratio).label}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-red-600">
                {formatPercentage(metrics.max_drawdown_pct)}
              </div>
              <div className="text-sm text-gray-600">Max Drawdown</div>
              <div className="text-xs text-gray-500">
                {formatCurrency(metrics.max_drawdown)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {formatPercentage(metrics.win_rate)}
              </div>
              <div className="text-sm text-gray-600">Win Rate</div>
              <div className="text-xs text-gray-500">
                {metrics.winning_trades}/{metrics.total_trades}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {metrics.profit_factor.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Profit Factor</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">
                {formatCurrency(metrics.expectancy)}
              </div>
              <div className="text-sm text-gray-600">Expectancy</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Equity Curve */}
      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
        </CardHeader>
        <CardContent>
          <EquityCurveChart data={equityData} />
        </CardContent>
      </Card>

      {/* Performance Metrics Component */}
      {metrics && (
        <PerformanceMetrics data={metrics} />
      )}

      {/* Symbol Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Performance by Symbol</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Symbol</th>
                  <th className="text-right p-2">Profit</th>
                  <th className="text-right p-2">Trades</th>
                  <th className="text-right p-2">Win Rate</th>
                  <th className="text-right p-2">Avg Profit</th>
                  <th className="text-right p-2">Profit Factor</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(symbolPerformance).map(([symbol, data]) => (
                  <tr key={symbol} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{symbol}</td>
                    <td className={`p-2 text-right font-medium ${
                      data.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(data.total_profit)}
                    </td>
                    <td className="p-2 text-right">{data.total_trades}</td>
                    <td className="p-2 text-right">{formatPercentage(data.win_rate)}</td>
                    <td className="p-2 text-right">{formatCurrency(data.average_profit)}</td>
                    <td className="p-2 text-right">{data.profit_factor.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Strategy Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Performance by Strategy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Strategy</th>
                  <th className="text-right p-2">Profit</th>
                  <th className="text-right p-2">Trades</th>
                  <th className="text-right p-2">Win Rate</th>
                  <th className="text-right p-2">Avg Duration</th>
                  <th className="text-right p-2">Profit Factor</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(strategyPerformance).map(([strategy, data]) => (
                  <tr key={strategy} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{strategy}</td>
                    <td className={`p-2 text-right font-medium ${
                      data.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(data.total_profit)}
                    </td>
                    <td className="p-2 text-right">{data.total_trades}</td>
                    <td className="p-2 text-right">{formatPercentage(data.win_rate)}</td>
                    <td className="p-2 text-right">{data.average_duration.toFixed(1)}m</td>
                    <td className="p-2 text-right">{data.profit_factor.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Monthly Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Monthly Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Object.entries(monthlyPerformance).map(([month, data]: [string, any]) => (
              <div key={month} className="text-center p-3 border rounded">
                <div className="text-sm font-medium text-gray-600">{month}</div>
                <div className={`text-lg font-bold ${
                  data.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(data.total_profit)}
                </div>
                <div className="text-xs text-gray-500">
                  {data.total_trades} trades
                </div>
                <div className="text-xs text-gray-500">
                  {formatPercentage(data.win_rate)} win rate
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PerformancePage; 