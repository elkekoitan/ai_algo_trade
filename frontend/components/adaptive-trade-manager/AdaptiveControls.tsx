'use client'
import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Check, ShieldCheck, Zap, AlertTriangle, X } from 'lucide-react'

interface AdaptiveControlsProps {
  alert: {
    position_ticket: number;
    title: string;
    recommended_action: {
        action_type: string;
        description: string;
        parameters: any;
    };
  } | undefined,
  riskScore?: number;
  ticket: number;
}

const actionIcons = {
  adjust_sl: <ShieldCheck className="w-4 h-4" />,
  adjust_tp: <ShieldCheck className="w-4 h-4" />,
  partial_close: <Zap className="w-4 h-4" />,
  full_close: <X className="w-4 h-4" />,
  default: <Brain className="w-4 h-4" />
}

export default function AdaptiveControls({ alert, riskScore, ticket }: AdaptiveControlsProps) {
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<'success' | 'error' | null>(null)

  const handleExecute = async () => {
    if (!alert) return;

    setIsExecuting(true);
    setExecutionResult(null);

    const { action_type, parameters } = alert.recommended_action;
    let url = `/api/v1/atm/actions/${ticket}/${action_type}`;
    if(parameters) {
        const query = new URLSearchParams(parameters).toString();
        url += `?${query}`;
    }

    try {
      const response = await fetch(url, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Action failed');
      }
      setExecutionResult('success');
    } catch (error) {
      console.error("Execution error:", error);
      setExecutionResult('error');
    } finally {
      setIsExecuting(false);
      setTimeout(() => setExecutionResult(null), 3000);
    }
  };

  const hasAlert = alert && alert.recommended_action.action_type !== 'do_nothing';

  return (
    <div className="mt-4 pt-4 border-t border-gray-700/50">
      <AnimatePresence mode="wait">
        {hasAlert ? (
          <motion.div
            key="alert"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-cyan-900/50 rounded-lg p-4 border border-cyan-500/30"
          >
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-full bg-cyan-500">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-cyan-300">AI Recommendation</h4>
                <p className="text-sm text-gray-300 mt-1">
                  {alert.recommended_action.description}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleExecute}
                    disabled={isExecuting || executionResult !== null}
                    className={`px-4 py-2 text-sm font-semibold rounded-lg flex items-center gap-2 transition-all duration-300
                        ${isExecuting ? 'bg-gray-600 text-gray-400' 
                        : executionResult === 'success' ? 'bg-green-500 text-white'
                        : executionResult === 'error' ? 'bg-red-500 text-white'
                        : 'bg-cyan-500 text-white hover:bg-cyan-400'}`}
                  >
                    {isExecuting ? (
                        <>
                            <Zap className="w-4 h-4 animate-ping" />
                            Executing...
                        </>
                    ) : executionResult === 'success' ? (
                        <>
                            <Check className="w-4 h-4" />
                            Success!
                        </>
                    ) : executionResult === 'error' ? (
                        <>
                            <AlertTriangle className="w-4 h-4" />
                            Failed
                        </>
                    ) : (
                        <>
                            {actionIcons[alert.recommended_action.action_type] || actionIcons.default}
                            Execute
                        </>
                    )}
                  </motion.button>
                  <button className="text-xs text-gray-400 hover:text-white transition-colors">
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="monitoring"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-sm"
          >
            <div className="flex items-center justify-center gap-2 text-gray-400">
              <ShieldCheck className="w-4 h-4 text-green-400" />
              <span>AI Protection Active</span>
            </div>
            {riskScore !== undefined && (
                <div className="w-full bg-gray-700 rounded-full h-1.5 mt-2">
                    <motion.div 
                        className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-1.5 rounded-full"
                        initial={{width: 0}}
                        animate={{width: `${riskScore}%`}}
                        transition={{duration: 0.5}}
                    />
                </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
} 