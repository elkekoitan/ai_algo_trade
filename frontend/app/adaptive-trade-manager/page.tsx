'use client'
import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import QuantumLayout from '@/components/layout/QuantumLayout'
import TradeMonitor from '@/components/adaptive-trade-manager/TradeMonitor'
import RiskDashboard from '@/components/adaptive-trade-manager/RiskDashboard'
import AlertCenter from '@/components/adaptive-trade-manager/AlertCenter'
import { Shield, Activity } from 'lucide-react'

// Mock types
interface ManagedPosition {
  ticket: number; symbol: string; position_type: 'buy' | 'sell'; volume: number;
  open_price: number; current_price: number; pnl: number; pips: number; open_time: string;
}
interface RiskMetrics { position_ticket: number; risk_level: 'low' | 'medium' | 'high' | 'critical'; risk_score: number; symbol: string; volume: number; }
interface DashboardData { portfolio_risk_score: number; portfolio_risk_level: string; }
interface AdaptiveAlert {
    alert_id: string; timestamp: string; position_ticket: number;
    title: string; description: string; urgency: number;
    recommended_action: { action_type: string; description: string; parameters: any; };
}

export default function AdaptiveTradeManagerPage() {
  const [positions, setPositions] = useState<ManagedPosition[]>([])
  const [risks, setRisks] = useState<RiskMetrics[]>([])
  const [dashboardData, setDashboardData] = useState<DashboardData>({ portfolio_risk_score: 0, portfolio_risk_level: 'low' })
  const [alerts, setAlerts] = useState<AdaptiveAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [posRes, riskRes, dashRes] = await Promise.all([
          fetch('/api/v1/atm/positions'),
          fetch('/api/v1/atm/risk-metrics'),
          fetch('/api/v1/atm/dashboard')
        ]);
        const posData = await posRes.json();
        const riskData = await riskRes.json();
        const dashData = await dashRes.json();

        setPositions(posData);
        setRisks(riskData);
        setDashboardData(dashData);
      } catch (error) {
        console.error("Failed to fetch initial data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    
    // WebSocket for alerts
    const ws = new WebSocket(`ws://${window.location.host}/api/v1/atm/ws/alerts`);
    ws.onmessage = (event) => {
      const newAlert: AdaptiveAlert = JSON.parse(event.data);
      setAlerts(prevAlerts => [newAlert, ...prevAlerts]);
    };
    ws.onclose = () => console.log('ATM WebSocket closed');
    ws.onerror = (error) => console.error('ATM WebSocket error:', error);

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const handleDismissAlert = (alertId: string) => {
    setAlerts(prevAlerts => prevAlerts.filter(a => a.alert_id !== alertId));
  };

  if (isLoading) {
    return (
      <QuantumLayout>
        <div className="flex items-center justify-center min-h-screen">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Activity className="w-16 h-16 text-cyan-400" />
          </motion.div>
        </div>
      </QuantumLayout>
    );
  }

  return (
    <QuantumLayout>
      <AlertCenter alerts={alerts} onDismiss={handleDismissAlert} />
      <div className="p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 
                       bg-clip-text text-transparent flex items-center gap-3">
            <Shield className="w-10 h-10 text-cyan-400" />
            Adaptive Trade Manager
          </h1>
          <p className="text-gray-400 mt-2">
            AI-powered protection and optimization for your live trades.
          </p>
        </motion.div>

        {/* Risk Dashboard */}
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
        >
            <RiskDashboard risks={risks} data={dashboardData}/>
        </motion.div>
        
        {/* Live Positions */}
         <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
        >
            <TradeMonitor positions={positions} risks={risks} alerts={alerts} />
        </motion.div>
      </div>
    </QuantumLayout>
  )
} 