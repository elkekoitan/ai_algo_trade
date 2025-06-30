'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Eye, Lock, AlertTriangle, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import GlassCard from '@/components/quantum/GlassCard';

interface DarkPoolActivity {
  id: string;
  timestamp: string;
  symbol: string;
  hidden_volume: number;
  visible_volume: number;
  dark_pool_ratio: number;
  liquidity_depth: number;
  execution_quality: number;
  fragmentation_score: number;
  price_improvement: number;
}

interface DarkPoolMonitorProps {
  symbol: string;
}

export default function DarkPoolMonitor({ symbol }: DarkPoolMonitorProps) {
  const [activities, setActivities] = useState<DarkPoolActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');

  // Fetch dark pool activities
  const fetchActivities = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/dark-pools?symbol=${symbol}`);
      if (!response.ok) throw new Error('Failed to fetch dark pool data');
      const data = await response.json();
      setActivities(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dark pool data');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await fetchActivities();
      setIsLoading(false);
    };

    loadData();

    // Auto-refresh every 20 seconds
    const interval = setInterval(fetchActivities, 20000);
    return () => clearInterval(interval);
  }, [symbol]);

  const getIntensityColor = (ratio: number) => {
    if (ratio > 50) return 'text-red-400 bg-red-500/20';
    if (ratio > 30) return 'text-orange-400 bg-orange-500/20';
    if (ratio > 15) return 'text-yellow-400 bg-yellow-500/20';
    return 'text-green-400 bg-green-500/20';
  };

  const getQualityColor = (quality: number) => {
    if (quality > 90) return 'text-green-400';
    if (quality > 75) return 'text-yellow-400';
    if (quality > 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const calculateAverages = () => {
    if (activities.length === 0) return {
      avgRatio: 0,
      avgQuality: 0,
      totalHidden: 0,
      avgFragmentation: 0
    };

    return {
      avgRatio: activities.reduce((sum, a) => sum + a.dark_pool_ratio, 0) / activities.length,
      avgQuality: activities.reduce((sum, a) => sum + a.execution_quality, 0) / activities.length,
      totalHidden: activities.reduce((sum, a) => sum + a.hidden_volume, 0),
      avgFragmentation: activities.reduce((sum, a) => sum + a.fragmentation_score, 0) / activities.length
    };
  };

  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
        <p className="text-gray-400">Scanning dark pools...</p>
      </div>
    );
  }

  const averages = calculateAverages();

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Eye className="h-6 w-6 text-indigo-400" />
          Dark Pool Monitor
        </h2>
        <Badge className={`${averages.avgRatio > 25 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'}`}>
          <Activity className={`h-3 w-3 mr-1 ${averages.avgRatio > 25 ? 'animate-pulse' : ''}`} />
          {averages.avgRatio > 25 ? 'HIGH ACTIVITY' : 'IDLE'}
        </Badge>
      </div>

      {!activities || activities.length === 0 ? (
        <div className="text-center py-12">
          <Lock className="h-16 w-16 mx-auto mb-4 text-gray-600" />
          <p className="text-gray-500">No dark pool activity detected</p>
          <p className="text-sm text-gray-600 mt-2">Monitoring {symbol} for hidden liquidity...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <div key={index} className="p-4 bg-gray-800/50 rounded-lg border border-indigo-500/20">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/20 rounded-lg">
                    <Lock className="h-5 w-5 text-indigo-400" />
                  </div>
                  <div>
                    <p className="font-bold text-lg">{activity.symbol}</p>
                    <p className="text-sm text-gray-400">Hidden Order Detected</p>
                  </div>
                </div>
                <Badge className="bg-yellow-500/20 text-yellow-400">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  DARK POOL
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-3 text-sm">
                <div className="bg-gray-900/50 p-3 rounded">
                  <p className="text-gray-500 mb-1">Hidden Liquidity</p>
                  <p className="font-bold text-indigo-400">
                    ${(activity.hidden_volume / 1000000).toFixed(2)}M
                  </p>
                </div>
                <div className="bg-gray-900/50 p-3 rounded">
                  <p className="text-gray-500 mb-1">Price Diff</p>
                  <p className={`font-bold ${
                    activity.price_improvement > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {activity.price_improvement > 0 ? '+' : ''}{(activity.price_improvement * 100).toFixed(3)}%
                  </p>
                </div>
                <div className="bg-gray-900/50 p-3 rounded">
                  <p className="text-gray-500 mb-1">Execution Prob</p>
                  <p className="font-bold text-cyan-400">
                    {(activity.execution_quality * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Arbitrage Opportunity Alert */}
              {Math.abs(activity.price_improvement) > 0.0003 && (
                <div className="mt-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded">
                  <p className="text-sm text-yellow-400 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Potential arbitrage opportunity detected
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Scanner Status */}
      <div className="mt-6 p-4 bg-gray-900/50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Scanner Status</span>
          <span className="text-indigo-400">
            Monitoring {activities.length} dark pools
          </span>
        </div>
        <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className="h-full bg-indigo-400 rounded-full transition-all duration-1000"
            style={{ 
              width: averages.avgRatio > 25 ? '100%' : '0%',
              transition: averages.avgRatio > 25 ? 'width 2s ease-in-out' : 'width 0.5s ease-out'
            }}
          />
        </div>
      </div>
    </GlassCard>
  );
} 