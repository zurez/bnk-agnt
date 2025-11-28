import React from "react";
import { Wallet } from "lucide-react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card = ({ children, className = "" }: CardProps) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

interface BalanceCardProps {
  userId: string;
}

export const BalanceCard = ({ userId }: BalanceCardProps) => {
  return (
    <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="flex justify-between items-start mb-6">
        <div>
          <p className="text-zinc-400 text-sm font-medium">Total Balance</p>
          <h2 className="text-4xl font-bold text-white mt-1">$124,592.45</h2>
        </div>
        <div className="p-3 bg-blue-500/10 rounded-full border border-blue-500/20">
          <Wallet className="w-6 h-6 text-blue-500" />
        </div>
      </div>
      <div className="space-y-3">
        <div className="bg-zinc-950/50 p-4 rounded-lg border border-zinc-800 flex justify-between items-center group hover:border-zinc-700 transition-colors">
          <div>
            <span className="text-zinc-300 text-sm block">Checking Account</span>
            <span className="text-zinc-500 text-xs">**** 4521 • Chase Bank</span>
          </div>
          <span className="text-white font-medium">$14,230.20</span>
        </div>
        <div className="bg-zinc-950/50 p-4 rounded-lg border border-zinc-800 flex justify-between items-center group hover:border-zinc-700 transition-colors">
          <div>
            <span className="text-zinc-300 text-sm block">Savings Vault</span>
            <span className="text-zinc-500 text-xs">**** 8892 • High Yield</span>
          </div>
          <span className="text-white font-medium">$110,362.25</span>
        </div>
      </div>
    </Card>
  );
};
