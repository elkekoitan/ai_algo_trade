"use client";

import { useRef, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Globe, TrendingUp, BarChart3 } from "lucide-react";

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  value: number;
  color: string;
  connections: string[];
}

export default function NetworkGraph3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([
    { id: "EURUSD", label: "EUR/USD", x: 50, y: 50, value: 1.16952, color: "#00ff88", connections: ["GBPUSD", "USDJPY"] },
    { id: "GBPUSD", label: "GBP/USD", x: 200, y: 100, value: 1.31245, color: "#ff4488", connections: ["EURUSD"] },
    { id: "USDJPY", label: "USD/JPY", x: 150, y: 200, value: 149.235, color: "#00d4ff", connections: ["EURUSD"] },
    { id: "XAUUSD", label: "XAU/USD", x: 300, y: 150, value: 3333.89, color: "#ffd700", connections: ["BTCUSD"] },
    { id: "BTCUSD", label: "BTC/USD", x: 250, y: 250, value: 107385, color: "#f7931a", connections: ["XAUUSD"] },
    { id: "ETHUSD", label: "ETH/USD", x: 400, y: 100, value: 2450.62, color: "#627eea", connections: ["BTCUSD"] }
  ]);

  // Animate nodes with real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prev => prev.map(node => ({
        ...node,
        value: node.value * (1 + (Math.random() - 0.5) * 0.001),
        x: node.x + Math.sin(Date.now() * 0.001 + node.x) * 2,
        y: node.y + Math.cos(Date.now() * 0.001 + node.y) * 2
      })));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const renderConnections = () => {
    const connections: JSX.Element[] = [];
    
    nodes.forEach(node => {
      node.connections.forEach(targetId => {
        const targetNode = nodes.find(n => n.id === targetId);
        if (targetNode) {
          connections.push(
            <motion.line
              key={`${node.id}-${targetId}`}
              x1={node.x}
              y1={node.y}
              x2={targetNode.x}
              y2={targetNode.y}
              stroke="rgba(0, 255, 136, 0.3)"
              strokeWidth="1"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, ease: "easeInOut" }}
            />
          );
        }
      });
    });
    
    return connections;
  };

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-black via-gray-900 to-black overflow-hidden">
      {/* Animated background grid */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px),
            linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px'
        }}
      />

      {/* SVG Network */}
      <svg 
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 500 300"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Connection lines */}
        {renderConnections()}
        
        {/* Nodes */}
        {nodes.map((node, index) => (
          <g key={node.id}>
            {/* Glow effect */}
            <motion.circle
              cx={node.x}
              cy={node.y}
              r="15"
              fill={node.color}
              opacity="0.3"
              initial={{ scale: 0 }}
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.6, 0.3]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                delay: index * 0.2
              }}
            />
            
            {/* Main node */}
            <motion.circle
              cx={node.x}
              cy={node.y}
              r="8"
              fill={node.color}
              stroke="rgba(255, 255, 255, 0.5)"
              strokeWidth="1"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.2 }}
              style={{ cursor: 'pointer' }}
            />
            
            {/* Label background */}
            <motion.rect
              x={node.x - 25}
              y={node.y - 35}
              width="50"
              height="20"
              rx="3"
              fill="rgba(0, 0, 0, 0.8)"
              stroke={node.color}
              strokeWidth="1"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 + 0.5 }}
            />
            
            {/* Symbol label */}
            <motion.text
              x={node.x}
              y={node.y - 22}
              textAnchor="middle"
              fill="white"
              fontSize="8"
              fontWeight="bold"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 + 0.7 }}
            >
              {node.label}
            </motion.text>
            
            {/* Price label */}
            <motion.text
              x={node.x}
              y={node.y + 25}
              textAnchor="middle"
              fill={node.color}
              fontSize="6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 + 0.9 }}
            >
              {node.value.toFixed(node.id.includes("BTC") ? 0 : 4)}
            </motion.text>
          </g>
        ))}
      </svg>

      {/* Floating particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-quantum-primary/50 rounded-full"
          initial={{ 
            x: Math.random() * 500, 
            y: Math.random() * 300,
            opacity: 0
          }}
          animate={{
            x: Math.random() * 500,
            y: Math.random() * 300,
            opacity: [0, 1, 0]
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2
          }}
        />
      ))}

      {/* Control panel */}
      <div className="absolute top-4 left-4 space-y-2">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="quantum-panel p-3"
        >
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-quantum-primary" />
            <span className="text-xs text-gray-400">Network Status</span>
          </div>
          <p className="text-sm font-semibold text-quantum-primary mt-1">LIVE</p>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="quantum-panel p-3"
        >
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-gray-400">Connections</span>
          </div>
          <p className="text-sm font-semibold text-white mt-1">{nodes.length} Active</p>
        </motion.div>
      </div>

      {/* Market stats */}
      <div className="absolute bottom-4 right-4 space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="quantum-panel p-4"
        >
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-4 h-4 text-quantum-accent" />
            <span className="text-xs text-gray-400">Market Correlation</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full" />
                <span className="text-xs text-gray-300">Strong +</span>
              </div>
              <span className="text-xs text-green-400 font-mono">85%</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-400 rounded-full" />
                <span className="text-xs text-gray-300">Strong -</span>
              </div>
              <span className="text-xs text-red-400 font-mono">72%</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-400 rounded-full" />
                <span className="text-xs text-gray-300">Neutral</span>
              </div>
              <span className="text-xs text-yellow-400 font-mono">43%</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Performance indicator */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1 }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none"
      >
        <div className="quantum-panel p-6 text-center">
          <TrendingUp className="w-8 h-8 text-quantum-primary mx-auto mb-2" />
          <p className="text-lg font-bold text-white">Neural Network</p>
          <p className="text-sm text-quantum-accent">Active Monitoring</p>
          <div className="flex items-center justify-center gap-1 mt-2">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="w-2 h-2 bg-quantum-primary rounded-full"
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ 
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
} 