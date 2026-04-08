import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Fingerprint, UploadCloud, CheckCircle2 } from 'lucide-react';
import { kycAPI, workflowAPI } from '../services/api';

export default function KycVerification() {
  const [cases, setCases] = useState<any[]>([]);
  const [selectedLoanId, setSelectedLoanId] = useState('');
  const [docType, setDocType] = useState('pan');
  const [docNumber, setDocNumber] = useState('');
  const [docFile, setDocFile] = useState<File | null>(null);
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    workflowAPI
      .myCases()
      .then((res) => {
        const list = res?.cases || [];
        setCases(list);
        if (list.length > 0) {
          setSelectedLoanId(String(list[0]._id));
        }
      })
      .catch(() => {
        setCases([]);
      });
  }, []);

  const submitKyc = async () => {
    if (!selectedLoanId || !docFile || !selfieFile) {
      setMessage('Select a loan and upload both document + selfie.');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      await kycAPI.uploadDocument(selectedLoanId, docType, docNumber, docFile);
      await kycAPI.uploadSelfie(selectedLoanId, selfieFile);
      await kycAPI.verifyLiveness(selectedLoanId, 0.8, 0.85);
      setMessage('KYC submitted successfully.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'KYC submission failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">KYC Verification</h1>
        <p className="text-neutral-500 mt-1">Upload PAN/Aadhaar/Passport and selfie for identity verification.</p>
      </div>

      <div className="bg-white border border-neutral-100 rounded-2xl p-6 space-y-4">
        <label className="block text-sm font-medium text-neutral-700">Loan Case</label>
        <select
          value={selectedLoanId}
          onChange={(e) => setSelectedLoanId(e.target.value)}
          className="w-full px-4 py-3 rounded-xl border border-neutral-200"
        >
          {cases.map((c) => (
            <option key={c._id} value={c._id}>
              {c.loan_purpose || 'Loan'} - {c._id}
            </option>
          ))}
        </select>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Document Type</label>
            <select value={docType} onChange={(e) => setDocType(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-neutral-200">
              <option value="pan">PAN</option>
              <option value="aadhaar">Aadhaar</option>
              <option value="passport">Passport</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Document Number</label>
            <input
              value={docNumber}
              onChange={(e) => setDocNumber(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-neutral-200"
              placeholder="Enter number"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="border-2 border-dashed border-neutral-200 rounded-xl p-4 text-center cursor-pointer">
            <UploadCloud className="mx-auto mb-2 text-neutral-500" size={20} />
            <span className="text-sm text-neutral-600">{docFile ? docFile.name : 'Upload KYC Document'}</span>
            <input type="file" className="hidden" onChange={(e) => setDocFile(e.target.files?.[0] || null)} />
          </label>

          <label className="border-2 border-dashed border-neutral-200 rounded-xl p-4 text-center cursor-pointer">
            <Fingerprint className="mx-auto mb-2 text-neutral-500" size={20} />
            <span className="text-sm text-neutral-600">{selfieFile ? selfieFile.name : 'Upload Selfie'}</span>
            <input type="file" className="hidden" onChange={(e) => setSelfieFile(e.target.files?.[0] || null)} />
          </label>
        </div>

        <button
          onClick={submitKyc}
          disabled={loading}
          className="w-full bg-neutral-900 text-white py-3 rounded-xl font-medium hover:bg-neutral-800 disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit KYC'}
        </button>

        {message && (
          <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-700 flex items-center gap-2">
            <CheckCircle2 size={16} /> {message}
          </div>
        )}
      </div>
    </motion.div>
  );
}

