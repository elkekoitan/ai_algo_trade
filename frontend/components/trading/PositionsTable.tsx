import React from 'react';
import { Card } from '@/components/ui/card';
import { Loader2, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Position } from '@/lib/types';

interface PositionsTableProps {
  positions: Position[];
  isLoading: boolean;
}

const PositionsTable = ({ positions, isLoading }: PositionsTableProps) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-40">
        <Loader2 className="animate-spin h-8 w-8 text-cyan-400" />
      </div>
    );
  }

  if (positions.length === 0) {
    return <div className="text-center py-4 text-gray-500">No open positions.</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-gray-700 text-gray-400 text-sm">
            <th className="p-2">Symbol</th>
            <th className="p-2">Type</th>
            <th className="p-2">Volume</th>
            <th className="p-2">Open Price</th>
            <th className="p-2">Current Price</th>
            <th className="p-2">P/L</th>
            <th className="p-2"></th>
          </tr>
        </thead>
        <tbody>
          {positions.map((p) => (
            <tr key={p.ticket} className="border-b border-gray-800 hover:bg-gray-700/50">
              <td className="p-2 font-mono">{p.symbol}</td>
              <td className={`p-2 font-semibold ${p.type === 'BUY' ? 'text-blue-400' : 'text-red-400'}`}>
                <div className="flex items-center">
                   {p.type === 'BUY' ? <TrendingUp className="h-4 w-4 mr-1"/> : <TrendingDown className="h-4 w-4 mr-1"/>}
                   {p.type}
                </div>
              </td>
              <td className="p-2">{p.volume}</td>
              <td className="p-2">{p.open_price}</td>
              <td className="p-2">{p.current_price}</td>
              <td className={`p-2 font-mono ${p.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {p.profit.toFixed(2)}
              </td>
              <td className="p-2 text-right">
                <button className="text-xs text-gray-400 hover:text-white">Close</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PositionsTable; 