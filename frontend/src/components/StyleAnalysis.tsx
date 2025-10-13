'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Upload, Image as ImageIcon, TrendingUp, BarChart3 } from 'lucide-react';

interface StyleMatch {
  style_name: string;
  confidence: number;
}

interface StyleBreakdown {
  [key: string]: number;
}

interface StyleAnalysisResponse {
  success: boolean;
  style_matches?: StyleMatch[];
  top_styles?: StyleMatch[];
  style_breakdown?: StyleBreakdown;
  top_match?: StyleMatch;
  top_style?: string;
}

const StyleAnalysis: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<StyleAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setAnalysisResults(null);
    }
  };

  const analyzeStyle = async (endpoint: string, formData?: FormData) => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app'}/api/style-analysis/${endpoint}`;
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: StyleAnalysisResponse = await response.json();
      setAnalysisResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    await analyzeStyle('analyze', formData);
  };

  const handleTopStyles = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('top_k', '5');
    await analyzeStyle('top-styles', formData);
  };

  const handleStyleBreakdown = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    await analyzeStyle('style-breakdown', formData);
  };

  const formatConfidence = (confidence: number) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">🧥 CLIP Style Analysis</h1>
        <p className="text-muted-foreground">
          Upload a clothing item image to analyze its style using AI-powered CLIP embeddings
        </p>
      </div>

      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Clothing Image
          </CardTitle>
          <CardDescription>
            Select an image of a clothing item to analyze its style characteristics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <ImageIcon className="w-8 h-8 mb-4 text-gray-500" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PNG, JPG, JPEG up to 10MB</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileSelect}
                />
              </label>
            </div>

            {previewUrl && (
              <div className="flex justify-center">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-w-xs max-h-64 object-contain rounded-lg border"
                />
              </div>
            )}

            {selectedFile && (
              <div className="flex gap-2 justify-center">
                <Button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="flex items-center gap-2"
                >
                  <TrendingUp className="h-4 w-4" />
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Style'}
                </Button>
                <Button
                  onClick={handleTopStyles}
                  disabled={isAnalyzing}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <BarChart3 className="h-4 w-4" />
                  Top Styles
                </Button>
                <Button
                  onClick={handleStyleBreakdown}
                  disabled={isAnalyzing}
                  variant="outline"
                >
                  Full Breakdown
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">❌ Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {/* Results Display */}
      {analysisResults && (
        <Card>
          <CardHeader>
            <CardTitle>🎯 Style Analysis Results</CardTitle>
            <CardDescription>
              AI-powered style classification using CLIP embeddings
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Top Match */}
            {analysisResults.top_match && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">🏆 Top Match</h3>
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">
                      {analysisResults.top_match.style_name}
                    </span>
                    <span className="text-2xl font-bold text-blue-600">
                      {formatConfidence(analysisResults.top_match.confidence)}
                    </span>
                  </div>
                  <Progress
                    value={analysisResults.top_match.confidence * 100}
                    className="mt-2"
                  />
                </div>
              </div>
            )}

            {/* Style Matches */}
            {analysisResults.style_matches && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">📊 All Style Matches</h3>
                <div className="space-y-3">
                  {analysisResults.style_matches.slice(0, 10).map((match, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-500">
                          #{index + 1}
                        </span>
                        <span className="font-medium">{match.style_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={match.confidence * 100}
                          className="w-24"
                        />
                        <span className="text-sm font-medium">
                          {formatConfidence(match.confidence)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Styles */}
            {analysisResults.top_styles && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">⭐ Top 5 Styles</h3>
                <div className="grid gap-3">
                  {analysisResults.top_styles.map((style, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-lg">#{index + 1}</span>
                        <span className="font-medium">{style.style_name}</span>
                      </div>
                      <span className="text-lg font-bold text-blue-600">
                        {formatConfidence(style.confidence)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Style Breakdown */}
            {analysisResults.style_breakdown && (
              <div>
                <h3 className="text-lg font-semibold mb-3">📈 Complete Style Breakdown</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {Object.entries(analysisResults.style_breakdown)
                    .sort(([, a], [, b]) => b - a)
                    .map(([style, confidence], index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{style}</span>
                        <div className="flex items-center gap-2">
                          <Progress
                            value={confidence * 100}
                            className="w-20"
                          />
                          <span className="text-sm font-medium">
                            {formatConfidence(confidence)}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Information Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-800">ℹ️ How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-blue-700">
            <p>
              • <strong>CLIP Embeddings:</strong> Uses OpenAI's CLIP model to generate visual embeddings
            </p>
            <p>
              • <strong>Style Prompts:</strong> Compares against 19 carefully crafted style descriptions
            </p>
            <p>
              • <strong>Cosine Similarity:</strong> Measures similarity between image and style embeddings
            </p>
            <p>
              • <strong>Ranked Results:</strong> Returns confidence scores for all supported styles
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StyleAnalysis; 