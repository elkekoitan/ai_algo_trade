"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Loader2, ArrowUpRight, ArrowDownLeft, History } from "lucide-react";
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';
import { Badge } from "@/components/ui/badge";

const fetcher = (url: string) => fetch(url).then(res => {
    if (!res.ok) {
        throw new Error('Network response was not ok');
    }
    return res.json();
});

interface Trade {
    ticket: number;
    symbol: string;
    type: string;
    volume: number;
    price: number;
    profit: number;
    time: string;
    comment: string;
}

interface TradeHistoryResponse {
    success: boolean;
    data: Trade[];
    count: number;
    last_update?: string;
}

export default function TradeHistoryTable() {
    const { data, error } = useSWR<TradeHistoryResponse>(API_ENDPOINTS.history, fetcher, { refreshInterval: 30000 });
    
    // Extract trades from response
    const trades = data?.data || [];
    const loading = !data && !error;

    return (
        <Card className="bg-gray-900/50 border-gray-800">
            <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                    <div className="flex items-center">
                        <History className="h-5 w-5 mr-2 text-cyan-400" />
                        Recent Trade History
                    </div>
                    {data?.count && (
                        <span className="text-sm text-gray-400 font-normal">
                            {data.count} trades
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ScrollArea className="h-[350px]">
                    <Table>
                        <TableHeader>
                            <TableRow className="border-gray-700 hover:bg-gray-800/50">
                                <TableHead className="text-gray-400">Symbol</TableHead>
                                <TableHead className="text-gray-400">Type</TableHead>
                                <TableHead className="text-center text-gray-400">Volume</TableHead>
                                <TableHead className="text-right text-gray-400">Price</TableHead>
                                <TableHead className="text-right text-gray-400">Profit</TableHead>
                                <TableHead className="text-right text-gray-400">Time</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center">
                                        <div className="flex items-center justify-center">
                                            <Loader2 className="h-6 w-6 text-cyan-400 animate-spin" />
                                            <p className="ml-2 text-gray-400">Loading trade history...</p>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            )}
                             {error && (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center text-red-400">
                                        Failed to load trade history.
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && trades.length === 0 && !error && (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center text-gray-500">
                                        No recent trade history found.
                                    </TableCell>
                                </TableRow>
                            )}
                            {trades.map((trade) => (
                                <TableRow key={trade.ticket} className="border-gray-800 hover:bg-gray-800/50">
                                    <TableCell className="font-medium text-white">{trade.symbol}</TableCell>
                                    <TableCell>
                                        <Badge variant={trade.type === 'buy' ? 'default' : 'destructive'} 
                                               className={`capitalize ${trade.type === 'buy' ? 'bg-green-600/20 text-green-300 border-green-500/30' : 'bg-red-600/20 text-red-300 border-red-500/30'}`}>
                                            {trade.type === 'buy' ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownLeft className="h-3 w-3 mr-1" />}
                                            {trade.type}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-center text-gray-300">{trade.volume}</TableCell>
                                    <TableCell className="text-right font-mono text-gray-300">
                                        {trade.price.toFixed(trade.symbol.includes('JPY') ? 3 : 5)}
                                    </TableCell>
                                    <TableCell className={`text-right font-mono ${trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {trade.profit >= 0 ? '+' : ''}${trade.profit.toFixed(2)}
                                    </TableCell>
                                    <TableCell className="text-right text-gray-500 text-xs">
                                        {new Date(trade.time).toLocaleDateString()} <br/>
                                        {new Date(trade.time).toLocaleTimeString()}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </ScrollArea>
                {data?.last_update && (
                    <div className="mt-2 text-xs text-gray-500 text-right">
                        Last update: {new Date(data.last_update).toLocaleTimeString()}
                    </div>
                )}
            </CardContent>
        </Card>
    );
} 