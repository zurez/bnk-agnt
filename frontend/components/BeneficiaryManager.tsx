import React, { useState } from "react";
import { Users, Trash2, Check, X, Plus, AlertCircle } from "lucide-react";

// Shared Card component
const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
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

interface BeneficiaryManagerProps {
  beneficiaries: Beneficiary[];
  setBeneficiaries: React.Dispatch<React.SetStateAction<Beneficiary[]>>;
}

export const BeneficiaryManager = ({ beneficiaries, setBeneficiaries }: BeneficiaryManagerProps) => {
  const [view, setView] = useState<'list' | 'add' | 'confirm-add'>('list');
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [newBen, setNewBen] = useState({ name: '', bank: '', account: '' });

  const handleDelete = (id: number) => {
    setBeneficiaries((prev) => prev.filter(b => b.id !== id));
    setDeleteId(null);
  };

  const handleAddSubmit = () => {
    if (newBen.name && newBen.bank) setView('confirm-add');
  };

  const confirmAdd = () => {
    setBeneficiaries((prev) => [...prev, { id: Date.now(), ...newBen }]);
    setNewBen({ name: '', bank: '', account: '' });
    setView('list');
  };

  return (
    <Card className="p-0 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
        <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
          <Users size={16} className="text-orange-400" />
          {view === 'list' ? 'Beneficiaries' : 'Add New Contact'}
        </h3>
        {view === 'list' && (
          <button 
            onClick={() => setView('add')}
            className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-md transition-colors flex items-center gap-1"
          >
            <Plus size={12} /> Add New
          </button>
        )}
        {view !== 'list' && (
          <button onClick={() => setView('list')} className="text-xs text-zinc-400 hover:text-white">Cancel</button>
        )}
      </div>

      {view === 'add' && (
        <div className="p-6 space-y-4">
           <div>
             <label className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Full Name</label>
             <input value={newBen.name} onChange={e => setNewBen({...newBen, name: e.target.value})} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 mt-1 text-sm text-white focus:border-blue-500 outline-none" placeholder="e.g. John Doe" />
           </div>
           <div>
             <label className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Bank Name</label>
             <input value={newBen.bank} onChange={e => setNewBen({...newBen, bank: e.target.value})} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 mt-1 text-sm text-white focus:border-blue-500 outline-none" placeholder="e.g. Chase Bank" />
           </div>
           <div>
             <label className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Account Number (Last 4)</label>
             <input value={newBen.account} onChange={e => setNewBen({...newBen, account: e.target.value})} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 mt-1 text-sm text-white focus:border-blue-500 outline-none" placeholder="e.g. **** 1234" />
           </div>
           <button onClick={handleAddSubmit} disabled={!newBen.name || !newBen.bank} className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-lg font-medium transition-colors mt-2">Review Details</button>
        </div>
      )}

      {view === 'confirm-add' && (
        <div className="p-6">
           <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-4 flex gap-3 items-start">
              <AlertCircle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-yellow-500 mb-1">Confirm New Contact</h4>
                <p className="text-xs text-yellow-200/70">Please verify details before adding.</p>
              </div>
           </div>
           <div className="bg-zinc-950 rounded-lg border border-zinc-800 p-4 space-y-3 mb-6">
              <div className="flex justify-between border-b border-zinc-800 pb-2"><span className="text-zinc-500 text-xs">Name</span><span className="text-zinc-200 text-sm font-medium">{newBen.name}</span></div>
              <div className="flex justify-between border-b border-zinc-800 pb-2"><span className="text-zinc-500 text-xs">Bank</span><span className="text-zinc-200 text-sm font-medium">{newBen.bank}</span></div>
              <div className="flex justify-between"><span className="text-zinc-500 text-xs">Account</span><span className="text-zinc-200 text-sm font-medium">{newBen.account}</span></div>
           </div>
           <div className="flex gap-3">
              <button onClick={() => setView('add')} className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 py-2.5 rounded-lg text-sm font-medium">Edit</button>
              <button onClick={confirmAdd} className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-lg text-sm font-medium">Confirm Add</button>
           </div>
        </div>
      )}

      {view === 'list' && (
        <div className="divide-y divide-zinc-800">
          {beneficiaries.map((b) => (
            <div key={b.id} className="p-4 flex items-center justify-between hover:bg-zinc-800/30 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-400">
                  <span className="font-semibold">{b.name.charAt(0)}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-200">{b.name}</p>
                  <p className="text-xs text-zinc-500">{b.bank} • {b.account}</p>
                </div>
              </div>
              {deleteId === b.id ? (
                <div className="flex items-center gap-2 animate-in slide-in-from-right-4 duration-200">
                  <span className="text-xs text-red-400 font-medium mr-1">Delete?</span>
                  <button onClick={() => handleDelete(b.id)} className="p-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-md transition-colors"><Check size={14} /></button>
                  <button onClick={() => setDeleteId(null)} className="p-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 rounded-md transition-colors"><X size={14} /></button>
                </div>
              ) : (
                <button onClick={() => setDeleteId(b.id)} className="p-2 text-zinc-600 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors"><Trash2 size={16} /></button>
              )}
            </div>
          ))}
          {beneficiaries.length === 0 && <div className="p-8 text-center text-zinc-500 text-xs">No beneficiaries found.</div>}
        </div>
      )}
    </Card>
  );
};
