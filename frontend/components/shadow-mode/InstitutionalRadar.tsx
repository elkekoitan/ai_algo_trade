'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface InstitutionalFlow {
  flow_id: string;
  symbol: string;
  institution_type: string;
  flow_direction: string;
  volume: number;
  confidence: number;
  source: string;
}

export default function InstitutionalRadar() {
  const [flows, setFlows] = useState<InstitutionalFlow[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchFlows = async () => {
      try {
        const response = await fetch('/api/v1/shadow/institutional-flows');
        const data = await response.json();
        setFlows(data.recent_flows || []);
      } catch (error) {
        console.error('Failed to fetch institutional flows:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFlows();
    const interval = setInterval(fetchFlows, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-xl border border-orange-500/30 rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          🏛️ Institutional Radar
        </h3>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-green-400 text-sm">Live</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {flows.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No institutional flows detected
            </div>
          ) : (
            flows.slice(0, 5).map((flow, index) => (
              <motion.div
                key={flow.flow_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-orange-400 font-semibold">{flow.symbol}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      flow.flow_direction === 'BUY' 
                        ? 'bg-green-500/20 text-green-400' 
                        : flow.flow_direction === 'SELL'
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {flow.flow_direction}
                    </span>
                  </div>
                  <span className="text-gray-400 text-sm">
                    {flow.confidence.toFixed(1)}% confidence
                  </span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">
                    {flow.institution_type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="text-blue-400">
                    ${(flow.volume / 1000000).toFixed(1)}M
                  </span>
                </div>
                
                <div className="mt-2 bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full"
                    style={{ width: `${flow.confidence}%` }}
                  ></div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}
    </motion.div>
  );
} 