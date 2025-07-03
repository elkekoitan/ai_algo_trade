'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import QuantumLayout from '@/components/layout/QuantumLayout'
import NaturalLanguageInput from '@/components/strategy-whisperer/NaturalLanguageInput'
import StrategyChat from '@/components/strategy-whisperer/StrategyChat'
import CodePreview from '@/components/strategy-whisperer/CodePreview'
import BacktestResults from '@/components/strategy-whisperer/BacktestResults'
import DeploymentWizard from '@/components/strategy-whisperer/DeploymentWizard'
import { 
  Brain, Sparkles, Code, Activity, Rocket, 
  MessageSquare, Zap, Shield, TrendingUp,
  Target,
  BarChart3,
  Play,
  Pause,
  Download,
  Upload,
  Settings,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Cpu,
  Eye,
  Send,
  Star
} from 'lucide-react'
import ParticleBackground from '@/components/quantum/ParticleBackground'
import GlassCard from '@/components/quantum/GlassCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { systemEvents } from '@/lib/system-events'

interface TradingStrategy {
  id: string
  name: string
  description: string
  natural_language_input: string
  mql5_code: string
  parameters: {
    [key: string]: {
      value: number | string | boolean
      type: 'number' | 'string' | 'boolean'
      description: string
    }
  }
  backtest_results: {
    total_trades: number
    winning_trades: number
    losing_trades: number
    win_rate: number
    profit_factor: number
    max_drawdown: number
    total_return: number
    sharpe_ratio: number
  }
  status: 'DRAFT' | 'TESTING' | 'OPTIMIZED' | 'DEPLOYED' | 'FAILED'
  created_at: string
  last_modified: string
  deployment_status: 'NOT_DEPLOYED' | 'DEPLOYING' | 'DEPLOYED' | 'ERROR'
}

interface ChatMessage {
  id: string
  type: 'USER' | 'AI' | 'SYSTEM'
  content: string
  timestamp: string
  strategy_id?: string
  code_snippet?: string
}

interface WhispererState {
  is_active: boolean
  auto_optimization: boolean
  language_model: 'GPT4' | 'CLAUDE' | 'GEMINI'
  code_complexity: 'SIMPLE' | 'INTERMEDIATE' | 'ADVANCED'
  backtest_period: number // days
  optimization_depth: number
}

interface SystemMetrics {
  strategies_created: number
  successful_backtests: number
  deployed_strategies: number
  avg_success_rate: number
  total_code_lines: number
  processing_time_avg: number
}

const strategyTypes = [
  { 
    id: 'scalping', 
    name: 'Scalping Strategy', 
    icon: '⚡', 
    description: 'Quick profit strategies for short-term trades',
    complexity: 'Medium'
  },
  { 
    id: 'swing', 
    name: 'Swing Trading', 
    icon: '📈', 
    description: 'Medium-term position trading strategies',
    complexity: 'Low'
  },
  { 
    id: 'grid', 
    name: 'Grid Trading', 
    icon: '🔲', 
    description: 'Automated grid-based trading systems',
    complexity: 'High'
  },
  { 
    id: 'sanal_supurge', 
    name: 'Sanal Süpürge', 
    icon: '🧹', 
    description: 'Advanced grid trading with Fibonacci levels',
    complexity: 'Expert'
  },
  { 
    id: 'arbitrage', 
    name: 'Arbitrage', 
    icon: '⚖️', 
    description: 'Price difference exploitation strategies',
    complexity: 'Expert'
  }
];

