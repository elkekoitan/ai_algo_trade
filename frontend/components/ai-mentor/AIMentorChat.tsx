"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  Send, Bot, User, Brain, TrendingUp, AlertTriangle, 
  Lightbulb, Target, BookOpen, Heart, Zap 
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'mentor';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  resources?: any[];
  mood?: string;
  analysis?: any;
}

interface AIMentorChatProps {
  userId: string;
}

export default function AIMentorChat({ userId }: AIMentorChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);
  const [mentorPersonality, setMentorPersonality] = useState('supportive');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    startMentorSession();
  }, [userId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startMentorSession = async () => {
    try {
      const response = await fetch('/api/v1/ai-mentor/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: userId,
          session_goals: ['improve_trading_skills', 'risk_management'] 
        })
      });
      
      const data = await response.json();
      
      if (data.welcome_message) {
        setMessages([{
          id: 'welcome',
          type: 'mentor',
          content: data.welcome_message,
          timestamp: new Date(),
          mood: 'welcoming'
        }]);
        setSessionActive(true);
      }
    } catch (error) {
      console.error('Failed to start mentor session:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/ai-mentor/session/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: inputMessage,
          context: {
            session_active: sessionActive,
            personality: mentorPersonality
          }
        })
      });

      const data = await response.json();

      const mentorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'mentor',
        content: data.content,
        timestamp: new Date(),
        suggestions: data.suggestions,
        resources: data.resources,
        analysis: data.analysis
      };

      setMessages(prev => [...prev, mentorMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'mentor',
        content: 'I apologize, but I\'m having trouble processing your message right now. Please try again.',
        timestamp: new Date(),
        mood: 'apologetic'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickHelp = async (topic: string) => {
    try {
      const response = await fetch('/api/v1/ai-mentor/quick-help', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          topic: topic,
          urgency: 'normal'
        })
      });

      const data = await response.json();

      const helpMessage: Message = {
        id: Date.now().toString(),
        type: 'mentor',
        content: data.quick_help,
        timestamp: new Date(),
        suggestions: data.follow_up_actions
      };

      setMessages(prev => [...prev, helpMessage]);
    } catch (error) {
      console.error('Failed to get quick help:', error);
    }
  };

  const getMentorAvatar = () => {
    const avatars = {
      supportive: '🤗',
      analytical: '🧠',
      motivational: '💪',
      strict: '👨‍🏫',
      friendly: '😊'
    };
    return avatars[mentorPersonality as keyof typeof avatars] || '🤖';
  };

  const getMessageIcon = (type: string, mood?: string) => {
    if (type === 'user') return <User className="w-4 h-4" />;
    
    switch (mood) {
      case 'analytical':
        return <Brain className="w-4 h-4 text-blue-500" />;
      case 'encouraging':
        return <Heart className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'insightful':
        return <Lightbulb className="w-4 h-4 text-yellow-400" />;
      default:
        return <Bot className="w-4 h-4 text-green-500" />;
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto">
      {/* Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getMentorAvatar()}</div>
              <div>
                <CardTitle className="text-lg">AI Trading Mentor</CardTitle>
                <p className="text-sm text-gray-600">
                  Your personal trading coach • {sessionActive ? 'Session Active' : 'Starting Session...'}
                </p>
              </div>
            </div>
            
            {/* Personality Selector */}
            <div className="flex space-x-1">
              {[
                { key: 'supportive', emoji: '🤗', label: 'Supportive' },
                { key: 'analytical', emoji: '🧠', label: 'Analytical' },
                { key: 'motivational', emoji: '💪', label: 'Motivational' },
                { key: 'strict', emoji: '👨‍🏫', label: 'Strict' },
                { key: 'friendly', emoji: '😊', label: 'Friendly' }
              ].map((personality) => (
                <Button
                  key={personality.key}
                  variant={mentorPersonality === personality.key ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setMentorPersonality(personality.key)}
                  className="text-xs"
                  title={personality.label}
                >
                  {personality.emoji}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Quick Help Buttons */}
      <div className="my-4">
        <div className="flex flex-wrap gap-2">
          {[
            { topic: 'risk_management', label: 'Risk Management', icon: <Target className="w-4 h-4" /> },
            { topic: 'emotional_control', label: 'Emotional Control', icon: <Heart className="w-4 h-4" /> },
            { topic: 'strategy_review', label: 'Strategy Review', icon: <TrendingUp className="w-4 h-4" /> },
            { topic: 'market_analysis', label: 'Market Analysis', icon: <Brain className="w-4 h-4" /> }
          ].map((help) => (
            <Button
              key={help.topic}
              variant="outline"
              size="sm"
              onClick={() => handleQuickHelp(help.topic)}
              className="flex items-center space-x-1"
            >
              {help.icon}
              <span>{help.label}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                <div className={`flex items-start space-x-2 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <Avatar className="w-8 h-8 mt-1">
                    <AvatarFallback className={message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-green-500 text-white'}>
                      {getMessageIcon(message.type, message.mood)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className={`rounded-lg p-3 ${
                    message.type === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    
                    {/* Suggestions */}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs font-semibold opacity-75">Suggestions:</p>
                        {message.suggestions.map((suggestion, index) => (
                          <Button
                            key={index}
                            variant="ghost"
                            size="sm"
                            className="w-full text-left justify-start text-xs h-auto p-2 bg-white/10 hover:bg-white/20"
                            onClick={() => setInputMessage(suggestion)}
                          >
                            <Lightbulb className="w-3 h-3 mr-2" />
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}
                    
                    {/* Resources */}
                    {message.resources && message.resources.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-semibold opacity-75 mb-2">Resources:</p>
                        <div className="space-y-1">
                          {message.resources.map((resource, index) => (
                            <div key={index} className="flex items-center space-x-2 text-xs">
                              <BookOpen className="w-3 h-3" />
                              <span>{resource.title || resource}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="text-xs opacity-50 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-600">AI Mentor is thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </CardContent>
        
        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask your AI mentor anything about trading..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              onClick={sendMessage} 
              disabled={isLoading || !inputMessage.trim()}
              size="sm"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 mt-2">
            {[
              '💡 Give me a trading tip',
              '📊 Analyze my last trade',
              '🎯 Help with position sizing',
              '😌 I need emotional support',
              '📚 Teach me something new'
            ].map((quickAction) => (
              <Button
                key={quickAction}
                variant="ghost"
                size="sm"
                onClick={() => setInputMessage(quickAction.substring(2))}
                className="text-xs h-6 px-2"
              >
                {quickAction}
              </Button>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
} 