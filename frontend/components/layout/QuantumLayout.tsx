"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import QuantumHeader from "./QuantumHeader";

interface QuantumLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  showNavigation?: boolean;
  headerActions?: ReactNode;
  className?: string;
}

export default function QuantumLayout({ 
  children, 
  title, 
  subtitle, 
  showNavigation = true, 
  headerActions,
  className = ""
}: QuantumLayoutProps) {
  return (
    <div className="min-h-screen bg-quantum-dark relative overflow-hidden">
      {/* Quantum Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-quantum-primary/5 via-transparent to-quantum-accent/5" />
        
        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
        
        {/* Floating Particles */}
        {[...Array(25)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-quantum-primary/30 rounded-full"
            initial={{ 
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : 0, 
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : 0
            }}
            animate={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : 0,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : 0,
            }}
            transition={{
              duration: 20 + Math.random() * 15,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}

        {/* Quantum Energy Streams */}
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={`stream-${i}`}
            className="absolute w-px h-32 bg-gradient-to-b from-transparent via-quantum-primary/20 to-transparent"
            initial={{ 
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1200),
              y: -128
            }}
            animate={{
              y: typeof window !== 'undefined' ? window.innerHeight + 128 : 800
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              ease: "linear",
              delay: Math.random() * 8
            }}
          />
        ))}

        {/* Pulsing Orbs */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={`orb-${i}`}
            className="absolute w-32 h-32 rounded-full"
            style={{
              background: `radial-gradient(circle, ${
                i === 0 ? 'rgba(0, 255, 136, 0.1)' :
                i === 1 ? 'rgba(233, 69, 96, 0.1)' :
                'rgba(114, 9, 183, 0.1)'
              } 0%, transparent 70%)`
            }}
            initial={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1200),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 800),
            }}
            animate={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1200),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 800),
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 12 + Math.random() * 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Header */}
      <QuantumHeader 
        title={title} 
        subtitle={subtitle}
      />

      {/* Main Content */}
      <motion.main 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className={`relative z-10 ${className}`}
      >
        {children}
      </motion.main>

      {/* Quantum Footer Glow */}
      <div className="fixed bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-quantum-accent/30 to-transparent pointer-events-none" />

      {/* Global Quantum Styles */}
      <style jsx global>{`
        .quantum-panel {
          background: rgba(0, 0, 0, 0.4);
          backdrop-filter: blur(20px) saturate(200%);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 1rem;
          box-shadow: 
            0 8px 32px rgba(0, 255, 136, 0.1),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05);
          transition: all 0.3s ease;
        }
        
        .quantum-panel:hover {
          box-shadow: 
            0 8px 32px rgba(0, 255, 136, 0.2),
            inset 0 0 0 1px rgba(255, 255, 255, 0.1);
          transform: translateY(-2px);
        }
        
        .quantum-button {
          background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
          border: 1px solid rgba(0, 255, 136, 0.3);
          color: white;
          font-weight: 600;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
        }
        
        .quantum-button:hover {
          background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
          border-color: rgba(0, 255, 136, 0.5);
          box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
          transform: translateY(-1px);
        }
        
        .quantum-button-primary {
          background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
          color: black;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .quantum-button-primary:hover {
          box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
          transform: translateY(-2px) scale(1.02);
        }
        
        .quantum-button-danger {
          background: linear-gradient(135deg, #ff0055 0%, #ff4488 100%);
          color: white;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .quantum-button-danger:hover {
          box-shadow: 0 0 30px rgba(255, 0, 85, 0.5);
          transform: translateY(-2px) scale(1.02);
        }
        
        .quantum-button-accent {
          background: linear-gradient(135deg, #00d4ff 0%, #9945ff 100%);
          color: white;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .quantum-button-accent:hover {
          box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
          transform: translateY(-2px) scale(1.02);
        }

        .quantum-input {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 0.5rem;
          color: white;
          padding: 0.75rem 1rem;
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
        }

        .quantum-input:focus {
          outline: none;
          border-color: rgba(0, 255, 136, 0.5);
          box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1);
        }

        .quantum-card {
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(20px) saturate(180%);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 1rem;
          transition: all 0.3s ease;
        }

        .quantum-card:hover {
          border-color: rgba(0, 255, 136, 0.3);
          box-shadow: 0 8px 32px rgba(0, 255, 136, 0.15);
        }

        .quantum-text-glow {
          text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }

        .quantum-border-glow {
          box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar {
          width: 8px;
        }

        ::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.3);
        }

        ::-webkit-scrollbar-thumb {
          background: linear-gradient(135deg, #00ff88, #00d4ff);
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(135deg, #00d4ff, #9945ff);
        }
      `}</style>
    </div>
  );
} 