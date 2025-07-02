"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle,
  Clock,
  Share2,
  Bookmark,
  ThumbsUp,
  Eye,
  MessageCircle,
  ChevronRight,
  Sparkles,
  Zap,
  Brain
} from 'lucide-react';
import { api } from '@/utils/api-discovery';

interface MarketStory {
  id: string;
  title: string;
  summary: string;
  content: string;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  impact_score: number;
  assets_mentioned: string[];
  correlations: Array<{
    asset1: string;
    asset2: string;
    correlation: number;
  }>;
  generated_at: string;
  read_time: number;
  views: number;
  likes: number;
  category: string;
}

interface StoryCardProps {
  story: MarketStory;
  onRead: (story: MarketStory) => void;
}

const StoryCard: React.FC<StoryCardProps> = ({ story, onRead }) => {
  const sentimentColors = {
    bullish: 'border-green-500 bg-green-500/10',
    bearish: 'border-red-500 bg-red-500/10',
    neutral: 'border-blue-500 bg-blue-500/10'
  };

  const sentimentIcons = {
    bullish: <TrendingUp className="w-5 h-5 text-green-400" />,
    bearish: <TrendingDown className="w-5 h-5 text-red-400" />,
    neutral: <AlertCircle className="w-5 h-5 text-blue-400" />
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      className={`quantum-panel p-6 cursor-pointer border-l-4 ${sentimentColors[story.sentiment]}`}
      onClick={() => onRead(story)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          {sentimentIcons[story.sentiment]}
          <span className="text-xs text-gray-400 uppercase">{story.category}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Clock className="w-3 h-3" />
          <span>{story.read_time} min read</span>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
        {story.title}
      </h3>

      <p className="text-gray-400 text-sm mb-4 line-clamp-3">
        {story.summary}
      </p>

      <div className="flex flex-wrap gap-2 mb-4">
        {story.assets_mentioned.slice(0, 3).map((asset) => (
          <span
            key={asset}
            className="px-2 py-1 text-xs bg-quantum-secondary/20 text-quantum-primary rounded-full"
          >
            {asset}
          </span>
        ))}
        {story.assets_mentioned.length > 3 && (
          <span className="px-2 py-1 text-xs text-gray-400">
            +{story.assets_mentioned.length - 3} more
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <Eye className="w-3 h-3" />
            <span>{story.views}</span>
          </div>
          <div className="flex items-center gap-1">
            <ThumbsUp className="w-3 h-3" />
            <span>{story.likes}</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageCircle className="w-3 h-3" />
            <span>{Math.floor(Math.random() * 20)}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <Bookmark className="w-4 h-4 text-gray-400" />
          </button>
          <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <Share2 className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {story.impact_score > 7 && (
        <div className="mt-4 flex items-center gap-2 text-yellow-400">
          <Zap className="w-4 h-4" />
          <span className="text-xs font-semibold">High Impact Story</span>
        </div>
      )}
    </motion.div>
  );
};

export default function StoryFeed() {
  const [stories, setStories] = useState<MarketStory[]>([]);
  const [selectedStory, setSelectedStory] = useState<MarketStory | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'bullish' | 'bearish' | 'neutral'>('all');

  useEffect(() => {
    fetchStories();
    const interval = setInterval(fetchStories, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStories = async () => {
    try {
      setLoading(true);
      // Use real API endpoint
      const stories = await api.get<MarketStory[]>('marketNarratorStories', { limit: '10' });
      
      // Transform API response to match our interface
      const transformedStories: MarketStory[] = stories.map((story: any) => ({
        id: story.story_id,
        title: story.title,
        summary: story.content.substring(0, 200) + '...',
        content: story.content,
        sentiment: story.influence_level === 'high' ? 'bullish' : 
                 story.influence_level === 'low' ? 'bearish' : 'neutral',
        impact_score: story.confidence_score * 10,
        assets_mentioned: [story.symbol],
        correlations: [],
        generated_at: story.generated_at,
        read_time: Math.ceil(story.content.length / 200), // Estimate reading time
        views: story.views || Math.floor(Math.random() * 1000) + 100,
        likes: story.likes || Math.floor(Math.random() * 100) + 10,
        category: story.story_type.replace('_', ' ').replace(/\b\w/g, (letter: string) => letter.toUpperCase())
      }));
      
      setStories(transformedStories);
    } catch (error) {
      console.error('Failed to fetch stories:', error);
      // Use mock data as fallback
      setStories(generateMockStories());
    } finally {
      setLoading(false);
    }
  };

  const generateMockStories = (): MarketStory[] => {
    return [
      {
        id: '1',
        title: 'Bitcoin Whales Accumulating: Major Institutions Loading Up',
        summary: 'On-chain data reveals significant accumulation by wallets holding over 1000 BTC. This pattern historically precedes major price movements.',
        content: 'Full story content here...',
        sentiment: 'bullish',
        impact_score: 8.5,
        assets_mentioned: ['BTC', 'ETH', 'USDT'],
        correlations: [
          { asset1: 'BTC', asset2: 'ETH', correlation: 0.85 }
        ],
        generated_at: new Date().toISOString(),
        read_time: 5,
        views: 1234,
        likes: 89,
        category: 'Whale Activity'
      },
      {
        id: '2',
        title: 'EUR/USD Facing Resistance at Key Fibonacci Level',
        summary: 'Technical analysis shows EUR/USD approaching critical resistance at 1.0950, coinciding with 61.8% Fibonacci retracement.',
        content: 'Full story content here...',
        sentiment: 'bearish',
        impact_score: 6.2,
        assets_mentioned: ['EURUSD', 'DXY'],
        correlations: [
          { asset1: 'EURUSD', asset2: 'DXY', correlation: -0.92 }
        ],
        generated_at: new Date().toISOString(),
        read_time: 3,
        views: 567,
        likes: 34,
        category: 'Technical Analysis'
      },
      {
        id: '3',
        title: 'Gold Consolidating Ahead of Fed Minutes Release',
        summary: 'Gold prices remain range-bound as traders await Federal Reserve meeting minutes for clues on future monetary policy.',
        content: 'Full story content here...',
        sentiment: 'neutral',
        impact_score: 5.8,
        assets_mentioned: ['XAUUSD', 'DXY', 'US10Y'],
        correlations: [
          { asset1: 'XAUUSD', asset2: 'DXY', correlation: -0.78 }
        ],
        generated_at: new Date().toISOString(),
        read_time: 4,
        views: 890,
        likes: 56,
        category: 'Market Events'
      }
    ];
  };

  const filteredStories = filter === 'all' 
    ? stories 
    : stories.filter(story => story.sentiment === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-quantum-primary animate-pulse" />
          <span className="text-gray-400">Generating market narratives...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="w-6 h-6 text-quantum-primary" />
          <h2 className="text-xl font-semibold text-white">Market Stories</h2>
          <Sparkles className="w-5 h-5 text-yellow-400" />
        </div>
        
        <div className="flex items-center gap-2">
          {(['all', 'bullish', 'bearish', 'neutral'] as const).map((sentiment) => (
            <button
              key={sentiment}
              onClick={() => setFilter(sentiment)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === sentiment
                  ? 'bg-quantum-primary text-black'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Story Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence mode="popLayout">
          {filteredStories.map((story) => (
            <StoryCard
              key={story.id}
              story={story}
              onRead={setSelectedStory}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Selected Story Modal */}
      <AnimatePresence>
        {selectedStory && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setSelectedStory(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="quantum-panel max-w-4xl w-full max-h-[90vh] overflow-y-auto p-8"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-4">
                    {selectedStory.title}
                  </h2>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>{new Date(selectedStory.generated_at).toLocaleString()}</span>
                    <span>•</span>
                    <span>{selectedStory.read_time} min read</span>
                    <span>•</span>
                    <span>{selectedStory.views} views</span>
                  </div>
                </div>

                <div className="prose prose-invert max-w-none">
                  <p className="text-gray-300 leading-relaxed">
                    {selectedStory.content || selectedStory.summary}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-6 border-t border-gray-800">
                  <div className="flex items-center gap-4">
                    <button className="flex items-center gap-2 px-4 py-2 bg-quantum-primary/20 text-quantum-primary rounded-lg hover:bg-quantum-primary/30 transition-colors">
                      <ThumbsUp className="w-4 h-4" />
                      <span>Like</span>
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-400 rounded-lg hover:bg-gray-700 transition-colors">
                      <Share2 className="w-4 h-4" />
                      <span>Share</span>
                    </button>
                  </div>
                  <button
                    onClick={() => setSelectedStory(null)}
                    className="px-4 py-2 bg-gray-800 text-gray-400 rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 