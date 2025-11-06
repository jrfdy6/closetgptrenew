"use client";

import { useEffect, useState } from 'react';
import { useFirebase } from '@/lib/firebase-context';

interface WardrobeItem {
  id: string;
  name: string;
  imageUrl: string;
  backgroundRemovedUrl?: string;
  thumbnailUrl?: string;
  processing_status?: string;
  createdAt?: number;
  [key: string]: any;
}

export default function DebugWardrobePage() {
  const { user } = useFirebase();
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [rawResponse, setRawResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const token = await user.getIdToken();
        
        const response = await fetch('/api/wardrobe', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        setRawResponse(data);
        setItems(data.items || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            🔍 Wardrobe Debug Page
          </h1>
          <p className="text-red-500">Not authenticated. Please sign in.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            🔍 Wardrobe Debug Page
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            🔍 Wardrobe Debug Page
          </h1>
          <div className="bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-300">Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Sort items by createdAt (newest first)
  const sortedItems = [...items].sort((a, b) => {
    const aTime = a.createdAt || 0;
    const bTime = b.createdAt || 0;
    return bTime - aTime;
  });

  // Get newest 10 items
  const newestItems = sortedItems.slice(0, 10);

  // Stats
  const totalItems = items.length;
  const itemsWithProcessing = items.filter(item => item.processing_status).length;
  const itemsPending = items.filter(item => item.processing_status === 'pending').length;
  const itemsDone = items.filter(item => item.processing_status === 'done').length;
  const itemsWithBgRemoved = items.filter(item => item.backgroundRemovedUrl).length;
  const itemsWithThumbnail = items.filter(item => item.thumbnailUrl).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          🔍 Wardrobe Debug Page
        </h1>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{totalItems}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Items</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-blue-600">{itemsWithProcessing}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">With processing_status</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-yellow-600">{itemsPending}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Pending</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-green-600">{itemsDone}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Done</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-purple-600">{itemsWithBgRemoved}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">With backgroundRemovedUrl</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-2xl font-bold text-indigo-600">{itemsWithThumbnail}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">With thumbnailUrl</div>
          </div>
        </div>

        {/* Raw Response */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            📦 Raw API Response
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <pre className="text-xs overflow-auto max-h-96">
              {JSON.stringify(rawResponse, null, 2)}
            </pre>
          </div>
        </div>

        {/* Newest Items */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            🆕 Newest 10 Items (Sorted by createdAt)
          </h2>
          <div className="space-y-6">
            {newestItems.map((item, index) => {
              const createdDate = item.createdAt 
                ? new Date(item.createdAt * 1000).toLocaleString() 
                : 'Unknown';
              
              return (
                <div 
                  key={item.id} 
                  className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start gap-6">
                    {/* Item Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg font-bold text-gray-900 dark:text-white">
                          #{index + 1}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {item.id}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        {item.name}
                      </h3>
                      
                      <div className="space-y-1 text-sm">
                        <div>
                          <span className="font-semibold text-gray-700 dark:text-gray-300">Created:</span>{' '}
                          <span className="text-gray-600 dark:text-gray-400">{createdDate}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700 dark:text-gray-300">Status:</span>{' '}
                          <span className={`font-mono ${
                            item.processing_status === 'done' ? 'text-green-600' :
                            item.processing_status === 'pending' ? 'text-yellow-600' :
                            'text-gray-500'
                          }`}>
                            {item.processing_status || 'null'}
                          </span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700 dark:text-gray-300">backgroundRemovedUrl:</span>{' '}
                          {item.backgroundRemovedUrl ? (
                            <a 
                              href={item.backgroundRemovedUrl} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline text-xs break-all"
                            >
                              {item.backgroundRemovedUrl.substring(0, 60)}...
                            </a>
                          ) : (
                            <span className="text-red-600 font-mono">null</span>
                          )}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700 dark:text-gray-300">thumbnailUrl:</span>{' '}
                          {item.thumbnailUrl ? (
                            <a 
                              href={item.thumbnailUrl} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline text-xs break-all"
                            >
                              {item.thumbnailUrl.substring(0, 60)}...
                            </a>
                          ) : (
                            <span className="text-red-600 font-mono">null</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Images */}
                    <div className="flex gap-4">
                      {/* Original */}
                      <div className="text-center">
                        <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Original
                        </div>
                        <img 
                          src={item.imageUrl} 
                          alt="Original"
                          className="w-32 h-32 object-cover rounded border border-gray-300 dark:border-gray-600"
                        />
                      </div>

                      {/* Processed */}
                      {item.backgroundRemovedUrl && (
                        <div className="text-center">
                          <div className="text-xs font-semibold text-green-700 dark:text-green-400 mb-2">
                            Processed ✅
                          </div>
                          <img 
                            src={item.backgroundRemovedUrl} 
                            alt="Processed"
                            className="w-32 h-32 object-cover rounded border-2 border-green-500"
                          />
                        </div>
                      )}

                      {/* Thumbnail */}
                      {item.thumbnailUrl && (
                        <div className="text-center">
                          <div className="text-xs font-semibold text-purple-700 dark:text-purple-400 mb-2">
                            Thumbnail
                          </div>
                          <img 
                            src={item.thumbnailUrl} 
                            alt="Thumbnail"
                            className="w-32 h-32 object-cover rounded border-2 border-purple-500"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

