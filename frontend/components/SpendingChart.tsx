import React, { useMemo } from "react";
import { PieChart, AlertCircle } from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';

const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

// Color palette for categories
const CATEGORY_COLORS: Record<string, string> = {
  groceries: '#10b981',
  restaurants: '#f59e0b', 
  shopping: '#ec4899',
  transport: '#8b5cf6',
  utilities: '#6366f1',
  entertainment: '#14b8a6',
  transfer: '#3b82f6',
  salary: '#22c55e',
  housing: '#f97316',
  health: '#ef4444',
  education: '#0ea5e9',
  other: '#71717a',
};

const DEFAULT_COLOR = '#6366f1';

interface SpendingData {
  category: string;
  total: number;
}

interface SpendingChartProps {
  spendingData?: SpendingData[] | string;
  currency?: string;
}

export const SpendingChart = ({ spendingData, currency = 'AED' }: SpendingChartProps) => {
  const chartData = useMemo(() => {
    
    if (!spendingData) {
      return [];
    }
    
    let parsed: SpendingData[] = [];
    
    // Parse if string
    if (typeof spendingData === 'string') {
      try {
        parsed = JSON.parse(spendingData);
      } catch (e) {
        console.error('Failed to parse spending data:', e);
        return [];
      }
    } else if (Array.isArray(spendingData)) {
      parsed = spendingData;
    }
    
    // Transform to chart format
    return parsed.map(item => ({
      name: item.category ? item.category.charAt(0).toUpperCase() + item.category.slice(1) : 'Other',
      value: Number(item.total) || 0,
      color: CATEGORY_COLORS[item.category?.toLowerCase()] || DEFAULT_COLOR,
    }));
  }, [spendingData]);

  const totalSpending = chartData.reduce((sum, item) => sum + item.value, 0);

  const formatCurrency = (amount: number) => {
    if (currency === 'AED') {
      return `AED ${amount.toLocaleString('en-AE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  };

  if (chartData.length === 0) {
    return (
      <Card className="p-6 max-w-lg w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-yellow-500">
          <AlertCircle className="w-5 h-5" />
          <div>
            <p className="font-medium">No spending data available</p>
            <p className="text-xs text-zinc-500 mt-1">
              Try asking for spending data for a specific period.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 max-w-lg w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-purple-500" />
            Spending Analysis
          </h3>
          <p className="text-zinc-500 text-sm mt-1">Expenses by category</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-zinc-500">Total</p>
          <p className="text-lg font-bold text-white">{formatCurrency(totalSpending)}</p>
        </div>
      </div>
      
      <div className="h-64 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
            <XAxis 
              type="number" 
              stroke="#52525b" 
              fontSize={10} 
              tickFormatter={(val) => `${currency} ${val.toLocaleString()}`} 
            />
            <YAxis 
              dataKey="name" 
              type="category" 
              stroke="#a1a1aa" 
              fontSize={11} 
              width={80} 
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#18181b', 
                borderColor: '#27272a', 
                color: '#fff', 
                borderRadius: '8px' 
              }} 
              itemStyle={{ color: '#fff' }} 
              cursor={{ fill: '#27272a', opacity: 0.4 }}
              formatter={(value: number) => [formatCurrency(value), 'Amount']}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-zinc-800">
        {chartData.map((item, index) => (
          <div key={index} className="flex items-center gap-1.5">
            <div 
              className="w-2.5 h-2.5 rounded-full" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-zinc-400">{item.name}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};