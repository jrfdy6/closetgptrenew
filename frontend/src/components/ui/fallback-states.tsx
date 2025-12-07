"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  AlertCircle, 
  Search, 
  Image as ImageIcon, 
  Sparkles, 
  RefreshCw,
  Filter,
  Heart,
  Share2,
  ArrowLeft,
  Home,
  Settings,
  HelpCircle,
  ExternalLink
} from "lucide-react";
import { useRouter } from "next/navigation";

// Base empty state component
interface EmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  secondaryActionText?: string;
  onSecondaryAction?: () => void;
  showHomeButton?: boolean;
  className?: string;
}

export const EmptyState = ({
  icon: Icon = ImageIcon,
  title,
  description,
  actionText,
  onAction,
  secondaryActionText,
  onSecondaryAction,
  showHomeButton = false,
  className = ""
}: EmptyStateProps) => {
  const router = useRouter();

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12 px-4 text-center bg-card/85 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-3xl backdrop-blur-xl shadow-lg",
      className
    )}>
      <div className="w-16 h-16 bg-secondary dark:bg-card rounded-full flex items-center justify-center mb-4 shadow-inner">
        <Icon className="w-8 h-8 text-accent" />
      </div>
      <h3 className="text-xl font-display font-semibold text-card-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-sm leading-relaxed">{description}</p>
      
      <div className="flex flex-col sm:flex-row gap-3">
        {onAction && actionText && (
          <Button onClick={onAction} size="sm" className="px-5 py-2 rounded-2xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-amber-500/15">
            {actionText}
          </Button>
        )}
        {onSecondaryAction && secondaryActionText && (
          <Button variant="outline" onClick={onSecondaryAction} size="sm" className="px-5 py-2 rounded-2xl border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary">
            {secondaryActionText}
          </Button>
        )}
        {showHomeButton && (
          <Button variant="ghost" onClick={() => router.push('/')} size="sm" className="px-5 py-2 rounded-2xl text-muted-foreground hover:text-foreground">
            <Home className="w-4 h-4 mr-2" />
            Go home
          </Button>
        )}
      </div>
    </div>
  );
};

// Error state component
interface ErrorStateProps {
  error: string;
  title?: string;
  onRetry?: () => void;
  onGoBack?: () => void;
  showHomeButton?: boolean;
  className?: string;
}

export const ErrorState = ({
  error,
  title = "Something went wrong",
  onRetry,
  onGoBack,
  showHomeButton = false,
  className = ""
}: ErrorStateProps) => {
  const router = useRouter();

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12 px-4 text-center bg-card/85 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-3xl backdrop-blur-xl shadow-lg",
      className
    )}>
      <div className="w-16 h-16 bg-destructive/10 dark:bg-destructive/20 rounded-full flex items-center justify-center mb-4 shadow-inner">
        <AlertCircle className="w-8 h-8 text-destructive" />
      </div>
      <h3 className="text-xl font-display font-semibold text-card-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-sm leading-relaxed">{error}</p>
      
      <div className="flex flex-col sm:flex-row gap-3">
        {onRetry && (
          <Button onClick={onRetry} size="sm" className="px-5 py-2 rounded-2xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-amber-500/15">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try again
          </Button>
        )}
        {onGoBack && (
          <Button variant="outline" onClick={onGoBack} size="sm" className="px-5 py-2 rounded-2xl border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go back
          </Button>
        )}
        {showHomeButton && (
          <Button variant="ghost" onClick={() => router.push('/')} size="sm" className="px-5 py-2 rounded-2xl text-muted-foreground hover:text-foreground">
            <Home className="w-4 h-4 mr-2" />
            Go home
          </Button>
        )}
      </div>
    </div>
  );
};

// No results found component
interface NoResultsProps {
  searchQuery?: string;
  filters?: string[];
  onClearFilters?: () => void;
  onNewSearch?: () => void;
  suggestions?: string[];
  className?: string;
}

