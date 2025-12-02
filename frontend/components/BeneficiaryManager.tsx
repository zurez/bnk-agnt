import React, { useMemo } from "react";
import { Users, Building2, ArrowRightLeft, AlertCircle } from "lucide-react";

const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl ${className}`}>
    {children}
  </div>
);

// Backend returns this structure from get_beneficiaries
interface Beneficiary {
  id: string;
  nickname: string;
  account_number: string;
  bank_name: string;
  is_internal: boolean;
  beneficiary_name?: string;
}

interface BeneficiaryManagerProps {
  beneficiaries?: Beneficiary[] | string;
}

export const BeneficiaryManager = ({ beneficiaries }: BeneficiaryManagerProps) => {
  const beneficiaryList = useMemo(() => {

    
    if (!beneficiaries) {
      return [];
    }
    
    // Parse if string
    if (typeof beneficiaries === 'string') {
      try {
        const parsed = JSON.parse(beneficiaries);
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        console.error('Failed to parse beneficiaries:', e);
        return [];
      }
    }
    
    return Array.isArray(beneficiaries) ? beneficiaries : [];
  }, [beneficiaries]);

  if (beneficiaryList.length === 0) {
    return (
      <Card className="p-6 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
        <div className="flex items-center gap-3 text-yellow-500">
          <AlertCircle className="w-5 h-5" />
          <div>
            <p className="font-medium">No beneficiaries found</p>
            <p className="text-xs text-zinc-500 mt-1">
              Ask me to add a beneficiary to get started.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-0 max-w-md w-full animate-in fade-in zoom-in-95 duration-300 mx-auto md:mx-0">
      <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
        <h3 className="font-semibold text-zinc-100 flex items-center gap-2">
          <Users size={16} className="text-orange-400" />
          Beneficiaries
        </h3>
        <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-1 rounded-full">
          {beneficiaryList.length} saved
        </span>
      </div>

      <div className="divide-y divide-zinc-800">
        {beneficiaryList.map((b, index) => (
          <div 
            key={b.id || index} 
            className="p-4 flex items-center justify-between hover:bg-zinc-800/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                b.is_internal 
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' 
                  : 'bg-zinc-800 text-zinc-400'
              }`}>
                {b.is_internal ? (
                  <ArrowRightLeft size={16} />
                ) : (
                  <span className="font-semibold text-sm">
                    {(b.beneficiary_name || b.nickname || '?').charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-200">
                  {b.nickname || b.beneficiary_name || 'Unknown'}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  <Building2 size={10} className="text-zinc-600" />
                  <p className="text-xs text-zinc-500">
                    {b.bank_name || 'Unknown Bank'}
                  </p>
                </div>
                <p className="text-xs text-zinc-600 mt-0.5 font-mono">
                  {b.account_number || 'No account number'}
                </p>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-1">
              {b.is_internal && (
                <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full border border-blue-500/20">
                  Internal
                </span>
              )}
              {b.beneficiary_name && b.beneficiary_name !== b.nickname && (
                <span className="text-xs text-zinc-500">
                  {b.beneficiary_name}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-3 border-t border-zinc-800 bg-zinc-950/50">
        <p className="text-xs text-zinc-500 text-center">
          To add or remove beneficiaries, just ask me.
        </p>
      </div>
    </Card>
  );
};