"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Users,
  Zap,
  Bot,
  MessageSquare,
  Radar,
  Activity,
  DollarSign
} from 'lucide-react';

// God Mode Demo - Prediction Simulation
export const GodModeDemo = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [prediction, setPrediction] = useState(0);
  const [confidence, setConfidence] = useState(0);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setPrediction(prev => {
        const change = (Math.random() - 0.5) * 10;
        return Math.max(-100, Math.min(100, prev + change));
      });
      setConfidence(prev => Math.min(100, prev + Math.random() * 5));
    }, 500);

    return () => clearInterval(interval);
  }, [isRunning]);

  const startDemo = () => {
    setIsRunning(true);
    setPrediction(0);
    setConfidence(75);
  };

  const stopDemo = () => {
    setIsRunning(false);
  };

  return (
    <Card className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-purple-500/30">
      <CardHeader>
        <CardTitle className="flex items-center text-purple-300">
          <Eye className="h-5 w-5 mr-2" />
          God Mode Prediction Engine
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${prediction > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {prediction > 0 ? '+' : ''}{prediction.toFixed(1)}%
            </div>
            <p className="text-xs text-gray-400">Market Direction</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-cyan-400">
              {confidence.toFixed(1)}%
            </div>
            <p className="text-xs text-gray-400">Confidence</p>
          </div>
        </div>
        
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-purple-400 to-pink-400 h-2 rounded-full transition-all duration-500"
            style={{ width: `${confidence}%` }}
          />
        </div>

        <div className="flex space-x-2">
          <Button
            onClick={startDemo}
            disabled={isRunning}
            size="sm"
            className="flex-1"
          >
            <Play className="h-3 w-3 mr-1" />
            {isRunning ? 'Predicting...' : 'Start Prediction'}
          </Button>
          <Button
            onClick={stopDemo}
            disabled={!isRunning}
            size="sm"
            variant="outline"
          >
            <Pause className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Shadow Mode Demo - Whale Detection
export const ShadowModeDemo = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [whaleActivity, setWhaleActivity] = useState<Array<{ symbol: string; volume: number; type: 'buy' | 'sell' }>>([]);

  useEffect(() => {
    if (!isScanning) return;

    const interval = setInterval(() => {
      const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'];
      const newActivity = {
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        volume: Math.floor(Math.random() * 50) + 10,
        type: Math.random() > 0.5 ? 'buy' : 'sell' as 'buy' | 'sell'
      };

      setWhaleActivity(prev => [newActivity, ...prev.slice(0, 3)]);
    }, 2000);

    return () => clearInterval(interval);
  }, [isScanning]);

  return (
    <Card className="bg-gradient-to-br from-gray-900/40 to-black/40 border-gray-600/30">
      <CardHeader>
        <CardTitle className="flex items-center text-gray-300">
          <Users className="h-5 w-5 mr-2" />
          Shadow Mode Scanner
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {whaleActivity.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              No whale activity detected
            </div>
          ) : (
            whaleActivity.map((activity, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-800/50 rounded">
                <span className="text-sm text-white">{activity.symbol}</span>
                <span className={`text-sm ${activity.type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                  {activity.type.toUpperCase()} {activity.volume}M
                </span>
              </div>
            ))
          )}
        </div>

        <Button
          onClick={() => setIsScanning(!isScanning)}
          size="sm"
          className="w-full"
          variant={isScanning ? "destructive" : "default"}
        >
          {isScanning ? (
            <>
              <Pause className="h-3 w-3 mr-1" />
              Stop Scanning
            </>
          ) : (
            <>
              <Play className="h-3 w-3 mr-1" />
              Start Whale Hunt
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

// Adaptive Trade Manager Demo
export const AdaptiveTradeDemo = () => {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [riskLevel, setRiskLevel] = useState(25);
  const [positionSize, setPositionSize] = useState(1.0);

  useEffect(() => {
    if (!isOptimizing) return;

    const interval = setInterval(() => {
      setRiskLevel(prev => {
        const target = 15; // Optimal risk level
        const diff = target - prev;
        return prev + (diff * 0.1);
      });
      
      setPositionSize(prev => {
        const target = 0.8; // Optimal position size
        const diff = target - prev;
        return prev + (diff * 0.1);
      });
    }, 200);

    setTimeout(() => setIsOptimizing(false), 3000);

    return () => clearInterval(interval);
  }, [isOptimizing]);

  return (
    <Card className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 border-yellow-500/30">
      <CardHeader>
        <CardTitle className="flex items-center text-yellow-300">
          <Zap className="h-5 w-5 mr-2" />
          Adaptive Risk Manager
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Risk Level</span>
              <span className={`${riskLevel < 20 ? 'text-green-400' : riskLevel < 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                {riskLevel.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  riskLevel < 20 ? 'bg-green-400' : riskLevel < 40 ? 'bg-yellow-400' : 'bg-red-400'
                }`}
                style={{ width: `${Math.min(riskLevel, 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Position Size</span>
              <span className="text-cyan-400">{positionSize.toFixed(2)} lots</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
              <div 
                className="bg-cyan-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(positionSize * 50, 100)}%` }}
              />
            </div>
          </div>
        </div>

        <Button
          onClick={() => setIsOptimizing(true)}
          disabled={isOptimizing}
          size="sm"
          className="w-full"
        >
          {isOptimizing ? (
            <>
              <Activity className="h-3 w-3 mr-1 animate-spin" />
              Optimizing...
            </>
          ) : (
            <>
              <Zap className="h-3 w-3 mr-1" />
              Optimize Positions
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

// Strategy Whisperer Demo
export const StrategyWhispererDemo = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [strategy, setStrategy] = useState('');

  const strategies = [
    "RSI Divergence + MA Cross",
    "Bollinger Band Squeeze",
    "ICT Fair Value Gap",
    "Support/Resistance Breakout",
    "Moving Average Convergence"
  ];

  const generateStrategy = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setStrategy(strategies[Math.floor(Math.random() * strategies.length)]);
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <Card className="bg-gradient-to-br from-blue-900/20 to-cyan-900/20 border-blue-500/30">
      <CardHeader>
        <CardTitle className="flex items-center text-blue-300">
          <Bot className="h-5 w-5 mr-2" />
          Strategy Whisperer
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="min-h-[60px] flex items-center justify-center">
          {isGenerating ? (
            <div className="text-center">
              <Activity className="h-6 w-6 animate-spin mx-auto text-blue-400" />
              <p className="text-sm text-gray-400 mt-2">Generating strategy...</p>
            </div>
          ) : strategy ? (
            <div className="text-center">
              <p className="text-white font-medium">{strategy}</p>
              <p className="text-xs text-gray-400 mt-1">Ready for backtesting</p>
            </div>
          ) : (
            <p className="text-gray-500 text-center">Click to generate a trading strategy</p>
          )}
        </div>

        <Button
          onClick={generateStrategy}
          disabled={isGenerating}
          size="sm"
          className="w-full"
        >
          {isGenerating ? 'Generating...' : 'Create Strategy'}
        </Button>
      </CardContent>
    </Card>
  );
};

// Market Narrator Demo
export const MarketNarratorDemo = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sentiment, setSentiment] = useState<'bullish' | 'bearish' | 'neutral'>('neutral');
  const [story, setStory] = useState('');

  const stories = {
    bullish: "Bulls are taking control as institutional money flows into risk assets. Strong momentum building...",
    bearish: "Bears dominate as risk-off sentiment spreads. Institutional selling pressure intensifies...",
    neutral: "Markets consolidating in tight range. Waiting for catalyst to determine next major move..."
  };

  const analyzeMarket = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      const sentiments: Array<'bullish' | 'bearish' | 'neutral'> = ['bullish', 'bearish', 'neutral'];
      const newSentiment = sentiments[Math.floor(Math.random() * sentiments.length)];
      setSentiment(newSentiment);
      setStory(stories[newSentiment]);
      setIsAnalyzing(false);
    }, 2500);
  };

  return (
    <Card className="bg-gradient-to-br from-green-900/20 to-teal-900/20 border-green-500/30">
      <CardHeader>
        <CardTitle className="flex items-center text-green-300">
          <MessageSquare className="h-5 w-5 mr-2" />
          Market Narrator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="min-h-[80px] flex items-center justify-center">
          {isAnalyzing ? (
            <div className="text-center">
              <Activity className="h-6 w-6 animate-spin mx-auto text-green-400" />
              <p className="text-sm text-gray-400 mt-2">Analyzing market story...</p>
            </div>
          ) : story ? (
            <div className="space-y-2">
              <div className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                sentiment === 'bullish' ? 'bg-green-400/20 text-green-400' :
                sentiment === 'bearish' ? 'bg-red-400/20 text-red-400' :
                'bg-gray-400/20 text-gray-400'
              }`}>
                {sentiment.toUpperCase()}
              </div>
              <p className="text-sm text-white">{story}</p>
            </div>
          ) : (
            <p className="text-gray-500 text-center">Click to generate market narrative</p>
          )}
        </div>

        <Button
          onClick={analyzeMarket}
          disabled={isAnalyzing}
          size="sm"
          className="w-full"
        >
          {isAnalyzing ? 'Analyzing...' : 'Generate Story'}
        </Button>
      </CardContent>
    </Card>
  );
};

// Real-time Metrics Demo
export const RealTimeMetrics = () => {
  const [metrics, setMetrics] = useState({
    profit: 2450.75,
    trades: 127,
    winRate: 68.5,
    drawdown: 3.2
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        profit: prev.profit + (Math.random() - 0.4) * 50,
        trades: prev.trades + (Math.random() > 0.8 ? 1 : 0),
        winRate: Math.max(50, Math.min(90, prev.winRate + (Math.random() - 0.5) * 2)),
        drawdown: Math.max(0, Math.min(10, prev.drawdown + (Math.random() - 0.5) * 1))
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card className="bg-gray-900/50 border-gray-800">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4 text-green-400" />
            <div>
              <p className="text-lg font-bold text-green-400">
                ${metrics.profit.toFixed(2)}
              </p>
              <p className="text-xs text-gray-400">Total Profit</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gray-900/50 border-gray-800">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-blue-400" />
            <div>
              <p className="text-lg font-bold text-blue-400">{metrics.trades}</p>
              <p className="text-xs text-gray-400">Total Trades</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gray-900/50 border-gray-800">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-cyan-400" />
            <div>
              <p className="text-lg font-bold text-cyan-400">
                {metrics.winRate.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-400">Win Rate</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gray-900/50 border-gray-800">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <TrendingDown className="h-4 w-4 text-red-400" />
            <div>
              <p className="text-lg font-bold text-red-400">
                {metrics.drawdown.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-400">Max Drawdown</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 