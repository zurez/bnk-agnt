"use client";

import React, { useState } from 'react';
import { CopilotKit, useFrontendTool, useCopilotReadable } from "@copilotkit/react-core";
import { 
  Wallet, 
  Send, 
  User,
  ChevronDown,
  Check,
  Loader2
} from 'lucide-react';

// Component imports
import { Sidebar } from '../components/Sidebar';
import { BalanceCard } from '../components/BalanceCard';
import { BeneficiaryManager } from '../components/BeneficiaryManager';
import { TransferMoney } from '../components/TransferMoney';
import { SpendingChart } from '../components/SpendingChart';
import { BankingChat } from '../components/BankingChat';

// --- DATA & TYPES ---
const users = [
  { id: 'usr_01', name: 'Alice Chen', avatar: 'A' },
  { id: 'usr_02', name: 'Bob Smith', avatar: 'B' },
];

const models = [
  { id: 'gpt-4', name: 'GPT-4 Turbo' },
  { id: 'claude-3', name: 'Claude 3 Opus' },
];

const DEFAULT_BENEFICIARIES = [
  { id: 1, name: 'Sarah Wilson', account: '**** 4521', bank: 'Chase' },
  { id: 2, name: 'Mike Ross', account: '**** 8892', bank: 'BOA' },
  { id: 3, name: 'Jessica Pearson', account: '**** 1234', bank: 'Citi' },
];

// --- MAIN PAGE CONTENT ---
function PageContent({ selectedUserId, setSelectedUserId, selectedModelId, setSelectedModelId }: any) {
  const selectedUser = users.find(u => u.id === selectedUserId);
  const [messages, setMessages] = useState<any[]>([{ id: 'init', role: 'assistant', content: "Hello! I'm your Banking Assistant. How can I help you today?", timestamp: new Date() }]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [thinkingStep, setThinkingStep] = useState("Thinking...");
  const [beneficiaries, setBeneficiaries] = useState(DEFAULT_BENEFICIARIES);

  const addMessage = (role: 'user' | 'assistant', content: string, component?: React.ReactNode) => {
    setMessages(prev => [...prev, { id: Date.now().toString(), role, content, timestamp: new Date(), component }]);
  };

  const handleSend = (e?: React.FormEvent, overridePrompt?: string) => {
    e?.preventDefault();
    const prompt = overridePrompt || inputValue;
    if (!prompt.trim()) return;

    addMessage('user', prompt);
    setInputValue("");
    // CopilotKit will handle the AI response via frontend tools
  };

  // --- COPILOT ACTIONS (Updated to use Shared State) ---
  useCopilotReadable({ description: "List of available beneficiaries", value: beneficiaries });
  
  useFrontendTool({ 
    name: "showBeneficiaries", 
    description: "Display beneficiaries", 
    parameters: [],
    handler: async () => addMessage('assistant', "Here are your beneficiaries.", <BeneficiaryManager beneficiaries={beneficiaries} setBeneficiaries={setBeneficiaries} />) 
  });
  
  useFrontendTool({ 
    name: "transferMoney", 
    description: "Show transfer form", 
    parameters: [],
    handler: async () => addMessage('assistant', "Transfer form ready.", <TransferMoney beneficiaries={beneficiaries} />) 
  });
  
  useFrontendTool({ 
    name: "showBalance", 
    description: "Show account balance", 
    parameters: [],
    handler: async () => addMessage('assistant', "Here is your current balance.", <BalanceCard userId={selectedUserId} />) 
  });
  
  useFrontendTool({ 
    name: "showSpending", 
    description: "Show spending analysis", 
    parameters: [],
    handler: async () => addMessage('assistant', "Here is your spending breakdown.", <SpendingChart />) 
  });

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-200 font-sans overflow-hidden">
      {/* SIDEBAR */}
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
                <button onClick={() => handleSend(undefined, "Show my balance")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2">
                  <Wallet size={14} /> Balance
                </button>
                <button onClick={() => handleSend(undefined, "Transfer money")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2">
                  <ArrowRightLeft size={14} /> Transfer
                </button>
                <button onClick={() => handleSend(undefined, "Show spending")} className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 text-sm transition-colors flex items-center gap-2">
                  <PieChart size={14} /> Reports
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col relative min-w-0">
        <header className="h-16 flex items-center justify-between px-6 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md z-20 shrink-0">
          <div className="md:hidden flex items-center gap-3">
            <Wallet className="w-5 h-5 text-blue-500" />
            <span className="font-bold">BankAgent</span>
          </div>
          <div className="hidden md:block text-sm text-zinc-500">
            Dashboard / <span className="text-zinc-200">Assistant</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="hidden sm:flex items-center gap-2">
                <div className="relative group">
                  <button className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-md text-xs font-medium text-zinc-400 hover:text-zinc-200 transition-colors">
                    <User size={14} /> {selectedUser?.name} <ChevronDown size={12} />
                  </button>
                  <div className="absolute right-0 top-full mt-1 w-48 bg-zinc-950 border border-zinc-800 rounded-lg shadow-xl overflow-hidden hidden group-hover:block z-50 animate-in fade-in slide-in-from-top-1">
                    {users.map(u => (
                      <button key={u.id} onClick={() => setSelectedUserId(u.id)} className={`w-full text-left px-3 py-2 text-xs flex items-center gap-2 hover:bg-zinc-900 transition-colors ${selectedUserId === u.id ? 'text-white bg-zinc-900' : 'text-zinc-400'}`}>
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${selectedUserId === u.id ? 'bg-blue-600 text-white' : 'bg-zinc-800'}`}>{u.avatar}</div>{u.name}
                        {selectedUserId === u.id && <Check size={12} className="ml-auto text-blue-500" />}
                      </button>
                    ))}
                  </div>
                </div>
             </div>
             <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-xs font-bold border border-blue-500/20 text-white cursor-pointer hover:ring-2 ring-blue-500/50 transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)]">{selectedUser?.name.charAt(0)}</div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden relative flex flex-col">
          <BankingChat messages={messages} isTyping={isTyping} thinkingStep={thinkingStep} onSend={handleSend} />
          <div className="absolute bottom-6 left-0 right-0 px-4 z-10">
            <div className="max-w-2xl mx-auto relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
              <form onSubmit={(e) => handleSend(e)} className="relative flex items-center bg-zinc-900/90 backdrop-blur-xl border border-zinc-700/50 rounded-full shadow-2xl p-1.5">
                <input type="text" value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="Ask about your finances..." className="flex-1 bg-transparent text-white placeholder:text-zinc-500 focus:outline-none px-4 py-3 text-sm" />
                <button type="submit" disabled={!inputValue.trim() || isTyping} className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white rounded-full transition-all shrink-0">
                  {isTyping ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// --- APP ENTRY ---
export default function App() {
  const [selectedUserId, setSelectedUserId] = useState(users[0].id);
  const [selectedModelId, setSelectedModelId] = useState(models[0].id);
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="bankbot" properties={{ user_id: selectedUserId }}>
      <PageContent selectedUserId={selectedUserId} setSelectedUserId={setSelectedUserId} selectedModelId={selectedModelId} setSelectedModelId={setSelectedModelId} />
    </CopilotKit>
  );
}