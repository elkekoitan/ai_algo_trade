"use client";

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Send, Repeat, AlertCircle } from 'lucide-react';
import ApiService from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { API_ENDPOINTS } from '@/lib/api';

interface TickData {
  time: string;
  bid: number;
  ask: number;
  last: number;
}

const QuickTrade = () => {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD');
  const [tick, setTick] = useState<TickData | null>(null);
  const [volume, setVolume] = useState('0.01');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastOrder, setLastOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [action, setAction] = useState('BUY');
  const [responseMsg, setResponseMsg] = useState('');

  // Fetch all available symbols on component mount
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        setLoading(true);
        const response = await ApiService.getSymbols();
        
        if (!response.error && response.data) {
          if (Array.isArray(response.data)) {
            const symbolData = response.data;
            // Gelen verinin bir nesne dizisi olup olmadığını kontrol et ve sadece 'name' alanını al
            if (symbolData.length > 0 && typeof symbolData[0] === 'object' && symbolData[0] !== null && 'name' in symbolData[0]) {
              setSymbols(symbolData.map((s: any) => s.name));
            } else {
              setSymbols(symbolData); // Zaten string dizisi ise olduğu gibi kullan
            }
            setError(null);
          } else {
            console.error("Symbols data is not an array:", response.data);
            setSymbols([]);
            setError("Invalid symbols data format");
          }
        } else {
          setError(response.message || "Failed to fetch symbols");
          setSymbols([]);
        }
      } catch (error) {
        console.error("Error fetching symbols:", error);
        setError("Connection error");
        setSymbols([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSymbols();
  }, []);

  // Fetch tick data for the selected symbol periodically
  useEffect(() => {
    if (!selectedSymbol) return;

    const fetchTick = async () => {
      try {
        const response = await ApiService.getSymbolTick(selectedSymbol);
        if (!response.error && response.data) {
          setTick(response.data);
          setError(null);
        } else {
          console.error(`Error fetching tick: ${response.message}`);
          setTick(null);
        }
      } catch (error) {
        console.error(`Error fetching tick for ${selectedSymbol}:`, error);
        setTick(null);
      }
    };

    fetchTick();
    const interval = setInterval(fetchTick, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleTrade = async () => {
    setIsSubmitting(true);
    setLastOrder(null);
    setResponseMsg('');

    const orderData = {
      symbol: selectedSymbol,
      order_type: action, // 'BUY' or 'SELL'
      volume: parseFloat(volume) || 0.01,
      price: 0, // Market order
      sl: 0,
      tp: 0,
      magic: 234001,
      comment: "QuickTrade"
    };

    try {
      const response = await ApiService.placeOrder(orderData);
      
      if (!response.error && response.data?.success) {
        setLastOrder({ success: true, ...response.data });
        setResponseMsg(`Success: Order #${response.data.order_id} placed.`);
      } else {
        setLastOrder({ 
          success: false, 
          message: response.message || 'Failed to place trade.' 
        });
        setResponseMsg(`Error: ${response.message || 'Failed to place trade.'}`);
      }
    } catch (error) {
      console.error("Error placing trade:", error);
      setLastOrder({ 
        success: false, 
        message: 'Error: Network request failed.' 
      });
      setResponseMsg('Error: Network request failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentPrice = tick?.ask ?? 0;
  const priceColor = tick && tick.last > 0 ? (tick.ask > tick.last ? 'text-green-400' : 'text-red-400') : 'text-white';

  // Default symbols if API fails
  const defaultSymbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD'];
  const displaySymbols = symbols.length > 0 ? symbols : defaultSymbols;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Trade</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <Label htmlFor="symbol">Symbol</Label>
              <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Symbol" />
                </SelectTrigger>
                <SelectContent>
                  {displaySymbols.map((symbol) => (
                    <SelectItem key={symbol} value={symbol}>{symbol}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="volume">Volume</Label>
              <Input id="volume" type="number" value={volume} onChange={(e) => setVolume(e.target.value)} step="0.01" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Button variant="outline" className={action === 'BUY' ? 'ring-2 ring-green-500' : ''} onClick={() => setAction('BUY')}>BUY</Button>
            <Button variant="outline" className={action === 'SELL' ? 'ring-2 ring-red-500' : ''} onClick={() => setAction('SELL')}>SELL</Button>
          </div>
          <Button onClick={handleTrade} disabled={isSubmitting}>
            {isSubmitting ? 'Executing...' : `Execute ${action} ${selectedSymbol}`}
          </Button>
          {responseMsg && <p className="text-sm text-center text-muted-foreground">{responseMsg}</p>}
        </div>
      </CardContent>
    </Card>
  );
};

export default QuickTrade; 