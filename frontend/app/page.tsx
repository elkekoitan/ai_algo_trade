"use client";

import { useState, useEffect } from 'react';
import { 
  DollarSign, Zap, Target, BarChart3, Users, Bot, Code, Rss, Eye, GitBranch,
  TrendingUp, Shield, Brain, MessageSquare, Activity, Cpu, Globe, 
  ArrowUpRight, Play, Settings, ChevronRight, Sparkles, Layers,
  PieChart, LineChart, BarChart, Radar, Map, Bell, Search, Filter
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import useSWR from 'swr';
import { API_BASE_URL, API_ENDPOINTS } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { GodModeDemo, ShadowModeDemo } from '@/components/DemoComponents';
import PerformanceChart from '@/components/dashboard/PerformanceChart';
import TradeHistoryTable from '@/components/dashboard/TradeHistoryTable';
import PerformanceMetrics from '@/components/performance/PerformanceMetrics';

const fetcher = (url: string) => fetch(url).then(res => res.json());

// Enhanced Hero Module Card Component
const ModuleHeroCard = ({ 
  title, 
  description, 
  icon: Icon, 
  value, 
  detail, 
  status,
  trend,
  route,
  demoActions,
  gradient,
  isActive = false
}: { 
  title: string;
  description: string;
  icon: React.ElementType;
  value: string | number;
  detail: string;
  status: 'active' | 'warning' | 'success' | 'info';
  trend?: number;
  route: string;
  demoActions: { label: string; action: () => void }[];
  gradient: string;
  isActive?: boolean;
}) => {
  const router = useRouter();
  const [isHovered, setIsHovered] = useState(false);
  const [demoRunning, setDemoRunning] = useState(false);

  const statusColors = {
    active: 'border-cyan-400/50 bg-cyan-400/5',
    warning: 'border-yellow-400/50 bg-yellow-400/5',
    success: 'border-green-400/50 bg-green-400/5',
    info: 'border-blue-400/50 bg-blue-400/5'
  };

  const runDemo = async (action: () => void) => {
    setDemoRunning(true);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate demo
    action();
    setDemoRunning(false);
  };

  return (
    <Card 
      className={`group relative overflow-hidden bg-gray-900/50 border-gray-800 hover:${statusColors[status]} transition-all duration-500 transform hover:scale-[1.02] hover:shadow-2xl ${isActive ? statusColors[status] : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500 ${gradient}`} />
      
      {/* Animated Border */}
      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{
        background: 'linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.2), transparent)',
        animation: isHovered ? 'shimmer 2s infinite' : 'none'
      }} />

      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${gradient} bg-opacity-20`}>
            <Icon className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">
              {title}
            </CardTitle>
            {isActive && (
              <div className="flex items-center space-x-1 mt-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-xs text-green-400">Live</span>
              </div>
            )}
          </div>
        </div>
        
        {trend && (
          <div className={`flex items-center space-x-1 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            <TrendingUp className="h-3 w-3" />
            <span className="text-xs font-medium">{trend > 0 ? '+' : ''}{trend}%</span>
          </div>
        )}
      </CardHeader>

      <CardContent className="relative z-10">
        <div className="space-y-4">
          {/* Main Metric */}
          <div>
            <div className="text-2xl font-bold text-white group-hover:text-cyan-400 transition-colors">
              {value}
            </div>
            <p className="text-xs text-gray-400">{detail}</p>
          </div>

          {/* Description */}
          <p className="text-xs text-gray-500 group-hover:text-gray-400 transition-colors line-clamp-2">
            {description}
          </p>

          {/* Demo Actions */}
          <div className={`space-y-2 transition-all duration-300 ${isHovered ? 'opacity-100 max-h-32' : 'opacity-0 max-h-0 overflow-hidden'}`}>
            {demoActions.map((demo, index) => (
              <Button
                key={index}
                variant="ghost"
                size="sm"
                className="w-full justify-start text-xs text-gray-400 hover:text-white hover:bg-white/10"
                onClick={() => runDemo(demo.action)}
                disabled={demoRunning}
              >
                <Play className="h-3 w-3 mr-2" />
                {demoRunning ? 'Running...' : demo.label}
              </Button>
            ))}
          </div>

          {/* Navigate Button */}
          <Button
            onClick={() => router.push(route)}
            className={`w-full transition-all duration-300 ${isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}
            variant="outline"
            size="sm"
          >
            Explore Module
            <ChevronRight className="h-3 w-3 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Real-time System Status Component
const SystemStatus = () => {
  const { data, error } = useSWR(`${API_BASE_URL}/health`, fetcher, { refreshInterval: 15000 });

  const isConnected = data?.mt5_connected;
  const statusText = isConnected ? "Connected" : "Connecting...";
  const statusColor = isConnected ? "text-green-400" : "text-yellow-400";
  const pulseColor = isConnected ? "bg-green-400" : "bg-yellow-400";

  return (
    <Card className="bg-gray-900/50 border-gray-800">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-300 flex items-center">
          <Activity className="h-4 w-4 mr-2" />
          System Status
        </CardTitle>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full animate-pulse ${pulseColor}`} />
          <span className={`text-xs ${statusColor}`}>{statusText}</span>
        </div>
      </CardHeader>
      <CardContent>
          <div className="text-2xl font-bold text-white">
            {data?.status || 'Checking...'}
          </div>
          <p className="text-xs text-gray-400">
            {data?.message || 'Establishing connection...'}
          </p>
      </CardContent>
    </Card>
  );
};

