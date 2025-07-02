"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SocialFeed from '@/components/social-trading/SocialFeed';
import { 
  Users, TrendingUp, Trophy, MessageSquare, 
  Plus, Search, Filter, Globe
} from 'lucide-react';

export default function SocialTradingPage() {
  const [activeTab, setActiveTab] = useState('feed');
  const userId = 'user_001'; // This would come from auth context

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent">
                Social Trading
              </h1>
              <p className="text-gray-600 text-lg">
                Connect, learn, and trade with the community
              </p>
            </div>
            
            <div className="flex space-x-3">
              <Button className="flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Create Post</span>
              </Button>
              <Button variant="outline" className="flex items-center space-x-2">
                <Search className="w-4 h-4" />
                <span>Find Traders</span>
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm">Following</p>
                    <p className="text-2xl font-bold">127</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm">Followers</p>
                    <p className="text-2xl font-bold">1,892</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-200" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-yellow-100 text-sm">Rank</p>
                    <p className="text-2xl font-bold">#47</p>
                  </div>
                  <Trophy className="w-8 h-8 text-yellow-200" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm">Posts</p>
                    <p className="text-2xl font-bold">89</p>
                  </div>
                  <MessageSquare className="w-8 h-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="feed">Feed</TabsTrigger>
            <TabsTrigger value="signals">Signals</TabsTrigger>
            <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
            <TabsTrigger value="communities">Communities</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
          </TabsList>

          <TabsContent value="feed" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Main Feed */}
              <div className="lg:col-span-3">
                <SocialFeed userId={userId} />
              </div>
              
              {/* Sidebar */}
              <div className="space-y-6">
                {/* Trending Topics */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Trending Topics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      { topic: '#bitcoin', posts: 156, trend: '+12%' },
                      { topic: '#forex', posts: 89, trend: '+8%' },
                      { topic: '#ethereum', posts: 67, trend: '+15%' },
                      { topic: '#gold', posts: 45, trend: '-3%' },
                      { topic: '#sp500', posts: 34, trend: '+5%' }
                    ].map((item) => (
                      <div key={item.topic} className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-blue-600">{item.topic}</p>
                          <p className="text-sm text-gray-500">{item.posts} posts</p>
                        </div>
                        <span className={`text-sm font-semibold ${
                          item.trend.startsWith('+') ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {item.trend}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Top Traders */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Top Traders</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      { name: 'Crypto King 👑', return: '+145.8%', followers: '1.2K' },
                      { name: 'Forex Ninja 🥷', return: '+89.2%', followers: '890' },
                      { name: 'Swing Master 📈', return: '+67.3%', followers: '567' }
                    ].map((trader, index) => (
                      <div key={trader.name} className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold text-sm">{trader.name}</p>
                          <p className="text-xs text-gray-500">{trader.followers} followers</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-green-500">{trader.return}</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Market Sentiment */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Market Sentiment</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Bullish</span>
                          <span>65%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Bearish</span>
                          <span>35%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-red-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="signals">
            <Card>
              <CardHeader>
                <CardTitle>Trading Signals</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">Trading signals will be displayed here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leaderboard">
            <Card>
              <CardHeader>
                <CardTitle>Leaderboard</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">Leaderboard will be displayed here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="communities">
            <Card>
              <CardHeader>
                <CardTitle>Communities</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">Communities will be displayed here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Your Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">Profile settings will be displayed here.</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 