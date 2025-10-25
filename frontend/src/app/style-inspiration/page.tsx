"use client"

import React from 'react';
import { StyleInspirationCard } from '@/components/ui/style-inspiration-card';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';

export default function StyleInspirationPage() {
  const handleRefresh = () => {
    console.log('Card refreshed!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-yellow-500" />
            Style Inspiration
          </h1>
          <p className="text-gray-600 text-lg">
            Discover pieces that complement and expand your personal style
          </p>
        </div>

        {/* Info Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
            <CardDescription>
              Our algorithm analyzes your style profile and recommends items that either:
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-start gap-3">
              <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                Reinforce
              </div>
              <p className="text-sm text-gray-700">
                Strengthen your core style with pieces that match your primary aesthetic
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium">
                Bridge
              </div>
              <p className="text-sm text-gray-700">
                Blend your dominant styles with versatile pieces that work across aesthetics
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                Expand
              </div>
              <p className="text-sm text-gray-700">
                Explore new style directions while staying true to your preferences
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Main Inspiration Card */}
        <div className="flex justify-center">
          <StyleInspirationCard onRefresh={handleRefresh} />
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Recommendations are personalized based on your style profile and current weather conditions
          </p>
        </div>
      </div>
    </div>
  );
}

