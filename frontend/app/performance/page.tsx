"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import QuantumLayout from "@/components/layout/QuantumLayout";
import EquityCurveChart from "@/components/performance/EquityCurveChart";
import PerformanceMetrics from "@/components/performance/PerformanceMetrics";
import { api } from "@/utils/api-discovery";
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
  const [equityData, setEquityData] = useState<EquityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState("30D");

  const fetchEquityData = useCallback(async () => {
    setLoading(true);
    try {
      // Dinamik API endpoint kullan
      const data = await api.get<{ equity_curve: EquityData[] }>('equityCurve');
      setEquityData(data.equity_curve || []);
    } catch (error) {
      console.error("Error fetching equity data:", error);
      // Fallback to mock data if API fails
      setEquityData([
        { date: "2024-01-01", equity: 10000, drawdown: 0 },
        { date: "2024-01-02", equity: 10150, drawdown: 0 },
        { date: "2024-01-03", equity: 10280, drawdown: 0 },
        { date: "2024-01-04", equity: 10100, drawdown: -1.75 },
        { date: "2024-01-05", equity: 10350, drawdown: 0 },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEquityData();
    const interval = setInterval(fetchEquityData, 60000); // Update every 60 seconds
    return () => clearInterval(interval);
  }, [fetchEquityData]);

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
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Metrikler ve Özet - PerformanceMetrics kendi verisini çekiyor */}
        <motion.div variants={itemVariants}>
          <PerformanceMetrics />
        </motion.div>

        {/* Grafikler */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="quantum-panel p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Equity Curve</h3>
            <div className="h-80">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <RefreshCw className="w-8 h-8 text-quantum-primary animate-spin" />
                </div>
              ) : (
                <EquityCurveChart data={equityData} />
              )}
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