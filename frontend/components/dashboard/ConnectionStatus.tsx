'use client';
import useSWR from 'swr';
import { API_ENDPOINTS } from '@/lib/api';

const fetcher = (url: string) => fetch(url).then(res => res.json());

const StatusIndicator = ({ label, isConnected }: { label: string; isConnected: boolean }) => (
  <div className="flex items-center space-x-2">
    <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
    <span className="text-sm text-gray-300">{label}</span>
    <span className={`text-xs font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
      {isConnected ? 'Online' : 'Offline'}
    </span>
  </div>
);

export default function ConnectionStatus() {
  const { data: healthData } = useSWR(API_ENDPOINTS.health, fetcher, { refreshInterval: 5000 });

  const mt5Connected = healthData?.status === 'healthy' && healthData?.mt5_connected;
  // Placeholders for other services
  const websocketConnected = false;
  const databaseConnected = false; 
  const apiConnected = !!healthData;

  return (
    <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-4 border border-gray-800">
      <h3 className="font-semibold text-white mb-3">Connection Status</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatusIndicator label="MT5" isConnected={mt5Connected} />
        <StatusIndicator label="WebSocket" isConnected={websocketConnected} />
        <StatusIndicator label="Database" isConnected={databaseConnected} />
        <StatusIndicator label="API" isConnected={apiConnected} />
      </div>
    </div>
  );
} 