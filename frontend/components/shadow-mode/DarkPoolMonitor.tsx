'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface DarkPoolSummary {
  total_activities: number;
  active_pools: number;
  total_volume: number;
  avg_price_improvement: number;
  most_active_pool: string;
  arbitrage_opportunities: number;
  institutional_activity: number;
}

interface ArbitrageOpportunity {
  activity_id: string;
  symbol: string;
  dark_pool: string;
  dark_pool_price: number;
  public_price: number;
  price_improvement: number;
  volume: number;
  estimated_profit: number;
  opportunity_score: number;
  time_remaining: string;
  risk_level: string;
}

export default function DarkPoolMonitor() {
  const [summary, setSummary] = useState<DarkPoolSummary | null>(null);
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryResponse, opportunitiesResponse] = await Promise.all([
          fetch('/api/v1/shadow/dark-pools'),
          fetch('/api/v1/shadow/arbitrage-opportunities')
        ]);
        
        const summaryData = await summaryResponse.json();
        const opportunitiesData = await opportunitiesResponse.json();
        
        setSummary(summaryData);
        setOpportunities(opportunitiesData || []);
      } catch (error) {
        console.error('Failed to fetch dark pool data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 12000); // Update every 12 seconds

    return () => clearInterval(interval);
  }, []);

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'text-green-400 bg-green-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'high': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-xl border border-orange-500/30 rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          🌑 Dark Pool Monitor
        </h3>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
          <span className="text-purple-400 text-sm">Scanning</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stats */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700/50">
                <div className="text-purple-400 text-sm">Active Pools</div>
                <div className="text-white text-xl font-bold">{summary.active_pools}</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700/50">
                <div className="text-blue-400 text-sm">Total Volume</div>
                <div className="text-white text-xl font-bold">
                  ${(summary.total_volume / 1000000).toFixed(1)}M
                </div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700/50">
                <div className="text-green-400 text-sm">Activities</div>
                <div className="text-white text-xl font-bold">{summary.total_activities}</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700/50">
                <div className="text-orange-400 text-sm">Arbitrage</div>
                <div className="text-white text-xl font-bold">{summary.arbitrage_opportunities}</div>
              </div>
            </div>
          )}

          {/* Arbitrage Opportunities */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              💰 Arbitrage Opportunities
            </h4>
            
            {opportunities.length === 0 ? (
              <div className="text-center py-6 text-gray-400 bg-gray-900/30 rounded-lg">
                No arbitrage opportunities detected
              </div>
            ) : (
              <div className="space-y-3">
                {opportunities.slice(0, 3).map((opportunity, index) => (
                  <motion.div
                    key={opportunity.activity_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50 hover:border-purple-500/50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-orange-400 font-semibold">{opportunity.symbol}</span>
                        <span className={`px-2 py-1 rounded text-xs ${getRiskLevelColor(opportunity.risk_level)}`}>
                          {opportunity.risk_level.toUpperCase()} RISK
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-green-400 font-bold">
                          +${opportunity.estimated_profit.toFixed(0)}
                        </div>
                        <div className="text-gray-400 text-xs">
                          Score: {opportunity.opportunity_score.toFixed(1)}/10
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <span className="text-gray-400">Dark Pool:</span>
                        <span className="ml-2 text-purple-400">{opportunity.dark_pool}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Volume:</span>
                        <span className="ml-2 text-blue-400">
                          ${(opportunity.volume / 1000000).toFixed(1)}M
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <span className="text-gray-400">Dark Price:</span>
                        <span className="ml-2 text-white">{opportunity.dark_pool_price.toFixed(5)}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Public Price:</span>
                        <span className="ml-2 text-white">{opportunity.public_price.toFixed(5)}</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-green-400 text-sm">
                        +{(opportunity.price_improvement * 10000).toFixed(1)} pips improvement
                      </span>
                      <span className="text-gray-400 text-xs">
                        ⏱️ {opportunity.time_remaining}
                      </span>
                    </div>
                    
                    <div className="mt-3 bg-gray-800 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                        style={{ width: `${(opportunity.opportunity_score / 10) * 100}%` }}
                      ></div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Most Active Pool */}
          {summary?.most_active_pool && (
            <div className="bg-gray-900/30 rounded-lg p-4 border border-gray-700/50">
              <div className="text-sm text-gray-400 mb-1">Most Active Dark Pool</div>
              <div className="text-purple-400 font-semibold">{summary.most_active_pool}</div>
              <div className="text-xs text-gray-400 mt-1">
                Avg. Price Improvement: +{(summary.avg_price_improvement * 10000).toFixed(1)} pips
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
} 