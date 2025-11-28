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

// Component imports
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

interface Beneficiary {
  id: number;
  name: string;
  account: string;
  bank: string;
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

const DEFAULT_BENEFICIARIES: Beneficiary[] = [
  { id: 1, name: 'Sarah Wilson', account: '**** 4521', bank: 'Chase' },
  { id: 2, name: 'Mike Ross', account: '**** 8892', bank: 'BOA' },
  { id: 3, name: 'Jessica Pearson', account: '**** 1234', bank: 'Citi' },
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
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>(DEFAULT_BENEFICIARIES);
  
  // Local messages for components from frontend actions
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);

  // Use CopilotChat hook
  const { appendMessage, isLoading, visibleMessages } = useCopilotChat();

  // Build messages from visibleMessages + local messages
  const messages: ChatMessage[] = useMemo(() => {
    const result: ChatMessage[] = [
      { 
        id: 'init', 
        role: 'assistant', 
        content: "Hello! I'm your Banking Assistant. How can I help you today?", 
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
    description: "List of available beneficiaries for money transfers", 
    value: beneficiaries 
  });
  
  // --- COPILOT ACTIONS (Frontend Tools) ---
  // These are exposed to the LangGraph agent via CopilotKit
  useCopilotAction({ 
    name: "showBeneficiaries", 
    description: "Display the list of beneficiaries that the user can transfer money to. Call this when user wants to SEE or VIEW their beneficiaries.", 
    parameters: [],
    handler: async () => {
      console.log("🎯 showBeneficiaries handler called!");
      addLocalMessage(
        'assistant', 
        "Here are your beneficiaries:", 
        <BeneficiaryManager beneficiaries={beneficiaries} setBeneficiaries={setBeneficiaries} />
      );
      return "Displayed beneficiaries list to the user";
    }
  });
  
  useCopilotAction({ 
    name: "transferMoney", 
    description: "Show the money transfer form to allow user to send money. Call this when user wants to make a transfer.", 
    parameters: [],
    handler: async () => {
      console.log("🎯 transferMoney handler called!");
      addLocalMessage(
        'assistant', 
        "Here's the transfer form:", 
        <TransferMoney beneficiaries={beneficiaries} />
      );
      return "Displayed transfer money form to the user";
    }
  });
  
  useCopilotAction({ 
    name: "showBalance", 
    description: "Show the user's current account balance with a visual UI component. ALWAYS call this when user asks to show, see, view, or display their balance.", 
    parameters: [],
    handler: async () => {
      console.log("🎯 showBalance handler called!");
      addLocalMessage(
        'assistant', 
        "Here is your current balance:", 
        <BalanceCard userId={selectedUserId} />
      );
      return "Displayed account balance to the user";
    }
  });
  
  useCopilotAction({ 
    name: "showSpending", 
    description: "Show spending analysis and breakdown chart. Call this when user wants to SEE or VIEW their spending.", 
    parameters: [],
    handler: async () => {
      console.log("🎯 showSpending handler called!");
      addLocalMessage(
        'assistant', 
        "Here is your spending breakdown:", 
        <SpendingChart />
      );
      return "Displayed spending analysis chart to the user";
    }
  });

  // Debug: Log visibleMessages
  React.useEffect(() => {
    console.log('visibleMessages:', visibleMessages);
  }, [visibleMessages]);

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

// --- APP ENTRY ---
export default function App() {
  const DEFAULT_USER_ID = users[0].id; 
  const DEFAULT_MODEL_ID = models[0].id;

  const [selectedUserId, setSelectedUserId] = useState(DEFAULT_USER_ID);
  const [selectedModelId, setSelectedModelId] = useState(DEFAULT_MODEL_ID);
  
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="bankbot" properties={{ user_id: selectedUserId, model: selectedModelId }}>
      <PageContent 
        selectedUserId={selectedUserId} 
        setSelectedUserId={setSelectedUserId} 
        selectedModelId={selectedModelId} 
        setSelectedModelId={setSelectedModelId} 
      />
    </CopilotKit>
  );
}