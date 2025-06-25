"use client";

import { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  RefreshCw,
  Filter
} from "lucide-react";

interface ICTSignal {
  id: string;
  symbol: string;
  timeframe: string;
  signal_type: string;
  pattern_type: string;
  strength: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  risk_reward_ratio: number;
  score: number;
  risk_level: string;
  confluence_factors: {
    trend_strength: number;
    volume_confirmation: number;
    structure_quality: number;
    liquidity_presence: number;
    confluence_factor: number;
    time_of_day: number;
    market_sentiment: number;
    setup_strength: number;
  };
  analysis: {
    trend_analysis: string;
    volume_analysis: string;
    structure_analysis: string;
    entry_reasoning: string;
  };
  timestamp: string;
}

export default function SignalsPage() {
  const [signals, setSignals] = useState<ICTSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState("all");
  const [selectedPattern, setSelectedPattern] = useState("all");
  const [minScore, setMinScore] = useState(80);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    try {
      const response = await fetch(
        `http://localhost:8001/api/v1/signals/ict?min_score=${minScore}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setSignals(data);
        setError(null);
      } else {
        setError("Failed to fetch signals");
      }
    } catch (err) {
      setError("Connection error");
    } finally {
      setLoading(false);
    }
  };

  const filteredSignals = signals.filter(signal => {
    if (selectedTimeframe !== "all" && signal.timeframe !== selectedTimeframe) return false;
    if (selectedPattern !== "all" && signal.pattern_type !== selectedPattern) return false;
    return true;
  });

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 80) return "text-yellow-400";
    if (score >= 70) return "text-orange-400";
    return "text-red-400";
  };

  const getRiskColor = (risk: string) => {
    switch(risk) {
      case "LOW": return "text-green-400 bg-green-400/10";
      case "MEDIUM": return "text-yellow-400 bg-yellow-400/10";
      case "HIGH": return "text-orange-400 bg-orange-400/10";
      case "EXTREME": return "text-red-400 bg-red-400/10";
      default: return "text-gray-400 bg-gray-400/10";
    }
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-950 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">ICT Signals</h1>
              <p className="text-gray-400">Real-time ICT pattern detection and analysis</p>
            </div>
            <button
              onClick={fetchSignals}
              className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-white font-medium transition-colors"
            >
              <RefreshCw size={18} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Filters */}
          <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 mb-6">
            <div className="flex items-center space-x-2 mb-4">
              <Filter size={20} className="text-gray-400" />
              <h3 className="text-lg font-semibold text-white">Filters</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Timeframe</label>
                <select 
                  value={selectedTimeframe}
                  onChange={(e) => setSelectedTimeframe(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="all">All Timeframes</option>
                  <option value="M5">M5</option>
                  <option value="M15">M15</option>
                  <option value="M30">M30</option>
                  <option value="H1">H1</option>
                  <option value="H4">H4</option>
                  <option value="D1">D1</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Pattern Type</label>
                <select 
                  value={selectedPattern}
                  onChange={(e) => setSelectedPattern(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="all">All Patterns</option>
                  <option value="order_block">Order Block</option>
                  <option value="fair_value_gap">Fair Value Gap</option>
                  <option value="breaker_block">Breaker Block</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Min Score: {minScore}</label>
                <input 
                  type="range"
                  min="50"
                  max="100"
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Signals List */}
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="animate-spin text-gray-400" size={32} />
            </div>
          ) : error ? (
            <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
              <p className="text-red-400">{error}</p>
            </div>
          ) : filteredSignals.length === 0 ? (
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 text-center">
              <p className="text-gray-400">No signals found matching your criteria</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredSignals.map((signal) => (
                <div 
                  key={signal.id}
                  className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 hover:border-gray-700 transition-colors"
                >
                  {/* Signal Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        signal.signal_type === "BUY" ? "bg-green-500/20" : "bg-red-500/20"
                      }`}>
                        {signal.signal_type === "BUY" ? 
                          <TrendingUp className="text-green-500" size={20} /> : 
                          <TrendingDown className="text-red-500" size={20} />
                        }
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-white">{signal.symbol}</h4>
                        <p className="text-sm text-gray-400">{signal.timeframe} • {signal.pattern_type.replace(/_/g, ' ')}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${getScoreColor(signal.score)}`}>
                        {signal.score}
                      </p>
                      <span className={`text-xs px-2 py-1 rounded-full ${getRiskColor(signal.risk_level)}`}>
                        {signal.risk_level}
                      </span>
                    </div>
                  </div>

                  {/* Price Levels */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Entry</p>
                      <p className="text-sm font-medium text-white">{signal.entry_price.toFixed(5)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Stop Loss</p>
                      <p className="text-sm font-medium text-red-400">{signal.stop_loss.toFixed(5)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Take Profit</p>
                      <p className="text-sm font-medium text-green-400">{signal.take_profit.toFixed(5)}</p>
                    </div>
                  </div>

                  {/* Risk Reward */}
                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg mb-4">
                    <span className="text-sm text-gray-400">Risk/Reward Ratio</span>
                    <span className="text-sm font-medium text-white">1:{signal.risk_reward_ratio.toFixed(2)}</span>
                  </div>

                  {/* Confluence Factors */}
                  <div className="space-y-2">
                    <p className="text-xs text-gray-400 uppercase tracking-wider">Confluence Factors</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Trend</span>
                        <span className="text-gray-300">{(signal.confluence_factors.trend_strength * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Volume</span>
                        <span className="text-gray-300">{(signal.confluence_factors.volume_confirmation * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Structure</span>
                        <span className="text-gray-300">{(signal.confluence_factors.structure_quality * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Liquidity</span>
                        <span className="text-gray-300">{(signal.confluence_factors.liquidity_presence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Timestamp */}
                  <div className="mt-4 pt-4 border-t border-gray-800">
                    <p className="text-xs text-gray-500">
                      Generated {new Date(signal.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
} 