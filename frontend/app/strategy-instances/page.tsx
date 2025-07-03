"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, Pause, Settings, RefreshCw, Activity, 
  AlertCircle, CheckCircle, Clock, TrendingUp, Signal,
  Shield, Zap, Brain, Eye, Trash2, Download, Upload, Plus, DollarSign
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'react-hot-toast';
import { useRouter } from 'next/navigation';

interface StrategyInstance {
  instance: {
    instance_id: string;
    strategy_id: string;
    user_id: string;
    account_login: number;
    execution_mode: string;
    is_active: boolean;
    status: string;
    parameters: Record<string, any>;
    open_positions: number;
    total_trades: number;
    profit_loss: number;
    win_rate: number;
    last_signal: string | null;
    total_signals: number;
    started_at: string | null;
    stopped_at: string | null;
    created_at: string;
    updated_at: string;
  };
  strategy_name: string;
  strategy_type: string;
}

interface TradingSignal {
  signal_id: string;
  signal_type: string;
  symbol: string;
  direction: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  lot_size: number;
  confidence: number;
  reasoning: string;
  created_at: string;
  expires_at: string;
  is_executed: boolean;
}

const executionModeIcons = {
  robot: Zap,
  signal: Activity,
  manual: Shield,
  hybrid: Brain
};

const executionModeColors = {
  robot: 'from-yellow-500 to-orange-600',
  signal: 'from-blue-500 to-cyan-600',
  manual: 'from-purple-500 to-pink-600',
  hybrid: 'from-green-500 to-emerald-600'
};

const statusColors = {
  idle: 'bg-gray-500',
  running: 'bg-green-500',
  paused: 'bg-yellow-500',
  error: 'bg-red-500',
  stopped: 'bg-gray-500'
};

