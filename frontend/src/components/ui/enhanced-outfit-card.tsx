'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Heart, 
  HeartOff, 
  Eye, 
  Edit, 
  Trash2, 
  Calendar,
  Star,
  Zap,
  Palette,
  Target,
  Clock,
  Share2,
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface Outfit {
  id: string;
  name: string;
  occasion: string;
  style: string;
  mood?: string;
  confidence_score?: number;
  rating?: number;
  isFavorite?: boolean;
  isWorn?: boolean;
  lastWorn?: string;
  wearCount?: number;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    color: string;
  }>;
  metadata?: {
    flat_lay_url?: string;
    [key: string]: any;
  };
  createdAt: string;
}

interface EnhancedOutfitCardProps {
  outfit: Outfit;
  onFavorite: (id: string) => void;
  onWear: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onView?: (id: string) => void;
  onShare?: (id: string) => void;
  showActions?: boolean;
  className?: string;
}

export default function EnhancedOutfitCard({
  outfit,
  onFavorite,
  onWear,
  onEdit,
  onDelete,
  onView,
  onShare,
  showActions = true,
  className = ""
}: EnhancedOutfitCardProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleFavorite = () => onFavorite(outfit.id);
  const handleWear = () => onWear(outfit.id);
  const handleEdit = () => onEdit(outfit.id);
  const handleDeleteClick = () => setDeleteDialogOpen(true);
  const handleView = () => onView?.(outfit.id);
  const handleShare = () => onShare?.(outfit.id);
  
  const handleDeleteConfirm = () => {
    onDelete(outfit.id);
    setDeleteDialogOpen(false);
  };

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-500 bg-gray-100 dark:bg-gray-800';
    if (score >= 0.8) return 'text-amber-600 bg-green-100 dark:bg-green-900/20';
    if (score >= 0.6) return 'text-amber-600 bg-yellow-100 dark:bg-yellow-900/20';
    return 'text-red-600 bg-red-100 dark:bg-red-900/20';
  };

  const getConfidenceText = (score?: number) => {
    if (!score) return 'No Score';
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    return 'Fair';
  };

  const formatLastWorn = (dateValue?: string | number | Date | any) => {
    if (!dateValue) return 'Never worn';
    
    // Parse date from multiple formats
    let date: Date;
    if (dateValue instanceof Date) {
      date = dateValue;
    } else if (typeof dateValue === 'number') {
      date = new Date(dateValue);
    } else if (typeof dateValue === 'string') {
      date = new Date(dateValue);
    } else if (dateValue.seconds) {
      date = new Date(dateValue.seconds * 1000);
    } else if (dateValue.toDate && typeof dateValue.toDate === 'function') {
      date = dateValue.toDate();
    } else {
      return 'Invalid date';
    }
    
    // Validate date
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  return (
    <Card 
      className={`group hover:shadow-xl transition-all duration-300 border-2 hover:border-purple-200 dark:hover:border-purple-800 ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-2 mb-2">
              {outfit.name}
            </CardTitle>
            <div className="flex flex-wrap gap-1 mb-2">
              <Badge variant="secondary" className="text-xs flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {outfit.occasion}
              </Badge>
              <Badge variant="outline" className="text-xs flex items-center gap-1">
                <Palette className="h-3 w-3" />
                {outfit.style}
              </Badge>
              {outfit.mood && (
                <Badge variant="outline" className="text-xs flex items-center gap-1">
                  <Target className="h-3 w-3" />
                  {outfit.mood}
                </Badge>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            {outfit.confidence_score && (
              <Badge 
                variant="secondary" 
                className={`text-xs ${getConfidenceColor(outfit.confidence_score)}`}
              >
                <Zap className="h-3 w-3 mr-1" />
                {Math.round(outfit.confidence_score * 100)}%
              </Badge>
            )}
            
            {showActions && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {onView && (
                    <DropdownMenuItem onClick={handleView}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                  {onShare && (
                    <DropdownMenuItem onClick={handleShare}>
                      <Share2 className="h-4 w-4 mr-2" />
                      Share
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem 
                    onClick={handleDeleteClick}
                    className="text-red-600 dark:text-red-400"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Outfit Preview - Flat Lay as Hero or Item Grid */}
        <div className="mb-4">
          {/* If flat lay exists, show it as the main preview */}
          {outfit.metadata?.flat_lay_url ? (
            <div className="mb-3">
              <div className="aspect-[9/16] bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                <img
                  src={outfit.metadata.flat_lay_url}
                  alt={outfit.name}
                  className="w-full h-full object-contain hover:scale-105 transition-transform duration-200 cursor-pointer"
                  onClick={() => onView?.(outfit.id)}
                />
              </div>
              <div className="flex items-center justify-between mt-2">
                <Badge variant="secondary" className="text-xs">
                  <Eye className="h-3 w-3 mr-1" />
                  Flat Lay View
                </Badge>
                {outfit.wearCount && outfit.wearCount > 0 && (
                  <Badge variant="outline" className="text-xs">
                    <Clock className="h-3 w-3 mr-1" />
                    Worn {outfit.wearCount}x
                  </Badge>
                )}
              </div>
            </div>
          ) : (
            /* Fallback: Show item grid preview */
            <>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Items ({outfit.items.length})
                </p>
                {outfit.wearCount && outfit.wearCount > 0 && (
                  <Badge variant="outline" className="text-xs">
                    <Clock className="h-3 w-3 mr-1" />
                    Worn {outfit.wearCount}x
                  </Badge>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                {outfit.items.slice(0, 4).map((item, index) => (
                  <div key={index} className="relative group/item">
                    <div className="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                      {item.imageUrl ? (
                        <img
                          src={item.imageUrl}
                          alt={item.name}
                          className="w-full h-full object-cover group-hover/item:scale-105 transition-transform duration-200"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/placeholder.jpg';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="text-gray-400 text-xs text-center">
                            <div className="w-6 h-6 mx-auto mb-1 bg-gray-300 dark:bg-gray-600 rounded"></div>
                            <span className="text-xs">{item.type}</span>
                          </div>
                        </div>
                      )}
                    </div>
                {index === 3 && outfit.items.length > 4 && (
                  <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                    <span className="text-white text-xs font-medium">
                      +{outfit.items.length - 4}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Stats and Info */}
        <div className="space-y-2 mb-4">
          {outfit.rating && (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-3 w-3 ${
                      star <= outfit.rating!
                        ? 'text-amber-400 fill-current'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {outfit.rating} star{outfit.rating !== 1 ? 's' : ''}
              </span>
            </div>
          )}
          
          {outfit.lastWorn && (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Last worn: {formatLastWorn(outfit.lastWorn)}
            </p>
          )}
        </div>

        {/* Action Buttons */}
        {showActions && (
          <div className="flex gap-2">
            <Button
              variant={outfit.isFavorite ? "default" : "outline"}
              size="sm"
              onClick={handleFavorite}
              className={`flex-1 ${
                outfit.isFavorite 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'hover:bg-red-50 hover:text-red-600'
              }`}
            >
              {outfit.isFavorite ? (
                <Heart className="h-4 w-4 mr-1 fill-current" />
              ) : (
                <HeartOff className="h-4 w-4 mr-1" />
              )}
              {outfit.isFavorite ? 'Liked' : 'Like'}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleWear}
              className="flex-1 hover:bg-green-50 hover:text-amber-600 hover:border-green-300"
            >
              <Calendar className="h-4 w-4 mr-1" />
              Wear
            </Button>
          </div>
        )}

        {/* Hover Overlay */}
        {isHovered && (
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-lg pointer-events-none" />
        )}
      </CardContent>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Outfit</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{outfit.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
