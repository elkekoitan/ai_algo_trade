"use client"

import React, { useState, useEffect } from 'react'
import ShadowControlPanel from '../../components/shadow-mode/ShadowControlPanel'
import WhaleTracker from '../../components/shadow-mode/WhaleTracker'
import DarkPoolMonitor from '../../components/shadow-mode/DarkPoolMonitor'
import InstitutionalRadar from '../../components/shadow-mode/InstitutionalRadar'

// Types
interface ShadowModeStatus {
  status: string
  whales_detected_24h: number
  dark_pools_monitored: number
  institutional_flows_tracked: number
  stealth_orders_active: number
  system_health: number
  last_update: string
}

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

export default function ShadowModePage() {
  const [status, setStatus] = useState<ShadowModeStatus | null>(null)
  const [analytics, setAnalytics] = useState<ShadowAnalytics | null>(null)
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSD')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch Shadow Mode status
  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/shadow-mode/status')
      if (!response.ok) throw new Error('Failed to fetch status')
      const data = await response.json()
      setStatus(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status')
    }
  }

  // Fetch Shadow Analytics
  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/analytics?symbol=${selectedSymbol}`)
      if (!response.ok) throw new Error('Failed to fetch analytics')
      const data = await response.json()
      setAnalytics(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics')
    }
  }

  // Initialize data
  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true)
      await Promise.all([fetchStatus(), fetchAnalytics()])
      setIsLoading(false)
    }

    initializeData()

    // Set up auto-refresh
    const interval = setInterval(() => {
      fetchStatus()
      fetchAnalytics()
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [selectedSymbol])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-white mb-2">Initializing Shadow Mode</h2>
          <p className="text-gray-400">Connecting to institutional networks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">
        {/* Header */}
      <div className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 p-6 border-b border-purple-500/30">
        <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                🌑 Shadow Mode
          </h1>
              <p className="text-gray-300 mt-2">
                Institutional tracking • Whale detection • Dark pool monitoring
              </p>
        </div>

            {/* Symbol Selector */}
            <div className="flex items-center space-x-4">
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="bg-gray-800 border border-purple-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-400"
              >
                <option value="BTCUSD">BTCUSD</option>
                <option value="EURUSD">EURUSD</option>
                <option value="GBPUSD">GBPUSD</option>
                <option value="XAUUSD">XAUUSD</option>
                <option value="US30">US30</option>
              </select>
              
              {/* Status Indicator */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${status?.status === 'active' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-sm text-gray-300">
                  {status?.status === 'active' ? 'Shadow Mode Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          {status && (
            <div className="grid grid-cols-5 gap-4 mt-6">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-purple-500/20">
                <div className="text-2xl font-bold text-purple-400">{status.whales_detected_24h}</div>
                <div className="text-sm text-gray-400">Whales 24h</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-blue-500/20">
                <div className="text-2xl font-bold text-blue-400">{status.dark_pools_monitored}</div>
                <div className="text-sm text-gray-400">Dark Pools</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-orange-500/20">
                <div className="text-2xl font-bold text-orange-400">{status.institutional_flows_tracked}</div>
                <div className="text-sm text-gray-400">Institutional Flows</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-green-500/20">
                <div className="text-2xl font-bold text-green-400">{status.stealth_orders_active}</div>
                <div className="text-sm text-gray-400">Stealth Orders</div>
            </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-yellow-500/20">
                <div className="text-2xl font-bold text-yellow-400">{status.system_health.toFixed(1)}%</div>
                <div className="text-sm text-gray-400">System Health</div>
              </div>
            </div>
          )}
              </div>
            </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/50 border border-red-500/30 rounded-lg p-4 m-6">
          <div className="flex items-center space-x-2">
            <span className="text-red-400">⚠️</span>
            <span className="text-red-300">Error: {error}</span>
            <button
              onClick={() => {
                setError(null)
                fetchStatus()
                fetchAnalytics()
              }}
              className="ml-auto text-red-400 hover:text-red-300"
            >
              Retry
            </button>
          </div>
        </div>
      )}

        {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Shadow Control Panel */}
        <ShadowControlPanel analytics={analytics} selectedSymbol={selectedSymbol} />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Whale Tracker */}
          <div className="bg-gray-900/50 rounded-xl border border-purple-500/30 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-900/50 to-purple-800/50 p-4 border-b border-purple-500/30">
              <h3 className="text-xl font-bold text-purple-300 flex items-center">
                🐋 Whale Tracker
                <span className="ml-2 text-sm bg-purple-500/20 px-2 py-1 rounded-full">
                  {analytics?.whale_activity_score.toFixed(1) || 0}% Active
                </span>
              </h3>
                    </div>
            <WhaleTracker symbol={selectedSymbol} />
                  </div>
                  
          {/* Dark Pool Monitor */}
          <div className="bg-gray-900/50 rounded-xl border border-blue-500/30 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 p-4 border-b border-blue-500/30">
              <h3 className="text-xl font-bold text-blue-300 flex items-center">
                🌑 Dark Pool Monitor
                <span className="ml-2 text-sm bg-blue-500/20 px-2 py-1 rounded-full">
                  {analytics?.dark_pool_intensity.toFixed(1) || 0}% Intensity
                </span>
              </h3>
                    </div>
            <DarkPoolMonitor symbol={selectedSymbol} />
                    </div>
                  </div>
                  
        {/* Institutional Radar - Full Width */}
        <div className="bg-gray-900/50 rounded-xl border border-orange-500/30 overflow-hidden">
          <div className="bg-gradient-to-r from-orange-900/50 to-orange-800/50 p-4 border-b border-orange-500/30">
            <h3 className="text-xl font-bold text-orange-300 flex items-center">
              🏛️ Institutional Radar
              <span className="ml-2 text-sm bg-orange-500/20 px-2 py-1 rounded-full">
                                 Smart Money: {analytics?.smart_money_flow ? (analytics.smart_money_flow > 0 ? '+' : '') + analytics.smart_money_flow.toFixed(1) : '0'}
              </span>
            </h3>
          </div>
          <InstitutionalRadar symbol={selectedSymbol} />
                  </div>

        {/* Analytics Summary */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-900/50 rounded-xl p-6 border border-purple-500/30">
              <h4 className="text-lg font-semibold text-purple-300 mb-4">Whale Metrics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Activity Score</span>
                  <span className="text-purple-400 font-semibold">{analytics.whale_activity_score.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sentiment</span>
                  <span className={`font-semibold ${analytics.whale_sentiment > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {analytics.whale_sentiment > 0 ? '+' : ''}{analytics.whale_sentiment.toFixed(1)}
                  </span>
            </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">24h Volume</span>
                  <span className="text-purple-400 font-semibold">{analytics.whale_volume_24h.toFixed(2)}</span>
                    </div>
                    </div>
                  </div>
                  
            <div className="bg-gray-900/50 rounded-xl p-6 border border-blue-500/30">
              <h4 className="text-lg font-semibold text-blue-300 mb-4">Dark Pool Metrics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Intensity</span>
                  <span className="text-blue-400 font-semibold">{analytics.dark_pool_intensity.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Hidden Liquidity</span>
                  <span className="text-blue-400 font-semibold">{analytics.hidden_liquidity.toFixed(0)}</span>
                  </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Fragmentation</span>
                  <span className="text-blue-400 font-semibold">{analytics.market_fragmentation.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-900/50 rounded-xl p-6 border border-orange-500/30">
              <h4 className="text-lg font-semibold text-orange-300 mb-4">Market Impact</h4>
              <div className="space-y-3">
                    <div className="flex justify-between">
                  <span className="text-gray-400">Predicted Impact</span>
                  <span className="text-orange-400 font-semibold">{analytics.predicted_impact.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                  <span className="text-gray-400">Volatility Forecast</span>
                  <span className="text-orange-400 font-semibold">{analytics.volatility_forecast.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                  <span className="text-gray-400">Trend Strength</span>
                  <span className="text-orange-400 font-semibold">{analytics.trend_strength.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 