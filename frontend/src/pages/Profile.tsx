import { useEffect, useMemo, useState } from 'react';
import { motion } from 'motion/react';
import { BadgeCheck, Camera, Trash2, UserCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { profileAPI, ProfileData } from '../services/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '');

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const imageUrl = useMemo(() => {
    const raw = profile?.profile_image_url || '';
    if (!raw) return '';
    if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
    return `${API_ORIGIN}${raw}`;
  }, [profile?.profile_image_url]);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await profileAPI.getProfile();
      setProfile(data);
      setMessage('');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Unable to load profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const onUpload = async (file?: File) => {
    if (!file) return;
    setUploading(true);
    setMessage('');
    try {
      await profileAPI.uploadProfilePicture(file);
      await loadProfile();
      setMessage('Profile picture updated.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Failed to upload profile picture.');
    } finally {
      setUploading(false);
    }
  };

  const onDeletePicture = async () => {
    setUploading(true);
    setMessage('');
    try {
      await profileAPI.deleteProfilePicture();
      await loadProfile();
      setMessage('Profile picture removed.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Failed to remove profile picture.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">My Profile</h1>
        <p className="text-neutral-500 mt-1">Manage your profile picture and identity verification status.</p>
      </div>

      <div className="bg-white border border-neutral-100 rounded-2xl p-6 space-y-6">
        {loading ? (
          <p className="text-sm text-neutral-500">Loading profile...</p>
        ) : (
          <>
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="w-24 h-24 rounded-full border border-neutral-200 bg-neutral-50 overflow-hidden flex items-center justify-center">
                {imageUrl ? (
                  <img src={imageUrl} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <UserCircle2 size={64} className="text-neutral-400" />
                )}
              </div>

              <div className="space-y-1">
                <h2 className="text-xl font-semibold text-neutral-900">{profile?.full_name || user?.full_name}</h2>
                <p className="text-sm text-neutral-500">{profile?.email || user?.email}</p>
                <p className="text-sm text-neutral-500 capitalize">{profile?.user_type || user?.user_type}</p>
                {profile?.kyc_verified ? (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <BadgeCheck size={14} /> KYC Verified
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                    KYC Pending
                  </span>
                )}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <label className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-neutral-300 text-sm font-medium cursor-pointer hover:bg-neutral-50">
                <Camera size={16} />
                {uploading ? 'Uploading...' : 'Upload Picture'}
                <input
                  type="file"
                  className="hidden"
                  accept="image/png,image/jpeg,image/webp"
                  disabled={uploading}
                  onChange={(e) => onUpload(e.target.files?.[0])}
                />
              </label>

              <button
                type="button"
                onClick={onDeletePicture}
                disabled={uploading || !profile?.profile_image_url}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-red-200 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                <Trash2 size={16} /> Remove Picture
              </button>
            </div>

            {message && (
              <div className="rounded-xl bg-neutral-50 border border-neutral-200 p-3 text-sm text-neutral-700">
                {message}
              </div>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}

