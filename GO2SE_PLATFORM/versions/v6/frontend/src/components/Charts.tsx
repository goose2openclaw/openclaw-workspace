/**
 * 🪿 Charts Component
 * 数据可视化
 */

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface ChartProps {
  data: any[]
  dataKey: string
  color?: string
}

export function PriceChart({ data, dataKey = 'price', color = '#00d4aa' }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} domain={['auto', 'auto']} />
        <Tooltip 
          contentStyle={{ 
            background: '#1a1a25', 
            border: '1px solid #2a2a3a',
            borderRadius: '8px'
          }}
        />
        <Line 
          type="monotone" 
          dataKey={dataKey} 
          stroke={color} 
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function VolumeChart({ data }: { data: any[] }) {
  return (
    <ResponsiveContainer width="100%" height={100}>
      <LineChart data={data}>
        <XAxis dataKey="time" stroke="#6b7280" fontSize={10} hide />
        <YAxis stroke="#6b7280" fontSize={10} />
        <Tooltip 
          contentStyle={{ 
            background: '#1a1a25', 
            border: '1px solid #2a2a3a',
            borderRadius: '8px'
          }}
        />
        <Line 
          type="monotone" 
          dataKey="volume" 
          stroke="#7c3aed" 
          strokeWidth={1}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function ConfidenceGauge({ value, max = 10 }: { value: number; max?: number }) {
  const percentage = (value / max) * 100
  const color = percentage >= 70 ? '#10b981' : percentage >= 50 ? '#f59e0b' : '#6b7280'
  
  return (
    <div className="confidence-gauge">
      <div className="gauge-track">
        <div 
          className="gauge-fill" 
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      <span className="gauge-value" style={{ color }}>
        {value.toFixed(1)}/{max}
      </span>
    </div>
  )
}
