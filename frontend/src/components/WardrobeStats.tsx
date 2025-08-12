"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  Calendar, 
  Heart, 
  Shirt, 
  Sparkles,
  BarChart3,
  RefreshCw,
  Eye,
  Clock,
  Star
} from "lucide-react";

interface WardrobeStats {
  totalItems: number;
  totalWears: number;
  averageWearsPerItem: number;
  favoriteItems: number;
  unwornItems: number;
  mostWornItem: {
    name: string;
    wearCount: number;
    type: string;
  };
  leastWornItem: {
    name: string;
    wearCount: number;
    type: string;
  };
  categoryBreakdown: {
    [key: string]: number;
  };
  colorBreakdown: {
    [key: string]: number;
  };
  seasonalCoverage: {
    spring: number;
    summer: number;
    fall: number;
    winter: number;
  };
  styleDiversity: {
    [key: string]: number;
  };
  lastUpdated: string;
}

interface WardrobeStatsProps {
  userId: string;
  onRefresh?: () => void;
}

export default function WardrobeStats({ userId, onRefresh }: WardrobeStatsProps) {
  const [stats, setStats] = useState<WardrobeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWardrobeStats();
  }, [userId]);

  const fetchWardrobeStats = async () => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API call - replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock data - replace with actual API response
      const mockStats: WardrobeStats = {
        totalItems: 47,
        totalWears: 156,
        averageWearsPerItem: 3.3,
        favoriteItems: 12,
        unwornItems: 8,
        mostWornItem: {
          name: "Blue Denim Jacket",
          wearCount: 23,
          type: "jacket"
        },
        leastWornItem: {
          name: "Red Evening Dress",
          wearCount: 0,
          type: "dress"
        },
        categoryBreakdown: {
          shirts: 15,
          pants: 12,
          jackets: 8,
          dresses: 5,
          shoes: 4,
          accessories: 3
        },
        colorBreakdown: {
          black: 12,
          blue: 10,
          white: 8,
          gray: 6,
          red: 4,
          green: 3,
          other: 4
        },
        seasonalCoverage: {
          spring: 85,
          summer: 90,
          fall: 95,
          winter: 80
        },
        styleDiversity: {
          casual: 25,
          formal: 12,
          streetwear: 8,
          vintage: 2
        },
        lastUpdated: new Date().toISOString()
      };

      setStats(mockStats);
    } catch (err) {
      setError('Failed to load wardrobe statistics');
      console.error('Error fetching wardrobe stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchWardrobeStats();
    if (onRefresh) {
      onRefresh();
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <Card key={index} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50 dark:bg-red-950/20">
        <CardContent className="pt-6">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-2">
              Failed to load statistics
            </h3>
            <p className="text-red-600 dark:text-red-300 mb-4">{error}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'shirts': return '👕';
      case 'pants': return '👖';
      case 'jackets': return '🧥';
      case 'dresses': return '👗';
      case 'shoes': return '👟';
      case 'accessories': return '💍';
      default: return '👕';
    }
  };

  const getColorIcon = (color: string) => {
    const colorMap: Record<string, string> = {
      'black': '⚫',
      'blue': '🔵',
      'white': '⚪',
      'gray': '⚪',
      'red': '🔴',
      'green': '🟢',
      'other': '🌈'
    };
    return colorMap[color] || '🌈';
  };

  const getSeasonIcon = (season: string) => {
    switch (season) {
      case 'spring': return '🌸';
      case 'summer': return '☀️';
      case 'fall': return '🍂';
      case 'winter': return '❄️';
      default: return '🌱';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Wardrobe Statistics
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Insights and analytics about your clothing collection
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Shirt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalItems}</div>
            <p className="text-xs text-muted-foreground">
              in your wardrobe
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Wears</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalWears}</div>
            <p className="text-xs text-muted-foreground">
              {stats.averageWearsPerItem.toFixed(1)} avg per item
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Favorites</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.favoriteItems}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((stats.favoriteItems / stats.totalItems) * 100)}% of items
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unworn</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.unwornItems}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((stats.unwornItems / stats.totalItems) * 100)}% of items
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Most Worn Item
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {stats.mostWornItem.wearCount}
              </div>
              <div className="text-lg font-medium mb-1">
                {stats.mostWornItem.name}
              </div>
              <Badge variant="secondary">
                {getCategoryIcon(stats.mostWornItem.type)} {stats.mostWornItem.type}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-gray-500" />
              Least Worn Item
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-600 mb-2">
                {stats.leastWornItem.wearCount}
              </div>
              <div className="text-lg font-medium mb-1">
                {stats.leastWornItem.name}
              </div>
              <Badge variant="outline">
                {getCategoryIcon(stats.leastWornItem.type)} {stats.leastWornItem.type}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Category Distribution</CardTitle>
          <CardDescription>
            How your wardrobe is organized by item type
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(stats.categoryBreakdown).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getCategoryIcon(category)}</span>
                  <span className="capitalize font-medium">{category}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32">
                    <Progress 
                      value={(count / stats.totalItems) * 100} 
                      className="h-2"
                    />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">
                    {count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Color Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Color Palette</CardTitle>
          <CardDescription>
            Your wardrobe's color distribution
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.colorBreakdown).map(([color, count]) => (
              <div key={color} className="text-center">
                <div className="text-2xl mb-2">{getColorIcon(color)}</div>
                <div className="font-medium capitalize">{color}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {count} items
                </div>
                <div className="text-xs text-gray-500">
                  {Math.round((count / stats.totalItems) * 100)}%
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Seasonal Coverage */}
      <Card>
        <CardHeader>
          <CardTitle>Seasonal Coverage</CardTitle>
          <CardDescription>
            How well your wardrobe covers different seasons
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(stats.seasonalCoverage).map(([season, coverage]) => (
              <div key={season} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getSeasonIcon(season)}</span>
                    <span className="capitalize font-medium">{season}</span>
                  </div>
                  <span className="text-sm font-medium">{coverage}%</span>
                </div>
                <Progress value={coverage} className="h-2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Style Diversity */}
      <Card>
        <CardHeader>
          <CardTitle>Style Diversity</CardTitle>
          <CardDescription>
            Variety of styles in your wardrobe
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.styleDiversity).map(([style, count]) => (
              <Badge key={style} variant="outline" className="text-sm">
                <Sparkles className="w-3 h-3 mr-1" />
                {style} ({count})
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Last updated: {new Date(stats.lastUpdated).toLocaleString()}
      </div>
    </div>
  );
}
