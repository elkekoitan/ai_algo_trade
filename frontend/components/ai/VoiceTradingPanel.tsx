"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX,
  Play,
  Pause,
  Brain,
  Zap,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  MessageSquare,
  Waveform,
  Settings
} from 'lucide-react';

interface VoiceCommand {
  id: string;
  transcript: string;
  confidence: number;
  interpretation: {
    action: string;
    symbol?: string;
    volume?: number;
    price?: number;
    isValid: boolean;
  };
  response: string;
  timestamp: Date;
  status: 'processing' | 'executed' | 'failed';
}

interface AudioVisualizerProps {
  isRecording: boolean;
  audioLevel: number;
}

const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ isRecording, audioLevel }) => {
  return (
    <div className="flex items-center justify-center gap-1 h-16">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className={`w-1 bg-gradient-to-t ${
            isRecording 
              ? 'from-quantum-primary to-quantum-secondary' 
              : 'from-gray-600 to-gray-500'
          } rounded-full`}
          animate={{
            height: isRecording 
              ? Math.random() * audioLevel * 60 + 10
              : 10,
            opacity: isRecording ? 0.8 + Math.random() * 0.2 : 0.3
          }}
          transition={{
            duration: 0.1,
            repeat: isRecording ? Infinity : 0,
            repeatType: "reverse"
          }}
        />
      ))}
    </div>
  );
};

