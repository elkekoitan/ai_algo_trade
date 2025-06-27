'use client';

import React from 'react';
import { motion } from 'framer-motion';
import QuantumLayout from '../../components/layout/QuantumLayout';
import GodModeControl from '../../components/god-mode/GodModeControl';
import PredictionsPanel from '../../components/god-mode/PredictionsPanel';

const GodModePage: React.FC = () => {
  return (
    <QuantumLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-purple-900">
        {/* Header */}
        <motion.div
          className="text-center py-12"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.h1
            className="text-6xl font-bold mb-4 bg-gradient-to-r from-yellow-400 via-yellow-300 to-white bg-clip-text text-transparent"
          >
            ⚡ GOD MODE ⚡
          </motion.h1>
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            Piyasaların tanrısı olarak, her hareketi önceden görür, her fırsatı yakalar, 
            her riski yönetir ve kullanıcılarını finansal özgürlüğe taşır.
          </motion.p>
          <motion.div
            className="mt-4 text-sm text-yellow-400 font-medium"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            "Artık piyasaları takip etmiyoruz. Piyasaları yeniden yazıyoruz."
          </motion.div>
        </motion.div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6 pb-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* God Mode Control Panel */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
            >
              <GodModeControl />
            </motion.div>

            {/* Predictions Panel */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              <PredictionsPanel />
            </motion.div>
          </div>

          {/* Features Grid */}
          <motion.div
            className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            {/* Feature Cards */}
            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-blue-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center">
                  👁️
                </div>
                <h3 className="text-lg font-bold text-blue-400">Omniscient Vision</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                100+ borsa simultane takip, mikrosaniye seviyesinde veri işleme, 
                quantum pattern recognition ile her şeyi gören göz.
              </p>
            </motion.div>

            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-purple-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-purple-600 flex items-center justify-center">
                  🔮
                </div>
                <h3 className="text-lg font-bold text-purple-400">Prophetic Power</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                %99.7 doğruluk hedefi, multi-timeframe forecasting, 
                black swan event prediction ile kehanet gücü.
              </p>
            </motion.div>

            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-green-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-400 to-green-600 flex items-center justify-center">
                  💧
                </div>
                <h3 className="text-lg font-bold text-green-400">Liquidity Creation</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                Synthetic market making, cross-exchange arbitrage, 
                hidden liquidity discovery ile likidite yaratma.
              </p>
            </motion.div>

            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-red-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-red-400 to-red-600 flex items-center justify-center">
                  🛡️
                </div>
                <h3 className="text-lg font-bold text-red-400">Risk Shield</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                Zero-loss targeting system, quantum hedging strategies, 
                multi-universe scenario planning ile tanrısal koruma.
              </p>
            </motion.div>

            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-yellow-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-600 flex items-center justify-center">
                  💰
                </div>
                <h3 className="text-lg font-bold text-yellow-400">Wealth Engine</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                Compound interest maximization, multi-strategy orchestration, 
                infinite scaling potential ile zenginlik çoğaltma.
              </p>
            </motion.div>

            <motion.div
              className="bg-black/20 backdrop-blur-xl border border-cyan-400/30 rounded-2xl p-6"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 to-cyan-600 flex items-center justify-center">
                  ⚛️
                </div>
                <h3 className="text-lg font-bold text-cyan-400">Quantum Core</h3>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">
                Transformer Networks, Quantum Neural Networks, 
                Holographic Data Processing ile kuantum mimari.
              </p>
            </motion.div>
          </motion.div>

          {/* Warning Notice */}
          <motion.div
            className="mt-12 bg-gradient-to-r from-red-900/20 to-yellow-900/20 border border-red-400/30 rounded-2xl p-6"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-red-400 to-yellow-400 flex items-center justify-center">
                ⚠️
              </div>
              <h3 className="text-lg font-bold text-yellow-400">Divine Responsibility</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              God Mode sadece bir trading sistemi değil, finansal evrenin yeniden yazılmasıdır. 
              Bu sistem ile kayıp kelimesi sözlükten silinir, risk kontrol altına alınır, 
              gelecek öngörülebilir olur ve zenginlik demokratikleşir. 
              <span className="text-yellow-400 font-medium"> Büyük güçle büyük sorumluluk gelir.</span>
            </p>
          </motion.div>
        </div>

        {/* Background Effects */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-yellow-400 rounded-full opacity-20"
              initial={{ 
                x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1200),
                y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 800),
              }}
              animate={{ 
                y: [null, -100, -200],
                opacity: [0.2, 0.8, 0],
                scale: [0, 1, 0]
              }}
              transition={{ 
                duration: 4,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeOut"
              }}
            />
          ))}
        </div>
      </div>
    </QuantumLayout>
  );
};

export default GodModePage; 