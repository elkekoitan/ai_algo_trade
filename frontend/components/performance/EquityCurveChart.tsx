"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  DollarSign,
  Calendar,
  Filter,
  Download,
  Maximize2,
  RefreshCw,
  Settings
} from 'lucide-react';

interface EquityCurvePoint {
  timestamp: string;
  balance: number;
  equity: number;
  drawdown: number;
  drawdown_pct: number;
  trade_count: number;
  cumulative_return: number;
}

interface EquityCurveChartProps {
  data: EquityCurvePoint[];
  height?: number;
  showControls?: boolean;
  autoRefresh?: boolean;
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({ 
  data = [], 
  height = 400, 
  showControls = true,
  autoRefresh = false 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<any>(null);
  const [chartType, setChartType] = useState<'equity' | 'drawdown' | 'returns'>('equity');
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'ALL'>('1M');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Chart.js dynamic import and initialization
  useEffect(() => {
    const initChart = async () => {
      if (!canvasRef.current || !data.length) return;

      try {
        // Dynamic import of Chart.js
        const { default: Chart } = await import('chart.js/auto');
        
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        // Destroy existing chart
        if (chartRef.current) {
          chartRef.current.destroy();
        }

        // Prepare data based on chart type
        const chartData = prepareChartData();
        
        // Create new chart
        chartRef.current = new Chart(ctx, {
          type: 'line',
          data: chartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
              intersect: false,
              mode: 'index'
            },
            plugins: {
              legend: {
                display: true,
                position: 'top',
                labels: {
                  usePointStyle: true,
                  padding: 20,
                  font: {
                    size: 12
                  }
                }
              },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: 'white',
                bodyColor: 'white',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 12,
                displayColors: true,
                callbacks: {
                  title: (context: any) => {
                    const date = new Date(context[0].parsed.x);
                    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                  },
                  label: (context: any) => {
                    const value = context.parsed.y;
                    if (chartType === 'equity') {
                      return `${context.dataset.label}: $${value.toFixed(2)}`;
                    } else if (chartType === 'drawdown') {
                      return `${context.dataset.label}: ${value.toFixed(2)}%`;
                    } else {
                      return `${context.dataset.label}: ${value.toFixed(2)}%`;
                    }
                  }
                }
              }
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  displayFormats: {
                    hour: 'HH:mm',
                    day: 'MMM DD',
                    week: 'MMM DD',
                    month: 'MMM YYYY'
                  }
                },
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                  color: '#6B7280',
                  font: {
                    size: 11
                  }
                }
              },
              y: {
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                  color: '#6B7280',
                  font: {
                    size: 11
                  },
                  callback: function(value: any) {
                    if (chartType === 'equity') {
                      return '$' + value.toFixed(0);
                    } else {
                      return value.toFixed(1) + '%';
                    }
                  }
                }
              }
            },
            elements: {
              point: {
                radius: 0,
                hoverRadius: 6,
                hitRadius: 10
              },
              line: {
                borderWidth: 2,
                tension: 0.1
              }
            }
          }
        });

      } catch (error) {
        console.error('Error initializing chart:', error);
      }
    };

    initChart();

    // Cleanup
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data, chartType, timeRange]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      setLastUpdate(new Date());
      // Trigger data refresh here if needed
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const prepareChartData = () => {
    if (!data.length) return { labels: [], datasets: [] };

    // Filter data based on time range
    const filteredData = filterDataByTimeRange(data);
    
    const labels = filteredData.map(point => point.timestamp);

    if (chartType === 'equity') {
      return {
        labels,
        datasets: [
          {
            label: 'Balance',
            data: filteredData.map(point => ({
              x: point.timestamp,
              y: point.balance
            })),
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: false,
            tension: 0.1
          },
          {
            label: 'Equity',
            data: filteredData.map(point => ({
              x: point.timestamp,
              y: point.equity
            })),
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: false,
            tension: 0.1
          }
        ]
      };
    } else if (chartType === 'drawdown') {
      return {
        labels,
        datasets: [
          {
            label: 'Drawdown %',
            data: filteredData.map(point => ({
              x: point.timestamp,
              y: -point.drawdown_pct // Negative for visual representation
            })),
            borderColor: '#EF4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            fill: true,
            tension: 0.1
          }
        ]
      };
    } else { // returns
      return {
        labels,
        datasets: [
          {
            label: 'Cumulative Return %',
            data: filteredData.map(point => ({
              x: point.timestamp,
              y: point.cumulative_return
            })),
            borderColor: '#8B5CF6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            fill: false,
            tension: 0.1
          }
        ]
      };
    }
  };

  const filterDataByTimeRange = (data: EquityCurvePoint[]) => {
    if (timeRange === 'ALL') return data;

    const now = new Date();
    const cutoffDate = new Date();

    switch (timeRange) {
      case '1D':
        cutoffDate.setDate(now.getDate() - 1);
        break;
      case '1W':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case '1M':
        cutoffDate.setMonth(now.getMonth() - 1);
        break;
      case '3M':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      case '6M':
        cutoffDate.setMonth(now.getMonth() - 6);
        break;
      case '1Y':
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
    }

    return data.filter(point => new Date(point.timestamp) >= cutoffDate);
  };

  const getChartStats = () => {
    if (!data.length) return null;

    const filteredData = filterDataByTimeRange(data);
    const latest = filteredData[filteredData.length - 1];
    const first = filteredData[0];

    if (!latest || !first) return null;

    const totalReturn = latest.equity - first.equity;
    const totalReturnPct = ((latest.equity - first.equity) / first.equity) * 100;
    const maxDrawdown = Math.max(...filteredData.map(p => p.drawdown_pct));
    const totalTrades = latest.trade_count;

    return {
      totalReturn,
      totalReturnPct,
      maxDrawdown,
      totalTrades,
      currentEquity: latest.equity,
      currentBalance: latest.balance
    };
  };

  const handleExport = () => {
    if (!chartRef.current) return;

    const link = document.createElement('a');
    link.download = `equity-curve-${chartType}-${timeRange}-${Date.now()}.png`;
    link.href = chartRef.current.toBase64Image();
    link.click();
  };

  const refreshData = async () => {
    setIsLoading(true);
    // Simulate data refresh
    setTimeout(() => {
      setIsLoading(false);
      setLastUpdate(new Date());
    }, 1000);
  };

  const stats = getChartStats();

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Equity Curve Analysis
          </CardTitle>
          
          {showControls && (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={refreshData}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button variant="outline" size="sm" onClick={handleExport}>
                <Download className="h-4 w-4 mr-1" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Controls */}
        {showControls && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {/* Chart Type Selector */}
              <div className="flex items-center gap-1">
                {(['equity', 'drawdown', 'returns'] as const).map((type) => (
                  <Button
                    key={type}
                    variant={chartType === type ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType(type)}
                  >
                    {type === 'equity' && <DollarSign className="h-3 w-3 mr-1" />}
                    {type === 'drawdown' && <TrendingDown className="h-3 w-3 mr-1" />}
                    {type === 'returns' && <TrendingUp className="h-3 w-3 mr-1" />}
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Time Range Selector */}
              <div className="flex items-center gap-1">
                {(['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'] as const).map((range) => (
                  <Button
                    key={range}
                    variant={timeRange === range ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTimeRange(range)}
                  >
                    {range}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mt-4">
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">
                ${stats.currentEquity.toFixed(2)}
              </div>
              <div className="text-xs text-gray-600">Current Equity</div>
            </div>
            
            <div className="text-center">
              <div className={`text-lg font-bold ${stats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${stats.totalReturn.toFixed(2)}
              </div>
              <div className="text-xs text-gray-600">Total Return</div>
            </div>
            
            <div className="text-center">
              <div className={`text-lg font-bold ${stats.totalReturnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {stats.totalReturnPct.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-600">Return %</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-red-600">
                {stats.maxDrawdown.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-600">Max Drawdown</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {stats.totalTrades}
              </div>
              <div className="text-xs text-gray-600">Total Trades</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">
                {timeRange}
              </div>
              <div className="text-xs text-gray-600">Period</div>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent>
        {data.length > 0 ? (
          <div style={{ height: `${height}px`, position: 'relative' }}>
            <canvas ref={canvasRef} />
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <Activity className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium mb-2">No Data Available</h3>
              <p className="text-sm">Equity curve data will appear here once trading begins.</p>
            </div>
          </div>
        )}

        {/* Last Update Info */}
        {showControls && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Calendar className="h-4 w-4" />
              Last updated: {lastUpdate.toLocaleString()}
            </div>
            
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {data.length} data points
              </Badge>
              {autoRefresh && (
                <Badge variant="outline" className="text-xs text-green-600">
                  Auto-refresh enabled
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EquityCurveChart; 