"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Mic, 
  Brain, 
  Zap, 
  MessageSquare,
  TrendingUp,
  VolumeX,
  Volume2,
  Sparkles
} from 'lucide-react';
import QuantumLayout from '@/components/layout/QuantumLayout';
import VoiceTradingPanel from '@/components/ai/VoiceTradingPanel';

export default function VoiceTradingPage() {
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
                <Mic className="w-8 h-8 text-quantum-primary" />
                <h1 className="text-4xl font-bold bg-gradient-to-r from-quantum-primary to-quantum-secondary bg-clip-text text-transparent">
                  Voice Trading AI
                </h1>
                <Brain className="w-8 h-8 text-quantum-secondary" />
              </div>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                Trade with your voice using advanced AI. Simply speak your commands and let AI execute your trades with precision.
              </p>
            </motion.div>

            {/* Features Overview */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Voice Recognition', value: '99.8%', icon: Mic, color: 'text-blue-400' },
                { label: 'AI Accuracy', value: '96.2%', icon: Brain, color: 'text-purple-400' },
                { label: 'Response Time', value: '< 500ms', icon: Zap, color: 'text-yellow-400' },
                { label: 'Languages', value: '12+', icon: MessageSquare, color: 'text-green-400' }
              ].map((stat, index) => (
                <div key={index} className="quantum-panel p-6 text-center">
                  <stat.icon className={`w-8 h-8 ${stat.color} mx-auto mb-2`} />
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-sm text-gray-400">{stat.label}</p>
                </div>
              ))}
            </motion.div>

            {/* Main Voice Panel */}
            <motion.div variants={itemVariants}>
              <VoiceTradingPanel />
            </motion.div>

            {/* Features Grid */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  icon: Brain,
                  title: "AI-Powered Understanding",
                  description: "Advanced natural language processing understands complex trading commands with context and intent recognition.",
                  color: "text-purple-400"
                },
                {
                  icon: Zap,
                  title: "Lightning Fast Execution",
                  description: "Sub-second latency from voice command to trade execution with optimized AI processing pipeline.",
                  color: "text-yellow-400"
                },
                {
                  icon: TrendingUp,
                  title: "Smart Trade Analysis",
                  description: "AI analyzes market conditions and provides intelligent suggestions before executing your trades.",
                  color: "text-green-400"
                },
                {
                  icon: Volume2,
                  title: "Natural Voice Feedback",
                  description: "Receive spoken confirmations and market updates in natural, conversational language.",
                  color: "text-blue-400"
                },
                {
                  icon: Sparkles,
                  title: "Multi-Language Support",
                  description: "Trade in your native language with support for 12+ languages and regional dialects.",
                  color: "text-pink-400"
                },
                {
                  icon: MessageSquare,
                  title: "Conversational Trading",
                  description: "Have natural conversations about markets, ask questions, and get personalized trading advice.",
                  color: "text-cyan-400"
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02, y: -5 }}
                  className="quantum-panel p-6"
                >
                  <feature.icon className={`w-12 h-12 ${feature.color} mb-4`} />
                  <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* Voice Commands Guide */}
            <motion.div variants={itemVariants} className="quantum-panel p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <MessageSquare className="w-6 h-6 text-quantum-primary" />
                Voice Commands Guide
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-quantum-primary mb-4">Trading Commands</h3>
                  <div className="space-y-3">
                    {[
                      "Buy EURUSD with 0.1 lot",
                      "Sell Bitcoin at market price",
                      "Close all my positions",
                      "Set stop loss at 1.0900",
                      "Place a buy limit at 1.0950",
                      "Increase position size to 0.5 lot"
                    ].map((command, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-gray-800/30 rounded-lg">
                        <div className="w-2 h-2 bg-quantum-primary rounded-full mt-2"></div>
                        <span className="text-gray-300 italic">"{command}"</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-quantum-secondary mb-4">Information Commands</h3>
                  <div className="space-y-3">
                    {[
                      "What's the price of Gold?",
                      "Show me GBPUSD chart",
                      "How is my portfolio performing?",
                      "What are the top gainers today?",
                      "Give me a market summary",
                      "What's my account balance?"
                    ].map((command, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-gray-800/30 rounded-lg">
                        <div className="w-2 h-2 bg-quantum-secondary rounded-full mt-2"></div>
                        <span className="text-gray-300 italic">"{command}"</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mt-8 p-4 bg-quantum-primary/10 border border-quantum-primary/30 rounded-lg">
                <p className="text-quantum-primary text-sm">
                  <strong>Pro Tip:</strong> Speak naturally! Our AI understands context, so you can say things like 
                  "Buy some Euro" instead of the formal "Buy EURUSD". The AI will ask for clarification when needed.
                </p>
              </div>
            </motion.div>

            {/* Safety Features */}
            <motion.div variants={itemVariants} className="quantum-panel p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <Brain className="w-6 h-6 text-green-400" />
                AI Safety & Risk Management
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    title: "Smart Confirmation",
                    description: "AI asks for confirmation on large trades or unusual commands to prevent mistakes."
                  },
                  {
                    title: "Risk Assessment",
                    description: "Every command is analyzed for risk before execution with automatic safety limits."
                  },
                  {
                    title: "Learning Protection",
                    description: "AI learns your trading patterns and warns about potentially harmful deviations."
                  }
                ].map((safety, index) => (
                  <div key={index} className="text-center">
                    <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Brain className="w-8 h-8 text-green-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{safety.title}</h3>
                    <p className="text-gray-400">{safety.description}</p>
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