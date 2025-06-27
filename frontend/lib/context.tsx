'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import ApiService, { ApiResponse } from '@/lib/api';

// Define types for our context
interface AccountInfo {
  login: number;
  balance: number;
  equity: number;
  profit: number;
  server: string;
  company: string;
  currency: string;
  leverage: number;
  margin: number;
  free_margin: number;
  margin_level: number;
}

interface Position {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  open_price: number;
  current_price: number;
  profit: number;
  swap: number;
  open_time: string;
}

interface ConnectionStatus {
  mt5: boolean;
  api: boolean;
  lastUpdate: Date;
}

interface AppContextType {
  // Account & Trading
  accountInfo: AccountInfo | null;
  positions: Position[];
  symbols: string[];
  
  // Connection status
  connectionStatus: ConnectionStatus;
  
  // Loading & error states
  isLoading: {
    account: boolean;
    positions: boolean;
    symbols: boolean;
  };
  errors: {
    account: string | null;
    positions: string | null;
    symbols: string | null;
  };
  
  // UI state
  activeSymbol: string;
  setActiveSymbol: (symbol: string) => void;
  activeTimeframe: string;
  setActiveTimeframe: (timeframe: string) => void;
  
  // Actions
  refreshAccountInfo: () => Promise<void>;
  refreshPositions: () => Promise<void>;
  refreshSymbols: () => Promise<void>;
  refreshAll: () => Promise<void>;
}

// Create the context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Account & Trading state
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  
  // Connection status
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    mt5: false,
    api: false,
    lastUpdate: new Date()
  });
  
  // Loading states
  const [isLoading, setIsLoading] = useState({
    account: true,
    positions: true,
    symbols: true
  });
  
  // Error states
  const [errors, setErrors] = useState({
    account: null as string | null,
    positions: null as string | null,
    symbols: null as string | null
  });
  
  // UI state
  const [activeSymbol, setActiveSymbol] = useState('EURUSD');
  const [activeTimeframe, setActiveTimeframe] = useState('H1');
  
  // Fetch account info
  const refreshAccountInfo = async () => {
    setIsLoading(prev => ({ ...prev, account: true }));
    
    try {
      const response = await ApiService.getAccountInfo();
      
      if (!response.error && response.data) {
        setAccountInfo(response.data);
        setErrors(prev => ({ ...prev, account: null }));
      } else {
        setErrors(prev => ({ ...prev, account: response.message || 'Failed to fetch account data' }));
      }
    } catch (error) {
      setErrors(prev => ({ ...prev, account: 'Connection error' }));
    } finally {
      setIsLoading(prev => ({ ...prev, account: false }));
    }
  };
  
  // Fetch positions
  const refreshPositions = async () => {
    setIsLoading(prev => ({ ...prev, positions: true }));
    
    try {
      const response = await ApiService.getPositions();
      
      if (!response.error && response.data) {
        setPositions(response.data.positions || []);
        setErrors(prev => ({ ...prev, positions: null }));
      } else {
        setErrors(prev => ({ ...prev, positions: response.message || 'Failed to fetch positions' }));
      }
    } catch (error) {
      setErrors(prev => ({ ...prev, positions: 'Connection error' }));
    } finally {
      setIsLoading(prev => ({ ...prev, positions: false }));
    }
  };
  
  // Fetch symbols
  const refreshSymbols = async () => {
    setIsLoading(prev => ({ ...prev, symbols: true }));
    
    try {
      const response = await ApiService.getSymbols();
      
      if (!response.error && response.data) {
        if (Array.isArray(response.data)) {
          setSymbols(response.data);
          setErrors(prev => ({ ...prev, symbols: null }));
        } else {
          setErrors(prev => ({ ...prev, symbols: 'Invalid symbols data format' }));
        }
      } else {
        setErrors(prev => ({ ...prev, symbols: response.message || 'Failed to fetch symbols' }));
      }
    } catch (error) {
      setErrors(prev => ({ ...prev, symbols: 'Connection error' }));
    } finally {
      setIsLoading(prev => ({ ...prev, symbols: false }));
    }
  };
  
  // Check connection status
  const checkConnection = async () => {
    try {
      const response = await ApiService.getHealth();
      
      setConnectionStatus({
        mt5: !!response.data?.mt5_connected,
        api: !response.error,
        lastUpdate: new Date()
      });
    } catch (error) {
      setConnectionStatus(prev => ({
        ...prev,
        api: false,
        lastUpdate: new Date()
      }));
    }
  };
  
  // Refresh all data
  const refreshAll = async () => {
    await Promise.all([
      refreshAccountInfo(),
      refreshPositions(),
      refreshSymbols(),
      checkConnection()
    ]);
  };
  
  // Initial data load
  useEffect(() => {
    refreshAll();
    
    // Set up periodic refreshes
    const accountInterval = setInterval(refreshAccountInfo, 5000);
    const positionsInterval = setInterval(refreshPositions, 3000);
    const connectionInterval = setInterval(checkConnection, 10000);
    
    return () => {
      clearInterval(accountInterval);
      clearInterval(positionsInterval);
      clearInterval(connectionInterval);
    };
  }, []);
  
  const value = {
    // Data
    accountInfo,
    positions,
    symbols,
    connectionStatus,
    
    // Loading & error states
    isLoading,
    errors,
    
    // UI state
    activeSymbol,
    setActiveSymbol,
    activeTimeframe,
    setActiveTimeframe,
    
    // Actions
    refreshAccountInfo,
    refreshPositions,
    refreshSymbols,
    refreshAll
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Custom hook to use the context
export const useAppContext = () => {
  const context = useContext(AppContext);
  
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  
  return context;
}; 