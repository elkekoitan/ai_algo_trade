"use client";

import { motion } from "framer-motion";
import { useRouter, usePathname } from "next/navigation";
import { 
  Activity, 
  TrendingUp, 
  Brain, 
  Zap, 
  Layers,
  Settings,
  Bell,
  User,
  Menu,
  X,
  CheckCircle,
  AlertTriangle,
  Shield,
  Mail,
  BarChart3,
  Target,
  MessageSquare,
  BookText
} from "lucide-react";
import { useState, useEffect } from "react";
import Link from 'next/link';
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';

interface QuantumHeaderProps {
  title?: string;
  subtitle?: string;
}

const navigationItems = [
  { id: "dashboard", icon: BarChart3, label: "Dashboard", path: "/" },
  { id: "trading", icon: TrendingUp, label: "Trading", path: "/trading" },
  { id: "signals", icon: Target, label: "Signals", path: "/signals" },
  { id: "performance", icon: Activity, label: "Performance", path: "/performance" },
  { id: "whisperer", icon: MessageSquare, label: "Whisperer", path: "/strategy-whisperer" },
  { id: "adaptive_manager", icon: Shield, label: "Adaptive Manager", path: "/adaptive-trade-manager" },
  { id: "market_narrator", icon: BookText, label: "Narrator", path: "/market-narrator" },
  { id: "god_mode", icon: Brain, label: "God Mode", path: "/god-mode" },
  { id: "shadow_mode", icon: Shield, label: "Shadow Mode", path: "/shadow" },
  { id: "contact", icon: Mail, label: "Contact", path: "/contact" },
];

interface ConnectionStatus {
  connected: boolean;
  message: string;
}

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function QuantumHeader({ title = "AI Algo Trade", subtitle = "Quantum Edition" }: QuantumHeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { data: healthData, error } = useSWR(API_ENDPOINTS.health, fetcher, { refreshInterval: 10000 });

  const isServerReachable = healthData && healthData.status === 'healthy' && healthData.mt5_connected;

  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-50 border-b border-white/10 backdrop-blur-xl bg-black/20"
    >
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-quantum-primary/5 via-transparent to-quantum-accent/5" />
      </div>

      <div className="container mx-auto px-6 py-3 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-4">
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="text-3xl md:text-4xl"
                >
                  ⚛️
                </motion.div>
                <div>
                  <h1 className="text-xl md:text-2xl font-bold text-white">{title}</h1>
                  <p className="text-sm text-gray-400">{subtitle}</p>
                </div>
            </Link>
          </div>
          
          <nav className="hidden md:flex items-center gap-2">
            {navigationItems.map((item) => (
              <Link key={item.id} href={item.path} passHref>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 cursor-pointer ${
                    pathname === item.path
                      ? "bg-quantum-primary text-black shadow-lg shadow-quantum-primary/30" 
                      : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </motion.div>
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
             <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${isServerReachable ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {isServerReachable ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4 animate-pulse" />}
                <span>{isServerReachable ? 'Live Data' : 'MT5 Error'}</span>
             </div>
            <div className="hidden md:flex items-center gap-2">
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <Bell className="w-5 h-5 text-gray-400" />
                </motion.button>
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <Settings className="w-5 h-5 text-gray-400" />
                </motion.button>
                <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <User className="w-5 h-5 text-gray-400" />
                </motion.button>
            </div>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
            >
              {mobileMenuOpen ? <X className="w-5 h-5 text-white" /> : <Menu className="w-5 h-5 text-white" />}
            </motion.button>
          </div>
        </div>

        <motion.div
          initial={false}
          animate={mobileMenuOpen ? { height: "auto", opacity: 1 } : { height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="md:hidden overflow-hidden"
        >
          <nav className="pt-4 pb-2 space-y-2">
            {navigationItems.map((item) => (
               <Link key={item.id} href={item.path} passHref>
                 <div
                    onClick={() => setMobileMenuOpen(false)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all cursor-pointer ${
                    pathname === item.path
                      ? "bg-quantum-primary text-black" 
                      : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                 </div>
              </Link>
            ))}
          </nav>
        </motion.div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-quantum-primary/50 to-transparent" />
    </motion.header>
  );
} 