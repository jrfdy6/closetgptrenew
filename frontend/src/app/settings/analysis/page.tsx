'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { analyzeWardrobeMetadata } from '@/lib/wardrobeAnalysis';

interface CategoryStats {
  count: number;
  percentage: string;
  types: { [key: string]: number };
}

interface AnalysisReport {
  totalItems: number;
  categoryStats: {
    tops: CategoryStats;
    bottoms: CategoryStats;
    shoes: CategoryStats;
    layers: CategoryStats;
    accessories: CategoryStats;
  };
  basicFields: { [key: string]: string };
  metadataFields: {
    visualAttributes: { [key: string]: string };
    itemMetadata: { [key: string]: string };
    colorAnalysis: { [key: string]: string };
  };
}

export default function AnalysisPage() {
  const router = useRouter();
  const { user, loading } = useFirebase();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/signin');
    } else if (user) {
      const fetchReport = async () => {
        try {
          const analysisReport = await analyzeWardrobeMetadata(user.uid);
          setReport(analysisReport);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to analyze wardrobe metadata');
        } finally {
          setIsLoading(false);
        }
      };

      fetchReport();
    }
  }, [user, loading, router]);

  if (loading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-gray-500">No report available.</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Wardrobe Analysis</h1>
      
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Overview</h2>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-lg mb-4 text-gray-900">Total Items: {report.totalItems}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {Object.entries(report.categoryStats).map(([category, stats]) => (
          <div key={category} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 capitalize text-gray-900">{category}</h3>
            <div className="space-y-4">
              <div>
                <p className="text-gray-600">Count</p>
                <p className="text-2xl font-bold text-gray-900">{stats.count}</p>
                <p className="text-sm text-gray-500">{stats.percentage} of total</p>
              </div>
              <div>
                <p className="text-gray-600 mb-2">Types</p>
                <div className="space-y-1">
                  {Object.entries(stats.types).map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="capitalize text-gray-700">{type}</span>
                      <span className="font-medium text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-900">Basic Fields Completion</h3>
          <div className="space-y-4">
            {Object.entries(report.basicFields).map(([field, percentage]) => (
              <div key={field} className="flex justify-between items-center">
                <span className="capitalize text-gray-700">{field}</span>
                <span className="font-medium text-gray-900">{percentage}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-900">Metadata Fields Completion</h3>
          {Object.entries(report.metadataFields).map(([category, fields]) => (
            <div key={category} className="mb-6">
              <h4 className="text-lg font-medium mb-3 capitalize text-gray-800">{category}</h4>
              <div className="space-y-2">
                {Object.entries(fields).map(([field, percentage]) => (
                  <div key={field} className="flex justify-between items-center">
                    <span className="capitalize text-gray-700">{field}</span>
                    <span className="font-medium text-gray-900">{percentage}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 