export default function VoiceTradingPanel() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0.5);
  const [commands, setCommands] = useState<VoiceCommand[]>([]);
  const [isListening, setIsListening] = useState(true);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Initialize microphone access
    if (isListening) {
      initializeMicrophone();
    }
    
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isListening]);

  const initializeMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // Setup audio level monitoring
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateAudioLevel = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255);
        
        if (isListening) {
          requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
      
    } catch (error) {
      console.error('Failed to access microphone:', error);
    }
  };

  const startRecording = async () => {
    if (!streamRef.current) return;

    try {
      audioChunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(streamRef.current);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        processAudioCommand();
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const processAudioCommand = async () => {
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      
      // Convert to base64 or send as FormData to backend
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('user_id', 'user_123'); // Would come from auth
      
      // Send to AI voice processing endpoint
      const response = await fetch('/api/v1/ai/voice-command', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        
        const newCommand: VoiceCommand = {
          id: `cmd_${Date.now()}`,
          transcript: result.transcript || "Could not transcribe audio",
          confidence: result.confidence || 0,
          interpretation: result.interpretation || {
            action: "info",
            isValid: false
          },
          response: result.response || "I couldn't understand that command.",
          timestamp: new Date(),
          status: result.interpretation?.isValid ? 'executed' : 'failed'
        };
        
        setCommands(prev => [newCommand, ...prev.slice(0, 9)]); // Keep last 10 commands
        
        // Speak response if not muted
        if (!isMuted && result.response) {
          speakResponse(result.response);
        }
        
      } else {
        throw new Error('Failed to process voice command');
      }
      
    } catch (error) {
      console.error('Error processing voice command:', error);
      
      const errorCommand: VoiceCommand = {
        id: `cmd_${Date.now()}`,
        transcript: "Error processing audio",
        confidence: 0,
        interpretation: { action: "error", isValid: false },
        response: "Sorry, I couldn't process your command. Please try again.",
        timestamp: new Date(),
        status: 'failed'
      };
      
      setCommands(prev => [errorCommand, ...prev.slice(0, 9)]);
      
    } finally {
      setIsProcessing(false);
    }
  };

  const speakResponse = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const getCommandIcon = (command: VoiceCommand) => {
    if (command.interpretation.action === 'buy' || command.interpretation.action === 'sell') {
      return <TrendingUp className="w-4 h-4 text-green-400" />;
    }
    if (command.status === 'failed') {
      return <AlertTriangle className="w-4 h-4 text-red-400" />;
    }
    return <CheckCircle className="w-4 h-4 text-blue-400" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'executed': return 'text-green-400';
      case 'failed': return 'text-red-400';
      case 'processing': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="quantum-panel p-6 max-w-2xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-quantum-primary" />
          <h2 className="text-xl font-semibold text-white">AI Voice Trading</h2>
          <Zap className="w-5 h-5 text-yellow-400" />
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`p-2 rounded-lg transition-colors ${
              isMuted ? 'bg-red-500/20 text-red-400' : 'bg-gray-700 text-gray-400'
            }`}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
          
          <button
            onClick={() => setIsListening(!isListening)}
            className={`p-2 rounded-lg transition-colors ${
              isListening ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
            }`}
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Audio Visualizer */}
      <div className="bg-gray-800/50 rounded-xl p-6 mb-6">
        <AudioVisualizer isRecording={isRecording} audioLevel={audioLevel} />
        
        <div className="text-center mt-4">
          {isProcessing ? (
            <div className="flex items-center justify-center gap-2">
              <Brain className="w-5 h-5 text-quantum-primary animate-pulse" />
              <span className="text-quantum-primary">Processing with AI...</span>
            </div>
          ) : isRecording ? (
            <div className="space-y-2">
              <p className="text-white font-medium">Listening...</p>
              <p className="text-sm text-gray-400">Say your trading command</p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-400">Ready to listen</p>
              <p className="text-xs text-gray-500">
                Try: "Buy EURUSD with 0.1 lot" or "What's the price of Gold?"
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <motion.button
          whileTap={{ scale: 0.95 }}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
          disabled={isProcessing || !isListening}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
            isRecording
              ? 'bg-red-500 text-white scale-110'
              : isProcessing
              ? 'bg-gray-600 text-gray-400'
              : 'bg-quantum-primary text-black hover:bg-quantum-primary/80'
          }`}
        >
          {isProcessing ? (
            <Brain className="w-6 h-6 animate-pulse" />
          ) : isRecording ? (
            <MicOff className="w-6 h-6" />
          ) : (
            <Mic className="w-6 h-6" />
          )}
        </motion.button>
        
        <div className="text-center">
          <p className="text-sm text-gray-400">
            {isRecording ? 'Release to send' : 'Hold to record'}
          </p>
        </div>
      </div>

      {/* Command History */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-medium text-white">Recent Commands</h3>
        </div>
        
        <div className="max-h-96 overflow-y-auto space-y-3">
          <AnimatePresence mode="popLayout">
            {commands.map((command) => (
              <motion.div
                key={command.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50"
              >
                <div className="flex items-start gap-3">
                  {getCommandIcon(command)}
                  
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-white font-medium">
                        "{command.transcript}"
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400">
                          {command.confidence.toFixed(0)}%
                        </span>
                        <span className={`text-xs ${getStatusColor(command.status)}`}>
                          {command.status}
                        </span>
                      </div>
                    </div>
                    
                    {command.interpretation.isValid && (
                      <div className="text-sm text-gray-300 bg-gray-700/30 rounded px-3 py-2">
                        <strong>Action:</strong> {command.interpretation.action}
                        {command.interpretation.symbol && (
                          <> • <strong>Symbol:</strong> {command.interpretation.symbol}</>
                        )}
                        {command.interpretation.volume && (
                          <> • <strong>Volume:</strong> {command.interpretation.volume}</>
                        )}
                      </div>
                    )}
                    
                    <div className="text-sm text-quantum-primary bg-quantum-primary/10 rounded px-3 py-2">
                      <strong>AI Response:</strong> {command.response}
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      {command.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {commands.length === 0 && (
            <div className="text-center py-8">
              <MessageSquare className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400">No voice commands yet</p>
              <p className="text-sm text-gray-500">Start by recording a command</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Commands */}
      <div className="mt-6 pt-6 border-t border-gray-800">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Example Commands:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          {[
            "Buy EURUSD with 0.1 lot",
            "Sell Bitcoin at market price",
            "Close all positions",
            "What's the price of Gold?",
            "Show me GBPUSD chart",
            "Set stop loss at 1.0900"
          ].map((example, index) => (
            <div key={index} className="text-gray-500 italic">
              "{example}"
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
} 