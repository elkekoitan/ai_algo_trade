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
  FlameIcon
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

export default function QuantumDashboard() {
  const [activeView, setActiveView] = useState<"overview" | "3d" | "ai" | "strategy">("overview");
  const [isAutoTrading, setIsAutoTrading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState("H1");
  const [marketSentiment, setMarketSentiment] = useState(72);
  const [aiSignals, setAiSignals] = useState<AISignal[]>([]);
  const [portfolioValue, setPortfolioValue] = useState(2725252.20);
  const [dailyPnL, setDailyPnL] = useState(53754.11);
  const [activePositions, setActivePositions] = useState(42);
  const [winRate, setWinRate] = useState(78.5);
  const [soundEnabled, setSoundEnabled] = useState(true);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  // Market data with real-time updates
  const [marketData, setMarketData] = useState<MarketData[]>([
    { symbol: "EURUSD", price: 1.16952, change: 0.0012, volume: 125000, signal: "BUY", confidence: 87, prediction: 1.1750, timeframe: "15m" },
    { symbol: "BTCUSD", price: 107385, change: 0.0065, volume: 450000, signal: "BUY", confidence: 92, prediction: 108500, timeframe: "2h" },
    { symbol: "GBPUSD", price: 1.31245, change: -0.0008, volume: 98000, signal: "SELL", confidence: 75, prediction: 1.3080, timeframe: "30m" },
    { symbol: "XAUUSD", price: 3333.89, change: 0.0034, volume: 75000, signal: "BUY", confidence: 88, prediction: 3350, timeframe: "1h" },
    { symbol: "USDJPY", price: 149.235, change: -0.0015, volume: 110000, signal: "HOLD", confidence: 65, prediction: 149.00, timeframe: "4h" },
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // Update portfolio value from backend
        const accountResponse = await fetch('http://localhost:8001/api/v1/trading/account');
        if (accountResponse.ok) {
          const accountData = await accountResponse.json();
          setPortfolioValue(accountData.balance);
          setDailyPnL(accountData.profit);
        }

        // Update market data from backend
        const symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"];
        const updatedData = await Promise.all(
          symbols.map(async (symbol) => {
            try {
              const response = await fetch(`http://localhost:8001/api/v1/market/tick/${symbol}`);
              if (response.ok) {
                const tickData = await response.json();
                return {
                  symbol: tickData.symbol,
                  price: tickData.last,
                  change: (Math.random() - 0.5) * 0.01,
                  volume: tickData.volume,
                  signal: Math.random() > 0.6 ? "BUY" : Math.random() > 0.3 ? "SELL" : "HOLD",
                  confidence: 75 + Math.random() * 25,
                  prediction: tickData.last * (1 + (Math.random() - 0.5) * 0.01),
                  timeframe: "15m"
                };
              }
              return marketData.find(item => item.symbol === symbol);
            } catch (err) {
              return marketData.find(item => item.symbol === symbol);
            }
          })
        );

        setMarketData(updatedData.filter((item): item is MarketData => item !== undefined));

        // Update auto trader status
        const autoTraderResponse = await fetch('http://localhost:8001/api/v1/auto-trader/status');
        if (autoTraderResponse.ok) {
          const autoTraderData = await autoTraderResponse.json();
          setWinRate(autoTraderData.win_rate || winRate);
          setActivePositions(autoTraderData.active_signals || activePositions);
        }

      } catch (error) {
        console.log('API call failed, using mock data:', error);
        // Fallback to original mock behavior
        setMarketData(prev => prev.map(item => ({
          ...item,
          price: item.price * (1 + (Math.random() - 0.5) * 0.001),
          change: (Math.random() - 0.5) * 0.01,
          volume: Math.floor(item.volume * (0.9 + Math.random() * 0.2)),
          confidence: Math.min(100, Math.max(50, item.confidence + (Math.random() - 0.5) * 5))
        })));
      }
      
      setMarketSentiment(prev => Math.min(100, Math.max(0, prev + (Math.random() - 0.5) * 2)));
      
      // Generate new AI signals occasionally
      if (Math.random() > 0.9) {
        try {
          const signalsResponse = await fetch('http://localhost:8001/api/v1/signals/ict?limit=5');
          if (signalsResponse.ok) {
            const signalsData = await signalsResponse.json();
            if (signalsData.signals && signalsData.signals.length > 0) {
              const newSignal = signalsData.signals[0];
              const convertedSignal: AISignal = {
                id: newSignal.id,
                type: newSignal.type,
                symbol: newSignal.symbol,
                action: newSignal.direction === "bullish" ? "BUY" : "SELL",
                confidence: newSignal.confidence,
                target: newSignal.price * 1.002,
                stopLoss: newSignal.price * 0.998,
                reasoning: newSignal.description || "AI analysis detected pattern",
                timestamp: new Date()
              };
              
              setAiSignals(prev => [convertedSignal, ...prev.slice(0, 4)]);
              
              // Play sound if enabled
              if (soundEnabled && audioRef.current) {
                audioRef.current.play().catch(e => console.log("Audio play failed:", e));
              }
            }
          }
        } catch (err) {
          console.log('AI signals fetch failed, using mock');
          // Fallback to original mock signal generation
          const symbols = ["EURUSD", "BTCUSD", "GBPUSD", "XAUUSD"];
          const actions = ["BUY", "SELL"] as const;
          const symbol = symbols[Math.floor(Math.random() * symbols.length)];
          const action = actions[Math.floor(Math.random() * actions.length)];
          
          const newSignal: AISignal = {
            id: Date.now().toString(),
            type: "AI_NEURAL",
            symbol,
            action,
            confidence: 75 + Math.random() * 25,
            target: 1.1850,
            stopLoss: 1.1750,
            reasoning: "Neural network detected strong momentum pattern",
            timestamp: new Date()
          };
          
          setAiSignals(prev => [newSignal, ...prev.slice(0, 4)]);
          
          // Play sound if enabled
          if (soundEnabled && audioRef.current) {
            audioRef.current.play().catch(e => console.log("Audio play failed:", e));
          }
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [soundEnabled, marketData, winRate, activePositions]);

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

  return (
    <div className="min-h-screen bg-quantum-dark relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-quantum-primary/5 via-transparent to-quantum-accent/5" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
        {/* Floating particles */}
        {[...Array(20)].map((_, i) => (
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
      <main className="container mx-auto px-6 py-8 relative z-10">
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
              {/* Command Center */}
              <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="quantum-panel p-6 text-center">
                  <Zap className="w-8 h-8 text-quantum-primary mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Portfolio Value</p>
                  <p className="text-2xl font-bold text-white">${portfolioValue.toLocaleString()}</p>
                  <p className="text-sm text-green-400 mt-1">+{((dailyPnL / portfolioValue) * 100).toFixed(2)}%</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <TrendingUp className="w-8 h-8 text-green-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Daily P&L</p>
                  <p className="text-2xl font-bold text-green-400">+${dailyPnL.toLocaleString()}</p>
                  <p className="text-sm text-gray-500 mt-1">Last 24h</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Activity className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Active Positions</p>
                  <p className="text-2xl font-bold text-white">{activePositions}</p>
                  <p className="text-sm text-blue-400 mt-1">+3 pending</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Target className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Win Rate</p>
                  <p className="text-2xl font-bold text-white">{winRate}%</p>
                  <p className="text-sm text-purple-400 mt-1">Last 100 trades</p>
                </div>
                
                <div className="quantum-panel p-6 text-center">
                  <Brain className="w-8 h-8 text-quantum-accent mx-auto mb-2" />
                  <p className="text-sm text-gray-400">AI Confidence</p>
                  <p className="text-2xl font-bold text-white">{marketSentiment}%</p>
                  <p className="text-sm text-quantum-accent mt-1">Neural Score</p>
                </div>
              </motion.div>

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

              {/* Market Overview */}
              <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Live Market Data */}
                <div className="quantum-panel p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-quantum-primary" />
                    Live Market Data
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
                            <p className="text-sm text-gray-400">Vol: {(item.volume / 1000).toFixed(0)}K</p>
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

                {/* AI Signals */}
                <div className="quantum-panel p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-quantum-accent" />
                    Neural AI Signals
                  </h3>
                  <div className="space-y-3">
                    {aiSignals.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Waiting for AI signals...</p>
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
                </div>
              </motion.div>

              {/* Market Sentiment */}
              <motion.div variants={itemVariants} className="quantum-panel p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-quantum-primary" />
                  Global Market Sentiment
                </h3>
                <div className="relative h-32">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full bg-gradient-to-r from-red-500/20 via-yellow-500/20 to-green-500/20 rounded-full h-8">
                      <motion.div
                        className="relative h-full"
                        initial={{ x: 0 }}
                        animate={{ x: `${(marketSentiment / 100) * 100}%` }}
                        transition={{ type: "spring", stiffness: 50 }}
                      >
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-12 bg-white rounded-full shadow-lg shadow-white/50" />
                      </motion.div>
                    </div>
                  </div>
                  <div className="absolute inset-x-0 top-0 flex justify-between text-xs text-gray-400">
                    <span>Extreme Fear</span>
                    <span>Neutral</span>
                    <span>Extreme Greed</span>
                  </div>
                  <div className="absolute inset-x-0 bottom-0 text-center">
                    <p className="text-3xl font-bold text-white">{marketSentiment}</p>
                    <p className="text-sm text-gray-400">Market Score</p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}

          {activeView === "3d" && (
            <motion.div
              key="3d"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-[600px] quantum-panel p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-quantum-primary" />
                3D Market Network Analysis
              </h3>
              <NetworkGraph3D />
            </motion.div>
          )}

          {activeView === "ai" && (
            <motion.div
              key="ai"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <AIPatternRecognition />
            </motion.div>
          )}

          {activeView === "strategy" && (
            <motion.div
              key="strategy"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="quantum-panel p-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Rocket className="w-5 h-5 text-quantum-primary" />
                Strategy Lab - Coming Soon
              </h3>
              <div className="text-center py-16">
                <Rocket className="w-24 h-24 mx-auto mb-4 text-quantum-primary animate-pulse" />
                <p className="text-xl text-white mb-2">Advanced Strategy Builder</p>
                <p className="text-gray-400">Drag & drop strategy creation with AI optimization</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Floating Action Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-8 right-8 w-16 h-16 bg-quantum-primary rounded-full shadow-lg shadow-quantum-primary/50 flex items-center justify-center text-black"
      >
        <Zap className="w-8 h-8" />
      </motion.button>

      {/* Custom Styles */}
      <style jsx global>{`
        .quantum-panel {
          background: rgba(0, 0, 0, 0.4);
          backdrop-filter: blur(20px) saturate(200%);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 1rem;
          box-shadow: 
            0 8px 32px rgba(0, 255, 136, 0.1),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05);
          transition: all 0.3s ease;
        }
        
        .quantum-panel:hover {
          box-shadow: 
            0 8px 32px rgba(0, 255, 136, 0.2),
            inset 0 0 0 1px rgba(255, 255, 255, 0.1);
        }
        
        .quantum-button-primary {
          background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
          color: black;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .quantum-button-danger {
          background: linear-gradient(135deg, #ff0055 0%, #ff4488 100%);
          color: white;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .quantum-button-accent {
          background: linear-gradient(135deg, #00d4ff 0%, #9945ff 100%);
          color: white;
          font-weight: 600;
          transition: all 0.3s ease;
        }
      `}</style>
    </div>
  );
} 