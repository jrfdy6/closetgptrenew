'use client';

import React, { useEffect, useState } from 'react';
import { processCurrentUserWardrobe } from '../lib/testWardrobeCleaner';
import { useFirebase } from '../lib/firebase-context';

export const WardrobeProcessor: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastProcessed, setLastProcessed] = useState<Date | null>(null);
  const { user } = useFirebase();

  const processWardrobe = async () => {
    if (!user) {
      setError(new Error('No user is currently logged in'));
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      await processCurrentUserWardrobe(user.uid);
      setLastProcessed(new Date());
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An error occurred'));
    } finally {
      setIsProcessing(false);
    }
  };

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <h2 className="text-red-800 font-semibold mb-2">Error</h2>
        <p className="text-red-600">{error.message}</p>
        <button
          onClick={processWardrobe}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">Please log in to process your wardrobe.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Wardrobe Processing</h2>
        <button
          onClick={processWardrobe}
          disabled={isProcessing}
          className={`px-4 py-2 rounded transition-colors ${
            isProcessing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {isProcessing ? 'Processing...' : 'Process Wardrobe'}
        </button>
      </div>

      {isProcessing && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800">Processing your wardrobe...</p>
        </div>
      )}

      {lastProcessed && !isProcessing && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800">
            Last processed: {lastProcessed.toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}; 