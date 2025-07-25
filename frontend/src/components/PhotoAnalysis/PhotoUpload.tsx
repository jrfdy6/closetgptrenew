'use client';

import React from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';

interface PhotoUploadProps {
  onUploadComplete: (file: File) => void;
  type: 'fullBody' | 'outfit';
  maxFiles?: number;
  isLoading?: boolean;
}

export const PhotoUpload: React.FC<PhotoUploadProps> = ({
  onUploadComplete,
  type,
  maxFiles = 1,
  isLoading = false,
}) => {
  const [previewUrls, setPreviewUrls] = React.useState<string[]>([]);

  const onDrop = React.useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > maxFiles) {
        toast.error(`You can only upload up to ${maxFiles} ${type === 'outfit' ? 'outfits' : 'photo'}`);
        return;
      }

      // Create preview URLs
      const newPreviewUrls = acceptedFiles.map(file => URL.createObjectURL(file));
      setPreviewUrls(prev => [...prev, ...newPreviewUrls].slice(0, maxFiles));

      // Call onUploadComplete with the first file
      onUploadComplete(acceptedFiles[0]);
    },
    [maxFiles, onUploadComplete, type]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
    disabled: isLoading,
  });

  const removePreview = (index: number) => {
    setPreviewUrls(prev => prev.filter((_, i) => i !== index));
  };

  React.useEffect(() => {
    // Cleanup preview URLs when component unmounts
    return () => {
      previewUrls.forEach(url => URL.revokeObjectURL(url));
    };
  }, [previewUrls]);

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        {isLoading ? (
          <div className="space-y-2">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-600">Uploading...</p>
          </div>
        ) : isDragActive ? (
          <p className="text-blue-500">Drop the photo here...</p>
        ) : (
          <div className="space-y-2">
            <p className="text-gray-600">
              Drag and drop a {type === 'fullBody' ? 'full body' : 'outfit'} photo here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supported formats: JPG, PNG (max 5MB)
            </p>
          </div>
        )}
      </div>

      {previewUrls.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {previewUrls.map((url, index) => (
            <div key={url} className="relative group">
              <img
                src={url}
                alt={`Preview ${index + 1}`}
                className="w-full h-48 object-cover rounded-lg"
              />
              <button
                onClick={() => removePreview(index)}
                className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}; 