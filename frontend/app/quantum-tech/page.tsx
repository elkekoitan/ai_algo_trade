'use client';

import QuantumLayout from "@/components/layout/QuantumLayout";
import { Brain } from "lucide-react";

export default function QuantumTechPage() {
  return (
    <QuantumLayout title="Quantum Tech" subtitle="Next-Generation Strategies">
      <div className="container mx-auto p-8 text-center">
        <Brain className="mx-auto h-16 w-16 text-quantum-primary animate-pulse" />
        <h1 className="mt-4 text-4xl font-bold">Quantum Technology</h1>
        <p className="mt-2 text-lg text-gray-400">This module is under heavy development.</p>
      </div>
    </QuantumLayout>
  );
} 