'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BookOpen, 
  TrendingUp, 
  Users, 
  Zap,
  Search,
  Filter,
  RefreshCw,
  BarChart3,
  Globe,
  Newspaper,
  AlertCircle,
  MessageSquare,
  Settings,
  Play,
  Pause,
  Eye,
  Clock,
  Network
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import QuantumLayout from '@/components/layout/QuantumLayout'
import ParticleBackground from '@/components/quantum/ParticleBackground'
import GlassCard from '@/components/quantum/GlassCard'

// Market Narrator components
import StoryFeed from '@/components/market-narrator/StoryFeed'
import InfluenceMap from '@/components/market-narrator/InfluenceMap'
import StoryDetail from '@/components/market-narrator/StoryDetail'
import { systemEvents } from '@/lib/system-events'

interface MarketStory {
  id: string;
  title: string;
  content: string;
  summary: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  impact_score: number;
  affected_symbols: string[];
  story_type: 'BREAKING' | 'ANALYSIS' | 'PREDICTION' | 'ALERT';
  sources: string[];
  correlations: Array<{
    symbol: string;
    correlation: number;
    impact: string;
  }>;
  timestamp: string;
  author: 'AI_NARRATOR' | 'QUANTUM_ENGINE' | 'SENTIMENT_ANALYZER';
  engagement: {
    views: number;
    relevance: number;
    accuracy_rating: number;
  };
}

interface InfluenceNode {
  id: string;
  name: string;
  type: 'SYMBOL' | 'EVENT' | 'INDICATOR' | 'NEWS';
  influence: number;
  connections: string[];
  position: { x: number; y: number };
}

interface SentimentData {
  overall_sentiment: number; // -100 to 100
  bullish_signals: number;
  bearish_signals: number;
  neutral_signals: number;
  market_fear_greed: number;
  social_sentiment: number;
  institutional_sentiment: number;
  retail_sentiment: number;
}

interface NarratorState {
  is_active: boolean;
  auto_generation: boolean;
  story_frequency: number;
  sentiment_tracking: boolean;
  influence_analysis: boolean;
  cross_correlation: boolean;
  story_types: string[];
}

