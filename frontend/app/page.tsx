"use client";

import React, { useState, useCallback, useMemo, useEffect } from 'react';
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
import { AddBeneficiaryForm } from '../components/AddBeneficiaryForm';

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

function stripThinkingTags(content: string): string {
  if (!content) return content;
  return content
    .replace(/<think>[\s\S]*?<\/think>/gi, '')
    .replace(/<think>[\s\S]*/gi, '') // unclosed tags
    .replace(/^\s+|\s+$/g, '')
    .replace(/\n{3,}/g, '\n\n');
}

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

  // Add this useEffect to debug streaming messages
  useEffect(() => {
    console.log('=== VISIBLE MESSAGES UPDATE ===');
    console.log('Count:', visibleMessages?.length);
    visibleMessages?.forEach((msg: any, i: number) => {
      console.log(`[${i}] Type: ${msg?.type}, Content length: ${msg?.content?.length || 0}`);
    });
  }, [visibleMessages]);

  // Build messages from visibleMessages + local messages
  const messages: ChatMessage[] = useMemo(() => {
    const result: ChatMessage[] = [];
    const seenIds = new Set<string>();
    const rawMessages = visibleMessages as any[];
    
    // Track which local messages we've inserted
    const insertedLocalIds = new Set<string>();

    // Show initial greeting only if there are no messages yet
    if (!rawMessages || rawMessages.length === 0) {
      result.push({
        id: 'init',
        role: 'assistant',
        content: "Hello! I'm your Phoenix Digital Bank Assistant. How can I help you today?",
        timestamp: new Date(0)
      });
    }

    // Process API messages in their natural order
    for (const msg of rawMessages) {
      // Handle TextMessage
      if (msg?.type === 'TextMessage' && msg?.content && !seenIds.has(msg.id)) {
        seenIds.add(msg.id);
        
        let content = stripThinkingTags(msg.content);
        if (content) {
          result.push({
            id: msg.id,
            role: msg.role === 'user' ? 'user' : 'assistant',
            content,
            timestamp: new Date(msg.createdAt || Date.now()),
          });
        }
      }
      
      // Handle AgentStateMessage - check for local messages to insert after tool calls
      if (msg?.type === 'AgentStateMessage') {
        // Process state messages for content
        if (msg?.state?.messages) {
          for (const stateMsg of msg.state.messages) {
            if (!stateMsg.content || seenIds.has(stateMsg.id)) continue;
            if (stateMsg.role !== 'user' && stateMsg.role !== 'assistant') continue;
            if (stateMsg.name || stateMsg.tool_calls?.length) continue; // Skip tool messages
            
            seenIds.add(stateMsg.id);
            
            let content = stripThinkingTags(stateMsg.content);
            if (content) {
              result.push({
                id: stateMsg.id,
                role: stateMsg.role as 'user' | 'assistant',
                content,
                timestamp: new Date(msg.createdAt || Date.now()),
              });
            }
          }
        }
        
        // Insert any pending local messages that were triggered by this state
        localMessages.forEach((lm) => {
          if (!insertedLocalIds.has(lm.id) && !seenIds.has(lm.id)) {
            insertedLocalIds.add(lm.id);
            seenIds.add(lm.id);
            result.push(lm);
          }
        });
      }
    }

    // Add any remaining local messages at the end
    localMessages.forEach((lm) => {
      if (!seenIds.has(lm.id)) {
        result.push(lm);
      }
    });

    // DO NOT SORT - maintain insertion order
    return result;
  }, [visibleMessages, localMessages]);

  // Add local message helper
  const addLocalMessage = useCallback((role: 'user' | 'assistant', content: string, component?: React.ReactNode) => {
    const id = `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setLocalMessages(prev => [
      ...prev,
      {
        id,
        role,
        content,
        timestamp: new Date(), // Use current time
        component,
      }
    ]);
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
    description: "Display beneficiaries list UI. Call this after get_beneficiaries to show the data.", 
    parameters: [
      { 
        name: "beneficiaries", 
        type: "object[]" as const, 
        description: "Array of beneficiary objects from get_beneficiaries.",
        required: false
      }
    ],
    handler: async ({ beneficiaries }: { beneficiaries?: any[] | string }) => {
      console.log('showBeneficiaries called with:', beneficiaries, typeof beneficiaries);
      
      let benData: any[] = [];
      
      // Handle string (possibly double-encoded)
      if (typeof beneficiaries === 'string') {
        try {
          let parsed = JSON.parse(beneficiaries);
          // Handle double-encoding
          if (typeof parsed === 'string') {
            parsed = JSON.parse(parsed);
          }
          benData = Array.isArray(parsed) ? parsed : [];
        } catch (e) {
          console.error('Parse error:', e);
          benData = cachedBeneficiaries; // fallback to cache
        }
      } else if (Array.isArray(beneficiaries)) {
        benData = beneficiaries;
      }
      
      // Fallback to cache if empty
      if (benData.length === 0) benData = cachedBeneficiaries;
      
      // Update cache
      if (benData.length > 0) {
        setCachedBeneficiaries(benData);
      }
      
      
      addLocalMessage(
        'assistant', 
        "Here are your saved beneficiaries:", 
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

 // Replace the showTransferForm useCopilotAction in page.tsx with this:

useCopilotAction({ 
  name: "showTransferForm", 
  description: "Display transfer money form. Call this after fetching accounts and beneficiaries.", 
  parameters: [
    { name: "accounts", type: "object[]" as const, description: "Array of account objects from get_balance.", required: false },
    { name: "beneficiaries", type: "object[]" as const, description: "Array of beneficiary objects from get_beneficiaries.", required: false }
  ],
  handler: async ({ accounts, beneficiaries }: { accounts?: any[] | string; beneficiaries?: any[] | string }) => {
    // Parse accounts
    let acctData: any[] = [];
    if (typeof accounts === 'string') {
      try { acctData = JSON.parse(accounts); } catch (e) { console.error('Parse error:', e); }
    } else if (Array.isArray(accounts)) {
      acctData = accounts;
    }
    
    // Parse beneficiaries
    let benData: any[] = [];
    if (typeof beneficiaries === 'string') {
      try { benData = JSON.parse(beneficiaries); } catch (e) { console.error('Parse error:', e); }
    } else if (Array.isArray(beneficiaries)) {
      benData = beneficiaries;
    }
    
    // Fallback to cache
    if (acctData.length === 0) acctData = cachedAccounts;
    if (benData.length === 0) benData = cachedBeneficiaries;
    
    // Update cache
    if (acctData.length > 0) setCachedAccounts(acctData);
    if (benData.length > 0) setCachedBeneficiaries(benData);
    
    // Callback to send message to agent
    const handleSendMessage = (message: string) => {
      appendMessage(new TextMessage({ role: Role.User, content: message }));
    };
    
    // Use timestamp as key to force re-mount and reset state after proposal
    const transferFormKey = `transfer-${Date.now()}`;
    
    addLocalMessage(
      'assistant', 
      "Here's the transfer form. Fill in the details and click 'Propose Transfer':", 
      <TransferMoney 
        key={transferFormKey}
        accounts={acctData} 
        beneficiaries={benData} 
        userId={selectedUserId}
        onSendMessage={handleSendMessage}
      />
    );
    return "Displayed transfer form to user";
  }
});

// Also update showPendingTransfers to include approve/reject buttons:
useCopilotAction({ 
  name: "showPendingTransfers", 
  description: "Display pending transfers that need approval.", 
  parameters: [
    { name: "transfers", type: "object[]" as const, description: "Array of pending transfer objects", required: false }
  ],
  handler: async ({ transfers }: { transfers?: any[] | string }) => {
    let transferList: any[] = [];
    if (typeof transfers === 'string') {
      try { transferList = JSON.parse(transfers); } catch (e) { console.error('Parse error:', e); }
    } else if (Array.isArray(transfers)) {
      transferList = transfers;
    }
    
    if (transferList.length === 0) {
      addLocalMessage('assistant', "You have no pending transfers awaiting approval.");
      return "No pending transfers";
    }
    
    const handleApprove = (transferId: string) => {
      appendMessage(new TextMessage({ role: Role.User, content: `Approve transfer ${transferId}` }));
    };
    
    const handleReject = (transferId: string) => {
      appendMessage(new TextMessage({ role: Role.User, content: `Reject transfer ${transferId}` }));
    };
    
    const PendingTransfersUI = () => (
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden max-w-md">
        <div className="p-4 border-b border-zinc-800 bg-yellow-500/10">
          <h3 className="font-semibold text-yellow-400">Pending Transfers ({transferList.length})</h3>
        </div>
        <div className="divide-y divide-zinc-800">
          {transferList.map((t: any) => (
            <div key={t.id} className="p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-white font-medium">{t.amount} {t.currency || 'AED'}</p>
                  <p className="text-xs text-zinc-500">{t.from_account} → {t.to_destination}</p>
                </div>
                <span className="text-xs text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded">Pending</span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleReject(t.id)} className="flex-1 py-2 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 text-xs font-medium">
                  Reject
                </button>
                <button onClick={() => handleApprove(t.id)} className="flex-1 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-xs font-medium">
                  Approve
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
    
    addLocalMessage('assistant', `You have ${transferList.length} pending transfer(s):`, <PendingTransfersUI />);
    return "Displayed pending transfers";
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

  useCopilotAction({
    name: "showAddBeneficiaryForm",
    description: "Display form to add a new beneficiary. Call this when user wants to add a beneficiary.",
    parameters: [],
    handler: async () => {
      const handleSendMessage = (message: string) => {
        appendMessage(new TextMessage({ role: Role.User, content: message }));
      };

      addLocalMessage(
        'assistant',
        "Here's the form to add a new beneficiary:",
        <AddBeneficiaryForm 
          onSendMessage={handleSendMessage}
          currentUserId={selectedUserId}
        />
      );
      return "Displayed add beneficiary form to user";
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
<div className="absolute right-0 top-full pt-1 w-48 z-50 hidden group-hover:block">
  <div className="bg-zinc-950 border border-zinc-800 rounded-lg shadow-xl overflow-hidden animate-in fade-in slide-in-from-top-1">                    {models.map(m => (
                      <button key={m.id} onClick={() => setSelectedModelId(m.id)} className={`w-full text-left px-3 py-2 text-xs flex items-center gap-2 hover:bg-zinc-900 transition-colors ${selectedModelId === m.id ? 'text-white bg-zinc-900' : 'text-zinc-400'}`}>
                        <Bot size={14} className={selectedModelId === m.id ? 'text-blue-500' : 'text-zinc-600'} />
                        {m.name}
                        {selectedModelId === m.id && <Check size={12} className="ml-auto text-blue-500" />}
                      </button>
                    ))}
                  </div>
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
      key={`${selectedUserId}-${selectedModelId}`}
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