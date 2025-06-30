"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, Zap, Target, Percent } from "lucide-react";
import AutoTraderChart from "@/components/autotrader/AutoTraderChart";
import TradesHistoryTable from "@/components/autotrader/TradesHistoryTable";

const AutoTraderDashboardPage = () => {
    // Bu kısım daha sonra API'den gelen verilerle doldurulacak
    const status = {
        balance: 2595000.50,
        equity: 2595150.75,
        total_profit: 150.25,
        total_trades: 42,
        winning_trades: 30,
        win_rate: 71.4,
        active_positions: 3,
        floating_pnl: 25.10
    };

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Auto-Trader Dashboard</h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Total Equity
                        </CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">${status.equity.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">
                            Floating P&L: ${status.floating_pnl.toFixed(2)}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Profit</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">${status.total_profit.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">
                           Based on closed trades
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                        <Target className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{status.win_rate.toFixed(1)}%</div>
                        <p className="text-xs text-muted-foreground">
                            {status.winning_trades} wins out of {status.total_trades} trades
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Positions</CardTitle>
                        <Zap className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">+{status.active_positions}</div>
                        <p className="text-xs text-muted-foreground">
                            Currently open trades
                        </p>
                    </CardContent>
                </Card>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Equity Curve</CardTitle>
                    </CardHeader>
                    <CardContent className="pl-2">
                       <AutoTraderChart />
                    </CardContent>
                </Card>
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Recent Trades</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <TradesHistoryTable />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default AutoTraderDashboardPage; 