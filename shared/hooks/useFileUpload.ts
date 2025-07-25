import { useState } from 'react';
import { ApiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';
import { validateFile } from '../utils';
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from '../constants';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = async (file: File, onProgress?: (progress: number) => void) => {
    try {
      setUploading(true);
      setError(null);
      setProgress(0);

      // Validate file
      const validation = validateFile(file);
      if (!validation.isValid) {
        throw new Error(validation.error);
      }

      const formData = new FormData();
      formData.append('file', file);

      const response = await ApiClient.getInstance().uploadFile<{ url: string }>(
        API_ENDPOINTS.WARDROBE.UPLOAD,
        formData,
        (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
          onProgress?.(percentCompleted);
        }
      );

      return response.data?.url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
      throw err;
    } finally {
      setUploading(false);
    }
  };

  const uploadMultipleFiles = async (
    files: File[],
    onProgress?: (progress: number) => void
  ) => {
    try {
      setUploading(true);
      setError(null);
      setProgress(0);

      // Validate all files
      for (const file of files) {
        const validation = validateFile(file);
        if (!validation.isValid) {
          throw new Error(`Invalid file ${file.name}: ${validation.error}`);
        }
      }

      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await ApiClient.getInstance().uploadFile<{ urls: string[] }>(
        API_ENDPOINTS.WARDROBE.UPLOAD,
        formData,
        (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
          onProgress?.(percentCompleted);
        }
      );

      return response.data?.urls;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files');
      throw err;
    } finally {
      setUploading(false);
    }
  };

  const validateFiles = (files: File[]): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    for (const file of files) {
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        errors.push(`Invalid file type for ${file.name}. Allowed types: ${ALLOWED_FILE_TYPES.join(', ')}`);
      }

      if (file.size > MAX_FILE_SIZE) {
        errors.push(`File ${file.name} is too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB`);
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  };

  return {
    uploading,
    progress,
    error,
    uploadFile,
    uploadMultipleFiles,
    validateFiles,
  };
}; 