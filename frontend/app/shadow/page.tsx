'use client';

import React from 'react';
import { motion } from 'framer-motion';
import QuantumLayout from '@/components/layout/QuantumLayout';
import ShadowControlPanel from '@/components/shadow-mode/ShadowControlPanel';
import InstitutionalRadar from '@/components/shadow-mode/InstitutionalRadar';
import WhaleTracker from '@/components/shadow-mode/WhaleTracker';
import DarkPoolMonitor from '@/components/shadow-mode/DarkPoolMonitor';

export default function ShadowModePage() {
  return (
    <QuantumLayout>
      <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden bg-gradient-to-r from-orange-500/10 via-red-500/10 to-purple-500/10 border-b border-orange-500/20"
        >
          <div className="absolute inset-0 bg-black/50"></div>
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-orange-400 via-red-400 to-purple-400 bg-clip-text text-transparent mb-4"
              >
                🥷 SHADOW MODE
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-xl md:text-2xl text-gray-300 mb-2"
              >
                Büyük Oyuncuların Gölgesinde Hareket Et
              </motion.p>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-lg text-orange-400 font-semibold"
              >
                "Onlar gibi düşün, onlar gibi kazan"
              </motion.p>
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Control Panel */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <ShadowControlPanel />
          </motion.div>

          {/* Monitoring Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <InstitutionalRadar />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <WhaleTracker />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 }}
              className="lg:col-span-2 xl:col-span-1"
            >
              <DarkPoolMonitor />
            </motion.div>
          </div>

          {/* Features Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="bg-black/40 backdrop-blur-xl border border-orange-500/30 rounded-2xl p-8 mb-8"
          >
            <h2 className="text-3xl font-bold text-white mb-6 text-center">
              🥷 Shadow Mode Özellikleri
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">🏛️</div>
                <h3 className="text-xl font-semibold text-white mb-2">Kurumsal Takip</h3>
                <p className="text-gray-400">
                  Goldman Sachs, BlackRock, JPMorgan gibi büyük kurumların hareketlerini gerçek zamanlı takip et.
                </p>
              </div>
              
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">🐋</div>
                <h3 className="text-xl font-semibold text-white mb-2">Whale Detector</h3>
                <p className="text-gray-400">
                  Büyük pozisyonları tespit et, whale'lerin stratejilerini analiz et ve onları takip et.
                </p>
              </div>
              
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">🌑</div>
                <h3 className="text-xl font-semibold text-white mb-2">Dark Pool Monitor</h3>
                <p className="text-gray-400">
                  Gizli likidite havuzlarını izle, arbitraj fırsatlarını yakala ve price improvement'tan faydallan.
                </p>
              </div>
              
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">🥷</div>
                <h3 className="text-xl font-semibold text-white mb-2">Stealth Execution</h3>
                <p className="text-gray-400">
                  Emirlerini parçala, rastgele zamanlamayla yürüt ve tespit edilmeden büyük pozisyonlar aç.
                </p>
              </div>
              
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">🔍</div>
                <h3 className="text-xl font-semibold text-white mb-2">Manipulation Detection</h3>
                <p className="text-gray-400">
                  Spoofing, stop-hunt, pump-dump gibi manipulation pattern'lerini tespit et ve korun.
                </p>
              </div>
              
              <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-700/50">
                <div className="text-2xl mb-3">📊</div>
                <h3 className="text-xl font-semibold text-white mb-2">Shadow Portfolio</h3>
                <p className="text-gray-400">
                  Kurumsal portföyleri replike et, risk-adjusted takip yap ve alpha elde et.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Warning Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">⚠️</span>
              <h3 className="text-xl font-bold text-red-400">Gizlilik Uyarısı</h3>
            </div>
            <p className="text-gray-300 mb-4">
              Shadow Mode, kurumsal yatırımcıların stratejilerini taklit etmek için tasarlanmıştır. 
              Bu sistem son derece güçlüdür ve dikkatli kullanılmalıdır.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2 text-yellow-400">
                <span>🔒</span>
                <span>Tüm aktiviteler şifrelenir</span>
              </div>
              <div className="flex items-center gap-2 text-yellow-400">
                <span>🥷</span>
                <span>Stealth mode her zaman aktif</span>
              </div>
              <div className="flex items-center gap-2 text-yellow-400">
                <span>📊</span>
                <span>Sadece yasal arbitraj fırsatları</span>
              </div>
              <div className="flex items-center gap-2 text-yellow-400">
                <span>⚖️</span>
                <span>Düzenleyici kurallara uyum</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </QuantumLayout>
  );
} 