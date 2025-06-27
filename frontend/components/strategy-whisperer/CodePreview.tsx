'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Code, Copy, Download, Check, Maximize2, Minimize2, FileCode, Zap } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface CodePreviewProps {
  code: string
  language?: string
  filename?: string
  version?: string
  lines?: number
  performanceScore?: number
  optimizationHints?: string[]
  onDownload?: () => void
}

export default function CodePreview({
  code,
  language = 'cpp',
  filename = 'strategy.mq5',
  version = '1.0.0',
  lines = 0,
  performanceScore = 0,
  optimizationHints = [],
  onDownload
}: CodePreviewProps) {
  const [copied, setCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [activeTab, setActiveTab] = useState<'code' | 'optimization'>('code')

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleDownload = () => {
    if (onDownload) {
      onDownload()
    } else {
      // Default download implementation
      const blob = new Blob([code], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <motion.div
      className={`bg-gradient-to-b from-gray-900/90 to-black/90 rounded-2xl 
                border border-cyan-500/20 backdrop-blur-xl overflow-hidden
                ${isFullscreen ? 'fixed inset-4 z-50' : 'relative'}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="px-6 py-4 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 
                    border-b border-cyan-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileCode className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="font-semibold text-white flex items-center gap-2">
                {filename}
                <span className="text-xs text-gray-400">v{version}</span>
              </h3>
              <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                <span>{lines} satır</span>
                <span className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  Performance: 
                  <span className={`font-semibold ${getPerformanceColor(performanceScore)}`}>
                    {performanceScore}%
                  </span>
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleCopy}
              className="p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 
                       transition-all group relative"
              title="Copy code"
            >
              <AnimatePresence mode="wait">
                {copied ? (
                  <motion.div
                    key="check"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Check className="w-4 h-4 text-green-400" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="copy"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Copy className="w-4 h-4 text-gray-400 group-hover:text-cyan-400" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleDownload}
              className="p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 
                       transition-all group"
              title="Download code"
            >
              <Download className="w-4 h-4 text-gray-400 group-hover:text-cyan-400" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 
                       transition-all group"
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4 text-gray-400 group-hover:text-cyan-400" />
              ) : (
                <Maximize2 className="w-4 h-4 text-gray-400 group-hover:text-cyan-400" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Tabs */}
        {optimizationHints.length > 0 && (
          <div className="flex gap-4 mt-4">
            <button
              onClick={() => setActiveTab('code')}
              className={`pb-2 px-1 text-sm font-medium transition-all relative ${
                activeTab === 'code'
                  ? 'text-cyan-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Code
              {activeTab === 'code' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
                />
              )}
            </button>
            <button
              onClick={() => setActiveTab('optimization')}
              className={`pb-2 px-1 text-sm font-medium transition-all relative ${
                activeTab === 'optimization'
                  ? 'text-cyan-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Optimization Hints ({optimizationHints.length})
              {activeTab === 'optimization' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
                />
              )}
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      <div className={`${isFullscreen ? 'h-[calc(100%-120px)]' : 'max-h-[600px]'} overflow-auto`}>
        <AnimatePresence mode="wait">
          {activeTab === 'code' ? (
            <motion.div
              key="code"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="relative"
            >
              {/* Line numbers background */}
              <div className="absolute left-0 top-0 bottom-0 w-12 bg-gray-900/50 
                            border-r border-gray-800" />
              
              {/* Syntax highlighted code */}
              <div className="pl-12">
                <SyntaxHighlighter
                  language={language}
                  style={atomDark}
                  customStyle={{
                    margin: 0,
                    padding: '1rem',
                    background: 'transparent',
                    fontSize: '0.875rem',
                    lineHeight: '1.5'
                  }}
                  showLineNumbers={true}
                  lineNumberStyle={{
                    position: 'absolute',
                    left: '-2.5rem',
                    color: '#4a5568',
                    userSelect: 'none'
                  }}
                >
                  {code}
                </SyntaxHighlighter>
              </div>

              {/* Code minimap (for fullscreen) */}
              {isFullscreen && (
                <div className="absolute right-4 top-4 w-24 h-48 bg-gray-900/50 
                              rounded-lg border border-gray-800 p-2">
                  <div className="text-xs text-gray-500 mb-1">Minimap</div>
                  <div className="space-y-0.5">
                    {Array.from({ length: 20 }).map((_, i) => (
                      <div
                        key={i}
                        className="h-1 bg-gray-700 rounded"
                        style={{
                          width: `${Math.random() * 60 + 40}%`,
                          opacity: Math.random() * 0.5 + 0.5
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="optimization"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="p-6"
            >
              <div className="space-y-4">
                {optimizationHints.map((hint, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-3 p-4 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 
                             rounded-lg border border-yellow-500/30"
                  >
                    <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-200">{hint}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-gradient-to-r from-cyan-900/20 to-purple-900/20 
                    border-t border-cyan-500/20">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Generated by Strategy Whisperer AI</span>
          <span>MQL5 Compatible</span>
        </div>
      </div>

      {/* Fullscreen backdrop */}
      {isFullscreen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 -z-10"
          onClick={() => setIsFullscreen(false)}
        />
      )}
    </motion.div>
  )
} 