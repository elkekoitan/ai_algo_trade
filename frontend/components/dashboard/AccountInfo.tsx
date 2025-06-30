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
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function AccountInfo() {
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  // Get market status which includes account info
  const { data: statusData, error, mutate } = useSWR(API_ENDPOINTS.status, fetcher, { refreshInterval: 5000 });

  if (error) {
    return (
      <Card className="bg-gray-900/50 backdrop-blur-lg border-gray-800">
        <CardContent className="p-6">
          <div className="text-center py-8">
            <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-3" />
            <p className="text-red-400 mb-4">Failed to load account info</p>
            <button 
              onClick={() => mutate()}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium transition-colors"
            >
              Retry Connection
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!statusData) {
    return (
      <Card className="bg-gray-900/50 backdrop-blur-lg border-gray-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-40">
            <RefreshCw className="animate-spin text-gray-400" size={32} />
          </div>
        </CardContent>
      </Card>
    );
  }

  const accountData = statusData?.account || {};
  const isConnected = statusData?.mt5_connected || false;
  const weekendMode = statusData?.weekend_mode || false;

  if (!isConnected) {
    return (
      <Card className="bg-gray-900/50 backdrop-blur-lg border-gray-800">
        <CardContent className="p-6">
          <div className="text-center py-8">
            <ShieldAlert className="mx-auto h-12 w-12 text-red-500 mb-3" />
            <p className="text-red-400 mb-2">MT5 Not Connected</p>
            <p className="text-gray-400 text-sm">Please check your connection</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const profit = accountData.equity - accountData.balance || 0;
  const profitColor = profit >= 0 ? "text-green-400" : "text-red-400";
  const profitIcon = profit >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />;

  return (
    <div className="space-y-4">
      <Card className="bg-gray-900/50 backdrop-blur-lg border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-white">Account Balance</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-white">
            ${accountData.balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </div>
          <p className="text-xs text-gray-400">
            Equity: ${accountData.equity?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </p>
        </CardContent>
      </Card>

      {weekendMode && (
        <Card className="bg-amber-900/20 backdrop-blur-lg border-amber-800">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4 text-amber-400" />
              <span className="text-amber-400 text-sm font-medium">Weekend Crypto Mode</span>
            </div>
            <p className="text-amber-300 text-xs mt-1">
              Only crypto instruments are active during weekends
            </p>
          </CardContent>
        </Card>
      )}

      <Card className="bg-gray-900/50 backdrop-blur-lg border-gray-800">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">Account: {accountData.login}</span>
            <span className="text-gray-400 text-sm">{accountData.server}</span>
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-gray-400 text-sm">Currency: {accountData.currency}</span>
            <div className={`flex items-center space-x-1 ${profitColor}`}>
              {profitIcon}
              <span className="text-sm font-medium">
                ${Math.abs(profit).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 