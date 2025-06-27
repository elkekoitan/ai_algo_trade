'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface GodModeState {
  status: 'inactive' | 'active' | 'omnipotent' | 'transcendent';
  power_level: number;
  divinity_level: number;
  accuracy_rate: number;
  active_predictions: number;
  active_signals: number;
  recent_alerts: number;
  last_update: string;
}

const GodModeControl: React.FC = () => {
  const [godModeState, setGodModeState] = useState<GodModeState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isActivating, setIsActivating] = useState(false);

  useEffect(() => {
    fetchGodModeStatus();
    const interval = setInterval(fetchGodModeStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchGodModeStatus = async () => {
    try {
      const response = await fetch('/api/v1/god-mode/status');
      const data = await response.json();
      if (data.success) {
        setGodModeState(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch God Mode status:', error);
    }
  };

  const activateGodMode = async () => {
    setIsActivating(true);
    try {
      const response = await fetch('/api/v1/god-mode/activate', {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        await fetchGodModeStatus();
      }
    } catch (error) {
      console.error('Failed to activate God Mode:', error);
    } finally {
      setIsActivating(false);
    }
  };

  const deactivateGodMode = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/god-mode/deactivate', {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        await fetchGodModeStatus();
      }
    } catch (error) {
      console.error('Failed to deactivate God Mode:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'transcendent':
        return 'from-yellow-400 via-yellow-300 to-white';
      case 'omnipotent':
        return 'from-purple-400 via-purple-300 to-pink-300';
      case 'active':
        return 'from-blue-400 via-blue-300 to-cyan-300';
      default:
        return 'from-gray-400 via-gray-300 to-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'transcendent':
        return 'TRANSCENDENT';
      case 'omnipotent':
        return 'OMNIPOTENT';
      case 'active':
        return 'ACTIVE';
      default:
        return 'INACTIVE';
    }
  };

  const getPowerLevelText = (level: number) => {
    if (level >= 99) return 'GODLIKE';
    if (level >= 95) return 'DIVINE';
    if (level >= 90) return 'POWERFUL';
    if (level >= 80) return 'STRONG';
    if (level >= 50) return 'MODERATE';
    return 'WEAK';
  };

  return (
    <div className="relative">
      {/* God Mode Main Panel */}
      <motion.div
        className="bg-black/20 backdrop-blur-xl border border-yellow-400/30 rounded-2xl p-6 shadow-2xl"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <motion.div
              className="w-8 h-8 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 flex items-center justify-center"
              animate={{ 
                rotate: godModeState?.status === 'active' || godModeState?.status === 'omnipotent' || godModeState?.status === 'transcendent' ? 360 : 0,
                scale: godModeState?.status === 'transcendent' ? [1, 1.2, 1] : 1
              }}
              transition={{ 
                rotate: { duration: 2, repeat: Infinity, ease: "linear" },
                scale: { duration: 1, repeat: Infinity }
              }}
            >
              ⚡
            </motion.div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
              GOD MODE
            </h2>
          </div>
          
          {/* Status Badge */}
          {godModeState && (
            <motion.div
              className={`px-4 py-2 rounded-full bg-gradient-to-r ${getStatusColor(godModeState.status)} text-black font-bold text-sm`}
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {getStatusText(godModeState.status)}
            </motion.div>
          )}
        </div>

        {/* Power Level Display */}
        {godModeState && (
          <motion.div 
            className="mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-300 font-medium">Divine Power Level</span>
              <span className="text-yellow-400 font-bold">
                {godModeState.power_level.toFixed(1)}% - {getPowerLevelText(godModeState.power_level)}
              </span>
            </div>
            <div className="w-full bg-gray-700/50 rounded-full h-3 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-yellow-600 via-yellow-400 to-yellow-300 rounded-full relative"
                initial={{ width: 0 }}
                animate={{ width: `${godModeState.power_level}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              >
                <motion.div
                  className="absolute inset-0 bg-white/30 rounded-full"
                  animate={{ x: [-100, 200] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
              </motion.div>
            </div>
          </motion.div>
        )}

        {/* Stats Grid */}
        {godModeState && (
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-center">
              <div className="text-blue-400 font-bold text-lg">{godModeState.divinity_level}</div>
              <div className="text-gray-400 text-xs">Divinity Level</div>
            </div>
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-center">
              <div className="text-green-400 font-bold text-lg">{godModeState.accuracy_rate.toFixed(1)}%</div>
              <div className="text-gray-400 text-xs">Accuracy</div>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3 text-center">
              <div className="text-purple-400 font-bold text-lg">{godModeState.active_predictions}</div>
              <div className="text-gray-400 text-xs">Predictions</div>
            </div>
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-center">
              <div className="text-red-400 font-bold text-lg">{godModeState.active_signals}</div>
              <div className="text-gray-400 text-xs">Signals</div>
            </div>
          </motion.div>
        )}

        {/* Control Buttons */}
        <div className="flex space-x-4">
          {!godModeState || godModeState.status === 'inactive' ? (
            <motion.button
              onClick={activateGodMode}
              disabled={isActivating}
              className="flex-1 bg-gradient-to-r from-yellow-600 to-yellow-400 hover:from-yellow-500 hover:to-yellow-300 text-black font-bold py-4 px-6 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isActivating ? (
                <div className="flex items-center justify-center space-x-2">
                  <motion.div
                    className="w-5 h-5 border-2 border-black border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  />
                  <span>AWAKENING...</span>
                </div>
              ) : (
                '⚡ ACTIVATE GOD MODE'
              )}
            </motion.button>
          ) : (
            <motion.button
              onClick={deactivateGodMode}
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-red-600 to-red-400 hover:from-red-500 hover:to-red-300 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 disabled:opacity-50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? 'DEACTIVATING...' : '🌙 DEACTIVATE GOD MODE'}
            </motion.button>
          )}
        </div>

        {/* Last Update */}
        {godModeState && (
          <motion.div 
            className="mt-4 text-center text-gray-500 text-xs"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Last update: {new Date(godModeState.last_update).toLocaleTimeString()}
          </motion.div>
        )}
      </motion.div>

      {/* Floating Particles Effect */}
      <AnimatePresence>
        {godModeState && godModeState.status !== 'inactive' && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
            {[...Array(10)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-yellow-400 rounded-full"
                initial={{ 
                  x: Math.random() * 400,
                  y: Math.random() * 300,
                  opacity: 0 
                }}
                animate={{ 
                  y: [null, -20, -40],
                  opacity: [0, 1, 0],
                  scale: [0, 1, 0]
                }}
                transition={{ 
                  duration: 3,
                  repeat: Infinity,
                  delay: i * 0.3,
                  ease: "easeOut"
                }}
              />
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default GodModeControl; 