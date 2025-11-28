"use client";

import React from "react";
import { User } from "lucide-react";

export const users = [
  { id: "usr_01", name: "Alice Chen", avatar: "A", balance: 124592.45 },
  { id: "usr_02", name: "Bob Smith", avatar: "B", balance: 89341.20 },
  { id: "usr_03", name: "Carol Ali", avatar: "C", balance: 2000 },
];

interface UserSelectorProps {
  selectedUserId: string;
  onUserSelect: (userId: string) => void;
}

export function UserSelector({ selectedUserId, onUserSelect }: UserSelectorProps) {
  return (
    <div className="flex items-center gap-2 bg-zinc-900/50 px-3 py-2 rounded-lg border border-zinc-800/50 hover:border-zinc-700 transition-colors shadow-sm">
      <User className="w-4 h-4 text-zinc-500 shrink-0" />
      <select
        id="user-select"
        value={selectedUserId}
        onChange={(e) => onUserSelect(e.target.value)}
        className="bg-transparent text-sm font-medium text-zinc-300 focus:outline-none cursor-pointer hover:text-zinc-100 [&>option]:bg-zinc-900 [&>option]:text-zinc-300 min-w-[120px]"
      >
        {users.map((user) => (
          <option key={user.id} value={user.id}>
            {user.name}
          </option>
        ))}
      </select>
    </div>
  );
}
