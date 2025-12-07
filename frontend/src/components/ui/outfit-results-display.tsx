'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Sparkles, 
  Zap,
  Shirt,
  Heart,
  Calendar,
  RefreshCw,
  Star,
  ThumbsUp,
  ThumbsDown,
  Info,
  Palette,
  Target,
  Clock,
  CheckCircle,
  ArrowRight,
  Eye,
  Share2,
  Download,
  Cloud,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import StyleEducationModule from './style-education-module';
import FlatLayViewer from '../FlatLayViewer';

interface GeneratedOutfit {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number;
  score_breakdown?: any;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    thumbnailUrl?: string;
    backgroundRemovedUrl?: string;
    color: string;
    reason?: string;
  }>;
  reasoning: string;
  createdAt: string;
  metadata?: {
    generation_strategy?: string;
    flat_lay_url?: string;
    flatLayUrl?: string;
    flat_lay_status?: string;
    flatLayStatus?: string;
    flat_lay_error?: string;
    flatLayError?: string;
    [key: string]: any;
  };
  flat_lay_status?: string;
  flatLayStatus?: string;
  flat_lay_url?: string;
  flatLayUrl?: string;
  flat_lay_error?: string;
  flatLayError?: string;
  outfitAnalysis?: {
    textureAnalysis?: any;
    patternBalance?: any;
    colorStrategy?: any;
    styleSynergy?: any;
  };
}

interface OutfitRating {
  rating: number;
  isLiked: boolean;
  isDisliked: boolean;
  feedback?: string;
}

interface FlatLayUsageInfo {
  tier: string;
  limit: number | null;
  used: number;
  remaining: number | null;
}

interface OutfitResultsDisplayProps {
  outfit: GeneratedOutfit;
  rating: OutfitRating;
  onRatingChange: (rating: number) => void;
  onLikeToggle: () => void;
  onDislikeToggle: () => void;
  onFeedbackChange: (feedback: string) => void;
  onWearOutfit: () => void;
  onRegenerate: () => void;
  onViewOutfits: () => void;
  ratingSubmitted: boolean;
  isWorn?: boolean;
  flatLayUsage?: FlatLayUsageInfo | null;
  flatLayLoading?: boolean;
  flatLayError?: string | null;
  onRequestFlatLay?: () => void;
  onSkipFlatLay?: () => void;
  flatLayActionLoading?: boolean;
  hasFlatLayCredits?: boolean;
}

interface FlatLayState {
  url: string | null;
  status: string;
  error: string | null;
}

function extractFlatLayState(outfit: GeneratedOutfit): FlatLayState {
  const metadata = outfit.metadata ?? {};
  const url =
    metadata.flat_lay_url ??
    metadata.flatLayUrl ??
    outfit.flat_lay_url ??
    outfit.flatLayUrl ??
    null;
  const status =
    metadata.flat_lay_status ??
    metadata.flatLayStatus ??
    outfit.flat_lay_status ??
    outfit.flatLayStatus ??
    (url ? 'done' : 'awaiting_consent');
  const error =
    metadata.flat_lay_error ??
    metadata.flatLayError ??
    outfit.flat_lay_error ??
    outfit.flatLayError ??
    null;

  return {
    url,
    status,
    error,
  };
}

