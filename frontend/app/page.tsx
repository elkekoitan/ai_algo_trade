'use client';

import React from 'react';
import Header from '@/components/layout/Header';
import AccountInfo from '@/components/dashboard/AccountInfo';
import QuickTrade from '@/components/dashboard/QuickTrade';
import AutoTraderControl from '@/components/dashboard/AutoTraderControl';
import MarketScanner from '@/components/dashboard/MarketScanner';
import PerformanceChart from '@/components/performance/EquityCurveChart';

const AdvancedDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Top Row: Account Info and Quick Trade */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AccountInfo />
          </div>
          <div>
            <QuickTrade />
          </div>
        </div>

        {/* Second Row: Autotrader and Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <AutoTraderControl />
          </div>
          <div>
            <PerformanceChart data={[]} height={300} showControls={false} />
          </div>
        </div>

        {/* Third Row: Market Scanner */}
        <div>
          <MarketScanner />
        </div>
      </main>
    </div>
  );
};

export default AdvancedDashboardPage; 