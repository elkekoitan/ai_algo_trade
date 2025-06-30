'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BookText, Target, TrendingUp, AlertTriangle } from 'lucide-react';
import { MarketNarrative } from '@/lib/types/market-narrator';

interface StoryDetailProps {
  narrative: MarketNarrative | null;
}

export function StoryDetail({ narrative }: StoryDetailProps) {
  if (!narrative) {
    return (
      <Card className="bg-black/40 border-gray-700 h-[40vh]">
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <BookText size={48} className="mx-auto mb-4" />
            <p>Select a narrative from the feed to see the full story.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const sentimentData = narrative.sentiment_arc.map((score, index) => ({
    name: `t-${index}`,
    sentiment: score,
  }));

  const overallSentiment = narrative.sentiment_arc.length > 0 ? narrative.sentiment_arc.reduce((a, b) => a + b, 0) / narrative.sentiment_arc.length : 0;

  return (
    <Card className="bg-black/40 border-gray-700">
      <CardHeader>
        <CardTitle className="text-xl text-indigo-300">{narrative.title}</CardTitle>
        <div className="flex items-center gap-2 text-xs text-gray-400 pt-2 flex-wrap">
            <Badge variant="outline" className="border-cyan-400 text-cyan-300">{narrative.key_theme}</Badge>
            {narrative.protagonist_symbols.map(symbol => (
                <Badge key={symbol} variant="secondary">{symbol}</Badge>
            ))}
            <span className="text-gray-500 hidden sm:inline">|</span>
            <span>Confidence: <span className="font-bold text-white">{(narrative.confidence_level * 100).toFixed(0)}%</span></span>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-cyan-400 mb-2 flex items-center gap-2"><BookText size={18}/>Full Narrative</h4>
            <ScrollArea className="h-48 bg-gray-900/50 p-3 rounded-md border border-gray-700">
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{narrative.full_story}</p>
            </ScrollArea>
          </div>
          <div>
            <h4 className="font-semibold text-yellow-400 mb-2 flex items-center gap-2"><AlertTriangle size={18}/>Market Implications</h4>
            <p className="text-sm bg-yellow-900/30 p-3 rounded-md border border-yellow-500/30 text-yellow-200">{narrative.market_implication}</p>
          </div>
          <div>
            <h4 className="font-semibold text-green-400 mb-2 flex items-center gap-2"><TrendingUp size={18}/>Potential Trades</h4>
            <div className="space-y-2">
              {narrative.potential_trades.map((trade, index) => (
                <div key={index} className="bg-gray-800/70 p-2 rounded-md text-xs flex justify-between items-center">
                  <div>
                    <span className={`font-bold ${trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>{trade.action} {trade.symbol}</span>
                    <span className="text-gray-400 ml-2">{trade.reason}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">Conf: {(trade.confidence * 100).toFixed(0)}%</Badge>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
            <h4 className="font-semibold text-purple-400 mb-2 flex items-center gap-2"><Target size={18}/>Sentiment Arc</h4>
            <div className="h-64 w-full bg-gray-900/50 p-2 rounded-md border border-gray-700">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={sentimentData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                        <defs>
                            <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={overallSentiment > 0 ? "#82ca9d" : "#ca8282"} stopOpacity={0.8}/>
                            <stop offset="95%" stopColor={overallSentiment > 0 ? "#82ca9d" : "#ca8282"} stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                        <XAxis dataKey="name" stroke="#8884d8" fontSize={12} />
                        <YAxis domain={[-1, 1]} stroke="#8884d8" fontSize={12} />
                        <Tooltip
                            contentStyle={{ 
                                backgroundColor: 'rgba(20, 20, 30, 0.8)', 
                                border: '1px solid #4a00e0',
                                color: '#fff'
                            }}
                            itemStyle={{ color: '#ddd' }}
                        />
                        <Area type="monotone" dataKey="sentiment" stroke={overallSentiment > 0 ? "#82ca9d" : "#ca8282"} fillOpacity={1} fill="url(#colorSentiment)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
      </CardContent>
    </Card>
  );
} 