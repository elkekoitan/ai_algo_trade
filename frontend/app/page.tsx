'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface StatusResponse {
  api_status: string;
  mt5_status: string;
  terminal?: {
    name: string;
    company: string;
    version: string;
    build: string;
    path: string;
  };
  error?: string;
}

interface AccountInfoResponse {
  login: number;
  balance: number;
  equity: number;
  margin: number;
  margin_free: number;
  margin_level: number;
  currency: string;
  server: string;
  name: string;
  leverage: number;
  profit: number;
}

export default function Home() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [accountInfo, setAccountInfo] = useState<AccountInfoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch API status
        const statusResponse = await axios.get<StatusResponse>(
          'http://localhost:8001/api/status'
        );
        setStatus(statusResponse.data);

        // If MT5 is connected, fetch account info
        if (statusResponse.data.mt5_status === 'connected') {
          const accountResponse = await axios.get<AccountInfoResponse>(
            'http://localhost:8001/api/account_info'
          );
          setAccountInfo(accountResponse.data);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to connect to the backend API. Please ensure the server is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border p-4">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">ICT Ultra v2: Algo Forge Edition</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${status?.api_status === 'online' ? 'bg-primary' : 'bg-destructive'}`}></div>
              <span className="text-sm">API</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${status?.mt5_status === 'connected' ? 'bg-primary' : 'bg-destructive'}`}></div>
              <span className="text-sm">MT5</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-4">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="text-lg">Loading...</div>
          </div>
        ) : error ? (
          <div className="rounded-lg bg-destructive/20 p-4 text-destructive">
            <h2 className="text-lg font-semibold">Connection Error</h2>
            <p>{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* System Status Card */}
            <div className="rounded-lg bg-card p-6 shadow-md">
              <h2 className="mb-4 text-xl font-semibold">System Status</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>API Status:</span>
                  <span className={status?.api_status === 'online' ? 'text-primary' : 'text-destructive'}>
                    {status?.api_status?.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>MT5 Status:</span>
                  <span className={status?.mt5_status === 'connected' ? 'text-primary' : 'text-destructive'}>
                    {status?.mt5_status?.toUpperCase()}
                  </span>
                </div>
                {status?.terminal && (
                  <>
                    <div className="my-2 border-t border-border"></div>
                    <div className="flex items-center justify-between">
                      <span>Terminal:</span>
                      <span>{status.terminal.name}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Company:</span>
                      <span>{status.terminal.company}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Version:</span>
                      <span>{status.terminal.version}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Account Info Card */}
            {accountInfo ? (
              <div className="rounded-lg bg-card p-6 shadow-md">
                <h2 className="mb-4 text-xl font-semibold">Account Information</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Login:</span>
                    <span>{accountInfo.login}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Name:</span>
                    <span>{accountInfo.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Server:</span>
                    <span>{accountInfo.server}</span>
                  </div>
                  <div className="my-2 border-t border-border"></div>
                  <div className="flex items-center justify-between">
                    <span>Balance:</span>
                    <span className="text-lg font-semibold text-primary">
                      {accountInfo.balance.toLocaleString()} {accountInfo.currency}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Equity:</span>
                    <span>{accountInfo.equity.toLocaleString()} {accountInfo.currency}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Profit:</span>
                    <span className={accountInfo.profit >= 0 ? 'text-primary' : 'text-destructive'}>
                      {accountInfo.profit.toLocaleString()} {accountInfo.currency}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-lg bg-card p-6 shadow-md">
                <h2 className="mb-4 text-xl font-semibold">Account Information</h2>
                <div className="flex h-40 items-center justify-center">
                  <p className="text-muted-foreground">
                    {status?.mt5_status === 'connected'
                      ? 'Loading account information...'
                      : 'Connect to MT5 to view account information'}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Feature Cards */}
        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          {/* MQL5 Algo Forge Card */}
          <div className="rounded-lg bg-card p-6 shadow-md">
            <h3 className="mb-3 text-lg font-semibold">MQL5 Algo Forge</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Manage your Git repositories and synchronize with MT5 using the new Algo Forge integration.
            </p>
            <button 
              className="mt-2 w-full rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/80"
              disabled={!status || status.mt5_status !== 'connected'}
            >
              Open Forge Manager
            </button>
          </div>

          {/* ICT Analysis Card */}
          <div className="rounded-lg bg-card p-6 shadow-md">
            <h3 className="mb-3 text-lg font-semibold">ICT Analysis</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Analyze markets using ICT concepts like order blocks, fair value gaps, and breaker blocks.
            </p>
            <button 
              className="mt-2 w-full rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/80"
              disabled={!status || status.mt5_status !== 'connected'}
            >
              Start Analysis
            </button>
          </div>

          {/* Trading Dashboard Card */}
          <div className="rounded-lg bg-card p-6 shadow-md">
            <h3 className="mb-3 text-lg font-semibold">Trading Dashboard</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Access your full trading dashboard with charts, positions, and real-time updates.
            </p>
            <button 
              className="mt-2 w-full rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/80"
              disabled={!status || status.mt5_status !== 'connected'}
            >
              Open Dashboard
            </button>
          </div>
        </div>
      </main>
    </div>
  );
} 