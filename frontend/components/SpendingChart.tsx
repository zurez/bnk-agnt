import React from "react";
import { PieChart } from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className = "" }: CardProps) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

const spendingData = [
  { name: 'Housing', value: 2000, color: '#3b82f6' },
  { name: 'Food', value: 800, color: '#10b981' },
  { name: 'Transport', value: 400, color: '#f59e0b' },
  { name: 'Utilities', value: 300, color: '#6366f1' },
  { name: 'Ent.', value: 200, color: '#ec4899' },
];

export const SpendingChart = () => (
  <Card className="p-6 max-w-lg w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
    <h3 className="font-semibold text-zinc-100 mb-2 flex items-center gap-2">
      <PieChart className="w-5 h-5 text-purple-500" />
      Spending Analysis
    </h3>
    <p className="text-zinc-500 text-sm mb-6">Monthly expenses by category</p>
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={spendingData} layout="vertical" margin={{ left: 10, right: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
          <XAxis type="number" stroke="#52525b" fontSize={10} tickFormatter={(val) => `$${val}`} />
          <YAxis dataKey="name" type="category" stroke="#a1a1aa" fontSize={11} width={60} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#18181b', 
              borderColor: '#27272a', 
              color: '#fff', 
              borderRadius: '8px' 
            }} 
            itemStyle={{ color: '#fff' }} 
            cursor={{ fill: '#27272a', opacity: 0.4 }} 
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
            {spendingData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  </Card>
);
