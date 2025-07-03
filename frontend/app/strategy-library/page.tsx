"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, Filter, Search, Play, Pause, Settings, TrendingUp, 
  Grid, Zap, BarChart3, Shield, Layers, Code, Download,
  Plus, Eye, Star, Users, Clock, AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { toast } from 'react-hot-toast';

// Strategy type icons
const strategyIcons = {
  grid_trading: Grid,
  scalping: Zap,
  trend_following: TrendingUp,
  breakout: BarChart3,
  arbitrage: Layers,
  hedging: Shield,
  custom: Code
};

// Strategy type colors
const strategyColors = {
  grid_trading: 'from-purple-500 to-purple-700',
  scalping: 'from-yellow-500 to-orange-600',
  trend_following: 'from-green-500 to-green-700',
  breakout: 'from-blue-500 to-blue-700',
  arbitrage: 'from-pink-500 to-pink-700',
  hedging: 'from-indigo-500 to-indigo-700',
  custom: 'from-gray-500 to-gray-700'
};

interface Strategy {
  strategy_id: string;
  name: string;
  display_name: string;
  type: string;
  platform: string;
  description: string;
  author: string;
  created_at: string;
  total_users: number;
  active_instances: number;
  average_rating: number;
  categories: string[];
  tags: string[];
  supported_symbols: string[];
  recommended_timeframes: string[];
  backtest_results?: {
    win_rate: number;
    profit_factor: number;
    sharpe_ratio: number;
  };
}

