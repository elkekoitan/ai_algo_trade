'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  glow?: boolean
  variant?: 'default' | 'neon' | 'hologram'
}

export default function GlassCard({ 
  children, 
  className = '', 
  hover = true,
  glow = false,
  variant = 'default' 
}: GlassCardProps) {
  const variants = {
    default: {
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
    },
    neon: {
      background: 'rgba(0, 255, 136, 0.03)',
      border: '1px solid rgba(0, 255, 136, 0.3)',
      boxShadow: '0 0 20px rgba(0, 255, 136, 0.5), inset 0 0 20px rgba(0, 255, 136, 0.1)'
    },
    hologram: {
      background: 'linear-gradient(135deg, rgba(233, 69, 96, 0.05) 0%, rgba(114, 9, 183, 0.05) 100%)',
      border: '1px solid transparent',
      borderImage: 'linear-gradient(135deg, #e94560 0%, #7209b7 100%) 1',
      boxShadow: '0 8px 32px 0 rgba(114, 9, 183, 0.37)'
    }
  }

  const cardVariants = {
    initial: { 
      opacity: 0, 
      y: 20,
      rotateX: -10
    },
    animate: { 
      opacity: 1, 
      y: 0,
      rotateX: 0,
      transition: {
        duration: 0.6,
        ease: [0.6, -0.05, 0.01, 0.99]
      }
    },
    hover: hover ? {
      y: -5,
      boxShadow: variant === 'neon' 
        ? '0 0 30px rgba(0, 255, 136, 0.7), inset 0 0 30px rgba(0, 255, 136, 0.2)'
        : '0 12px 40px 0 rgba(31, 38, 135, 0.5)',
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    } : {}
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      whileHover="hover"
      variants={cardVariants}
      className={`relative rounded-2xl backdrop-blur-xl ${className}`}
      style={{
        ...variants[variant],
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        transformStyle: 'preserve-3d',
        perspective: '1000px'
      }}
    >
      {glow && (
        <motion.div
          className="absolute inset-0 rounded-2xl opacity-50"
          animate={{
            boxShadow: [
              '0 0 20px rgba(0, 255, 136, 0.5)',
              '0 0 40px rgba(0, 255, 136, 0.7)',
              '0 0 20px rgba(0, 255, 136, 0.5)'
            ]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
      )}
      
      {/* Holographic shimmer effect */}
      {variant === 'hologram' && (
        <motion.div
          className="absolute inset-0 rounded-2xl opacity-30"
          style={{
            background: 'linear-gradient(105deg, transparent 40%, rgba(255, 255, 255, 0.7) 50%, transparent 60%)',
            backgroundSize: '200% 200%'
          }}
          animate={{
            backgroundPosition: ['200% 0%', '-200% 0%']
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'linear'
          }}
        />
      )}
      
      <div className="relative z-10 p-6">
        {children}
      </div>
    </motion.div>
  )
} 