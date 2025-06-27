"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Activity, BarChart3 } from "lucide-react";

interface ChartData {
  time: string;
  value: number;
  volume: number;
}

export default function HolographicChart() {
  const [data, setData] = useState<ChartData[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState("1H");

  // Generate realistic market data
  useEffect(() => {
    const generateData = () => {
      const points = 50;
      const baseValue = 1.16952;
      let currentValue = baseValue;
      const newData: ChartData[] = [];

      for (let i = 0; i < points; i++) {
        const volatility = 0.002;
        const change = (Math.random() - 0.5) * volatility;
        currentValue += change;
        
        newData.push({
          time: new Date(Date.now() - (points - i) * 60000).toISOString(),
          value: currentValue,
          volume: Math.random() * 1000 + 500
        });
      }
      
      setData(newData);
    };

    generateData();
    const interval = setInterval(generateData, 2000);
    return () => clearInterval(interval);
  }, [selectedTimeframe]);

  const getChartDimensions = () => ({
    width: 400,
    height: 200,
    padding: 40
  });

  const normalizeData = () => {
    if (data.length === 0) return { points: [], volumes: [] };
    
    const { width, height, padding } = getChartDimensions();
    const minValue = Math.min(...data.map(d => d.value));
    const maxValue = Math.max(...data.map(d => d.value));
    const maxVolume = Math.max(...data.map(d => d.volume));
    
    const points = data.map((point, index) => ({
      x: padding + (index / (data.length - 1)) * (width - 2 * padding),
      y: padding + ((maxValue - point.value) / (maxValue - minValue)) * (height - 2 * padding),
      value: point.value,
      time: point.time
    }));

    const volumes = data.map((point, index) => ({
      x: padding + (index / (data.length - 1)) * (width - 2 * padding),
      height: (point.volume / maxVolume) * 30,
      volume: point.volume
    }));

    return { points, volumes };
  };

  const { points, volumes } = normalizeData();
  const { width, height } = getChartDimensions();

  const currentPrice = data.length > 0 ? data[data.length - 1].value : 0;
  const priceChange = data.length > 1 ? currentPrice - data[data.length - 2].value : 0;
  const priceChangePercent = data.length > 1 ? (priceChange / data[data.length - 2].value) * 100 : 0;

  const pathData = points.length > 0 
    ? `M ${points[0].x} ${points[0].y} ` + 
      points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')
    : '';

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-black via-purple-900/20 to-black overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-quantum-primary/5 via-transparent to-quantum-accent/5" />
        
        {/* Grid overlay */}
        <svg className="absolute inset-0 w-full h-full opacity-10">
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Header */}
      <div className="relative z-10 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            >
              <Activity className="w-6 h-6 text-quantum-primary" />
            </motion.div>
            <div>
              <h3 className="text-lg font-bold text-white">Holographic Analysis</h3>
              <p className="text-sm text-gray-400">EURUSD Real-time Data</p>
            </div>
          </div>

          {/* Price Display */}
          <div className="text-right">
            <p className="text-2xl font-bold text-white font-mono">
              {currentPrice.toFixed(5)}
            </p>
            <div className={`flex items-center gap-1 ${priceChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {priceChange >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span className="text-sm font-mono">
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(5)} ({priceChangePercent.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>

        {/* Timeframe Controls */}
        <div className="flex items-center gap-2 mb-4">
          {['5M', '15M', '30M', '1H', '4H', '1D'].map((tf) => (
            <motion.button
              key={tf}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                selectedTimeframe === tf
                  ? 'bg-quantum-primary text-black'
                  : 'bg-white/10 text-gray-400 hover:bg-white/20'
              }`}
            >
              {tf}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Chart Area */}
      <div className="relative z-10 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="quantum-panel p-4"
        >
          <svg width="100%" height="250" viewBox={`0 0 ${width} ${height + 50}`}>
            {/* Gradient definitions */}
            <defs>
              <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgba(0, 255, 136, 0.3)" />
                <stop offset="100%" stopColor="rgba(0, 255, 136, 0.05)" />
              </linearGradient>
              <linearGradient id="glowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgba(0, 255, 136, 0.8)" />
                <stop offset="100%" stopColor="rgba(0, 255, 136, 0.2)" />
              </linearGradient>
            </defs>

            {/* Volume bars */}
            {volumes.map((vol, index) => (
              <motion.rect
                key={index}
                x={vol.x - 2}
                y={height - vol.height}
                width="4"
                height={vol.height}
                fill="rgba(0, 212, 255, 0.3)"
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: index * 0.02 }}
              />
            ))}

            {/* Area under curve */}
            {pathData && (
              <motion.path
                d={`${pathData} L ${points[points.length - 1]?.x || 0} ${height} L ${points[0]?.x || 0} ${height} Z`}
                fill="url(#chartGradient)"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1 }}
              />
            )}

            {/* Main price line */}
            {pathData && (
              <motion.path
                d={pathData}
                fill="none"
                stroke="url(#glowGradient)"
                strokeWidth="2"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 2, ease: "easeInOut" }}
              />
            )}

            {/* Data points */}
            {points.map((point, index) => (
              <motion.g key={index}>
                <motion.circle
                  cx={point.x}
                  cy={point.y}
                  r="3"
                  fill="rgba(0, 255, 136, 0.8)"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                />
                <motion.circle
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  fill="none"
                  stroke="rgba(0, 255, 136, 0.3)"
                  strokeWidth="1"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ 
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 0, 0.5]
                  }}
                  transition={{ 
                    delay: index * 0.05,
                    duration: 2,
                    repeat: Infinity
                  }}
                />
              </motion.g>
            ))}

            {/* Current price indicator */}
            {points.length > 0 && (
              <motion.g>
                <motion.line
                  x1={0}
                  y1={points[points.length - 1].y}
                  x2={width}
                  y2={points[points.length - 1].y}
                  stroke="rgba(255, 255, 255, 0.5)"
                  strokeWidth="1"
                  strokeDasharray="5,5"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                />
                <motion.rect
                  x={width - 80}
                  y={points[points.length - 1].y - 10}
                  width="70"
                  height="20"
                  rx="3"
                  fill="rgba(0, 0, 0, 0.8)"
                  stroke="rgba(0, 255, 136, 0.5)"
                  strokeWidth="1"
                />
                <text
                  x={width - 45}
                  y={points[points.length - 1].y + 4}
                  textAnchor="middle"
                  fill="white"
                  fontSize="10"
                  fontFamily="monospace"
                >
                  {currentPrice.toFixed(5)}
                </text>
              </motion.g>
            )}
          </svg>
        </motion.div>
      </div>

      {/* Stats Panel */}
      <div className="absolute bottom-4 left-4 right-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="quantum-panel p-4"
        >
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <BarChart3 className="w-5 h-5 text-quantum-primary mx-auto mb-1" />
              <p className="text-xs text-gray-400">Volume</p>
              <p className="text-sm font-bold text-white">
                {volumes.length > 0 ? volumes[volumes.length - 1].volume.toFixed(0) : '0'}
              </p>
            </div>
            
            <div className="text-center">
              <TrendingUp className="w-5 h-5 text-green-400 mx-auto mb-1" />
              <p className="text-xs text-gray-400">High</p>
              <p className="text-sm font-bold text-white">
                {data.length > 0 ? Math.max(...data.map(d => d.value)).toFixed(5) : '0'}
              </p>
            </div>
            
            <div className="text-center">
              <TrendingDown className="w-5 h-5 text-red-400 mx-auto mb-1" />
              <p className="text-xs text-gray-400">Low</p>
              <p className="text-sm font-bold text-white">
                {data.length > 0 ? Math.min(...data.map(d => d.value)).toFixed(5) : '0'}
              </p>
            </div>
            
            <div className="text-center">
              <Activity className="w-5 h-5 text-quantum-accent mx-auto mb-1" />
              <p className="text-xs text-gray-400">Volatility</p>
              <p className="text-sm font-bold text-white">
                {data.length > 1 ? 
                  (Math.abs(Math.max(...data.map(d => d.value)) - Math.min(...data.map(d => d.value))) * 10000).toFixed(1)
                  : '0'
                } pips
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 