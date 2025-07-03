"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, Play, Settings, Code, BarChart3, Users, Star, 
  Download, Upload, Save, RefreshCw, Terminal, AlertTriangle,
  CheckCircle, Clock, TrendingUp, TrendingDown, Activity,
  Zap, Shield, Brain, Gauge, Target, DollarSign
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { toast } from 'react-hot-toast';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface StrategyDetails {
  metadata: {
    strategy_id: string;
    name: string;
    display_name: string;
    type: string;
    platform: string;
    description: string;
    author: string;
    version: string;
    created_at: string;
    supported_symbols: string[];
    recommended_timeframes: string[];
    minimum_balance: number;
    recommended_leverage: number;
    default_risk_percent: number;
    max_positions: number;
    categories: string[];
    tags: string[];
  };
  parameters: Array<{
    name: string;
    display_name: string;
    type: string;
    default_value: any;
    current_value: any;
    description: string;
    min_value?: number;
    max_value?: number;
    step?: number;
    options?: string[];
    group: string;
    is_required: boolean;
  }>;
  parameter_groups: Array<{
    name: string;
    display_name: string;
    description?: string;
    parameters: string[];
    order: number;
    is_expanded: boolean;
  }>;
  files: Record<string, string>;
  active_instances: number;
}

const executionModes = [
  {
    value: 'robot',
    label: 'Robot Mode',
    icon: Zap,
    color: 'from-yellow-500 to-orange-600',
    description: 'Tam otomatik trading - Sinyaller otomatik execute edilir'
  },
  {
    value: 'signal',
    label: 'Signal Mode',
    icon: Activity,
    color: 'from-blue-500 to-cyan-600',
    description: 'Sadece sinyal üret - Manuel onay gerekir'
  },
  {
    value: 'manual',
    label: 'Manual Mode',
    icon: Shield,
    color: 'from-purple-500 to-pink-600',
    description: 'Sadece analiz sağla - Tüm işlemler manuel'
  },
  {
    value: 'hybrid',
    label: 'Hybrid Mode',
    icon: Brain,
    color: 'from-green-500 to-emerald-600',
    description: 'Yüksek güvenlikli sinyaller otomatik, diğerleri manuel'
  }
];

