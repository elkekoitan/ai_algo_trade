import React from 'react';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface TradeHistoryProps {
    history: any[];
    isLoading: boolean;
}

const TradeHistory = ({ history, isLoading }: TradeHistoryProps) => {
    if (isLoading) {
        return (
          <div className="flex justify-center items-center h-24">
            <Loader2 className="animate-spin h-6 w-6 text-cyan-400" />
          </div>
        );
    }

    if (history.length === 0) {
        return <div className="text-center py-4 text-gray-500">No trade history available.</div>;
    }

    return (
        <div className="space-y-2">
            {history.map((trade, index) => (
                <div key={index} className="flex justify-between items-center text-sm p-1 rounded bg-gray-700/30">
                    <span className="text-gray-400">{trade.date}</span>
                    <span className={`font-mono ${trade.equity > 10000 ? 'text-green-400' : 'text-red-400'}`}>${trade.equity.toLocaleString()}</span>
                </div>
            ))}
        </div>
    );
};

export default TradeHistory; 