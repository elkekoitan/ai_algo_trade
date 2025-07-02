"use client";

import React from 'react';
import BrokerDashboard from '@/components/multi-broker/BrokerDashboard';

export default function MultiBrokerPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      <div className="container mx-auto px-4 py-8">
        <BrokerDashboard />
      </div>
    </div>
  );
} 