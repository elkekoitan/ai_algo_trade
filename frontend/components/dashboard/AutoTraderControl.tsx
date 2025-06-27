"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Pause, 
  Square, 
  Settings, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  DollarSign,
  Target,
  Clock
} from 'lucide-react';

interface TradingStrategy {
  name: string;
  description: string;
  signal_types: string[];
  min_score: number;
  max_risk_per_trade: number;
  max_daily_trades: number;
  trading_hours: {
    start: string;
    end: string;
  };
  symbols: string[];
  timeframes: string[];
  parameters: Record<string, any>;
}

interface TradingSession {
  session_id: string;
  strategy_name: string;
  status: string;
  created_at: string;
  started_at?: string;
  stopped_at?: string;
  duration_minutes?: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  signals_processed: number;
  is_running: boolean;
  is_paused: boolean;
}

interface AutoTraderStatus {
  is_running: boolean;
  active_sessions: number;
  total_sessions: number;
  total_profit: number;
  total_trades: number;
  mt5_connected: boolean;
  sessions: TradingSession[];
}

const AutoTraderControl: React.FC = () => {
  const [status, setStatus] = useState<AutoTraderStatus | null>(null);
  const [strategies, setStrategies] = useState<TradingStrategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Configuration state
  const [config, setConfig] = useState({
    signal_check_interval: 30,
    max_concurrent_trades: 5,
    emergency_stop_loss: 1000,
    notification_enabled: true
  });

  const availableSymbols = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 
    'USDCHF', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'BTCUSD'
  ];

  useEffect(() => {
    fetchStatus();
    fetchStrategies();
    
    // Set up real-time updates
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/v1/auto-trader/status');
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  const fetchStrategies = async () => {
    try {
      const response = await fetch('/api/v1/auto-trader/strategies');
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array before setting it
        if (Array.isArray(data)) {
          setStrategies(data);
          if (data.length > 0 && !selectedStrategy) {
            setSelectedStrategy(data[0].name);
          }
        } else {
          console.warn("Strategies data is not an array:", data);
          setStrategies([]); // Set to empty array on unexpected format
        }
      } else {
        setStrategies([]); // Also clear on error response
      }
    } catch (err) {
      console.error('Error fetching strategies:', err);
      setStrategies([]); // Also clear on fetch error
    }
  };

  const startTrading = async () => {
    if (!selectedStrategy) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/auto-trader/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_name: selectedStrategy,
          symbols: selectedSymbols.length > 0 ? selectedSymbols : undefined,
          config: config
        }),
      });

      const data = await response.json();

      if (data.success) {
        await fetchStatus();
      } else {
        setError(data.message || 'Failed to start trading');
      }
    } catch (err) {
      setError('Error starting trading session');
    } finally {
      setIsLoading(false);
    }
  };

  const stopSession = async (sessionId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/auto-trader/stop/${sessionId}`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        await fetchStatus();
      } else {
        setError(data.message || 'Failed to stop session');
      }
    } catch (err) {
      setError('Error stopping session');
    } finally {
      setIsLoading(false);
    }
  };

  const pauseSession = async (sessionId: string) => {
    try {
      await fetch(`/api/v1/auto-trader/pause/${sessionId}`, {
        method: 'POST',
      });
      await fetchStatus();
    } catch (err) {
      setError('Error pausing session');
    }
  };

  const resumeSession = async (sessionId: string) => {
    try {
      await fetch(`/api/v1/auto-trader/resume/${sessionId}`, {
        method: 'POST',
      });
      await fetchStatus();
    } catch (err) {
      setError('Error resuming session');
    }
  };

  const emergencyStopAll = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/auto-trader/emergency-stop', {
        method: 'POST',
      });

      const data = await response.json();
      if (data.success) {
        await fetchStatus();
      }
    } catch (err) {
      setError('Error executing emergency stop');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (session: TradingSession) => {
    if (!session.is_running) return 'bg-gray-500';
    if (session.is_paused) return 'bg-yellow-500';
    if (session.total_profit > 0) return 'bg-green-500';
    if (session.total_profit < 0) return 'bg-red-500';
    return 'bg-blue-500';
  };

  const getStatusText = (session: TradingSession) => {
    if (!session.is_running) return 'Stopped';
    if (session.is_paused) return 'Paused';
    return 'Running';
  };

  const formatDuration = (minutes?: number) => {
    if (!minutes) return '0m';
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            AutoTrader Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {status?.active_sessions || 0}
              </div>
              <div className="text-sm text-gray-600">Active Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(status?.total_profit || 0)}
              </div>
              <div className="text-sm text-gray-600">Total Profit</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {status?.total_trades || 0}
              </div>
              <div className="text-sm text-gray-600">Total Trades</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2">
                {status?.mt5_connected ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-sm">
                  {status?.mt5_connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Start New Session */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="h-5 w-5" />
            Start New Trading Session
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 bg-red-100 border border-red-300 text-red-700 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Strategy</label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Strategy</option>
              {strategies.map((strategy) => (
                <option key={strategy.name} value={strategy.name}>
                  {strategy.name} - {strategy.description}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Symbols (optional - leave empty for strategy defaults)
            </label>
            <div className="grid grid-cols-5 gap-2">
              {availableSymbols.map((symbol) => (
                <label key={symbol} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedSymbols.includes(symbol)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedSymbols([...selectedSymbols, symbol]);
                      } else {
                        setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">{symbol}</span>
                </label>
              ))}
            </div>
          </div>

          {showSettings && (
            <div className="border rounded p-4 space-y-3">
              <h4 className="font-medium">Advanced Settings</h4>
              
              <div>
                <label className="block text-sm font-medium mb-1">
                  Signal Check Interval (seconds)
                </label>
                <input
                  type="number"
                  value={config.signal_check_interval}
                  onChange={(e) => setConfig({
                    ...config,
                    signal_check_interval: parseInt(e.target.value)
                  })}
                  className="w-full p-2 border rounded"
                  min="10"
                  max="300"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Max Concurrent Trades
                </label>
                <input
                  type="number"
                  value={config.max_concurrent_trades}
                  onChange={(e) => setConfig({
                    ...config,
                    max_concurrent_trades: parseInt(e.target.value)
                  })}
                  className="w-full p-2 border rounded"
                  min="1"
                  max="20"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Emergency Stop Loss ($)
                </label>
                <input
                  type="number"
                  value={config.emergency_stop_loss}
                  onChange={(e) => setConfig({
                    ...config,
                    emergency_stop_loss: parseInt(e.target.value)
                  })}
                  className="w-full p-2 border rounded"
                  min="100"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.notification_enabled}
                    onChange={(e) => setConfig({
                      ...config,
                      notification_enabled: e.target.checked
                    })}
                    className="rounded"
                  />
                  <span className="text-sm">Enable Notifications</span>
                </label>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={startTrading}
              disabled={!selectedStrategy || isLoading}
              className="flex-1"
            >
              {isLoading ? 'Starting...' : 'Start Trading'}
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Active Sessions */}
      {status?.sessions && status.sessions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Active Sessions
              </span>
              <Button
                variant="destructive"
                size="sm"
                onClick={emergencyStopAll}
                disabled={isLoading}
              >
                <AlertTriangle className="h-4 w-4 mr-1" />
                Emergency Stop All
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {status.sessions.map((session) => (
                <div
                  key={session.session_id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge className={getStatusColor(session)}>
                        {getStatusText(session)}
                      </Badge>
                      <h4 className="font-medium">{session.strategy_name}</h4>
                      <span className="text-sm text-gray-500">
                        ID: {session.session_id.substring(0, 8)}...
                      </span>
                    </div>
                    
                    <div className="flex gap-2">
                      {session.is_running && !session.is_paused && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => pauseSession(session.session_id)}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      )}
                      
                      {session.is_running && session.is_paused && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => resumeSession(session.session_id)}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => stopSession(session.session_id)}
                      >
                        <Square className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Duration</div>
                      <div className="font-medium flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDuration(session.duration_minutes)}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Profit</div>
                      <div className={`font-medium flex items-center gap-1 ${
                        session.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        <DollarSign className="h-3 w-3" />
                        {formatCurrency(session.total_profit)}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Trades</div>
                      <div className="font-medium">{session.total_trades}</div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Win Rate</div>
                      <div className="font-medium flex items-center gap-1">
                        <Target className="h-3 w-3" />
                        {session.win_rate.toFixed(1)}%
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Wins/Losses</div>
                      <div className="font-medium">
                        <span className="text-green-600">{session.winning_trades}</span>
                        /
                        <span className="text-red-600">{session.losing_trades}</span>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Signals</div>
                      <div className="font-medium">{session.signals_processed}</div>
                    </div>
                  </div>

                  {session.started_at && (
                    <div className="text-xs text-gray-500">
                      Started: {new Date(session.started_at).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Strategy Information */}
      {selectedStrategy && strategies.find(s => s.name === selectedStrategy) && (
        <Card>
          <CardHeader>
            <CardTitle>Strategy Details</CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const strategy = strategies.find(s => s.name === selectedStrategy);
              if (!strategy) return null;

              return (
                <div className="space-y-3">
                  <p className="text-gray-600">{strategy.description}</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Min Score</div>
                      <div className="font-medium">{strategy.min_score}</div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Risk per Trade</div>
                      <div className="font-medium">{(strategy.max_risk_per_trade * 100).toFixed(1)}%</div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Daily Trades</div>
                      <div className="font-medium">{strategy.max_daily_trades}</div>
                    </div>
                    
                    <div>
                      <div className="text-gray-600">Trading Hours</div>
                      <div className="font-medium">
                        {strategy.trading_hours.start} - {strategy.trading_hours.end}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-gray-600 text-sm mb-1">Signal Types</div>
                    <div className="flex gap-2 flex-wrap">
                      {strategy.signal_types.map((type) => (
                        <Badge key={type} variant="secondary">
                          {type.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-gray-600 text-sm mb-1">Symbols</div>
                    <div className="flex gap-2 flex-wrap">
                      {strategy.symbols.map((symbol) => (
                        <Badge key={symbol} variant="outline">
                          {symbol}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-gray-600 text-sm mb-1">Timeframes</div>
                    <div className="flex gap-2 flex-wrap">
                      {strategy.timeframes.map((tf) => (
                        <Badge key={tf} variant="outline">
                          {tf}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })()}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AutoTraderControl; 