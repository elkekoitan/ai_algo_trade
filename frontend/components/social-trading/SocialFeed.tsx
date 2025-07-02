"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Heart, MessageCircle, Share2, TrendingUp, TrendingDown, Target, Award } from 'lucide-react';

interface SocialPost {
  post_id: string;
  user_id: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  post_type: string;
  title?: string;
  content: string;
  symbols_mentioned: string[];
  signal?: any;
  likes_count: number;
  comments_count: number;
  views_count: number;
  tags: string[];
  created_at: string;
}

interface SocialFeedProps {
  userId: string;
}

export default function SocialFeed({ userId }: SocialFeedProps) {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchSocialFeed();
  }, [userId, filter]);

  const fetchSocialFeed = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/social/feed/${userId}?limit=20${filter !== 'all' ? `&post_type=${filter}` : ''}`);
      const data = await response.json();
      setPosts(data.posts || []);
    } catch (error) {
      console.error('Failed to fetch social feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId: string) => {
    try {
      await fetch(`/api/v1/social/posts/${postId}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      
      // Update local state
      setPosts(posts.map(post => 
        post.post_id === postId 
          ? { ...post, likes_count: post.likes_count + 1 }
          : post
      ));
    } catch (error) {
      console.error('Failed to like post:', error);
    }
  };

  const getPostTypeIcon = (type: string) => {
    switch (type) {
      case 'signal':
        return <Target className="w-4 h-4 text-blue-500" />;
      case 'analysis':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'celebration':
        return <Award className="w-4 h-4 text-yellow-500" />;
      default:
        return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-300 rounded w-24"></div>
                  <div className="h-3 bg-gray-300 rounded w-16"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-300 rounded"></div>
                <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex space-x-2 overflow-x-auto pb-2">
        {[
          { key: 'all', label: 'All Posts', icon: '📰' },
          { key: 'signal', label: 'Signals', icon: '🎯' },
          { key: 'analysis', label: 'Analysis', icon: '📊' },
          { key: 'education', label: 'Education', icon: '📚' },
          { key: 'celebration', label: 'Wins', icon: '🎉' }
        ].map((tab) => (
          <Button
            key={tab.key}
            variant={filter === tab.key ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(tab.key)}
            className="flex items-center space-x-2 whitespace-nowrap"
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </Button>
        ))}
      </div>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.map((post) => (
          <Card key={post.post_id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              {/* Post Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Avatar className="w-10 h-10">
                    <AvatarImage src={post.avatar_url} />
                    <AvatarFallback>{post.display_name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="font-semibold text-sm">{post.display_name}</h4>
                      <Badge variant="secondary" className="text-xs">
                        @{post.username}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      {getPostTypeIcon(post.post_type)}
                      <span>{formatTimeAgo(post.created_at)}</span>
                    </div>
                  </div>
                </div>
                
                {post.post_type === 'signal' && (
                  <Badge className="bg-blue-500 text-white">
                    Signal
                  </Badge>
                )}
              </div>

              {/* Post Title */}
              {post.title && (
                <h3 className="font-bold text-lg mb-2">{post.title}</h3>
              )}

              {/* Post Content */}
              <div className="mb-4">
                <p className="text-gray-700 leading-relaxed">{post.content}</p>
              </div>

              {/* Symbols Mentioned */}
              {post.symbols_mentioned.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {post.symbols_mentioned.map((symbol) => (
                    <Badge key={symbol} variant="outline" className="text-blue-600 border-blue-200">
                      ${symbol}
                    </Badge>
                  ))}
                </div>
              )}

              {/* Signal Details */}
              {post.signal && (
                <div className="bg-blue-50 rounded-lg p-4 mb-4 border border-blue-200">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Type:</span>
                      <div className="font-semibold flex items-center">
                        {post.signal.type === 'buy' ? (
                          <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
                        )}
                        {post.signal.type.toUpperCase()}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Entry:</span>
                      <div className="font-semibold">{post.signal.entry_price}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Stop Loss:</span>
                      <div className="font-semibold">{post.signal.stop_loss}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Take Profit:</span>
                      <div className="font-semibold">{post.signal.take_profit}</div>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span className="text-gray-600">Confidence:</span>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${post.signal.confidence}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold">{post.signal.confidence}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Tags */}
              {post.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {post.tags.map((tag) => (
                    <span key={tag} className="text-blue-500 text-sm hover:underline cursor-pointer">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Post Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center space-x-6">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleLike(post.post_id)}
                    className="flex items-center space-x-2 text-gray-600 hover:text-red-500"
                  >
                    <Heart className="w-4 h-4" />
                    <span>{post.likes_count}</span>
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex items-center space-x-2 text-gray-600 hover:text-blue-500"
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>{post.comments_count}</span>
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex items-center space-x-2 text-gray-600 hover:text-green-500"
                  >
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </Button>
                </div>
                
                <div className="text-xs text-gray-500">
                  {post.views_count} views
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Load More */}
      {posts.length > 0 && (
        <div className="text-center">
          <Button variant="outline" onClick={fetchSocialFeed}>
            Load More Posts
          </Button>
        </div>
      )}

      {/* Empty State */}
      {!loading && posts.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">No Posts Yet</h3>
            <p className="text-gray-500 mb-4">
              Follow some traders to see their posts in your feed!
            </p>
            <Button>Discover Traders</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 