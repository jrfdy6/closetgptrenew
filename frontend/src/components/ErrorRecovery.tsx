"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  AlertCircle, 
  RefreshCw, 
  Home, 
  Upload, 
  Settings,
  HelpCircle,
  ArrowLeft,
  Sparkles
} from "lucide-react";

interface ErrorRecoveryProps {
  error: Error | string;
  context?: {
    action?: string;
    itemCount?: number;
    minRequired?: number;
    page?: string;
  };
  onRetry?: () => void;
  onGoBack?: () => void;
}

export default function ErrorRecovery({
  error,
  context,
  onRetry,
  onGoBack
}: ErrorRecoveryProps) {
  const errorMessage = typeof error === 'string' ? error : error.message;
  
  // Analyze error and provide appropriate recovery options
  const getRecoveryStrategy = () => {
    const lowerError = errorMessage.toLowerCase();
    
    // Insufficient items error
    if (lowerError.includes('insufficient') || lowerError.includes('not enough')) {
      return {
        type: 'insufficient_items',
        title: 'Need More Items',
        message: context?.itemCount && context?.minRequired
          ? `You have ${context.itemCount} items, but we need at least ${context.minRequired} to generate this outfit.`
          : 'You need a few more items in your wardrobe to generate this outfit.',
        icon: Upload,
        primaryAction: {
          label: 'Add More Items',
          icon: Upload,
          action: () => window.location.href = '/wardrobe?action=upload'
        },
        secondaryActions: [
          {
            label: 'Try Simpler Outfit',
            action: onRetry
          },
          {
            label: 'View Saved Outfits',
            action: () => window.location.href = '/outfits?view=saved'
          }
        ]
      };
    }
    
    // Network/timeout errors
    if (lowerError.includes('network') || lowerError.includes('timeout') || lowerError.includes('fetch')) {
      return {
        type: 'network',
        title: 'Connection Issue',
        message: 'We couldn\'t reach our servers. Please check your internet connection and try again.',
        icon: RefreshCw,
        primaryAction: {
          label: 'Try Again',
          icon: RefreshCw,
          action: onRetry
        },
        secondaryActions: [
          {
            label: 'Go to Dashboard',
            action: () => window.location.href = '/dashboard'
          }
        ]
      };
    }
    
    // Authentication errors
    if (lowerError.includes('auth') || lowerError.includes('unauthorized') || lowerError.includes('401')) {
      return {
        type: 'auth',
        title: 'Authentication Required',
        message: 'Your session may have expired. Please sign in again.',
        icon: Settings,
        primaryAction: {
          label: 'Sign In',
          icon: Settings,
          action: () => window.location.href = '/signin'
        },
        secondaryActions: []
      };
    }
    
    // AI generation errors
    if (lowerError.includes('generation') || lowerError.includes('ai') || lowerError.includes('outfit')) {
      return {
        type: 'generation',
        title: 'Outfit Generation Failed',
        message: 'We encountered an issue generating your outfit. This could be due to conflicting style preferences or limited wardrobe options.',
        icon: Sparkles,
        primaryAction: {
          label: 'Try Different Style',
          icon: RefreshCw,
          action: onRetry
        },
        secondaryActions: [
          {
            label: 'View Previous Outfits',
            action: () => window.location.href = '/outfits'
          },
          {
            label: 'Browse Wardrobe',
            action: () => window.location.href = '/wardrobe'
          }
        ]
      };
    }
    
    // Generic error
    return {
      type: 'generic',
      title: 'Something Went Wrong',
      message: errorMessage || 'An unexpected error occurred. We\'re here to help!',
      icon: AlertCircle,
      primaryAction: {
        label: 'Try Again',
        icon: RefreshCw,
        action: onRetry
      },
      secondaryActions: [
        {
          label: onGoBack ? 'Go Back' : 'Go to Dashboard',
          action: onGoBack || (() => window.location.href = '/dashboard')
        },
        {
          label: 'Contact Support',
          action: () => window.location.href = '/support'
        }
      ]
    };
  };
  
  const strategy = getRecoveryStrategy();
  const Icon = strategy.icon;
  
  return (
    <div className="min-h-[400px] flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <Icon className="h-8 w-8 text-red-600 dark:text-red-400" />
          </div>
          <CardTitle className="text-2xl">{strategy.title}</CardTitle>
          <CardDescription className="text-base mt-2">
            {strategy.message}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Primary Action */}
          {strategy.primaryAction && strategy.primaryAction.action && (
            <Button
              onClick={strategy.primaryAction.action}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              size="lg"
            >
              {strategy.primaryAction.icon && <strategy.primaryAction.icon className="h-5 w-5 mr-2" />}
              {strategy.primaryAction.label}
            </Button>
          )}
          
          {/* Secondary Actions */}
          {strategy.secondaryActions && strategy.secondaryActions.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {strategy.secondaryActions.map((action, index) => (
                action.action && (
                  <Button
                    key={index}
                    onClick={action.action}
                    variant="outline"
                    className="w-full"
                  >
                    {action.label}
                  </Button>
                )
              ))}
            </div>
          )}
          
          {/* Help Text */}
          <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
            <HelpCircle className="h-4 w-4" />
            <AlertDescription className="text-sm">
              {strategy.type === 'insufficient_items' && (
                <>
                  <strong>Tip:</strong> We recommend having at least 10-15 items (2-3 tops, 2-3 bottoms, outerwear, shoes) for the best outfit suggestions.
                </>
              )}
              {strategy.type === 'network' && (
                <>
                  <strong>Tip:</strong> If this persists, try refreshing the page or clearing your browser cache.
                </>
              )}
              {strategy.type === 'generation' && (
                <>
                  <strong>Tip:</strong> Try adjusting your occasion or style preferences, or add more variety to your wardrobe.
                </>
              )}
              {strategy.type === 'generic' && (
                <>
                  <strong>Need help?</strong> Contact us at support@easyoutfitapp.com or check the browser console (F12) for technical details.
                </>
              )}
            </AlertDescription>
          </Alert>
          
          {/* Technical Details (Collapsed) */}
          <details className="text-sm text-gray-500 dark:text-gray-400">
            <summary className="cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
              Technical details
            </summary>
            <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-900 rounded-lg font-mono text-xs break-all">
              {errorMessage}
            </div>
          </details>
        </CardContent>
      </Card>
    </div>
  );
}

