"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  AlertCircle,
  Send,
  Zap,
  Target,
  Shield,
  Activity,
  BarChart3,
  Clock,
  X,
  RefreshCw,
  Maximize2,
  Brain,
  Eye,
  Crosshair,
  BarChart,
  Gauge,
  Timer,
  Layers,
  Sparkles
} from "lucide-react";
import TradingViewChart from '@/components/charts/TradingViewChart';
import ApiService from '@/lib/api';

interface Position {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  open_price: number;
  current_price: number;
  sl: number | null;
  tp: number | null;
  profit: number;
  swap: number;
  magic: number;
  comment: string;
  open_time: string;
}

interface AccountInfo {
  login: string;
  server: string;
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  margin_level: number;
  currency: string;
  company: string;
  name: string;
  leverage: number;
  profit: number;
}

interface MarketData {
  symbol: string;
  bid: number;
  ask: number;
  spread: number;
  change: number;
  changePercent: number;
  volume: number;
}

export default function QuantumTradingPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("EURUSD");
  const [selectedTimeframe, setSelectedTimeframe] = useState("H1");
  const [positions, setPositions] = useState<Position[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [isLiveMode, setIsLiveMode] = useState(true);
  
  // Order form state
  const [orderType, setOrderType] = useState<"BUY" | "SELL">("BUY");
  const [volume, setVolume] = useState("0.01");
  const [stopLoss, setStopLoss] = useState("");
  const [takeProfit, setTakeProfit] = useState("");
  const [comment, setComment] = useState("AI Algo Trade v3.0");
  
  // Advanced features state
  const [riskLevel, setRiskLevel] = useState<"LOW" | "MEDIUM" | "HIGH">("MEDIUM");
  const [autoSL, setAutoSL] = useState(true);
  const [autoTP, setAutoTP] = useState(true);
  const [trailingStop, setTrailingStop] = useState(false);
  const [orderSize, setOrderSize] = useState<"FIXED" | "PERCENT" | "RISK">("RISK");

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const [accountRes, symbolsRes, positionsRes, ...marketRes] = await Promise.all([
        ApiService.getAccountInfo(),
        ApiService.getSymbols(),
        ApiService.getPositions(),
        ...["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"].map(s => ApiService.getSymbolTick(s))
      ]);

      if (!accountRes.error && accountRes.data) {
        setAccountInfo(accountRes.data);
      }

      if (!symbolsRes.error && Array.isArray(symbolsRes.data)) {
        setSymbols(symbolsRes.data.map((s: { name: string }) => s.name));
      } else {
         setSymbols(["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]);
      }

      if (!positionsRes.error && Array.isArray(positionsRes.data)) {
        setPositions(positionsRes.data);
      }

      const marketDataResults = marketRes
        .filter(res => !res.error && res.data)
        .map(res => {
            const data = res.data;
            return {
              symbol: data.symbol,
              bid: data.bid,
              ask: data.ask,
              spread: (data.ask - data.bid) * 10000,
              change: Math.random() * 0.002 - 0.001, // Simulated change
              changePercent: (Math.random() * 2 - 1),
              volume: data.volume || 0
            };
        });
      setMarketData(marketDataResults);

    } catch (error) {
      console.error("Error fetching initial data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [fetchAllData]);

  const placeOrder = async () => {
    const orderData = {
      symbol: selectedSymbol,
      order_type: orderType,
      volume: parseFloat(volume),
      sl: stopLoss ? parseFloat(stopLoss) : null,
      tp: takeProfit ? parseFloat(takeProfit) : null,
      comment: comment,
    };

    console.log("SENDING ORDER DATA:", orderData);

    const result = await ApiService.placeOrder(orderData);
    
    if (!result.error && result.data?.success) {
      alert(`Order placed successfully! Order ID: ${result.data.order_id}`);
      setVolume("0.01");
      setStopLoss("");
      setTakeProfit("");
      fetchAllData(); // Refresh all data
    } else {
      alert(`Order failed: ${result.message || result.data?.message}`);
    }
  };

  const closePosition = async (ticket: number) => {
    if (!confirm(`Are you sure you want to close position #${ticket}?`)) return;

    const result = await ApiService.closePosition(ticket);
    
    if (!result.error && result.data?.success) {
      alert("Position closed successfully!");
      fetchAllData(); // Refresh all data
    } else {
      alert(`Failed to close position: ${result.message || result.data?.message}`);
    }
  };

  const totalProfit = positions.reduce((sum, pos) => sum + pos.profit, 0);

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
    <div className="container mx-auto p-4 md:p-6 space-y-6">
      {/* Advanced Account Dashboard */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
      >
        {/* Account Balance */}
        <motion.div variants={itemVariants} className="quantum-panel p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-quantum-primary/20 to-transparent rounded-full -mr-10 -mt-10" />
          <DollarSign className="w-8 h-8 text-quantum-primary mb-3" />
          <p className="text-sm text-gray-400">Account Balance</p>
          <p className="text-2xl font-bold text-white">
            ${accountInfo?.balance?.toLocaleString() || '0.00'}
          </p>
          <p className="text-xs text-quantum-primary mt-1">{accountInfo?.currency || 'USD'}</p>
        </motion.div>

        {/* Equity */}
        <motion.div variants={itemVariants} className="quantum-panel p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-green-500/20 to-transparent rounded-full -mr-10 -mt-10" />
          <Gauge className="w-8 h-8 text-green-400 mb-3" />
          <p className="text-sm text-gray-400">Equity</p>
          <p className="text-2xl font-bold text-white">
            ${accountInfo?.equity?.toLocaleString() || '0.00'}
          </p>
          <p className={`text-xs mt-1 ${(accountInfo?.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            P&L: ${accountInfo?.profit?.toFixed(2) || '0.00'}
          </p>
        </motion.div>

        {/* Margin Level */}
        <motion.div variants={itemVariants} className="quantum-panel p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full -mr-10 -mt-10" />
          <Shield className="w-8 h-8 text-blue-400 mb-3" />
          <p className="text-sm text-gray-400">Margin Level</p>
          <p className="text-2xl font-bold text-white">
            {accountInfo?.margin_level?.toFixed(0) || '0'}%
          </p>
          <p className="text-xs text-blue-400 mt-1">Leverage 1:{accountInfo?.leverage || 0}</p>
        </motion.div>

        {/* Open Positions */}
        <motion.div variants={itemVariants} className="quantum-panel p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-500/20 to-transparent rounded-full -mr-10 -mt-10" />
          <Activity className="w-8 h-8 text-purple-400 mb-3" />
          <p className="text-sm text-gray-400">Open Positions</p>
          <p className="text-2xl font-bold text-white">{positions.length}</p>
          <p className={`text-xs mt-1 ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            Total P&L: ${totalProfit.toFixed(2)}
          </p>
        </motion.div>

        {/* Connection Status */}
        <motion.div variants={itemVariants} className="quantum-panel p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-quantum-accent/20 to-transparent rounded-full -mr-10 -mt-10" />
          <div className="flex items-center gap-2 mb-3">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            <Zap className="w-6 h-6 text-quantum-accent" />
          </div>
          <p className="text-sm text-gray-400">MT5 Status</p>
          <p className="text-lg font-bold text-white">{accountInfo?.server || 'Connecting...'}</p>
          <p className="text-xs text-green-400 mt-1">Live Connected</p>
        </motion.div>
      </motion.div>

      {/* Market Overview Panel */}
      <motion.div
        variants={itemVariants}
        className="quantum-panel p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-quantum-primary" />
            Market Overview - Live Data
          </h3>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-green-400">Live</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {marketData.map((data, index) => (
            <motion.div
              key={data.symbol}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gradient-to-br from-white/5 to-white/10 p-4 rounded-lg border border-white/10 hover:border-quantum-primary/30 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white">{data.symbol}</span>
                <div className={`flex items-center gap-1 ${data.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {data.changePercent >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  <span className="text-xs">{data.changePercent.toFixed(2)}%</span>
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Bid:</span>
                  <span className="text-red-400 font-mono">{data.bid.toFixed(5)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Ask:</span>
                  <span className="text-green-400 font-mono">{data.ask.toFixed(5)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Spread:</span>
                  <span className="text-blue-400 font-mono">{data.spread.toFixed(1)}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Advanced Chart Panel */}
        <div className="lg:col-span-8 xl:col-span-9">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-6"
          >

            {/* Advanced Chart Panel */}
            <div className="quantum-panel p-6">
              {/* Chart Controls */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-quantum-primary" />
                    <select
                      value={selectedSymbol}
                      onChange={(e) => setSelectedSymbol(e.target.value)}
                      className="quantum-input min-w-[120px]"
                    >
                      {symbols.map((symbol) => (
                        <option key={symbol} value={symbol}>{symbol}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsLiveMode(!isLiveMode)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                        isLiveMode ? "quantum-button-primary" : "quantum-button"
                      }`}
                    >
                      <div className={`w-2 h-2 rounded-full ${isLiveMode ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                      {isLiveMode ? 'Live' : 'Paused'}
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={fetchAllData}
                      className="quantum-button p-2 rounded-lg"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  {["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"].map((tf) => (
                    <motion.button
                      key={tf}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setSelectedTimeframe(tf)}
                      className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                        selectedTimeframe === tf
                          ? "quantum-button-primary shadow-lg shadow-quantum-primary/30" 
                          : "quantum-button"
                      }`}
                    >
                      {tf}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Chart */}
              <div className="h-[600px] rounded-lg overflow-hidden border border-white/10 relative">
                <TradingViewChart symbol={selectedSymbol} timeframe={selectedTimeframe} height={600} />
                
                {/* Chart Overlay Controls */}
                <div className="absolute top-4 left-4 flex gap-2">
                  <div className="bg-black/50 backdrop-blur-sm px-3 py-1 rounded-lg text-xs text-white">
                    {selectedSymbol} • {selectedTimeframe}
                  </div>
                  {isLiveMode && (
                    <div className="bg-green-500/20 backdrop-blur-sm px-3 py-1 rounded-lg text-xs text-green-400 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                      Live Data
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Positions Panel */}
            <div className="quantum-panel p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-quantum-primary" />
                  Open Positions
                </h3>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={fetchAllData}
                  className="quantum-button p-2 rounded-lg"
                >
                  <RefreshCw className="w-4 h-4" />
                </motion.button>
              </div>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-quantum-primary border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-gray-400 mt-2">Loading positions...</p>
                </div>
              ) : positions.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 mx-auto mb-2 text-gray-500" />
                  <p className="text-gray-400">No open positions</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 border-b border-white/10">
                        <th className="text-left p-3">Symbol</th>
                        <th className="text-left p-3">Ticket</th>
                        <th className="text-left p-3">Type</th>
                        <th className="text-left p-3">Volume</th>
                        <th className="text-left p-3">Open Price</th>
                        <th className="text-left p-3">S/L</th>
                        <th className="text-left p-3">T/P</th>
                        <th className="text-left p-3">Profit</th>
                        <th className="text-left p-3">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {positions.map((pos, index) => (
                        <motion.tr 
                          key={pos.ticket}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="border-b border-white/5 hover:bg-white/5 transition-colors"
                        >
                          <td className="p-3 text-white font-medium">{pos.symbol}</td>
                          <td className="p-3 text-gray-400">#{pos.ticket}</td>
                          <td className="p-3">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              pos.type === "buy"
                                ? "bg-green-500/20 text-green-400 border border-green-500/30" 
                                : "bg-red-500/20 text-red-400 border border-red-500/30"
                            }`}>
                              {pos.type?.toUpperCase()}
                            </span>
                          </td>
                          <td className="p-3 text-white">{pos.volume}</td>
                          <td className="p-3 text-white font-mono">{pos.open_price?.toFixed(5) || 'N/A'}</td>
                          <td className="p-3 text-gray-400 font-mono">{pos.sl?.toFixed(5) || '---'}</td>
                          <td className="p-3 text-gray-400 font-mono">{pos.tp?.toFixed(5) || '---'}</td>
                          <td className={`p-3 font-medium ${
                            pos.profit >= 0 ? "text-green-400" : "text-red-400"
                          }`}>
                            ${pos.profit?.toFixed(2) || '0.00'}
                          </td>
                          <td className="p-3">
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => closePosition(pos.ticket)}
                              className="quantum-button-danger px-3 py-1 rounded text-xs font-medium"
                            >
                              <X className="w-3 h-3 inline mr-1" />
                              Close
                            </motion.button>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                    {positions.length > 0 && (
                      <tfoot>
                        <tr className="border-t border-white/20">
                          <td colSpan={5} className="py-3 text-right text-gray-400 font-medium">Total P&L:</td>
                          <td className={`py-3 font-bold text-lg ${
                            totalProfit >= 0 ? "text-green-400" : "text-red-400"
                          }`}>
                            ${totalProfit.toFixed(2)}
                          </td>
                          <td></td>
                        </tr>
                      </tfoot>
                    )}
                  </table>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Advanced Quantum Order Panel */}
        <div className="lg:col-span-4 xl:col-span-3">
          <div className="space-y-6">
            {/* Main Order Panel */}
            <div className="quantum-panel p-6 sticky top-24">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-quantum-primary" />
                  AI Order Engine
                </h3>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-quantum-primary rounded-full animate-pulse" />
                  <span className="text-xs text-quantum-primary">Active</span>
                </div>
              </div>

              {/* Risk Management Panel */}
              <div className="mb-6 p-4 bg-gradient-to-r from-quantum-accent/10 to-purple-500/10 rounded-lg border border-quantum-accent/20">
                <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-quantum-accent" />
                  Risk Management
                </h4>
                <div className="grid grid-cols-3 gap-2 mb-3">
                  {(["LOW", "MEDIUM", "HIGH"] as const).map((level) => (
                    <motion.button
                      key={level}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setRiskLevel(level)}
                      className={`py-2 px-3 rounded text-xs font-medium transition-all ${
                        riskLevel === level
                          ? level === "LOW" ? "bg-green-500/20 text-green-400 border border-green-500/30"
                          : level === "MEDIUM" ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                          : "bg-white/5 text-gray-400 border border-white/10"
                      }`}
                    >
                      {level}
                    </motion.button>
                  ))}
                </div>
                
                {/* Position Sizing */}
                <div className="mb-3">
                  <label className="block text-xs text-gray-400 mb-2">Position Sizing</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(["FIXED", "PERCENT", "RISK"] as const).map((type) => (
                      <motion.button
                        key={type}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setOrderSize(type)}
                        className={`py-2 px-2 rounded text-xs font-medium transition-all ${
                          orderSize === type
                            ? "bg-quantum-primary/20 text-quantum-primary border border-quantum-primary/30"
                            : "bg-white/5 text-gray-400 border border-white/10"
                        }`}
                      >
                        {type}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Auto Features */}
                <div className="space-y-2">
                  <label className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Auto Stop Loss</span>
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setAutoSL(!autoSL)}
                      className={`w-10 h-5 rounded-full transition-all ${
                        autoSL ? 'bg-quantum-primary' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 bg-white rounded-full transition-all ${
                        autoSL ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </motion.button>
                  </label>
                  
                  <label className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Auto Take Profit</span>
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setAutoTP(!autoTP)}
                      className={`w-10 h-5 rounded-full transition-all ${
                        autoTP ? 'bg-quantum-primary' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 bg-white rounded-full transition-all ${
                        autoTP ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </motion.button>
                  </label>

                  <label className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Trailing Stop</span>
                    <motion.button
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setTrailingStop(!trailingStop)}
                      className={`w-10 h-5 rounded-full transition-all ${
                        trailingStop ? 'bg-quantum-primary' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 bg-white rounded-full transition-all ${
                        trailingStop ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </motion.button>
                  </label>
                </div>
              </div>

            {/* Order Type Buttons */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setOrderType("BUY")}
                className={`py-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  orderType === "BUY"
                    ? "quantum-button-primary shadow-lg shadow-green-500/30"
                    : "quantum-button"
                }`}
              >
                <TrendingUp className="w-5 h-5" />
                BUY
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setOrderType("SELL")}
                className={`py-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  orderType === "SELL"
                    ? "quantum-button-danger shadow-lg shadow-red-500/30"
                    : "quantum-button"
                }`}
              >
                <TrendingDown className="w-5 h-5" />
                SELL
              </motion.button>
            </div>

            {/* Volume Input */}
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Volume (Lots)
              </label>
              <input
                type="number"
                value={volume}
                onChange={(e) => setVolume(e.target.value)}
                step="0.01"
                min="0.01"
                className="quantum-input w-full"
                placeholder="0.01"
              />
            </div>

            {/* Stop Loss */}
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Stop Loss (Optional)
              </label>
              <input
                type="number"
                value={stopLoss}
                onChange={(e) => setStopLoss(e.target.value)}
                step="0.00001"
                className="quantum-input w-full"
                placeholder="0.00000"
              />
            </div>

            {/* Take Profit */}
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2 flex items-center gap-2">
                <Target className="w-4 h-4" />
                Take Profit (Optional)
              </label>
              <input
                type="number"
                value={takeProfit}
                onChange={(e) => setTakeProfit(e.target.value)}
                step="0.00001"
                className="quantum-input w-full"
                placeholder="0.00000"
              />
            </div>

            {/* Comment */}
            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">Comment</label>
              <input
                type="text"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="quantum-input w-full"
                placeholder="Trade comment..."
              />
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02, boxShadow: orderType === "BUY" ? "0 0 30px rgba(0, 255, 136, 0.5)" : "0 0 30px rgba(255, 0, 85, 0.5)" }}
              whileTap={{ scale: 0.98 }}
              onClick={placeOrder}
              className={`w-full py-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                orderType === "BUY"
                  ? "quantum-button-primary"
                  : "quantum-button-danger"
              }`}
            >
              <Send className="w-5 h-5" />
              <span>Execute {orderType} Order</span>
            </motion.button>

            {/* Risk Warning */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-6 p-4 quantum-card border-yellow-500/30"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="text-yellow-500 mt-0.5 flex-shrink-0" size={18} />
                <div>
                  <p className="text-sm text-yellow-400 font-medium mb-1">Risk Warning</p>
                  <p className="text-xs text-yellow-400/80">
                    Trading involves significant risk of loss. Only trade with capital you can afford to lose.
                  </p>
                </div>
              </div>
            </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 