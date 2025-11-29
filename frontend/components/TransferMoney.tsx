import React, { useState, useMemo } from "react";
import { ArrowRightLeft, ChevronDown, AlertCircle, Wallet, Users, Send, Check, Loader2 } from "lucide-react";

const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

interface Account {
  id: string;
  name: string;
  type: string;
  balance: number;
  currency: string;
}

interface Beneficiary {
  id: string;
  nickname: string;
  account_number: string;
  bank_name: string;
  is_internal: boolean;
}

interface TransferMoneyProps {
  accounts?: Account[] | string;
  beneficiaries?: Beneficiary[] | string;
  userId: string;
  onSendMessage?: (message: string) => void;
}

export const TransferMoney = ({ accounts, beneficiaries, userId, onSendMessage }: TransferMoneyProps) => {
  const [formData, setFormData] = useState({
    fromAccountId: '',
    toType: 'beneficiary' as 'beneficiary' | 'own',
    toBeneficiaryId: '',
    toAccountId: '',
    amount: '',
    description: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const accountList: Account[] = useMemo(() => {
    if (!accounts) return [];
    if (typeof accounts === 'string') {
      try { return JSON.parse(accounts); } catch { return []; }
    }
    return Array.isArray(accounts) ? accounts : [];
  }, [accounts]);

  const beneficiaryList: Beneficiary[] = useMemo(() => {
    if (!beneficiaries) return [];
    if (typeof beneficiaries === 'string') {
      try { return JSON.parse(beneficiaries); } catch { return []; }
    }
    return Array.isArray(beneficiaries) ? beneficiaries : [];
  }, [beneficiaries]);

  const selectedFromAccount = accountList.find(a => a.id === formData.fromAccountId);
  const selectedBeneficiary = beneficiaryList.find(b => b.id === formData.toBeneficiaryId);
  const selectedToAccount = accountList.find(a => a.id === formData.toAccountId);
  const currency = selectedFromAccount?.currency || 'AED';

  const formatCurrency = (amount: number, curr: string = currency) => {
    return `${curr} ${amount.toLocaleString('en-AE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const amountNum = parseFloat(formData.amount) || 0;
  const hasInsufficientFunds = selectedFromAccount && amountNum > selectedFromAccount.balance;
  const isValidTransfer = formData.fromAccountId && 
    formData.amount && 
    amountNum > 0 &&
    !hasInsufficientFunds &&
    ((formData.toType === 'beneficiary' && formData.toBeneficiaryId) ||
     (formData.toType === 'own' && formData.toAccountId && formData.toAccountId !== formData.fromAccountId));

  const handlePropose = () => {
    if (!isValidTransfer || !onSendMessage) return;
    
    let message = '';
    if (formData.toType === 'beneficiary' && selectedBeneficiary) {
      message = `Propose transfer of ${formData.amount} ${currency} from "${selectedFromAccount?.name}" to beneficiary "${selectedBeneficiary.nickname}"`;
    } else if (formData.toType === 'own' && selectedToAccount) {
      message = `Propose internal transfer of ${formData.amount} ${currency} from "${selectedFromAccount?.name}" to "${selectedToAccount.name}"`;
    }
    
    if (formData.description) {
      message += ` with description "${formData.description}"`;
    }
    
    setSubmitted(true);
    onSendMessage(message);
  };

  if (accountList.length === 0) {
    return (
      <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-yellow-500">
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">No account data available</p>
        </div>
      </Card>
    );
  }

  if (submitted) {
    return (
      <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-blue-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <div>
            <p className="font-medium">Transfer proposal sent</p>
            <p className="text-xs text-zinc-500 mt-1">Waiting for confirmation...</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-0 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/50">
        <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
          <ArrowRightLeft size={16} className="text-blue-500" /> Transfer Money
        </h3>
      </div>

      <div className="p-4 space-y-4">
        {/* From Account */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide">
            <Wallet size={12} /> From Account
          </label>
          <div className="relative">
            <select 
              value={formData.fromAccountId} 
              onChange={(e) => setFormData({...formData, fromAccountId: e.target.value})}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-300 outline-none appearance-none"
            >
              <option value="">Select source account</option>
              {accountList.map((acc) => (
                <option key={acc.id} value={acc.id}>{acc.name} • {formatCurrency(acc.balance, acc.currency)}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-3.5 text-zinc-500 pointer-events-none" size={14} />
          </div>
          {selectedFromAccount && (
            <p className="text-xs text-zinc-600 mt-1">Available: {formatCurrency(selectedFromAccount.balance)}</p>
          )}
        </div>

        {/* Transfer Type */}
        <div>
          <label className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide block">Transfer To</label>
          <div className="flex gap-2">
            <button
              onClick={() => setFormData({...formData, toType: 'beneficiary', toAccountId: ''})}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1.5 ${
                formData.toType === 'beneficiary' ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
            >
              <Users size={12} /> Beneficiary
            </button>
            <button
              onClick={() => setFormData({...formData, toType: 'own', toBeneficiaryId: ''})}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1.5 ${
                formData.toType === 'own' ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
            >
              <Wallet size={12} /> Own Account
            </button>
          </div>
        </div>

        {/* To Beneficiary */}
        {formData.toType === 'beneficiary' && (
          <div>
            <label className="flex items-center gap-1.5 text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide">
              <Users size={12} /> Recipient
            </label>
            <div className="relative">
              <select 
                value={formData.toBeneficiaryId} 
                onChange={(e) => setFormData({...formData, toBeneficiaryId: e.target.value})}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-300 outline-none appearance-none"
              >
                <option value="">Select beneficiary</option>
                {beneficiaryList.map((ben) => (
                  <option key={ben.id} value={ben.id}>{ben.nickname} • {ben.bank_name}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3.5 text-zinc-500 pointer-events-none" size={14} />
            </div>
          </div>
        )}

        {/* To Own Account */}
        {formData.toType === 'own' && (
          <div>
            <label className="flex items-center gap-1.5 text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide">
              <Wallet size={12} /> Destination Account
            </label>
            <div className="relative">
              <select 
                value={formData.toAccountId} 
                onChange={(e) => setFormData({...formData, toAccountId: e.target.value})}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-300 outline-none appearance-none"
              >
                <option value="">Select destination account</option>
                {accountList.filter(acc => acc.id !== formData.fromAccountId).map((acc) => (
                  <option key={acc.id} value={acc.id}>{acc.name} • {formatCurrency(acc.balance, acc.currency)}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3.5 text-zinc-500 pointer-events-none" size={14} />
            </div>
          </div>
        )}

        {/* Amount */}
        <div>
          <label className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide block">Amount ({currency})</label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-zinc-500 text-sm">{currency}</span>
            <input 
              type="number" 
              value={formData.amount} 
              onChange={(e) => setFormData({...formData, amount: e.target.value})}
              className={`w-full bg-zinc-950 border rounded-lg p-3 pl-14 text-sm text-white outline-none placeholder:text-zinc-600 ${
                hasInsufficientFunds ? 'border-red-500' : 'border-zinc-800'
              }`}
              placeholder="0.00"
            />
          </div>
          {hasInsufficientFunds && (
            <p className="text-xs text-red-500 mt-1 flex items-center gap-1"><AlertCircle size={10} /> Insufficient funds</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide block">Description (Optional)</label>
          <input 
            type="text" 
            value={formData.description} 
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-white outline-none placeholder:text-zinc-600"
            placeholder="Payment for..."
          />
        </div>

        {/* Submit */}
        <button
          onClick={handlePropose}
          disabled={!isValidTransfer || !onSendMessage}
          className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
            isValidTransfer && onSendMessage
              ? 'bg-blue-600 hover:bg-blue-500 text-white'
              : 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
          }`}
        >
          <Send size={16} /> Propose Transfer
        </button>
      </div>
    </Card>
  );
};