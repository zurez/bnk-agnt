"use client";

import React, { useState, useCallback, useMemo } from 'react';
import { 
  CopilotKit, 
  useCopilotAction,
  useCopilotReadable, 
  useCopilotChat,
} from "@copilotkit/react-core";
import { TextMessage, Role } from "@copilotkit/runtime-client-gql";
import { 
  Wallet, 
  Send, 
  User,
  ChevronDown,
  Check,
  Loader2,
  Bot
} from 'lucide-react';

import { Sidebar } from '../components/Sidebar';
import { BalanceCard } from '../components/BalanceCard';
import { BeneficiaryManager } from '../components/BeneficiaryManager';
import { TransferMoney } from '../components/TransferMoney';
import { SpendingChart } from '../components/SpendingChart';
import { BankingChat } from '../components/BankingChat';

// --- DATA & TYPES ---
interface UserType {
  id: string;
  name: string;
  avatar: string;
}

interface ModelType {
  id: string;
  name: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  component?: React.ReactNode;
}

const users: UserType[] = [
  { id: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', name: 'Alice Ahmed', avatar: 'A' },
  { id: 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', name: 'Bob Mansour', avatar: 'B' },
  { id: 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', name: 'Carol Ali', avatar: 'C' },
];

const models: ModelType[] = [
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'deepseek-r1', name: 'DeepSeek R1' },
  { id: 'deepseek-v3', name: 'DeepSeek V3' },
  { id: 'llama-3.3-70b', name: 'Llama 3.3 70B' },
  { id: 'llama-3.1-8b', name: 'Llama 3.1 8B' },
  { id: 'qwen3-32b', name: 'Qwen3 32B' },
];

// --- MAIN PAGE CONTENT ---
interface PageContentProps {
  selectedUserId: string;
  setSelectedUserId: (id: string) => void;
  selectedModelId: string;
  setSelectedModelId: (id: string) => void;
}

function PageContent({ selectedUserId, setSelectedUserId, selectedModelId, setSelectedModelId }: PageContentProps) {
  const selectedUser = users.find(u => u.id === selectedUserId);
  const [inputValue, setInputValue] = useState("");
  
  // Local messages for components from frontend actions
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);
  
  // Cache for fetched data to pass to components
  const [cachedAccounts, setCachedAccounts] = useState<any[]>([]);
  const [cachedBeneficiaries, setCachedBeneficiaries] = useState<any[]>([]);
  const [cachedSpending, setCachedSpending] = useState<any[]>([]);

  // Use CopilotChat hook
  const { appendMessage, isLoading, visibleMessages } = useCopilotChat();

  // Build messages from visibleMessages + local messages
  const messages: ChatMessage[] = useMemo(() => {
    const result: ChatMessage[] = [
      { 
        id: 'init', 
        role: 'assistant', 
        content: "Hello! I'm your Phoenix Digital Bank Assistant. How can I help you today?", 
        timestamp: new Date(0)
      }
    ];

    const rawMessages = visibleMessages as any[];
    
    if (!rawMessages || rawMessages.length === 0) {
      return [...result, ...localMessages];
    }

    // Strategy 1: Look for AgentStateMessage with complete conversation history
    let stateMessages: any[] = [];
    for (let i = rawMessages.length - 1; i >= 0; i--) {
      const msg = rawMessages[i];
      if (msg?.type === 'AgentStateMessage' && msg?.state?.messages) {
        stateMessages = msg.state.messages;
        break;
      }
    }

    if (stateMessages.length > 0) {
      // Use messages from agent state (complete history from LangGraph)
      stateMessages.forEach((m: any, index: number) => {
        // Skip if no content (tool calls have 'name' instead of 'content')
        if (!m.content) return;
        // Skip tool-related messages
        if (m.name || m.actionExecutionId || m.result) return;
        // Only process user and assistant messages
        if (m.role !== 'user' && m.role !== 'assistant') return;

        result.push({
          id: m.id || `state-${index}`,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(index + 1),
        });
      });
    } else {
      // Strategy 2: Fallback to TextMessages directly
      const seenIds = new Set<string>();
      rawMessages.forEach((m: any, index: number) => {
        if (m?.type === 'TextMessage' && m?.content && m?.role && !seenIds.has(m.id)) {
          seenIds.add(m.id);
          result.push({
            id: m.id,
            role: m.role === 'user' ? 'user' : 'assistant',
            content: m.content,
            timestamp: new Date(index + 1),
          });
        }
      });
    }

    // Add local messages (from frontend actions with components)
    localMessages.forEach((lm) => {
      result.push(lm);
    });

    // Sort by timestamp and dedupe by ID
    const seenFinal = new Set<string>();
    return result
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .filter(m => {
        if (seenFinal.has(m.id)) return false;
        seenFinal.add(m.id);
        return true;
      });
  }, [visibleMessages, localMessages]);

  // Add local message helper
  const addLocalMessage = useCallback((role: 'user' | 'assistant', content: string, component?: React.ReactNode) => {
    const id = `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setLocalMessages(prev => [...prev, {
      id,
      role,
      content,
      timestamp: new Date(),
      component,
    }]);
  }, []);

  const handleSend = async (e?: React.FormEvent, overridePrompt?: string) => {
    e?.preventDefault();
    const prompt = overridePrompt || inputValue;
    if (!prompt.trim() || isLoading) return;

    setInputValue("");

    try {
      await appendMessage(
        new TextMessage({
          role: Role.User,
          content: prompt,
        })
      );
    } catch (error) {
      console.error('Error sending message:', error);
      addLocalMessage('assistant', 'Sorry, there was an error processing your request.');
    }
  };

  // --- COPILOT READABLE STATE ---
  useCopilotReadable({ 
    description: "Current user ID for banking operations", 
    value: selectedUserId 
  });
  
  useCopilotReadable({ 
    description: "Cached account balances", 
    value: cachedAccounts 
  });
  
  useCopilotReadable({ 
    description: "Cached beneficiaries list", 
    value: cachedBeneficiaries 
  });
  
  // --- COPILOT ACTIONS (Frontend Tools) ---
  useCopilotAction({ 
    name: "showBalance", 
    description: "Display account balances UI. Use when user wants to SEE/VIEW their balance. Pass the accounts data from get_balance tool.", 
    parameters: [
      { 
        name: "accounts", 
        type: "object[]" as const, 
        description: "Array of account objects with id, name, type, balance, currency fields",
        required: false
      }
    ],
    handler: async ({ accounts }: { accounts?: any[] | string }) => {
    // Parse if it's a string
    let accountData = accounts;
    if (typeof accounts === 'string') {
      try {
        accountData = JSON.parse(accounts);
      } catch (e) {
        console.error('Failed to parse accounts:', e);
        accountData = cachedAccounts;
      }
    }
    accountData = accountData || cachedAccounts;
    if (Array.isArray(accountData)) setCachedAccounts(accountData);
    
    addLocalMessage(
      'assistant', 
      "Here are your account balances:", 
      <BalanceCard userId={selectedUserId} accounts={Array.isArray(accountData) ? accountData : []} />
    );
    return "Displayed account balances to user";
  }
  });
  
  useCopilotAction({ 
    name: "showBeneficiaries", 
    description: "Display beneficiaries list UI. Use when user wants to SEE/VIEW their beneficiaries. Pass the beneficiaries data from get_beneficiaries tool.", 
    parameters: [
      { 
        name: "beneficiaries", 
        type: "object[]" as const, 
        description: "Array of beneficiary objects with id, nickname, account_number, bank_name, is_internal fields",
        required: false
      }
    ],
    handler: async ({ beneficiaries }: { beneficiaries?: any[] }) => {
      const benData = beneficiaries || cachedBeneficiaries;
      if (beneficiaries) setCachedBeneficiaries(beneficiaries);
      addLocalMessage(
        'assistant', 
        "Here are your beneficiaries:", 
        <BeneficiaryManager beneficiaries={benData} />
      );
      return "Displayed beneficiaries list to user";
    }
  });
  
  useCopilotAction({ 
    name: "showSpending", 
    description: "Display spending analysis chart. Use when user wants to SEE/VIEW their spending breakdown. Pass spending data from get_spend_by_category tool.", 
    parameters: [
      { 
        name: "spendingData", 
        type: "object[]" as const, 
        description: "Array of spending objects with category and total fields",
        required: false
      },
      { 
        name: "currency", 
        type: "string" as const, 
        description: "Currency code (e.g. AED)",
        required: false
      }
    ],
    handler: async ({ spendingData, currency }: { spendingData?: any[]; currency?: string }) => {
      const spending = spendingData || cachedSpending;
      if (spendingData) setCachedSpending(spendingData);
      addLocalMessage(
        'assistant', 
        "Here is your spending breakdown:", 
        <SpendingChart spendingData={spending} currency={currency || 'AED'} />
      );
      return "Displayed spending analysis to user";
    }
  });

  useCopilotAction({ 
    name: "showTransferForm", 
    description: "Display transfer money form. Use when user wants to MAKE a transfer. Requires accounts and beneficiaries data.", 
    parameters: [
      { 
        name: "accounts", 
        type: "object[]" as const, 
        description: "User's accounts for 'from' selection",
        required: false
      },
      { 
        name: "beneficiaries", 
        type: "object[]" as const, 
        description: "User's beneficiaries for 'to' selection",
        required: false
      }
    ],
    handler: async ({ accounts, beneficiaries }: { accounts?: any[]; beneficiaries?: any[] }) => {
      const accts = accounts || cachedAccounts;
      const bens = beneficiaries || cachedBeneficiaries;
      if (accounts) setCachedAccounts(accounts);
      if (beneficiaries) setCachedBeneficiaries(beneficiaries);
      addLocalMessage(
        'assistant', 
        "Here's the transfer form:", 
        <TransferMoney accounts={accts} beneficiaries={bens} />
      );
      return "Displayed transfer form to user";
    }
  });

  useCopilotAction({ 
    name: "showPendingTransfers", 
    description: "Display pending transfers that need approval. Pass data from get_pending_transfers tool.", 
    parameters: [
      { 
        name: "transfers", 
        type: "object[]" as const, 
        description: "Array of pending transfer objects",
        required: false
      }
    ],
    handler: async ({ transfers }: { transfers?: any[] }) => {
      const pendingList = transfers || [];
      if (pendingList.length === 0) {
        addLocalMessage('assistant', "You have no pending transfers awaiting approval.");
      } else {
        const content = pendingList.map((t: any) => 
          `• ${t.amount} ${t.currency || 'AED'} from ${t.from_account} to ${t.to_destination} - ID: ${t.id}`
        ).join('\n');
        addLocalMessage(
          'assistant', 
          `You have ${pendingList.length} pending transfer(s):\n\n${content}\n\nSay "approve transfer [ID]" to approve or "reject transfer [ID]" to reject.`
        );
      }
      return "Displayed pending transfers to user";
    }
  });

  useCopilotAction({ 
    name: "showTransactions", 
    description: "Display recent transactions. Pass data from get_transactions tool.", 
    parameters: [
      { 
        name: "transactions", 
        type: "object[]" as const, 
        description: "Array of transaction objects",
        required: false
      }
    ],
    handler: async ({ transactions }: { transactions?: any[] }) => {
      const txList = transactions || [];
      if (txList.length === 0) {
        addLocalMessage('assistant', "No transactions found for the specified criteria.");
      } else {
        const content = txList.slice(0, 10).map((t: any) => {
          const sign = t.type === 'credit' || t.type === 'transfer_in' ? '+' : '-';
          return `• ${sign}${t.amount} ${t.currency || 'AED'} - ${t.description || t.category} (${new Date(t.timestamp).toLocaleDateString()})`;
        }).join('\n');
        addLocalMessage('assistant', `Here are your recent transactions:\n\n${content}`);
      }
      return "Displayed transactions to user";
    }
  });

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-200 font-sans overflow-hidden">
      {/* SIDEBAR */}
      <Sidebar onQuickAction={(prompt: string) => handleSend(undefined, prompt)} />

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
                {/* Model Selector */}
                <div className="relative group">
                  <button className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-md text-xs font-medium text-zinc-400 hover:text-zinc-200 transition-colors">
                    <Bot size={14} /> {models.find(m => m.id === selectedModelId)?.name} <ChevronDown size={12} />
                  </button>
                  <div className="absolute right-0 top-full mt-1 w-48 bg-zinc-950 border border-zinc-800 rounded-lg shadow-xl overflow-hidden hidden group-hover:block z-50 animate-in fade-in slide-in-from-top-1">
                    {models.map(m => (
                      <button key={m.id} onClick={() => setSelectedModelId(m.id)} className={`w-full text-left px-3 py-2 text-xs flex items-center gap-2 hover:bg-zinc-900 transition-colors ${selectedModelId === m.id ? 'text-white bg-zinc-900' : 'text-zinc-400'}`}>
                        <Bot size={14} className={selectedModelId === m.id ? 'text-blue-500' : 'text-zinc-600'} />
                        {m.name}
                        {selectedModelId === m.id && <Check size={12} className="ml-auto text-blue-500" />}
                      </button>
                    ))}
                  </div>
                </div>

                {/* User Selector */}
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
          <BankingChat messages={messages} isTyping={isLoading} thinkingStep="Thinking..." onSend={handleSend} />
          <div className="absolute bottom-6 left-0 right-0 px-4 z-10">
            <div className="max-w-2xl mx-auto relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
              <form onSubmit={(e) => handleSend(e)} className="relative flex items-center bg-zinc-900/90 backdrop-blur-xl border border-zinc-700/50 rounded-full shadow-2xl p-1.5">
                <input type="text" value={inputValue} onChange={(e) => setInputValue(e.target.value)} placeholder="Ask about your finances..." className="flex-1 bg-transparent text-white placeholder:text-zinc-500 focus:outline-none px-4 py-3 text-sm" />
                <button type="submit" disabled={!inputValue.trim() || isLoading} className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white rounded-full transition-all shrink-0">
                  {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}


export default function App() {
  const DEFAULT_USER_ID = users[0].id; 
  const DEFAULT_MODEL_ID = models[0].id;

  const [selectedUserId, setSelectedUserId] = useState(DEFAULT_USER_ID);
  const [selectedModelId, setSelectedModelId] = useState(DEFAULT_MODEL_ID);
  
  return (
    <CopilotKit 
      runtimeUrl="/api/copilotkit" 
      agent="bankbot" 
      properties={{ user_id: selectedUserId, model_name: selectedModelId }}
    >
      <PageContent 
        selectedUserId={selectedUserId} 
        setSelectedUserId={setSelectedUserId} 
        selectedModelId={selectedModelId} 
        setSelectedModelId={setSelectedModelId} 
      />
    </CopilotKit>
  );
}