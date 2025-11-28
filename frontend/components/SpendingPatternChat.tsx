"use client";

import React from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import { MessageSquare } from "lucide-react";
import { Thinking } from "./Thinking";

export function SpendingPatternChat() {
  return (
    <div className="h-full flex flex-col bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="flex-1 overflow-hidden">
        <CopilotChat
          className="h-full [&_.copilot-kit-branding]:hidden"
          instructions="You are a helpful banking assistant that can help users with their finances. You can show balances, transfer money, and analyze spending patterns. Be friendly and professional."
          labels={{
            title: "Banking Assistant",
            initial: "👋 Hi! I'm your AI banking assistant. I can help you:\n\n• Check your account balance\n• Transfer money between accounts\n• Analyze your spending patterns\n• Answer questions about your finances\n\nWhat would you like to do today?",
          }}
          markdownTagRenderers={{
            think: Thinking,
          }}
        />
      </div>
    </div>
  );
}
