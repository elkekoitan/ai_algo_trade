'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface WhaleDetection {
  detection_id: string;
  symbol: string;
  whale_size: string;
  position_size: number;
  confidence: number;
  pattern_type: string;
  stealth_score: number;
  detection_time: string;
}

export default function WhaleTracker() {
  const [whales, setWhales] = useState<WhaleDetection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchWhales = async () => {
      try {
        const response = await fetch('/api/v1/shadow/whales');
        const data = await response.json();
        setWhales(data || []);
      } catch (error) {
        console.error('Failed to fetch whale detections:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWhales();
    const interval = setInterval(fetchWhales, 8000); // Update every 8 seconds

    return () => clearInterval(interval);
  }, []);

  const getWhaleSizeColor = (size: string) => {
    switch (size) {
      case 'massive': return 'text-red-400 bg-red-500/20';
      case 'large': return 'text-orange-400 bg-orange-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'small': return 'text-green-400 bg-green-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getWhaleSizeIcon = (size: string) => {
    switch (size) {
      case 'massive': return '🐋';
      case 'large': return '🐳';
      case 'medium': return '🐟';
      case 'small': return '🐠';
      default: return '🐟';
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
          🐋 Whale Tracker
        </h3>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          <span className="text-blue-400 text-sm">Hunting</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {whales.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No whales detected in the waters
            </div>
          ) : (
            whales.slice(0, 4).map((whale, index) => (
              <motion.div
                key={whale.detection_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50 hover:border-orange-500/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getWhaleSizeIcon(whale.whale_size)}</span>
                    <div>
                      <span className="text-orange-400 font-semibold">{whale.symbol}</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${getWhaleSizeColor(whale.whale_size)}`}>
                        {whale.whale_size.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-blue-400 font-bold">
                      ${(whale.position_size / 1000000).toFixed(1)}M
                    </div>
                    <div className="text-gray-400 text-xs">
                      {whale.confidence.toFixed(1)}% confidence
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Pattern:</span>
                    <span className="ml-2 text-white capitalize">{whale.pattern_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Stealth:</span>
                    <span className="ml-2 text-purple-400">{whale.stealth_score.toFixed(0)}/100</span>
                  </div>
                </div>
                
                <div className="mt-3 space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Detection Confidence</span>
                    <span>{whale.confidence.toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-800 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                      style={{ width: `${whale.confidence}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Stealth Level</span>
                    <span>{whale.stealth_score.toFixed(0)}/100</span>
                  </div>
                  <div className="bg-gray-800 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                      style={{ width: `${whale.stealth_score}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="mt-3 text-xs text-gray-400">
                  Detected: {new Date(whale.detection_time).toLocaleTimeString()}
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}
    </motion.div>
  );
} 