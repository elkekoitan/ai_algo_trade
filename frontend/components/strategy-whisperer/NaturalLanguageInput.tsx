'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Mic, MicOff, Sparkles, Brain, Zap } from 'lucide-react'

interface NaturalLanguageInputProps {
  onSubmit: (text: string) => void
  isProcessing?: boolean
  placeholder?: string
}

export default function NaturalLanguageInput({ 
  onSubmit, 
  isProcessing = false,
  placeholder = "RSI 30'un altında al, 70'in üstünde sat..."
}: NaturalLanguageInputProps) {
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [charCount, setCharCount] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setCharCount(input.length)
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isProcessing) {
      onSubmit(input.trim())
      setInput('')
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Voice recording implementation would go here
  }

  const examples = [
    "RSI oversold stratejisi oluştur",
    "MACD cross ile trend takip",
    "5 dakikalık scalping stratejisi",
    "Bollinger bantları ile volatilite ticareti"
  ]

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header with animated gradient */}
      <motion.div 
        className="mb-6 text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="inline-flex items-center gap-3 mb-4">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <Brain className="w-8 h-8 text-cyan-400" />
          </motion.div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            Strategy Whisperer
          </h2>
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Sparkles className="w-6 h-6 text-purple-400" />
          </motion.div>
        </div>
        <p className="text-gray-400">
          Doğal dilde stratejinizi anlatın, gerisini bize bırakın
        </p>
      </motion.div>

      {/* Example chips */}
      <div className="mb-4 flex flex-wrap gap-2 justify-center">
        {examples.map((example, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setInput(example)}
            className="px-4 py-2 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 
                     border border-cyan-500/30 rounded-full text-sm text-gray-300
                     hover:border-cyan-400/50 transition-all duration-300
                     backdrop-blur-sm"
          >
            <span className="flex items-center gap-2">
              <Zap className="w-3 h-3" />
              {example}
            </span>
          </motion.button>
        ))}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="relative">
        <motion.div
          className="relative bg-gradient-to-r from-cyan-900/20 to-purple-900/20 
                   rounded-2xl border border-cyan-500/30 backdrop-blur-xl
                   shadow-2xl overflow-hidden"
          whileHover={{ borderColor: 'rgba(34, 211, 238, 0.5)' }}
        >
          {/* Animated background effect */}
          <div className="absolute inset-0 opacity-30">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 
                          animate-pulse" />
          </div>

          <div className="relative p-4">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              placeholder={placeholder}
              disabled={isProcessing}
              className="w-full bg-transparent text-white placeholder-gray-500 
                       outline-none resize-none min-h-[60px] max-h-[200px]
                       text-lg leading-relaxed"
              rows={1}
            />

            {/* Character count */}
            <div className="flex items-center justify-between mt-3">
              <motion.div 
                className="text-xs text-gray-500"
                animate={{ opacity: charCount > 0 ? 1 : 0 }}
              >
                {charCount} karakter
              </motion.div>

              <div className="flex items-center gap-2">
                {/* Voice input button */}
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={toggleRecording}
                  className={`p-2 rounded-full transition-all duration-300 ${
                    isRecording 
                      ? 'bg-red-500/20 text-red-400 animate-pulse' 
                      : 'bg-gray-800/50 text-gray-400 hover:text-cyan-400'
                  }`}
                >
                  {isRecording ? (
                    <MicOff className="w-5 h-5" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </motion.button>

                {/* Send button */}
                <motion.button
                  type="submit"
                  disabled={!input.trim() || isProcessing}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className={`p-2 rounded-full transition-all duration-300 ${
                    input.trim() && !isProcessing
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg'
                      : 'bg-gray-800/50 text-gray-600'
                  }`}
                >
                  <AnimatePresence mode="wait">
                    {isProcessing ? (
                      <motion.div
                        key="processing"
                        initial={{ opacity: 0, rotate: 0 }}
                        animate={{ opacity: 1, rotate: 360 }}
                        exit={{ opacity: 0 }}
                        transition={{ rotate: { duration: 1, repeat: Infinity, ease: "linear" } }}
                      >
                        <Sparkles className="w-5 h-5" />
                      </motion.div>
                    ) : (
                      <motion.div
                        key="send"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 10 }}
                      >
                        <Send className="w-5 h-5" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Processing indicator */}
        <AnimatePresence>
          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute -bottom-8 left-0 right-0 text-center"
            >
              <span className="text-sm text-cyan-400 animate-pulse">
                AI stratejinizi analiz ediyor...
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </form>

      {/* Decorative elements */}
      <div className="absolute -z-10 top-0 left-1/4 w-64 h-64 bg-cyan-500/10 
                    rounded-full blur-3xl animate-pulse" />
      <div className="absolute -z-10 bottom-0 right-1/4 w-64 h-64 bg-purple-500/10 
                    rounded-full blur-3xl animate-pulse animation-delay-2000" />
    </div>
  )
} 