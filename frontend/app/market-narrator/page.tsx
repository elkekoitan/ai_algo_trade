'use client'
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import QuantumLayout from '@/components/layout/QuantumLayout';
import StoryFeed from '@/components/market-narrator/StoryFeed';
import InfluenceMap from '@/components/market-narrator/InfluenceMap';
import { BookText, GitCommit, Loader } from 'lucide-react';

// Mock Types
interface MarketStory {
    story_id: string;
    timestamp: string;
    title: string;
    narrative: string;
    protagonist_asset: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    key_takeaway: string;
    // For influence map
    correlations: Record<string, number>; 
}

export default function MarketNarratorPage() {
  const [stories, setStories] = useState<MarketStory[]>([]);
  const [selectedStory, setSelectedStory] = useState<MarketStory | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStories = async () => {
      setIsLoading(true);
      try {
        // Mocking correlations for now
        const mockCorrelations = {
            "DXY": { "XAUUSD": -0.85, "EURUSD": -0.92 },
            "EURUSD": { "DXY": -0.92 },
            "BTCUSD": { "ETHUSD": 0.88 }
        };

        const response = await fetch('/api/v1/narrator/feed');
        if (!response.ok) throw new Error('Failed to fetch stories');
        
        let fetchedStories = await response.json();
        
        // Add mock correlations to the fetched stories
        fetchedStories = fetchedStories.map(story => ({
            ...story,
            correlations: mockCorrelations[story.protagonist_asset] || {}
        }));

        setStories(fetchedStories);
        if (fetchedStories.length > 0) {
            setSelectedStory(fetchedStories[0]);
        }
      } catch (error) {
        console.error("Error fetching market stories:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStories();
  }, []);

  const handleStorySelect = (storyId: string) => {
    const story = stories.find(s => s.story_id === storyId);
    if (story) {
        setSelectedStory(story);
    }
  };

  return (
    <QuantumLayout>
      <div className="p-6">
        {/* Header */}
        <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 
                       bg-clip-text text-transparent flex items-center gap-3">
            <BookText className="w-10 h-10 text-cyan-400" />
            Market Narrator
          </h1>
          <p className="text-gray-400 mt-2">
            The story behind the numbers, powered by AI.
          </p>
        </motion.div>

        {isLoading ? (
            <div className="flex items-center justify-center h-96">
                <Loader className="w-16 h-16 text-cyan-400 animate-spin" />
            </div>
        ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column: Story Feed */}
                <div className="lg:col-span-1">
                    <StoryFeed stories={stories} onStorySelect={handleStorySelect} />
                </div>
                
                {/* Right Column: Visualization */}
                <div className="lg:col-span-1 sticky top-24 h-fit">
                    {selectedStory ? (
                        <InfluenceMap 
                            key={selectedStory.story_id} // Re-mount when story changes
                            protagonist={selectedStory.protagonist_asset} 
                            correlations={selectedStory.correlations}
                        />
                    ) : (
                        <div className="flex flex-col items-center justify-center h-96 bg-gray-900/50 rounded-2xl border border-dashed border-gray-700">
                            <GitCommit className="w-16 h-16 text-gray-600 mb-4" />
                            <h3 className="text-2xl font-semibold text-gray-400">Select a Story</h3>
                            <p className="text-gray-500">Choose a narrative from the feed to see its influence map.</p>
                        </div>
                    )}
                </div>
            </div>
        )}
      </div>
    </QuantumLayout>
  );
} 