'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { RefreshCw } from 'lucide-react';

const MarketScanner: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'US30'];

  return (
    <div>
      <Card className="w-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-medium mb-2">Scanning Markets</h3>
            <p className="text-sm text-gray-600">Analyzing opportunities across {symbols.length} symbols...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MarketScanner; 