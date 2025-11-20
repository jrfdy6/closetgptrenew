'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuthContext } from '@/contexts/AuthContext';
import { db } from '@/lib/firebase/config';
import { collection, query, where, getDocs, doc, updateDoc, onSnapshot } from 'firebase/firestore';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Image, RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';

interface Outfit {
  id: string;
  name?: string;
  items?: any[];
  flat_lay_status?: string;
  flatLayStatus?: string;
  flat_lay_url?: string;
  flatLayUrl?: string;
  flat_lay_error?: string;
  flatLayError?: string;
  flat_lay_requested?: boolean;
  flatLayRequested?: boolean;
  metadata?: {
    flat_lay_status?: string;
    flatLayStatus?: string;
    flat_lay_url?: string;
    flatLayUrl?: string;
    flat_lay_error?: string;
    flatLayError?: string;
    flat_lay_requested?: boolean;
    flatLayRequested?: boolean;
  };
}

export default function TestFlatLayPage() {
  const { user } = useAuthContext();
  const { toast } = useToast();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [selectedOutfit, setSelectedOutfit] = useState<Outfit | null>(null);
  const [loading, setLoading] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [polling, setPolling] = useState(false);

  // Fetch user's outfits
  const fetchOutfits = useCallback(async () => {
    if (!user?.uid) return;

    setLoading(true);
    try {
      const outfitsRef = collection(db, 'outfits');
      const q = query(outfitsRef, where('userId', '==', user.uid));
      const querySnapshot = await getDocs(q);
      
      const outfitsList: Outfit[] = [];
      querySnapshot.forEach((doc) => {
        outfitsList.push({
          id: doc.id,
          ...doc.data()
        } as Outfit);
      });

      // Sort by creation date (newest first)
      outfitsList.sort((a, b) => {
        const aDate = a.metadata?.createdAt || (a as any).createdAt || 0;
        const bDate = b.metadata?.createdAt || (b as any).createdAt || 0;
        return bDate - aDate;
      });

      setOutfits(outfitsList);
      console.log('✅ Fetched outfits:', outfitsList.length);
    } catch (error) {
      console.error('❌ Error fetching outfits:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch outfits',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [user, toast]);

  useEffect(() => {
    fetchOutfits();
  }, [fetchOutfits]);

  // Subscribe to outfit updates when one is selected
  useEffect(() => {
    if (!selectedOutfit?.id || !user?.uid) return;

    const outfitRef = doc(db, 'outfits', selectedOutfit.id);
    const unsubscribe = onSnapshot(outfitRef, (doc) => {
      if (doc.exists()) {
        const updatedOutfit = {
          id: doc.id,
          ...doc.data()
        } as Outfit;
        setSelectedOutfit(updatedOutfit);
        
        // Update in outfits list too
        setOutfits(prev => prev.map(o => o.id === updatedOutfit.id ? updatedOutfit : o));
      }
    });

    return () => unsubscribe();
  }, [selectedOutfit?.id, user?.uid]);

  // Request flatlay for selected outfit
  const handleRequestFlatLay = async () => {
    if (!selectedOutfit?.id || !user?.uid) {
      toast({
        title: 'Error',
        description: 'Please select an outfit first',
        variant: 'destructive'
      });
      return;
    }

    setRequesting(true);
    try {
      const outfitRef = doc(db, 'outfits', selectedOutfit.id);
      await updateDoc(outfitRef, {
        flat_lay_requested: true,
        flatLayRequested: true,
        'metadata.flat_lay_requested': true,
        'metadata.flatLayRequested': true,
        flat_lay_status: 'pending',
        flatLayStatus: 'pending',
        'metadata.flat_lay_status': 'pending',
        'metadata.flatLayStatus': 'pending',
        flat_lay_error: null,
        flatLayError: null,
        'metadata.flat_lay_error': null,
        'metadata.flatLayError': null,
        'metadata.flat_lay_worker': 'premium_v1',
        'metadata.flatLayWorker': 'premium_v1',
      });

      toast({
        title: 'Flat lay requested!',
        description: 'The worker will process your flat lay request. This page will update automatically.',
      });

      // Start polling for updates
      setPolling(true);
    } catch (error) {
      console.error('❌ Error requesting flat lay:', error);
      toast({
        title: 'Error',
        description: 'Failed to request flat lay',
        variant: 'destructive'
      });
    } finally {
      setRequesting(false);
    }
  };

  // Get flatlay status
  const getFlatLayStatus = (outfit: Outfit) => {
    return outfit.flat_lay_status || 
           outfit.flatLayStatus || 
           outfit.metadata?.flat_lay_status || 
           outfit.metadata?.flatLayStatus || 
           'awaiting_consent';
  };

  // Get flatlay URL
  const getFlatLayUrl = (outfit: Outfit) => {
    return outfit.flat_lay_url || 
           outfit.flatLayUrl || 
           outfit.metadata?.flat_lay_url || 
           outfit.metadata?.flatLayUrl || 
           null;
  };

  // Get flatlay error
  const getFlatLayError = (outfit: Outfit) => {
    return outfit.flat_lay_error || 
           outfit.flatLayError || 
           outfit.metadata?.flat_lay_error || 
           outfit.metadata?.flatLayError || 
           null;
  };

  // Check if flatlay is requested
  const isFlatLayRequested = (outfit: Outfit) => {
    return outfit.flat_lay_requested || 
           outfit.flatLayRequested || 
           outfit.metadata?.flat_lay_requested || 
           outfit.metadata?.flatLayRequested || 
           false;
  };

  const status = selectedOutfit ? getFlatLayStatus(selectedOutfit) : null;
  const flatLayUrl = selectedOutfit ? getFlatLayUrl(selectedOutfit) : null;
  const flatLayError = selectedOutfit ? getFlatLayError(selectedOutfit) : null;
  const isRequested = selectedOutfit ? isFlatLayRequested(selectedOutfit) : false;

  return (
    <div className="min-h-screen bg-background">
      <ClientOnlyNav />
      <Navigation />
      
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Flat Lay Pipeline Test</h1>
          <p className="text-muted-foreground">
            Test the flat lay generation pipeline. Select an outfit and request a flat lay.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Outfits List */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Your Outfits</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchOutfits}
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
              <CardDescription>
                {outfits.length} outfit{outfits.length !== 1 ? 's' : ''} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
              ) : outfits.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  No outfits found. Create an outfit first.
                </p>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {outfits.map((outfit) => {
                    const outfitStatus = getFlatLayStatus(outfit);
                    const outfitUrl = getFlatLayUrl(outfit);
                    const outfitError = getFlatLayError(outfit);
                    const outfitRequested = isFlatLayRequested(outfit);
                    const isSelected = selectedOutfit?.id === outfit.id;

                    return (
                      <div
                        key={outfit.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                          isSelected
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                        onClick={() => setSelectedOutfit(outfit)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold">
                              {outfit.name || `Outfit ${outfit.id.slice(0, 8)}`}
                            </h3>
                            <p className="text-sm text-muted-foreground mt-1">
                              {outfit.items?.length || 0} items
                            </p>
                            <div className="flex gap-2 mt-2">
                              <Badge variant="outline">
                                {outfitStatus}
                              </Badge>
                              {outfitRequested && (
                                <Badge variant="secondary">Requested</Badge>
                              )}
                              {outfitUrl && (
                                <Badge variant="default" className="bg-green-500">
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Ready
                                </Badge>
                              )}
                              {outfitError && (
                                <Badge variant="destructive">
                                  <XCircle className="w-3 h-3 mr-1" />
                                  Error
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Selected Outfit Details */}
          <Card>
            <CardHeader>
              <CardTitle>Selected Outfit</CardTitle>
              <CardDescription>
                {selectedOutfit
                  ? `ID: ${selectedOutfit.id.slice(0, 16)}...`
                  : 'Select an outfit from the list'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedOutfit ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Select an outfit to test flat lay generation</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Outfit Info */}
                  <div>
                    <h3 className="font-semibold mb-2">
                      {selectedOutfit.name || `Outfit ${selectedOutfit.id.slice(0, 8)}`}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedOutfit.items?.length || 0} items
                    </p>
                  </div>

                  {/* Status */}
                  <div>
                    <h4 className="font-semibold mb-2">Flat Lay Status</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{status}</Badge>
                        {polling && (
                          <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                        )}
                      </div>
                      {flatLayError && (
                        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded">
                          <p className="text-sm text-destructive font-medium">Error:</p>
                          <p className="text-sm text-destructive/80 mt-1">{flatLayError}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Flat Lay Image */}
                  {flatLayUrl && (
                    <div>
                      <h4 className="font-semibold mb-2">Flat Lay Image</h4>
                      <div className="border rounded-lg overflow-hidden">
                        <img
                          src={flatLayUrl}
                          alt="Flat lay"
                          className="w-full h-auto"
                          onError={(e) => {
                            console.error('Failed to load flat lay image');
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="pt-4 border-t">
                    <Button
                      onClick={handleRequestFlatLay}
                      disabled={requesting || isRequested || status === 'pending' || status === 'processing'}
                      className="w-full"
                    >
                      {requesting ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Requesting...
                        </>
                      ) : isRequested ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Already Requested
                        </>
                      ) : (
                        <>
                          <Image className="w-4 h-4 mr-2" />
                          Request Flat Lay
                        </>
                      )}
                    </Button>
                    {status === 'pending' || status === 'processing' ? (
                      <p className="text-sm text-muted-foreground mt-2 text-center">
                        Worker is processing your flat lay request...
                      </p>
                    ) : null}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

