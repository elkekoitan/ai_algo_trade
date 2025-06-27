'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, TrendingDown, Activity, DollarSign, 
  BarChart3, PieChart, Target, Shield, Calendar,
  ChevronRight, AlertTriangle, Award
} from 'lucide-react'
import { Line, Bar, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface BacktestResult {
  totalTrades: number
  winningTrades: number
  losingTrades: number
  winRate: number
  netProfit: number
  grossProfit: number
  grossLoss: number
  profitFactor: number
  maxDrawdown: number
  maxDrawdownPercent: number
  sharpeRatio: number
  averageWin: number
  averageLoss: number
  largestWin: number
  largestLoss: number
  equityCurve: number[]
  monthlyReturns: { [key: string]: number }
  executionTime: number
}

interface BacktestResultsProps {
  result: BacktestResult
  strategyName?: string
  onDeploy?: () => void
  onOptimize?: () => void
}

export default function BacktestResults({
  result,
  strategyName = 'Strategy',
  onDeploy,
  onOptimize
}: BacktestResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'risk' | 'monthly'>('overview')

  const getScoreColor = (score: number, reverse = false) => {
    if (reverse) {
      if (score <= 20) return 'text-green-400'
      if (score <= 40) return 'text-yellow-400'
      return 'text-red-400'
    }
    if (score >= 70) return 'text-green-400'
    if (score >= 50) return 'text-yellow-400'
    return 'text-red-400'
  }

  const equityChartData = {
    labels: result.equityCurve.map((_, i) => i),
    datasets: [{
      label: 'Equity Curve',
      data: result.equityCurve,
      borderColor: 'rgb(34, 211, 238)',
      backgroundColor: 'rgba(34, 211, 238, 0.1)',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.4,
      fill: true
    }]
  }

  const tradeDistributionData = {
    labels: ['Winning Trades', 'Losing Trades'],
    datasets: [{
      data: [result.winningTrades, result.losingTrades],
      backgroundColor: [
        'rgba(34, 211, 238, 0.8)',
        'rgba(239, 68, 68, 0.8)'
      ],
      borderColor: [
        'rgb(34, 211, 238)',
        'rgb(239, 68, 68)'
      ],
      borderWidth: 1
    }]
  }

  const monthlyReturnsData = {
    labels: Object.keys(result.monthlyReturns),
    datasets: [{
      label: 'Monthly Returns',
      data: Object.values(result.monthlyReturns),
      backgroundColor: Object.values(result.monthlyReturns).map(v => 
        v >= 0 ? 'rgba(34, 211, 238, 0.8)' : 'rgba(239, 68, 68, 0.8)'
      ),
      borderColor: Object.values(result.monthlyReturns).map(v => 
        v >= 0 ? 'rgb(34, 211, 238)' : 'rgb(239, 68, 68)'
      ),
      borderWidth: 1
    }]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(34, 211, 238, 0.5)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.5)'
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.5)'
        }
      }
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'trades', label: 'Trades', icon: Activity },
    { id: 'risk', label: 'Risk', icon: Shield },
    { id: 'monthly', label: 'Monthly', icon: Calendar }
  ]

  return (
    <motion.div
      className="bg-gradient-to-b from-gray-900/90 to-black/90 rounded-2xl 
                border border-cyan-500/20 backdrop-blur-xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 
                    border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              Backtest Results
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              {strategyName} • {result.totalTrades} trades • 
              Execution time: {result.executionTime.toFixed(2)}s
            </p>
          </div>

          {/* Quick stats */}
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-xs text-gray-400">Net Profit</p>
              <p className={`text-lg font-bold ${result.netProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${result.netProfit.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">Win Rate</p>
              <p className={`text-lg font-bold ${getScoreColor(result.winRate)}`}>
                {result.winRate.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mt-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium 
                       transition-all ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Performance metrics grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div
                className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <span className="text-xs text-gray-400">Profit Factor</span>
                </div>
                <p className="text-2xl font-bold text-green-400">
                  {result.profitFactor.toFixed(2)}
                </p>
              </motion.div>

              <motion.div
                className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Target className="w-5 h-5 text-cyan-400" />
                  <span className="text-xs text-gray-400">Sharpe Ratio</span>
                </div>
                <p className="text-2xl font-bold text-cyan-400">
                  {result.sharpeRatio.toFixed(2)}
                </p>
              </motion.div>

              <motion.div
                className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <TrendingDown className="w-5 h-5 text-red-400" />
                  <span className="text-xs text-gray-400">Max Drawdown</span>
                </div>
                <p className="text-2xl font-bold text-red-400">
                  -{result.maxDrawdownPercent.toFixed(1)}%
                </p>
              </motion.div>

              <motion.div
                className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <DollarSign className="w-5 h-5 text-green-400" />
                  <span className="text-xs text-gray-400">Avg Win/Loss</span>
                </div>
                <p className="text-2xl font-bold text-white">
                  {(result.averageWin / Math.abs(result.averageLoss)).toFixed(2)}
                </p>
              </motion.div>
            </div>

            {/* Equity curve */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
              <h4 className="text-lg font-semibold text-white mb-4">Equity Curve</h4>
              <div className="h-64">
                <Line data={equityChartData} options={chartOptions} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trades' && (
          <div className="space-y-6">
            {/* Trade distribution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <h4 className="text-lg font-semibold text-white mb-4">Trade Distribution</h4>
                <div className="h-64">
                  <Pie data={tradeDistributionData} options={{
                    ...chartOptions,
                    plugins: {
                      ...chartOptions.plugins,
                      legend: {
                        display: true,
                        position: 'bottom' as const,
                        labels: {
                          color: 'rgba(255, 255, 255, 0.7)'
                        }
                      }
                    }
                  }} />
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <h4 className="text-lg font-semibold text-white mb-4">Trade Statistics</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Trades</span>
                    <span className="text-white font-semibold">{result.totalTrades}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Winning Trades</span>
                    <span className="text-green-400 font-semibold">{result.winningTrades}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Losing Trades</span>
                    <span className="text-red-400 font-semibold">{result.losingTrades}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Largest Win</span>
                    <span className="text-green-400 font-semibold">${result.largestWin.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Largest Loss</span>
                    <span className="text-red-400 font-semibold">-${Math.abs(result.largestLoss).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="space-y-6">
            {/* Risk metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 
                            rounded-lg p-4 border border-red-500/30">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  <h5 className="font-semibold text-white">Risk Level</h5>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400 text-sm">Max Drawdown</span>
                    <span className={`font-semibold ${getScoreColor(result.maxDrawdownPercent, true)}`}>
                      {result.maxDrawdownPercent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full"
                      style={{ width: `${Math.min(result.maxDrawdownPercent, 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-yellow-900/20 to-amber-900/20 
                            rounded-lg p-4 border border-yellow-500/30">
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-5 h-5 text-yellow-400" />
                  <h5 className="font-semibold text-white">Risk/Reward</h5>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-yellow-400">
                    1:{(result.averageWin / Math.abs(result.averageLoss)).toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">Avg Risk/Reward Ratio</p>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 
                            rounded-lg p-4 border border-green-500/30">
                <div className="flex items-center gap-2 mb-3">
                  <Award className="w-5 h-5 text-green-400" />
                  <h5 className="font-semibold text-white">Performance</h5>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-400">
                    {result.sharpeRatio.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">Sharpe Ratio</p>
                </div>
              </div>
            </div>

            {/* Risk warnings */}
            {result.maxDrawdownPercent > 20 && (
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-semibold text-red-400 mb-1">High Risk Warning</h5>
                    <p className="text-sm text-gray-300">
                      This strategy has a maximum drawdown of {result.maxDrawdownPercent.toFixed(1)}%, 
                      which is considered high risk. Consider adjusting position sizing or adding 
                      additional risk management rules.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'monthly' && (
          <div className="space-y-6">
            {/* Monthly returns chart */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
              <h4 className="text-lg font-semibold text-white mb-4">Monthly Returns</h4>
              <div className="h-64">
                <Bar data={monthlyReturnsData} options={chartOptions} />
              </div>
            </div>

            {/* Monthly statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <p className="text-xs text-gray-400 mb-1">Best Month</p>
                <p className="text-lg font-bold text-green-400">
                  ${Math.max(...Object.values(result.monthlyReturns)).toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <p className="text-xs text-gray-400 mb-1">Worst Month</p>
                <p className="text-lg font-bold text-red-400">
                  ${Math.min(...Object.values(result.monthlyReturns)).toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <p className="text-xs text-gray-400 mb-1">Positive Months</p>
                <p className="text-lg font-bold text-cyan-400">
                  {Object.values(result.monthlyReturns).filter(v => v > 0).length}
                </p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <p className="text-xs text-gray-400 mb-1">Negative Months</p>
                <p className="text-lg font-bold text-gray-400">
                  {Object.values(result.monthlyReturns).filter(v => v < 0).length}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/20 to-purple-900/20 
                    border-t border-cyan-500/20">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-400">
            Ready to deploy this strategy?
          </p>
          <div className="flex items-center gap-3">
            {onOptimize && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onOptimize}
                className="px-4 py-2 bg-gray-800/50 text-gray-300 rounded-lg
                         hover:bg-gray-700/50 transition-all flex items-center gap-2"
              >
                <Shield className="w-4 h-4" />
                Optimize
              </motion.button>
            )}
            {onDeploy && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onDeploy}
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-500 
                         text-white rounded-lg hover:shadow-lg transition-all
                         flex items-center gap-2"
              >
                Deploy Strategy
                <ChevronRight className="w-4 h-4" />
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
} 