// Enhanced Account Info with Real-time Updates
const AccountInfoCard = () => {
  const { data, error } = useSWR(API_ENDPOINTS.account, fetcher, { refreshInterval: 5000 });
  
  const accountData = data?.data || {};

  return (
    <Card className="bg-gray-900/50 border-gray-800 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-green-400/5 to-cyan-400/5" />
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
        <CardTitle className="text-sm font-medium text-gray-300 flex items-center">
          <DollarSign className="h-4 w-4 mr-2" />
          Account Equity
        </CardTitle>
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-green-400">Live</span>
        </div>
      </CardHeader>
      <CardContent className="relative z-10">
        <div className="space-y-2">
          <div className="text-2xl font-bold text-white">
            ${(accountData.equity || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">P&L:</span>
            <span className={accountData.profit >=0 ? 'text-green-400' : 'text-red-400'}>
              ${accountData.profit?.toFixed(2) || '0.00'}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default function Dashboard() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [showNotifications, setShowNotifications] = useState(false);

  const moduleConfigs = [
    {
      title: "God Mode",
      description: "Omniscient market analysis with prophetic predictions and divine insights.",
      icon: Eye,
      value: "94.7%",
      detail: "Prediction Accuracy",
      status: "success" as const,
      trend: 5.2,
      route: "/god-mode",
      gradient: "bg-gradient-to-br from-purple-500 to-pink-500",
      demoActions: [
        { label: "Run Prediction", action: () => console.log("Running prediction...") },
        { label: "Market Oracle", action: () => console.log("Consulting oracle...") }
      ],
      isActive: true
    },
    {
      title: "Shadow Mode",
      description: "Institutional tracking, whale detection, and stealth execution.",
      icon: Users,
      value: "WHALE",
      detail: "Activity Detected",
      status: "warning" as const,
      trend: 12.8,
      route: "/shadow",
      gradient: "bg-gradient-to-br from-gray-700 to-black",
      demoActions: [
        { label: "Track Whales", action: () => console.log("Tracking whales...") },
        { label: "Dark Pool Monitor", action: () => console.log("Monitoring dark pools...") }
      ],
      isActive: true
    },
    {
      title: "Adaptive Trade Manager",
      description: "AI-powered position management with dynamic risk adjustment.",
      icon: Zap,
      value: "LOW",
      detail: "Portfolio Risk",
      status: "success" as const,
      trend: -2.1,
      route: "/adaptive-trade-manager",
      gradient: "bg-gradient-to-br from-yellow-400 to-orange-500",
      demoActions: [
        { label: "Optimize Positions", action: () => console.log("Optimizing...") },
        { label: "Risk Analysis", action: () => console.log("Analyzing risk...") }
      ],
      isActive: true
    },
    {
      title: "Strategy Whisperer",
      description: "Natural language to MQL5 strategy creation with AI assistance.",
      icon: Bot,
      value: "23",
      detail: "Active Strategies",
      status: "info" as const,
      trend: 8.5,
      route: "/strategy-whisperer",
      gradient: "bg-gradient-to-br from-blue-500 to-cyan-500",
      demoActions: [
        { label: "Create Strategy", action: () => console.log("Creating strategy...") },
        { label: "Backtest", action: () => console.log("Running backtest...") }
      ],
      isActive: true
    },
    {
      title: "Market Narrator",
      description: "AI storytelling for market movements with correlation analysis.",
      icon: MessageSquare,
      value: "BULLISH",
      detail: "Market Sentiment",
      status: "success" as const,
      trend: 3.7,
      route: "/market-narrator",
      gradient: "bg-gradient-to-br from-green-500 to-teal-500",
      demoActions: [
        { label: "Generate Story", action: () => console.log("Generating story...") },
        { label: "Sentiment Analysis", action: () => console.log("Analyzing sentiment...") }
      ],
      isActive: true
    },
    {
      title: "Quantum Tech",
      description: "Advanced quantum algorithms for market prediction and analysis.",
      icon: Cpu,
      value: "∞",
      detail: "Quantum States",
      status: "info" as const,
      trend: 15.3,
      route: "/quantum-tech",
      gradient: "bg-gradient-to-br from-indigo-500 to-purple-500",
      demoActions: [
        { label: "Quantum Scan", action: () => console.log("Quantum scanning...") },
        { label: "Probability Matrix", action: () => console.log("Calculating probabilities...") }
      ]
    },
    {
      title: "Signal Scanner",
      description: "ICT-based signal detection with breaker blocks and FVG analysis.",
      icon: Radar,
      value: "47",
      detail: "Active Signals",
      status: "active" as const,
      trend: 6.9,
      route: "/signals",
      gradient: "bg-gradient-to-br from-red-500 to-pink-500",
      demoActions: [
        { label: "Scan Market", action: () => console.log("Scanning market...") },
        { label: "Signal Alert", action: () => console.log("Setting alerts...") }
      ],
      isActive: true
    },
    {
      title: "Social Trading",
      description: "Copy trading and social sentiment analysis platform.",
      icon: Globe,
      value: "1.2K",
      detail: "Active Traders",
      status: "success" as const,
      trend: 4.2,
      route: "/social",
      gradient: "bg-gradient-to-br from-pink-500 to-rose-500",
      demoActions: [
        { label: "Find Traders", action: () => console.log("Finding traders...") },
        { label: "Social Signals", action: () => console.log("Analyzing social signals...") }
      ]
    }
  ];

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* System Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <SystemStatus />
        <AccountInfoCard />
        
        {/* Market Status */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Market Status</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">OPEN</div>
            <p className="text-xs text-gray-400">NYSE • 6h 23m remaining</p>
          </CardContent>
        </Card>

        {/* Active Strategies */}
        <Card className="bg-gray-900/50 border-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Active Strategies</CardTitle>
            <Layers className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-cyan-400">12</div>
            <p className="text-xs text-gray-400">8 profitable • 4 monitoring</p>
          </CardContent>
        </Card>
      </div>

      {/* Performance & History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-1 flex flex-col gap-6">
          <PerformanceMetrics />
          <PerformanceChart />
        </div>
        <TradeHistoryTable />
      </div>

      {/* Module Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Core Modules</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {moduleConfigs.map((module, index) => (
            <ModuleHeroCard key={index} {...module} />
          ))}
        </div>
      </div>

      {/* Custom Styles */}
      <style jsx global>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
} 