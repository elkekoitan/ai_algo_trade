'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from "@/components/layout/Header";
import AccountInfo from "@/components/dashboard/AccountInfo";

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
    <>
      <Header />
      <main className="min-h-screen bg-gray-950 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page Title */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-gray-400">Welcome to ICT Ultra v2: Algo Forge Edition</p>
          </div>

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Account Info */}
            <div className="lg:col-span-2">
              <AccountInfo />
            </div>

            {/* Quick Stats */}
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
              <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">API Status</span>
                  <span className="text-green-400 font-medium">Online</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">MT5 Connection</span>
                  <span className="text-green-400 font-medium">Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Active Signals</span>
                  <span className="text-white font-medium">0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Open Positions</span>
                  <span className="text-white font-medium">0</span>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
              <div className="space-y-3">
                <p className="text-gray-400 text-sm">No recent activity</p>
              </div>
            </div>
          </div>

          {/* Features Grid */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a href="/trading" className="group bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 hover:border-emerald-600/50 transition-all duration-200 cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-emerald-600/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <h4 className="text-white font-semibold mb-2">Trading</h4>
              <p className="text-gray-400 text-sm">Execute trades and manage positions</p>
            </a>

            <a href="/signals" className="group bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 hover:border-cyan-600/50 transition-all duration-200 cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <h4 className="text-white font-semibold mb-2">ICT Signals</h4>
              <p className="text-gray-400 text-sm">View and analyze trading signals</p>
            </a>

            <a href="/ai" className="group bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 hover:border-purple-600/50 transition-all duration-200 cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <h4 className="text-white font-semibold mb-2">AI Analysis</h4>
              <p className="text-gray-400 text-sm">Advanced market predictions</p>
            </a>

            <a href="/risk" className="group bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-800 hover:border-orange-600/50 transition-all duration-200 cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-orange-600/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              </div>
              <h4 className="text-white font-semibold mb-2">Risk Manager</h4>
              <p className="text-gray-400 text-sm">Monitor and control risk exposure</p>
            </a>
          </div>
        </div>
      </main>
    </>
  );
} 