export default function MarketNarratorPage() {
  const [stories, setStories] = useState<MarketStory[]>([])
  const [influenceNodes, setInfluenceNodes] = useState<InfluenceNode[]>([])
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null)
  const [narratorState, setNarratorState] = useState<NarratorState>({
    is_active: false,
    auto_generation: true,
    story_frequency: 300, // 5 minutes
    sentiment_tracking: true,
    influence_analysis: true,
    cross_correlation: true,
    story_types: ['BREAKING', 'ANALYSIS', 'PREDICTION']
  })
  const [selectedStory, setSelectedStory] = useState<MarketStory | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const fetchNarratorData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/market-narrator/stories');
      
      if (response.ok) {
        const data = await response.json();
        
        // Transform stories
        const marketStories: MarketStory[] = data.stories?.map((story: any, index: number) => ({
          id: `story_${Date.now()}_${index}`,
          title: story.title || generateStoryTitle(),
          content: story.content || generateStoryContent(),
          summary: story.summary || generateStorySummary(),
          sentiment: story.sentiment || ['BULLISH', 'BEARISH', 'NEUTRAL'][Math.floor(Math.random() * 3)],
          confidence: story.confidence || (70 + Math.random() * 25),
          impact_score: story.impact_score || (60 + Math.random() * 40),
          affected_symbols: story.affected_symbols || ['EURUSD', 'XAUUSD', 'BTCUSD'].slice(0, 1 + Math.floor(Math.random() * 2)),
          story_type: story.story_type || narratorState.story_types[Math.floor(Math.random() * narratorState.story_types.length)],
          sources: story.sources || ['Technical Analysis', 'Sentiment Data', 'Institutional Flow'],
          correlations: story.correlations || generateCorrelations(),
          timestamp: story.timestamp || new Date().toISOString(),
          author: story.author || 'AI_NARRATOR',
          engagement: {
            views: Math.floor(Math.random() * 1000),
            relevance: 75 + Math.random() * 25,
            accuracy_rating: 80 + Math.random() * 20
          }
        })) || [];
        
        setStories(marketStories);
        
        // Generate influence nodes
        const nodes: InfluenceNode[] = [
          { id: 'EURUSD', name: 'EUR/USD', type: 'SYMBOL', influence: 85, connections: ['DXY', 'ECB'], position: { x: 100, y: 100 } },
          { id: 'XAUUSD', name: 'Gold', type: 'SYMBOL', influence: 78, connections: ['DXY', 'INFLATION'], position: { x: 200, y: 150 } },
          { id: 'DXY', name: 'Dollar Index', type: 'INDICATOR', influence: 92, connections: ['EURUSD', 'XAUUSD'], position: { x: 150, y: 50 } },
          { id: 'ECB', name: 'ECB Policy', type: 'EVENT', influence: 70, connections: ['EURUSD'], position: { x: 50, y: 200 } },
          { id: 'INFLATION', name: 'Inflation Data', type: 'NEWS', influence: 65, connections: ['XAUUSD', 'DXY'], position: { x: 250, y: 100 } }
        ];
        
        setInfluenceNodes(nodes);
        
        // Update sentiment data
        setSentimentData({
          overall_sentiment: -20 + Math.random() * 40,
          bullish_signals: 35 + Math.random() * 30,
          bearish_signals: 25 + Math.random() * 30,
          neutral_signals: 40 + Math.random() * 20,
          market_fear_greed: 45 + Math.random() * 30,
          social_sentiment: -10 + Math.random() * 20,
          institutional_sentiment: 10 + Math.random() * 30,
          retail_sentiment: -15 + Math.random() * 25
        });
        
        // Broadcast stories to other modules
        if (marketStories.length > 0) {
          const topStory = marketStories[0];
          await systemEvents.syncModuleData('market_narrator', 'narrator_story', {
            story: topStory,
            sentiment: topStory.sentiment,
            impact: topStory.impact_score,
            affected_symbols: topStory.affected_symbols
          });
        }
        
      } else {
        // Generate mock stories
        const mockStories: MarketStory[] = Array.from({ length: 5 }, (_, index) => ({
          id: `mock_${Date.now()}_${index}`,
          title: generateStoryTitle(),
          content: generateStoryContent(),
          summary: generateStorySummary(),
          sentiment: ['BULLISH', 'BEARISH', 'NEUTRAL'][Math.floor(Math.random() * 3)] as any,
          confidence: 70 + Math.random() * 25,
          impact_score: 60 + Math.random() * 40,
          affected_symbols: ['EURUSD', 'XAUUSD', 'BTCUSD'].slice(0, 1 + Math.floor(Math.random() * 2)),
          story_type: narratorState.story_types[Math.floor(Math.random() * narratorState.story_types.length)] as any,
          sources: ['Technical Analysis', 'Sentiment Data', 'Institutional Flow'],
          correlations: generateCorrelations(),
          timestamp: new Date(Date.now() - index * 300000).toISOString(),
          author: 'AI_NARRATOR',
          engagement: {
            views: Math.floor(Math.random() * 1000),
            relevance: 75 + Math.random() * 25,
            accuracy_rating: 80 + Math.random() * 20
          }
        }));
        
        setStories(mockStories);
        
        // Mock sentiment data
        setSentimentData({
          overall_sentiment: 15.5,
          bullish_signals: 45,
          bearish_signals: 30,
          neutral_signals: 25,
          market_fear_greed: 62,
          social_sentiment: 8.5,
          institutional_sentiment: 22.3,
          retail_sentiment: -5.2
        });
      }
      
      setLastUpdate(new Date());
      
    } catch (error) {
      console.error('Error fetching narrator data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateStoryTitle = () => {
    const titles = [
      "EUR/USD Breaks Key Resistance as ECB Signals Shift",
      "Gold Surges on Inflation Concerns and Dollar Weakness",
      "Bitcoin Shows Institutional Accumulation Patterns",
      "DXY Tests Critical Support Amid Fed Policy Uncertainty",
      "GBP/USD Rallies on Positive Economic Data",
      "Oil Prices Spike on Supply Chain Disruptions",
      "Tech Stocks Lead Market Recovery Session"
    ];
    return titles[Math.floor(Math.random() * titles.length)];
  };

  const generateStoryContent = () => {
    const contents = [
      "Market analysis reveals significant institutional buying pressure in major currency pairs. Technical indicators suggest a potential breakout scenario developing across multiple timeframes. Volume analysis confirms strong participation from smart money.",
      "Recent economic data releases have shifted market sentiment dramatically. Central bank policy expectations are being repriced as inflation data continues to surprise markets. Cross-asset correlations are strengthening.",
      "Algorithmic trading patterns indicate a regime change in market microstructure. High-frequency trading flows show increased directional bias. Options flow suggests large institutional positioning for upcoming volatility.",
      "Geopolitical developments are creating new risk-on/risk-off dynamics. Safe haven assets are experiencing unusual flow patterns. Currency carry trades are being unwound systematically."
    ];
    return contents[Math.floor(Math.random() * contents.length)];
  };

  const generateStorySummary = () => {
    const summaries = [
      "Strong bullish momentum driven by institutional flows and technical breakouts.",
      "Market sentiment shifts as economic data surprises and central bank policy evolves.",
      "Algorithmic patterns suggest regime change with increased volatility ahead.",
      "Geopolitical factors drive safe haven flows and currency repositioning."
    ];
    return summaries[Math.floor(Math.random() * summaries.length)];
  };

  const generateCorrelations = () => {
    const symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD', 'US30'];
    return symbols.slice(0, 2 + Math.floor(Math.random() * 3)).map(symbol => ({
      symbol,
      correlation: -0.5 + Math.random(),
      impact: ['Strong', 'Moderate', 'Weak'][Math.floor(Math.random() * 3)]
    }));
  };

  const toggleNarrator = async () => {
    try {
      const newState = { ...narratorState, is_active: !narratorState.is_active };
      setNarratorState(newState);
      
      await systemEvents.broadcastEvent('narrator:mode_toggled', {
        active: newState.is_active,
        auto_generation: newState.auto_generation
      });
      
    } catch (error) {
      console.error('Failed to toggle narrator:', error);
    }
  };

  const updateSettings = async (newSettings: Partial<NarratorState>) => {
    const updatedState = { ...narratorState, ...newSettings };
    setNarratorState(updatedState);
    
    await systemEvents.broadcastEvent('narrator:settings_updated', updatedState);
  };

  const generateNewStory = async () => {
    try {
      const response = await fetch('/api/v1/market-narrator/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          type: 'BREAKING',
          symbols: ['EURUSD', 'XAUUSD'],
          sentiment_analysis: narratorState.sentiment_tracking
        })
      });
      
      if (response.ok) {
        await fetchNarratorData();
      }
    } catch (error) {
      console.error('Failed to generate story:', error);
    }
  };

  useEffect(() => {
    fetchNarratorData();
    const interval = setInterval(fetchNarratorData, narratorState.is_active ? narratorState.story_frequency * 1000 : 30000);
    return () => clearInterval(interval);
  }, [narratorState.is_active, narratorState.story_frequency]);

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'BULLISH': return 'text-green-400 bg-green-500/20';
      case 'BEARISH': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getStoryTypeColor = (type: string) => {
    switch (type) {
      case 'BREAKING': return 'text-red-400 bg-red-500/20';
      case 'ANALYSIS': return 'text-blue-400 bg-blue-500/20';
      case 'PREDICTION': return 'text-purple-400 bg-purple-500/20';
      case 'ALERT': return 'text-yellow-400 bg-yellow-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <MessageSquare className="w-12 h-12 animate-pulse text-yellow-400 mx-auto mb-4" />
          <p className="text-xl">Initializing Market Narrator...</p>
          <p className="text-gray-400">AI analyzing market stories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <ParticleBackground />
      
      <div className="relative z-10 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-yellow-400" />
            Market Narrator
            {narratorState.is_active && <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse" />}
          </h1>
          
          <div className="flex items-center gap-4">
            <Badge className={`${getSentimentColor(sentimentData && sentimentData.overall_sentiment > 10 ? 'BULLISH' : sentimentData && sentimentData.overall_sentiment < -10 ? 'BEARISH' : 'NEUTRAL')}`}>
              Sentiment: {sentimentData?.overall_sentiment.toFixed(1) || '0.0'}
            </Badge>
            <button
              onClick={toggleNarrator}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                narratorState.is_active 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              {narratorState.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {narratorState.is_active ? 'Narrator ON' : 'Activate Narrator'}
            </button>
          </div>
        </div>

        {/* Sentiment Dashboard */}
        {sentimentData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <GlassCard className="p-4">
              <div className="text-center">
                <p className="text-sm text-gray-400">Market Fear/Greed</p>
                <p className="text-2xl font-bold text-purple-400">{sentimentData.market_fear_greed.toFixed(0)}</p>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                  <div className="bg-purple-400 h-2 rounded-full" style={{ width: `${sentimentData.market_fear_greed}%` }}></div>
                </div>
              </div>
            </GlassCard>
            
            <GlassCard className="p-4">
              <div className="text-center">
                <p className="text-sm text-gray-400">Bullish Signals</p>
                <p className="text-2xl font-bold text-green-400">{sentimentData.bullish_signals.toFixed(0)}%</p>
              </div>
            </GlassCard>
            
            <GlassCard className="p-4">
              <div className="text-center">
                <p className="text-sm text-gray-400">Bearish Signals</p>
                <p className="text-2xl font-bold text-red-400">{sentimentData.bearish_signals.toFixed(0)}%</p>
              </div>
            </GlassCard>
            
            <GlassCard className="p-4">
              <div className="text-center">
                <p className="text-sm text-gray-400">Institutional</p>
                <p className={`text-2xl font-bold ${sentimentData.institutional_sentiment >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {sentimentData.institutional_sentiment >= 0 ? '+' : ''}{sentimentData.institutional_sentiment.toFixed(1)}
                </p>
              </div>
            </GlassCard>
          </div>
        )}

        {/* Control Panel */}
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Settings className="h-6 w-6 text-yellow-400" />
            Narrator Control Panel
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Story Generation Frequency (seconds)
              </label>
              <select
                value={narratorState.story_frequency}
                onChange={(e) => updateSettings({ story_frequency: parseInt(e.target.value) })}
                className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-2"
              >
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
                <option value={600}>10 minutes</option>
                <option value={1800}>30 minutes</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Story Types
              </label>
              <div className="space-y-2">
                {['BREAKING', 'ANALYSIS', 'PREDICTION', 'ALERT'].map(type => (
                  <label key={type} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={narratorState.story_types.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          updateSettings({ story_types: [...narratorState.story_types, type] });
                        } else {
                          updateSettings({ story_types: narratorState.story_types.filter(t => t !== type) });
                        }
                      }}
                      className="rounded"
                    />
                    <span className="text-sm text-white">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={narratorState.auto_generation}
                  onChange={(e) => updateSettings({ auto_generation: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm text-white">Auto Generation</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={narratorState.sentiment_tracking}
                  onChange={(e) => updateSettings({ sentiment_tracking: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm text-white">Sentiment Tracking</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={narratorState.influence_analysis}
                  onChange={(e) => updateSettings({ influence_analysis: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm text-white">Influence Analysis</span>
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={generateNewStory}
                className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg"
              >
                Generate New Story
              </button>
            </div>
          </div>
        </GlassCard>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Story Feed */}
          <div className="lg:col-span-2">
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-cyan-400" />
                Live Story Feed ({stories.length})
              </h2>
              
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {stories.map((story) => (
                  <motion.div
                    key={story.id}
                    className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-yellow-500/50 cursor-pointer transition-all"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    onClick={() => setSelectedStory(story)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getStoryTypeColor(story.story_type)}>
                          {story.story_type}
                        </Badge>
                        <Badge className={getSentimentColor(story.sentiment)}>
                          {story.sentiment}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-yellow-400">{story.confidence.toFixed(0)}%</p>
                        <p className="text-xs text-gray-400">Impact: {story.impact_score.toFixed(0)}</p>
                      </div>
                    </div>
                    
                    <h3 className="font-bold text-white mb-2">{story.title}</h3>
                    <p className="text-sm text-gray-300 mb-3">{story.summary}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        {story.affected_symbols.map(symbol => (
                          <Badge key={symbol} variant="outline" className="text-xs">
                            {symbol}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <div className="flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          <span>{story.engagement.views}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(story.timestamp).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {stories.length === 0 && (
                  <div className="text-center py-8">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                    <p className="text-gray-400">No stories generated yet</p>
                    <p className="text-sm text-gray-500">AI narrator analyzing market patterns...</p>
                  </div>
                )}
              </div>
            </GlassCard>
          </div>

          {/* Influence Map */}
          <div>
            <GlassCard className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Network className="h-6 w-6 text-purple-400" />
                Market Influence Map
              </h2>
              
              <div className="h-64 bg-gray-900/50 rounded-lg relative overflow-hidden">
                {influenceNodes.map((node) => (
                  <div
                    key={node.id}
                    className={`absolute w-12 h-12 rounded-full flex items-center justify-center text-xs font-bold cursor-pointer transition-all hover:scale-110 ${
                      node.type === 'SYMBOL' ? 'bg-cyan-500/30 text-cyan-400 border-2 border-cyan-500' :
                      node.type === 'EVENT' ? 'bg-yellow-500/30 text-yellow-400 border-2 border-yellow-500' :
                      node.type === 'INDICATOR' ? 'bg-purple-500/30 text-purple-400 border-2 border-purple-500' :
                      'bg-green-500/30 text-green-400 border-2 border-green-500'
                    }`}
                    style={{
                      left: `${(node.position.x / 300) * 100}%`,
                      top: `${(node.position.y / 250) * 100}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                    title={`${node.name} - Influence: ${node.influence}%`}
                  >
                    {node.name.slice(0, 3)}
                  </div>
                ))}
                
                {/* Connection lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {influenceNodes.map((node) =>
                    node.connections.map((connId) => {
                      const connNode = influenceNodes.find(n => n.id === connId);
                      if (!connNode) return null;
                      return (
                        <line
                          key={`${node.id}-${connId}`}
                          x1={`${(node.position.x / 300) * 100}%`}
                          y1={`${(node.position.y / 250) * 100}%`}
                          x2={`