export default function StrategyLibraryPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [categoryStats, setCategoryStats] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchStrategies();
    fetchCategoryStats();
  }, [selectedType, selectedPlatform, sortBy]);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      
      // Sanal Süpürge stratejisini ekle
      const sanalSupurgeStrategy: Strategy = {
        strategy_id: 'sanal_supurge_pro',
        name: 'sanal_supurge_pro',
        display_name: 'Sanal Süpürge Pro',
        type: 'grid_trading',
        platform: 'MT5',
        description: 'Advanced Grid Trading with Fibonacci levels and intelligent risk management. Automatic lot progression and smart grid level adaptation.',
        author: 'AI Algo Trade',
        created_at: new Date().toISOString(),
        total_users: 247,
        active_instances: 12,
        average_rating: 4.8,
        categories: ['Grid Trading', 'Fibonacci', 'Risk Management'],
        tags: ['fibonacci', 'grid', 'adaptive', 'risk-control', 'pro'],
        supported_symbols: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD'],
        recommended_timeframes: ['M15', 'M30', 'H1', 'H4'],
        backtest_results: {
          win_rate: 87.3,
          profit_factor: 2.4,
          sharpe_ratio: 1.8
        }
      };

      // Diğer stratejileri API'den al
      const response = await fetch('/api/v1/strategy-manager/strategies/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: selectedType === 'all' ? null : selectedType,
          platform: selectedPlatform === 'all' ? null : selectedPlatform,
          search: searchTerm,
          sort_by: sortBy,
          sort_order: 'desc',
          page: 1,
          page_size: 50
        })
      });

      const data = await response.json();
      let allStrategies: Strategy[] = [sanalSupurgeStrategy];
      
      if (data.success && data.strategies) {
        allStrategies = [...allStrategies, ...data.strategies];
      }

      // Filtreleme uygula
      let filteredStrategies = allStrategies;
      
      if (selectedType !== 'all') {
        filteredStrategies = filteredStrategies.filter(s => s.type === selectedType);
      }
      
      if (selectedPlatform !== 'all') {
        filteredStrategies = filteredStrategies.filter(s => s.platform === selectedPlatform);
      }
      
      if (searchTerm) {
        filteredStrategies = filteredStrategies.filter(s => 
          s.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          s.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          s.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }

      setStrategies(filteredStrategies);
    } catch (error) {
      console.error('Error fetching strategies:', error);
      toast.error('Stratejiler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategoryStats = async () => {
    try {
      const response = await fetch('/api/v1/strategy-manager/strategies/stats/categories');
      const data = await response.json();
      if (data.success) {
        setCategoryStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching category stats:', error);
    }
  };

  const handleCreateInstance = async (strategyId: string) => {
    // Navigate to strategy detail page
    if (strategyId === 'sanal_supurge_pro') {
      window.location.href = `/sanal-supurge`;
    } else {
    window.location.href = `/strategy-library/${strategyId}`;
    }
  };

  const StrategyCard = ({ strategy }: { strategy: Strategy }) => {
    const Icon = strategyIcons[strategy.type as keyof typeof strategyIcons] || Code;
    const colorClass = strategyColors[strategy.type as keyof typeof strategyColors] || 'from-gray-500 to-gray-700';

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="h-full bg-black/40 backdrop-blur-xl border-white/10 hover:border-white/20 transition-all duration-300 overflow-hidden group">
          {/* Gradient Header */}
          <div className={`h-32 bg-gradient-to-br ${colorClass} p-6 relative overflow-hidden`}>
            <div className="absolute inset-0 bg-black/20" />
            <div className="relative z-10 flex items-start justify-between">
              <Icon className="w-10 h-10 text-white/90" />
              <Badge className="bg-black/30 text-white border-white/30">
                {strategy.platform}
              </Badge>
            </div>
            <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
          </div>

          <CardContent className="p-6 space-y-4">
            {/* Title & Description */}
            <div>
              <h3 className="text-xl font-bold text-white mb-2">
                {strategy.display_name}
              </h3>
              <p className="text-gray-400 text-sm line-clamp-2">
                {strategy.description || 'Açıklama mevcut değil'}
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-yellow-500 mb-1">
                  <Star className="w-4 h-4 fill-current" />
                  <span className="text-sm font-semibold">{strategy.average_rating.toFixed(1)}</span>
                </div>
                <p className="text-xs text-gray-500">Rating</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-blue-500 mb-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm font-semibold">{strategy.total_users}</span>
                </div>
                <p className="text-xs text-gray-500">Users</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-green-500 mb-1">
                  <Play className="w-4 h-4" />
                  <span className="text-sm font-semibold">{strategy.active_instances}</span>
                </div>
                <p className="text-xs text-gray-500">Active</p>
              </div>
            </div>

            {/* Backtest Results */}
            {strategy.backtest_results && (
              <div className="pt-3 border-t border-white/10">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Win Rate</span>
                  <span className="text-green-400 font-semibold">
                    {strategy.backtest_results.win_rate}%
                  </span>
                </div>
                <Progress 
                  value={strategy.backtest_results.win_rate} 
                  className="h-1.5 mt-1"
                />
              </div>
            )}

            {/* Tags */}
            <div className="flex flex-wrap gap-2 pt-3">
              {strategy.tags.slice(0, 3).map((tag, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {strategy.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{strategy.tags.length - 3}
                </Badge>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-3">
              <Button
                size="sm"
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                onClick={() => handleCreateInstance(strategy.strategy_id)}
              >
                <Play className="w-4 h-4 mr-1" />
                Kullan
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={() => window.location.href = `/strategy-library/${strategy.strategy_id}`}
              >
                <Eye className="w-4 h-4 mr-1" />
                Detay
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
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
                Strategy Library
              </h1>
              <p className="text-gray-400 text-lg">
                Profesyonel trading stratejilerini keşfet ve kullan
              </p>
            </div>
            <Button
              size="lg"
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
              onClick={() => setShowUploadModal(true)}
            >
              <Upload className="w-5 h-5 mr-2" />
              Strateji Yükle
            </Button>
          </div>

          {/* Category Stats */}
          <div className="grid grid-cols-7 gap-4 mb-8">
            {Object.entries(categoryStats).map(([category, count]) => {
              const Icon = strategyIcons[category as keyof typeof strategyIcons] || Code;
              const colorClass = strategyColors[category as keyof typeof strategyColors] || 'from-gray-500 to-gray-700';
              
              return (
                <motion.div
                  key={category}
                  whileHover={{ scale: 1.05 }}
                  className={`p-4 rounded-xl bg-gradient-to-br ${colorClass} bg-opacity-20 backdrop-blur-sm border border-white/10 cursor-pointer`}
                  onClick={() => setSelectedType(category)}
                >
                  <Icon className="w-6 h-6 mb-2 text-white/80" />
                  <p className="text-sm font-semibold text-white">{count}</p>
                  <p className="text-xs text-white/60 capitalize">
                    {category.replace('_', ' ')}
                  </p>
                </motion.div>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Strateji ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white placeholder-gray-400"
                onKeyPress={(e) => e.key === 'Enter' && fetchStrategies()}
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-48 bg-white/5 border-white/10">
                <SelectValue placeholder="Strateji Türü" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Türler</SelectItem>
                <SelectItem value="grid_trading">Grid Trading</SelectItem>
                <SelectItem value="scalping">Scalping</SelectItem>
                <SelectItem value="trend_following">Trend Following</SelectItem>
                <SelectItem value="breakout">Breakout</SelectItem>
                <SelectItem value="arbitrage">Arbitrage</SelectItem>
                <SelectItem value="hedging">Hedging</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
              <SelectTrigger className="w-40 bg-white/5 border-white/10">
                <SelectValue placeholder="Platform" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Platformlar</SelectItem>
                <SelectItem value="MT4">MT4</SelectItem>
                <SelectItem value="MT5">MT5</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-40 bg-white/5 border-white/10">
                <SelectValue placeholder="Sıralama" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">En Yeni</SelectItem>
                <SelectItem value="rating">En Yüksek Puan</SelectItem>
                <SelectItem value="name">İsme Göre</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex gap-2">
              <Button
                size="icon"
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                onClick={() => setViewMode('grid')}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                size="icon"
                variant={viewMode === 'list' ? 'default' : 'outline'}
                onClick={() => setViewMode('list')}
              >
                <Layers className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Strategy Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        ) : strategies.length === 0 ? (
          <Card className="bg-black/40 backdrop-blur-xl border-white/10 p-12 text-center">
            <AlertCircle className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Strateji Bulunamadı</h3>
            <p className="text-gray-400">Arama kriterlerinize uygun strateji bulunamadı.</p>
          </Card>
        ) : (
          <div className={`grid ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'} gap-6`}>
            {strategies.map((strategy) => (
              <StrategyCard key={strategy.strategy_id} strategy={strategy} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 