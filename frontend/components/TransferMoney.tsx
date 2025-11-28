import React, { useState } from "react";
import { ArrowRightLeft, ChevronDown, Check } from "lucide-react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className = "" }: CardProps) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

interface Beneficiary {
  id: number;
  name: string;
  account: string;
  bank: string;
}

interface TransferMoneyProps {
  beneficiaries: Beneficiary[];
}

export const TransferMoney = ({ beneficiaries }: TransferMoneyProps) => {
  const [step, setStep] = useState<'input' | 'confirm' | 'processing' | 'success'>('input');
  const [formData, setFormData] = useState({ recipientId: '', amount: '' });

  const handleReview = (e: React.FormEvent) => {
    e.preventDefault();
    if(formData.recipientId && formData.amount) setStep('confirm');
  };

  const handleConfirm = () => {
    setStep('processing');
    setTimeout(() => setStep('success'), 2000);
  };

  const reset = () => {
    setFormData({ recipientId: '', amount: '' });
    setStep('input');
  };

  const recipientName = beneficiaries.find(b => b.id.toString() === formData.recipientId)?.name || 'Unknown Recipient';

  return (
    <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <h3 className="font-semibold text-zinc-100 mb-6 flex items-center gap-2">
        <ArrowRightLeft className={`w-5 h-5 ${step === 'success' ? 'text-green-500' : 'text-blue-500'}`} />
        {step === 'input' ? 'Transfer Money' : step === 'success' ? 'Transfer Successful' : 'Confirm Transfer'}
      </h3>

      {step === 'input' && (
        <form onSubmit={handleReview} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide">Recipient</label>
            <div className="relative">
              <select 
                value={formData.recipientId} 
                onChange={(e) => setFormData({...formData, recipientId: e.target.value})} 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 pl-3 text-sm text-zinc-300 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none"
              >
                <option value="">Select a beneficiary</option>
                {beneficiaries.map(b => (
                  <option key={b.id} value={b.id}>{b.name} ({b.bank})</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3.5 text-zinc-500 pointer-events-none" size={14} />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wide">Amount (USD)</label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-zinc-500">$</span>
              <input 
                type="number" 
                value={formData.amount} 
                onChange={(e) => setFormData({...formData, amount: e.target.value})} 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 pl-7 text-sm text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none placeholder:text-zinc-600" 
                placeholder="0.00" 
              />
            </div>
          </div>
          <button 
            type="submit" 
            disabled={!formData.amount || !formData.recipientId} 
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition-all mt-4"
          >
            Review Transfer
          </button>
        </form>
      )}

      {step === 'confirm' && (
        <div className="space-y-6 animate-in zoom-in-95 duration-200">
           <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-zinc-500 text-xs uppercase tracking-wide">To</span>
                <div className="text-right">
                  <p className="text-white font-medium text-sm">{recipientName}</p>
                  <p className="text-zinc-500 text-xs">**** 4521</p>
                </div>
              </div>
              <div className="h-px bg-zinc-800 w-full"></div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500 text-xs uppercase tracking-wide">Amount</span>
                <p className="text-2xl font-bold text-white">${formData.amount}</p>
              </div>
              <div className="flex justify-between items-center bg-blue-500/10 p-2 rounded-lg border border-blue-500/20">
                <span className="text-blue-400 text-xs">Fee</span>
                <span className="text-blue-400 text-xs font-medium">$0.00</span>
              </div>
           </div>
           <div className="flex gap-3">
              <button 
                onClick={() => setStep('input')} 
                className="flex-1 py-3 rounded-lg border border-zinc-700 text-zinc-300 hover:bg-zinc-800 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
              <button 
                onClick={handleConfirm} 
                className="flex-[2] py-3 rounded-lg bg-green-600 hover:bg-green-500 text-white shadow-lg shadow-green-900/20 transition-all text-sm font-medium flex items-center justify-center gap-2"
              >
                Confirm & Send <ArrowRightLeft size={16} />
              </button>
           </div>
        </div>
      )}

      {(step === 'processing' || step === 'success') && (
        <div className="flex flex-col items-center justify-center py-8 text-center animate-in fade-in duration-300">
          {step === 'processing' ? (
             <div className="relative">
               <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-4"></div>
               <div className="absolute inset-0 flex items-center justify-center">
                 <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
               </div>
             </div>
          ) : (
             <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mb-4 border border-green-500/20 animate-in zoom-in duration-300">
               <Check size={32} />
             </div>
          )}
          <h4 className="text-white font-medium text-lg mb-1">
            {step === 'processing' ? 'Processing...' : 'Transfer Sent!'}
          </h4>
          <p className="text-zinc-500 text-sm max-w-[200px]">
            {step === 'processing' 
              ? 'Securely communicating with the bank servers.' 
              : `You successfully sent $${formData.amount} to ${recipientName}.`
            }
          </p>
          {step === 'success' && (
            <button 
              onClick={reset} 
              className="mt-6 text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              Make another transfer
            </button>
          )}
        </div>
      )}
    </Card>
  );
};