export default function StrategyInstancesPage() {
  const router = useRouter();
  const [instances, setInstances] = useState<StrategyInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInstance, setSelectedInstance] = useState<string | null>(null);
  const [pendingSignals, setPendingSignals] = useState<Record<string, TradingSignal[]>>({});
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchInstances();
    const interval = setInterval(fetchInstances, 5000); // 5 saniyede bir güncelle
    return () => clearInterval(interval);
  }, []);

  const fetchInstances = async () => {
    try {
      const response = await fetch('/api/v1/strategy-manager/instances');
      const data = await response.json();
      
      if (data.success) {
        setInstances(data.instances);
        
        // Aktif instance'lar için sinyalleri getir
        for (const instance of data.instances) {
          if (instance.instance.is_active) {
            fetchSignals(instance.instance.instance_id);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching instances:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSignals = async (instanceId: string) => {
    try {
      const response = await fetch(`/api/v1/strategy-manager/instances/${instanceId}/signals`);
      const data = await response.json();
      
      if (data.success) {
        setPendingSignals(prev => ({
          ...prev,
          [instanceId]: data.pending_signals
        }));
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    }
  };

  const handleStartStop = async (instanceId: string, isActive: boolean) => {
    try {
      const endpoint = isActive ? 'stop' : 'start';
      const response = await fetch(`/api/v1/strategy-manager/instances/${instanceId}/${endpoint}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success(isActive ? 'Instance durduruldu' : 'Instance başlatıldı');
        fetchInstances();
      } else {
        toast.error(data.error || 'İşlem başarısız');
      }
    } catch (error) {
      console.error('Error toggling instance:', error);
      toast.error('Bir hata oluştu');
    }
  };

  const handleExecuteSignal = async (instanceId: string, signalId: string) => {
    try {
      const response = await fetch(`/api/v1/strategy-manager/instances/${instanceId}/signals/${signalId}/execute`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success('Sinyal execute edildi');
        fetchSignals(instanceId);
      } else {
        toast.error(data.error || 'Execute başarısız');
      }
    } catch (error) {
      console.error('Error executing signal:', error);
      toast.error('Bir hata oluştu');
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchInstances();
    setRefreshing(false);
    toast.success('Veriler güncellendi');
  };

  const InstanceCard = ({ instance }: { instance: StrategyInstance }) => {
    const Icon = executionModeIcons[instance.instance.execution_mode as keyof typeof executionModeIcons] || Shield;
    const colorClass = executionModeColors[instance.instance.execution_mode as keyof typeof executionModeColors] || 'from-gray-500 to-gray-700';
    const statusColor = statusColors[instance.instance.status as keyof typeof statusColors] || 'bg-gray-500';
    const signals = pendingSignals[instance.instance.instance_id] || [];

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="bg-black/40 backdrop-blur-xl border-white/10 hover:border-white/20 transition-all duration-300 overflow-hidden">
          {/* Header with gradient */}
          <div className={`h-2 bg-gradient-to-r ${colorClass}`} />
          
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-lg bg-gradient-to-br ${colorClass}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{instance.strategy_name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {instance.strategy_type}
                    </Badge>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${statusColor} animate-pulse`} />
                      <span className="text-xs text-gray-400 capitalize">{instance.instance.status}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => router.push(`/strategy-instances/${instance.instance.instance_id}`)}
                >
                  <Eye className="w-4 h-4" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => handleStartStop(instance.instance.instance_id, instance.instance.is_active)}
                >
                  {instance.instance.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Stats Grid */}
            <div className="grid grid-cols-4 gap-3">
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-white">{instance.instance.open_positions}</p>
                <p className="text-xs text-gray-400">Açık Pozisyon</p>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-white">{instance.instance.total_trades}</p>
                <p className="text-xs text-gray-400">Toplam İşlem</p>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className={`text-2xl font-bold ${instance.instance.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${instance.instance.profit_loss.toFixed(2)}
                </p>
                <p className="text-xs text-gray-400">Kar/Zarar</p>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <p className="text-2xl font-bold text-blue-400">{instance.instance.win_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400">Başarı Oranı</p>
              </div>
            </div>

            {/* Win Rate Progress */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">Win Rate</span>
                <span className="text-green-400">{instance.instance.win_rate.toFixed(1)}%</span>
              </div>
              <Progress value={instance.instance.win_rate} className="h-2" />
            </div>

            {/* Pending Signals */}
            {signals.length > 0 && (
              <div className="pt-3 border-t border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-semibold text-gray-300">Bekleyen Sinyaller</h4>
                  <Badge className="bg-orange-600/20 text-orange-400 border-orange-500/30">
                    {signals.length}
                  </Badge>
                </div>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {signals.slice(0, 3).map((signal) => (
                    <div key={signal.signal_id} className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Signal className="w-4 h-4 text-blue-400" />
                        <span className="text-sm">
                          {signal.direction.toUpperCase()} {signal.symbol}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {signal.confidence}%
                        </Badge>
                      </div>
                      {instance.instance.execution_mode === 'signal' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleExecuteSignal(instance.instance.instance_id, signal.signal_id)}
                        >
                          Execute
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Account Info */}
            <div className="flex items-center justify-between pt-3 border-t border-white/10">
              <span className="text-sm text-gray-400">Hesap</span>
              <span className="text-sm font-mono">{instance.instance.account_login}</span>
            </div>

            {/* Running Time */}
            {instance.instance.started_at && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Çalışma Süresi</span>
                <span className="text-sm">
                  {getRunningTime(instance.instance.started_at)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const getRunningTime = (startedAt: string) => {
    const start = new Date(startedAt);
    const now = new Date();
    const diff = now.getTime() - start.getTime();
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days} gün ${hours % 24} saat`;
    }
    
    return `${hours} saat ${minutes} dakika`;
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-600/20 rounded-full filter blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-600/20 rounded-full filter blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent mb-2">
                Strategy Instances
              </h1>
              <p className="text-gray-400 text-lg">
                Çalışan stratejilerini yönet ve izle
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Yenile
              </Button>
              <Button
                className="bg-gradient-to-r from-blue-600 to-purple-600"
                onClick={() => router.push('/strategy-library')}
              >
                <Plus className="w-4 h-4 mr-2" />
                Yeni Strateji
              </Button>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <Card className="bg-black/40 backdrop-blur-xl border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-3xl font-bold text-white">{instances.length}</p>
                    <p className="text-sm text-gray-400">Toplam Instance</p>
                  </div>
                  <Activity className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-3xl font-bold text-green-400">
                      {instances.filter(i => i.instance.is_active).length}
                    </p>
                    <p className="text-sm text-gray-400">Aktif</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-3xl font-bold text-white">
                      {instances.reduce((sum, i) => sum + i.instance.total_trades, 0)}
                    </p>
                    <p className="text-sm text-gray-400">Toplam İşlem</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-3xl font-bold ${
                      instances.reduce((sum, i) => sum + i.instance.profit_loss, 0) >= 0 
                        ? 'text-green-400' 
                        : 'text-red-400'
                    }`}>
                      ${instances.reduce((sum, i) => sum + i.instance.profit_loss, 0).toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-400">Toplam Kar/Zarar</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-yellow-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        {/* Instances Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        ) : instances.length === 0 ? (
          <Card className="bg-black/40 backdrop-blur-xl border-white/10 p-12 text-center">
            <AlertCircle className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Çalışan Strateji Yok</h3>
            <p className="text-gray-400 mb-6">Henüz hiçbir strateji başlatılmamış.</p>
            <Button
              className="bg-gradient-to-r from-blue-600 to-purple-600"
              onClick={() => router.push('/strategy-library')}
            >
              Strateji Kütüphanesine Git
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {instances.map((instance) => (
              <InstanceCard key={instance.instance.instance_id} instance={instance} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
