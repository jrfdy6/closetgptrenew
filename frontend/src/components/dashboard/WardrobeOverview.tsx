'use client';

import { useWardrobe } from '@/hooks/useWardrobe';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Shirt, 
  Users, 
  Footprints, 
  Layers, 
  Plus,
  TrendingUp,
  Palette,
  Calendar,
  Star
} from 'lucide-react';

export default function WardrobeOverview() {
  const { wardrobe, loading, error } = useWardrobe();

  if (loading) {
    return (
      <Card className="overflow-hidden border border-border bg-card shadow-xl">
        <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Shirt className="w-6 h-6" />
            </div>
            <span>Wardrobe Overview</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-3/4"></div>
            <div className="h-32 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="overflow-hidden border border-border bg-card shadow-xl">
        <CardHeader className="bg-gradient-to-r from-red-600 to-pink-600 text-white">
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Shirt className="w-6 h-6" />
            </div>
            <span>Wardrobe Overview</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-red-500">{error}</div>
        </CardContent>
      </Card>
    );
  }

  const totalItems = wardrobe?.length || 0;
  
  // Calculate item type distribution
  const itemTypes = wardrobe?.reduce((acc, item) => {
    const type = item.type || 'other';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  // Calculate color distribution
  const colors = wardrobe?.reduce((acc, item) => {
    const color = item.color || 'unknown';
    acc[color] = (acc[color] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  // Get top colors
  const topColors = Object.entries(colors)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'shirt': return <Shirt className="w-4 h-4" />;
      case 'pants': return <Footprints className="w-4 h-4" />;
      case 'shoes': return <Footprints className="w-4 h-4" />;
      case 'jacket': return <Layers className="w-4 h-4" />;
      default: return <Shirt className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'shirt': return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      case 'pants': return 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20';
      case 'shoes': return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20';
      case 'jacket': return 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20';
      default: return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <Card className="overflow-hidden border border-border bg-card shadow-xl">
      <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Shirt className="w-6 h-6" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold">Wardrobe Overview</CardTitle>
              <p className="text-green-100 text-sm">Your complete style collection</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{totalItems}</div>
            <div className="text-green-100 text-sm">Total Items</div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{itemTypes.shirt || 0}</div>
            <div className="text-sm text-blue-700 dark:text-blue-300">Tops</div>
          </div>
          <div className="text-center p-4 bg-green-500/10 rounded-xl border border-green-500/20">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{itemTypes.pants || 0}</div>
            <div className="text-sm text-green-700 dark:text-green-300">Bottoms</div>
          </div>
          <div className="text-center p-4 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{itemTypes.shoes || 0}</div>
            <div className="text-sm text-purple-700 dark:text-purple-300">Shoes</div>
          </div>
          <div className="text-center p-4 bg-orange-500/10 rounded-xl border border-orange-500/20">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{itemTypes.jacket || 0}</div>
            <div className="text-sm text-orange-700 dark:text-orange-300">Outerwear</div>
          </div>
        </div>

        {/* Item Type Breakdown */}
        <div className="space-y-4">
          <h3 className="font-semibold text-foreground flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            Item Distribution
          </h3>
          <div className="space-y-3">
            {Object.entries(itemTypes).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between p-3 bg-card rounded-lg border border-border hover:border-border/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getTypeColor(type)}`}>
                    {getTypeIcon(type)}
                  </div>
                  <div>
                    <p className="font-medium text-foreground capitalize">{type}</p>
                    <p className="text-sm text-muted-foreground">{count} items</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-muted-foreground">
                    {Math.round((count / totalItems) * 100)}%
                  </div>
                  <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full"
                      style={{ width: `${(count / totalItems) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Color Palette */}
        {topColors.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Palette className="w-4 h-4 text-purple-500" />
              Color Palette
            </h3>
            <div className="flex flex-wrap gap-2">
              {topColors.map(([color, count]) => (
                <div key={color} className="flex items-center gap-2 p-2 bg-card rounded-lg border border-border">
                  <div 
                    className="w-4 h-4 rounded-full border border-border"
                    style={{ backgroundColor: color.toLowerCase() }}
                  />
                  <span className="text-sm font-medium text-foreground capitalize">{color}</span>
                  <Badge variant="outline" className="text-xs">{count}</Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-4">
          <Button 
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add New Item
          </Button>
        </div>
      </CardContent>
    </Card>
  );
} 