"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Maximize2, 
  Download, 
  Share2, 
  X,
  ImageOff,
  Loader2,
  Eye,
  Grid3x3
} from "lucide-react";

interface FlatLayViewerProps {
  flatLayUrl?: string | null;
  outfitName?: string;
  outfitItems?: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  className?: string;
  showItemGrid?: boolean;
  onViewChange?: (view: 'flat-lay' | 'grid') => void;
}

export default function FlatLayViewer({
  flatLayUrl,
  outfitName,
  outfitItems = [],
  className = "",
  showItemGrid = true,
  onViewChange
}: FlatLayViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const [currentView, setCurrentView] = useState<'flat-lay' | 'grid'>('flat-lay');

  // DEBUG: Log component props
  console.log('🎨 FLAT LAY VIEWER: Component mounted');
  console.log('🎨 FLAT LAY VIEWER: flatLayUrl:', flatLayUrl);
  console.log('🎨 FLAT LAY VIEWER: outfitName:', outfitName);
  console.log('🎨 FLAT LAY VIEWER: currentView:', currentView);

  const handleImageLoad = () => {
    setIsLoading(false);
  };

  const handleImageError = () => {
    setIsLoading(false);
    setImageError(true);
  };

  const handleDownload = async () => {
    if (!flatLayUrl) return;
    
    try {
      const response = await fetch(flatLayUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${outfitName || 'outfit'}-flat-lay.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading flat lay:', error);
    }
  };

  const handleShare = async () => {
    if (!flatLayUrl) return;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: outfitName || 'My Outfit',
          text: 'Check out this outfit!',
          url: flatLayUrl
        });
      } catch (error) {
        console.error('Error sharing:', error);
      }
    } else {
      // Fallback: Copy URL to clipboard
      navigator.clipboard.writeText(flatLayUrl);
      alert('Link copied to clipboard!');
    }
  };

  const toggleView = () => {
    const newView = currentView === 'flat-lay' ? 'grid' : 'flat-lay';
    setCurrentView(newView);
    onViewChange?.(newView);
  };

  const renderFlatLay = () => {
    if (!flatLayUrl || imageError) {
      return (
        <div className="aspect-[9/16] bg-gray-100 dark:bg-gray-800 rounded-lg flex flex-col items-center justify-center p-8">
          <ImageOff className="w-16 h-16 text-gray-400 dark:text-gray-600 mb-4" />
          <p className="text-gray-600 dark:text-gray-400 text-center mb-2">
            {imageError ? 'Failed to load flat lay image' : 'No flat lay image available'}
          </p>
          {showItemGrid && outfitItems.length > 0 && (
            <Button 
              variant="outline" 
              onClick={toggleView}
              className="mt-4"
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              View Item Grid
            </Button>
          )}
        </div>
      );
    }

    return (
      <div className="relative aspect-[9/16] bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
          </div>
        )}
        
        <img
          src={flatLayUrl}
          alt={outfitName || 'Outfit flat lay'}
          className="w-full h-full object-contain"
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
        
        {/* Action buttons */}
        <div className="absolute top-4 right-4 flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm"
            onClick={() => setIsFullscreen(true)}
          >
            <Maximize2 className="w-4 h-4" />
          </Button>
          
          {showItemGrid && outfitItems.length > 0 && (
            <Button
              size="sm"
              variant="secondary"
              className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm"
              onClick={toggleView}
            >
              <Grid3x3 className="w-4 h-4" />
            </Button>
          )}
        </div>
        
        {/* Download and share buttons */}
        <div className="absolute bottom-4 right-4 flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm"
            onClick={handleDownload}
          >
            <Download className="w-4 h-4" />
          </Button>
          
          <Button
            size="sm"
            variant="secondary"
            className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm"
            onClick={handleShare}
          >
            <Share2 className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Flat Lay Badge */}
        <div className="absolute top-4 left-4">
          <Badge variant="secondary" className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
            <Eye className="w-3 h-3 mr-1" />
            Flat Lay View
          </Badge>
        </div>
      </div>
    );
  };

  const renderItemGrid = () => {
    return (
      <div className="aspect-[9/16] bg-gray-50 dark:bg-gray-900 rounded-lg p-4 overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Outfit Items
          </h3>
          <Button
            size="sm"
            variant="outline"
            onClick={toggleView}
          >
            <Eye className="w-4 h-4 mr-2" />
            Flat Lay View
          </Button>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          {outfitItems.map((item) => (
            <div 
              key={item.id}
              className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700"
            >
              <div className="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                {item.imageUrl && !item.imageUrl.includes('placeholder') ? (
                  <img 
                    src={item.imageUrl}
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <ImageOff className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <div className="p-2">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {item.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {item.type}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Fullscreen modal
  const renderFullscreen = () => {
    if (!isFullscreen || !flatLayUrl) return null;

    return (
      <div 
        className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4"
        onClick={() => setIsFullscreen(false)}
      >
        <Button
          size="sm"
          variant="ghost"
          className="absolute top-4 right-4 text-white hover:bg-white/10"
          onClick={() => setIsFullscreen(false)}
        >
          <X className="w-6 h-6" />
        </Button>
        
        <img
          src={flatLayUrl}
          alt={outfitName || 'Outfit flat lay'}
          className="max-w-full max-h-full object-contain"
          onClick={(e) => e.stopPropagation()}
        />
        
        <div className="absolute bottom-4 right-4 flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={handleDownload}
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </Button>
          
          <Button
            size="sm"
            variant="secondary"
            onClick={handleShare}
          >
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>
    );
  };

  return (
    <>
      <div className={className}>
        {currentView === 'flat-lay' ? renderFlatLay() : renderItemGrid()}
      </div>
      
      {renderFullscreen()}
    </>
  );
}

