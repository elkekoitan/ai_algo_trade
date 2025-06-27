'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Rocket, Settings, Shield, Bell, CheckCircle, 
  AlertCircle, Loader2, ChevronRight, ChevronLeft,
  Server, TestTube, Mail, Power, GitBranch, Clock
} from 'lucide-react'

interface DeploymentConfig {
  symbol: string
  autoStart: boolean
  testMode: boolean
  notificationEmail?: string
  accountType: 'demo' | 'live'
  riskLimit?: number
  maxPositions?: number
}

interface DeploymentWizardProps {
  strategyId: string
  strategyName: string
  onDeploy: (config: DeploymentConfig) => Promise<void>
  onCancel: () => void
}

export default function DeploymentWizard({
  strategyId,
  strategyName,
  onDeploy,
  onCancel
}: DeploymentWizardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isDeploying, setIsDeploying] = useState(false)
  const [deploymentStatus, setDeploymentStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  
  const [config, setConfig] = useState<DeploymentConfig>({
    symbol: 'EURUSD',
    autoStart: false,
    testMode: true,
    accountType: 'demo',
    notificationEmail: '',
    riskLimit: 2,
    maxPositions: 1
  })

  const steps = [
    { id: 'account', title: 'Account Selection', icon: Server },
    { id: 'settings', title: 'Strategy Settings', icon: Settings },
    { id: 'risk', title: 'Risk Management', icon: Shield },
    { id: 'notifications', title: 'Notifications', icon: Bell },
    { id: 'review', title: 'Review & Deploy', icon: Rocket }
  ]

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleDeploy = async () => {
    setIsDeploying(true)
    setDeploymentStatus('deploying')
    setErrorMessage('')

    try {
      await onDeploy(config)
      setDeploymentStatus('success')
    } catch (error: any) {
      setDeploymentStatus('error')
      setErrorMessage(error.message || 'Deployment failed')
    } finally {
      setIsDeploying(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Account Selection
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Select Trading Account</h3>
              <p className="text-sm text-gray-400 mb-4">
                Choose where to deploy your strategy
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setConfig({ ...config, accountType: 'demo', testMode: true })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  config.accountType === 'demo'
                    ? 'border-cyan-500 bg-cyan-500/10'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                }`}
              >
                <TestTube className="w-8 h-8 text-cyan-400 mb-2" />
                <h4 className="font-semibold text-white">Demo Account</h4>
                <p className="text-xs text-gray-400 mt-1">Test with virtual funds</p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setConfig({ ...config, accountType: 'live', testMode: false })}
                className={`p-4 rounded-lg border-2 transition-all ${
                  config.accountType === 'live'
                    ? 'border-purple-500 bg-purple-500/10'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                }`}
              >
                <Server className="w-8 h-8 text-purple-400 mb-2" />
                <h4 className="font-semibold text-white">Live Account</h4>
                <p className="text-xs text-gray-400 mt-1">Trade with real funds</p>
              </motion.button>
            </div>

            {config.accountType === 'live' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4"
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-semibold text-yellow-400">Live Trading Warning</h5>
                    <p className="text-sm text-gray-300 mt-1">
                      You are about to deploy to a live account. Real money will be at risk. 
                      Make sure you have thoroughly tested this strategy.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )

      case 1: // Strategy Settings
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Strategy Settings</h3>
              <p className="text-sm text-gray-400 mb-4">
                Configure how your strategy will operate
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Trading Symbol
                </label>
                <select
                  value={config.symbol}
                  onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
                  className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-2 
                           text-white focus:outline-none focus:border-cyan-500 transition-all"
                >
                  <option value="EURUSD">EUR/USD</option>
                  <option value="GBPUSD">GBP/USD</option>
                  <option value="USDJPY">USD/JPY</option>
                  <option value="AUDUSD">AUD/USD</option>
                  <option value="XAUUSD">XAU/USD (Gold)</option>
                </select>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                <div>
                  <h4 className="font-medium text-white">Auto Start Trading</h4>
                  <p className="text-xs text-gray-400 mt-1">
                    Start trading immediately after deployment
                  </p>
                </div>
                <button
                  onClick={() => setConfig({ ...config, autoStart: !config.autoStart })}
                  className={`relative w-12 h-6 rounded-full transition-all ${
                    config.autoStart ? 'bg-cyan-500' : 'bg-gray-700'
                  }`}
                >
                  <motion.div
                    className="absolute top-1 w-4 h-4 bg-white rounded-full"
                    animate={{ left: config.autoStart ? '1.5rem' : '0.25rem' }}
                    transition={{ type: 'spring', stiffness: 300 }}
                  />
                </button>
              </div>

              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <GitBranch className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-medium text-blue-400">Version Control</span>
                </div>
                <p className="text-xs text-gray-300">
                  Your strategy will be automatically versioned and saved to AlgoForge
                </p>
              </div>
            </div>
          </motion.div>
        )

      case 2: // Risk Management
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Risk Management</h3>
              <p className="text-sm text-gray-400 mb-4">
                Set safety limits for your strategy
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Risk Limit per Trade (%)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0.5"
                    max="5"
                    step="0.5"
                    value={config.riskLimit}
                    onChange={(e) => setConfig({ ...config, riskLimit: parseFloat(e.target.value) })}
                    className="flex-1"
                  />
                  <span className="text-lg font-semibold text-cyan-400 w-12">
                    {config.riskLimit}%
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Maximum Open Positions
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 5, 10].map((num) => (
                    <button
                      key={num}
                      onClick={() => setConfig({ ...config, maxPositions: num })}
                      className={`py-2 rounded-lg font-medium transition-all ${
                        config.maxPositions === num
                          ? 'bg-cyan-500 text-white'
                          : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 
                            border border-green-500/30 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-medium text-green-400">Safety Features Active</h5>
                    <ul className="text-xs text-gray-300 mt-2 space-y-1">
                      <li>• Automatic stop-loss on all trades</li>
                      <li>• Daily loss limit protection</li>
                      <li>• Emergency shutdown capability</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )

      case 3: // Notifications
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Notifications</h3>
              <p className="text-sm text-gray-400 mb-4">
                Stay informed about your strategy's performance
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email Notifications
                </label>
                <input
                  type="email"
                  value={config.notificationEmail}
                  onChange={(e) => setConfig({ ...config, notificationEmail: e.target.value })}
                  placeholder="your@email.com"
                  className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-2 
                           text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 
                           transition-all"
                />
              </div>

              {config.notificationEmail && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-3"
                >
                  <p className="text-sm text-gray-400">You will receive notifications for:</p>
                  <div className="space-y-2">
                    {[
                      'Strategy deployment status',
                      'Trade executions',
                      'Daily performance summary',
                      'Risk limit warnings',
                      'System errors'
                    ].map((item, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-sm text-gray-300">{item}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )

      case 4: // Review & Deploy
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Review & Deploy</h3>
              <p className="text-sm text-gray-400 mb-4">
                Confirm your settings and deploy the strategy
              </p>
            </div>

            <div className="bg-gray-800/50 rounded-lg p-4 space-y-3">
              <h4 className="font-medium text-white mb-3">Deployment Summary</h4>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Strategy</span>
                  <span className="text-white font-medium">{strategyName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Account Type</span>
                  <span className={config.accountType === 'demo' ? 'text-cyan-400' : 'text-purple-400'}>
                    {config.accountType.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Symbol</span>
                  <span className="text-white">{config.symbol}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Auto Start</span>
                  <span className={config.autoStart ? 'text-green-400' : 'text-gray-400'}>
                    {config.autoStart ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Limit</span>
                  <span className="text-white">{config.riskLimit}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Positions</span>
                  <span className="text-white">{config.maxPositions}</span>
                </div>
                {config.notificationEmail && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Notifications</span>
                    <span className="text-white text-xs">{config.notificationEmail}</span>
                  </div>
                )}
              </div>
            </div>

            {deploymentStatus === 'success' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-green-900/20 border border-green-500/30 rounded-lg p-4"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <h5 className="font-semibold text-green-400">Deployment Successful!</h5>
                    <p className="text-sm text-gray-300 mt-1">
                      Your strategy has been deployed and is ready to trade.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}

            {deploymentStatus === 'error' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-red-900/20 border border-red-500/30 rounded-lg p-4"
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-semibold text-red-400">Deployment Failed</h5>
                    <p className="text-sm text-gray-300 mt-1">{errorMessage}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )
    }
  }

  return (
    <motion.div
      className="bg-gradient-to-b from-gray-900/95 to-black/95 rounded-2xl 
                border border-cyan-500/20 backdrop-blur-xl overflow-hidden
                max-w-2xl mx-auto"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 
                    border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Rocket className="w-6 h-6 text-cyan-400" />
            Deploy Strategy
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-300 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="px-6 py-4 border-b border-gray-800">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <motion.div
                className={`flex items-center justify-center w-10 h-10 rounded-full
                          transition-all ${
                  index <= currentStep
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                    : 'bg-gray-800 text-gray-500'
                }`}
                whileHover={{ scale: 1.1 }}
              >
                <step.icon className="w-5 h-5" />
              </motion.div>
              {index < steps.length - 1 && (
                <div className={`w-full h-0.5 mx-2 transition-all ${
                  index < currentStep ? 'bg-cyan-500' : 'bg-gray-800'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="mt-2 text-center">
          <p className="text-sm font-medium text-white">{steps[currentStep].title}</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 min-h-[400px]">
        <AnimatePresence mode="wait">
          {renderStepContent()}
        </AnimatePresence>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/20 to-purple-900/20 
                    border-t border-cyan-500/20">
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0 || isDeploying}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              currentStep === 0 || isDeploying
                ? 'bg-gray-800/30 text-gray-600 cursor-not-allowed'
                : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50'
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>

          {currentStep < steps.length - 1 ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleNext}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-500 
                       text-white rounded-lg hover:shadow-lg transition-all"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </motion.button>
          ) : (
            <motion.button
              whileHover={{ scale: deploymentStatus === 'success' ? 1 : 1.05 }}
              whileTap={{ scale: deploymentStatus === 'success' ? 1 : 0.95 }}
              onClick={deploymentStatus === 'success' ? onCancel : handleDeploy}
              disabled={isDeploying}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium
                       transition-all ${
                deploymentStatus === 'success'
                  ? 'bg-green-500 text-white'
                  : 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white hover:shadow-lg'
              }`}
            >
              {isDeploying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Deploying...
                </>
              ) : deploymentStatus === 'success' ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Done
                </>
              ) : (
                <>
                  <Rocket className="w-4 h-4" />
                  Deploy Now
                </>
              )}
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  )
} 