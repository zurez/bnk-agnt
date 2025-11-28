import React, { useRef, useEffect } from "react";
import { Sparkles, Loader2 } from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  component?: React.ReactNode;
}

interface BankingChatProps {
  messages: Message[];
  isTyping: boolean;
  thinkingStep: string;
  onSend?: any;
}

export const BankingChat = ({ messages, isTyping, thinkingStep, onSend }: BankingChatProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isTyping, thinkingStep]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-32 scrollbar-hide">
      {messages.map((m: any) => (
        <div key={m.id} className={`flex gap-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}>
          {m.role === 'assistant' && (
            <div className="w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center shrink-0 mt-1">
              <Sparkles size={14} className="text-blue-500" />
            </div>
          )}
          <div className={`flex flex-col gap-2 max-w-[90%] md:max-w-[75%]`}>
            {m.content && (
              <div className={`rounded-2xl px-5 py-3 shadow-sm ${m.role === 'user' ? 'bg-blue-600 text-white rounded-br-sm' : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-bl-sm'}`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.content}</p>
                <p className={`text-[10px] mt-1.5 opacity-50 ${m.role === 'user' ? 'text-blue-200' : 'text-zinc-500'}`}>{m.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
              </div>
            )}
            {m.component && <div className="mt-1">{m.component}</div>}
          </div>
        </div>
      ))}
      
      {isTyping && (
        <div className="flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 ml-1">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800"><Loader2 className="w-4 h-4 text-blue-500 animate-spin" /></div>
          <span className="text-xs font-medium text-zinc-400 animate-pulse">{thinkingStep}</span>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};
