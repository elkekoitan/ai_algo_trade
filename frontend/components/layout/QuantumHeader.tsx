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
  Target
} from "lucide-react";
import { useState, useEffect } from "react";
import Link from 'next/link';

interface QuantumHeaderProps {
  title?: string;
  subtitle?: string;
}

const navigationItems = [
  { id: "dashboard", icon: BarChart3, label: "Dashboard", path: "/" },
  { id: "trading", icon: TrendingUp, label: "Trading", path: "/trading" },
  { id: "signals", icon: Target, label: "Signals", path: "/signals" },
  { id: "performance", icon: Activity, label: "Performance", path: "/performance" },
  { id: "quantum", icon: Brain, label: "Quantum", path: "/quantum" },
  { id: "contact", icon: Mail, label: "Contact", path: "/contact" },
  { id: "ai_patterns", icon: Brain, label: "AI Patterns", path: "/quantum" },
  { id: "edge_computing", icon: Zap, label: "Edge", path: "/edge" },
  { id: "social_trading", icon: User, label: "Social", path: "/social" },
  { id: "institutional", icon: Shield, label: "Institutional", path: "/institutional" },
  { id: "quantum_tech", icon: Brain, label: "Quantum Tech", path: "/quantum-tech" },
  { id: "god_mode", icon: Brain, label: "God Mode", path: "/god-mode" },
  { id: "shadow_mode", icon: Shield, label: "Shadow Mode", path: "/shadow" },
];

interface ConnectionStatus {
  connected: boolean;
  message: string;
}

export default function QuantumHeader({ title = "AI Algo Trade", subtitle = "Quantum Edition" }: QuantumHeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [connection, setConnection] = useState<ConnectionStatus>({ connected: false, message: 'Connecting...' });

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/trading/account');
        if (response.ok) {
          const data = await response.json();
          if (data.login && data.server) {
             setConnection({ connected: true, message: `Connected to ${data.server}`});
          } else {
             setConnection({ connected: false, message: 'Connection Error'});
          }
        } else {
          setConnection({ connected: false, message: 'Backend Offline' });
        }
      } catch (error) {
        setConnection({ connected: false, message: 'Server Unreachable' });
      }
    };

    checkConnection();
    const intervalId = setInterval(checkConnection, 10000); 

    return () => clearInterval(intervalId);
  }, []);


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
             <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${connection.connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {connection.connected ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4 animate-pulse" />}
                <span>{connection.message}</span>
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