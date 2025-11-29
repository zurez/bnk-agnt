import React, { useMemo } from "react";
import { Wallet, AlertCircle } from "lucide-react";

const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

interface Account {
  id: string;
  name: string;
  type: string;
  currency: string;
  balance: number;
  is_active?: boolean;
}

interface BalanceCardProps {
  userId: string;
  accounts?: Account[] | string;
}

export const BalanceCard = ({ userId, accounts }: BalanceCardProps) => {
  const displayAccounts: Account[] = useMemo(() => {
    if (!accounts) {
      return [];
    }
    
    if (typeof accounts === 'string') {
      try {
        const parsed = JSON.parse(accounts);
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        console.error('Failed to parse accounts JSON:', e);
        return [];
      }
    }
    
    if (Array.isArray(accounts)) {
      return accounts;
    }
    
    return [];
  }, [accounts]);
  
  const totalBalance = displayAccounts.reduce((sum, acc) => sum + (Number(acc.balance) || 0), 0);
  const currency = displayAccounts[0]?.currency || 'AED';

  const formatCurrency = (amount: number, curr: string) => {
    if (curr === 'AED') {
      return `AED ${amount.toLocaleString('en-AE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: curr,
      minimumFractionDigits: 2
    }).format(amount);
  };

  if (displayAccounts.length === 0) {
    return (
      <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-yellow-500">
          <AlertCircle className="w-5 h-5" />
          <div>
            <p className="font-medium">No account data available</p>
            <p className="text-xs text-zinc-500 mt-1">
              Raw data received: {JSON.stringify(accounts).slice(0, 100)}...
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="flex justify-between items-start mb-6">
        <div>
          <p className="text-zinc-400 text-sm font-medium">Total Balance</p>
          <h2 className="text-4xl font-bold text-white mt-1">{formatCurrency(totalBalance, currency)}</h2>
        </div>
        <div className="p-3 bg-blue-500/10 rounded-full border border-blue-500/20">
          <Wallet className="w-6 h-6 text-blue-500" />
        </div>
      </div>
      <div className="space-y-3">
        {displayAccounts.map((account, index) => (
          <div 
            key={account.id || index} 
            className="bg-zinc-950/50 p-4 rounded-lg border border-zinc-800 flex justify-between items-center group hover:border-zinc-700 transition-colors"
          >
            <div>
              <span className="text-zinc-300 text-sm block">{account.name}</span>
              <span className="text-zinc-500 text-xs">
                {account.type === 'checking' ? 'Current' : account.type === 'savings' ? 'Savings' : account.type} • {account.currency}
              </span>
            </div>
            <span className="text-white font-medium">{formatCurrency(Number(account.balance), account.currency)}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};