export default function StrategyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const strategyId = params.strategyId as string;

  const [strategy, setStrategy] = useState<StrategyDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('parameters');
  const [selectedAccount, setSelectedAccount] = useState('25201110');
  const [executionMode, setExecutionMode] = useState('signal');
  const [parameterValues, setParameterValues] = useState<Record<string, any>>({});
  const [savedConfigs, setSavedConfigs] = useState<any[]>([]);
  const [backtestRunning, setBacktestRunning] = useState(false);

  useEffect(() => {
    fetchStrategyDetails();
    fetchSavedConfigs();
  }, [strategyId]);

  const fetchStrategyDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/strategy-manager/strategies/${strategyId}`);
      const data = await response.json();
      
      if (data.success) {
        setStrategy(data);
        // Initialize parameter values
        const values: Record<string, any> = {};
        data.parameters.forEach((param: any) => {
          values[param.name] = param.current_value || param.default_value;
        });
        setParameterValues(values);
      } else {
        toast.error('Strateji detayları yüklenemedi');
        router.push('/strategy-library');
      }
    } catch (error) {
      console.error('Error fetching strategy:', error);
      toast.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedConfigs = async () => {
    try {
      const response = await fetch(`/api/v1/strategy-manager/strategies/${strategyId}/configs`);
      const data = await response.json();
      if (data.success) {
        setSavedConfigs(data.configs);
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const handleParameterChange = (paramName: string, value: any) => {
    setParameterValues(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleSaveConfig = async () => {
    try {
      const configName = prompt('Konfigürasyon adı:');
      if (!configName) return;

      const response = await fetch(`/api/v1/strategy-manager/strategies/${strategyId}/configs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: configName,
          parameters: parameterValues
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Konfigürasyon kaydedildi');
        fetchSavedConfigs();
      }
    } catch (error) {
      console.error('Error saving config:', error);
      toast.error('Konfigürasyon kaydedilemedi');
    }
  };

  const handleLoadConfig = (config: any) => {
    setParameterValues(config.parameters);
    toast.success(`"${config.name}" konfigürasyonu yüklendi`);
  };

  const handleCreateInstance = async () => {
    try {
      const response = await fetch('/api/v1/strategy-manager/instances/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: strategyId,
          account_login: parseInt(selectedAccount),
          execution_mode: executionMode,
          parameters: parameterValues,
          auto_start: true
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Strateji başlatıldı!');
        router.push(`/strategy-instances/${data.instance_id}`);
      } else {
        toast.error(data.error || 'Strateji başlatılamadı');
      }
    } catch (error) {
      console.error('Error creating instance:', error);
      toast.error('Bir hata oluştu');
    }
  };

  const handleRunBacktest = async () => {
    try {
      setBacktestRunning(true);
      const response = await fetch('/api/v1/strategy-manager/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: strategyId,
          parameters: parameterValues,
          symbol: 'EURUSD',
          timeframe: 'H1',
          start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date().toISOString(),
          initial_balance: 10000
        })
      });

      const data = await response.json();
      if (data.success) {
        toast.success('Backtest tamamlandı');
        // Handle backtest results
      }
    } catch (error) {
      console.error('Error running backtest:', error);
      toast.error('Backtest başlatılamadı');
    } finally {
      setBacktestRunning(false);
    }
  };

  const renderParameterInput = (param: any) => {
    const value = parameterValues[param.name];

    switch (param.type) {
      case 'bool':
        return (
          <div className="flex items-center space-x-2">
            <Switch
              checked={value}
              onCheckedChange={(checked: boolean) => handleParameterChange(param.name, checked)}
            />
            <Label>{value ? 'Aktif' : 'Pasif'}</Label>
          </div>
        );

      case 'int':
      case 'double':
        if (param.min_value !== null && param.max_value !== null) {
          return (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">{param.min_value}</span>
                <span className="text-sm font-semibold">{value}</span>
                <span className="text-sm text-gray-400">{param.max_value}</span>
              </div>
              <Slider
                value={[value]}
                onValueChange={([v]: number[]) => handleParameterChange(param.name, v)}
                min={param.min_value}
                max={param.max_value}
                step={param.step || 1}
                className="w-full"
              />
            </div>
          );
        } else {
          return (
            <Input
              type="number"
              value={value}
              onChange={(e) => handleParameterChange(param.name, parseFloat(e.target.value))}
              step={param.step || 1}
              className="bg-white/5 border-white/10"
            />
          );
        }

      case 'enum':
        return (
          <Select value={value} onValueChange={(v) => handleParameterChange(param.name, v)}>
            <SelectTrigger className="bg-white/5 border-white/10">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {param.options?.map((option: string) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'string':
        return (
          <Input
            value={value}
            onChange={(e) => handleParameterChange(param.name, e.target.value)}
            className="bg-white/5 border-white/10"
          />
        );

      case 'color':
        return (
          <div className="flex items-center space-x-2">
            <Input
              type="color"
              value={value}
              onChange={(e) => handleParameterChange(param.name, e.target.value)}
              className="w-20 h-10"
            />
            <Input
              value={value}
              onChange={(e) => handleParameterChange(param.name, e.target.value)}
              className="bg-white/5 border-white/10"
            />
          </div>
        );

      default:
        return (
          <Input
            value={value}
            onChange={(e) => handleParameterChange(param.name, e.target.value)}
            className="bg-white/5 border-white/10"
          />
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!strategy) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-600/20 rounded-full filter blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-600/20 rounded-full filter blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="bg-black/50 backdrop-blur-xl border-b border-white/10 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => router.push('/strategy-library')}
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">{strategy.metadata.display_name}</h1>
                <p className="text-gray-400 text-sm">{strategy.metadata.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge className="bg-purple-600/20 text-purple-400 border-purple-500/30">
                {strategy.metadata.platform}
              </Badge>
              <Badge className="bg-blue-600/20 text-blue-400 border-blue-500/30">
                v{strategy.metadata.version}
              </Badge>
              <Badge className="bg-green-600/20 text-green-400 border-green-500/30">
                {strategy.active_instances} Active
              </Badge>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Parameters */}
            <div className="lg:col-span-2 space-y-6">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-4 w-full bg-white/5">
                  <TabsTrigger value="parameters">Parametreler</TabsTrigger>
                  <TabsTrigger value="backtest">Backtest</TabsTrigger>
                  <TabsTrigger value="code">Kod</TabsTrigger>
                  <TabsTrigger value="stats">İstatistikler</TabsTrigger>
                </TabsList>

                <TabsContent value="parameters" className="space-y-6 mt-6">
                  {/* Saved Configs */}
                  {savedConfigs.length > 0 && (
                    <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                      <CardHeader>
                        <CardTitle className="text-lg">Kayıtlı Konfigürasyonlar</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-3">
                          {savedConfigs.map((config) => (
                            <Button
                              key={config.id}
                              variant="outline"
                              className="justify-start"
                              onClick={() => handleLoadConfig(config)}
                            >
                              <Download className="w-4 h-4 mr-2" />
                              {config.name}
                            </Button>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Parameter Groups */}
                  {strategy.parameter_groups.map((group) => (
                    <Card key={group.name} className="bg-black/40 backdrop-blur-xl border-white/10">
                      <CardHeader>
                        <CardTitle className="text-lg">{group.display_name}</CardTitle>
                        {group.description && (
                          <p className="text-sm text-gray-400">{group.description}</p>
                        )}
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {strategy.parameters
                          .filter(p => group.parameters.includes(p.name))
                          .map((param) => (
                            <div key={param.name} className="space-y-2">
                              <Label className="text-sm font-medium">
                                {param.display_name}
                                {param.is_required && <span className="text-red-500 ml-1">*</span>}
                              </Label>
                              {param.description && (
                                <p className="text-xs text-gray-500">{param.description}</p>
                              )}
                              {renderParameterInput(param)}
                            </div>
                          ))}
                      </CardContent>
                    </Card>
                  ))}

                  <Button
                    onClick={handleSaveConfig}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    Konfigürasyonu Kaydet
                  </Button>
                </TabsContent>

                <TabsContent value="backtest" className="space-y-6 mt-6">
                  <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                    <CardHeader>
                      <CardTitle>Backtest Sonuçları</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-white/5 rounded-lg">
                          <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                          <p className="text-2xl font-bold">65.4%</p>
                          <p className="text-sm text-gray-400">Win Rate</p>
                        </div>
                        <div className="text-center p-4 bg-white/5 rounded-lg">
                          <DollarSign className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                          <p className="text-2xl font-bold">1.85</p>
                          <p className="text-sm text-gray-400">Profit Factor</p>
                        </div>
                        <div className="text-center p-4 bg-white/5 rounded-lg">
                          <Target className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                          <p className="text-2xl font-bold">1.24</p>
                          <p className="text-sm text-gray-400">Sharpe Ratio</p>
                        </div>
                        <div className="text-center p-4 bg-white/5 rounded-lg">
                          <TrendingDown className="w-8 h-8 text-red-500 mx-auto mb-2" />
                          <p className="text-2xl font-bold">12.3%</p>
                          <p className="text-sm text-gray-400">Max Drawdown</p>
                        </div>
                      </div>

                      <div className="h-64 mb-6">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={[
                            { date: 'Jan', equity: 10000 },
                            { date: 'Feb', equity: 10800 },
                            { date: 'Mar', equity: 11200 },
                            { date: 'Apr', equity: 10900 },
                            { date: 'May', equity: 11800 },
                            { date: 'Jun', equity: 12500 }
                          ]}>
                            <defs>
                              <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="date" stroke="#666" />
                            <YAxis stroke="#666" />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                              labelStyle={{ color: '#999' }}
                            />
                            <Area type="monotone" dataKey="equity" stroke="#8884d8" fillOpacity={1} fill="url(#colorEquity)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>

                      <Button
                        onClick={handleRunBacktest}
                        disabled={backtestRunning}
                        className="w-full bg-gradient-to-r from-blue-600 to-purple-600"
                      >
                        {backtestRunning ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Backtest Çalışıyor...
                          </>
                        ) : (
                          <>
                            <BarChart3 className="w-4 h-4 mr-2" />
                            Backtest Çalıştır
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="code" className="mt-6">
                  <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                    <CardHeader>
                      <CardTitle>Strateji Kodu</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Tabs defaultValue={Object.keys(strategy.files)[0]}>
                        <TabsList className="mb-4">
                          {Object.keys(strategy.files).map((filename) => (
                            <TabsTrigger key={filename} value={filename}>
                              {filename}
                            </TabsTrigger>
                          ))}
                        </TabsList>
                        {Object.entries(strategy.files).map(([filename, content]) => (
                          <TabsContent key={filename} value={filename}>
                            <pre className="bg-black/60 rounded-lg p-4 overflow-x-auto">
                              <code className="text-sm text-gray-300">
                                {content}
                              </code>
                            </pre>
                          </TabsContent>
                        ))}
                      </Tabs>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="stats" className="space-y-6 mt-6">
                  <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                    <CardHeader>
                      <CardTitle>Kullanım İstatistikleri</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Users className="w-5 h-5 text-blue-500" />
                            <span>Toplam Kullanıcı</span>
                          </div>
                          <span className="text-xl font-bold">127</span>
                        </div>
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Activity className="w-5 h-5 text-green-500" />
                            <span>Aktif Instance</span>
                          </div>
                          <span className="text-xl font-bold">{strategy.active_instances}</span>
                        </div>
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Star className="w-5 h-5 text-yellow-500" />
                            <span>Ortalama Puan</span>
                          </div>
                          <span className="text-xl font-bold">4.6/5.0</span>
                        </div>
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Clock className="w-5 h-5 text-purple-500" />
                            <span>Oluşturma Tarihi</span>
                          </div>
                          <span className="text-sm">
                            {new Date(strategy.metadata.created_at).toLocaleDateString('tr-TR')}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                    <CardHeader>
                      <CardTitle>Desteklenen Özellikler</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <Label className="text-sm text-gray-400">Semboller</Label>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {strategy.metadata.supported_symbols.map((symbol) => (
                              <Badge key={symbol} variant="outline">
                                {symbol}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <Label className="text-sm text-gray-400">Timeframe'ler</Label>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {strategy.metadata.recommended_timeframes.map((tf) => (
                              <Badge key={tf} variant="outline">
                                {tf}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <Label className="text-sm text-gray-400">Kategoriler</Label>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {strategy.metadata.categories.map((cat) => (
                              <Badge key={cat} className="bg-purple-600/20 text-purple-400 border-purple-500/30">
                                {cat}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>

            {/* Right Column - Execution */}
            <div className="space-y-6">
              {/* Execution Mode Selection */}
              <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                <CardHeader>
                  <CardTitle>Execution Mode</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {executionModes.map((mode) => {
                    const Icon = mode.icon;
                    const isSelected = executionMode === mode.value;
                    
                    return (
                      <motion.div
                        key={mode.value}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setExecutionMode(mode.value)}
                        className={`p-4 rounded-lg border cursor-pointer transition-all ${
                          isSelected 
                            ? 'bg-gradient-to-r ' + mode.color + ' border-transparent' 
                            : 'bg-white/5 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <Icon className={`w-5 h-5 mt-0.5 ${isSelected ? 'text-white' : 'text-gray-400'}`} />
                          <div className="flex-1">
                            <h4 className={`font-semibold ${isSelected ? 'text-white' : 'text-gray-200'}`}>
                              {mode.label}
                            </h4>
                            <p className={`text-sm mt-1 ${isSelected ? 'text-white/80' : 'text-gray-500'}`}>
                              {mode.description}
                            </p>
                          </div>
                          {isSelected && (
                            <CheckCircle className="w-5 h-5 text-white" />
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Account Selection */}
              <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                <CardHeader>
                  <CardTitle>Hesap Seçimi</CardTitle>
                </CardHeader>
                <CardContent>
                  <Select value={selectedAccount} onValueChange={setSelectedAccount}>
                    <SelectTrigger className="bg-white/5 border-white/10">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="25201110">
                        Master Account - $498,428.79
                      </SelectItem>
                      <SelectItem value="25216036">
                        Copy Account 1 - $10,000.00
                      </SelectItem>
                      <SelectItem value="25216037">
                        Copy Account 2 - $100,000.00
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {/* Risk Settings */}
              <Card className="bg-black/40 backdrop-blur-xl border-white/10">
                <CardHeader>
                  <CardTitle>Risk Ayarları</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-sm">Minimum Bakiye</Label>
                    <p className="text-xl font-bold text-green-400">
                      ${strategy.metadata.minimum_balance.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm">Önerilen Kaldıraç</Label>
                    <p className="text-xl font-bold text-blue-400">
                      1:{strategy.metadata.recommended_leverage}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm">Varsayılan Risk</Label>
                    <p className="text-xl font-bold text-orange-400">
                      %{strategy.metadata.default_risk_percent}
                    </p>
                  </div>
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Bu strateji maksimum {strategy.metadata.max_positions} pozisyon açabilir.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>

              {/* Start Button */}
              <Button
                size="lg"
                onClick={handleCreateInstance}
                className="w-full h-14 text-lg bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
              >
                <Play className="w-6 h-6 mr-2" />
                Stratejiyi Başlat
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
