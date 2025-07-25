import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Info, AlertTriangle, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FilteringFeedbackProps {
  totalItems: number;
  filteredItems: number;
  filteringInfo: {
    season_mismatch: number;
    style_mismatch: number;
    invalid_style_tags: number;
  };
  warnings: string[];
  isFallbackMode?: boolean;
  fallbackStrategy?: {
    name: string;
    reason: string;
    relaxed_constraints: string[];
    gaps: {
      missing_types: string[];
      suggestions: string[];
      type_counts: Record<string, number>;
    };
  };
}

export function FilteringFeedback({
  totalItems,
  filteredItems,
  filteringInfo,
  warnings,
  isFallbackMode = false,
  fallbackStrategy
}: FilteringFeedbackProps) {
  const feedback = getFilteringFeedback(
    totalItems,
    filteredItems,
    filteringInfo,
    warnings,
    isFallbackMode,
    fallbackStrategy
  );

  if (feedback.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {feedback.map((message, index) => (
        <Alert
          key={index}
          variant={
            message.startsWith("⚠️") 
              ? "destructive" 
              : message.startsWith("ℹ️") 
                ? "default" 
                : "default"
          }
          className="animate-in fade-in slide-in-from-bottom-4"
        >
          {message.startsWith("⚠️") ? (
            <AlertCircle className="h-4 w-4" />
          ) : message.startsWith("ℹ️") ? (
            <Info className="h-4 w-4" />
          ) : message.startsWith("🔍") ? (
            <AlertTriangle className="h-4 w-4" />
          ) : (
            <PlusCircle className="h-4 w-4" />
          )}
          <AlertTitle>
            {message.startsWith("⚠️") 
              ? "Warning" 
              : message.startsWith("ℹ️") 
                ? "Information" 
                : message.startsWith("🔍")
                  ? "Notice"
                  : "Suggestion"}
          </AlertTitle>
          <AlertDescription className="flex flex-col gap-2">
            <span>{message.replace(/^[⚠️ℹ️🔍➕]+\s*/, '')}</span>
            {message.startsWith("➕") && (
              <Button
                variant="outline"
                size="sm"
                className="self-start"
                onClick={() => {
                  // TODO: Implement add item flow
                  console.log("Add item clicked");
                }}
              >
                Add Item
              </Button>
            )}
          </AlertDescription>
        </Alert>
      ))}
    </div>
  );
}

function getFilteringFeedback(
  totalItems: number,
  filteredItems: number,
  filteringInfo: {
    season_mismatch: number;
    style_mismatch: number;
    invalid_style_tags: number;
  },
  warnings: string[],
  isFallbackMode: boolean,
  fallbackStrategy?: FilteringFeedbackProps["fallbackStrategy"]
): string[] {
  const feedback: string[] = [];

  // Add warnings
  feedback.push(...warnings);

  // Add fallback mode notice
  if (isFallbackMode && fallbackStrategy) {
    feedback.push(
      `🔍 ${fallbackStrategy.reason}`
    );

    // Add specific feedback based on fallback strategy
    switch (fallbackStrategy.name) {
      case "versatile_items":
        feedback.push(
          `ℹ️ Using the most versatile items from your wardrobe to create a practical outfit.`
        );
        break;
      case "relaxed_types":
        feedback.push(
          `ℹ️ Relaxing type constraints to create a complete outfit.`
        );
        break;
      case "relaxed_season_style":
        feedback.push(
          `ℹ️ Relaxing season and style constraints to create a practical outfit.`
        );
        break;
    }

    // Add suggestions for missing items
    if (fallbackStrategy.gaps?.suggestions) {
      fallbackStrategy.gaps.suggestions.forEach(suggestion => {
        feedback.push(`➕ ${suggestion}`);
      });
    }
  }

  // Add filtering statistics
  if (filteredItems < totalItems) {
    if (isFallbackMode) {
      feedback.push(
        `ℹ️ Only ${filteredItems} of your ${totalItems} wardrobe items are suitable for the current conditions. ` +
        `Consider adding more items for this season or style.`
      );
    } else {
      feedback.push(
        `⚠️ Only ${filteredItems} of your ${totalItems} wardrobe items are suitable for the current conditions.`
      );
    }
  }

  if (filteringInfo.season_mismatch > 0) {
    feedback.push(
      `ℹ️ ${filteringInfo.season_mismatch} items were filtered out due to season mismatch. ` +
      `Consider adding more items for the current season.`
    );
  }

  if (filteringInfo.style_mismatch > 0) {
    feedback.push(
      `ℹ️ ${filteringInfo.style_mismatch} items were filtered out due to style mismatch. ` +
      `Consider adding more items in your preferred styles.`
    );
  }

  if (filteringInfo.invalid_style_tags > 0) {
    feedback.push(
      `ℹ️ ${filteringInfo.invalid_style_tags} items had invalid style tags that were normalized. ` +
      `Please update these items with valid style tags.`
    );
  }

  return feedback;
}

function getMissingItemTypes(filteringInfo: {
  season_mismatch: number;
  style_mismatch: number;
  invalid_style_tags: number;
}): string[] {
  // This is a placeholder - in a real implementation, you would analyze the wardrobe
  // to determine which common item types are missing
  return ["tops", "bottoms", "outerwear"];
} 