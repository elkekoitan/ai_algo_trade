"use client";

import { useState, useEffect } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3,
  RefreshCw
} from "lucide-react";

interface AccountData {
  login: number;
  balance: number;
  equity: number;
  margin: number;
  margin_free: number;
  margin_level: number;
  profit: number;
  leverage: number;
  currency: string;
  server: string;
  company: string;
  margin_used_percent: number;
}

export default function AccountInfo() {
  const [accountData, setAccountData] = useState<AccountData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    fetchAccountInfo();
    const interval = setInterval(fetchAccountInfo, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAccountInfo = async () => {
    try {
      const response = await fetch("http://localhost:8001/api/v1/trading/account_info");
      if (response.ok) {
        const data = await response.json();
        setAccountData(data);
        setError(null);
        setLastUpdate(new Date());
      } else {
        setError("Failed to fetch account data");
      }
    } catch (err) {
      setError("Connection error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
        <div className="flex items-center justify-center h-40">
          <RefreshCw className="animate-spin text-gray-400" size={32} />
        </div>
      </div>
    );
  }

  if (error || !accountData) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
        <div className="text-center">
          <p className="text-red-400">{error || "No account data available"}</p>
          <button 
            onClick={fetchAccountInfo}
            className="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const profitColor = accountData.profit >= 0 ? "text-green-400" : "text-red-400";
  const profitIcon = accountData.profit >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />;

  return (
    <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Account Overview</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-400">
          <RefreshCw size={14} />
          <span>Updated {lastUpdate.toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Account Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Balance */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Balance</span>
            <DollarSign size={16} className="text-gray-400" />
          </div>
          <p className="text-2xl font-semibold text-white">
            {accountData.currency} {accountData.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Equity */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Equity</span>
            <BarChart3 size={16} className="text-gray-400" />
          </div>
          <p className="text-2xl font-semibold text-white">
            {accountData.currency} {accountData.equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Profit */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Floating P&L</span>
            {profitIcon}
          </div>
          <p className={`text-2xl font-semibold ${profitColor}`}>
            {accountData.profit >= 0 ? '+' : ''}{accountData.currency} {accountData.profit.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Margin */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Used Margin</span>
            <span className="text-xs text-gray-500">{accountData.margin_used_percent.toFixed(1)}%</span>
          </div>
          <p className="text-lg font-medium text-white">
            {accountData.currency} {accountData.margin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Free Margin */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Free Margin</span>
          </div>
          <p className="text-lg font-medium text-white">
            {accountData.currency} {accountData.margin_free.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {/* Leverage */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Leverage</span>
          </div>
          <p className="text-lg font-medium text-white">1:{accountData.leverage}</p>
        </div>
      </div>

      {/* Server Info */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            Account: #{accountData.login} • {accountData.server}
          </span>
          <span className="text-gray-500">{accountData.company}</span>
        </div>
      </div>
    </div>
  );
} 