export default function OutfitResultsDisplay({
  outfit,
  rating,
  onRatingChange,
  onLikeToggle,
  onDislikeToggle,
  onFeedbackChange,
  onWearOutfit,
  onRegenerate,
  onViewOutfits,
  ratingSubmitted,
  isWorn = false,
  flatLayUsage = null,
  flatLayLoading = false,
  flatLayError = null,
  onRequestFlatLay,
  onSkipFlatLay,
  flatLayActionLoading = false,
  hasFlatLayCredits = false
}: OutfitResultsDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [showWhyItWorks, setShowWhyItWorks] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);
  const [flatLayState, setFlatLayState] = useState<FlatLayState>(() =>
    extractFlatLayState(outfit)
  );
  const listenerAttachedRef = useRef(false);

  useEffect(() => {
    setFlatLayState(extractFlatLayState(outfit));
    listenerAttachedRef.current = false;
  }, [outfit.id]);

  useEffect(() => {
    if (!outfit.id) return;
    if (flatLayState.status === 'done' && flatLayState.url) return;

    let isMounted = true;
    let unsubscribe: (() => void) | null = null;

    (async () => {
      try {
        const { db } = await import('@/lib/firebase/config');
        const { doc, onSnapshot } = await import('firebase/firestore');
        if (!isMounted) return;

        const docRef = doc(db, 'outfits', outfit.id);
        unsubscribe = onSnapshot(docRef, (snapshot) => {
          if (!snapshot.exists()) return;
          const data = snapshot.data() || {};
          const metadata = data.metadata || {};
          const url =
            metadata.flat_lay_url ||
            metadata.flatLayUrl ||
            data.flat_lay_url ||
            data.flatLayUrl ||
            null;
          const status =
            metadata.flat_lay_status ||
            metadata.flatLayStatus ||
            data.flat_lay_status ||
            data.flatLayStatus ||
            (url ? 'done' : 'awaiting_consent');
          const error =
            metadata.flat_lay_error ||
            metadata.flatLayError ||
            data.flat_lay_error ||
            data.flatLayError ||
            null;

          setFlatLayState((prev) => ({
            url: url ?? prev.url,
            status: status ?? prev.status,
            error: error ?? prev.error,
          }));
        });
      } catch (error) {
        console.error('Failed to attach flat lay listener:', error);
        listenerAttachedRef.current = false;
      }
    })();

    return () => {
      isMounted = false;
      unsubscribe?.();
      listenerAttachedRef.current = false;
    };
  }, [outfit.id, flatLayState.status, flatLayState.url]);

  const flatLayUrl = flatLayState.url;
  const flatLayStatus = flatLayState.status;
  const flatLayGenerationError = flatLayState.error;

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-[#B8860B] bg-[#E8C8A0]/20 dark:text-[#E8C8A0] dark:bg-[#B8860B]/20';
    if (score >= 0.6) return 'text-[#B8860B] bg-[#E8C8A0]/20 dark:text-[#E8C8A0] dark:bg-[#B8860B]/20';
    return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
  };

  const getConfidenceText = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Fair Match';
  };

  // DEBUG: Log flat lay URL
  console.log('🎨 OUTFIT RESULTS: outfit.metadata:', outfit.metadata);
  console.log('🎨 OUTFIT RESULTS: flat_lay_url:', flatLayUrl);
  console.log('🎨 OUTFIT RESULTS: flat_lay_status:', flatLayStatus);
  console.log('🎨 OUTFIT RESULTS: Should show flat lay?', !!flatLayUrl);

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
      link.download = `${outfit.name}-flat-lay.png`;
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
    
    // Prevent multiple simultaneous share operations
    if (navigator.share) {
      try {
        // Fetch image via proxy to include in share
        const proxyUrl = `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}`;
        const response = await fetch(proxyUrl);
        const blob = await response.blob();
        const file = new File([blob], `${outfit.name}-flat-lay.png`, { type: 'image/png' });
        
        await navigator.share({
          title: outfit.name,
          text: 'Check out this outfit!',
          files: [file]
        });
      } catch (error: any) {
        // Ignore AbortError (user cancelled) and other expected errors
        if (error.name !== 'AbortError' && error.name !== 'InvalidStateError') {
          console.error('Error sharing:', error);
        }
      }
    } else {
      navigator.clipboard.writeText(flatLayUrl);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <div className="space-y-6">
      {/* Main Outfit Card */}
      <Card className="overflow-hidden border-2 border-[#E8C8A0]/40 dark:border-[#B8860B]/60 bg-gradient-to-br from-[#E8C8A0]/50 to-orange-50 dark:from-[#B8860B]/20 dark:to-[#C9956F]/20">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {outfit.name}
              </CardTitle>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Palette className="h-3 w-3" />
                  {outfit.style}
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1">
                  <Target className="h-3 w-3" />
                  {outfit.mood}
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {outfit.occasion}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge 
                variant="secondary" 
                className={`flex items-center gap-1 ${getConfidenceColor(outfit.confidence_score)}`}
              >
                <Zap className="h-3 w-3" />
                {Math.round(outfit.confidence_score * 100)}% Match
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-gray-500 hover:text-gray-700"
              >
                <Eye className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* HERO: Flat Lay Image (Primary Display) */}
          <div className="mb-6 p-6 bg-gradient-to-br from-[#E8C8A0]/30 to-[#C9956F]/30 dark:from-[#B8860B]/40 dark:to-[#C9956F]/40 rounded-2xl border-4 border-[#D4A574] dark:border-[#C9956F]">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
                <Eye className="h-6 w-6 text-[#B8860B] dark:text-[#E8C8A0]" />
                Complete Outfit Preview
              </h4>
              <Badge className="bg-[#B8860B] text-white dark:bg-[#E8C8A0]/100">
                Flat Lay
              </Badge>
            </div>

            <FlatLayViewer
              flatLayUrl={flatLayUrl}
              outfitName={outfit.name}
              outfitItems={outfit.items}
              className="w-full"
              status={flatLayStatus}
              error={flatLayGenerationError}
              onViewChange={(view) => console.log('Flat lay view changed:', view)}
              flatLayUsage={flatLayUsage}
              flatLayLoading={flatLayLoading}
              flatLayError={flatLayError}
              onRequestFlatLay={onRequestFlatLay}
              onSkipFlatLay={onSkipFlatLay}
              flatLayActionLoading={flatLayActionLoading}
              hasFlatLayCredits={hasFlatLayCredits}
            />

            <div className="mt-4 flex gap-2 justify-end">
              <Button
                size="sm"
                variant="secondary"
                onClick={handleDownload}
                disabled={!flatLayUrl}
                className="bg-rose-gold-200 hover:bg-rose-gold-300 dark:bg-rose-gold-800 dark:hover:bg-rose-gold-700 disabled:opacity-50"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleShare}
                disabled={!flatLayUrl}
                className="bg-rose-gold-200 hover:bg-rose-gold-300 dark:bg-rose-gold-800 dark:hover:bg-rose-gold-700 disabled:opacity-50"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
            </div>
          </div>

          {/* Outfit Items Grid (Secondary - Detailed View) */}
          <div>
            <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shirt className="h-5 w-5 text-[#B8860B]" />
              Outfit Details ({outfit.items.length} pieces)
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {outfit.items.map((item, index) => (
                <div 
                  key={index} 
                  className="group relative bg-white/85 dark:bg-[#0D0D0D]/85 rounded-2xl p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 hover:shadow-xl transition-all duration-200"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-16 h-16 bg-[#F5F0E8] dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-xl overflow-hidden flex-shrink-0">
                      {item.imageUrl ? (
                        <img 
                          src={item.thumbnailUrl || item.backgroundRemovedUrl || item.imageUrl} 
                          alt={item.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/placeholder.jpg';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Shirt className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-gray-900 dark:text-white truncate">
                        {item.name}
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {item.type} • {item.color}
                      </p>
                      {item.reason && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 line-clamp-2">
                          {item.reason}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Weather-Informed Advisory Text - Always Visible */}
          {outfit.reasoning && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0] mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Outfit Advisory</h4>
                  <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                    {outfit.reasoning}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Score Breakdown */}
          {showDetails && outfit.score_breakdown && (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900 dark:text-white">Outfit Analysis</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Overall Score</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-800 dark:text-blue-200">
                    {outfit.score_breakdown.total_score}
                  </div>
                  <div className="text-xs text-[#B8860B] dark:text-[#E8C8A0]">
                    Grade: {outfit.score_breakdown.grade}
                  </div>
                </div>
                <div className="bg-gradient-to-r from-[#E8C8A0]/50 to-[#E8C8A0]/10 dark:from-[#B8860B]/20 dark:to-[#B8860B]/10 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-[#B8860B]" />
                    <span className="text-sm font-medium text-[#B8860B] dark:text-[#E8C8A0]">Confidence</span>
                  </div>
                   <div className="text-2xl font-bold text-[#B8860B] dark:text-[#DDB896]">
                    {Math.round(outfit.confidence_score * 100)}%
                  </div>
                  <div className="text-xs text-[#B8860B] dark:text-[#E8C8A0]">
                    {getConfidenceText(outfit.confidence_score)}
                  </div>
                </div>
              </div>
              
              {/* Component Scores */}
              <div className="space-y-2">
                {Object.entries(outfit.score_breakdown).map(([key, value]) => {
                  if (key === 'total_score' || key === 'grade' || key === 'score_interpretation') return null;
                  return (
                    <div key={key} className="flex justify-between items-center text-sm py-2 px-3 bg-[#F5F0E8]/70 dark:bg-[#1A1A1A]/80 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-xl">
                      <span className="capitalize text-gray-700 dark:text-gray-300">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {value}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 🎯 UNIFIED "WHY THIS OUTFIT WORKS" SECTION - COLLAPSIBLE */}
          {(() => {
            // Debug logging
            console.log('🔍 OUTFIT METADATA CHECK:', {
              hasMetadata: !!outfit.metadata,
              hasUserLearning: !!outfit.metadata?.user_learning_insights,
              hasUserStats: !!outfit.metadata?.user_stats,
              hasItemIntel: !!outfit.metadata?.item_intelligence,
              metadataKeys: outfit.metadata ? Object.keys(outfit.metadata) : []
            });
            return outfit.metadata && (outfit.metadata.user_learning_insights || outfit.metadata.user_stats || outfit.metadata.item_intelligence || outfit.metadata.diversity_info);
          })() && (
            <div className="border-t border-[#E8C8A0]/30 dark:border-[#B8860B]/30 pt-6">
              {/* Collapsible Header Button */}
              <button
                onClick={() => setShowWhyItWorks(!showWhyItWorks)}
                className="w-full flex items-center justify-between gap-3 mb-4 p-4 rounded-2xl bg-gradient-to-r from-[#E8C8A0]/20 to-orange-50/20 dark:from-[#B8860B]/20 dark:to-orange-900/20 hover:from-[#E8C8A0]/30 hover:to-orange-50/30 dark:hover:from-[#B8860B]/30 dark:hover:to-orange-900/30 border-2 border-[#E8C8A0]/40 dark:border-[#B8860B]/40 transition-all"
              >
                <div className="flex items-center gap-3">
                  <Sparkles className="h-6 w-6 text-[#B8860B] dark:text-[#E8C8A0]" />
                  <h3 className="text-xl font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                    Why This Outfit Works
                  </h3>
                </div>
                {showWhyItWorks ? (
                  <ChevronUp className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                )}
              </button>

              {/* Collapsible Content */}
              {showWhyItWorks && (
                <div className="space-y-4"

              {/* Item-Level Insights - Your Picks */}
              {outfit.metadata.item_intelligence && outfit.metadata.item_intelligence.length > 0 && (
                <div className="bg-gradient-to-br from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-[#C9956F]/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <Target className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                    Your Picks 🎯
                  </h4>
                  <div className="space-y-3">
                    {outfit.metadata.item_intelligence.map((insight: any, idx: number) => (
                      <div 
                        key={idx}
                        className="flex items-start gap-3 p-3 bg-[#E8C8A0]/20 dark:bg-[#B8860B]/20 rounded-xl border border-[#E8C8A0]/40 dark:border-[#B8860B]/40"
                      >
                        <div className="text-2xl flex-shrink-0">{insight.icon || '✨'}</div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-[#1C1917] dark:text-[#F8F5F1]">
                            {insight.item_name}
                          </div>
                          <div className="text-sm text-[#57534E] dark:text-[#C4BCB4] mt-1">
                            {insight.reason}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Fresh Picks Indicator integrated */}
                  {outfit.metadata.diversity_info && (
                    <div className="mt-4 pt-4 border-t border-[#E8C8A0]/30 dark:border-[#B8860B]/30">
                      <div className="flex items-start gap-2">
                        <RefreshCw className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0] mt-0.5 flex-shrink-0" />
                        <div>
                          <span className="text-sm font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
                            Fresh Picks 🎯
                          </span>
                          <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">
                            {outfit.metadata.diversity_info.message || 
                              `🎯 Super fresh! This outfit introduces new combinations you haven't tried before.`}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Personalization Section */}
              {(outfit.metadata.user_learning_insights || outfit.metadata.user_stats) && (
                <div className="bg-gradient-to-r from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-orange-900/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                  <div className="flex items-start gap-3 mb-3">
                    <Sparkles className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0] mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-2">
                        Personalized for You 💜
                      </h4>
                      <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] leading-relaxed">
                        {outfit.metadata.user_learning_insights || 
                          `This outfit is tailored to your style preferences.`}
                      </p>
                      <ul className="mt-2 space-y-1 text-sm text-[#57534E] dark:text-[#C4BCB4]">
                        <li className="flex items-start gap-2">
                          <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                          <span>Based on your personal style profile</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                          <span>Combines items you love wearing</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  {/* Learning Stats */}
                  {outfit.metadata.user_stats && (
                    <div className="mt-4 pt-4 border-t border-[#E8C8A0]/30 dark:border-[#B8860B]/30">
                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div>
                          <div className="text-lg font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                            {outfit.metadata.user_stats.total_ratings || 0}
                          </div>
                          <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
                            Rated
                          </div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                            {outfit.metadata.user_stats.favorite_styles || 'Learning'}
                          </div>
                          <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
                            Top Style
                          </div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                            {outfit.metadata.user_stats.diversity_score ? `${outfit.metadata.user_stats.diversity_score}%` : 'Fresh'}
                          </div>
                          <div className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
                            Variety
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mt-4 p-3 bg-[#E8C8A0]/20 dark:bg-[#B8860B]/20 rounded-lg">
                    <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] flex items-start gap-2">
                      <Info className="h-4 w-4 flex-shrink-0 mt-0.5" />
                      <span>💡 Rate outfits to unlock Spotify-style personalization! Each rating helps us learn: colors, styles, patterns you prefer</span>
                    </p>
                  </div>
                </div>
              )}

              {/* Style Analysis Insights - Integrated from StyleEducationModule */}
              {outfit.outfitAnalysis && (
                <div className="space-y-3">
                  {/* Color Strategy */}
                  {outfit.outfitAnalysis.colorStrategy && (
                    <div className="bg-gradient-to-br from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-orange-900/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                      <h4 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-2 flex items-center gap-2">
                        <Palette className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                        Color Strategy
                      </h4>
                      <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">
                        {outfit.outfitAnalysis.colorStrategy.insight}
                      </p>
                      {outfit.items && outfit.items.length > 0 && (
                        <ul className="text-xs text-[#57534E] dark:text-[#C4BCB4] space-y-1 mt-2">
                          {outfit.items.slice(0, 2).map((item, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                              <span>{item.color} serves as {idx === 0 ? 'your base color' : 'accent and depth'}</span>
                            </li>
                          ))}
                          {outfit.items.length > 2 && (
                            <li className="flex items-start gap-2">
                              <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                              <span>Multiple colors add visual interest—keep accessories simple</span>
                            </li>
                          )}
                        </ul>
                      )}
                    </div>
                  )}

                  {/* Silhouette Balance */}
                  {outfit.items && outfit.items.length >= 2 && (
                    <div className="bg-gradient-to-br from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-orange-900/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                      <h4 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-2 flex items-center gap-2">
                        <Target className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                        Silhouette Balance
                      </h4>
                      <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                        Fitted + loose pieces create a flattering, proportioned silhouette
                      </p>
                    </div>
                  )}

                  {/* Style Harmony */}
                  {outfit.style && (
                    <div className="bg-gradient-to-br from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-orange-900/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                      <h4 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-2 flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                        Style Harmony
                      </h4>
                      <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">
                        {outfit.style} style creates personal expression
                      </p>
                      {outfit.occasion && (
                        <div className="mt-3 pt-3 border-t border-[#E8C8A0]/30 dark:border-[#B8860B]/30">
                          <p className="text-sm font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-1">
                            Perfect for {outfit.occasion}
                          </p>
                          <ul className="text-xs text-[#57534E] dark:text-[#C4BCB4] space-y-1">
                            <li className="flex items-start gap-2">
                              <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                              <span>{outfit.style} style matches the event's vibe</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                              <span>Comfortable enough to wear confidently</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                              <span>Easy to accessorize up or down as needed</span>
                            </li>
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Weather Appropriateness */}
                  {(outfit.metadata?.weather || (outfit as any).weather) && (
                    <div className="bg-gradient-to-br from-[#E8C8A0]/30 to-orange-50/30 dark:from-[#B8860B]/20 dark:to-orange-900/20 rounded-2xl p-5 border-2 border-[#E8C8A0]/50 dark:border-[#B8860B]/50">
                      <h4 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-2 flex items-center gap-2">
                        <Cloud className="h-5 w-5 text-[#B8860B] dark:text-[#E8C8A0]" />
                        Weather Appropriateness
                      </h4>
                      {(() => {
                        const weatherData = outfit.metadata?.weather || (outfit as any).weather;
                        const temp = weatherData?.temperature || 70;
                        return (
                          <>
                            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">
                              Warm layers appropriate for {temp}°F weather - cozy and protective.
                            </p>
                            <ul className="text-xs text-[#57534E] dark:text-[#C4BCB4] space-y-1">
                              <li className="flex items-start gap-2">
                                <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                                <span>Temperature-appropriate for {temp}°F conditions</span>
                              </li>
                              <li className="flex items-start gap-2">
                                <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                                <span>Layering allows you to adjust throughout the day</span>
                              </li>
                              {temp < 60 && (
                                <li className="flex items-start gap-2">
                                  <span className="text-[#B8860B] dark:text-[#E8C8A0] mt-1">•</span>
                                  <span>Materials chosen for weather comfort</span>
                                </li>
                              )}
                            </ul>
                          </>
                        );
                      })()}
                    </div>
                  )}
                </div>
              )}
                </div>
              )}
            </div>
          )}

          {/* Rating Section with Enhanced Context */}
          <div className="border-t pt-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-gray-900 dark:text-white">Rate This Outfit</h4>
              <Badge variant="outline" className="text-xs">
                <Star className="h-3 w-3 mr-1" />
                Powers Your AI
              </Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Your feedback trains our AI to understand your unique style preferences better!
            </p>
            
            {/* Star Rating */}
            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">Rating:</span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => onRatingChange(star)}
                    className={`text-2xl transition-all duration-200 hover:scale-110 cursor-pointer select-none ${
                      star <= rating.rating
                        ? 'text-[#E8C8A0] fill-current'
                        : 'text-gray-300 dark:text-gray-600 hover:text-[#E8C8A0]'
                    }`}
                    style={{ userSelect: 'none' }}
                    disabled={ratingSubmitted}
                  >
                    ★
                  </button>
                ))}
              </div>
              {rating.rating > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {rating.rating} star{rating.rating !== 1 ? 's' : ''}
                </span>
              )}
              {ratingSubmitted && (
                <span className="text-xs text-[#B8860B] dark:text-[#E8C8A0] ml-2">
                  ✓ Submitted
                </span>
              )}
            </div>

            {/* Like/Dislike Buttons */}
            <div className="flex gap-3 mb-4">
              <Button
                variant={rating.isLiked ? "default" : "outline"}
                size="sm"
                onClick={onLikeToggle}
                disabled={ratingSubmitted}
                  className={`flex items-center gap-2 ${
                    rating.isLiked 
                     ? 'bg-[#B8860B] hover:bg-[#A0744F] text-white' 
                     : 'hover:bg-green-50 hover:text-[#B8860B]'
                  } ${ratingSubmitted ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <ThumbsUp className="h-4 w-4" />
                {rating.isLiked ? 'Liked' : 'Like'}
              </Button>
              <Button
                variant={rating.isDisliked ? "destructive" : "outline"}
                size="sm"
                onClick={onDislikeToggle}
                disabled={ratingSubmitted}
                className={`flex items-center gap-2 ${ratingSubmitted ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <ThumbsDown className="h-4 w-4" />
                {rating.isDisliked ? 'Disliked' : 'Dislike'}
              </Button>
            </div>

            {/* Feedback */}
            <div className="mb-4">
              <Textarea
                placeholder="Share your thoughts about this outfit... (e.g., 'Love the color combo!' or 'Too formal for weekend')"
                value={rating.feedback}
                onChange={(e) => onFeedbackChange(e.target.value)}
                rows={3}
                className="text-sm"
                disabled={ratingSubmitted}
              />
            </div>

            {/* Status Messages */}
            {rating.rating > 0 && !ratingSubmitted && (
              <div className="text-xs text-[#B8860B] dark:text-[#E8C8A0] text-center mb-4 flex items-center justify-center gap-2">
                <Sparkles className="h-3 w-3" />
                ✓ Rating will be automatically submitted and improve your AI
              </div>
            )}

            {ratingSubmitted && (
              <div className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg mb-4">
                <div className="flex items-center justify-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                  <p className="text-sm text-green-700 dark:text-green-300 font-medium">
                    Thanks! Your AI is learning your style preferences 🎉
                  </p>
                </div>
              </div>
            )}

            {isWorn && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg mb-4">
                <p className="text-sm text-[#B8860B] dark:text-[#E8C8A0] text-center">
                  ✓ Outfit marked as worn! Redirecting to outfits page...
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            {isWorn ? (
              <Button 
                onClick={onViewOutfits} 
                className="flex-1 bg-gradient-to-r from-rose-gold-600 to-orange-600 hover:from-rose-gold-700 hover:to-orange-700"
              >
                <Shirt className="h-4 w-4 mr-2" />
                View My Looks
              </Button>
            ) : ratingSubmitted ? (
              <>
                <Button onClick={onWearOutfit} className="flex-1 bg-gradient-to-r from-rose-gold-600 to-orange-600 hover:from-green-700 hover:to-emerald-700">
                  <Calendar className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
                <Button 
                  variant="outline" 
                  onClick={onViewOutfits}
                  className="flex-1"
                >
                  <Shirt className="h-4 w-4 mr-2" />
                  View All Looks
                </Button>
              </>
            ) : (
              <>
                <Button onClick={onWearOutfit} className="flex-1 bg-gradient-to-r from-rose-gold-600 to-orange-600 hover:from-green-700 hover:to-emerald-700">
                  <Calendar className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
                <Button variant="outline" onClick={onRegenerate} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Integrated Style Education - Now part of "Why This Outfit Works" */}
      <div className="hidden">
        {/* Keep StyleEducationModule for any backend dependencies but hide it */}
        <StyleEducationModule 
          outfitStyle={outfit.style}
          outfitMood={outfit.mood}
          outfitOccasion={outfit.occasion}
          outfitItems={outfit.items}
          outfitReasoning={outfit.reasoning}
          styleStrategy={outfit.metadata?.generation_strategy}
          outfitAnalysis={outfit.outfitAnalysis}
          structuredExplanation={outfit.metadata?.structuredExplanation || outfit.metadata?.explanation}
          weather={outfit.metadata?.weather || (outfit as any).weather}
          personalizationInsights={outfit.metadata?.personalization_insights}
          className="mt-8"
        />
      </div>
    </div>
  );
}
