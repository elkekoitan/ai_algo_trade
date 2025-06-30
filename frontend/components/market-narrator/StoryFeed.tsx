'use client'
import React from 'react'
import { motion } from 'framer-motion'
import { BookOpen, TrendingUp, TrendingDown, Clock, Feather } from 'lucide-react'

// Mock Type
interface MarketStory {
    story_id: string;
    timestamp: string;
    title: string;
    narrative: string;
    protagonist_asset: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    key_takeaway: string;
}

interface StoryFeedProps {
    stories: MarketStory[];
    onStorySelect: (storyId: string) => void;
}

const StoryCard = ({ story, onSelect }: { story: MarketStory, onSelect: (id: string) => void }) => {
    const sentimentColor = story.sentiment === 'positive' ? 'border-green-500/50' :
                           story.sentiment === 'negative' ? 'border-red-500/50' :
                           'border-gray-500/50';
    const SentimentIcon = story.sentiment === 'positive' ? TrendingUp : TrendingDown;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            whileHover={{ y: -5, boxShadow: '0 10px 20px rgba(0, 255, 255, 0.1)' }}
            onClick={() => onSelect(story.story_id)}
            className={`bg-gray-900/50 rounded-2xl p-6 border ${sentimentColor}
                        backdrop-blur-lg cursor-pointer overflow-hidden`}
        >
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 flex items-center justify-center rounded-full bg-gray-800`}>
                        <Feather className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white">{story.title}</h3>
                        <p className="text-sm text-gray-400">
                            Focus: <span className="font-semibold text-cyan-400">{story.protagonist_asset}</span>
                        </p>
                    </div>
                </div>
                <div className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gray-800`}>
                    <SentimentIcon className={`w-4 h-4 ${story.sentiment === 'positive' ? 'text-green-400' : 'text-red-400'}`} />
                    <span className="text-gray-300">{story.sentiment.toUpperCase()}</span>
                </div>
            </div>

            <p className="text-gray-300 text-sm mb-4 leading-relaxed">
                {story.narrative.substring(0, 150)}...
            </p>
            
            <div className="bg-cyan-900/50 border-t border-cyan-500/20 p-3 -m-6 mt-4">
                 <p className="text-sm text-cyan-300 font-semibold">
                    Key Takeaway: <span className="font-normal text-gray-200">{story.key_takeaway}</span>
                </p>
            </div>

             <div className="absolute bottom-2 right-4 text-xs text-gray-600 flex items-center gap-1">
                <Clock className="w-3 h-3"/>
                <span>{new Date(story.timestamp).toLocaleTimeString()}</span>
            </div>
        </motion.div>
    )
}

export default function StoryFeed({ stories, onStorySelect }: StoryFeedProps) {
  if (stories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 bg-gray-900/50 rounded-2xl border border-dashed border-gray-700">
        <BookOpen className="w-16 h-16 text-gray-600 mb-4" />
        <h3 className="text-2xl font-semibold text-gray-400">No Market Stories Available</h3>
        <p className="text-gray-500">The AI Narrator is analyzing the markets. Stories will appear here shortly.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
        {stories.map(story => (
            <StoryCard key={story.story_id} story={story} onSelect={onStorySelect} />
        ))}
    </div>
  )
} 