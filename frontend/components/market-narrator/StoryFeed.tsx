'use client'
import React from 'react'
import { motion } from 'framer-motion'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { BookOpen } from 'lucide-react'
import { MarketNarrative } from '@/lib/types/market-narrator'

interface StoryFeedProps {
    narratives: MarketNarrative[];
    onSelectNarrative: (narrative: MarketNarrative) => void;
    selectedNarrativeId?: string;
    isLoading: boolean;
}

const getConfidenceColor = (level: number) => {
    if (level > 0.8) return 'border-green-400 text-green-300';
    if (level > 0.6) return 'border-yellow-400 text-yellow-300';
    return 'border-orange-400 text-orange-300';
};

export function StoryFeed({ narratives, onSelectNarrative, selectedNarrativeId, isLoading }: StoryFeedProps) {
    if (isLoading) {
        return (
            <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                    <div key={i} className="bg-gray-800/50 rounded-lg p-4 animate-pulse">
                        <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-700 rounded w-full mb-3"></div>
                        <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                    </div>
                ))}
            </div>
        );
    }

    if (narratives.length === 0) {
        return (
            <div className="text-center text-gray-500 py-10">
                <BookOpen size={48} className="mx-auto mb-4" />
                <p>No narratives available.</p>
                <p className="text-sm">Try generating a new one.</p>
            </div>
        );
    }

    return (
        <ScrollArea className="h-[calc(80vh-100px)]">
            <div className="space-y-3 pr-4">
                {narratives.map((narrative) => (
                    <motion.div
                        key={narrative.narrative_id}
                        onClick={() => onSelectNarrative(narrative)}
                        className={`p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
                            selectedNarrativeId === narrative.narrative_id
                                ? 'bg-indigo-500/30 border-indigo-400'
                                : 'bg-black/30 border-transparent hover:border-indigo-500/50'
                        }`}
                        layout
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <p className="text-sm font-bold text-white">{narrative.title}</p>
                            <Badge variant="outline" className={`text-xs ${getConfidenceColor(narrative.confidence_level)}`}>
                                {(narrative.confidence_level * 100).toFixed(0)}%
                            </Badge>
                        </div>

                        <p className="text-xs text-gray-400 mb-3">{narrative.summary}</p>
                        
                        <div className="flex items-center justify-between">
                            <div className="flex gap-2">
                                {narrative.protagonist_symbols.slice(0, 3).map((symbol) => (
                                    <Badge key={symbol} variant="secondary" className="text-xs bg-gray-700 text-gray-300">
                                        {symbol}
                                    </Badge>
                                ))}
                            </div>
                            <span className="text-xs text-gray-500">
                                {new Date(narrative.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                    </motion.div>
                ))}
            </div>
        </ScrollArea>
    );
} 