"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAppContext } from '@/lib/context';
import { useTranslations } from '@/lib/translations/context';
import LanguageSwitcher from '@/components/ui/language-switcher';
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
  X,
  Brain,
  Mail
} from 'lucide-react';

const Header: React.FC = () => {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [notifications, setNotifications] = useState<number>(0);
  
  // Use our context
  const { 
    connectionStatus, 
    accountInfo, 
    positions, 
    isLoading, 
    refreshAll 
  } = useAppContext();
  
  // Use translations
  const { t, language, setLanguage } = useTranslations();

  // Navigation items
  const navigationItems = [
    {
      name: t('navigation.dashboard'),
      href: '/',
      icon: BarChart3,
      description: t('dashboard.subtitle')
    },
    {
      name: 'QDashboard',
      href: '/quantum',
      icon: Brain,
      description: 'Quantum AI Trading Intelligence Hub'
    },
    {
      name: t('navigation.trading'),
      href: '/trading',
      icon: TrendingUp,
      description: 'Execute trades and manage positions'
    },
    {
      name: t('navigation.signals'),
      href: '/signals',
      icon: Target,
      description: 'ICT signals and market analysis'
    },
    {
      name: t('navigation.performance'),
      href: '/performance',
      icon: Activity,
      description: 'Analytics and performance metrics'
    },
    {
      name: t('contact.title'),
      href: '/contact',
      icon: Mail,
      description: 'Get in touch with our team'
    }
  ];

  const getConnectionIcon = () => {
    if (isLoading.account) return <AlertTriangle className="h-4 w-4 text-yellow-500 animate-pulse" />;
    if (connectionStatus.api && connectionStatus.mt5) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    } else if (connectionStatus.api) {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    } else {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getConnectionText = () => {
    if (isLoading.account) return 'Connecting...';
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

  // System stats derived from context
  const systemStats = {
    accountBalance: accountInfo?.balance || 0,
    dailyPnL: accountInfo?.profit || 0,
    activeSignals: 0, // We'll need to add this to context later
    openPositions: positions.length,
    autoTraderSessions: 0 // We'll need to add this to context later
  };

  return (
    <header className="bg-gray-900/90 backdrop-blur-lg border-b border-gray-800 shadow-md sticky top-0 z-50">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 w-full">
          
          {/* Left Section */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="relative">
                <Zap className="h-8 w-8 text-blue-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">ICT Ultra v2</h1>
                <p className="text-xs text-gray-400">Algo Forge Edition</p>
              </div>
            </Link>

            <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-gray-800/50 rounded-lg">
              {getConnectionIcon()}
              <span className="text-sm font-medium text-gray-300">
                {getConnectionText()}
              </span>
            </div>
          </div>

          {/* Center Section (Navigation) */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = isActiveRoute(item.href);
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-blue-600/20 text-blue-400' 
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                  }`}
                  title={item.description}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Section */}
          <div className="flex items-center gap-2">
            <div className="hidden xl:flex items-center gap-3 text-sm">
                <div className="text-center">
                  <div className="font-bold text-green-400">
                    {formatCurrency(systemStats.accountBalance)}
                  </div>
                  <div className="text-xs text-gray-400">Balance</div>
                </div>
                <div className="text-center">
                  <div className={`font-bold ${systemStats.dailyPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {systemStats.dailyPnL >= 0 ? '+' : ''}{formatCurrency(systemStats.dailyPnL)}
                  </div>
                  <div className="text-xs text-gray-400">Daily P&L</div>
                </div>
              </div>

              <div className="h-8 w-px bg-gray-700 mx-2 hidden xl:block" />

              <div className="hidden lg:flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-gray-800/50 text-gray-300 border-gray-700">
                    <Target className="h-3 w-3 mr-1 text-purple-400" />
                    {systemStats.activeSignals} Signals
                  </Badge>
                  <Badge variant="outline" className="text-xs bg-gray-800/50 text-gray-300 border-gray-700">
                    <BarChart3 className="h-3 w-3 mr-1 text-blue-400" />
                    {systemStats.openPositions} Positions
                  </Badge>
              </div>

            <LanguageSwitcher onLanguageChange={setLanguage} />

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
          <div className="lg:hidden border-t border-gray-800 py-4">
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
                        ? 'bg-blue-600/20 text-blue-400' 
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
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
            <div className="mt-4 pt-4 border-t border-gray-800">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                  <div className="font-bold text-green-400">
                    {formatCurrency(systemStats.accountBalance)}
                  </div>
                  <div className="text-xs text-gray-400">Account Balance</div>
                </div>
                
                <div className="text-center">
                  <div className={`font-bold ${systemStats.dailyPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {systemStats.dailyPnL >= 0 ? '+' : ''}{formatCurrency(systemStats.dailyPnL)}
                  </div>
                  <div className="text-xs text-gray-400">Daily P&L</div>
                </div>
              </div>

              <div className="flex items-center justify-center gap-2 mt-4">
                <Badge variant="outline" className="text-xs bg-gray-800/50 text-gray-300 border-gray-700">
                  {systemStats.activeSignals} Signals
                </Badge>
                <Badge variant="outline" className="text-xs bg-gray-800/50 text-gray-300 border-gray-700">
                  {systemStats.openPositions} Positions
                </Badge>
                <Badge variant="outline" className="text-xs bg-gray-800/50 text-gray-300 border-gray-700">
                  {systemStats.autoTraderSessions} Auto
                </Badge>
              </div>

              {/* Mobile Connection Status */}
              <div className="flex items-center justify-center gap-2 mt-4 px-3 py-2 bg-gray-800/50 rounded-lg">
                {getConnectionIcon()}
                <span className="text-sm font-medium text-gray-300">
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
