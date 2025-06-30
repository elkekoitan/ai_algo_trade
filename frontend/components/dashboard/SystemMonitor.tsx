'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  Cpu, 
  MemoryStick, 
  Clock, 
  Zap, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

interface SystemMetrics {
  system: {
    cpu_usage: number;
    memory_usage_mb: number;
    uptime_seconds: number;
    threads: number;
  };
  trading_engine: {
    running: boolean;
    mt5_connected: boolean;
    weekend_mode: boolean;
    active_modules: Record<string, boolean>;
  };
  trading_metrics: Record<string, any>;
  account?: {
    balance: number;
    equity: number;
    profit: number;
    margin_level: number;
  };
  market?: {
    active_symbols: number;
    weekend_mode: boolean;
  };
  timestamp: string;
}

const formatUptime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

const StatusIndicator = ({ active, label }: { active: boolean; label: string }) => (
  <div className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
    <span className="text-sm text-gray-300">{label}</span>
    <div className="flex items-center space-x-1">
      {active ? (
        <CheckCircle className="h-4 w-4 text-green-400" />
      ) : (
        <XCircle className="h-4 w-4 text-red-400" />
      )}
      <span className={`text-xs font-medium ${active ? 'text-green-400' : 'text-red-400'}`}>
        {active ? 'Active' : 'Inactive'}
      </span>
    </div>
  </div>
);

export default function SystemMonitor() {
  const { data: performanceData, error } = useSWR<SystemMetrics>(
    'http://localhost:8002/performance', 
    fetcher, 
    { 
      refreshInterval: 5000,
      errorRetryCount: 3,
      errorRetryInterval: 2000
    }
  );

  if (error) {
    return (
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="h-5 w-5" />
            System Monitor - Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-400 text-sm">Failed to load performance data</p>
          <p className="text-gray-500 text-xs mt-1">Check backend connection</p>
        </CardContent>
      </Card>
    );
  }

  if (!performanceData) {
    return (
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-400 animate-pulse" />
            System Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <Activity className="h-8 w-8 animate-pulse text-cyan-400" />
            <span className="ml-3 text-gray-400">Loading performance data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const cpuColor = performanceData.system.cpu_usage > 80 ? 'text-red-400' : 
                   performanceData.system.cpu_usage > 50 ? 'text-yellow-400' : 'text-green-400';
  
  const memoryColor = performanceData.system.memory_usage_mb > 1000 ? 'text-red-400' : 
                     performanceData.system.memory_usage_mb > 500 ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="space-y-4">
      {/* System Resources */}
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-400" />
            System Performance
            <Badge className="bg-green-500/20 text-green-400 text-xs">
              Live
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Cpu className="h-4 w-4 text-gray-400" />
              </div>
              <p className="text-xs text-gray-400">CPU Usage</p>
              <p className={`font-bold ${cpuColor}`}>
                {performanceData.system.cpu_usage.toFixed(1)}%
              </p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <MemoryStick className="h-4 w-4 text-gray-400" />
              </div>
              <p className="text-xs text-gray-400">Memory</p>
              <p className={`font-bold ${memoryColor}`}>
                {performanceData.system.memory_usage_mb.toFixed(0)} MB
              </p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Clock className="h-4 w-4 text-gray-400" />
              </div>
              <p className="text-xs text-gray-400">Uptime</p>
              <p className="font-bold text-white">
                {formatUptime(performanceData.system.uptime_seconds)}
              </p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Zap className="h-4 w-4 text-gray-400" />
              </div>
              <p className="text-xs text-gray-400">Threads</p>
              <p className="font-bold text-white">
                {performanceData.system.threads}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trading Engine Status */}
      <Card className="bg-gray-900/50 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-emerald-400" />
            Trading Engine
            {performanceData.trading_engine.weekend_mode && (
              <Badge className="bg-orange-500/20 text-orange-400 text-xs">
                Weekend Mode
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <StatusIndicator 
              active={performanceData.trading_engine.running} 
              label="Engine Running" 
            />
            <StatusIndicator 
              active={performanceData.trading_engine.mt5_connected} 
              label="MT5 Connected" 
            />
            
            {/* Module Status */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Active Modules:</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(performanceData.trading_engine.active_modules).map(([module, active]) => (
                  <StatusIndicator 
                    key={module}
                    active={active as boolean} 
                    label={module.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} 
                  />
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account & Market Info */}
      {(performanceData.account || performanceData.market) && (
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-400" />
              Trading Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {performanceData.account && (
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-xs text-gray-400">Balance</p>
                  <p className="font-bold text-white">
                    ${performanceData.account.balance.toLocaleString()}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Equity</p>
                  <p className="font-bold text-white">
                    ${performanceData.account.equity.toLocaleString()}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Profit</p>
                  <p className={`font-bold ${performanceData.account.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${performanceData.account.profit.toFixed(2)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Margin Level</p>
                  <p className="font-bold text-white">
                    {performanceData.account.margin_level.toFixed(0)}%
                  </p>
                </div>
              </div>
            )}
            
            {performanceData.market && (
              <div className="text-center p-3 bg-gray-800/30 rounded">
                <p className="text-xs text-gray-400">Active Symbols</p>
                <p className="font-bold text-cyan-400 text-lg">
                  {performanceData.market.active_symbols}
                </p>
                <p className="text-xs text-gray-500">
                  {performanceData.market.weekend_mode ? 'Crypto only' : 'All markets'}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Last Update */}
      <div className="text-center">
        <p className="text-xs text-gray-500">
          Last updated: {new Date(performanceData.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
} 