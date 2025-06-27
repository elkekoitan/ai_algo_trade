'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import GlassCard from './GlassCard'

interface Influencer {
  id: string
  name: string
  avatar: string
  score: number
  followers: number
  trades: number
  winRate: number
  roi: number
  trend: 'up' | 'down' | 'stable'
}

interface InfluenceAnalyticsProps {
  className?: string
}

export default function InfluenceAnalytics({ className = '' }: InfluenceAnalyticsProps) {
  const [selectedInfluencer, setSelectedInfluencer] = useState<Influencer | null>(null)
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('7d')
  
  // Mock data - in production this would come from API
  const influencers: Influencer[] = [
    {
      id: '1',
      name: 'QuantumTrader',
      avatar: '🚀',
      score: 95,
      followers: 12500,
      trades: 342,
      winRate: 78.5,
      roi: 145.2,
      trend: 'up'
    },
    {
      id: '2',
      name: 'AIWhale',
      avatar: '🐋',
      score: 92,
      followers: 8900,
      trades: 256,
      winRate: 72.3,
      roi: 98.7,
      trend: 'up'
    },
    {
      id: '3',
      name: 'NeuralNinja',
      avatar: '🥷',
      score: 88,
      followers: 6200,
      trades: 189,
      winRate: 69.8,
      roi: 67.4,
      trend: 'stable'
    },
    {
      id: '4',
      name: 'CryptoSage',
      avatar: '🧙',
      score: 85,
      followers: 4500,
      trades: 134,
      winRate: 65.2,
      roi: 45.8,
      trend: 'down'
    }
  ]
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  }
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Influence Analytics</h2>
          <p className="text-gray-400 mt-1">Track top traders and their market impact</p>
        </div>
        
        {/* Timeframe selector */}
        <div className="flex gap-2">
          {(['24h', '7d', '30d'] as const).map((tf) => (
            <motion.button
              key={tf}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                timeframe === tf
                  ? 'bg-quantum-primary text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {tf}
            </motion.button>
          ))}
        </div>
      </div>
      
      {/* Main Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Influencer Rankings */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <GlassCard variant="default" className="h-full">
            <h3 className="text-lg font-semibold text-white mb-4">Top Influencers</h3>
            
            <div className="space-y-3">
              {influencers.map((influencer, index) => (
                <motion.div
                  key={influencer.id}
                  whileHover={{ x: 5 }}
                  onClick={() => setSelectedInfluencer(influencer)}
                  className={`p-4 rounded-xl cursor-pointer transition-all ${
                    selectedInfluencer?.id === influencer.id
                      ? 'bg-quantum-primary/20 border border-quantum-primary/50'
                      : 'bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Rank */}
                      <div className="text-2xl font-bold text-quantum-primary">
                        #{index + 1}
                      </div>
                      
                      {/* Avatar and Name */}
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">{influencer.avatar}</div>
                        <div>
                          <h4 className="font-semibold text-white">{influencer.name}</h4>
                          <div className="flex items-center gap-4 mt-1">
                            <span className="text-xs text-gray-400">
                              {influencer.followers.toLocaleString()} followers
                            </span>
                            <span className="text-xs text-gray-400">
                              {influencer.trades} trades
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Metrics */}
                    <div className="flex items-center gap-6">
                      {/* Influence Score */}
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">{influencer.score}</div>
                        <div className="text-xs text-gray-400">Score</div>
                      </div>
                      
                      {/* Win Rate */}
                      <div className="text-center">
                        <div className="text-lg font-semibold text-green-400">
                          {influencer.winRate}%
                        </div>
                        <div className="text-xs text-gray-400">Win Rate</div>
                      </div>
                      
                      {/* ROI */}
                      <div className="text-center">
                        <div className={`text-lg font-semibold flex items-center gap-1 ${
                          influencer.roi > 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {influencer.roi > 0 ? '↑' : '↓'} {Math.abs(influencer.roi)}%
                        </div>
                        <div className="text-xs text-gray-400">ROI</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
        
        {/* Influence Metrics */}
        <motion.div variants={itemVariants}>
          <GlassCard variant="neon" glow className="h-full">
            <h3 className="text-lg font-semibold text-white mb-4">Network Impact</h3>
            
            {selectedInfluencer ? (
              <div className="space-y-4">
                {/* Selected Influencer Details */}
                <div className="text-center py-4">
                  <div className="text-4xl mb-2">{selectedInfluencer.avatar}</div>
                  <h4 className="text-xl font-bold text-white">{selectedInfluencer.name}</h4>
                  <div className="flex items-center justify-center gap-2 mt-2">
                    <div className={`w-2 h-2 rounded-full ${
                      selectedInfluencer.trend === 'up' ? 'bg-green-400' :
                      selectedInfluencer.trend === 'down' ? 'bg-red-400' : 'bg-yellow-400'
                    }`}></div>
                    <span className="text-sm text-gray-400">
                      {selectedInfluencer.trend === 'up' ? 'Trending Up' :
                       selectedInfluencer.trend === 'down' ? 'Trending Down' : 'Stable'}
                    </span>
                  </div>
                </div>
                
                {/* Circular Progress Indicators */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Influence Score */}
                  <div className="relative">
                    <svg className="w-24 h-24 mx-auto transform -rotate-90">
                      <circle
                        cx="48"
                        cy="48"
                        r="36"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="8"
                        fill="none"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="36"
                        stroke="url(#gradient1)"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${(selectedInfluencer.score / 100) * 226} 226`}
                        strokeLinecap="round"
                      />
                      <defs>
                        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#00ff88" />
                          <stop offset="100%" stopColor="#7209b7" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">{selectedInfluencer.score}</div>
                        <div className="text-xs text-gray-400">Score</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Win Rate */}
                  <div className="relative">
                    <svg className="w-24 h-24 mx-auto transform -rotate-90">
                      <circle
                        cx="48"
                        cy="48"
                        r="36"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="8"
                        fill="none"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="36"
                        stroke="url(#gradient2)"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${(selectedInfluencer.winRate / 100) * 226} 226`}
                        strokeLinecap="round"
                      />
                      <defs>
                        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#e94560" />
                          <stop offset="100%" stopColor="#00ff88" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">{selectedInfluencer.winRate}%</div>
                        <div className="text-xs text-gray-400">Win Rate</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="space-y-2 mt-6">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 bg-quantum-primary text-black font-semibold rounded-lg hover:bg-quantum-primary/90 transition-colors"
                  >
                    Follow Trader
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 bg-white/10 text-white font-semibold rounded-lg hover:bg-white/20 transition-colors"
                  >
                    View Strategy
                  </motion.button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-400 text-center">
                  Select an influencer to view detailed metrics
                </p>
              </div>
            )}
          </GlassCard>
        </motion.div>
      </motion.div>
      
      {/* Bottom Stats */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Total Influencers', value: '1,234', change: '+12%', color: 'text-quantum-primary' },
          { label: 'Active Traders', value: '892', change: '+8%', color: 'text-green-400' },
          { label: 'Total Volume', value: '$45.2M', change: '+23%', color: 'text-blue-400' },
          { label: 'Avg Win Rate', value: '68.5%', change: '+2.3%', color: 'text-purple-400' }
        ].map((stat, index) => (
          <motion.div key={index} variants={itemVariants}>
            <GlassCard variant="default" className="text-center">
              <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              <p className="text-sm text-green-400 mt-1">{stat.change}</p>
            </GlassCard>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
} 