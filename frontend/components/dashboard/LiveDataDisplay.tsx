"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';

interface PriceData {
  symbol: string;
  bid: number;
  ask: number;
  spread: number;
}

interface AccountInfo {
  login: number;
  balance: number;
  equity: number;
  currency: string;
  open_positions: number;
  total_profit: number;
}

// This is a more focused component now.
// The main page uses AccountInfo and other specific components.
export function LivePriceGrid({ prices }: { prices: PriceData[] }) {
  if (!prices || prices.length === 0) {
    return <div className="text-center text-gray-400">Fiyat verisi bekleniyor...</div>
  }
  
  return (
    <div className="grid grid-cols-2 gap-4">
      {prices.map((price) => (
        <div key={price.symbol} className="bg-gray-800 p-3 rounded-lg text-center">
          <p className="font-bold text-white">{price.symbol}</p>
          <p className="text-lg text-cyan-400 font-mono">{price.bid.toFixed(5)}</p>
          <p className="text-xs text-gray-400">Spread: {price.spread.toFixed(1)}</p>
        </div>
      ))}
    </div>
  )
}

// The following is kept for potential future use or reference, but is not actively used on the main dashboard.
const LiveDataDisplay = () => {
  const [liveData, setLiveData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const response = await fetch('http://localhost:8002/api/system/unified-view');
        if (response.ok) {
          const data = await response.json();
          // Extract relevant data for this component's potential use
          setLiveData({
            prices: data.signals?.map((s: any) => ({ symbol: s.symbol, bid: s.current_price, ask: s.current_price + 0.0001, spread: 1.0 })),
            account: data.modules?.adaptive_trader
          });
        }
      } catch (error) {
        console.error('Error fetching live data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLiveData();
    const interval = setInterval(fetchLiveData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) return <p>Yükleniyor...</p>;

  if (!liveData) return <p>Veri alınamadı.</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Canlı Veri</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Bakiye: {liveData.account?.total_pnl}</p>
        <LivePriceGrid prices={liveData.prices || []} />
      </CardContent>
    </Card>
  );
};

export default LiveDataDisplay; 