"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Brain, Zap, TrendingUp, Eye, Target, Cpu, Sparkles, CheckCircle } from "lucide-react";

interface PatternData {
  id: string;
  name: string;
  type: "bullish" | "bearish" | "neutral";
  confidence: number;
  coordinates: number[][];
  prediction: number;
  probability: number;
  timeframe: string;
  detected_at: Date;
}

interface AIModel {
  name: string;
  accuracy: number;
  isLoaded: boolean;
  lastPrediction: number;
  confidence: number;
}

export default function AIPatternRecognition() {
  const [patterns, setPatterns] = useState<PatternData[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState("M15");
  const [aiModels, setAiModels] = useState<AIModel[]>([
    { name: "LSTM Neural Network", accuracy: 87.5, isLoaded: false, lastPrediction: 0, confidence: 0 },
    { name: "Transformer Model", accuracy: 92.3, isLoaded: false, lastPrediction: 0, confidence: 0 },
    { name: "GRU Predictor", accuracy: 85.2, isLoaded: false, lastPrediction: 0, confidence: 0 },
    { name: "Ensemble Model", accuracy: 94.1, isLoaded: false, lastPrediction: 0, confidence: 0 }
  ]);
  const [neuronsActivity, setNeuronsActivity] = useState<number[]>([]);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Initialize AI models
  useEffect(() => {
    const initializeModels = async () => {
      try {
        // Simulate model loading
        setTimeout(() => {
          setAiModels(prev => prev.map(model => ({
            ...model,
            isLoaded: true
          })));
        }, 2000);
        
        // Start real-time analysis
        startRealTimeAnalysis();
        
      } catch (error) {
        console.error("Error initializing AI models:", error);
      }
    };

    initializeModels();
  }, []);

  // Real-time pattern analysis
  const startRealTimeAnalysis = () => {
    const interval = setInterval(async () => {
      try {
        setIsAnalyzing(true);
        
        // Simulate pattern detection
        const detectedPatterns = await analyzePatterns();
        setPatterns(detectedPatterns);
        
        // Update neuron activity
        updateNeuronActivity();
        
      } catch (error) {
        console.error("Error in real-time analysis:", error);
      } finally {
        setIsAnalyzing(false);
      }
    }, 5000);

    return () => clearInterval(interval);
  };

  // Simulate pattern analysis
  const analyzePatterns = async (): Promise<PatternData[]> => {
    const detectedPatterns: PatternData[] = [];
    
    // Randomly detect patterns with high confidence
    if (Math.random() > 0.7) {
      const patterns = [
        "Head and Shoulders", "Double Top", "Double Bottom", 
        "Ascending Triangle", "Descending Triangle", "Bull Flag", "Bear Flag"
      ];
      
      const pattern = patterns[Math.floor(Math.random() * patterns.length)];
      const isBullish = pattern.includes("Bull") || pattern.includes("Bottom") || pattern.includes("Ascending");
      
      detectedPatterns.push({
        id: `pattern_${Date.now()}`,
        name: pattern,
        type: isBullish ? "bullish" : "bearish",
        confidence: 75 + Math.random() * 20,
        coordinates: [[0, 0], [1, 1]],
        prediction: 1.1650 + (Math.random() - 0.5) * 0.01,
        probability: 0.8 + Math.random() * 0.15,
        timeframe: selectedTimeframe,
        detected_at: new Date()
      });
    }
    
    return detectedPatterns;
  };

  // Update neuron activity visualization
  const updateNeuronActivity = () => {
    const activity = Array.from({ length: 20 }, () => Math.random());
    setNeuronsActivity(activity);
  };

  return (
    <div className="space-y-6">
      {/* AI Status Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quantum-panel p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <motion.div
              animate={isAnalyzing ? { rotate: 360 } : {}}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Brain className="w-8 h-8 text-quantum-primary" />
            </motion.div>
            AI Pattern Recognition
          </h2>
          
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isAnalyzing ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
            <span className="text-sm text-gray-400">
              {isAnalyzing ? "Analyzing..." : "Standby"}
            </span>
          </div>
        </div>

        {/* AI Models Status */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {aiModels.map((model, index) => (
            <motion.div
              key={model.name}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 rounded-lg p-4 text-center"
            >
              <div className="flex items-center justify-center mb-2">
                {model.isLoaded ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Cpu className="w-5 h-5 text-gray-400 animate-pulse" />
                )}
              </div>
              <p className="text-sm font-medium text-white">{model.name}</p>
              <p className="text-xs text-gray-400">Accuracy: {model.accuracy}%</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Detected Patterns */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quantum-panel p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-white flex items-center gap-2">
            <Eye className="w-6 h-6 text-quantum-accent" />
            Detected Patterns
          </h3>
          <span className="text-sm text-gray-400">
            {patterns.length} pattern(s) detected
          </span>
        </div>

        <div className="space-y-3">
          {patterns.map((pattern, index) => (
            <motion.div
              key={pattern.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    pattern.type === 'bullish' ? 'bg-green-400' :
                    pattern.type === 'bearish' ? 'bg-red-400' : 'bg-yellow-400'
                  }`} />
                  <div>
                    <p className="font-semibold text-white">{pattern.name}</p>
                    <p className="text-sm text-gray-400">
                      {pattern.timeframe} • {pattern.detected_at.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-2 mb-1">
                    <Target className="w-4 h-4 text-quantum-primary" />
                    <span className="text-sm font-mono text-white">
                      {pattern.prediction.toFixed(5)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-white/10 rounded-full h-2">
                      <motion.div
                        className="bg-quantum-primary h-full rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${pattern.confidence}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                    <span className="text-xs text-gray-400">
                      {pattern.confidence.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
          
          {patterns.length === 0 && (
            <div className="text-center py-8">
              <Sparkles className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-400">No patterns detected yet</p>
              <p className="text-sm text-gray-500">AI is continuously scanning...</p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Neural Network Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quantum-panel p-6"
      >
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Zap className="w-6 h-6 text-quantum-primary" />
          Neural Network Activity
        </h3>
        
        <div className="grid grid-cols-10 gap-2">
          {neuronsActivity.map((activity, index) => (
            <motion.div
              key={index}
              className="aspect-square rounded-full bg-quantum-primary/20 flex items-center justify-center"
              animate={{
                opacity: 0.3 + activity * 0.7,
                scale: 0.8 + activity * 0.4
              }}
              transition={{ duration: 0.5 }}
            >
              <div
                className="w-2 h-2 rounded-full bg-quantum-primary"
                style={{ opacity: activity }}
              />
            </motion.div>
          ))}
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-400">
            Network Processing: {neuronsActivity.filter(a => a > 0.7).length} active neurons
          </p>
        </div>
      </motion.div>

      {/* AI Predictions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="quantum-panel p-6"
      >
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-green-400" />
          AI Price Predictions
        </h3>
        
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-sm text-gray-400">Next Hour</p>
            <p className="text-lg font-bold text-green-400">
              +{((Math.random() * 2) - 1).toFixed(3)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Next 4 Hours</p>
            <p className="text-lg font-bold text-blue-400">
              +{((Math.random() * 4) - 2).toFixed(3)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Next Day</p>
            <p className="text-lg font-bold text-purple-400">
              +{((Math.random() * 6) - 3).toFixed(3)}%
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
} 