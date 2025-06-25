"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { 
  Home, 
  BarChart3, 
  Bot, 
  Shield, 
  Settings, 
  Menu,
  X,
  Activity
} from "lucide-react";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    mt5Connected: false,
    apiStatus: "checking"
  });

  useEffect(() => {
    // Check system status
    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch("http://localhost:8001/health");
      if (response.ok) {
        const data = await response.json();
        setSystemStatus({
          mt5Connected: data.mt5_connected,
          apiStatus: "online"
        });
      } else {
        setSystemStatus({
          mt5Connected: false,
          apiStatus: "error"
        });
      }
    } catch (error) {
      setSystemStatus({
        mt5Connected: false,
        apiStatus: "offline"
      });
    }
  };

  const navigation = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "Trading", href: "/trading", icon: BarChart3 },
    { name: "Signals", href: "/signals", icon: Activity },
    { name: "AI Analysis", href: "/ai", icon: Bot },
    { name: "Risk Manager", href: "/risk", icon: Shield },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-lg border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">ICT</span>
              </div>
              <span className="text-white font-semibold text-lg">Ultra v2</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/50 transition-all duration-200"
              >
                <item.icon size={18} />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>

          {/* Status Indicators */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                systemStatus.apiStatus === "online" ? "bg-green-500" : "bg-red-500"
              } animate-pulse`} />
              <span className="text-xs text-gray-400">API</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                systemStatus.mt5Connected ? "bg-green-500" : "bg-yellow-500"
              } animate-pulse`} />
              <span className="text-xs text-gray-400">MT5</span>
            </div>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/50"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden py-4 border-t border-gray-800">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/50 transition-all duration-200"
              >
                <item.icon size={18} />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
} 