'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, AlertCircle } from "lucide-react";
import BatchImageUpload from "@/components/BatchImageUpload";
import type { ClothingItem } from "@/shared/types";
import { useFirebase } from "@/lib/firebase-context";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function BatchUploadPage() {
  const router = useRouter();
  const { user } = useFirebase();
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = (_items: ClothingItem[]) => {
    // Navigate back to wardrobe page after successful upload
    router.push("/wardrobe");
  };

  const handleError = (error: string) => {
    setError(error);
    // Clear error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </button>
          <h1 className="text-3xl font-bold">Batch Upload</h1>
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-yellow-50 p-4 text-yellow-800">
            <div className="flex items-center">
              <AlertCircle className="mr-2 h-5 w-5" />
              <p>{error}</p>
            </div>
          </div>
        )}

        <div>
          <BatchImageUpload
            onUploadComplete={handleUploadComplete}
            onError={handleError}
            userId={user?.uid}
          />
        </div>
      </div>
    </ProtectedRoute>
  );
} 