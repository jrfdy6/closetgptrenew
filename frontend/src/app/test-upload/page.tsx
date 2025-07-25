'use client';

import { useState } from 'react';
import { ClothingItem } from '../../shared/types/index';
import { useFirebase } from '@/lib/firebase-context';
import ProtectedRoute from '@/components/ProtectedRoute';
import { auth } from '@/lib/firebase/config';
import { toast } from '@/components/ui/use-toast';

type ProcessingStep = 'uploading' | 'analyzing' | 'embedding' | 'saving' | 'complete';

export default function TestUploadPage() {
  const { user } = useFirebase();
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<ProcessingStep | null>(null);
  const [result, setResult] = useState<ClothingItem | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !user) {
      setError('Please select a file and ensure you are logged in');
      return;
    }

    if (!auth) {
      toast({
        title: "Error",
        description: "Authentication is not initialized",
        variant: "destructive",
      });
      return;
    }

    setProcessing(true);
    setError(null);
    setCurrentStep('uploading');

    try {
      // Get the current user's ID token
      const idToken = await auth.currentUser?.getIdToken();
      if (!idToken) {
        throw new Error('Not authenticated');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('userId', user.uid);

      const response = await fetch('/api/process-image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      
      if (!data.success || !data.data) {
        throw new Error(data.error || 'Failed to process image');
      }

      setResult(data.data);
      setCurrentStep('complete');

      // Log the full metadata structure
      console.log('Processed Item:', data.data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Upload error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const getStepProgress = (step: ProcessingStep) => {
    if (!processing) return 0;
    if (currentStep === 'complete') return 100;
    
    const steps: ProcessingStep[] = ['uploading', 'analyzing', 'embedding', 'saving', 'complete'];
    const currentIndex = steps.indexOf(currentStep || 'uploading');
    const stepIndex = steps.indexOf(step);
    
    if (stepIndex < currentIndex) return 100;
    if (stepIndex === currentIndex) return 50;
    return 0;
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Test Image Upload</h1>
        
        <div className="mb-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="border p-2 rounded"
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || processing || !user}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
        >
          {processing ? 'Processing...' : 'Upload'}
        </button>

        {processing && (
          <div className="mt-4 space-y-2">
            {(['uploading', 'analyzing', 'embedding', 'saving'] as ProcessingStep[]).map((step) => (
              <div key={step} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="capitalize">{step}</span>
                  <span>{getStepProgress(step)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${getStepProgress(step)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Processed Item</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-2">Image</h3>
                <img
                  src={result.imageUrl}
                  alt={result.name}
                  className="max-w-sm rounded shadow-lg"
                />
              </div>

              <div>
                <h3 className="font-semibold mb-2">Metadata</h3>
                <div className="bg-gray-50 p-4 rounded">
                  <pre className="text-sm overflow-auto max-h-96">
                    {JSON.stringify({
                      id: result.id,
                      imageUrl: result.imageUrl,
                      backgroundRemoved: result.backgroundRemoved,
                      embedding: result.embedding ? `[${result.embedding.length} values]` : null,
                      metadata: result.metadata,
                      dominantColors: result.dominantColors,
                      matchingColors: result.matchingColors,
                      style: result.style,
                      occasion: result.occasion,
                      type: result.type,
                      subType: result.subType,
                      brand: result.brand,
                      colorName: result.colorName
                    }, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
} 