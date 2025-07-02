"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import AIMentorChat from '@/components/ai-mentor/AIMentorChat';
import { 
  Brain, Target, TrendingUp, BookOpen, Heart, 
  Award, Clock, Zap, BarChart3, Users
} from 'lucide-react';

interface UserAnalytics {
  learning_progress: {
    concepts_mastered: number;
    weak_areas: number;
    current_level: string;
  };
  session_stats: {
    total_sessions: number;
    total_time: number;
    current_session_active: boolean;
  };
  psychological_metrics: {
    confidence_level: number;
    discipline_score: number;
    emotional_state: string;
    risk_tolerance: number;
  };
}

export default function AIMentorPage() {
  const [activeTab, setActiveTab] = useState('chat');
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const userId = 'user_001'; // This would come from auth context

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/ai-mentor/analytics/${userId}`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEmotionalStateColor = (state: string) => {
    switch (state) {
      case 'confident':
        return 'text-green-500';
      case 'stressed':
        return 'text-red-500';
      case 'excited':
        return 'text-blue-500';
      case 'cautious':
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  const getEmotionalStateIcon = (state: string) => {
    switch (state) {
      case 'confident':
        return '😎';
      case 'stressed':
        return '😰';
      case 'excited':
        return '🤩';
      case 'cautious':
        return '🤔';
      default:
        return '😐';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                AI Trading Mentor
              </h1>
              <p className="text-gray-600 text-lg">
                Your personal AI coach for trading success
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className="text-3xl">🧠</div>
                <p className="text-sm text-gray-600">AI Mentor</p>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100 text-sm">Sessions</p>
                      <p className="text-2xl font-bold">{analytics.session_stats.total_sessions}</p>
                    </div>
                    <Clock className="w-8 h-8 text-purple-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-indigo-100 text-sm">Concepts Learned</p>
                      <p className="text-2xl font-bold">{analytics.learning_progress.concepts_mastered}</p>
                    </div>
                    <BookOpen className="w-8 h-8 text-indigo-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100 text-sm">Confidence</p>
                      <p className="text-2xl font-bold">{Math.round(analytics.psychological_metrics.confidence_level * 100)}%</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-green-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-sm">Discipline</p>
                      <p className="text-2xl font-bold">{Math.round(analytics.psychological_metrics.discipline_score * 100)}%</p>
                    </div>
                    <Target className="w-8 h-8 text-blue-200" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="chat">AI Chat</TabsTrigger>
            <TabsTrigger value="progress">Progress</TabsTrigger>
            <TabsTrigger value="psychology">Psychology</TabsTrigger>
            <TabsTrigger value="learning">Learning Path</TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Main Chat */}
              <div className="lg:col-span-3">
                <AIMentorChat userId={userId} />
              </div>
              
              {/* Sidebar */}
              <div className="space-y-6">
                {/* Current Emotional State */}
                {analytics && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Emotional State</CardTitle>
                    </CardHeader>
                    <CardContent className="text-center">
                      <div className="text-4xl mb-2">
                        {getEmotionalStateIcon(analytics.psychological_metrics.emotional_state)}
                      </div>
                      <p className={`font-semibold capitalize ${getEmotionalStateColor(analytics.psychological_metrics.emotional_state)}`}>
                        {analytics.psychological_metrics.emotional_state}
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Your AI mentor adapts to your emotional state
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Quick Help</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {[
                      { label: '💡 Trading Tip', action: 'Give me a trading tip' },
                      { label: '📊 Trade Analysis', action: 'Analyze my last trade' },
                      { label: '🎯 Position Sizing', action: 'Help with position sizing' },
                      { label: '😌 Emotional Support', action: 'I need emotional support' }
                    ].map((item) => (
                      <Button
                        key={item.action}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start text-left"
                      >
                        {item.label}
                      </Button>
                    ))}
                  </CardContent>
                </Card>

                {/* Recent Achievements */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Recent Achievements</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      { title: 'Risk Management Master', desc: 'Completed risk management course', icon: '🛡️' },
                      { title: 'Emotional Control', desc: '7 days of disciplined trading', icon: '🧘' },
                      { title: 'Strategy Builder', desc: 'Created first trading strategy', icon: '⚡' }
                    ].map((achievement) => (
                      <div key={achievement.title} className="flex items-center space-x-3">
                        <div className="text-2xl">{achievement.icon}</div>
                        <div>
                          <p className="font-semibold text-sm">{achievement.title}</p>
                          <p className="text-xs text-gray-500">{achievement.desc}</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="progress">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Learning Progress */}
              <Card>
                <CardHeader>
                  <CardTitle>Learning Progress</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {analytics && (
                    <>
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Overall Progress</span>
                          <span>{Math.round((analytics.learning_progress.concepts_mastered / 20) * 100)}%</span>
                        </div>
                        <Progress value={(analytics.learning_progress.concepts_mastered / 20) * 100} className="h-2" />
                      </div>
                      
                      <div className="space-y-4">
                        {[
                          { name: 'Risk Management', progress: 85, color: 'bg-green-500' },
                          { name: 'Technical Analysis', progress: 70, color: 'bg-blue-500' },
                          { name: 'Psychology', progress: 60, color: 'bg-purple-500' },
                          { name: 'Strategy Development', progress: 40, color: 'bg-yellow-500' }
                        ].map((skill) => (
                          <div key={skill.name}>
                            <div className="flex justify-between text-sm mb-1">
                              <span>{skill.name}</span>
                              <span>{skill.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`${skill.color} h-2 rounded-full`} 
                                style={{ width: `${skill.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Session History */}
              <Card>
                <CardHeader>
                  <CardTitle>Session History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { date: 'Today', duration: '45 min', topics: ['Risk Management', 'Position Sizing'] },
                      { date: 'Yesterday', duration: '32 min', topics: ['Emotional Control', 'Market Analysis'] },
                      { date: '2 days ago', duration: '28 min', topics: ['Strategy Review', 'Technical Analysis'] }
                    ].map((session, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4">
                        <div className="flex justify-between items-start mb-1">
                          <p className="font-semibold text-sm">{session.date}</p>
                          <span className="text-xs text-gray-500">{session.duration}</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {session.topics.map((topic) => (
                            <span key={topic} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="psychology">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Psychological Metrics */}
              {analytics && (
                <Card>
                  <CardHeader>
                    <CardTitle>Psychological Profile</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Confidence Level</span>
                          <span>{Math.round(analytics.psychological_metrics.confidence_level * 100)}%</span>
                        </div>
                        <Progress value={analytics.psychological_metrics.confidence_level * 100} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Discipline Score</span>
                          <span>{Math.round(analytics.psychological_metrics.discipline_score * 100)}%</span>
                        </div>
                        <Progress value={analytics.psychological_metrics.discipline_score * 100} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Risk Tolerance</span>
                          <span>{Math.round(analytics.psychological_metrics.risk_tolerance * 100)}%</span>
                        </div>
                        <Progress value={analytics.psychological_metrics.risk_tolerance * 100} className="h-2" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Emotional Coaching */}
              <Card>
                <CardHeader>
                  <CardTitle>Emotional Coaching</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center p-6 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg">
                    <Heart className="w-12 h-12 text-purple-500 mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">Need Emotional Support?</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Your AI mentor is here to help you manage trading emotions
                    </p>
                    <Button className="w-full">Start Emotional Coaching</Button>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-semibold">Recent Emotional Patterns:</h4>
                    {[
                      { emotion: 'Overconfidence', frequency: 'High', advice: 'Practice humility and risk management' },
                      { emotion: 'Fear of Missing Out', frequency: 'Medium', advice: 'Focus on your trading plan' },
                      { emotion: 'Loss Aversion', frequency: 'Low', advice: 'Good progress on accepting losses' }
                    ].map((pattern) => (
                      <div key={pattern.emotion} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-start mb-1">
                          <p className="font-semibold text-sm">{pattern.emotion}</p>
                          <span className={`text-xs px-2 py-1 rounded ${
                            pattern.frequency === 'High' ? 'bg-red-100 text-red-600' :
                            pattern.frequency === 'Medium' ? 'bg-yellow-100 text-yellow-600' :
                            'bg-green-100 text-green-600'
                          }`}>
                            {pattern.frequency}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600">{pattern.advice}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="learning">
            <Card>
              <CardHeader>
                <CardTitle>Personalized Learning Path</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {[
                    { 
                      module: 'Advanced Risk Management', 
                      status: 'current', 
                      progress: 60,
                      lessons: ['Position Sizing Strategies', 'Portfolio Risk Assessment', 'Correlation Analysis'],
                      estimatedTime: '3 hours'
                    },
                    { 
                      module: 'Market Psychology', 
                      status: 'next', 
                      progress: 0,
                      lessons: ['Understanding Market Sentiment', 'Behavioral Finance', 'Crowd Psychology'],
                      estimatedTime: '4 hours'
                    },
                    { 
                      module: 'Algorithm Trading Basics', 
                      status: 'locked', 
                      progress: 0,
                      lessons: ['Introduction to Algorithms', 'Strategy Automation', 'Backtesting'],
                      estimatedTime: '6 hours'
                    }
                  ].map((module) => (
                    <div key={module.module} className={`border rounded-lg p-4 ${
                      module.status === 'current' ? 'border-blue-500 bg-blue-50' :
                      module.status === 'next' ? 'border-gray-300' :
                      'border-gray-200 opacity-60'
                    }`}>
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold">{module.module}</h3>
                          <p className="text-sm text-gray-600">Estimated time: {module.estimatedTime}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {module.status === 'current' && <Zap className="w-5 h-5 text-blue-500" />}
                          {module.status === 'next' && <Clock className="w-5 h-5 text-gray-400" />}
                          {module.status === 'locked' && <Target className="w-5 h-5 text-gray-300" />}
                        </div>
                      </div>
                      
                      {module.progress > 0 && (
                        <div className="mb-3">
                          <div className="flex justify-between text-sm mb-1">
                            <span>Progress</span>
                            <span>{module.progress}%</span>
                          </div>
                          <Progress value={module.progress} className="h-2" />
                        </div>
                      )}
                      
                      <div className="space-y-2">
                        <p className="text-sm font-semibold">Lessons:</p>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                          {module.lessons.map((lesson) => (
                            <div key={lesson} className="text-xs bg-white p-2 rounded border">
                              {lesson}
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div className="mt-4">
                        <Button 
                          size="sm" 
                          disabled={module.status === 'locked'}
                          variant={module.status === 'current' ? 'default' : 'outline'}
                        >
                          {module.status === 'current' ? 'Continue Learning' :
                           module.status === 'next' ? 'Start Module' :
                           'Locked'}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 