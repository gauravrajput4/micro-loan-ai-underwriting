import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { auditAPI } from '../services/api';

export default function AuditViewer() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    auditAPI
      .listEvents(200)
      .then((res) => {
        setEvents(res?.events || []);
        setError('');
      })
      .catch((err) => {
        setError(err?.response?.data?.detail || 'Unable to load audit events');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">Tamper-Evident Audit Logs</h1>
        <p className="text-neutral-500 mt-1">Each event stores `prev_hash` + `event_hash` chain for integrity checks.</p>
      </div>

      {loading && <p className="text-sm text-neutral-500">Loading events...</p>}
      {error && <p className="text-sm text-rose-600">{error}</p>}

      {!loading && !error && (
        <div className="bg-white rounded-2xl border border-neutral-100 overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-4 py-3 text-left">Time</th>
                <th className="px-4 py-3 text-left">Action</th>
                <th className="px-4 py-3 text-left">Actor</th>
                <th className="px-4 py-3 text-left">Entity</th>
                <th className="px-4 py-3 text-left">Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {events.map((event) => (
                <tr key={event._id}>
                  <td className="px-4 py-3">{new Date(event.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">{event.action}</td>
                  <td className="px-4 py-3">{event.actor_email} ({event.actor_role})</td>
                  <td className="px-4 py-3">{event.entity_type}:{event.entity_id}</td>
                  <td className="px-4 py-3 font-mono text-xs max-w-[220px] truncate" title={event.event_hash}>{event.event_hash}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}

