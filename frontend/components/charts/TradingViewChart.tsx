"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  Target,
  Settings,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ICTLevel {
  id: string;
  type: 'order_block' | 'fair_value_gap' | 'breaker_block' | 'support' | 'resistance';
  price: number;
  startTime: string;
  endTime?: string;
  strength: number;
  direction: 'bullish' | 'bearish';
  active: boolean;
}

interface TradingViewChartProps {
  symbol: string;
  timeframe: string;
  height?: number;
  showControls?: boolean;
  autoRefresh?: boolean;
  onSignalGenerated?: (signal: any) => void;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  timeframe,
  height = 500,
  showControls = true,
  autoRefresh = true,
  onSignalGenerated
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<any>(null);
  
  // State management
  const [candleData, setCandleData] = useState<CandleData[]>([]);
  const [ictLevels, setIctLevels] = useState<ICTLevel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(autoRefresh);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  // Chart settings
  const [chartType, setChartType] = useState<'line' | 'area'>('line');
  const [showVolume, setShowVolume] = useState(true);
  const [showICTLevels, setShowICTLevels] = useState(true);
  const [showSignals, setShowSignals] = useState(true);

  // Timeframe options
  const timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1'];

  // Fetch real-time market data
  const fetchMarketData = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/market-data/candles/${symbol}?timeframe=${timeframe}&limit=500`);
      if (response.ok) {
        const data = await response.json();
        setCandleData(data.candles || []);
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  }, [symbol, timeframe]);

  // Fetch ICT analysis
  const fetchICTAnalysis = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/signals/ict/analysis?symbol=${symbol}&timeframe=${timeframe}`);
      if (response.ok) {
        const data = await response.json();
        setIctLevels(data.levels || []);
        
        // Trigger signal callback if new signals are generated
        if (data.signals && data.signals.length > 0 && onSignalGenerated) {
          data.signals.forEach((signal: any) => onSignalGenerated(signal));
        }
      }
    } catch (error) {
      console.error('Error fetching ICT analysis:', error);
    }
  }, [symbol, timeframe, onSignalGenerated]);

  // Initialize chart
  useEffect(() => {
    const initChart = async () => {
      if (!canvasRef.current) return;

      try {
        // Dynamic import of Chart.js
        const { default: Chart } = await import('chart.js/auto');

        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;

        // Destroy existing chart
        if (chartRef.current) {
          chartRef.current.destroy();
        }

        // Prepare chart data
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
                display: false
              },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                titleColor: 'white',
                bodyColor: 'white',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 15,
                displayColors: false,
                callbacks: {
                  title: (context: any) => {
                    const date = new Date(context[0].parsed.x);
                    return `${symbol} - ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
                  },
                  label: (context: any) => {
                    return `Price: ${context.parsed.y.toFixed(5)}`;
                  }
                }
              }
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  displayFormats: {
                    minute: 'HH:mm',
                    hour: 'MMM DD HH:mm',
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
                  font: { size: 11 }
                }
              },
              y: {
                position: 'right',
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                  color: '#6B7280',
                  font: { size: 11 },
                  callback: function(value: any) {
                    return value.toFixed(5);
                  }
                }
              }
            },
            elements: {
              point: {
                radius: 0,
                hoverRadius: 4
              }
            }
          }
        });

      } catch (error) {
        console.error('Error initializing chart:', error);
      }
    };

    initChart();

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [candleData, chartType, showICTLevels, ictLevels]);

  // Auto refresh data
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      fetchMarketData();
      fetchICTAnalysis();
      setLastUpdate(new Date());
    }, timeframe === 'M1' ? 5000 : 30000); // More frequent for M1

    return () => clearInterval(interval);
  }, [isPlaying, fetchMarketData, fetchICTAnalysis, timeframe]);

  // Initial data load
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true);
      await Promise.all([fetchMarketData(), fetchICTAnalysis()]);
      setIsLoading(false);
    };

    loadInitialData();
  }, [symbol, timeframe, fetchMarketData, fetchICTAnalysis]);

  const prepareChartData = () => {
    if (!candleData.length) return { labels: [], datasets: [] };

    const labels = candleData.map(candle => candle.time);

    return {
      labels,
      datasets: [
        {
          label: symbol,
          data: candleData.map(candle => ({
            x: candle.time,
            y: candle.close
          })),
          borderColor: '#3B82F6',
          backgroundColor: chartType === 'area' ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
          fill: chartType === 'area',
          tension: 0.1
        }
      ]
    };
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    await Promise.all([fetchMarketData(), fetchICTAnalysis()]);
    setIsLoading(false);
    setLastUpdate(new Date());
  };

  const getICTLevelColor = (type: string, direction: string) => {
    const colors = {
      order_block: direction === 'bullish' ? '#10B981' : '#EF4444',
      fair_value_gap: direction === 'bullish' ? '#3B82F6' : '#F59E0B',
      breaker_block: direction === 'bullish' ? '#8B5CF6' : '#EC4899',
      support: '#10B981',
      resistance: '#EF4444'
    };
    return colors[type as keyof typeof colors] || '#6B7280';
  };

  if (isLoading && !candleData.length) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-medium mb-2">Loading Chart Data</h3>
            <p className="text-sm text-gray-600">Fetching {symbol} {timeframe} data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            {symbol} - {timeframe}
            <Badge variant="outline" className="text-xs">
              ICT Analysis
            </Badge>
          </CardTitle>

          {showControls && (
            <div className="flex items-center gap-2">
              {/* Playback Controls */}
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePlayPause}
                >
                  {isPlaying ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  disabled={isLoading}
                >
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
              </div>

              {/* Chart Type Controls */}
              <div className="flex items-center gap-1">
                {(['line', 'area'] as const).map((type) => (
                  <Button
                    key={type}
                    variant={chartType === type ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType(type)}
                  >
                    {type === 'line' && <TrendingUp className="h-3 w-3" />}
                    {type === 'area' && <Activity className="h-3 w-3" />}
                  </Button>
                ))}
              </div>

              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Analysis Controls */}
        {showControls && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {/* ICT Analysis Toggles */}
              <div className="flex items-center gap-1">
                <Button
                  variant={showICTLevels ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setShowICTLevels(!showICTLevels)}
                >
                  <Target className="h-3 w-3 mr-1" />
                  ICT Levels
                </Button>
                <Button
                  variant={showSignals ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setShowSignals(!showSignals)}
                >
                  <Activity className="h-3 w-3 mr-1" />
                  Signals
                </Button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {candleData.length} candles
              </Badge>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent>
        {/* Main Chart */}
        <div style={{ height: `${height}px`, position: 'relative' }}>
          <canvas ref={canvasRef} />
        </div>

        {/* ICT Levels Summary */}
        {showICTLevels && ictLevels.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <h4 className="text-sm font-medium mb-2">Active ICT Levels</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {ictLevels.filter(level => level.active).slice(0, 6).map((level) => (
                <div key={level.id} className="flex items-center justify-between p-2 border rounded text-xs">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded"
                      style={{ backgroundColor: getICTLevelColor(level.type, level.direction) }}
                    />
                    <span className="font-medium">{level.type.replace('_', ' ').toUpperCase()}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{level.price.toFixed(5)}</div>
                    <div className={`text-xs ${level.direction === 'bullish' ? 'text-green-600' : 'text-red-600'}`}>
                      {level.direction}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Chart Info */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
            <span>{candleData.length} data points</span>
            <span>{ictLevels.filter(l => l.active).length} active levels</span>
          </div>
          
          <div className="flex items-center gap-2">
            {isPlaying && (
              <Badge variant="outline" className="text-xs text-green-600">
                Live
              </Badge>
            )}
            <Badge variant="outline" className="text-xs">
              {timeframe}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TradingViewChart; 