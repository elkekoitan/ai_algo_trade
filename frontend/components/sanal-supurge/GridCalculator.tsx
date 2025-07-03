"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calculator, TrendingUp, BarChart3, Settings, Download, 
  Save, Upload, RefreshCw, Target, DollarSign, Gauge,
  AlertTriangle, CheckCircle, Info, Sliders
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import GlassCard from '@/components/quantum/GlassCard';
import { toast } from 'sonner';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Types
interface InstrumentPreset {
  symbol: string;
  contractSize: number;
  pointDecimals: number;
  tickSize: number;
  valuePerPoint: number;
  defaultVolatility: number;
  description: string;
}

interface GridLevel {
  level: number;
  sendOrder: boolean;
  lotSize: number;
  distancePoints: number;
  tpPoints: number;
  slPoints: number;
}

interface GridConfig {
  instrument: string;
  startPrice: number;
  balance: number;
  leverage: number;
  riskPercent: number;
  gridLevels: GridLevel[];
  lotProgression: string;
  customMultiplier: number;
  fibonacciStrength: number;
  defaultDistance: number;
  defaultTp: number;
  defaultSl: number;
  buyEnabled: boolean;
  sellEnabled: boolean;
  pivotUpper: number;
  pivotLower: number;
}

interface CalculationResult {
  buyScenarios: any[];
  sellScenarios: any[];
  maxBuyDrawdown: number;
  maxSellDrawdown: number;
  buyMarginPercent: number;
  sellMarginPercent: number;
  totalBuyLots: number;
  totalSellLots: number;
}

const INSTRUMENT_PRESETS: Record<string, InstrumentPreset> = {
  "XAUUSD": {
    symbol: "XAUUSD",
    contractSize: 100,
    pointDecimals: 2,
    tickSize: 0.01,
    valuePerPoint: 1.0,
    defaultVolatility: 3000,
    description: "Gold vs USD"
  },
  "EURUSD": {
    symbol: "EURUSD", 
    pointDecimals: 5,
    tickSize: 0.00001,
    valuePerPoint: 1.0,
    contractSize: 100000,
    defaultVolatility: 800,
    description: "Euro vs USD"
  },
  "BTCUSD": {
    symbol: "BTCUSD",
    pointDecimals: 2,
    tickSize: 0.01,
    valuePerPoint: 0.01,
    contractSize: 1,
    defaultVolatility: 250000,
    description: "Bitcoin vs USD"
  }
};

const LOT_PROGRESSION_OPTIONS = [
  { value: "linear", label: "Lineer (Eşit Lotlar)" },
  { value: "martingale", label: "Martingale (x2)" },
  { value: "custom_multiplier", label: "Özel Çarpan" },
  { value: "fibonacci_weighted", label: "Fibonacci Ağırlıklı" },
  { value: "custom_sequence", label: "Özel Sıra (Manuel)" }
];