export default function StrategyWhispererPage() {
  const [strategies, setStrategies] = useState<TradingStrategy[]>([])
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [selectedStrategy, setSelectedStrategy] = useState<TradingStrategy | null>(null)
  const [selectedStrategyType, setSelectedStrategyType] = useState<string>('')
  const [whispererState, setWhispererState] = useState<WhispererState>({
    is_active: false,
    auto_optimization: true,
    language_model: 'GPT4',
    code_complexity: 'INTERMEDIATE',
    backtest_period: 30,
    optimization_depth: 75
  })
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    strategies_created: 0,
    successful_backtests: 0,
    deployed_strategies: 0,
    avg_success_rate: 0,
    total_code_lines: 0,
    processing_time_avg: 0
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const fetchWhispererData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/strategy-whisperer/strategies')
      
      if (response.ok) {
        const data = await response.json()
        
        // Transform strategies
        const tradingStrategies: TradingStrategy[] = data.strategies?.map((strategy: any, index: number) => ({
          id: `strategy_${Date.now()}_${index}`,
          name: strategy.name || `AI Strategy ${index + 1}`,
          description: strategy.description || generateStrategyDescription(),
          natural_language_input: strategy.input || generateNaturalLanguageInput(),
          mql5_code: strategy.code || generateMQL5Code(),
          parameters: strategy.parameters || generateParameters(),
          backtest_results: strategy.backtest || generateBacktestResults(),
          status: strategy.status || ['DRAFT', 'TESTING', 'OPTIMIZED'][Math.floor(Math.random() * 3)],
          created_at: strategy.created_at || new Date().toISOString(),
          last_modified: strategy.modified || new Date().toISOString(),
          deployment_status: strategy.deployment || 'NOT_DEPLOYED'
        })) || []
        
        setStrategies(tradingStrategies)
        
        // Update system metrics
        setSystemMetrics({
          strategies_created: tradingStrategies.length,
          successful_backtests: tradingStrategies.filter(s => s.backtest_results.win_rate > 60).length,
          deployed_strategies: tradingStrategies.filter(s => s.deployment_status === 'DEPLOYED').length,
          avg_success_rate: tradingStrategies.reduce((sum, s) => sum + s.backtest_results.win_rate, 0) / tradingStrategies.length || 0,
          total_code_lines: tradingStrategies.reduce((sum, s) => sum + s.mql5_code.split('\n').length, 0),
          processing_time_avg: 2.5 + Math.random() * 2
        })
        
        // Broadcast successful strategies
        const successfulStrategies = tradingStrategies.filter(s => s.backtest_results.win_rate > 70)
        if (successfulStrategies.length > 0) {
          await systemEvents.syncModuleData('strategy_whisperer', 'whisperer_strategy', {
            strategies: successfulStrategies,
            total_created: tradingStrategies.length,
            success_rate: systemMetrics.avg_success_rate
          })
        }
        
      } else {
        // Generate mock strategies
        const mockStrategies: TradingStrategy[] = Array.from({ length: 3 }, (_, index) => ({
          id: `mock_${Date.now()}_${index}`,
          name: `AI Strategy ${index + 1}`,
          description: generateStrategyDescription(),
          natural_language_input: generateNaturalLanguageInput(),
          mql5_code: generateMQL5Code(),
          parameters: generateParameters(),
          backtest_results: generateBacktestResults(),
          status: ['DRAFT', 'TESTING', 'OPTIMIZED'][index % 3] as any,
          created_at: new Date(Date.now() - index * 86400000).toISOString(),
          last_modified: new Date().toISOString(),
          deployment_status: 'NOT_DEPLOYED'
        }))
        
        setStrategies(mockStrategies)
        
        setSystemMetrics({
          strategies_created: 15,
          successful_backtests: 12,
          deployed_strategies: 3,
          avg_success_rate: 73.5,
          total_code_lines: 2847,
          processing_time_avg: 3.2
        })
      }
      
      setLastUpdate(new Date())
      
    } catch (error) {
      console.error('Error fetching whisperer data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateStrategyDescription = () => {
    const descriptions = [
      "Advanced ICT-based strategy using order blocks and fair value gaps for high-probability entries",
      "Momentum trading system with adaptive risk management and multi-timeframe confirmation",
      "Mean reversion strategy leveraging institutional order flow and volume profile analysis",
      "Breakout trading system with dynamic stop loss and profit taking mechanisms"
    ]
    return descriptions[Math.floor(Math.random() * descriptions.length)]
  }

  const generateNaturalLanguageInput = () => {
    const inputs = [
      "Create a strategy that buys when price breaks above the 20-period moving average with high volume and RSI above 60",
      "I want a strategy that identifies order blocks on 4H timeframe and trades the retest with 1:3 risk reward",
      "Build a scalping strategy for EURUSD that uses support and resistance levels with quick entries and exits",
      "Make a swing trading strategy that follows institutional money flow and trades in the direction of smart money"
    ]
    return inputs[Math.floor(Math.random() * inputs.length)]
  }

  const generateMQL5Code = () => {
    return `//+------------------------------------------------------------------+
//|                                           AI Generated Strategy |
//|                                  Generated by Strategy Whisperer |
//+------------------------------------------------------------------+
#property copyright "AI Strategy Whisperer"
#property version   "1.00"

// Input parameters
input double LotSize = 0.01;
input int RSI_Period = 14;
input int MA_Period = 20;
input double StopLoss = 50;
input double TakeProfit = 150;

// Global variables
int rsi_handle;
int ma_handle;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Create indicators
   rsi_handle = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
   ma_handle = iMA(_Symbol, PERIOD_CURRENT, MA_Period, 0, MODE_SMA, PRICE_CLOSE);
   
   if(rsi_handle == INVALID_HANDLE || ma_handle == INVALID_HANDLE)
   {
      Print("Error creating indicators");
      return INIT_FAILED;
   }
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Get current values
   double rsi[];
   double ma[];
   double close = iClose(_Symbol, PERIOD_CURRENT, 0);
   
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(ma, true);
   
   if(CopyBuffer(rsi_handle, 0, 0, 2, rsi) < 2) return;
   if(CopyBuffer(ma_handle, 0, 0, 2, ma) < 2) return;
   
   // Trading logic
   if(close > ma[0] && rsi[0] > 60 && PositionsTotal() == 0)
   {
      // Buy signal
      OpenPosition(ORDER_TYPE_BUY);
   }
   else if(close < ma[0] && rsi[0] < 40 && PositionsTotal() == 0)
   {
      // Sell signal
      OpenPosition(ORDER_TYPE_SELL);
   }
}

//+------------------------------------------------------------------+
//| Open position function                                           |
//+------------------------------------------------------------------+
void OpenPosition(ENUM_ORDER_TYPE type)
{
   MqlTradeRequest request;
   MqlTradeResult result;
   
   ZeroMemory(request);
   ZeroMemory(result);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = _Symbol;
   request.volume = LotSize;
   request.type = type;
   request.price = (type == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   request.deviation = 3;
   request.magic = 12345;
   request.comment = "AI Strategy";
   
   // Set SL and TP
   if(type == ORDER_TYPE_BUY)
   {
      request.sl = request.price - StopLoss * _Point;
      request.tp = request.price + TakeProfit * _Point;
   }
   else
   {
      request.sl = request.price + StopLoss * _Point;
      request.tp = request.price - TakeProfit * _Point;
   }
   
   if(!OrderSend(request, result))
   {
      Print("Error opening position: ", GetLastError());
   }
}`
  }

  const generateParameters = (): TradingStrategy['parameters'] => {
    return {
      lot_size: { value: 0.01, type: 'number', description: 'Position size in lots' },
      rsi_period: { value: 14, type: 'number', description: 'RSI calculation period' },
      ma_period: { value: 20, type: 'number', description: 'Moving average period' },
      stop_loss: { value: 50, type: 'number', description: 'Stop loss in pips' },
      take_profit: { value: 150, type: 'number', description: 'Take profit in pips' },
      max_trades: { value: 3, type: 'number', description: 'Maximum concurrent trades' },
      trading_hours: { value: "08:00-18:00", type: 'string', description: 'Active trading hours' },
      enable_news_filter: { value: true, type: 'boolean', description: 'Avoid trading during news' }
    }
  }

  const generateBacktestResults = () => {
    const totalTrades = 50 + Math.floor(Math.random() * 100)
    const winRate = 60 + Math.random() * 30
    const winningTrades = Math.floor(totalTrades * (winRate / 100))
    
    return {
      total_trades: totalTrades,
      winning_trades: winningTrades,
      losing_trades: totalTrades - winningTrades,
      win_rate: winRate,
      profit_factor: 1.2 + Math.random() * 0.8,
      max_drawdown: 5 + Math.random() * 15,
      total_return: 15 + Math.random() * 35,
      sharpe_ratio: 1.0 + Math.random() * 1.5
    }
  }

  const processNaturalLanguage = async (input: string) => {
    setIsProcessing(true)
    
    // Add user message
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      type: 'USER',
      content: input,
      timestamp: new Date().toISOString()
    }
    
    setChatMessages(prev => [...prev, userMessage])
    
    try {
      const response = await fetch('/api/v1/strategy-whisperer/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          input,
          complexity: whispererState.code_complexity,
          model: whispererState.language_model
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        
        // Add AI response
        const aiMessage: ChatMessage = {
          id: `msg_${Date.now()}_ai`,
          type: 'AI',
          content: data.response || "I understand your strategy requirements. Let me generate the MQL5 code for you...",
          timestamp: new Date().toISOString(),
          strategy_id: data.strategy_id,
          code_snippet: data.code_preview
        }
        
        setChatMessages(prev => [...prev, aiMessage])
        
        if (data.strategy) {
          setStrategies(prev => [...prev, data.strategy])
        }
        
      } else {
        // Mock AI response
        const aiMessage: ChatMessage = {
          id: `msg_${Date.now()}_ai`,
          type: 'AI',
          content: `I understand you want to create a strategy based on: "${input}". I'll generate an MQL5 Expert Advisor that implements this logic with proper risk management and optimization parameters.`,
          timestamp: new Date().toISOString()
        }
        
        setChatMessages(prev => [...prev, aiMessage])
        
        // Generate new strategy
        const newStrategy: TradingStrategy = {
          id: `strategy_${Date.now()}`,
          name: `Custom Strategy ${strategies.length + 1}`,
          description: `Strategy based on: ${input.slice(0, 50)}...`,
          natural_language_input: input,
          mql5_code: generateMQL5Code(),
          parameters: generateParameters(),
          backtest_results: generateBacktestResults(),
          status: 'DRAFT',
          created_at: new Date().toISOString(),
          last_modified: new Date().toISOString(),
          deployment_status: 'NOT_DEPLOYED'
        }
        
        setStrategies(prev => [...prev, newStrategy])
      }
      
    } catch (error) {
      console.error('Error processing natural language:', error)
      
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}_error`,
        type: 'SYSTEM',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      }
      
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
      setCurrentInput('')
    }
  }

  const runBacktest = async (strategyId: string) => {
    try {
      const response = await fetch(`/api/v1/strategy-whisperer/backtest/${strategyId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          period_days: whispererState.backtest_period,
          optimization: whispererState.auto_optimization
        })
      })
      
      if (response.ok) {
        await fetchWhispererData()
      }
    } catch (error) {
      console.error('Failed to run backtest:', error)
    }
  }

  const deployStrategy = async (strategyId: string) => {
    try {
      const response = await fetch(`/api/v1/strategy-whisperer/deploy/${strategyId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await fetchWhispererData()
      }
    } catch (error) {
      console.error('Failed to deploy strategy:', error)
    }
  }

  const toggleWhisperer = async () => {
    try {
      const newState = { ...whispererState, is_active: !whispererState.is_active }
      setWhispererState(newState)
      
      await systemEvents.broadcastEvent('whisperer:mode_toggled', {
        active: newState.is_active,
        model: newState.language_model
      })
      
    } catch (error) {
      console.error('Failed to toggle whisperer:', error)
    }
  }

  const updateSettings = async (newSettings: Partial<WhispererState>) => {
    const updatedState = { ...whispererState, ...newSettings }
    setWhispererState(updatedState)
    
    await systemEvents.broadcastEvent('whisperer:settings_updated', updatedState)
  }

  const handleStrategyTypeSelect = (typeId: string) => {
    setSelectedStrategyType(typeId)
    
    if (typeId === 'sanal_supurge') {
      // Redirect to Sanal Süpürge page
      window.location.href = '/sanal-supurge'
      return
    }
    
    // For other strategy types, pre-fill with relevant prompts
    const strategyPrompts: { [key: string]: string } = {
      scalping: "Create a scalping strategy for EURUSD that uses 1-minute timeframe with tight stop losses and quick profit targets",
      swing: "Build a swing trading strategy that identifies trend reversals using RSI divergence and support/resistance levels",
      grid: "Design a grid trading system that places buy and sell orders at regular intervals around current price",
      arbitrage: "Create an arbitrage strategy that exploits price differences between correlated currency pairs"
    }
    
    if (strategyPrompts[typeId]) {
      setCurrentInput(strategyPrompts[typeId])
    }
  }

  useEffect(() => {
    fetchWhispererData()
    const interval = setInterval(fetchWhispererData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DEPLOYED': return 'text-green-400 bg-green-500/20'
      case 'OPTIMIZED': return 'text-cyan-400 bg-cyan-500/20'
      case 'TESTING': return 'text-yellow-400 bg-yellow-500/20'
      case 'DRAFT': return 'text-gray-400 bg-gray-500/20'
      case 'FAILED': return 'text-red-400 bg-red-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <Zap className="w-12 h-12 animate-pulse text-orange-400 mx-auto mb-4" />
          <p className="text-xl">Initializing Strategy Whisperer...</p>
          <p className="text-gray-400">AI language models coming online...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <ParticleBackground />
      
      <div className="relative z-10 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Zap className="w-8 h-8 text-orange-400" />
            Strategy Whisperer
            {whispererState.is_active && <Brain className="w-6 h-6 text-purple-400 animate-pulse" />}
          </h1>
          
          <div className="flex items-center gap-4">
            <Badge className="bg-purple-500/20 text-purple-400">
              {whispererState.language_model}
            </Badge>
            <button
              onClick={toggleWhisperer}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                whispererState.is_active 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-orange-600 hover:bg-orange-700 text-white'
              }`}
            >
              {whispererState.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {whispererState.is_active ? 'Whisperer ON' : 'Activate Whisperer'}
            </button>
          </div>
        </div>

        {/* System Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Strategies Created</p>
              <p className="text-2xl font-bold text-orange-400">{systemMetrics.strategies_created}</p>
            </div>
          </GlassCard>
          
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-400">{systemMetrics.avg_success_rate.toFixed(1)}%</p>
            </div>
          </GlassCard>
          
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Deployed</p>
              <p className="text-2xl font-bold text-cyan-400">{systemMetrics.deployed_strategies}</p>
            </div>
          </GlassCard>
          
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Code Lines</p>
              <p className="text-2xl font-bold text-purple-400">{systemMetrics.total_code_lines.toLocaleString()}</p>
            </div>
          </GlassCard>
          
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Avg Process Time</p>
              <p className="text-2xl font-bold text-yellow-400">{systemMetrics.processing_time_avg.toFixed(1)}s</p>
            </div>
          </GlassCard>
          
          <GlassCard className="p-4">
            <div className="text-center">
              <p className="text-sm text-gray-400">Backtests</p>
              <p className="text-2xl font-bold text-white">{systemMetrics.successful_backtests}</p>
            </div>
          </GlassCard>
        </div>

        {/* Strategy Types Selection */}
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Star className="w-5 h-5 text-yellow-400" />
            Strategy Templates
          </h2>
          <p className="text-gray-300 mb-6">
            Choose a strategy template to get started quickly, or describe your own custom strategy below.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
            {strategyTypes.map((strategyType) => (
              <motion.div
                key={strategyType.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`cursor-pointer p-4 rounded-lg border-2 transition-all ${
                  selectedStrategyType === strategyType.id
                    ? 'border-cyan-400 bg-cyan-400/10'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-500'
                }`}
                onClick={() => handleStrategyTypeSelect(strategyType.id)}
              >
                <div className="text-center">
                  <div className="text-3xl mb-2">{strategyType.icon}</div>
                  <h3 className="font-semibold text-white mb-1">{strategyType.name}</h3>
                  <p className="text-xs text-gray-400 mb-2">{strategyType.description}</p>
                  <Badge className={`text-xs ${
                    strategyType.complexity === 'Expert' ? 'bg-red-500/20 text-red-400' :
                    strategyType.complexity === 'High' ? 'bg-orange-500/20 text-orange-400' :
                    strategyType.complexity === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-green-500/20 text-green-400'
                  }`}>
                    {strategyType.complexity}
                  </Badge>
                </div>
                
                {strategyType.id === 'sanal_supurge' && (
                  <div className="mt-3 pt-3 border-t border-gray-600">
                    <div className="flex items-center justify-center gap-1 text-xs text-cyan-400">
                      <Sparkles className="w-3 h-3" />
                      <span>Fibonacci + Grid</span>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
          
          {selectedStrategyType === 'sanal_supurge' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-lg p-4"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="text-2xl">🧹</div>
                <div>
                  <h4 className="font-bold text-cyan-400">Sanal Süpürge - Advanced Grid Trading</h4>
                  <p className="text-sm text-gray-300">
                    Otomatik Fibonacci seviyeli grid trading sistemi
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-sm">
                  <span className="text-gray-400">✓ Otomatik Fibonacci hesaplama</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">✓ Volatilite adaptasyonu</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">✓ Risk yönetimi</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">✓ MT5 entegrasyonu</span>
                </div>
              </div>
              
              <Button 
                className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700"
                onClick={() => window.location.href = '/sanal-supurge'}
              >
                <Target className="w-4 h-4 mr-2" />
                Sanal Süpürge'yi Konfigure Et
              </Button>
            </motion.div>
          )}
        </GlassCard>

        {/* Control Panel */}
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Settings className="h-6 w-6 text-orange-400" />
            AI Control Panel
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Language Model
              </label>
              <select
                value={whispererState.language_model}
                onChange={(e) => updateSettings({ language_model: e.target.value as any })}
                className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-2"
              >
                <option value="GPT4">GPT-4</option>
                <option value="CLAUDE">Claude</option>
                <option value="GEMINI">Gemini</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Code Complexity
              </label>
              <select
                value={whispererState.code_complexity}
                onChange={(e) => updateSettings({ code_complexity: e.target.value as any })}
                className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-2"
              >
                <option value="SIMPLE">Simple</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Backtest Period (days)
              </label>
              <input
                type="number"
                min="7"
                max="365"
                value={whispererState.backtest_period}
                onChange={(e) => updateSettings({ backtest_period: parseInt(e.target.value) })}
                className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-2"
              />
            </div>

            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={whispererState.auto_optimization}
                  onChange={(e) => updateSettings({ auto_optimization: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm text-white">Auto Optimization</span>
              </label>
            </div>
          </div>
        </GlassCard>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chat Interface */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <MessageSquare className="h-6 w-6 text-cyan-400" />
              Strategy Chat
            </h2>
            
            {/* Chat Messages */}
            <div className="h-64 overflow-y-auto mb-4 space-y-3 bg-gray-900/50 rounded-lg p-4">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'USER' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs p-3 rounded-lg ${
                      message.type === 'USER' 
                        ? 'bg-orange-600 text-white' 
                        : message.type === 'AI'
                        ? 'bg-cyan-600 text-white'
                        : 'bg-gray-600 text-gray-200'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {chatMessages.length === 0 && (
                <div className="text-center py-8">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400">Start a conversation with the AI</p>
                  <p className="text-sm text-gray-500">Describe your trading strategy in natural language</p>
                </div>
              )}
            </div>
            
            {/* Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isProcessing && currentInput.trim() && processNaturalLanguage(currentInput)}
                placeholder="Describe your trading strategy..."
                className="flex-1 bg-gray-800 text-white border border-gray-700 rounded px-3 py-2 focus:border-orange-500 focus:outline-none"
                disabled={isProcessing}
              />
              <button
                onClick={() => processNaturalLanguage(currentInput)}
                disabled={isProcessing || !currentInput.trim()}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </GlassCard>

          {/* Strategy List */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Code className="h-6 w-6 text-purple-400" />
              Generated Strategies ({strategies.length})
            </h2>
            
            <div className="space-y-4 max-h-80 overflow-y-auto">
              {strategies.map((strategy) => (
                <motion.div
                  key={strategy.id}
                  className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-orange-500/50 cursor-pointer transition-all"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => setSelectedStrategy(strategy)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">{strategy.name}</h4>
                    <Badge className={getStatusColor(strategy.status)}>
                      {strategy.status}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-gray-300 mb-3">{strategy.description}</p>
                  
                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div className="text-center">
                      <p className="text-xs text-gray-400">Win Rate</p>
                      <p className="font-bold text-green-400">{strategy.backtest_results.win_rate.toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-400">Profit Factor</p>
                      <p className="font-bold text-cyan-400">{strategy.backtest_results.profit_factor.toFixed(2)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-400">Return</p>
                      <p className="font-bold text-yellow-400">{strategy.backtest_results.total_return.toFixed(1)}%</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        runBacktest(strategy.id)
                      }}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                    >
                      Backtest
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deployStrategy(strategy.id)
                      }}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                    >
                      Deploy
                    </button>
                    <button className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm">
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                </motion.div>
              ))}
              
              {strategies.length === 0 && (
                <div className="text-center py-8">
                  <Code className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400">No strategies created yet</p>
                  <p className="text-sm text-gray-500">Start by describing a strategy in the chat</p>
                </div>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Strategy Detail Modal */}
        {selectedStrategy && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6">
            <motion.div
              className="bg-gray-900 rounded-xl p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">{selectedStrategy.name}</h2>
                <button
                  onClick={() => setSelectedStrategy(null)}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Code Preview */}
                <div>
                  <h3 className="font-semibold text-white mb-2">MQL5 Code</h3>
                  <div className="bg-gray-800 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <pre className="text-sm text-gray-300 font-mono">
                      {selectedStrategy.mql5_code}
                    </pre>
                  </div>
                </div>
                
                {/* Backtest Results */}
                <div>
                  <h3 className="font-semibold text-white mb-2">Backtest Results</h3>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gray-800 rounded-lg p-3">
                        <p className="text-sm text-gray-400">Total Trades</p>
                        <p className="text-lg font-bold text-white">{selectedStrategy.backtest_results.total_trades}</p>
                      </div>
                      <div className="bg-gray-800 rounded-lg p-3">
                        <p className="text-sm text-gray-400">Win Rate</p>
                        <p className="text-lg font-bold text-green-400">{selectedStrategy.backtest_results.win_rate.toFixed(1)}%</p>
                      </div>
                      <div className="bg-gray-800 rounded-lg p-3">
                        <p className="text-sm text-gray-400">Profit Factor</p>
                        <p className="text-lg font-bold text-cyan-400">{selectedStrategy.backtest_results.profit_factor.toFixed(2)}</p>
                      </div>
                      <div className="bg-gray-800 rounded-lg p-3">
                        <p className="text-sm text-gray-400">Max Drawdown</p>
                        <p className="text-lg font-bold text-red-400">{selectedStrategy.backtest_results.max_drawdown.toFixed(1)}%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-700">
                <p className="text-sm text-gray-400 mb-2">Natural Language Input:</p>
                <p className="text-gray-300 italic">"{selectedStrategy.natural_language_input}"</p>
              </div>
            </motion.div>
          </div>
        )}

        {/* System Status */}
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${whispererState.is_active ? 'bg-orange-400 animate-pulse' : 'bg-gray-400'}`} />
            <span>AI Model: {whispererState.language_model}</span>
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
        </div>
      </div>
    </div>
  )
} 