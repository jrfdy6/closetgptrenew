'use client';

import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import SavedOutfitView from '@/components/outfits/SavedOutfitView';
import { useFirebase } from '@/lib/firebase-context';

export default function SavedOutfitPage({ params }: { params: { id: string } }) {
  const { user, loading } = useFirebase();
  return <div className="min-h-screen bg-background"><Navigation /><main className="mx-auto max-w-6xl px-4 py-6 pb-28 sm:px-6 sm:py-10"><SavedOutfitView id={params.id} user={user} authLoading={loading} /></main><ClientOnlyNav /></div>;
}
