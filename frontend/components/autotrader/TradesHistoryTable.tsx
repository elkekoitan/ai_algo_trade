"use client";

import useSWR from 'swr';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from "@/components/ui/badge";

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function TradesHistoryTable() {
    const { data: trades, error } = useSWR('http://localhost:8004/api/v1/positions', fetcher, { refreshInterval: 5000 });

    if (error) return <div>Failed to load trade history. Is the backend running?</div>
    if (!trades) return <div>Loading Trade History...</div>
    
    const tradeData = trades.data || [];

    if (tradeData.length === 0) return <div className="text-center text-sm text-muted-foreground">No trades have been executed yet.</div>

    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>P/L</TableHead>
                    <TableHead className="text-right">Source</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {tradeData.map((trade: any) => (
                    <TableRow key={trade.ticket}>
                        <TableCell className="font-medium">{trade.symbol}</TableCell>
                        <TableCell>
                             <Badge variant={trade.type === 'buy' ? 'default' : 'destructive'}>
                                {trade.type.toUpperCase()}
                            </Badge>
                        </TableCell>
                         <TableCell className={trade.profit > 0 ? "text-green-500" : "text-red-500"}>
                            {trade.profit.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right">{trade.comment}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
} 