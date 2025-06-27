"use client";

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface EquityData {
  date: string;
  equity: number;
  drawdown: number;
}

interface EquityCurveChartProps {
  data: EquityData[];
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400">No equity data available</p>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#00ff88" stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            opacity={0.3}
          />
          
          <XAxis 
            dataKey="date"
            tickFormatter={formatDate}
            stroke="#9CA3AF"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          
          <YAxis 
            tickFormatter={formatCurrency}
            stroke="#9CA3AF"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
            formatter={(value: number, name: string) => [
              name === 'equity' ? formatCurrency(value) : `${value.toFixed(2)}%`,
              name === 'equity' ? 'Equity' : 'Drawdown'
            ]}
                         labelFormatter={(label: string) => `Date: ${formatDate(label)}`}
          />
          
          <Area
            type="monotone"
            dataKey="equity"
            stroke="#00ff88"
            strokeWidth={2}
            fill="url(#equityGradient)"
            dot={false}
            activeDot={{
              r: 4,
              stroke: '#00ff88',
              strokeWidth: 2,
              fill: '#1F2937'
            }}
          />
          
          <Line
            type="monotone"
            dataKey="drawdown"
            stroke="#ef4444"
            strokeWidth={1}
            dot={false}
            strokeDasharray="5 5"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityCurveChart; 