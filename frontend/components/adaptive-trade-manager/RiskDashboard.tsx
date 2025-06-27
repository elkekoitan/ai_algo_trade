'use client'
import React from 'react'
import { motion } from 'framer-motion'
import { Gauge, BarChart3, Shield, Activity } from 'lucide-react'
import { Pie, Bar } from 'react-chartjs-2'

// Mock types
interface RiskMetrics {
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    symbol: string;
    volume: number;
}
interface DashboardData {
    portfolio_risk_score: number;
    portfolio_risk_level: string;
}

interface RiskDashboardProps {
    risks: RiskMetrics[];
    data: DashboardData;
}

const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'rgba(34, 197, 94, 0.7)';
      case 'medium': return 'rgba(234, 179, 8, 0.7)';
      case 'high': return 'rgba(249, 115, 22, 0.7)';
      case 'critical': return 'rgba(239, 68, 68, 0.7)';
      default: return 'rgba(107, 114, 128, 0.7)';
    }
}

export default function RiskDashboard({ risks, data }: RiskDashboardProps) {
    const riskDistributionData = {
        labels: ['Low', 'Medium', 'High', 'Critical'],
        datasets: [{
            data: [
                risks.filter(r => r.risk_level === 'low').length,
                risks.filter(r => r.risk_level === 'medium').length,
                risks.filter(r => r.risk_level === 'high').length,
                risks.filter(r => r.risk_level === 'critical').length,
            ],
            backgroundColor: [
                'rgba(34, 197, 94, 0.7)',
                'rgba(234, 179, 8, 0.7)',
                'rgba(249, 115, 22, 0.7)',
                'rgba(239, 68, 68, 0.7)',
            ],
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
        }]
    };

    const exposureBySymbolData = {
        labels: [...new Set(risks.map(r => r.symbol))],
        datasets: [{
            label: 'Exposure',
            data: [...new Set(risks.map(r => r.symbol))].map(symbol => 
                risks.filter(r => r.symbol === symbol).reduce((acc, r) => acc + r.volume, 0)
            ),
            backgroundColor: 'rgba(34, 211, 238, 0.7)',
            borderColor: 'rgba(34, 211, 238, 1)',
            borderWidth: 1,
        }]
    }

    const chartOptions = (legendDisplay = false) => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: legendDisplay, labels: { color: '#9ca3af' } } },
        scales: {
            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
        }
    });

    const portfolioScoreColor = getRiskColor(data.portfolio_risk_level);

  return (
    <div className="bg-gray-900/50 rounded-2xl p-6 border border-gray-700/50 backdrop-blur-lg">
        <h2 className="text-2xl font-bold text-white mb-4">Portfolio Risk Dashboard</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Portfolio Risk Gauge */}
            <div className="md:col-span-1 flex flex-col items-center justify-center bg-gray-800/50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-300 mb-2">Overall Risk</h3>
                <div className="relative w-48 h-24">
                    <Gauge className="w-48 h-48 text-gray-700" strokeWidth={1}/>
                    <motion.div
                        className="absolute bottom-0 left-0 w-48 h-24 overflow-hidden"
                        initial={{'--angle': '0deg'}}
                        animate={{'--angle': `${data.portfolio_risk_score * 1.8}deg`}}
                        transition={{ duration: 1, ease: "circOut" }}
                        style={{
                            clipPath: 'polygon(0% 100%, 50% 100%, 50% 0, 0 0)',
                            transform: 'rotate(var(--angle))',
                            transformOrigin: 'bottom center',
                            background: `conic-gradient(from -90deg at 50% 100%, #10b981, #f59e0b, #ef4444)`,
                        }}
                    />
                </div>
                 <p className="text-4xl font-bold -mt-8" style={{color: portfolioScoreColor}}>
                    {data.portfolio_risk_score.toFixed(0)}
                </p>
                <p className="font-semibold" style={{color: portfolioScoreColor}}>
                    {data.portfolio_risk_level.toUpperCase()}
                </p>
            </div>

            {/* Risk Distribution */}
            <div className="md:col-span-2 bg-gray-800/50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-300 mb-2">Risk Distribution</h3>
                <div className="h-48">
                    <Pie data={riskDistributionData} options={chartOptions(true)} />
                </div>
            </div>

            {/* Exposure by Symbol */}
            <div className="md:col-span-3 bg-gray-800/50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-300 mb-2">Exposure by Symbol (Lots)</h3>
                <div className="h-48">
                    <Bar data={exposureBySymbolData} options={chartOptions()} />
                </div>
            </div>
        </div>
    </div>
  )
} 