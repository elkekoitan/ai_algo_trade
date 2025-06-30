"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp, Loader2 } from "lucide-react";
import useSWR from 'swr';
import { API_BASE_URL } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const fetcher = (url: string) => fetch(url).then(res => res.json());

interface EquityPoint {
  time: string;
  equity: number;
  profit: number;
  trade_count: number;
}

interface EquityCurveResponse {
  success: boolean;
  data: EquityPoint[];
  count: number;
}

// Custom Tooltip for the chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-gray-900/90 backdrop-blur p-2 shadow-lg border-gray-700">
        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col space-y-1">
            <span className="text-[0.70rem] uppercase text-gray-400">
              Date
            </span>
            <span className="font-bold text-gray-200 text-xs">
              {new Date(label).toLocaleDateString()}
            </span>
          </div>
          <div className="flex flex-col space-y-1">
            <span className="text-[0.70rem] uppercase text-gray-400">
              Equity
            </span>
            <span className="font-bold text-green-400">
              ${payload[0].value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>
        {payload[0].payload.profit !== undefined && (
          <div className="mt-2 pt-2 border-t border-gray-700">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Trade P&L:</span>
              <span className={payload[0].payload.profit >= 0 ? 'text-green-400' : 'text-red-400'}>
                {payload[0].payload.profit >= 0 ? '+' : ''}${payload[0].payload.profit.toFixed(2)}
              </span>
            </div>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function PerformanceChart() {
    const { data, error } = useSWR<EquityCurveResponse>(`${API_BASE_URL}/api/v1/performance/equity_curve`, fetcher, { 
        refreshInterval: 60000,
        revalidateOnFocus: true 
    });

    // Extract chart data from response
    const chartData = data?.data || [];
    const loading = !data && !error;

    // Calculate statistics
    const startEquity = chartData.length > 0 ? chartData[0].equity : 0;
    const endEquity = chartData.length > 0 ? chartData[chartData.length - 1].equity : 0;
    const totalProfit = endEquity - startEquity;
    const profitPercentage = startEquity > 0 ? ((totalProfit / startEquity) * 100) : 0;

    return (
        <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                    <div className="flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2 text-green-400" />
                        Equity Curve
                    </div>
                    {chartData.length > 0 && (
                        <div className="flex items-center gap-3 text-sm">
                            <span className={`font-medium ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {totalProfit >= 0 ? '+' : ''}{profitPercentage.toFixed(2)}%
                            </span>
                            <span className="text-gray-400 font-normal">
                                ({chartData.length} trades)
                            </span>
                        </div>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    {loading && (
                        <div className="flex items-center justify-center h-full">
                            <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
                            <p className="ml-2 text-gray-400">Loading performance data...</p>
                        </div>
                    )}
                    {error && (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-red-400">Failed to load performance data.</p>
                        </div>
                    )}
                    {!loading && chartData.length === 0 && !error && (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <TrendingUp className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                                <p className="text-gray-500">No equity data available yet.</p>
                                <p className="text-xs text-gray-600 mt-1">Start trading to see your equity curve!</p>
                            </div>
                        </div>
                    )}
                    {chartData.length > 0 && (
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                                data={chartData}
                                margin={{
                                    top: 5,
                                    right: 20,
                                    left: 20,
                                    bottom: 5,
                                }}
                            >
                                <defs>
                                    <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                                <XAxis 
                                    dataKey="time" 
                                    tickFormatter={(str) => {
                                        const date = new Date(str);
                                        return `${date.getMonth() + 1}/${date.getDate()}`;
                                    }}
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    stroke="#6b7280"
                                />
                                <YAxis 
                                    domain={['dataMin - 100', 'dataMax + 100']}
                                    tickFormatter={(val) => `$${(val/1000).toFixed(0)}k`}
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    stroke="#6b7280"
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Area 
                                    type="monotone" 
                                    dataKey="equity" 
                                    stroke="#22c55e" 
                                    strokeWidth={2}
                                    fill="url(#colorEquity)" 
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </CardContent>
        </Card>
    );
} 