export default function GridCalculator() {
  // State management
  const [config, setConfig] = useState<GridConfig>({
    instrument: "XAUUSD",
    startPrice: 2300.00,
    balance: 10000,
    leverage: 100,
    riskPercent: 5.0,
    gridLevels: [],
    lotProgression: "martingale",
    customMultiplier: 1.5,
    fibonacciStrength: 0.618,
    defaultDistance: 3500,
    defaultTp: 7000,
    defaultSl: 60000,
    buyEnabled: true,
    sellEnabled: true,
    pivotUpper: 1.8,
    pivotLower: 1.01
  });

  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [activeTab, setActiveTab] = useState("basic");
  const [volatility, setVolatility] = useState([3000]);
  const [gridLevelCount, setGridLevelCount] = useState([14]);

  // Initialize grid levels
  useEffect(() => {
    const levels: GridLevel[] = [];
    for (let i = 0; i < gridLevelCount[0]; i++) {
      levels.push({
        level: i + 1,
        sendOrder: true,
        lotSize: i < 9 ? (i + 1) * 0.01 : 0.1,
        distancePoints: i === 0 ? 0 : config.defaultDistance,
        tpPoints: i < 9 ? 1000 : 2500,
        slPoints: 100
      });
    }
    setConfig(prev => ({ ...prev, gridLevels: levels }));
  }, [gridLevelCount[0], config.defaultDistance]);

  // Handle instrument change
  const handleInstrumentChange = useCallback((instrument: string) => {
    const preset = INSTRUMENT_PRESETS[instrument];
    if (preset) {
      setConfig(prev => ({
        ...prev,
        instrument,
        startPrice: instrument === "XAUUSD" ? 2300 : instrument === "EURUSD" ? 1.08 : 60000,
        defaultDistance: preset.defaultVolatility * 0.15 / 100 * 100 // Smart distance
      }));
      setVolatility([preset.defaultVolatility]);
    }
  }, []);

  // Calculate grid
  const calculateGrid = useCallback(async () => {
    setIsCalculating(true);
    
    try {
      // Simulate API call - in real implementation, call backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const preset = INSTRUMENT_PRESETS[config.instrument];
      
      // Mock calculation result
      const result: CalculationResult = {
        buyScenarios: config.gridLevels.map((level, index) => ({
          level: level.level,
          lot: level.lotSize,
          entry: config.startPrice - (index * config.defaultDistance * preset.tickSize),
          cumulativeLot: config.gridLevels.slice(0, index + 1).reduce((sum, l) => sum + l.lotSize, 0),
          pnlAtTp: (level.tpPoints * level.lotSize * preset.valuePerPoint),
          margin: (level.lotSize * preset.contractSize * config.startPrice) / config.leverage
        })),
        sellScenarios: config.gridLevels.map((level, index) => ({
          level: level.level,
          lot: level.lotSize,
          entry: config.startPrice + (index * config.defaultDistance * preset.tickSize),
          cumulativeLot: config.gridLevels.slice(0, index + 1).reduce((sum, l) => sum + l.lotSize, 0),
          pnlAtTp: (level.tpPoints * level.lotSize * preset.valuePerPoint),
          margin: (level.lotSize * preset.contractSize * config.startPrice) / config.leverage
        })),
        maxBuyDrawdown: 5000,
        maxSellDrawdown: 4800,
        buyMarginPercent: 15,
        sellMarginPercent: 12,
        totalBuyLots: config.gridLevels.reduce((sum, l) => sum + l.lotSize, 0),
        totalSellLots: config.gridLevels.reduce((sum, l) => sum + l.lotSize, 0)
      };
      
      setCalculationResult(result);
      toast.success("Grid hesaplaması tamamlandı!");
      
    } catch (error) {
      toast.error("Hesaplama sırasında hata oluştu");
      console.error(error);
    } finally {
      setIsCalculating(false);
    }
  }, [config]);

  // Export .set file
  const exportSetFile = useCallback(() => {
    const preset = INSTRUMENT_PRESETS[config.instrument];
    let setContent = `# Sanal-Süpürge Configuration\n`;
    setContent += `BuyIslemiAc=${config.buyEnabled}\n`;
    setContent += `SellIslemiAc=${config.sellEnabled}\n`;
    setContent += `PositionComment=HayaletSüpürge\n`;
    setContent += `PivotUst=${config.pivotUpper}\n`;
    setContent += `PivotAlt=${config.pivotLower}\n\n`;
    
    config.gridLevels.forEach((level, index) => {
      const levelNum = index + 1;
      setContent += `SendOrder${levelNum}=${level.sendOrder}\n`;
      setContent += `LotSize${levelNum}=${level.lotSize.toFixed(2)}\n`;
      if (levelNum > 1) {
        setContent += `NewPositionAddLevel${levelNum}=${level.distancePoints}\n`;
      }
      setContent += `tp${levelNum}=${level.tpPoints}\n`;
      setContent += `sl${levelNum}=${level.slPoints}\n`;
    });

    const blob = new Blob([setContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${config.gridLevels.length}kademe_${config.lotProgression}_sanal_supurge.set`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success(".set dosyası indirildi!");
  }, [config]);

  // Chart data
  const pnlChartData = {
    labels: calculationResult?.buyScenarios.map(s => `Seviye ${s.level}`) || [],
    datasets: [
      {
        label: 'Alış P&L',
        data: calculationResult?.buyScenarios.map(s => s.pnlAtTp) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.1
      },
      {
        label: 'Satış P&L',
        data: calculationResult?.sellScenarios.map(s => s.pnlAtTp) || [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.1
      }
    ]
  };

  const riskChartData = {
    labels: ['Max DD Alış', 'Max DD Satış'],
    datasets: [{
      data: [
        calculationResult?.maxBuyDrawdown || 0,
        calculationResult?.maxSellDrawdown || 0
      ],
      backgroundColor: [
        'rgba(239, 68, 68, 0.8)',
        'rgba(245, 158, 11, 0.8)'
      ],
      borderColor: [
        'rgb(239, 68, 68)',
        'rgb(245, 158, 11)'
      ],
      borderWidth: 2
    }]
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20">
            <Calculator className="h-8 w-8 text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              Sanal-Süpürge Grid Calculator
            </h1>
            <p className="text-muted-foreground">Gelişmiş grid trading hesaplama ve analiz aracı</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={exportSetFile}>
            <Download className="h-4 w-4 mr-2" />
            .set İndir
          </Button>
          <Button onClick={calculateGrid} disabled={isCalculating}>
            {isCalculating ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4 mr-2" />
            )}
            Hesapla
          </Button>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="xl:col-span-2">
          <GlassCard className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="basic">Temel Ayarlar</TabsTrigger>
                <TabsTrigger value="grid">Grid Seviyeleri</TabsTrigger>
                <TabsTrigger value="risk">Risk Ayarları</TabsTrigger>
                <TabsTrigger value="results">Sonuçlar</TabsTrigger>
              </TabsList>

              {/* Basic Settings */}
              <TabsContent value="basic" className="space-y-6 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="instrument">Enstrüman</Label>
                    <Select value={config.instrument} onValueChange={handleInstrumentChange}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(INSTRUMENT_PRESETS).map(([key, preset]) => (
                          <SelectItem key={key} value={key}>
                            {preset.symbol} - {preset.description}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="startPrice">Başlangıç Fiyatı</Label>
                    <Input
                      id="startPrice"
                      type="number"
                      value={config.startPrice}
                      onChange={(e) => setConfig(prev => ({ ...prev, startPrice: parseFloat(e.target.value) || 0 }))}
                      step="any"
                    />
                  </div>

                  <div>
                    <Label htmlFor="balance">Hesap Bakiyesi</Label>
                    <Input
                      id="balance"
                      type="number"
                      value={config.balance}
                      onChange={(e) => setConfig(prev => ({ ...prev, balance: parseFloat(e.target.value) || 0 }))}
                    />
                  </div>

                  <div>
                    <Label htmlFor="leverage">Kaldıraç (1:X)</Label>
                    <Input
                      id="leverage"
                      type="number"
                      value={config.leverage}
                      onChange={(e) => setConfig(prev => ({ ...prev, leverage: parseInt(e.target.value) || 1 }))}
                    />
                  </div>
                </div>

                <div>
                  <Label>Piyasa Volatilitesi (ATR Puan): {volatility[0]}</Label>
                  <Slider
                    value={volatility}
                    onValueChange={setVolatility}
                    max={50000}
                    min={100}
                    step={100}
                    className="mt-2"
                  />
                </div>

                <div>
                  <Label>Kademe Sayısı: {gridLevelCount[0]}</Label>
                  <Slider
                    value={gridLevelCount}
                    onValueChange={setGridLevelCount}
                    max={14}
                    min={1}
                    step={1}
                    className="mt-2"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Lot Artış Modeli</Label>
                    <Select value={config.lotProgression} onValueChange={(value) => setConfig(prev => ({ ...prev, lotProgression: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {LOT_PROGRESSION_OPTIONS.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {config.lotProgression === "custom_multiplier" && (
                    <div>
                      <Label>Özel Çarpan: {config.customMultiplier}</Label>
                      <Slider
                        value={[config.customMultiplier]}
                        onValueChange={(value) => setConfig(prev => ({ ...prev, customMultiplier: value[0] }))}
                        max={10}
                        min={1}
                        step={0.1}
                        className="mt-2"
                      />
                    </div>
                  )}
                </div>
              </TabsContent>

              {/* Grid Levels */}
              <TabsContent value="grid" className="space-y-6 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Varsayılan Mesafe (Puan): {config.defaultDistance}</Label>
                    <Slider
                      value={[config.defaultDistance]}
                      onValueChange={(value) => setConfig(prev => ({ ...prev, defaultDistance: value[0] }))}
                      max={10000}
                      min={100}
                      step={100}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Varsayılan TP (Puan): {config.defaultTp}</Label>
                    <Slider
                      value={[config.defaultTp]}
                      onValueChange={(value) => setConfig(prev => ({ ...prev, defaultTp: value[0] }))}
                      max={20000}
                      min={100}
                      step={100}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Varsayılan SL (Puan): {config.defaultSl}</Label>
                    <Slider
                      value={[config.defaultSl]}
                      onValueChange={(value) => setConfig(prev => ({ ...prev, defaultSl: value[0] }))}
                      max={100000}
                      min={100}
                      step={1000}
                      className="mt-2"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-border rounded-lg">
                    <thead>
                      <tr className="bg-muted/50">
                        <th className="border border-border p-2">Seviye</th>
                        <th className="border border-border p-2">Aktif</th>
                        <th className="border border-border p-2">Lot</th>
                        <th className="border border-border p-2">Mesafe (P)</th>
                        <th className="border border-border p-2">TP (P)</th>
                        <th className="border border-border p-2">SL (P)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {config.gridLevels.map((level, index) => (
                        <tr key={level.level} className="hover:bg-muted/20">
                          <td className="border border-border p-2 text-center">{level.level}</td>
                          <td className="border border-border p-2 text-center">
                            <Switch
                              checked={level.sendOrder}
                              onCheckedChange={(checked) => {
                                const newLevels = [...config.gridLevels];
                                newLevels[index].sendOrder = checked;
                                setConfig(prev => ({ ...prev, gridLevels: newLevels }));
                              }}
                            />
                          </td>
                          <td className="border border-border p-2">
                            <Input
                              type="number"
                              value={level.lotSize}
                              onChange={(e) => {
                                const newLevels = [...config.gridLevels];
                                newLevels[index].lotSize = parseFloat(e.target.value) || 0;
                                setConfig(prev => ({ ...prev, gridLevels: newLevels }));
                              }}
                              step="0.01"
                              min="0.01"
                              className="w-20"
                            />
                          </td>
                          <td className="border border-border p-2">
                            <Input
                              type="number"
                              value={level.distancePoints}
                              onChange={(e) => {
                                const newLevels = [...config.gridLevels];
                                newLevels[index].distancePoints = parseInt(e.target.value) || 0;
                                setConfig(prev => ({ ...prev, gridLevels: newLevels }));
                              }}
                              disabled={index === 0}
                              className="w-24"
                            />
                          </td>
                          <td className="border border-border p-2">
                            <Input
                              type="number"
                              value={level.tpPoints}
                              onChange={(e) => {
                                const newLevels = [...config.gridLevels];
                                newLevels[index].tpPoints = parseInt(e.target.value) || 0;
                                setConfig(prev => ({ ...prev, gridLevels: newLevels }));
                              }}
                              className="w-24"
                            />
                          </td>
                          <td className="border border-border p-2">
                            <Input
                              type="number"
                              value={level.slPoints}
                              onChange={(e) => {
                                const newLevels = [...config.gridLevels];
                                newLevels[index].slPoints = parseInt(e.target.value) || 0;
                                setConfig(prev => ({ ...prev, gridLevels: newLevels }));
                              }}
                              className="w-24"
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </TabsContent>

              {/* Risk Settings */}
              <TabsContent value="risk" className="space-y-6 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label>Risk Yüzdesi (%): {config.riskPercent}</Label>
                    <Slider
                      value={[config.riskPercent]}
                      onValueChange={(value) => setConfig(prev => ({ ...prev, riskPercent: value[0] }))}
                      max={20}
                      min={0.1}
                      step={0.1}
                      className="mt-2"
                    />
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label>Alış İşlemleri</Label>
                      <Switch
                        checked={config.buyEnabled}
                        onCheckedChange={(checked) => setConfig(prev => ({ ...prev, buyEnabled: checked }))}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>Satış İşlemleri</Label>
                      <Switch
                        checked={config.sellEnabled}
                        onCheckedChange={(checked) => setConfig(prev => ({ ...prev, sellEnabled: checked }))}
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="pivotUpper">Pivot Üst</Label>
                    <Input
                      id="pivotUpper"
                      type="number"
                      value={config.pivotUpper}
                      onChange={(e) => setConfig(prev => ({ ...prev, pivotUpper: parseFloat(e.target.value) || 0 }))}
                      step="0.1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="pivotLower">Pivot Alt</Label>
                    <Input
                      id="pivotLower"
                      type="number"
                      value={config.pivotLower}
                      onChange={(e) => setConfig(prev => ({ ...prev, pivotLower: parseFloat(e.target.value) || 0 }))}
                      step="0.01"
                    />
                  </div>
                </div>
              </TabsContent>

              {/* Results */}
              <TabsContent value="results" className="space-y-6 mt-6">
                {calculationResult ? (
                  <div className="space-y-6">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-green-500" />
                            <div>
                              <p className="text-sm text-muted-foreground">Toplam Alış Lot</p>
                              <p className="text-xl font-bold">{calculationResult.totalBuyLots.toFixed(2)}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-red-500" />
                            <div>
                              <p className="text-sm text-muted-foreground">Max Drawdown</p>
                              <p className="text-xl font-bold">
                                ${Math.max(calculationResult.maxBuyDrawdown, calculationResult.maxSellDrawdown).toFixed(0)}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2">
                            <Gauge className="h-5 w-5 text-blue-500" />
                            <div>
                              <p className="text-sm text-muted-foreground">Marjin Kullanımı</p>
                              <p className="text-xl font-bold">
                                {Math.max(calculationResult.buyMarginPercent, calculationResult.sellMarginPercent).toFixed(1)}%
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Charts */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <Card>
                        <CardHeader>
                          <CardTitle>P&L Analizi</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <Line data={pnlChartData} options={{ responsive: true, maintainAspectRatio: false }} height={200} />
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Risk Dağılımı</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <Doughnut data={riskChartData} options={{ responsive: true, maintainAspectRatio: false }} height={200} />
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Calculator className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg text-muted-foreground">Hesaplama sonuçları için "Hesapla" butonuna tıklayın</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </GlassCard>
        </div>

        {/* Side Panel - Quick Actions & Status */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Hızlı İşlemler
            </h3>
            
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Target className="h-4 w-4 mr-2" />
                Altın Optimizeli
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <DollarSign className="h-4 w-4 mr-2" />
                Forex Muhafazakar
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <TrendingUp className="h-4 w-4 mr-2" />
                Kripto Agresif
              </Button>
            </div>
          </GlassCard>

          {/* Risk Meters */}
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Gauge className="h-5 w-5" />
              Risk Göstergeleri
            </h3>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Marjin Kullanımı</span>
                  <span className="font-medium">
                    {calculationResult ? Math.max(calculationResult.buyMarginPercent, calculationResult.sellMarginPercent).toFixed(1) : 0}%
                  </span>
                </div>
                <Progress 
                  value={calculationResult ? Math.max(calculationResult.buyMarginPercent, calculationResult.sellMarginPercent) : 0} 
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Risk Seviyesi</span>
                  <span className="font-medium">
                    {calculationResult && Math.max(calculationResult.buyMarginPercent, calculationResult.sellMarginPercent) > 30 ? "Yüksek" : "Düşük"}
                  </span>
                </div>
                <Progress 
                  value={calculationResult ? Math.min(Math.max(calculationResult.buyMarginPercent, calculationResult.sellMarginPercent) * 2, 100) : 0}
                  className="h-2"
                />
              </div>
            </div>
          </GlassCard>

          {/* Status */}
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Info className="h-5 w-5" />
              Sistem Durumu
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">MT5 Bağlantısı</span>
                <Badge variant="default" className="bg-green-500/20 text-green-400 border-green-500/30">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Aktif
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Copy Trading</span>
                <Badge variant="default" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  3 Hesap
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">Grid Hesaplama</span>
                <Badge variant="default" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Hazır
                </Badge>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
} 