export const NoResults = ({
  searchQuery,
  filters = [],
  onClearFilters,
  onNewSearch,
  suggestions = [],
  className = ""
}: NoResultsProps) => {
  return (
    <div className={cn("space-y-6", className)}>
      <div className="flex flex-col items-center justify-center py-8 px-4 text-center bg-card/85 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-3xl backdrop-blur-xl shadow-lg">
        <div className="w-16 h-16 bg-secondary dark:bg-card rounded-full flex items-center justify-center mb-4 shadow-inner">
          <Search className="w-8 h-8 text-accent" />
        </div>
        <h3 className="text-xl font-display font-semibold text-card-foreground mb-2">No results found</h3>
        <p className="text-sm text-muted-foreground mb-4 max-w-sm leading-relaxed">
          {searchQuery 
            ? `No items match "${searchQuery}"`
            : "No items match your current filters"
          }
        </p>
        
        <div className="flex flex-col sm:flex-row gap-3">
          {onClearFilters && filters.length > 0 && (
            <Button variant="outline" onClick={onClearFilters} size="sm" className="px-5 py-2 rounded-2xl border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary">
              <Filter className="w-4 h-4 mr-2" />
              Clear filters
            </Button>
          )}
          {onNewSearch && (
            <Button onClick={onNewSearch} size="sm" className="px-5 py-2 rounded-2xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-amber-500/15">
              <Search className="w-4 h-4 mr-2" />
              New search
            </Button>
          )}
        </div>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Card className="bg-card/80 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-3xl shadow-md">
          <CardContent className="p-5 space-y-3">
            <h4 className="font-semibold text-sm text-card-foreground uppercase tracking-wide">Try searching for</h4>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => onNewSearch?.()}
                  className="text-xs px-3 py-1.5 rounded-full border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary"
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Wardrobe empty state
export const WardrobeEmptyState = ({ onAddItems }: { onAddItems?: () => void }) => (
  <EmptyState
    icon={ImageIcon}
    title="Your wardrobe is empty"
    description="Start building your digital wardrobe by adding your favorite clothing items. We'll help you organize and create amazing outfits."
    actionText="Add your first item"
    onAction={onAddItems}
    secondaryActionText="Learn how it works"
    onSecondaryAction={() => window.open('/help', '_blank')}
  />
);

// Outfits empty state
export const OutfitsEmptyState = ({ onGenerateOutfit }: { onGenerateOutfit?: () => void }) => (
  <EmptyState
    icon={Sparkles}
    title="No outfits yet"
    description="Generate your first outfit to unlock personalized ideas tailored for today’s vibe."
    actionText="Generate outfit"
    onAction={onGenerateOutfit}
    secondaryActionText="Browse wardrobe"
    onSecondaryAction={() => window.location.href = '/wardrobe'}
  />
);

// Search empty state
export const SearchEmptyState = ({ 
  searchQuery,
  onClearSearch 
}: { 
  searchQuery?: string;
  onClearSearch?: () => void;
}) => (
  <EmptyState
    icon={Search}
    title={searchQuery ? `No results for "${searchQuery}"` : "No search results"}
    description="Try fresh keywords or browse your full wardrobe to spark inspiration."
    actionText="Browse all items"
    onAction={() => window.location.href = '/wardrobe'}
    secondaryActionText="Clear search"
    onSecondaryAction={onClearSearch}
  />
);

// Network error state
export const NetworkErrorState = ({ onRetry }: { onRetry?: () => void }) => (
  <ErrorState
    error="Unable to connect to the server. Please check your internet connection and try again."
    title="Connection error"
    onRetry={onRetry}
    showHomeButton
  />
);

// Permission error state
export const PermissionErrorState = ({ onGoBack }: { onGoBack?: () => void }) => (
  <ErrorState
    error="You don't have permission to access this content. Please contact support if you believe this is an error."
    title="Access denied"
    onGoBack={onGoBack}
    showHomeButton
  />
);

// Maintenance mode state
export const MaintenanceState = () => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center bg-card/85 dark:bg-card/80 border border-border/60 dark:border-border/70 rounded-3xl backdrop-blur-xl shadow-lg">
    <div className="w-16 h-16 bg-secondary/90 dark:bg-muted rounded-full flex items-center justify-center mb-4 shadow-inner">
      <Settings className="w-8 h-8 text-accent" />
    </div>
    <h3 className="text-xl font-display font-semibold text-card-foreground mb-2">Under maintenance</h3>
    <p className="text-sm text-muted-foreground mb-6 max-w-sm leading-relaxed">
      We’re upgrading Easy Outfit for an even smoother experience. Sit tight and check back shortly.
    </p>
    <div className="flex flex-col sm:flex-row gap-3">
      <Button variant="outline" size="sm" onClick={() => window.location.reload()} className="px-5 py-2 rounded-2xl border-border/60 dark:border-border/70 text-muted-foreground hover:bg-secondary">
        <RefreshCw className="w-4 h-4 mr-2" />
        Refresh page
      </Button>
      <Button variant="ghost" size="sm" onClick={() => window.open('/status', '_blank')} className="px-5 py-2 rounded-2xl text-muted-foreground hover:text-foreground">
        <ExternalLink className="w-4 h-4 mr-2" />
        Check status
      </Button>
    </div>
  </div>
);

// Feature not available state
export const FeatureNotAvailableState = ({ 
  feature,
  description 
}: { 
  feature: string;
  description?: string;
}) => (
  <EmptyState
    icon={HelpCircle}
    title={`${feature} not available`}
    description={description || `This feature is coming soon. We’re working to bring you ${feature.toLowerCase()} with a luxe Easy Outfit finish.`}
    actionText="Get notified"
    onAction={() => window.open('/notifications', '_blank')}
    secondaryActionText="Learn more"
    onSecondaryAction={() => window.open('/roadmap', '_blank')}
  />
);

// Loading timeout state
export const LoadingTimeoutState = ({ onRetry }: { onRetry?: () => void }) => (
  <ErrorState
    error="The request is taking longer than expected. This might be due to high server load or a slow connection."
    title="Loading timeout"
    onRetry={onRetry}
    showHomeButton
  />
);

// Offline state
export const OfflineState = ({ onRetry }: { onRetry?: () => void }) => (
  <ErrorState
    error="You appear to be offline. Please check your internet connection and try again."
    title="You're offline"
    onRetry={onRetry}
    showHomeButton
  />
);

// Rate limit exceeded state
export const RateLimitState = ({ onRetry }: { onRetry?: () => void }) => (
  <ErrorState
    error="You've made too many requests. Please wait a moment before trying again."
    title="Rate limit exceeded"
    onRetry={onRetry}
    showHomeButton
  />
);

// Mobile-specific empty state with larger touch targets
export const MobileEmptyState = (props: EmptyStateProps) => (
  <EmptyState
    {...props}
    className="py-16 px-6"
  />
);

// Mobile-specific error state with larger touch targets
export const MobileErrorState = (props: ErrorStateProps) => (
  <ErrorState
    {...props}
    className="py-16 px-6"
  />
); 