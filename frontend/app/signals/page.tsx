"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  Zap,
  AlertCircle,
  RefreshCw,
  Filter,
  Star,
  Activity,
  BarChart3,
  Brain,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import TradingViewChart from '@/components/charts/TradingViewChart'; // reusing our great chart

interface Signal {
  id: string;
  symbol: string;
  timeframe: string;
  direction: "BULLISH" | "BEARISH";
  status: "ACTIVE" | "TRIGGERED" | "TP" | "SL" | "CANCELLED";
  pattern: string;
  confidence: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  risk_reward: number;
  ai_analysis: string;
  timestamp: string;
}

const SignalCard = ({ signal }: { signal: Signal }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const getDirectionStyles = () => {
        if (signal.direction === "BULLISH") {
            return {
                main: "border-green-500/50",
                bg: "bg-green-500/10",
                text: "text-green-400",
                icon: <TrendingUp className="w-5 h-5 text-green-400" />
            };
        }
        return {
            main: "border-red-500/50",
            bg: "bg-red-500/10",
            text: "text-red-400",
            icon: <TrendingDown className="w-5 h-5 text-red-400" />
        };
    };

    const styles = getDirectionStyles();

    return (
        <motion.div
            layout
            className={`quantum-card p-5 rounded-lg border-l-4 transition-all duration-300 ${styles.main} ${styles.bg}`}
        >
            {/* Collapsed View */}
            <div className="flex items-center justify-between cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex items-center gap-4">
                    {styles.icon}
                    <div>
                        <h4 className="font-bold text-white text-lg">{signal.symbol} <span className="text-sm font-normal text-gray-400">({signal.timeframe})</span></h4>
                        <p className="text-sm text-gray-300">{signal.pattern}</p>
                    </div>
                </div>
                <div className="text-right">
                    <div className="font-mono text-lg text-white">{signal.entry_price.toFixed(5)}</div>
                    <div className={`text-xs font-bold ${styles.text}`}>{signal.direction}</div>
                </div>
                 <div className="flex items-center gap-2">
                    <div className={`font-bold text-lg ${signal.confidence > 85 ? 'text-green-400' : 'text-yellow-400'}`}>
                        {signal.confidence.toFixed(0)}%
                    </div>
                    {isExpanded ? <ChevronUp /> : <ChevronDown />}
                </div>
            </div>

            {/* Expanded View */}
            <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: isExpanded ? 1 : 0, height: isExpanded ? 'auto' : 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
            >
                <div className="pt-4 mt-4 border-t border-white/10">
                    <div className="mb-4">
                        <h5 className="text-sm font-semibold text-quantum-primary mb-2 flex items-center gap-2">
                            <Brain size={16} /> AI Analysis
                        </h5>
                        <p className="text-gray-300 text-sm leading-relaxed">{signal.ai_analysis}</p>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 text-sm mb-4">
                        <div className="text-center">
                            <p className="text-gray-400">Stop Loss</p>
                            <p className="font-mono text-red-400">{signal.stop_loss.toFixed(5)}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-gray-400">Take Profit</p>
                            <p className="font-mono text-green-400">{signal.take_profit.toFixed(5)}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-gray-400">Risk/Reward</p>
                            <p className="font-bold text-quantum-primary">1 : {signal.risk_reward.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="h-48 rounded-lg overflow-hidden mt-2">
                         <TradingViewChart 
                            symbol={signal.symbol} 
                            timeframe={signal.timeframe} 
                            height={192} 
                         />
                    </div>

                     <div className="mt-4 pt-3 border-t border-white/10">
                        <div className="flex items-center justify-between text-xs text-gray-400">
                             <div className="flex items-center gap-2">
                                <Clock className="w-3 h-3" />
                                <span>{new Date(signal.timestamp).toLocaleString()}</span>
                            </div>
                            <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded">{signal.status}</span>
                        </div>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
}


export default function QuantumSignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/signals");
      if (response.ok) {
        const data = await response.json();
        if (data.success && Array.isArray(data.signals)) {
          setSignals(data.signals);
        }
      }
    } catch (error) {
      console.error("Error fetching signals:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [fetchSignals]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.05 } }
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Zap className="w-8 h-8 text-quantum-primary" />
            Real-Time AI Signal Feed
        </h1>
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchSignals}
            className="quantum-button p-2 rounded-lg flex items-center gap-2"
        >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
        </motion.button>
      </div>

      {loading && signals.length === 0 ? (
        <div className="text-center py-12">
            <div className="animate-spin w-10 h-10 border-4 border-quantum-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-300 text-lg">Scanning markets for high-probability setups...</p>
        </div>
      ) : signals.length === 0 ? (
        <div className="text-center py-12 quantum-panel">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-500" />
          <p className="text-gray-300 text-lg">No active signals found.</p>
          <p className="text-gray-400">The AI engine is constantly monitoring the markets. Check back soon.</p>
        </div>
      ) : (
        <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
        >
          {signals.map((signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </motion.div>
      )}
    </div>
  );
} 