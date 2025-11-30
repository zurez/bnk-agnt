import React, { useState } from "react";
import { UserPlus, ChevronDown, AlertCircle, Loader2, Send } from "lucide-react";

const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

const VALID_ACCOUNTS = [
  { number: "PDB-ALICE-001", name: "Alice Ahmed" },
  { number: "PDB-BOB-001", name: "Bob Mansour" },
  { number: "PDB-CAROL-001", name: "Carol Ali" },
];

interface AddBeneficiaryFormProps {
  onSendMessage?: (message: string) => void;
  currentUserId?: string;
}

export const AddBeneficiaryForm = ({ onSendMessage, currentUserId }: AddBeneficiaryFormProps) => {
  const [formData, setFormData] = useState({
    accountNumber: "",
    nickname: ""
  });
  const [submitted, setSubmitted] = useState(false);

  const selectedAccount = VALID_ACCOUNTS.find(a => a.number === formData.accountNumber);
  
  const isValid = formData.accountNumber && formData.nickname.trim().length > 0;

  const handleSubmit = () => {
    if (!isValid || !onSendMessage) return;
    
    const message = `Add beneficiary: account_number="${formData.accountNumber}", nickname="${formData.nickname}"`;
    
    setSubmitted(true);
    onSendMessage(message);
  };

  if (submitted) {
    return (
      <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-blue-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <div>
            <p className="font-medium">Adding beneficiary...</p>
            <p className="text-xs text-zinc-500 mt-1">Please wait for confirmation</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-0 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/50">
        <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
          <UserPlus size={16} className="text-green-500" /> Add Beneficiary
        </h3>
      </div>

      <div className="p-4 space-y-4">
        <div>
          <label className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide block">
            Account Number
          </label>
          <div className="relative">
            <select
              value={formData.accountNumber}
              onChange={(e) => setFormData({ ...formData, accountNumber: e.target.value })}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-300 outline-none appearance-none"
            >
              <option value="">Select account</option>
              {VALID_ACCOUNTS.map((acc) => (
                <option key={acc.number} value={acc.number}>
                  {acc.number} ({acc.name})
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-3.5 text-zinc-500 pointer-events-none" size={14} />
          </div>
          {selectedAccount && (
            <p className="text-xs text-zinc-500 mt-1.5">
              Account holder: <span className="text-zinc-300">{selectedAccount.name}</span>
            </p>
          )}
        </div>

        <div>
          <label className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide block">
            Nickname
          </label>
          <input
            type="text"
            value={formData.nickname}
            onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-white outline-none placeholder:text-zinc-600"
            placeholder="e.g., Bob - Personal"
          />
          <p className="text-xs text-zinc-600 mt-1">A friendly name to identify this beneficiary</p>
        </div>

        <div className="bg-zinc-950/50 border border-zinc-800 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <AlertCircle size={14} className="text-yellow-500 mt-0.5 shrink-0" />
            <p className="text-xs text-zinc-400">
              Only Phoenix Digital Bank accounts can be added as beneficiaries.
            </p>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!isValid || !onSendMessage}
          className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
            isValid && onSendMessage
              ? "bg-green-600 hover:bg-green-500 text-white"
              : "bg-zinc-800 text-zinc-600 cursor-not-allowed"
          }`}
        >
          <Send size={16} /> Add Beneficiary
        </button>
      </div>
    </Card>
  );
};
