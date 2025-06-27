'use client'
import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Clock, Hash, Layers, BarChart } from 'lucide-react'
import AdaptiveControls from './AdaptiveControls'

// Mock types for props - these would be imported from a types file
interface ManagedPosition {
  ticket: number
  symbol: string
  position_type: 'buy' | 'sell'
  volume: number
  open_price: number
  current_price: number
  pnl: number
  pips: number
  open_time: string
}

interface RiskMetrics {
  position_ticket: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
}

interface AdaptiveAlert {
    position_ticket: number;
    title: string;
    recommended_action: {
        action_type: string;
        description: string;
        parameters: any;
    };
}


interface TradeMonitorProps {
  positions: ManagedPosition[]
  risks: RiskMetrics[]
  alerts: AdaptiveAlert[]
}

const getRiskStyles = (level: string) => {
  switch (level) {
    case 'low':
      return 'border-green-500/50 bg-green-500/10 text-green-400'
    case 'medium':
      return 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400'
    case 'high':
      return 'border-orange-500/50 bg-orange-500/10 text-orange-400'
    case 'critical':
      return 'border-red-500/50 bg-red-500/10 text-red-400 animate-pulse'
    default:
      return 'border-gray-600 bg-gray-800/50 text-gray-400'
  }
}

const PositionCard = ({ position, risk, alert }: { position: ManagedPosition, risk?: RiskMetrics, alert?: AdaptiveAlert }) => {
  const isBuy = position.position_type === 'buy'
  const pnlColor = position.pnl >= 0 ? 'text-green-400' : 'text-red-400'
  const riskStyles = getRiskStyles(risk?.risk_level || 'low')

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`relative rounded-2xl p-5 border overflow-hidden bg-gray-900/50
                  border-gray-700/50 backdrop-blur-lg
                  hover:border-cyan-500/50 transition-all duration-300`}
    >
        <div className={`absolute top-0 left-0 right-0 h-1 ${riskStyles.replace('text-green-400', 'bg-green-500').replace('text-yellow-400', 'bg-yellow-500').replace('text-orange-400', 'bg-orange-500').replace('text-red-400', 'bg-red-500')}`}></div>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          {isBuy ? (
            <div className="w-10 h-10 flex items-center justify-center rounded-full bg-green-500/10">
              <TrendingUp className="w-5 h-5 text-green-400" />
            </div>
          ) : (
            <div className="w-10 h-10 flex items-center justify-center rounded-full bg-red-500/10">
              <TrendingDown className="w-5 h-5 text-red-400" />
            </div>
          )}
          <div>
            <h3 className="text-xl font-bold text-white">{position.symbol}</h3>
            <p className="text-sm text-gray-400">
              {isBuy ? 'LONG' : 'SHORT'} @ {position.open_price}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2 ${riskStyles}`}>
          <BarChart className="w-4 h-4" />
          <span>Risk: {risk?.risk_level.toUpperCase() || 'N/A'}</span>
        </div>
      </div>

      {/* PnL Display */}
      <div className="text-center my-4">
        <p className={`text-4xl font-bold ${pnlColor}`}>
          {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
        </p>
        <p className={`text-lg ${pnlColor}`}>
          {position.pips >= 0 ? '+' : ''}{position.pips.toFixed(1)} pips
        </p>
      </div>

      {/* Details */}
      <div className="grid grid-cols-3 gap-4 text-center text-sm mb-4">
        <div>
          <p className="text-gray-400 flex items-center justify-center gap-1"><Layers className="w-3 h-3"/>Volume</p>
          <p className="font-semibold text-white">{position.volume}</p>
        </div>
        <div>
          <p className="text-gray-400 flex items-center justify-center gap-1"><Hash className="w-3 h-3"/>Ticket</p>
          <p className="font-semibold text-white">{position.ticket}</p>
        </div>
        <div>
          <p className="text-gray-400 flex items-center justify-center gap-1"><Clock className="w-3 h-3"/>Opened</p>
          <p className="font-semibold text-white">{new Date(position.open_time).toLocaleTimeString()}</p>
        </div>
      </div>

      {/* AI Controls */}
      <AdaptiveControls alert={alert} riskScore={risk?.risk_score} ticket={position.ticket}/>

    </motion.div>
  )
}


export default function TradeMonitor({ positions, risks, alerts }: TradeMonitorProps) {
  if (positions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-gray-900/50 rounded-2xl border border-dashed border-gray-700">
        <Layers className="w-12 h-12 text-gray-600 mb-4" />
        <h3 className="text-xl font-semibold text-gray-400">No Open Positions</h3>
        <p className="text-gray-500">Your open trades will appear here for management.</p>
      </div>
    )
  }
  return (
    <div className="space-y-4">
        <h2 className="text-2xl font-bold text-white mb-4">Live Positions ({positions.length})</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {positions.map((pos) => {
                const risk = risks.find(r => r.position_ticket === pos.ticket)
                const alert = alerts.find(a => a.position_ticket === pos.ticket)
                return <PositionCard key={pos.ticket} position={pos} risk={risk} alert={alert} />
            })}
        </div>
    </div>
  )
} 