"use client";

import React from 'react';
import QuantumLayout from '@/components/layout/QuantumLayout';
import StoryFeed from '@/components/market-narrator/StoryFeed';
import InfluenceMap from '@/components/market-narrator/InfluenceMap';
import { motion } from 'framer-motion';
import { BookOpen, Brain, Sparkles, TrendingUp } from 'lucide-react';

export default function MarketNarratorPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  // Mock correlations for the influence map
  const mockCorrelations = {
    'EURUSD': {
      'GBPUSD': 0.85,
      'DXY': -0.92,
      'XAUUSD': -0.45,
      'USDJPY': -0.78
    },
    'XAUUSD': {
      'DXY': -0.88,
      'USDCHF': -0.72,
      'EURUSD': 0.45,
      'SILVER': 0.92
    }
  };

  return (
    <QuantumLayout>
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-black to-gray-900">
        <div className="container mx-auto px-4 py-8">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-8"
          >
        {/* Header */}
            <motion.div variants={itemVariants} className="text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <BookOpen className="w-8 h-8 text-quantum-primary" />
                <h1 className="text-4xl font-bold bg-gradient-to-r from-quantum-primary to-quantum-secondary bg-clip-text text-transparent">
            Market Narrator
          </h1>
                <Brain className="w-8 h-8 text-quantum-secondary" />
              </div>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                AI-powered market stories that reveal hidden patterns and correlations through narrative intelligence
              </p>
            </motion.div>

            {/* Stats Overview */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { label: 'Stories Today', value: '12', icon: BookOpen, color: 'text-blue-400' },
                { label: 'Correlations Found', value: '47', icon: Sparkles, color: 'text-yellow-400' },
                { label: 'Impact Score', value: '8.4', icon: TrendingUp, color: 'text-green-400' },
                { label: 'AI Confidence', value: '92%', icon: Brain, color: 'text-purple-400' }
              ].map((stat, index) => (
                <div key={index} className="quantum-panel p-6 text-center">
                  <stat.icon className={`w-8 h-8 ${stat.color} mx-auto mb-2`} />
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-sm text-gray-400">{stat.label}</p>
              </div>
              ))}
            </motion.div>

            {/* Main Content */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Story Feed - Takes 2 columns */}
              <div className="lg:col-span-2">
                <StoryFeed />
              </div>

              {/* Influence Maps - Takes 1 column */}
              <div className="lg:col-span-1 space-y-6">
                {Object.entries(mockCorrelations).map(([protagonist, correlations]) => (
                  <div key={protagonist} className="quantum-panel p-6">
                    <InfluenceMap 
                      protagonist={protagonist}
                      correlations={correlations}
                    />
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </QuantumLayout>
  );
} 
