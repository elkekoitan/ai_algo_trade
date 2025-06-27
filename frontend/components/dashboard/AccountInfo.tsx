"use client";

import { useState } from "react";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3,
  RefreshCw,
  ShieldAlert,
  AlertTriangle
} from "lucide-react";
import { useAppContext } from "@/lib/context";

export default function AccountInfo() {
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  // Use our context
  const { accountInfo, isLoading, errors, refreshAccountInfo } = useAppContext();

  if (isLoading.account && !accountInfo) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
        <div className="flex items-center justify-center h-40">
          <RefreshCw className="animate-spin text-gray-400" size={32} />
        </div>
      </div>
    );
  }

  if (errors.account || !accountInfo) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
        <div className="text-center py-8">
          <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-3" />
          <p className="text-red-400 mb-4">{errors.account || "No account data available"}</p>
          <button 
            onClick={refreshAccountInfo}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const profitColor = accountInfo.profit >= 0 ? "text-green-400" : "text-red-400";
  const profitIcon = accountInfo.profit >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />;
  
  // Calculate margin used percent if not available
  const marginUsedPercent = accountInfo.margin > 0 && accountInfo.equity > 0
    ? (accountInfo.margin / accountInfo.equity) * 100
    : 0;

  return (
    <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Account Overview</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-400">
          <RefreshCw 
            size={14} 
            className={isLoading.account ? "animate-spin" : ""} 
            onClick={refreshAccountInfo}
            style={{ cursor: 'pointer' }}
          />
          <span>Updated {new Date().toLocaleTimeString()}</span>
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
            {accountInfo?.currency || 'USD'} {accountInfo?.balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </div>

        {/* Equity */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Equity</span>
            <BarChart3 size={16} className="text-gray-400" />
          </div>
          <p className="text-2xl font-semibold text-white">
            {accountInfo?.currency || 'USD'} {accountInfo?.equity?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </div>

        {/* Profit */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Floating P&L</span>
            {profitIcon}
          </div>
          <p className={`text-2xl font-semibold ${profitColor}`}>
            {accountInfo.profit >= 0 ? '+' : ''}{accountInfo?.currency || 'USD'} {accountInfo?.profit?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </div>

        {/* Margin */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Used Margin</span>
            <span className="text-xs text-gray-500">{marginUsedPercent?.toFixed(1) || '0.0'}%</span>
          </div>
          <p className="text-lg font-medium text-white">
            {accountInfo?.currency || 'USD'} {accountInfo?.margin?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </div>

        {/* Free Margin */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Free Margin</span>
          </div>
          <p className="text-lg font-medium text-white">
            {accountInfo?.currency || 'USD'} {accountInfo?.free_margin?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </div>

        {/* Leverage */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Leverage</span>
          </div>
          <p className="text-lg font-medium text-white">1:{accountInfo.leverage}</p>
        </div>
      </div>

      {/* Server Info */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            Account: #{accountInfo?.login || '...'} • {accountInfo?.server || '...'}
          </span>
          <span className="text-gray-500">{accountInfo?.company || '...'}</span>
        </div>
      </div>
    </div>
  );
} 