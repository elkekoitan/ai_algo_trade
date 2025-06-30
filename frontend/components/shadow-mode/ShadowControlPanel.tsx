"use client"

import React, { useState } from 'react'

interface ShadowAnalytics {
  timestamp: string
  symbol: string
  whale_activity_score: number
  whale_sentiment: number
  whale_volume_24h: number
  dark_pool_intensity: number
  hidden_liquidity: number
  market_fragmentation: number
  institutional_pressure: number
  smart_money_flow: number
  retail_sentiment: number
  predicted_impact: number
  volatility_forecast: number
  trend_strength: number
}

interface ShadowControlPanelProps {
  analytics: ShadowAnalytics | null
  selectedSymbol: string
}

export default function ShadowControlPanel({ analytics, selectedSymbol }: ShadowControlPanelProps) {
  const [stealthMode, setStealthMode] = useState(false)
  const [autoAlerts, setAutoAlerts] = useState(true)
  const [sensitivity, setSensitivity] = useState(75)

  const startRealTimeAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/shadow-mode/analyze-realtime', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symbol: selectedSymbol,
          interval_seconds: 30
        })
      })
      
      if (response.ok) {
        console.log('Real-time analysis started')
      }
    } catch (error) {
      console.error('Failed to start real-time analysis:', error)
    }
  }

  const getRiskLevel = () => {
    if (!analytics) return 'UNKNOWN'
    
    const riskScore = (analytics.volatility_forecast + analytics.market_fragmentation + Math.abs(analytics.smart_money_flow)) / 3
    
    if (riskScore > 80) return 'HIGH'
    if (riskScore > 60) return 'MEDIUM' 
    if (riskScore > 40) return 'LOW'
    return 'VERY_LOW'
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'HIGH': return 'text-red-400 bg-red-500/20 border-red-500/50'
      case 'MEDIUM': return 'text-orange-400 bg-orange-500/20 border-orange-500/50'
      case 'LOW': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50'
      case 'VERY_LOW': return 'text-green-400 bg-green-500/20 border-green-500/50'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/50'
    }
  }

  const riskLevel = getRiskLevel()

  return (
    <div className="bg-gray-900/50 rounded-xl border border-purple-500/30 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-purple-300 flex items-center">
          🎛️ Shadow Control Panel
          <span className="ml-2 text-sm bg-purple-500/20 px-2 py-1 rounded-full">
            {selectedSymbol}
          </span>
        </h3>
        
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm border ${getRiskColor(riskLevel)}`}>
            Risk: {riskLevel}
          </span>
          <button
            onClick={startRealTimeAnalysis}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            🚀 Start Analysis
          </button>
        </div>
      </div>

      {/* Analytics Display */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800/50 rounded-lg p-4 border border-purple-500/20">
            <div className="text-sm text-gray-400 mb-1">Market Impact</div>
            <div className="text-2xl font-bold text-purple-400">
              {analytics.predicted_impact.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">
              Predicted influence on price
            </div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 border border-blue-500/20">
            <div className="text-sm text-gray-400 mb-1">Smart Money Flow</div>
            <div className={`text-2xl font-bold ${analytics.smart_money_flow > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {analytics.smart_money_flow > 0 ? '+' : ''}{analytics.smart_money_flow.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">
              Institutional direction
            </div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 border border-orange-500/20">
            <div className="text-sm text-gray-400 mb-1">Volatility Forecast</div>
            <div className="text-2xl font-bold text-orange-400">
              {analytics.volatility_forecast.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">
              Expected volatility
            </div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4 border border-yellow-500/20">
            <div className="text-sm text-gray-400 mb-1">Trend Strength</div>
            <div className="text-2xl font-bold text-yellow-400">
              {analytics.trend_strength.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">
              Directional confidence
            </div>
          </div>
        </div>
      )}

      {/* Control Settings */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sensitivity Control */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Detection Sensitivity
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="50"
              max="95"
              value={sensitivity}
              onChange={(e) => setSensitivity(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-400">
              <span>Conservative</span>
              <span className="text-purple-400 font-medium">{sensitivity}%</span>
              <span>Aggressive</span>
            </div>
          </div>
        </div>

        {/* Mode Toggles */}
        <div className="space-y-4">
          <div>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={stealthMode}
                onChange={(e) => setStealthMode(e.target.checked)}
                className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
              />
              <span className="text-sm text-gray-300">Stealth Mode</span>
              <span className="text-xs text-gray-500">(Hide from detection)</span>
            </label>
          </div>
          
          <div>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoAlerts}
                onChange={(e) => setAutoAlerts(e.target.checked)}
                className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
              />
              <span className="text-sm text-gray-300">Auto Alerts</span>
              <span className="text-xs text-gray-500">(Whale notifications)</span>
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm transition-colors flex items-center justify-center">
            🌑 Monitor Dark Pools
          </button>
          <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg text-sm transition-colors flex items-center justify-center">
            🎯 Create Stealth Order
          </button>
          <button className="w-full bg-orange-600 hover:bg-orange-700 text-white py-2 px-4 rounded-lg text-sm transition-colors flex items-center justify-center">
            📊 Export Analysis
          </button>
        </div>
      </div>

      {/* Status Information */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-gray-400">Shadow Mode Active</span>
            </div>
            <div className="text-gray-500">
              Last Update: {analytics ? new Date(analytics.timestamp).toLocaleTimeString() : 'Never'}
            </div>
          </div>
          
          <div className="text-gray-500">
            Monitoring: {selectedSymbol} • Sensitivity: {sensitivity}%
          </div>
        </div>
      </div>
    </div>
  )
} 