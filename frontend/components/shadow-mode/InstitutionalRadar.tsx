"use client"

import React, { useState, useEffect } from 'react'
import { Target, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import GlassCard from '@/components/quantum/GlassCard'

interface InstitutionalPosition {
  symbol: string
  institutional_position: 'LONG' | 'SHORT'
  confidence: number
  buy_pressure: number
  sell_pressure: number
  major_players: {
    commercials: string
    large_speculators: string
    small_speculators: string
  }
}

interface InstitutionalFlow {
  id: string
  timestamp: string
  symbol: string
  institution_type: 'hedge_fund' | 'pension_fund' | 'investment_bank' | 'central_bank' | 'retail_cluster'
  flow_direction: 'buy' | 'sell'
  flow_strength: number
  volume_estimate: number
  duration_minutes: number
  retail_vs_institutional: number
  momentum_score: number
  correlation_with_price: number
}

interface MarketImpact {
  symbol: string
  timeframe: string
  overall_impact_score: number
  whale_impact: number
  institutional_impact: number
  market_direction: 'bullish' | 'bearish' | 'neutral'
  direction_confidence: number
  whales_detected: number
  institutional_flows: number
  predicted_volatility: number
  smart_money_flow: number
  recommendation: string
  risk_level: string
  timestamp: string
}

interface InstitutionalRadarProps {
  symbol: string
}

export default function InstitutionalRadar({ symbol }: InstitutionalRadarProps) {
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null)
  const [flows, setFlows] = useState<InstitutionalFlow[]>([])
  const [marketImpact, setMarketImpact] = useState<MarketImpact | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h')

  // Fetch institutional flows
  const fetchFlows = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/institutional-flows?symbol=${symbol}`)
      if (!response.ok) throw new Error('Failed to fetch institutional flows')
      const data = await response.json()
      setFlows(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch institutional flows')
    }
  }

  // Fetch market impact analysis
  const fetchMarketImpact = async () => {
    try {
      const response = await fetch(`http://localhost:8002/api/v1/shadow-mode/market-impact?symbol=${symbol}&timeframe=${selectedTimeframe}`)
      if (!response.ok) throw new Error('Failed to fetch market impact')
      const data = await response.json()
      setMarketImpact(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market impact')
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      await Promise.all([fetchFlows(), fetchMarketImpact()])
      setIsLoading(false)
    }

    loadData()

    // Auto-refresh every 25 seconds
    const interval = setInterval(() => {
      fetchFlows()
      fetchMarketImpact()
    }, 25000)

    return () => clearInterval(interval)
  }, [symbol, selectedTimeframe])

  const getInstitutionIcon = (type: string) => {
    switch (type) {
      case 'hedge_fund': return '🏛️'
      case 'pension_fund': return '🏦'
      case 'investment_bank': return '🏢'
      case 'central_bank': return '🏛️'
      case 'retail_cluster': return '👥'
      default: return '🏢'
    }
  }

  const getInstitutionColor = (type: string) => {
    switch (type) {
      case 'hedge_fund': return 'text-purple-400 bg-purple-500/20'
      case 'pension_fund': return 'text-blue-400 bg-blue-500/20'
      case 'investment_bank': return 'text-orange-400 bg-orange-500/20'
      case 'central_bank': return 'text-red-400 bg-red-500/20'
      case 'retail_cluster': return 'text-green-400 bg-green-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getFlowColor = (direction: string) => {
    return direction === 'buy' ? 'text-green-400' : 'text-red-400'
  }

  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'bullish': return 'text-green-400 bg-green-500/20'
      case 'bearish': return 'text-red-400 bg-red-500/20'
      default: return 'text-yellow-400 bg-yellow-500/20'
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'HIGH': return 'text-red-400 bg-red-500/20'
      case 'MEDIUM': return 'text-orange-400 bg-orange-500/20'
      case 'LOW': return 'text-yellow-400 bg-yellow-500/20'
      case 'VERY_LOW': return 'text-green-400 bg-green-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-2"></div>
        <p className="text-gray-400">Scanning institutional activity...</p>
      </div>
    )
  }

  const totalBuyFlow = flows.filter(f => f.flow_direction === 'buy').reduce((sum, f) => sum + f.flow_strength, 0)
  const totalSellFlow = flows.filter(f => f.flow_direction === 'sell').reduce((sum, f) => sum + f.flow_strength, 0)
  const netFlow = totalBuyFlow - totalSellFlow

  return (
    <GlassCard className="p-6 space-y-6">

      {/* Market Impact Summary */}
      {marketImpact && (
        <div className="bg-gray-800/50 rounded-xl p-6 border border-orange-500/30">
          <h5 className="text-lg font-semibold text-orange-300 mb-4 flex items-center">
            📊 Market Impact Analysis
            <span className="ml-2 text-sm bg-orange-500/20 px-2 py-1 rounded-full">
              {marketImpact.timeframe.toUpperCase()}
            </span>
          </h5>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Overall Impact</div>
              <div className="text-2xl font-bold text-orange-400">
                {marketImpact.overall_impact_score.toFixed(1)}%
        </div>
              <div className="text-xs text-gray-500">market influence</div>
      </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Market Direction</div>
              <div className={`text-lg font-bold px-2 py-1 rounded ${getDirectionColor(marketImpact.market_direction)}`}>
                {marketImpact.market_direction.toUpperCase()}
              </div>
              <div className="text-xs text-gray-500">
                {marketImpact.direction_confidence.toFixed(0)}% confidence
              </div>
            </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Smart Money Flow</div>
              <div className={`text-2xl font-bold ${marketImpact.smart_money_flow > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {marketImpact.smart_money_flow > 0 ? '+' : ''}{marketImpact.smart_money_flow.toFixed(1)}
                </div>
              <div className="text-xs text-gray-500">flow direction</div>
                </div>

            <div className="bg-gray-900/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Risk Level</div>
              <div className={`text-lg font-bold px-2 py-1 rounded ${getRiskColor(marketImpact.risk_level)}`}>
                {marketImpact.risk_level}
              </div>
              <div className="text-xs text-gray-500">
                {marketImpact.predicted_volatility.toFixed(1)}% volatility
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-gray-900/30 rounded-lg p-4 border border-orange-500/20">
            <div className="text-sm font-semibold text-orange-300 mb-2">Trading Recommendation</div>
            <div className="text-white">{marketImpact.recommendation}</div>
          </div>
        </div>
      )}

      {/* Flow Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-green-500/20">
          <div className="text-xs text-gray-400 mb-1">Total Buy Flow</div>
          <div className="text-xl font-bold text-green-400">
            {totalBuyFlow.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">institutional buying</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4 border border-red-500/20">
          <div className="text-xs text-gray-400 mb-1">Total Sell Flow</div>
          <div className="text-xl font-bold text-red-400">
            {totalSellFlow.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500">institutional selling</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4 border border-orange-500/20">
          <div className="text-xs text-gray-400 mb-1">Net Flow</div>
          <div className={`text-xl font-bold ${netFlow > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {netFlow > 0 ? '+' : ''}{netFlow.toFixed(1)}
                </div>
          <div className="text-xs text-gray-500">net institutional</div>
        </div>
      </div>

      {/* Flow Activities */}
      <div>
        <h5 className="text-sm font-semibold text-orange-300 mb-3">Recent Institutional Flows</h5>
        
        {flows.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🏛️</div>
            <p className="text-gray-400">No institutional flows detected</p>
            <p className="text-gray-500 text-sm">Monitoring {symbol} for smart money movements...</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {flows.map((flow) => (
              <div key={flow.id} className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-orange-500/30 transition-colors">
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{getInstitutionIcon(flow.institution_type)}</span>
                    <div>
                      <span className={`px-2 py-1 rounded-full text-xs ${getInstitutionColor(flow.institution_type)}`}>
                        {flow.institution_type.replace('_', ' ').toUpperCase()}
                      </span>
                </div>
                    <div className={`text-sm font-semibold ${getFlowColor(flow.flow_direction)}`}>
                      {flow.flow_direction.toUpperCase()}
              </div>
            </div>

                  <div className="text-right">
                    <div className="text-sm text-gray-400">
                      {new Date(flow.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {flow.duration_minutes}min flow
                    </div>
                  </div>
                </div>

                {/* Flow Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div>
                    <div className="text-xs text-gray-400">Flow Strength</div>
                    <div className="text-orange-400 font-semibold text-sm">
                      {flow.flow_strength.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Volume Estimate</div>
                    <div className="text-white font-mono text-sm">
                      {flow.volume_estimate.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Momentum</div>
                    <div className="text-cyan-400 font-semibold text-sm">
                      {flow.momentum_score.toFixed(1)}
                    </div>
                  </div>
                </div>

                {/* Analysis Bars */}
                <div className="bg-gray-900/50 rounded p-3 space-y-3">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-gray-400">Institutional vs Retail</span>
                      <span className="text-xs text-orange-400">{(flow.retail_vs_institutional * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-orange-400 h-2 rounded-full" 
                        style={{width: `${flow.retail_vs_institutional * 100}%`}}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-gray-400">Price Correlation</span>
                      <span className="text-xs text-green-400">{(flow.correlation_with_price * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-green-400 h-2 rounded-full" 
                        style={{width: `${flow.correlation_with_price * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Flow Impact */}
                <div className="flex justify-between items-center mt-3 text-xs">
                  <span className="text-gray-400">Impact Level:</span>
                  <span className={`font-semibold ${
                    flow.flow_strength > 80 ? 'text-red-400' : 
                    flow.flow_strength > 60 ? 'text-orange-400' : 
                    flow.flow_strength > 40 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {flow.flow_strength > 80 ? 'CRITICAL' : 
                     flow.flow_strength > 60 ? 'HIGH' : 
                     flow.flow_strength > 40 ? 'MEDIUM' : 'LOW'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Smart Money Intelligence */}
      <div className="bg-gray-800/30 rounded-lg p-4 border border-orange-500/20">
        <h5 className="text-sm font-semibold text-orange-300 mb-3 flex items-center">
          🧠 Smart Money Intelligence
        </h5>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-gray-400 mb-2">Institution Distribution</div>
            <div className="space-y-1">
              {['hedge_fund', 'investment_bank', 'pension_fund', 'central_bank'].map(type => {
                const count = flows.filter(f => f.institution_type === type).length
                return (
                  <div key={type} className="flex justify-between">
                    <span className="text-gray-400">{type.replace('_', ' ')}:</span>
                    <span className="text-white">{count}</span>
                  </div>
                )
              })}
            </div>
          </div>

          <div>
            <div className="text-gray-400 mb-2">Flow Characteristics</div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-400">Avg Strength:</span>
                <span className="text-orange-400">
                  {flows.length > 0 ? (flows.reduce((sum, f) => sum + f.flow_strength, 0) / flows.length).toFixed(1) : 0}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Avg Duration:</span>
                <span className="text-white">
                  {flows.length > 0 ? (flows.reduce((sum, f) => sum + f.duration_minutes, 0) / flows.length).toFixed(0) : 0}min
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Momentum:</span>
                <span className="text-cyan-400">
                  {flows.length > 0 ? (flows.reduce((sum, f) => sum + f.momentum_score, 0) / flows.length).toFixed(1) : 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Money Alert */}
        {Math.abs(netFlow) > 50 && (
          <div className="mt-4 p-3 bg-orange-900/30 border border-orange-500/30 rounded-lg">
            <div className="flex items-center space-x-2">
              <span className="text-orange-400">🚨</span>
              <div>
                <div className="text-orange-300 text-sm font-semibold">
                  Strong Institutional {netFlow > 0 ? 'Buying' : 'Selling'} Detected
                </div>
                <div className="text-orange-400 text-xs">
                  Smart money is moving significantly in {symbol}. Consider following the trend.
                </div>
              </div>
            </div>
        </div>
      )}
      </div>
    </GlassCard>
  )
} 