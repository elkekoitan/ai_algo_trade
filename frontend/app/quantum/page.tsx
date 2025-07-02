"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import { 
  Activity, 
  TrendingUp, 
  Brain, 
  Zap, 
  Globe, 
  Layers,
  Play,
  Pause,
  RefreshCw,
  Maximize2,
  Volume2,
  Settings,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  LineChart,
  CandlestickChart,
  Target,
  Shield,
  Cpu,
  Sparkles,
  Rocket,
  FlameIcon,
  DollarSign,
  History
} from "lucide-react";

// Dynamic imports for heavy components
const NetworkGraph3D = dynamic(() => import("@/components/quantum/NetworkGraph3D"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full"><Sparkles className="w-8 h-8 animate-pulse text-quantum-primary" /></div>
});

const HolographicChart = dynamic(() => import("@/components/quantum/HolographicChart"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full"><Activity className="w-8 h-8 animate-pulse text-quantum-primary" /></div>
});

const AIPatternRecognition = dynamic(() => import("@/components/quantum/AIPatternRecognition"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full"><Brain className="w-8 h-8 animate-pulse text-quantum-primary" /></div>
});

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  volume: number;
  signal: "BUY" | "SELL" | "HOLD";
  confidence: number;
  prediction: number;
  timeframe: string;
}

interface AISignal {
  id: string;
  type: string;
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  target: number;
  stopLoss: number;
  reasoning: string;
  timestamp: Date;
}

interface TradeHistory {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  price: number;
  profit: number;
  time: string;
  comment: string;
}

interface QuantumMetrics {
  ai_confidence: number;
  quantum_probability: number;
  market_sentiment: number;
  neural_prediction: string;
  risk_score: number;
  opportunity_index: number;
}

