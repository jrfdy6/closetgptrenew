"use client";

import React, { useEffect, useState } from 'react';
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
import Link from "next/link";

interface FlatLayUsageInfo {
  tier: string;
  limit: number | null;
  used: number;
  remaining: number | null;
}

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
  status?: string;
  error?: string | null;
  flatLayUsage?: FlatLayUsageInfo | null;
  flatLayLoading?: boolean;
  flatLayError?: string | null;
  onRequestFlatLay?: () => void;
  onSkipFlatLay?: () => void;
  flatLayActionLoading?: boolean;
  hasFlatLayCredits?: boolean;
}

export default function FlatLayViewer({
  flatLayUrl,
  outfitName,
  outfitItems = [],
  className = "",
  showItemGrid = true,
  onViewChange,
  status,
  error,
  flatLayUsage = null,
  flatLayLoading = false,
  flatLayError = null,
  onRequestFlatLay,
  onSkipFlatLay,
  flatLayActionLoading = false,
  hasFlatLayCredits = false
}: FlatLayViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const normalizedStatus = (status ?? '').toLowerCase();
  const getInitialView = () => {
    if (
      !flatLayUrl &&
      ['awaiting_consent', 'manual_pending', 'declined', 'skipped', 'failed', 'error'].includes(
        normalizedStatus
      )
    ) {
      return 'grid';
    }
    return 'flat-lay';
  };
  const [currentView, setCurrentView] = useState<'flat-lay' | 'grid'>(getInitialView);

  useEffect(() => {
    setImageError(false);
    setIsLoading(!!flatLayUrl);
  }, [flatLayUrl]);

  useEffect(() => {
    setCurrentView(getInitialView());
  }, [flatLayUrl, status]);

  // DEBUG: Log component props
  console.log('🎨 FLAT LAY VIEWER: Component mounted');
  console.log('🎨 FLAT LAY VIEWER: flatLayUrl:', flatLayUrl);
  console.log('🎨 FLAT LAY VIEWER: outfitName:', outfitName);
  console.log('🎨 FLAT LAY VIEWER: currentView:', currentView);
  console.log('🎨 FLAT LAY VIEWER: status:', status);

  const flatLayBalanceText = flatLayUsage
    ? flatLayUsage.remaining !== null && flatLayUsage.limit !== null
      ? `You got ${flatLayUsage.remaining} out of ${flatLayUsage.limit} credits left this week based on your tier level.`
      : 'Unlimited flat lay credits available this week.'
    : flatLayLoading
      ? 'Checking your flat lay balance…'
      : (flatLayError || 'Unable to load your flat lay balance right now.');
  const requestDisabled =
    flatLayActionLoading || flatLayLoading || !hasFlatLayCredits || !onRequestFlatLay;
  const showUpgradeButton = !flatLayLoading && !hasFlatLayCredits;
  const renderRequestButtonContent = () => {
    if (flatLayActionLoading) {
      return (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Requesting flat lay…
        </>
      );
    }

    if (!hasFlatLayCredits) {
      return 'No credits available';
    }

    return 'Create a flat lay';
  };

  const showConsentOverlay =
    currentView === 'grid' &&
    !flatLayUrl &&
    ['awaiting_consent', 'manual_pending'].includes(normalizedStatus);

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
      // Use proxy endpoint to avoid CORS issues
      const proxyUrl = `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}`;
      const response = await fetch(proxyUrl);
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
    if ((status === 'pending' || status === 'processing') && !flatLayUrl) {
      return (
        <div className="aspect-[4/3] max-h-[600px] bg-[#F5F0E8]/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl flex flex-col items-center justify-center p-8 shadow-xl backdrop-blur">
          <Loader2 className="w-10 h-10 animate-spin text-amber-600 mb-4" />
          <p className="text-[#57534E] dark:text-[#C4BCB4] text-center font-semibold">
            Crafting your premium flat lay…
          </p>
          <p className="text-sm text-[#827869] dark:text-[#8A827A] text-center mt-2">
            This usually takes a few seconds.
          </p>
        </div>
      );
    }

    if ((status === 'awaiting_consent' || status === 'manual_pending') && !flatLayUrl) {
      return (
        <div className="aspect-[4/3] max-h-[600px] bg-[#F5F0E8]/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl flex flex-col items-center justify-center p-8 shadow-xl backdrop-blur">
          <Eye className="w-12 h-12 text-[#FFB84C] mb-4" />
          <p className="text-[#1C1917] dark:text-[#F8F5F1] text-center font-semibold">
            Flat lay not requested yet
          </p>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] text-center mt-2 max-w-sm">
            Generate a premium flat lay from the outfit actions to see a styled visual here.
          </p>
          {showItemGrid && outfitItems.length > 0 && (
            <Button 
              variant="outline" 
              onClick={toggleView}
              className="mt-4 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              View item grid
            </Button>
          )}
        </div>
      );
    }

    if ((status === 'declined' || status === 'skipped') && !flatLayUrl) {
      return (
        <div className="aspect-[4/3] max-h-[600px] bg-[#F5F0E8]/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl flex flex-col items-center justify-center p-8 shadow-xl backdrop-blur">
          <ImageOff className="w-12 h-12 text-[#8A827A] dark:text-[#806A5A] mb-4" />
          <p className="text-[#1C1917] dark:text-[#F8F5F1] text-center font-semibold">
            Flat lay skipped for this outfit
          </p>
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] text-center mt-2 max-w-sm">
            You can request a flat lay later if you change your mind.
          </p>
          {showItemGrid && outfitItems.length > 0 && (
            <Button 
              variant="outline" 
              onClick={toggleView}
              className="mt-4 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              View item grid
            </Button>
          )}
        </div>
      );
    }

    if (status === 'failed' && !flatLayUrl) {
      return (
        <div className="aspect-[4/3] max-h-[600px] bg-[#FFF0EC]/90 dark:bg-[#3D211F]/85 border border-[#FF6F61]/40 rounded-3xl flex flex-col items-center justify-center p-8 shadow-xl backdrop-blur">
          <ImageOff className="w-16 h-16 text-[#FF6F61] mb-4" />
          <p className="text-[#7F1D1D] dark:text-[#FCA5A5] text-center mb-2 font-semibold">
            We couldn't generate this flat lay automatically.
          </p>
          {error && (
            <p className="text-sm text-[#B42318] dark:text-[#FCA5A5] text-center max-w-sm">
              {error}
            </p>
          )}
          {showItemGrid && outfitItems.length > 0 && (
            <Button 
              variant="outline" 
              onClick={toggleView}
              className="mt-4 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              View item grid
            </Button>
          )}
        </div>
      );
    }

    if (!flatLayUrl || imageError) {
      return (
        <div className="aspect-[4/3] max-h-[600px] bg-[#F5F0E8]/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl flex flex-col items-center justify-center p-8 shadow-xl backdrop-blur">
          <ImageOff className="w-16 h-16 text-[#8A827A] dark:text-[#806A5A] mb-4" />
          <p className="text-[#57534E] dark:text-[#C4BCB4] text-center mb-2 font-semibold">
            {imageError ? 'Failed to load flat lay image' : 'No flat lay image available'}
          </p>
          {showItemGrid && outfitItems.length > 0 && (
            <Button 
              variant="outline" 
              onClick={toggleView}
              className="mt-4 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <Grid3x3 className="w-4 h-4 mr-2" />
              View item grid
            </Button>
          )}
        </div>
      );
    }

    return (
      <div className="relative aspect-[4/3] max-h-[600px] bg-[#F5F0E8]/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl overflow-hidden shadow-xl backdrop-blur">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
          </div>
        )}
        
        <img
          src={flatLayUrl?.includes('storage.googleapis.com') || flatLayUrl?.includes('firebasestorage.googleapis.com') 
            ? `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}`
            : flatLayUrl}
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
            className="bg-white/85 dark:bg-[#0D0D0D]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 backdrop-blur-sm text-[#1C1917] dark:text-[#F8F5F1] hover:bg-white"
            onClick={() => setIsFullscreen(true)}
            aria-label="View flat lay in full screen"
          >
            <Maximize2 className="w-4 h-4" />
          </Button>
          
          {showItemGrid && outfitItems.length > 0 && (
            <Button
              size="sm"
              variant="secondary"
              className="bg-white/85 dark:bg-[#0D0D0D]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 backdrop-blur-sm text-[#1C1917] dark:text-[#F8F5F1] hover:bg-white"
              onClick={toggleView}
              aria-label="Switch to item grid"
            >
              <Grid3x3 className="w-4 h-4" />
            </Button>
          )}
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
      <div className="relative">
        <div
          className={`aspect-[9/16] bg-gray-50 dark:bg-gray-900 rounded-lg p-4 overflow-y-auto transition-all duration-200 ${
            showConsentOverlay ? 'pointer-events-none blur-sm brightness-50' : ''
          }`}
        >
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

        {showConsentOverlay && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="mx-4 w-full max-w-md rounded-2xl border border-amber-400/60 bg-stone-900/80 p-6 text-center shadow-2xl backdrop-blur">
              <Badge className="mb-3 bg-amber-500 text-white">Premium Flat Lay</Badge>
              <h3 className="text-lg font-semibold text-white">
                Create a flat lay for this outfit
              </h3>
              <p className="mt-2 text-sm text-amber-100">
                {flatLayBalanceText}
              </p>
              <div className="mt-5 flex flex-col gap-2">
                <Button
                  onClick={() => onRequestFlatLay?.()}
                  disabled={requestDisabled}
                  className="w-full bg-amber-500 hover:bg-amber-600 text-white"
                >
                  {renderRequestButtonContent()}
                </Button>
                {showUpgradeButton && (
                  <Button
                    variant="outline"
                    className="w-full border-amber-300 text-amber-200 hover:bg-amber-500/20"
                    asChild
                  >
                    <Link href="/upgrade">
                      Upgrade to unlock more flat lays
                    </Link>
                  </Button>
                )}
                {onSkipFlatLay && (
                  <Button
                    variant="ghost"
                    onClick={() => {
                      onSkipFlatLay();
                      setCurrentView('grid');
                    }}
                    disabled={flatLayActionLoading}
                    className="w-full text-amber-100 hover:text-white"
                  >
                    Maybe later
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
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
          src={flatLayUrl?.includes('storage.googleapis.com') || flatLayUrl?.includes('firebasestorage.googleapis.com')
            ? `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}`
            : flatLayUrl}
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

