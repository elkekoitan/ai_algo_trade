"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
    BarChart, 
    TrendingUp, 
    TrendingDown, 
    Zap, 
    Target, 
    Percent, 
    Plus, 
    Minus,
    Loader2,
    AlertTriangle,
    Trophy,
    DollarSign,
    Activity
} from "lucide-react";
import useSWR from 'swr';
import { API_BASE_URL } from '@/lib/api';

const fetcher = (url: string) => fetch(url).then(res => res.json());

interface PerformanceData {
    balance: number;
    equity: number;
    profit: number;
    margin: number;
    free_margin: number;
    margin_level: number;
    open_positions: number;
    total_profit_today: number;
    daily_stats: {
        total_trades: number;
        winning_trades: number;
        losing_trades: number;
        total_profit: number;
        win_rate: number;
        average_profit: number;
        best_trade: number;
        worst_trade: number;
    };
    last_update?: string;
}

const MetricCard = ({ title, value, icon: Icon, color, unit, info }: { 
    title: string; 
    value: string | number; 
    icon: React.ElementType; 
    color: string;
    unit?: string;
    info?: string;
}) => (
    <div className="bg-gray-800/50 p-3 rounded-lg">
        <div className="flex items-center justify-between mb-1">
            <p className="text-xs text-gray-400">{title}</p>
            <Icon className={`h-4 w-4 ${color}`} />
        </div>
        <p className="text-lg font-bold text-white">
            {value}
            {unit && <span className="text-xs ml-1 text-gray-400">{unit}</span>}
        </p>
        {info && <p className="text-xs text-gray-500 mt-1">{info}</p>}
    </div>
);

export default function PerformanceMetrics() {
    const { data, error } = useSWR<PerformanceData>(`${API_BASE_URL}/api/v1/performance/performance_summary`, fetcher, { 
        refreshInterval: 30000,
        revalidateOnFocus: true 
    });

    if (error) {
        return (
            <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                    <CardTitle className="text-red-400 flex items-center">
                        <AlertTriangle className="h-5 w-5 mr-2" />
                        Performance Metrics
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center h-32 text-red-400">
                    Failed to load performance data.
                </CardContent>
            </Card>
        );
    }
    
    if (!data) {
        return (
            <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                    <CardTitle className="text-white flex items-center">
                        <BarChart className="h-5 w-5 mr-2 text-blue-400" />
                        Performance Metrics
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center h-56">
                    <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
                </CardContent>
            </Card>
        );
    }

    const stats = data.daily_stats || {};
    const profitColor = data.profit >= 0 ? 'text-green-400' : 'text-red-400';
    const winRateColor = stats.win_rate >= 50 ? 'text-green-400' : 'text-red-400';
    const profitFactorColor = stats.winning_trades > stats.losing_trades ? 'text-green-400' : 'text-red-400';

    return (
        <Card className="bg-gray-900/50 border-gray-800 h-full">
            <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                    <div className="flex items-center">
                    <BarChart className="h-5 w-5 mr-2 text-blue-400" />
                    Performance Metrics
                    </div>
                    {data.last_update && (
                        <span className="text-xs text-gray-400 font-normal">
                            Updated: {new Date(data.last_update).toLocaleTimeString()}
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 gap-3">
                    <MetricCard 
                        title="Total P&L" 
                        value={stats.total_profit >= 0 ? `+$${stats.total_profit.toFixed(2)}` : `-$${Math.abs(stats.total_profit).toFixed(2)}`} 
                        icon={stats.total_profit >= 0 ? TrendingUp : TrendingDown} 
                        color={stats.total_profit >= 0 ? 'text-green-400' : 'text-red-400'} 
                    />
                    <MetricCard 
                        title="Win Rate" 
                        value={stats.win_rate.toFixed(1)}
                        unit="%"
                        icon={Trophy} 
                        color={winRateColor}
                    />
                     <MetricCard 
                        title="Total Trades" 
                        value={stats.total_trades} 
                        icon={Target} 
                        color="text-cyan-400"
                        info={`${stats.winning_trades}W / ${stats.losing_trades}L`}
                    />
                    <MetricCard 
                        title="Profit Factor" 
                        value={(stats.winning_trades / (stats.losing_trades || 1)).toFixed(2)}
                        icon={Zap} 
                        color={profitFactorColor}
                    />
                    <MetricCard 
                        title="Average P&L" 
                        value={`$${stats.average_profit.toFixed(2)}`} 
                        icon={DollarSign} 
                        color={stats.average_profit >= 0 ? 'text-green-400' : 'text-red-400'}
                    />
                    <MetricCard 
                        title="Open Positions" 
                        value={data.open_positions}
                        icon={Activity} 
                        color="text-blue-400"
                        info={`Margin: ${data.margin_level.toFixed(0)}%`}
                    />
                     <MetricCard 
                        title="Best Trade" 
                        value={`$${stats.best_trade.toFixed(2)}`} 
                        icon={TrendingUp} 
                        color="text-green-400"
                    />
                    <MetricCard 
                        title="Worst Trade" 
                        value={`$${stats.worst_trade.toFixed(2)}`}
                        icon={TrendingDown} 
                        color="text-red-400"
                    />
                </div>
            </CardContent>
        </Card>
    );
} 