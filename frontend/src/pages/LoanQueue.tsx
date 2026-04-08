import { useEffect, useMemo, useState } from 'react';
import { motion } from 'motion/react';
import { workflowAPI } from '../services/api';

export default function LoanQueue() {
  const [cases, setCases] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [decisionReason, setDecisionReason] = useState('');
  const [overrideReason, setOverrideReason] = useState('');
  const [message, setMessage] = useState('');

  const refreshCases = () => {
    workflowAPI
      .myCases()
      .then((res) => {
        const list = res?.cases || [];
        setCases(list);
        if (!selected && list.length > 0) {
          setSelected(list[0]);
        }
      })
      .catch(() => setCases([]));
  };

  useEffect(() => {
    refreshCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentStatus = useMemo(() => String(selected?.status || 'submitted').toLowerCase(), [selected]);

  const transition = async (toStatus: string) => {
    if (!selected?._id) return;
    try {
      await workflowAPI.transition(selected._id, toStatus, `Transitioned to ${toStatus}`);
      setMessage(`Status changed to ${toStatus}`);
      refreshCases();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Transition failed');
    }
  };

  const decide = async (decision: 'approved' | 'rejected') => {
    if (!selected?._id || !decisionReason.trim()) {
      setMessage('Decision reason is required.');
      return;
    }
    try {
      await workflowAPI.decide(selected._id, decision, decisionReason.trim());
      setMessage(`Decision marked as ${decision}`);
      setDecisionReason('');
      refreshCases();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Decision update failed');
    }
  };

  const override = async (toDecision: 'approved' | 'rejected') => {
    if (!selected?._id || overrideReason.trim().length < 8) {
      setMessage('Override reason must be at least 8 characters.');
      return;
    }

    const fromDecision = String(selected?.final_decision || selected?.ai_decision || currentStatus || 'rejected').toLowerCase();
    try {
      await workflowAPI.overrideDecision(selected._id, fromDecision, toDecision, overrideReason.trim());
      setMessage(`Decision overridden to ${toDecision}`);
      setOverrideReason('');
      refreshCases();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Override failed');
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">Loan Review Queue</h1>
        <p className="text-neutral-500 mt-1">Underwriter/Risk Manager workflow with final decisions and overrides.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl border border-neutral-100 p-4 space-y-2 max-h-[70vh] overflow-auto">
          {cases.map((c) => (
            <button
              key={c._id}
              onClick={() => setSelected(c)}
              className={`w-full text-left p-3 rounded-xl border ${selected?._id === c._id ? 'border-neutral-900 bg-neutral-50' : 'border-neutral-200'}`}
            >
              <p className="font-medium text-sm">{c.loan_purpose || 'Loan Case'}</p>
              <p className="text-xs text-neutral-500">Status: {String(c.status || 'submitted')}</p>
              <p className="text-xs text-neutral-500">Amount: {c.loan_amount || 0}</p>
            </button>
          ))}
          {cases.length === 0 && <p className="text-sm text-neutral-500 p-3">No cases found.</p>}
        </div>

        <div className="lg:col-span-2 bg-white rounded-2xl border border-neutral-100 p-6 space-y-4">
          {!selected && <p className="text-sm text-neutral-500">Select a loan case.</p>}
          {selected && (
            <>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-neutral-500">Loan ID</p>
                  <p className="font-mono text-xs break-all">{selected._id}</p>
                </div>
                <div>
                  <p className="text-neutral-500">Current Status</p>
                  <p className="font-semibold capitalize">{String(selected.status || 'submitted')}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button onClick={() => transition('under_review')} className="px-3 py-2 rounded-lg bg-neutral-100 text-sm">Move to Under Review</button>
                <button onClick={() => transition('disbursed')} className="px-3 py-2 rounded-lg bg-blue-100 text-blue-700 text-sm">Mark Disbursed</button>
                <button onClick={() => transition('closed')} className="px-3 py-2 rounded-lg bg-emerald-100 text-emerald-700 text-sm">Mark Closed</button>
                <button onClick={() => transition('defaulted')} className="px-3 py-2 rounded-lg bg-rose-100 text-rose-700 text-sm">Mark Defaulted</button>
              </div>

              <div className="space-y-2 pt-2">
                <label className="text-sm font-medium">Decision Reason (required)</label>
                <textarea
                  value={decisionReason}
                  onChange={(e) => setDecisionReason(e.target.value)}
                  className="w-full border border-neutral-200 rounded-xl p-3 text-sm"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button onClick={() => decide('approved')} className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm">Approve</button>
                  <button onClick={() => decide('rejected')} className="px-4 py-2 rounded-lg bg-rose-600 text-white text-sm">Reject</button>
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-neutral-100">
                <label className="text-sm font-medium">Override Reason (min 8 chars, mandatory)</label>
                <textarea
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="w-full border border-neutral-200 rounded-xl p-3 text-sm"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button onClick={() => override('approved')} className="px-4 py-2 rounded-lg bg-emerald-100 text-emerald-700 text-sm">Override to Approved</button>
                  <button onClick={() => override('rejected')} className="px-4 py-2 rounded-lg bg-rose-100 text-rose-700 text-sm">Override to Rejected</button>
                </div>
              </div>
            </>
          )}

          {message && <p className="text-sm text-indigo-600">{message}</p>}
        </div>
      </div>
    </motion.div>
  );
}

