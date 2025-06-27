'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, User, Check, CheckCheck, Clock, AlertCircle, Sparkles } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered' | 'read'
  type?: 'text' | 'code' | 'clarification' | 'parameters' | 'result'
  data?: any
}

interface StrategyChatProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isTyping?: boolean
  sessionId?: string
}

export default function StrategyChat({ 
  messages, 
  onSendMessage, 
  isTyping = false,
  sessionId 
}: StrategyChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const renderMessageContent = (message: Message) => {
    switch (message.type) {
      case 'code':
        return (
          <div className="mt-2">
            <div className="text-xs text-gray-400 mb-1">Generated MQL5 Code:</div>
            <pre className="bg-black/50 p-3 rounded-lg overflow-x-auto">
              <code className="text-green-400 text-xs">{message.content}</code>
            </pre>
          </div>
        )
      
      case 'clarification':
        return (
          <div className="space-y-2">
            <p>{message.content}</p>
            {message.data?.options && (
              <div className="flex flex-wrap gap-2 mt-2">
                {message.data.options.map((option: string, index: number) => (
                  <button
                    key={index}
                    onClick={() => onSendMessage(option)}
                    className="px-3 py-1 bg-cyan-500/20 border border-cyan-500/30 
                             rounded-full text-sm hover:bg-cyan-500/30 transition-all"
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>
        )
      
      case 'parameters':
        return (
          <div className="space-y-2">
            <p className="mb-2">{message.content}</p>
            <div className="bg-black/30 p-3 rounded-lg text-sm">
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(message.data || {}).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-400">{key}:</span>
                    <span className="text-cyan-400">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )
      
      case 'result':
        return (
          <div className="space-y-2">
            <p className="mb-2">{message.content}</p>
            {message.data && (
              <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 
                            p-4 rounded-lg border border-green-500/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-green-400 font-semibold">Backtest Results</span>
                  <span className="text-xs text-gray-400">
                    {message.data.totalTrades} trades
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-400">Win Rate:</span>
                    <span className="ml-2 text-green-400">{message.data.winRate}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Profit:</span>
                    <span className="ml-2 text-green-400">
                      ${message.data.netProfit.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      
      default:
        return <p className="whitespace-pre-wrap">{message.content}</p>
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-500" />
      case 'sent':
        return <Check className="w-3 h-3 text-gray-400" />
      case 'delivered':
        return <CheckCheck className="w-3 h-3 text-gray-400" />
      case 'read':
        return <CheckCheck className="w-3 h-3 text-cyan-400" />
      default:
        return null
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-gradient-to-b from-gray-900/50 to-black/50 
                  rounded-2xl border border-cyan-500/20 backdrop-blur-xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 
                    border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 
                            flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 
                            rounded-full border-2 border-gray-900" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Strategy Whisperer AI</h3>
              <p className="text-xs text-gray-400">
                {isTyping ? 'Yazıyor...' : 'Çevrimiçi'}
              </p>
            </div>
          </div>
          {sessionId && (
            <div className="text-xs text-gray-500">
              Session: {sessionId.slice(0, 8)}...
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                <div className={`flex items-end gap-2 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-500' 
                      : 'bg-gradient-to-r from-cyan-500 to-purple-500'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message bubble */}
                  <div className={`px-4 py-3 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600/80 to-indigo-600/80 text-white rounded-br-sm'
                      : 'bg-gray-800/80 text-gray-100 rounded-bl-sm'
                  }`}>
                    {renderMessageContent(message)}
                    
                    {/* Time and status */}
                    <div className={`flex items-center gap-2 mt-1 text-xs ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}>
                      <span className="text-gray-400">{formatTime(message.timestamp)}</span>
                      {message.role === 'user' && getStatusIcon(message.status)}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center gap-2"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 
                            flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-gray-800/80 px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex items-center gap-1">
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-cyan-500/20">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Mesajınızı yazın..."
            className="flex-1 bg-gray-800/50 text-white placeholder-gray-500 
                     px-4 py-3 rounded-full outline-none focus:ring-2 
                     focus:ring-cyan-500/50 transition-all"
          />
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!input.trim()}
            className={`p-3 rounded-full transition-all ${
              input.trim()
                ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                : 'bg-gray-800/50 text-gray-600'
            }`}
          >
            <Sparkles className="w-5 h-5" />
          </motion.button>
        </div>
      </form>
    </div>
  )
} 