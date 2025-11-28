"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const data = [
  { name: "Groceries", amount: 450, color: "#60a5fa" },
  { name: "Dining", amount: 320, color: "#a78bfa" },
  { name: "Transport", amount: 180, color: "#34d399" },
  { name: "Utilities", amount: 250, color: "#f472b6" },
  { name: "Shopping", amount: 550, color: "#fbbf24" },
];

export function SpendingChart() {
  return (
    <div className="h-full w-full flex flex-col">
      <h3 className="text-lg font-semibold text-slate-200 mb-4 px-2">Monthly Spending</h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#94a3b8"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip
              cursor={{ fill: "#1e293b", opacity: 0.5 }}
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "8px",
                color: "#f1f5f9",
              }}
              itemStyle={{ color: "#f1f5f9" }}
            />
            <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
