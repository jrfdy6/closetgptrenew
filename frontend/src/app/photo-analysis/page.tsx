'use client';

import React from 'react';
import { PhotoUpload } from '@/components/PhotoAnalysis/PhotoUpload';
import { PhotoAnalysisResults } from '@/components/PhotoAnalysis/PhotoAnalysisResults';
import { PhotoAnalysis } from '@/types/photo-analysis';
import { toast } from 'sonner';

export default function PhotoAnalysisPage() {
  const [analysis, setAnalysis] = React.useState<PhotoAnalysis | null>(null);
  const [photoType, setPhotoType] = React.useState<'fullBody' | 'outfit'>('fullBody');
  const [isLoading, setIsLoading] = React.useState(false);

  const handleUploadComplete = async (file: File) => {
    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', photoType);

      const response = await fetch('/api/upload-photo', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.details || 'Failed to upload photo');
      }

      const data = await response.json();
      setAnalysis(data.analysis);
      toast.success('Photo uploaded and analyzed successfully');
    } catch (error) {
      console.error('Error uploading photo:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to upload photo');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Photo Analysis</h1>

        <div className="mb-8">
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setPhotoType('fullBody')}
              className={`px-4 py-2 rounded-lg ${
                photoType === 'fullBody'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Full Body Photo
            </button>
            <button
              onClick={() => setPhotoType('outfit')}
              className={`px-4 py-2 rounded-lg ${
                photoType === 'outfit'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Outfit Photo
            </button>
          </div>

          <PhotoUpload
            onUploadComplete={handleUploadComplete}
            type={photoType}
            maxFiles={photoType === 'outfit' ? 5 : 1}
            isLoading={isLoading}
          />
        </div>

        {analysis && (
          <div className="mt-8">
            <PhotoAnalysisResults analysis={analysis} type={photoType} />
          </div>
        )}
      </div>
    </div>
  );
} 