'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

interface ChartData {
  label: string;
  value: number;
  color?: string;
}

interface AnalyticsChartProps {
  title: string;
  data: ChartData[];
  type: 'bar' | 'line' | 'pie';
  height?: number;
}

export default function AnalyticsChart({ title, data, type, height = 200 }: AnalyticsChartProps) {
  const maxValue = Math.max(...data.map(d => d.value));
  const totalValue = data.reduce((sum, d) => sum + d.value, 0);

  const renderBarChart = () => (
    <div className="flex items-end justify-between h-full space-x-2">
      {data.map((item, index) => (
        <div key={index} className="flex flex-col items-center flex-1">
          <div
            className="w-full bg-blue-500 rounded-t"
            style={{
              height: `${(item.value / maxValue) * 100}%`,
              backgroundColor: item.color || '#3b82f6'
            }}
          ></div>
          <div className="text-xs text-gray-600 mt-1 text-center">
            {item.label}
          </div>
          <div className="text-xs font-medium">
            {item.value}
          </div>
        </div>
      ))}
    </div>
  );

  const renderLineChart = () => (
    <div className="relative h-full">
      <svg className="w-full h-full" viewBox={`0 0 100 ${height}`}>
        <polyline
          fill="none"
          stroke="#3b82f6"
          strokeWidth="2"
          points={data.map((item, index) => {
            const x = (index / (data.length - 1)) * 100;
            const y = height - (item.value / maxValue) * height;
            return `${x},${y}`;
          }).join(' ')}
        />
        {data.map((item, index) => {
          const x = (index / (data.length - 1)) * 100;
          const y = height - (item.value / maxValue) * height;
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="3"
              fill="#3b82f6"
            />
          );
        })}
      </svg>
    </div>
  );

  const renderPieChart = () => (
    <div className="flex items-center justify-center h-full">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {data.map((item, index) => {
            const percentage = (item.value / totalValue) * 100;
            const startAngle = data
              .slice(0, index)
              .reduce((sum, d) => sum + (d.value / totalValue) * 360, 0);
            const endAngle = startAngle + (item.value / totalValue) * 360;
            
            const x1 = 50 + 40 * Math.cos((startAngle - 90) * Math.PI / 180);
            const y1 = 50 + 40 * Math.sin((startAngle - 90) * Math.PI / 180);
            const x2 = 50 + 40 * Math.cos((endAngle - 90) * Math.PI / 180);
            const y2 = 50 + 40 * Math.sin((endAngle - 90) * Math.PI / 180);
            
            const largeArcFlag = percentage > 50 ? 1 : 0;
            
            return (
              <path
                key={index}
                d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                fill={item.color || `hsl(${(index * 60) % 360}, 70%, 60%)`}
              />
            );
          })}
        </svg>
      </div>
      <div className="ml-4 space-y-1">
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: item.color || `hsl(${(index * 60) % 360}, 70%, 60%)` }}
            ></div>
            <span className="text-sm">{item.label}</span>
            <span className="text-sm font-medium">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return renderBarChart();
      case 'line':
        return renderLineChart();
      case 'pie':
        return renderPieChart();
      default:
        return renderBarChart();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div style={{ height: `${height}px` }}>
          {renderChart()}
        </div>
      </CardContent>
    </Card>
  );
} 