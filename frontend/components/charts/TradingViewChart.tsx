"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, IChartApi, ISeriesApi, UTCTimestamp } from 'lightweight-charts';
import ApiService from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, AlertTriangle, Play, Pause } from 'lucide-react';

// Interface'leri tanımlayalım
interface CandleData {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface TradingViewChartProps {
  symbol: string;
  timeframe?: string;
  height?: number;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  timeframe = 'H1',
  height = 400,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  
  const handleResize = useCallback(() => {
    if (chartRef.current && chartContainerRef.current) {
      chartRef.current.resize(chartContainerRef.current.clientWidth, height);
    }
  }, [height]);

  // Veri çekme fonksiyonu
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await ApiService.getCandles(symbol, timeframe, 500);
      if (response.error || !response.data || !Array.isArray(response.data.candles)) {
        throw new Error(response.message || 'Failed to fetch chart data');
      }
      
      const formattedData = response.data.candles.map((d: any) => ({
        time: (new Date(d.time).getTime() / 1000) as UTCTimestamp,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })).sort((a: CandleData, b: CandleData) => a.time - b.time);

      if (candleSeriesRef.current) {
        candleSeriesRef.current.setData(formattedData);
        chartRef.current?.timeScale().fitContent();
      }
      setError(null);
    } catch (err: any) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, timeframe]);

  // Grafik oluşturma ve güncelleme
  useEffect(() => {
    if (!chartContainerRef.current) return;

    if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#D1D5DB',
      },
      grid: {
        vertLines: { color: 'rgba(75, 85, 99, 0.5)' },
        horzLines: { color: 'rgba(75, 85, 99, 0.5)' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = chart.addCandlestickSeries({
      upColor: '#10B981',
      downColor: '#EF4444',
      borderDownColor: '#EF4444',
      borderUpColor: '#10B981',
      wickDownColor: '#EF4444',
      wickUpColor: '#10B981',
    });

    fetchData(); 
    
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [symbol, timeframe, height, fetchData, handleResize]);

  // Otomatik yenileme
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      fetchData();
    }, 30000);
    return () => clearInterval(interval);
  }, [isPlaying, fetchData]);
  
  if (error) {
    return (
      <Card className="w-full" style={{ height: `${height}px` }}>
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-red-500" />
            <h3 className="text-lg font-medium mb-2">Chart Error</h3>
            <p className="text-sm text-gray-400 mb-4">{error}</p>
            <Button onClick={fetchData}>Retry</Button>
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
                    {symbol} - {timeframe}
                </CardTitle>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setIsPlaying(!isPlaying)}>
                        {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        <span className="ml-2">{isPlaying ? "Live" : "Paused"}</span>
                    </Button>
                    <Button variant="outline" size="sm" onClick={fetchData} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                </div>
            </div>
        </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} style={{ height: `${height}px`, width: '100%', position: 'relative' }}>
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm z-10">
              <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TradingViewChart; 