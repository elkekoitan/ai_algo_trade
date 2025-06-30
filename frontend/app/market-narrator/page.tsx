'use client'
import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  MessageSquare, 
  BookOpen, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Brain,
  Network,
  Zap,
  Eye,
  Target,
  RefreshCw,
  Settings,
  Play,
  Pause,
  Heart,
  Share,
  Clock,
  BarChart3,
  Globe,
  Users,
  Cpu,
  Database,
  AlertCircle
} from 'lucide-react'
import QuantumLayout from '@/components/layout/QuantumLayout';
import { StoryFeed } from '@/components/market-narrator/StoryFeed';
import { StoryDetail } from '@/components/market-narrator/StoryDetail';
import { InfluenceMap } from '@/components/market-narrator/InfluenceMap';
import ParticleBackground from '@/components/quantum/ParticleBackground';
import GlassCard from '@/components/quantum/GlassCard';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { systemEvents } from '@/lib/system-events';
import { Button } from '@/components/ui/button';
import { MarketNarrative, MarketNarratorStatus } from '@/lib/types/market-narrator';

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
  const [narratives, setNarratives] = useState<MarketNarrative[]>([])
  const [selectedNarrative, setSelectedNarrative] = useState<MarketNarrative | null>(null)
  const [selectedSymbolForMap, setSelectedSymbolForMap] = useState<string | null>(null)
  const [status, setStatus] = useState<MarketNarratorStatus | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/market-narrator/status');
      if (response.ok) {
        setStatus(await response.json());
      }
    } catch (err) {
      console.error("Failed to fetch status", err);
    }
  }, []);

  const fetchNarratives = useCallback(async () => {
    setError(null);
    if (!isLoading) setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8002/api/v1/market-narrator/latest-narratives?limit=20');
      if (!response.ok) {
        throw new Error('Failed to fetch narratives.');
      }
      const data = await response.json();
      setNarratives(data);
      if (data.length > 0) {
        if (!selectedNarrative || !data.find((n: MarketNarrative) => n.narrative_id === selectedNarrative.narrative_id)) {
            setSelectedNarrative(data[0]);
            setSelectedSymbolForMap(data[0].protagonist_symbols[0]);
        }
      } else {
        setSelectedNarrative(null);
        setSelectedSymbolForMap(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedNarrative, isLoading]);
  
  const generateNarrative = async () => {
    setError(null);
    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:8002/api/v1/market-narrator/generate-narrative', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'EURUSD' })
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to generate new narrative.');
      }
      setTimeout(() => {
        fetchNarratives();
        fetchStatus();
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred during generation.');
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    fetchNarratorData();
    const interval = setInterval(fetchNarratorData, narratorState.is_active ? narratorState.story_frequency * 1000 : 30000);
    return () => clearInterval(interval);
  }, [narratorState.is_active, narratorState.story_frequency]);

  useEffect(() => {
    fetchStatus();
    fetchNarratives();
    const interval = setInterval(() => {
        fetchStatus();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

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

  const handleSelectNarrative = (narrative: MarketNarrative) => {
    setSelectedNarrative(narrative);
    if (narrative.protagonist_symbols.length > 0) {
      setSelectedSymbolForMap(narrative.protagonist_symbols[0]);
    }
  };

  const handleRefresh = () => {
      fetchStatus();
      fetchNarratives();
  }

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-indigo-900 to-slate-900 text-white p-6">
      <div className="max-w-8xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent mb-2">
              📖 Market Narrator
            </h1>
            <p className="text-gray-300">AI-Powered Market Storytelling & Influence Analysis</p>
          </div>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <Button onClick={generateNarrative} disabled={isGenerating} className="bg-indigo-600 hover:bg-indigo-700">
              <Zap className={`h-4 w-4 mr-2 ${isGenerating ? 'animate-spin' : ''}`} />
              {isGenerating ? 'Generating...' : 'Generate New Narrative'}
            </Button>
            <Button onClick={handleRefresh} variant="outline" className="border-indigo-400 text-indigo-400 hover:bg-indigo-500/10 hover:text-indigo-300">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Status Dashboard */}
        {status && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="bg-black/40 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Status</CardTitle>
                <Cpu className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-400">{status.status.toUpperCase()}</div>
                <p className="text-xs text-gray-500">
                    {status.last_story_generated_at ? `Last story at ${new Date(status.last_story_generated_at).toLocaleTimeString()}` : 'No stories yet'}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Stories (24h)</CardTitle>
                <BookOpen className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-indigo-400">{status.stories_generated_24h}</div>
                <p className="text-xs text-gray-500">narratives generated</p>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Data Sources</CardTitle>
                <Database className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-cyan-400">{status.data_sources_connected}</div>
                <p className="text-xs text-gray-500">active connections</p>
              </CardContent>
            </Card>
            <Card className="bg-black/40 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Error Rate</CardTitle>
                <AlertCircle className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-400">{(status.error_rate * 100).toFixed(1)}%</div>
                <p className="text-xs text-gray-500">system stability</p>
              </CardContent>
            </Card>
          </div>
        )}
        
        {error && <div className="bg-red-500/20 text-red-300 p-3 rounded-md mb-6 text-center">Error: {error}</div>}

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Story Feed */}
          <div className="lg:col-span-1">
            <Card className="bg-black/40 border-gray-700 h-[80vh]">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                      <BookOpen className="text-indigo-400"/>
                      Narrative Feed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                    <StoryFeed
                        narratives={narratives}
                        onSelectNarrative={handleSelectNarrative}
                        selectedNarrativeId={selectedNarrative?.narrative_id}
                        isLoading={isLoading}
                    />
                </CardContent>
            </Card>
          </div>

          {/* Column 2: Details & Map */}
          <div className="lg:col-span-2 space-y-6">
            <StoryDetail narrative={selectedNarrative} />
            <InfluenceMap symbol={selectedSymbolForMap} />
          </div>
        </div>
      </div>
    </div>
  )
} 