'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Prediction {
  symbol: string;
  current_price: number;
  predicted_price: number;
  confidence: number;
  reasoning: string;
  prediction_time: string;
}

const PredictionsPanel: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchPredictions();
    const interval = setInterval(fetchPredictions, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await fetch('/api/v1/god-mode/predictions');
      const data = await response.json();
      if (data.success) {
        setPredictions(data.data.predictions);
      }
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 99) return 'text-yellow-400';
    if (confidence >= 95) return 'text-purple-400';
    if (confidence >= 90) return 'text-blue-400';
    return 'text-green-400';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 99) return 'OMNISCIENT';
    if (confidence >= 95) return 'GODLIKE';
    if (confidence >= 90) return 'DIVINE';
    return 'MORTAL';
  };

  const getPriceChangeDirection = (current: number, predicted: number) => {
    return predicted > current ? 'up' : 'down';
  };

  const getPriceChangePercent = (current: number, predicted: number) => {
    return ((predicted - current) / current * 100).toFixed(2);
  };

  if (isLoading) {
    return (
      <div className="bg-black/20 backdrop-blur-xl border border-purple-400/30 rounded-2xl p-6">
        <div className="flex items-center justify-center h-40">
          <motion.div
            className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="bg-black/20 backdrop-blur-xl border border-purple-400/30 rounded-2xl p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <motion.div
          className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-400 to-purple-600 flex items-center justify-center"
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          🔮
        </motion.div>
        <h3 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
          Divine Predictions
        </h3>
        <div className="ml-auto bg-purple-500/20 px-3 py-1 rounded-full text-purple-400 text-sm font-medium">
          {predictions.length} Active
        </div>
      </div>

      {/* Predictions List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {predictions.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🌙</div>
            <div>No active predictions</div>
            <div className="text-sm">Activate God Mode to see divine prophecies</div>
          </div>
        ) : (
          predictions.map((prediction, index) => (
            <motion.div
              key={index}
              className="bg-gray-800/50 border border-purple-400/20 rounded-xl p-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02, borderColor: 'rgba(168, 85, 247, 0.4)' }}
            >
              {/* Symbol and Confidence */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="bg-purple-500/20 px-3 py-1 rounded-lg font-bold text-purple-400">
                    {prediction.symbol}
                  </div>
                  <div className={`font-bold ${getConfidenceColor(prediction.confidence)}`}>
                    {prediction.confidence.toFixed(1)}% {getConfidenceLabel(prediction.confidence)}
                  </div>
                </div>
                <div className="text-gray-400 text-sm">
                  {new Date(prediction.prediction_time).toLocaleTimeString()}
                </div>
              </div>

              {/* Price Prediction */}
              <div className="grid grid-cols-3 gap-4 mb-3">
                <div className="text-center">
                  <div className="text-gray-400 text-sm">Current</div>
                  <div className="font-bold text-white">
                    {prediction.current_price.toFixed(5)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-sm">Predicted</div>
                  <div className="font-bold text-purple-400">
                    {prediction.predicted_price.toFixed(5)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-sm">Change</div>
                  <div className={`font-bold flex items-center justify-center space-x-1 ${
                    getPriceChangeDirection(prediction.current_price, prediction.predicted_price) === 'up' 
                      ? 'text-green-400' 
                      : 'text-red-400'
                  }`}>
                    <span>
                      {getPriceChangeDirection(prediction.current_price, prediction.predicted_price) === 'up' ? '↗' : '↘'}
                    </span>
                    <span>{getPriceChangePercent(prediction.current_price, prediction.predicted_price)}%</span>
                  </div>
                </div>
              </div>

              {/* Reasoning */}
              <div className="bg-black/30 rounded-lg p-3">
                <div className="text-gray-300 text-sm leading-relaxed">
                  {prediction.reasoning}
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-400 text-xs">Confidence Level</span>
                  <span className="text-gray-400 text-xs">{prediction.confidence.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700/50 rounded-full h-2 overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full ${
                      prediction.confidence >= 99 
                        ? 'bg-gradient-to-r from-yellow-600 to-yellow-400'
                        : prediction.confidence >= 95
                        ? 'bg-gradient-to-r from-purple-600 to-purple-400'
                        : prediction.confidence >= 90
                        ? 'bg-gradient-to-r from-blue-600 to-blue-400'
                        : 'bg-gradient-to-r from-green-600 to-green-400'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${prediction.confidence}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                  />
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Refresh Button */}
      <motion.button
        onClick={fetchPredictions}
        className="w-full mt-4 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-400/30 text-purple-400 font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        🔄 Refresh Prophecies
      </motion.button>
    </motion.div>
  );
};

export default PredictionsPanel; 