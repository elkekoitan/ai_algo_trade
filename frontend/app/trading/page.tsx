"use client";

import { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import TradingViewChart from "@/components/charts/TradingViewChart";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  AlertCircle,
  Send
} from "lucide-react";

interface Position {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  price: number;
  sl: number;
  tp: number;
  profit: number;
  swap: number;
  commission: number;
  magic: number;
  comment: string;
  time: string;
}

export default function TradingPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("EURUSD");
  const [selectedTimeframe, setSelectedTimeframe] = useState("H1");
  const [positions, setPositions] = useState<Position[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Order form state
  const [orderType, setOrderType] = useState<"BUY" | "SELL">("BUY");
  const [volume, setVolume] = useState("0.01");
  const [stopLoss, setStopLoss] = useState("");
  const [takeProfit, setTakeProfit] = useState("");
  const [comment, setComment] = useState("ICT Ultra v2");

  useEffect(() => {
    fetchSymbols();
    fetchPositions();
    const interval = setInterval(fetchPositions, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSymbols = async () => {
    try {
      const response = await fetch("http://localhost:8001/api/v1/market/symbols");
      if (response.ok) {
        const data = await response.json();
        setSymbols(data);
      }
    } catch (error) {
      console.error("Error fetching symbols:", error);
    }
  };

  const fetchPositions = async () => {
    try {
      const response = await fetch("http://localhost:8001/api/v1/trading/positions");
      if (response.ok) {
        const data = await response.json();
        setPositions(data);
      }
    } catch (error) {
      console.error("Error fetching positions:", error);
    } finally {
      setLoading(false);
    }
  };

  const placeOrder = async () => {
    try {
      const response = await fetch("http://localhost:8001/api/v1/trading/place_order", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: selectedSymbol,
          order_type: orderType,
          volume: parseFloat(volume),
          sl: stopLoss ? parseFloat(stopLoss) : null,
          tp: takeProfit ? parseFloat(takeProfit) : null,
          comment: comment,
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`Order placed successfully! Order ID: ${result.order_id}`);
        // Reset form
        setVolume("0.01");
        setStopLoss("");
        setTakeProfit("");
        // Refresh positions
        fetchPositions();
      } else {
        alert(`Order failed: ${result.message}`);
      }
    } catch (error) {
      alert("Error placing order");
      console.error("Error placing order:", error);
    }
  };

  const closePosition = async (ticket: number) => {
    if (!confirm(`Are you sure you want to close position #${ticket}?`)) return;

    try {
      const response = await fetch(`http://localhost:8001/api/v1/trading/close_position/${ticket}`, {
        method: "POST",
      });

      const result = await response.json();
      
      if (result.success) {
        alert("Position closed successfully!");
        fetchPositions();
      } else {
        alert(`Failed to close position: ${result.message}`);
      }
    } catch (error) {
      alert("Error closing position");
      console.error("Error closing position:", error);
    }
  };

  const totalProfit = positions.reduce((sum, pos) => sum + pos.profit, 0);

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-950 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Trading Terminal</h1>
            <p className="text-gray-400">Execute trades and manage positions</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chart Section */}
            <div className="lg:col-span-2">
              <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
                {/* Symbol and Timeframe Selector */}
                <div className="flex items-center justify-between mb-4">
                  <select
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                    className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  >
                    {symbols.map((symbol) => (
                      <option key={symbol} value={symbol}>{symbol}</option>
                    ))}
                  </select>
                  
                  <div className="flex space-x-2">
                    {["M5", "M15", "M30", "H1", "H4", "D1"].map((tf) => (
                      <button
                        key={tf}
                        onClick={() => setSelectedTimeframe(tf)}
                        className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                          selectedTimeframe === tf
                            ? "bg-emerald-600 text-white"
                            : "bg-gray-800 text-gray-400 hover:text-white"
                        }`}
                      >
                        {tf}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Chart */}
                <div className="h-[500px]">
                  <TradingViewChart symbol={selectedSymbol} interval={selectedTimeframe} />
                </div>
              </div>

              {/* Open Positions */}
              <div className="mt-6 bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold text-white mb-4">Open Positions</h3>
                
                {positions.length === 0 ? (
                  <p className="text-gray-400 text-center py-8">No open positions</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-gray-400 border-b border-gray-800">
                          <th className="text-left py-2">Ticket</th>
                          <th className="text-left py-2">Symbol</th>
                          <th className="text-left py-2">Type</th>
                          <th className="text-left py-2">Volume</th>
                          <th className="text-left py-2">Price</th>
                          <th className="text-left py-2">Profit</th>
                          <th className="text-left py-2">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {positions.map((pos) => (
                          <tr key={pos.ticket} className="border-b border-gray-800/50">
                            <td className="py-3 text-white">#{pos.ticket}</td>
                            <td className="py-3 text-white">{pos.symbol}</td>
                            <td className="py-3">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                pos.type === "BUY" 
                                  ? "bg-green-500/20 text-green-400" 
                                  : "bg-red-500/20 text-red-400"
                              }`}>
                                {pos.type}
                              </span>
                            </td>
                            <td className="py-3 text-white">{pos.volume}</td>
                            <td className="py-3 text-white">{pos.price.toFixed(5)}</td>
                            <td className={`py-3 font-medium ${
                              pos.profit >= 0 ? "text-green-400" : "text-red-400"
                            }`}>
                              ${pos.profit.toFixed(2)}
                            </td>
                            <td className="py-3">
                              <button
                                onClick={() => closePosition(pos.ticket)}
                                className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-white text-xs font-medium transition-colors"
                              >
                                Close
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr className="border-t border-gray-700">
                          <td colSpan={5} className="py-3 text-right text-gray-400">Total:</td>
                          <td className={`py-3 font-semibold ${
                            totalProfit >= 0 ? "text-green-400" : "text-red-400"
                          }`}>
                            ${totalProfit.toFixed(2)}
                          </td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Order Panel */}
            <div className="lg:col-span-1">
              <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 sticky top-24">
                <h3 className="text-lg font-semibold text-white mb-4">Place Order</h3>

                {/* Order Type */}
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <button
                    onClick={() => setOrderType("BUY")}
                    className={`py-3 rounded-lg font-medium transition-all ${
                      orderType === "BUY"
                        ? "bg-green-600 text-white"
                        : "bg-gray-800 text-gray-400 hover:text-white"
                    }`}
                  >
                    <TrendingUp className="inline mr-2" size={18} />
                    BUY
                  </button>
                  <button
                    onClick={() => setOrderType("SELL")}
                    className={`py-3 rounded-lg font-medium transition-all ${
                      orderType === "SELL"
                        ? "bg-red-600 text-white"
                        : "bg-gray-800 text-gray-400 hover:text-white"
                    }`}
                  >
                    <TrendingDown className="inline mr-2" size={18} />
                    SELL
                  </button>
                </div>

                {/* Volume */}
                <div className="mb-4">
                  <label className="block text-sm text-gray-400 mb-2">Volume (Lots)</label>
                  <input
                    type="number"
                    value={volume}
                    onChange={(e) => setVolume(e.target.value)}
                    step="0.01"
                    min="0.01"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                {/* Stop Loss */}
                <div className="mb-4">
                  <label className="block text-sm text-gray-400 mb-2">Stop Loss (Optional)</label>
                  <input
                    type="number"
                    value={stopLoss}
                    onChange={(e) => setStopLoss(e.target.value)}
                    step="0.00001"
                    placeholder="0.00000"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                {/* Take Profit */}
                <div className="mb-4">
                  <label className="block text-sm text-gray-400 mb-2">Take Profit (Optional)</label>
                  <input
                    type="number"
                    value={takeProfit}
                    onChange={(e) => setTakeProfit(e.target.value)}
                    step="0.00001"
                    placeholder="0.00000"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                {/* Comment */}
                <div className="mb-6">
                  <label className="block text-sm text-gray-400 mb-2">Comment</label>
                  <input
                    type="text"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                {/* Submit Button */}
                <button
                  onClick={placeOrder}
                  className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
                    orderType === "BUY"
                      ? "bg-green-600 hover:bg-green-700 text-white"
                      : "bg-red-600 hover:bg-red-700 text-white"
                  }`}
                >
                  <Send size={18} />
                  <span>Place {orderType} Order</span>
                </button>

                {/* Risk Warning */}
                <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-800/50 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="text-yellow-500 mt-0.5" size={16} />
                    <p className="text-xs text-yellow-400">
                      Trading involves significant risk. Always use proper risk management.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
} 