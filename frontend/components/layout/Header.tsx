"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Zap,
  BarChart3,
  Target,
  Settings,
  Bell,
  User,
  Search,
  Activity,
  TrendingUp,
  Shield,
  Globe,
  Wifi,
  WifiOff,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Menu,
  X
} from 'lucide-react';

interface ConnectionStatus {
  mt5: boolean;
  api: boolean;
  websocket: boolean;
  lastUpdate: Date;
}

interface SystemStats {
  activeSignals: number;
  openPositions: number;
  autoTraderSessions: number;
  accountBalance: number;
  dailyPnL: number;
}

const Header: React.FC = () => {
  const pathname = usePathname();
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    mt5: false,
    api: false,
    websocket: false,
    lastUpdate: new Date()
  });
  const [systemStats, setSystemStats] = useState<SystemStats>({
    activeSignals: 0,
    openPositions: 0,
    autoTraderSessions: 0,
    accountBalance: 0,
    dailyPnL: 0
  });
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [notifications, setNotifications] = useState<number>(0);

  // Navigation items
  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/',
      icon: BarChart3,
      description: 'Main overview and real-time data'
    },
    {
      name: 'Trading',
      href: '/trading',
      icon: TrendingUp,
      description: 'Execute trades and manage positions'
    },
    {
      name: 'Signals',
      href: '/signals',
      icon: Target,
      description: 'ICT signals and market analysis'
    },
    {
      name: 'Performance',
      href: '/performance',
      icon: Activity,
      description: 'Analytics and performance metrics'
    },
    {
      name: 'Scanner',
      href: '/scanner',
      icon: Search,
      description: 'Market opportunity scanner'
    },
    {
      name: 'AutoTrader',
      href: '/autotrader',
      icon: Zap,
      description: 'Automated trading systems'
    }
  ];

  // Fetch connection status and system stats
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        // Check API and MT5 status
        const healthResponse = await fetch('/api/v1/health');
        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          setConnectionStatus(prev => ({
            ...prev,
            api: true,
            mt5: healthData.mt5_connected || false,
            lastUpdate: new Date()
          }));
        }

        // Get system stats
        const [signalsResponse, positionsResponse, autoTraderResponse, accountResponse] = await Promise.all([
          fetch('/api/v1/signals/ict?limit=100').catch(() => null),
          fetch('/api/v1/trading/positions').catch(() => null),
          fetch('/api/v1/auto-trader/status').catch(() => null),
          fetch('/api/v1/trading/account').catch(() => null)
        ]);

        // Update system stats
        let stats: SystemStats = {
          activeSignals: 0,
          openPositions: 0,
          autoTraderSessions: 0,
          accountBalance: 0,
          dailyPnL: 0
        };

        if (signalsResponse?.ok) {
          const signalsData = await signalsResponse.json();
          stats.activeSignals = signalsData.signals?.filter((s: any) => s.status === 'active').length || 0;
        }

        if (positionsResponse?.ok) {
          const positionsData = await positionsResponse.json();
          stats.openPositions = positionsData.length || 0;
        }

        if (autoTraderResponse?.ok) {
          const autoTraderData = await autoTraderResponse.json();
          stats.autoTraderSessions = autoTraderData.active_sessions || 0;
        }

        if (accountResponse?.ok) {
          const accountData = await accountResponse.json();
          stats.accountBalance = accountData.balance || 0;
          stats.dailyPnL = accountData.profit || 0;
        }

        setSystemStats(stats);

      } catch (error) {
        console.error('Error fetching header data:', error);
        setConnectionStatus(prev => ({
          ...prev,
          api: false,
          lastUpdate: new Date()
        }));
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const getConnectionIcon = () => {
    if (connectionStatus.api && connectionStatus.mt5) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    } else if (connectionStatus.api) {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    } else {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getConnectionText = () => {
    if (connectionStatus.api && connectionStatus.mt5) {
      return 'All Systems Online';
    } else if (connectionStatus.api) {
      return 'API Connected, MT5 Offline';
    } else {
      return 'Disconnected';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const isActiveRoute = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="relative">
                <Zap className="h-8 w-8 text-blue-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ICT Ultra v2</h1>
                <p className="text-xs text-gray-500">Algo Forge Edition</p>
              </div>
            </Link>

            {/* Connection Status */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-gray-50 rounded-lg">
              {getConnectionIcon()}
              <span className="text-sm font-medium text-gray-700">
                {getConnectionText()}
              </span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = isActiveRoute(item.href);
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                    ${isActive 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }
                  `}
                  title={item.description}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* System Stats */}
          <div className="hidden xl:flex items-center gap-4">
            <div className="flex items-center gap-3 text-sm">
              <div className="text-center">
                <div className="font-bold text-green-600">
                  {formatCurrency(systemStats.accountBalance)}
                </div>
                <div className="text-xs text-gray-500">Balance</div>
              </div>
              
              <div className="text-center">
                <div className={`font-bold ${systemStats.dailyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {systemStats.dailyPnL >= 0 ? '+' : ''}{formatCurrency(systemStats.dailyPnL)}
                </div>
                <div className="text-xs text-gray-500">Daily P&L</div>
              </div>
            </div>

            <div className="h-8 w-px bg-gray-200" />

            <div className="flex items-center gap-3">
              <Badge variant="outline" className="text-xs">
                <Target className="h-3 w-3 mr-1" />
                {systemStats.activeSignals} Signals
              </Badge>
              
              <Badge variant="outline" className="text-xs">
                <BarChart3 className="h-3 w-3 mr-1" />
                {systemStats.openPositions} Positions
              </Badge>
              
              <Badge variant="outline" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                {systemStats.autoTraderSessions} Auto
              </Badge>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Notifications */}
            <Button variant="outline" size="sm" className="relative">
              <Bell className="h-4 w-4" />
              {notifications > 0 && (
                <Badge className="absolute -top-2 -right-2 h-5 w-5 p-0 text-xs">
                  {notifications}
                </Badge>
              )}
            </Button>

            {/* Settings */}
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>

            {/* User Menu */}
            <Button variant="outline" size="sm">
              <User className="h-4 w-4" />
            </Button>

            {/* Mobile Menu Toggle */}
            <Button
              variant="outline"
              size="sm"
              className="lg:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 py-4">
            <div className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = isActiveRoute(item.href);
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                      ${isActive 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }
                    `}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <Icon className="h-4 w-4" />
                    <div>
                      <div>{item.name}</div>
                      <div className="text-xs text-gray-500">{item.description}</div>
                    </div>
                  </Link>
                );
              })}
            </div>

            {/* Mobile Stats */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                  <div className="font-bold text-green-600">
                    {formatCurrency(systemStats.accountBalance)}
                  </div>
                  <div className="text-xs text-gray-500">Account Balance</div>
                </div>
                
                <div className="text-center">
                  <div className={`font-bold ${systemStats.dailyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {systemStats.dailyPnL >= 0 ? '+' : ''}{formatCurrency(systemStats.dailyPnL)}
                  </div>
                  <div className="text-xs text-gray-500">Daily P&L</div>
                </div>
              </div>

              <div className="flex items-center justify-center gap-2 mt-4">
                <Badge variant="outline" className="text-xs">
                  {systemStats.activeSignals} Signals
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {systemStats.openPositions} Positions
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {systemStats.autoTraderSessions} Auto
                </Badge>
              </div>

              {/* Mobile Connection Status */}
              <div className="flex items-center justify-center gap-2 mt-4 px-3 py-2 bg-gray-50 rounded-lg">
                {getConnectionIcon()}
                <span className="text-sm font-medium text-gray-700">
                  {getConnectionText()}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header; 