import React from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface OutfitWarningsProps {
  warnings?: Array<string | object>;
  validationErrors?: Array<string | object>;
  validationDetails?: {
    errors?: Array<string | object>;
    warnings?: Array<string | object>;
    fixes?: Array<{
      method: string;
      original_error: string;
      applied: boolean;
    }>;
  };
  wasSuccessful?: boolean;
  className?: string;
}

export function OutfitWarnings({
  warnings = [],
  validationErrors = [],
  validationDetails,
  wasSuccessful = true,
  className
}: OutfitWarningsProps) {
  // Debug logging to help identify the issue
  if (process.env.NODE_ENV === 'development') {
    console.log('OutfitWarnings props:', {
      warnings,
      validationErrors,
      validationDetails,
      wasSuccessful
    });
  }

  // Helper function to convert any value to string
  const convertToString = (value: any): string => {
    if (typeof value === 'string') return value;
    if (typeof value === 'object' && value !== null) {
      // If it's an object with a message property, use that
      if (value.message) return value.message;
      // If it's an object with a step property, format it
      if (value.step) return `${value.step}: ${value.message || JSON.stringify(value)}`;
      // Otherwise, stringify the object
      return JSON.stringify(value);
    }
    return String(value);
  };

  // Combine all warnings and errors, ensuring they're strings
  const allWarnings = [
    ...warnings.map(convertToString),
    ...(validationDetails?.warnings || []).map(convertToString)
  ];
  
  const allErrors = [
    ...validationErrors.map(convertToString),
    ...(validationDetails?.errors || []).map(convertToString)
  ];

  const appliedFixes = validationDetails?.fixes?.filter(fix => fix.applied) || [];
  const failedFixes = validationDetails?.fixes?.filter(fix => !fix.applied) || [];

  if (allWarnings.length === 0 && allErrors.length === 0 && appliedFixes.length === 0) {
    return null;
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Success/Failure Status */}
      {wasSuccessful !== undefined && (
        <div className={cn(
          "flex items-center gap-2 p-3 rounded-lg",
          wasSuccessful 
            ? "bg-green-50 border border-green-200 text-green-800"
            : "bg-red-50 border border-red-200 text-red-800"
        )}>
          {wasSuccessful ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <XCircle className="h-4 w-4" />
          )}
          <span className="text-sm font-medium">
            {wasSuccessful ? "Outfit generated successfully" : "Outfit generation had issues"}
          </span>
        </div>
      )}

      {/* Applied Fixes */}
      {appliedFixes.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">
              Automatic Improvements Applied
            </span>
          </div>
          <ul className="space-y-1">
            {appliedFixes.map((fix, index) => (
              <li key={index} className="text-sm text-blue-700 flex items-start gap-2">
                <span className="text-blue-500">•</span>
                <span>
                  <span className="font-medium">{fix.method}:</span> {typeof fix.original_error === 'string' ? fix.original_error : JSON.stringify(fix.original_error)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {allWarnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-800">
              Suggestions & Recommendations
            </span>
          </div>
          <ul className="space-y-1">
            {allWarnings.map((warning, index) => (
              <li key={index} className="text-sm text-yellow-700 flex items-start gap-2">
                <span className="text-yellow-500">•</span>
                <span>{typeof warning === 'string' ? warning : JSON.stringify(warning)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Errors */}
      {allErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="h-4 w-4 text-red-600" />
            <span className="text-sm font-medium text-red-800">
              Issues Found
            </span>
          </div>
          <ul className="space-y-1">
            {allErrors.map((error, index) => (
              <li key={index} className="text-sm text-red-700 flex items-start gap-2">
                <span className="text-red-500">•</span>
                <span>{typeof error === 'string' ? error : JSON.stringify(error)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Failed Fixes */}
      {failedFixes.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Info className="h-4 w-4 text-orange-600" />
            <span className="text-sm font-medium text-orange-800">
              Issues That Couldn't Be Fixed Automatically
            </span>
          </div>
          <ul className="space-y-1">
            {failedFixes.map((fix, index) => (
              <li key={index} className="text-sm text-orange-700 flex items-start gap-2">
                <span className="text-orange-500">•</span>
                <span>
                  <span className="font-medium">{fix.method}:</span> {typeof fix.original_error === 'string' ? fix.original_error : JSON.stringify(fix.original_error)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 