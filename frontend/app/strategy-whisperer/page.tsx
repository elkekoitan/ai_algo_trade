'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import QuantumLayout from '@/components/layout/QuantumLayout'
import NaturalLanguageInput from '@/components/strategy-whisperer/NaturalLanguageInput'
import StrategyChat from '@/components/strategy-whisperer/StrategyChat'
import CodePreview from '@/components/strategy-whisperer/CodePreview'
import BacktestResults from '@/components/strategy-whisperer/BacktestResults'
import DeploymentWizard from '@/components/strategy-whisperer/DeploymentWizard'
import { 
  Brain, Sparkles, Code, Activity, Rocket, 
  MessageSquare, Zap, Shield, TrendingUp
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered' | 'read'
  type?: 'text' | 'code' | 'clarification' | 'parameters' | 'result'
  data?: any
}

export default function StrategyWhispererPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [currentStrategy, setCurrentStrategy] = useState<any>(null)
  const [generatedCode, setGeneratedCode] = useState<any>(null)
  const [backtestResult, setBacktestResult] = useState<any>(null)
  const [showDeployment, setShowDeployment] = useState(false)
  const [activeView, setActiveView] = useState<'chat' | 'code' | 'backtest'>('chat')

  useEffect(() => {
    // Initialize session
    setSessionId(`session_${Date.now()}`)
    
    // Welcome message
    setMessages([{
      id: '1',
      role: 'assistant',
      content: 'Merhaba! Ben Strategy Whisperer AI. Size nasıl bir trading stratejisi oluşturmamı istersiniz? Doğal dilde anlatın, gerisini ben halledeyim.',
      timestamp: new Date(),
      status: 'read',
      type: 'text'
    }])
  }, [])

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      status: 'sending',
      type: 'text'
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsProcessing(true)

    try {
      // Call API to process natural language
      const response = await fetch('/api/v1/strategy-whisperer/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          language: 'tr',
          session_id: sessionId
        })
      })

      const data = await response.json()

      // Update user message status
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'read' } : msg
      ))

      // Handle response based on state
      if (data.state === 'clarifying' && data.intent.clarifications_needed.length > 0) {
        // Add clarification messages
        data.intent.clarifications_needed.forEach((clarification: string, index: number) => {
          setTimeout(() => {
            setMessages(prev => [...prev, {
              id: `clarify_${Date.now()}_${index}`,
              role: 'assistant',
              content: clarification,
              timestamp: new Date(),
              status: 'read',
              type: 'clarification'
            }])
          }, 500 * (index + 1))
        })
      } else if (data.parameters) {
        // Strategy parameters ready
        setCurrentStrategy(data.parameters)
        
        // Add success message
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: `Harika! "${data.parameters.name}" stratejinizi oluşturdum. İşte detaylar:`,
          timestamp: new Date(),
          status: 'read',
          type: 'parameters',
          data: {
            'Strateji Tipi': data.parameters.type,
            'Zaman Dilimi': data.parameters.timeframe,
            'Risk Yönetimi': `${data.parameters.risk_value}%`,
            'Max Pozisyon': data.parameters.max_positions
          }
        }])

        // Generate code
        await generateCode(data.parameters)
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
        timestamp: new Date(),
        status: 'read',
        type: 'text'
      }])
    } finally {
      setIsProcessing(false)
    }
  }

  const generateCode = async (parameters: any) => {
    try {
      const response = await fetch('/api/v1/strategy-whisperer/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_parameters: parameters })
      })

      const code = await response.json()
      setGeneratedCode(code)

      // Add code message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `MQL5 kodunuz hazır! ${code.estimated_lines} satır optimize edilmiş kod ürettim.`,
        timestamp: new Date(),
        status: 'read',
        type: 'code',
        data: code
      }])

      // Suggest backtest
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Stratejinizi backtest etmek ister misiniz?',
          timestamp: new Date(),
          status: 'read',
          type: 'clarification',
          data: {
            options: ['Evet, backtest yap', 'Hayır, kodu göster']
          }
        }])
      }, 1000)
    } catch (error) {
      console.error('Code generation error:', error)
    }
  }

  const runBacktest = async () => {
    if (!currentStrategy) return

    setIsProcessing(true)
    
    try {
      const response = await fetch('/api/v1/strategy-whisperer/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: currentStrategy.name,
          symbol: currentStrategy.symbol,
          timeframe: currentStrategy.timeframe,
          start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date().toISOString()
        })
      })

      const result = await response.json()
      setBacktestResult(result)
      setActiveView('backtest')

      // Add result message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Backtest tamamlandı! ${result.totalTrades} işlem yapıldı, %${result.winRate.toFixed(1)} başarı oranı elde edildi.`,
        timestamp: new Date(),
        status: 'read',
        type: 'result',
        data: result
      }])
    } catch (error) {
      console.error('Backtest error:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDeploy = async (config: any) => {
    if (!generatedCode) return

    const response = await fetch('/api/v1/strategy-whisperer/deploy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        strategy_id: currentStrategy.name,
        code: generatedCode.code,
        ...config
      })
    })

    if (!response.ok) {
      throw new Error('Deployment failed')
    }

    return response.json()
  }

  const features = [
    {
      icon: MessageSquare,
      title: 'Doğal Dil İşleme',
      description: 'Stratejinizi kendi dilinizde anlatın'
    },
    {
      icon: Code,
      title: 'Otomatik Kod Üretimi',
      description: 'Optimize edilmiş MQL5 kodu'
    },
    {
      icon: Activity,
      title: 'Gerçek Zamanlı Backtest',
      description: 'Anında performans analizi'
    },
    {
      icon: Rocket,
      title: 'Tek Tık Deploy',
      description: 'MT5\'e otomatik yükleme'
    }
  ]

  return (
    <QuantumLayout>
      <div className="min-h-screen p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 
                           bg-clip-text text-transparent flex items-center gap-3">
                <Brain className="w-10 h-10 text-cyan-400" />
                Strategy Whisperer
              </h1>
              <p className="text-gray-400 mt-2">
                Doğal dilde strateji oluşturun, AI gerisini halleder
              </p>
            </div>

            {/* View switcher */}
            <div className="flex items-center gap-2 bg-gray-800/50 rounded-lg p-1">
              <button
                onClick={() => setActiveView('chat')}
                className={`px-4 py-2 rounded-md transition-all ${
                  activeView === 'chat'
                    ? 'bg-cyan-500 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Chat
              </button>
              {generatedCode && (
                <button
                  onClick={() => setActiveView('code')}
                  className={`px-4 py-2 rounded-md transition-all ${
                    activeView === 'code'
                      ? 'bg-cyan-500 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Code
                </button>
              )}
              {backtestResult && (
                <button
                  onClick={() => setActiveView('backtest')}
                  className={`px-4 py-2 rounded-md transition-all ${
                    activeView === 'backtest'
                      ? 'bg-cyan-500 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Backtest
                </button>
              )}
            </div>
          </div>

          {/* Feature cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 
                         rounded-lg p-4 border border-gray-700/50"
              >
                <feature.icon className="w-8 h-8 text-cyan-400 mb-2" />
                <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                <p className="text-xs text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left side - Input/Chat */}
          <div className="space-y-6">
            {messages.length === 1 ? (
              <NaturalLanguageInput
                onSubmit={handleSendMessage}
                isProcessing={isProcessing}
              />
            ) : (
              <StrategyChat
                messages={messages}
                onSendMessage={handleSendMessage}
                isTyping={isProcessing}
                sessionId={sessionId}
              />
            )}
          </div>

          {/* Right side - Results */}
          <div>
            <AnimatePresence mode="wait">
              {activeView === 'chat' && !generatedCode && !backtestResult && (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full flex items-center justify-center"
                >
                  <div className="text-center">
                    <Sparkles className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                    <p className="text-gray-500">
                      Stratejinizi anlatın, sonuçlar burada görünecek
                    </p>
                  </div>
                </motion.div>
              )}

              {activeView === 'code' && generatedCode && (
                <motion.div
                  key="code"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <CodePreview
                    code={generatedCode.code}
                    filename={`${currentStrategy?.name || 'strategy'}.mq5`}
                    version={generatedCode.version}
                    lines={generatedCode.estimated_lines}
                    performanceScore={generatedCode.performance_score}
                    optimizationHints={generatedCode.optimization_suggestions}
                  />
                </motion.div>
              )}

              {activeView === 'backtest' && backtestResult && (
                <motion.div
                  key="backtest"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <BacktestResults
                    result={backtestResult}
                    strategyName={currentStrategy?.name}
                    onDeploy={() => setShowDeployment(true)}
                    onOptimize={() => {
                      // Optimization logic
                    }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Deployment wizard modal */}
        <AnimatePresence>
          {showDeployment && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 
                       flex items-center justify-center p-4"
              onClick={() => setShowDeployment(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
              >
                <DeploymentWizard
                  strategyId={currentStrategy?.name || ''}
                  strategyName={currentStrategy?.name || 'Strategy'}
                  onDeploy={handleDeploy}
                  onCancel={() => setShowDeployment(false)}
                />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Floating action buttons */}
        <div className="fixed bottom-6 right-6 space-y-3">
          {generatedCode && !backtestResult && (
            <motion.button
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={runBacktest}
              className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 
                       text-white rounded-full shadow-lg hover:shadow-xl 
                       transition-all flex items-center gap-2"
            >
              <Activity className="w-5 h-5" />
              <span className="pr-2">Run Backtest</span>
            </motion.button>
          )}
          
          {backtestResult && (
            <motion.button
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowDeployment(true)}
              className="p-4 bg-gradient-to-r from-cyan-500 to-purple-500 
                       text-white rounded-full shadow-lg hover:shadow-xl 
                       transition-all flex items-center gap-2"
            >
              <Rocket className="w-5 h-5" />
              <span className="pr-2">Deploy Now</span>
            </motion.button>
          )}
        </div>
      </div>
    </QuantumLayout>
  )
} 