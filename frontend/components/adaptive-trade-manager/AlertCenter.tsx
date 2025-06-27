'use client'
import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, CheckCircle, Info, X, Zap, Brain } from 'lucide-react'

// Mock type for Alert
interface AdaptiveAlert {
    alert_id: string;
    timestamp: string;
    position_ticket: number;
    title: string;
    description: string;
    urgency: number;
}

interface AlertCenterProps {
  alerts: AdaptiveAlert[];
  onDismiss: (alertId: string) => void;
}

const alertStyles = {
  5: { icon: AlertTriangle, color: 'red-500', bg: 'bg-red-500/10', border: 'border-red-500/50' },
  4: { icon: AlertTriangle, color: 'orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/50' },
  3: { icon: Info, color: 'yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/50' },
  2: { icon: Brain, color: 'cyan-500', bg: 'bg-cyan-500/10', border: 'border-cyan-500/50' },
  1: { icon: Zap, color: 'green-500', bg: 'bg-green-500/10', border: 'border-green-500/50' },
}

export default function AlertCenter({ alerts, onDismiss }: AlertCenterProps) {
  const [visibleAlerts, setVisibleAlerts] = useState(alerts);

  useEffect(() => {
    setVisibleAlerts(alerts);
  }, [alerts]);

  const handleDismiss = (alertId: string) => {
    onDismiss(alertId);
    setVisibleAlerts(prevAlerts => prevAlerts.filter(a => a.alert_id !== alertId));
  }
  
  return (
    <div className="fixed top-24 right-6 w-96 z-50">
      <AnimatePresence>
        {visibleAlerts.slice(0, 5).map((alert, index) => {
          const style = alertStyles[alert.urgency] || alertStyles[3];
          const Icon = style.icon;

          return (
            <motion.div
              key={alert.alert_id}
              layout
              initial={{ opacity: 0, y: 50, scale: 0.5 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.5 }}
              transition={{ duration: 0.5, type: 'spring' }}
              className={`relative rounded-xl overflow-hidden border ${style.border} ${style.bg}
                          backdrop-blur-xl shadow-2xl mb-4`}
            >
              <div className={`absolute left-0 top-0 bottom-0 w-1.5 bg-${style.color}`} />
              <div className="pl-6 pr-4 py-4">
                <div className="flex items-start gap-3">
                  <Icon className={`w-6 h-6 flex-shrink-0 mt-1 text-${style.color}`} />
                  <div className="flex-grow">
                    <h4 className={`font-bold text-white`}>{alert.title}</h4>
                    <p className="text-sm text-gray-300 mt-1">{alert.description}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      Ticket #{alert.position_ticket} - {new Date(alert.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  <button 
                    onClick={() => handleDismiss(alert.alert_id)} 
                    className="p-1 rounded-full text-gray-500 hover:bg-gray-700/50 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
} 