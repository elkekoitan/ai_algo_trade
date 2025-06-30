"use client"

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function AutoTraderChart() {
  const { data, error } = useSWR('/api/v1/autotrader/equity-curve', fetcher, { refreshInterval: 5000 });

  if (error) return <div>Failed to load chart data</div>
  if (!data) return <div>Loading...</div>
  if (data.length === 0) return <div>No trading data available yet.</div>

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <XAxis
          dataKey="time"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip
            contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
            labelFormatter={(label) => new Date(label).toLocaleString()}
        />
        <Line type="monotone" dataKey="balance" stroke="#8884d8" dot={false} />
        <Line type="monotone" dataKey="equity" stroke="#82ca9d" dot={false}/>
      </LineChart>
    </ResponsiveContainer>
  )
} 