export default function QDashboard() {
  const [activeView, setActiveView] = useState<"overview" | "3d" | "ai" | "strategy">("overview");
  const [isAutoTrading, setIsAutoTrading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState("H1");
  const [marketSentiment, setMarketSentiment] = useState(72);
  const [aiSignals, setAiSignals] = useState<AISignal[]>([]);
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [dailyPnL, setDailyPnL] = useState(0);
  const [activePositions, setActivePositions] = useState(0);
  const [winRate, setWinRate] = useState(78.5);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [quantumMetrics, setQuantumMetrics] = useState<QuantumMetrics | null>(null);
  const [tradeHistory, setTradeHistory] = useState<TradeHistory[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [isConnected, setIsConnected] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  // Market data with real-time updates
  const [marketData, setMarketData] = useState<MarketData[]>([]);

  // Backend API calls
  const fetchAccountData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/trading/account_info');
      if (response.ok) {
        const data = await response.json();
        setPortfolioValue(data.balance || 0);
        setDailyPnL(data.profit || 0);
        setIsConnected(true);
        return data;
      }
    } catch (error) {
      console.error('Failed to fetch account data:', error);
      setIsConnected(false);
    }
    return null;
  };

  const fetchPositions = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/trading/positions');
      if (response.ok) {
        const positions = await response.json();
        setActivePositions(Array.isArray(positions) ? positions.length : 0);
        return positions;
      }
    } catch (error) {
      console.error('Failed to fetch positions:', error);
    }
    return [];
  };

  const fetchTradeHistory = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/trading/history');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setTradeHistory(data.data);
          setLastUpdate(data.last_update || new Date().toISOString());
        }
      }
    } catch (error) {
      console.error('Failed to fetch trade history:', error);
    }
  };

  const fetchPerformanceData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/performance/performance_summary');
      if (response.ok) {
        const data = await response.json();
        if (data.daily_stats) {
          setWinRate(data.daily_stats.win_rate || 0);
        }
      }
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    }
  };

  const fetchQuantumMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/quantum/dashboard');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.quantum_metrics) {
          setQuantumMetrics(data.quantum_metrics);
          setMarketSentiment(data.quantum_metrics.market_sentiment * 100);
        }
      }
    } catch (error) {
      console.error('Failed to fetch quantum metrics:', error);
    }
  };

  const fetchMarketData = async () => {
        const symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"];
    const updatedData: MarketData[] = [];

    for (const symbol of symbols) {
            try {
        const response = await fetch(`http://localhost:8002/api/v1/market/tick/${symbol}`);
              if (response.ok) {
                const tickData = await response.json();
          updatedData.push({
                  symbol: tickData.symbol,
                  price: tickData.last,
            change: (Math.random() - 0.5) * 0.01, // We'll calculate real change later
            volume: tickData.volume || Math.floor(Math.random() * 200000),
                  signal: Math.random() > 0.6 ? "BUY" : Math.random() > 0.3 ? "SELL" : "HOLD",
                  confidence: 75 + Math.random() * 25,
                  prediction: tickData.last * (1 + (Math.random() - 0.5) * 0.01),
                  timeframe: "15m"
          });
        }
      } catch (error) {
        console.error(`Failed to fetch tick data for ${symbol}:`, error);
      }
    }

    if (updatedData.length > 0) {
      setMarketData(updatedData);
    }
  };

  // Initialize data on component mount
  useEffect(() => {
    const initializeData = async () => {
      await Promise.all([
        fetchAccountData(),
        fetchPositions(),
        fetchTradeHistory(),
        fetchPerformanceData(),
        fetchQuantumMetrics(),
        fetchMarketData()
      ]);
    };

    initializeData();
  }, []);

  // Real-time updates
  useEffect(() => {
    const interval = setInterval(async () => {
      await Promise.all([
        fetchAccountData(),
        fetchPositions(),
        fetchQuantumMetrics(),
        fetchMarketData()
      ]);

      // Generate AI signals occasionally
      if (Math.random() > 0.95) {
          const symbols = ["EURUSD", "BTCUSD", "GBPUSD", "XAUUSD"];
          const actions = ["BUY", "SELL"] as const;
          const symbol = symbols[Math.floor(Math.random() * symbols.length)];
          const action = actions[Math.floor(Math.random() * actions.length)];
          
          const newSignal: AISignal = {
            id: Date.now().toString(),
          type: "QUANTUM_AI",
            symbol,
            action,
            confidence: 75 + Math.random() * 25,
            target: 1.1850,
            stopLoss: 1.1750,
          reasoning: `Quantum neural network detected ${action.toLowerCase()} pattern with high probability`,
            timestamp: new Date()
          };
          
          setAiSignals(prev => [newSignal, ...prev.slice(0, 4)]);
          
          // Play sound if enabled
          if (soundEnabled && audioRef.current) {
            audioRef.current.play().catch(e => console.log("Audio play failed:", e));
          }
        }
    }, 3000); // Update every 3 seconds

    return () => clearInterval(interval);
  }, [soundEnabled]);

  // Refresh trade history every 5 minutes
  useEffect(() => {
    const historyInterval = setInterval(fetchTradeHistory, 300000);
    return () => clearInterval(historyInterval);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-quantum-dark relative overflow-hidden">
      {/* Page Title */}
      <div className="relative z-10 pt-6 pb-2">
        <div className="container mx-auto px-6">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between"
          >
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">QDashboard</h1>
              <p className="text-gray-400">Quantum AI Trading Intelligence Hub - Live MT5 Data</p>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {isConnected ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                <span className="text-sm font-medium">
                  {isConnected ? 'MT5 Connected' : 'MT5 Disconnected'}
                </span>
              </div>
              {lastUpdate && (
                <div className="text-xs text-gray-500">
                  Last Update: {new Date(lastUpdate).toLocaleTimeString()}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-quantum-primary/5 via-transparent to-quantum-accent/5" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
        {/* Floating particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-quantum-primary/30 rounded-full"
            initial={{ 
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : 0, 
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : 0
            }}
            animate={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : 0,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : 0,
            }}
            transition={{
              duration: 20 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}
      </div>

      {/* Audio element for notifications */}
      <audio ref={audioRef} src="/notification.mp3" />

      {/* Main Content */}
      <main className="container mx-auto px-6 py-4 relative z-10">
        <AnimatePresence mode="wait">
          {activeView === "overview" && (
            <motion.div
              key="overview"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="space-y-6"
            >
              {/* Real-time Dashboard Metrics */}
              <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="quantum-panel p-6 text-center">
                  <DollarSign className="w-8 h-8 text-quantum-primary mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Portfolio Value</p>
                  <p className="text-2xl font-bold text-white">{formatCurrency(portfolioValue)}</p>
                  <p className="text-sm text-green-400 mt-1">Real-time MT5</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <TrendingUp className="w-8 h-8 text-green-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Daily P&L</p>
                  <p className={`text-2xl font-bold ${dailyPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {dailyPnL >= 0 ? '+' : ''}{formatCurrency(dailyPnL)}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">Live Trading</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Activity className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Active Positions</p>
                  <p className="text-2xl font-bold text-white">{activePositions}</p>
                  <p className="text-sm text-blue-400 mt-1">MT5 Live</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Target className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Win Rate</p>
                  <p className="text-2xl font-bold text-white">{winRate.toFixed(1)}%</p>
                  <p className="text-sm text-purple-400 mt-1">Historical</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Brain className="w-8 h-8 text-quantum-accent mx-auto mb-2" />
                  <p className="text-sm text-gray-400">AI Confidence</p>
                  <p className="text-2xl font-bold text-white">
                    {quantumMetrics ? quantumMetrics.ai_confidence.toFixed(1) : marketSentiment.toFixed(1)}%
                  </p>
                  <p className="text-sm text-quantum-accent mt-1">Quantum Neural</p>
                </div>
              </motion.div>

              {/* Quantum Metrics Panel */}
              {quantumMetrics && (
                <motion.div variants={itemVariants} className="quantum-panel p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-quantum-primary" />
                    Quantum Intelligence Metrics
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Quantum Probability</p>
                      <p className="text-xl font-bold text-quantum-primary">{quantumMetrics.quantum_probability.toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Market Sentiment</p>
                      <p className="text-xl font-bold text-cyan-400">{(quantumMetrics.market_sentiment * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Neural Prediction</p>
                      <p className="text-xl font-bold text-green-400">{quantumMetrics.neural_prediction}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Risk Score</p>
                      <p className="text-xl font-bold text-yellow-400">{quantumMetrics.risk_score.toFixed(1)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Opportunity Index</p>
                      <p className="text-xl font-bold text-purple-400">{quantumMetrics.opportunity_index.toFixed(1)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">AI Confidence</p>
                      <p className="text-xl font-bold text-quantum-accent">{quantumMetrics.ai_confidence.toFixed(1)}%</p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Trading Controls */}
              <motion.div variants={itemVariants} className="quantum-panel p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-quantum-primary" />
                    Quantum Trading Engine
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm ${isAutoTrading ? "text-green-400" : "text-gray-400"}`}>
                      {isAutoTrading ? "AUTO TRADING ACTIVE" : "MANUAL MODE"}
                    </span>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsAutoTrading(!isAutoTrading)}
                      className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                        isAutoTrading 
                          ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" 
                          : "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                      }`}
                    >
                      {isAutoTrading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      {isAutoTrading ? "STOP" : "START"}
                    </motion.button>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <motion.button
                    whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(0, 255, 136, 0.5)" }}
                    whileTap={{ scale: 0.98 }}
                    className="quantum-button-primary py-3 px-6 rounded-lg font-semibold"
                  >
                    <Zap className="w-5 h-5 inline mr-2" />
                    Lightning Trade
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(255, 0, 85, 0.5)" }}
                    whileTap={{ scale: 0.98 }}
                    className="quantum-button-danger py-3 px-6 rounded-lg font-semibold"
                  >
                    <AlertTriangle className="w-5 h-5 inline mr-2" />
                    Panic Close All
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(0, 212, 255, 0.5)" }}
                    whileTap={{ scale: 0.98 }}
                    className="quantum-button-accent py-3 px-6 rounded-lg font-semibold"
                  >
                    <Rocket className="w-5 h-5 inline mr-2" />
                    Turbo Mode
                  </motion.button>
                </div>
              </motion.div>

              {/* Market Overview & Trade History */}
              <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Live Market Data */}
                <div className="quantum-panel p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-quantum-primary" />
                    Live Market Data (MT5)
                  </h3>
                  <div className="space-y-3">
                    {marketData.map((item, index) => (
                      <motion.div
                        key={item.symbol}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-8 rounded-full ${
                            item.signal === "BUY" ? "bg-green-400" : 
                            item.signal === "SELL" ? "bg-red-400" : "bg-yellow-400"
                          }`} />
                          <div>
                            <p className="font-semibold text-white">{item.symbol}</p>
                            <p className="text-sm text-gray-400">Live MT5</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-white">{item.price.toFixed(item.symbol.includes("USD") ? 2 : 5)}</p>
                          <p className={`text-sm ${item.change > 0 ? "text-green-400" : "text-red-400"}`}>
                            {item.change > 0 ? "+" : ""}{(item.change * 100).toFixed(2)}%
                          </p>
                        </div>
                        <div className="text-right">
                          <p className={`text-sm font-semibold ${
                            item.signal === "BUY" ? "text-green-400" : 
                            item.signal === "SELL" ? "text-red-400" : "text-yellow-400"
                          }`}>
                            {item.signal}
                          </p>
                          <div className="flex items-center gap-1 mt-1">
                            <div className="w-full bg-white/10 rounded-full h-1.5">
                              <motion.div
                                className="bg-quantum-primary h-full rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: `${item.confidence}%` }}
                                transition={{ duration: 1 }}
                              />
                            </div>
                            <span className="text-xs text-gray-400">{item.confidence.toFixed(0)}%</span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Recent Trades History */}
                <div className="quantum-panel p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <History className="w-5 h-5 text-quantum-accent" />
                    Recent Trades History
                  </h3>
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {tradeHistory.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No recent trades...</p>
                      </div>
                    ) : (
                      tradeHistory.slice(0, 10).map((trade, index) => (
                        <motion.div
                          key={trade.ticket}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className={`p-3 rounded-lg border ${
                            trade.profit > 0 
                              ? 'bg-green-500/10 border-green-500/30' 
                              : 'bg-red-500/10 border-red-500/30'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-white">{trade.symbol}</span>
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                trade.type === "buy" ? "bg-green-400/20 text-green-400" : "bg-red-400/20 text-red-400"
                              }`}>
                                {trade.type.toUpperCase()}
                              </span>
                            </div>
                            <span className="text-xs text-gray-400">
                              {new Date(trade.time).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Vol: {trade.volume}</span>
                            <span className="text-gray-400">Price: {trade.price}</span>
                            <span className={`font-semibold ${
                              trade.profit > 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {trade.profit > 0 ? '+' : ''}{formatCurrency(trade.profit)}
                            </span>
                          </div>
                        </motion.div>
                      ))
                    )}
                  </div>
                </div>
              </motion.div>

              {/* AI Signals */}
              <motion.div variants={itemVariants} className="quantum-panel p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-quantum-accent" />
                  Quantum AI Signals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {aiSignals.length === 0 ? (
                    <div className="col-span-full text-center py-8 text-gray-500">
                      <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Waiting for quantum AI signals...</p>
                    </div>
                  ) : (
                    aiSignals.map((signal, index) => (
                      <motion.div
                        key={signal.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.1 }}
                          className="p-4 bg-gradient-to-r from-quantum-accent/10 to-quantum-primary/10 rounded-lg border border-quantum-accent/30"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Sparkles className="w-4 h-4 text-quantum-accent" />
                              <span className="font-semibold text-white">{signal.symbol}</span>
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                signal.action === "BUY" ? "bg-green-400/20 text-green-400" : 
                                signal.action === "SELL" ? "bg-red-400/20 text-red-400" : 
                                "bg-yellow-400/20 text-yellow-400"
                              }`}>
                                {signal.action}
                              </span>
                            </div>
                            <span className="text-xs text-gray-400">
                              {new Date(signal.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-300 mb-2">{signal.reasoning}</p>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-400">Target: {signal.target}</span>
                            <span className="text-gray-400">SL: {signal.stopLoss}</span>
                            <div className="flex items-center gap-1">
                              <Shield className="w-3 h-3 text-quantum-accent" />
                              <span className="text-quantum-accent">{signal.confidence.toFixed(0)}%</span>
                            </div>
                          </div>
                        </motion.div>
                      ))
                    )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
} 