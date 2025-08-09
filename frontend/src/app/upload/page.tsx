"use client";

import ProtectedRoute from "@/components/ProtectedRoute";
import UploadForm from "@/components/UploadForm";
import { Upload, Sparkles } from 'lucide-react';
import AuthDebug from "@/components/AuthDebug";

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <div className="container-readable space-section py-8">
        {/* Hero Header */}
        <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <Upload className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <h1 className="text-2xl sm:text-hero text-foreground">Add to Wardrobe</h1>
          </div>
          <p className="text-secondary text-base sm:text-lg">
            Upload your clothing items and let our AI analyze them for perfect outfit recommendations.
          </p>
        </div>

        {/* Upload Form */}
        <div className="space-section">
          <UploadForm />
        </div>
      </div>
      
      {/* Debug component */}
      <AuthDebug />
    </ProtectedRoute>
  );
} 