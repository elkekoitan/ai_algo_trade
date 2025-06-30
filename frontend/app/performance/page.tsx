"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import QuantumLayout from "@/components/layout/QuantumLayout";
import EquityCurveChart from "@/components/performance/EquityCurveChart";
import PerformanceMetrics from "@/components/performance/PerformanceMetrics";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  Target,
  Shield,
  Activity,
  BarChart3,
  Calendar,
  RefreshCw,
  Award,
  AlertTriangle,
  Zap,
  Clock,
  Percent
} from "lucide-react";

interface PerformanceSummary {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  total_loss: number;
  net_profit: number;
  profit_factor: number;
  max_drawdown: number;
  sharpe_ratio: number;
  daily_return: number;
  monthly_return: number;
  yearly_return: number;
}

interface EquityData {
  date: string;
  equity: number;
  drawdown: number;
}

export default function QuantumPerformancePage() {
  const [performanceData, setPerformanceData] = useState<PerformanceSummary | null>(null);
  const [equityData, setEquityData] = useState<EquityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState("30D");

  const fetchPerformanceData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8002/api/live-performance"); // CANLI API'YE GÜNCELLENDİ

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setPerformanceData(data.summary);
          setEquityData(data.equity_curve);
        }
      }
    } catch (error) {
      console.error("Error fetching performance data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 60000); // Update every 60 seconds
    return () => clearInterval(interval);
  }, [fetchPerformanceData]);

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

  const getPerformanceColor = (value: number, isPositive: boolean = true) => {
    if (isPositive) {
      return value >= 0 ? "text-green-400" : "text-red-400";
    }
    return value <= 0 ? "text-green-400" : "text-red-400";
  };

  if (loading || !performanceData) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="w-8 h-8 text-quantum-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Metrikler ve Özet */}
        <motion.div variants={itemVariants}>
          <PerformanceMetrics data={performanceData} />
        </motion.div>

        {/* Grafikler */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="quantum-panel p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Equity Curve</h3>
            <div className="h-80">
              <EquityCurveChart data={equityData} />
            </div>
          </div>
          <div className="quantum-panel p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Monthly Returns</h3>
            {/* Buraya Bar Chart gelecek */}
            <div className="h-80 flex items-center justify-center text-gray-500">
              Bar Chart Component Coming Soon
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
} 