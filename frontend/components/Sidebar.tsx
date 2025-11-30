import React from "react";
import { Wallet, ArrowRightLeft, PieChart, Users, Receipt, Clock } from "lucide-react";

interface SidebarProps {
  onQuickAction: (prompt: string) => void;
}

export const Sidebar = ({ onQuickAction }: SidebarProps) => {
  return (
    <aside className="w-64 bg-zinc-900/40 border-r border-zinc-800 hidden md:flex flex-col backdrop-blur-sm">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Wallet className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">BankAgent</span>
        </div>
        <div className="space-y-6">
          <div>
            <h3 className="text-xs font-semibold text-zinc-500 mb-3 tracking-wider uppercase">Quick Access</h3>
            <div className="space-y-1">
              <button 
                onClick={() => onQuickAction("Show my balance")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <Wallet size={14} /> Balance
              </button>
              <button 
                onClick={() => onQuickAction("Transfer money")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <ArrowRightLeft size={14} /> Transfer
              </button>
              <button 
                onClick={() => onQuickAction("Show spending")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <PieChart size={14} /> Reports
              </button>
              <button 
                onClick={() => onQuickAction("Show my beneficiaries")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <Users size={14} /> Beneficiaries
              </button>
              <button 
                onClick={() => onQuickAction("Show my recent transactions")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <Receipt size={14} /> Transactions
              </button>
              <button 
                onClick={() => onQuickAction("Show pending transfers")} 
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2"
              >
                <Clock size={14} /> Pending
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
