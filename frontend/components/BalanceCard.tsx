import React from "react";
import { Wallet } from "lucide-react";

// Shared Card component
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
  accounts?: Account[];
}

export const BalanceCard = ({ userId, accounts }: BalanceCardProps) => {
  // Use provided accounts or fallback to demo data
  const displayAccounts: Account[] = accounts && accounts.length > 0 
    ? accounts 
    : [
        { id: '1', name: 'Checking Account', type: 'checking', currency: 'AED', balance: 14230.20 },
        { id: '2', name: 'Savings Vault', type: 'savings', currency: 'AED', balance: 110362.25 },
      ];
  
  const totalBalance = displayAccounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
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
            <span className="text-white font-medium">{formatCurrency(account.balance, account.currency)}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};