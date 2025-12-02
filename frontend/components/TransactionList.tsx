import React from 'react';
import { ArrowUpRight, ArrowDownLeft, Calendar, CreditCard } from 'lucide-react';

interface Transaction {
  id: string;
  amount: number;
  currency: string;
  description: string;
  date: string;
  type: 'credit' | 'debit' | 'transfer_in' | 'transfer_out';
  category?: string;
  merchant?: string;
  timestamp?: string; // Support both date and timestamp
}

interface TransactionListProps {
  transactions: Transaction[];
}

export function TransactionList({ transactions }: TransactionListProps) {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="p-4 text-center text-zinc-500 bg-zinc-900/50 rounded-xl border border-zinc-800">
        No transactions found.
      </div>
    );
  }

  return (
    <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden shadow-lg">
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/50 flex justify-between items-center">
        <h3 className="font-semibold text-zinc-200 flex items-center gap-2">
          <CreditCard size={16} className="text-blue-500" />
          Recent Transactions
        </h3>
        <span className="text-xs text-zinc-500 bg-zinc-900 px-2 py-1 rounded-full border border-zinc-800">
          {transactions.length} items
        </span>
      </div>
      
      <div className="divide-y divide-zinc-800 max-h-[400px] overflow-y-auto custom-scrollbar">
        {transactions.map((tx, index) => {
          const isCredit = tx.type === 'credit' || tx.type === 'transfer_in';
          const dateStr = tx.date || tx.timestamp || new Date().toISOString();
          const date = new Date(dateStr);
          
          return (
            <div key={tx.id || index} className="p-4 hover:bg-zinc-900/30 transition-colors group">
              <div className="flex justify-between items-start mb-1">
                <div className="flex items-start gap-3">
                  <div className={`mt-1 p-2 rounded-full ${isCredit ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                    {isCredit ? <ArrowDownLeft size={14} /> : <ArrowUpRight size={14} />}
                  </div>
                  <div>
                    <p className="font-medium text-zinc-200 text-sm line-clamp-1">
                      {tx.description || tx.merchant || 'Unknown Transaction'}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-zinc-500 flex items-center gap-1">
                        <Calendar size={10} />
                        {date.toLocaleDateString()}
                      </span>
                      {tx.category && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-zinc-800 text-zinc-400 rounded border border-zinc-700">
                          {tx.category}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold text-sm ${isCredit ? 'text-green-400' : 'text-zinc-200'}`}>
                    {isCredit ? '+' : '-'}{Math.abs(tx.amount).toFixed(2)}
                    <span className="text-xs text-zinc-500 ml-1">{tx.currency || 'AED'}</span>
                  </p>
                  <p className="text-[10px] text-zinc-600 mt-0.5 capitalize">
                    {tx.type.replace('_', ' ')}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="p-3 bg-zinc-900/30 border-t border-zinc-800 text-center">
        <button className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
          View all transactions
        </button>
      </div>
    </div>
  );
}
