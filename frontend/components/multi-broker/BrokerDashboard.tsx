"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Wifi, WifiOff, TrendingUp, TrendingDown, Activity,
  Plus, Settings, BarChart3, Zap, Globe, Shield,
  CheckCircle, XCircle, AlertTriangle, Clock
} from 'lucide-react';

interface Broker {
  broker_id: string;
  name: string;
  type: string;
  status: string;
  is_demo: boolean;
  supports_forex: boolean;
  supports_crypto: boolean;
  supports_stocks: boolean;
  last_connected?: string;
}

interface BrokerConnection {
  broker_id: string;
  status: string;
  connected_at?: string;
  ping_latency?: number;
  account_info?: {
    balance: number;
    equity: number;
    margin: number;
    currency: string;
  };
  statistics?: {
    uptime_percentage: number;
    total_orders: number;
    total_trades: number;
    error_count: number;
  };
}

interface MarketData {
  symbol: string;
  data: {
    [brokerId: string]: {
      bid: number;
      ask: number;
      spread: number;
      timestamp: string;
    };
  };
}

export default function BrokerDashboard() {
  const [brokers, setBrokers] = useState<Broker[]>([]);
  const [connections, setConnections] = useState<{[key: string]: BrokerConnection}>({});
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD');

  useEffect(() => {
    fetchBrokers();
    fetchConnections();
    fetchMarketData();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchConnections();
      fetchMarketData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchBrokers = async () => {
    try {
      const response = await fetch('/api/v1/multi-broker/brokers');
      const data = await response.json();
      setBrokers(data.brokers || []);
    } catch (error) {
      console.error('Failed to fetch brokers:', error);
    }
  };

  const fetchConnections = async () => {
    try {
      const response = await fetch('/api/v1/multi-broker/connections/status');
      const data = await response.json();
      
      // Fetch detailed status for each broker
      const connectionDetails: {[key: string]: BrokerConnection} = {};
      
      for (const brokerId of Object.keys(data.connections)) {
        try {
          const detailResponse = await fetch(`/api/v1/multi-broker/brokers/${brokerId}/status`);
          const detailData = await detailResponse.json();
          connectionDetails[brokerId] = detailData;
        } catch (error) {
          console.error(`Failed to fetch status for ${brokerId}:`, error);
        }
      }
      
      setConnections(connectionDetails);
    } catch (error) {
      console.error('Failed to fetch connections:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketData = async () => {
    try {
      const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD'];
      const marketDataPromises = symbols.map(async (symbol) => {
        const response = await fetch(`/api/v1/multi-broker/market-data/${symbol}`);
        return await response.json();
      });
      
      const results = await Promise.all(marketDataPromises);
      setMarketData(results);
    } catch (error) {
      console.error('Failed to fetch market data:', error);
    }
  };

  const connectBroker = async (brokerId: string) => {
    try {
      await fetch(`/api/v1/multi-broker/brokers/${brokerId}/connect`, {
        method: 'POST'
      });
      fetchConnections();
    } catch (error) {
      console.error('Failed to connect broker:', error);
    }
  };

  const disconnectBroker = async (brokerId: string) => {
    try {
      await fetch(`/api/v1/multi-broker/brokers/${brokerId}/disconnect`, {
        method: 'POST'
      });
      fetchConnections();
    } catch (error) {
      console.error('Failed to disconnect broker:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'connecting':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <WifiOff className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'bg-green-500';
      case 'connecting':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getBrokerTypeIcon = (type: string) => {
    switch (type) {
      case 'mt5':
        return '📊';
      case 'binance':
        return '₿';
      case 'bybit':
        return '🚀';
      case 'interactive_brokers':
        return '🏦';
      case 'oanda':
        return '🌐';
      default:
        return '📈';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                  <div className="h-8 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Multi-Broker Dashboard</h1>
          <p className="text-gray-600">Manage all your trading accounts in one place</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Add Broker</span>
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Brokers</p>
                <p className="text-2xl font-bold">{brokers.length}</p>
              </div>
              <Globe className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Connected</p>
                <p className="text-2xl font-bold text-green-500">
                  {Object.values(connections).filter(c => c.status === 'connected').length}
                </p>
              </div>
              <Wifi className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Balance</p>
                <p className="text-2xl font-bold">
                  ${Object.values(connections).reduce((sum, c) => 
                    sum + (c.account_info?.balance || 0), 0
                  ).toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Latency</p>
                <p className="text-2xl font-bold">
                  {Math.round(Object.values(connections).reduce((sum, c) => 
                    sum + (c.ping_latency || 0), 0) / Object.keys(connections).length || 0
                  )}ms
                </p>
              </div>
              <Zap className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Broker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {brokers.map((broker) => {
          const connection = connections[broker.broker_id];
          const isConnected = connection?.status === 'connected';
          
          return (
            <Card key={broker.broker_id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{getBrokerTypeIcon(broker.type)}</div>
                    <div>
                      <CardTitle className="text-lg">{broker.name}</CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge variant={broker.is_demo ? 'secondary' : 'default'}>
                          {broker.is_demo ? 'Demo' : 'Live'}
                        </Badge>
                        <Badge variant="outline">{broker.type.toUpperCase()}</Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(connection?.status || 'disconnected')}`}></div>
                    {getStatusIcon(connection?.status || 'disconnected')}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Connection Status */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-sm">Status</p>
                    <p className="text-xs text-gray-600 capitalize">
                      {connection?.status || 'Disconnected'}
                    </p>
                  </div>
                  
                  {connection?.ping_latency && (
                    <div className="text-right">
                      <p className="font-semibold text-sm">{connection.ping_latency}ms</p>
                      <p className="text-xs text-gray-600">Latency</p>
                    </div>
                  )}
                </div>

                {/* Account Info */}
                {connection?.account_info && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-600">Balance</p>
                      <p className="font-semibold">
                        ${connection.account_info.balance.toLocaleString()} {connection.account_info.currency}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Equity</p>
                      <p className="font-semibold">
                        ${connection.account_info.equity.toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}

                {/* Supported Assets */}
                <div>
                  <p className="text-xs text-gray-600 mb-2">Supported Assets</p>
                  <div className="flex flex-wrap gap-1">
                    {broker.supports_forex && <Badge variant="outline" className="text-xs">Forex</Badge>}
                    {broker.supports_crypto && <Badge variant="outline" className="text-xs">Crypto</Badge>}
                    {broker.supports_stocks && <Badge variant="outline" className="text-xs">Stocks</Badge>}
                  </div>
                </div>

                {/* Statistics */}
                {connection?.statistics && (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Uptime</p>
                      <p className="font-semibold">{connection.statistics.uptime_percentage.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Orders</p>
                      <p className="font-semibold">{connection.statistics.total_orders}</p>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-2 pt-2">
                  {isConnected ? (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => disconnectBroker(broker.broker_id)}
                      className="flex-1"
                    >
                      <WifiOff className="w-4 h-4 mr-2" />
                      Disconnect
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => connectBroker(broker.broker_id)}
                      className="flex-1"
                    >
                      <Wifi className="w-4 h-4 mr-2" />
                      Connect
                    </Button>
                  )}
                  
                  <Button variant="ghost" size="sm">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Market Data Comparison */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Market Data Comparison</CardTitle>
            <div className="flex space-x-2">
              {['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD'].map((symbol) => (
                <Button
                  key={symbol}
                  variant={selectedSymbol === symbol ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedSymbol(symbol)}
                >
                  {symbol}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Broker</th>
                  <th className="text-right p-2">Bid</th>
                  <th className="text-right p-2">Ask</th>
                  <th className="text-right p-2">Spread</th>
                  <th className="text-right p-2">Last Update</th>
                </tr>
              </thead>
              <tbody>
                {marketData
                  .find(data => data.symbol === selectedSymbol)
                  ?.data && Object.entries(marketData.find(data => data.symbol === selectedSymbol)!.data)
                  .map(([brokerId, data]) => {
                    const broker = brokers.find(b => b.broker_id === brokerId);
                    return (
                      <tr key={brokerId} className="border-b hover:bg-gray-50">
                        <td className="p-2">
                          <div className="flex items-center space-x-2">
                            <span>{getBrokerTypeIcon(broker?.type || '')}</span>
                            <span>{broker?.name || brokerId}</span>
                          </div>
                        </td>
                        <td className="text-right p-2 font-mono">{data.bid.toFixed(5)}</td>
                        <td className="text-right p-2 font-mono">{data.ask.toFixed(5)}</td>
                        <td className="text-right p-2">
                          <Badge variant="outline" className="text-xs">
                            {data.spread.toFixed(1)} pips
                          </Badge>
                        </td>
                        <td className="text-right p-2 text-gray-500">
                          {new Date(data.timestamp).toLocaleTimeString()}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 