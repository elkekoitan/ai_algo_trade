"use client"

import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, AlertCircle, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import GlassCard from '@/components/quantum/GlassCard'

interface WhaleDetection {
  id: string
  timestamp: string
  symbol: string
  size: 'small' | 'medium' | 'large' | 'massive'
  volume: number
  value: number
  order_type: 'buy' | 'sell'
  price: number
  confidence: number
  impact_score: number
  spread_analysis: {
    spread: number
    spread_ratio: number
  }
  volume_profile: {
    volume_zscore: number
    volume_ratio: number
  }
  time_analysis: {
    time_of_day: number
    market_session: string
  }
}

interface WhaleAlert {
  alert_id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  whale_data: WhaleDetection
  recommended_action: string
}

interface WhaleTrackerProps {
  symbol: string
}

export default function WhaleTracker({ symbol }: WhaleTrackerProps) {
  const [whales, setWhales] = useState<WhaleDetection[]>([])
  const [alerts, setAlerts] = useState<WhaleAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch whale detections
  const fetchWhales = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/whales?symbol=${symbol}`)
      if (!response.ok) throw new Error('Failed to fetch whales')
      const data = await response.json()
      setWhales(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch whales')
    }
  }

  // Fetch whale alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/whale-alerts?symbol=${symbol}`)
      if (!response.ok) throw new Error('Failed to fetch alerts')
      const data = await response.json()
      setAlerts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts')
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      await Promise.all([fetchWhales(), fetchAlerts()])
      setIsLoading(false)
    }

    loadData()

    // Auto-refresh every 15 seconds
    const interval = setInterval(() => {
      fetchWhales()
      fetchAlerts()
    }, 15000)

    return () => clearInterval(interval)
  }, [symbol])

  const getWhaleIcon = (size: string) => {
    switch (size) {
      case 'massive': return '🐋'
      case 'large': return '🐳'
      case 'medium': return '🐙'
      case 'small': return '🐠'
      default: return '🐟'
    }
  }

  const getSizeColor = (size: string) => {
    switch (size) {
      case 'massive': return 'text-red-400 bg-red-500/20 border-red-500/50'
      case 'large': return 'text-orange-400 bg-orange-500/20 border-orange-500/50'
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50'
      case 'small': return 'text-green-400 bg-green-500/20 border-green-500/50'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/50'
    }
  }

  const getOrderColor = (orderType: string) => {
    return orderType === 'buy' ? 'text-green-400' : 'text-red-400'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/50'
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/50'
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50'
      case 'low': return 'text-green-400 bg-green-500/20 border-green-500/50'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/50'
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-2"></div>
        <p className="text-gray-400">Scanning for whales...</p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-3">
          <p className="text-red-300 text-sm">Error: {error}</p>
        </div>
      )}

      {/* Whale Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-purple-300 flex items-center">
            🚨 Active Alerts ({alerts.length})
          </h4>
          {alerts.slice(0, 3).map((alert) => (
            <div key={alert.alert_id} className="bg-gray-800/50 rounded-lg p-3 border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded-full text-xs border ${getSeverityColor(alert.severity)}`}>
                  {alert.severity.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(alert.whale_data.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-white text-sm mb-2">{alert.message}</p>
              <p className="text-gray-400 text-xs">{alert.recommended_action}</p>
            </div>
          ))}
        </div>
      )}

      {/* Recent Whale Detections */}
      <div>
        <h4 className="text-sm font-semibold text-purple-300 mb-3 flex items-center">
          🐋 Recent Detections ({whales.length})
        </h4>
        
        {whales.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🌊</div>
            <p className="text-gray-400">No whales detected</p>
            <p className="text-gray-500 text-sm">Monitoring {symbol} for large movements...</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {whales.map((whale) => (
              <div key={whale.id} className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-purple-500/30 transition-colors">
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getWhaleIcon(whale.size)}</span>
                    <div>
                      <span className={`px-2 py-1 rounded-full text-xs border ${getSizeColor(whale.size)}`}>
                        {whale.size.toUpperCase()}
                      </span>
                    </div>
                    <div className={`text-sm font-semibold ${getOrderColor(whale.order_type)}`}>
                      {whale.order_type.toUpperCase()}
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm text-gray-400">
                      {new Date(whale.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {whale.time_analysis.market_session} session
                    </div>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div>
                    <div className="text-xs text-gray-400">Volume</div>
                    <div className="text-white font-mono text-sm">
                      {whale.volume.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Value</div>
                    <div className="text-green-400 font-mono text-sm">
                      ${(whale.value / 1000000).toFixed(2)}M
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Price</div>
                    <div className="text-white font-mono text-sm">
                      {whale.price.toFixed(5)}
                    </div>
                  </div>
                </div>

                {/* Analysis Metrics */}
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <div className="text-xs text-gray-400">Confidence</div>
                    <div className="flex items-center space-x-2">
                      <div className="text-cyan-400 font-semibold text-sm">
                        {(whale.confidence * 100).toFixed(0)}%
                      </div>
                      <div className="w-16 bg-gray-700 rounded-full h-1">
                        <div 
                          className="bg-cyan-400 h-1 rounded-full" 
                          style={{width: `${whale.confidence * 100}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Impact Score</div>
                    <div className="flex items-center space-x-2">
                      <div className={`font-semibold text-sm ${whale.impact_score > 70 ? 'text-red-400' : whale.impact_score > 40 ? 'text-orange-400' : 'text-yellow-400'}`}>
                        {whale.impact_score.toFixed(0)}
                      </div>
                      <div className="w-16 bg-gray-700 rounded-full h-1">
                        <div 
                          className={`h-1 rounded-full ${whale.impact_score > 70 ? 'bg-red-400' : whale.impact_score > 40 ? 'bg-orange-400' : 'bg-yellow-400'}`}
                          style={{width: `${whale.impact_score}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Advanced Analysis */}
                <div className="bg-gray-900/50 rounded p-3 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Volume Z-Score:</span>
                    <span className="text-purple-400 font-mono">
                      {whale.volume_profile.volume_zscore.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Volume Ratio:</span>
                    <span className="text-purple-400 font-mono">
                      {whale.volume_profile.volume_ratio.toFixed(2)}x
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Spread:</span>
                    <span className="text-purple-400 font-mono">
                      {(whale.spread_analysis.spread * 10000).toFixed(1)} pips
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2 mt-3">
                  <button className="flex-1 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 text-xs py-2 px-3 rounded border border-blue-500/30 transition-colors">
                    Follow Whale
                  </button>
                  <button className="flex-1 bg-green-600/20 hover:bg-green-600/30 text-green-400 text-xs py-2 px-3 rounded border border-green-500/30 transition-colors">
                    Copy Trade
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="bg-gray-800/30 rounded-lg p-4 border border-purple-500/20">
        <h5 className="text-sm font-semibold text-purple-300 mb-3">Whale Summary</h5>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-400">Total Value (24h)</div>
            <div className="text-white font-semibold">
              ${whales.reduce((sum, w) => sum + w.value, 0) / 1000000 < 1 
                ? (whales.reduce((sum, w) => sum + w.value, 0) / 1000).toFixed(0) + 'K'
                : (whales.reduce((sum, w) => sum + w.value, 0) / 1000000).toFixed(1) + 'M'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400">Buy/Sell Ratio</div>
            <div className="text-white font-semibold">
              {whales.length > 0 
                ? `${whales.filter(w => w.order_type === 'buy').length}:${whales.filter(w => w.order_type === 'sell').length}`
                : '0:0'
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 