'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface ShadowState {
  status: string;
  stealth_level: number;
  active_components: any;
  recent_activity: any;
  metrics: any;
  last_update: string;
}

interface ShadowAlert {
  alert_id: string;
  type: string;
  priority: string;
  title: string;
  message: string;
  symbol?: string;
  stealth_required: boolean;
  created_at: string;
}

export default function ShadowControlPanel() {
  const [shadowState, setShadowState] = useState<ShadowState | null>(null);
  const [alerts, setAlerts] = useState<ShadowAlert[]>([]);
  const [isActivating, setIsActivating] = useState(false);
  const [stealthLevel, setStealthLevel] = useState(5);

  useEffect(() => {
    const fetchShadowData = async () => {
      try {
        const [stateResponse, alertsResponse] = await Promise.all([
          fetch('/api/v1/shadow/status'),
          fetch('/api/v1/shadow/alerts')
        ]);
        
        const stateData = await stateResponse.json();
        const alertsData = await alertsResponse.json();
        
        setShadowState(stateData);
        setAlerts(alertsData || []);
      } catch (error) {
        console.error('Failed to fetch shadow data:', error);
      }
    };

    fetchShadowData();
    const interval = setInterval(fetchShadowData, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleActivate = async () => {
    setIsActivating(true);
    try {
      const response = await fetch(`/api/v1/shadow/activate?stealth_level=${stealthLevel}`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'activated') {
        // Refresh state
        const stateResponse = await fetch('/api/v1/shadow/status');
        const stateData = await stateResponse.json();
        setShadowState(stateData);
      }
    } catch (error) {
      console.error('Failed to activate Shadow Mode:', error);
    } finally {
      setIsActivating(false);
    }
  };

  const handleDeactivate = async () => {
    try {
      const response = await fetch('/api/v1/shadow/deactivate', {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'deactivated') {
        // Refresh state
        const stateResponse = await fetch('/api/v1/shadow/status');
        const stateData = await stateResponse.json();
        setShadowState(stateData);
      }
    } catch (error) {
      console.error('Failed to deactivate Shadow Mode:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-500/20';
      case 'stealth': return 'text-purple-400 bg-purple-500/20';
      case 'hunting': return 'text-orange-400 bg-orange-500/20';
      case 'inactive': return 'text-gray-400 bg-gray-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'text-red-400 bg-red-500/20';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/20';
      case 'LOW': return 'text-green-400 bg-green-500/20';
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
        <h3 className="text-2xl font-bold text-white flex items-center gap-2">
          🥷 Shadow Mode Control
        </h3>
        {shadowState && (
          <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(shadowState.status)}`}>
            {shadowState.status.toUpperCase()}
          </div>
        )}
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Activation Controls */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">Activation Controls</h4>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Stealth Level: {stealthLevel}/10
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={stealthLevel}
                onChange={(e) => setStealthLevel(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                disabled={shadowState?.status === 'active'}
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Basic</span>
                <span>Ninja</span>
              </div>
            </div>
            
            <div className="flex gap-3">
              {shadowState?.status === 'inactive' ? (
                <button
                  onClick={handleActivate}
                  disabled={isActivating}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50"
                >
                  {isActivating ? '🔄 Activating...' : '🥷 Activate Shadow Mode'}
                </button>
              ) : (
                <button
                  onClick={handleDeactivate}
                  className="flex-1 bg-gradient-to-r from-gray-600 to-gray-700 text-white font-semibold py-3 px-6 rounded-lg hover:from-gray-700 hover:to-gray-800 transition-all"
                >
                  🛑 Deactivate
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Status Overview */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">System Status</h4>
          
          {shadowState && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="text-blue-400 text-sm">Whales</div>
                  <div className="text-white text-xl font-bold">
                    {shadowState.recent_activity?.whale_detections || 0}
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="text-purple-400 text-sm">Dark Pools</div>
                  <div className="text-white text-xl font-bold">
                    {shadowState.recent_activity?.dark_pool_activities || 0}
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="text-green-400 text-sm">Institutions</div>
                  <div className="text-white text-xl font-bold">
                    {shadowState.recent_activity?.institutional_flows || 0}
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-3">
                  <div className="text-orange-400 text-sm">Patterns</div>
                  <div className="text-white text-xl font-bold">
                    {shadowState.recent_activity?.manipulation_patterns || 0}
                  </div>
                </div>
              </div>
              
              {shadowState.metrics && (
                <div className="bg-gray-900/30 rounded-lg p-3">
                  <div className="text-sm text-gray-400 mb-2">Performance Metrics</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-400">Detection Accuracy:</span>
                      <span className="ml-2 text-green-400">
                        {shadowState.metrics.detection_accuracy?.toFixed(1) || 0}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-400">Stealth Success:</span>
                      <span className="ml-2 text-purple-400">
                        {shadowState.metrics.stealth_success_rate?.toFixed(1) || 0}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Recent Alerts */}
      <div>
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          🚨 Recent Alerts
        </h4>
        
        {alerts.length === 0 ? (
          <div className="text-center py-6 text-gray-400 bg-gray-900/30 rounded-lg">
            No alerts detected
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {alerts.slice(0, 5).map((alert, index) => (
              <motion.div
                key={alert.alert_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-900/50 rounded-lg p-3 border border-gray-700/50"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(alert.priority)}`}>
                      {alert.priority}
                    </span>
                    {alert.stealth_required && (
                      <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-400">
                        STEALTH
                      </span>
                    )}
                  </div>
                  <span className="text-gray-400 text-xs">
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="text-white font-medium mb-1">{alert.title}</div>
                <div className="text-gray-300 text-sm">{alert.message}</div>
                
                {alert.symbol && (
                  <div className="mt-2">
                    <span className="text-orange-400 text-sm font-semibold">{alert.symbol}</span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
} 