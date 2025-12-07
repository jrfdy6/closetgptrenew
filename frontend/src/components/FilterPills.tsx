"use client";

import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface FilterOption {
  value: string;
  label: string;
}

interface FilterPillsProps {
  filters: {
    label: string;
    options: FilterOption[];
    selected: string;
    onChange: (value: string) => void;
  }[];
  onClearAll?: () => void;
}

export default function FilterPills({ filters, onClearAll }: FilterPillsProps) {
  const hasActiveFilters = filters.some(f => f.selected !== 'all');

  return (
    <div className="sticky top-0 z-30 bg-background/95 dark:bg-background/95 pb-4 -mx-4 px-4 border-b border-border/60 dark:border-border/70 backdrop-blur-xl">
      {/* Horizontal scrollable filter pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {filters.map((filter) => (
          <div key={filter.label} className="flex items-center gap-1.5 flex-shrink-0">
            <span className="text-caption text-muted-foreground font-medium">
              {filter.label}:
            </span>
            <div className="flex gap-1.5">
              {filter.options.map((option) => {
                const isSelected = filter.selected === option.value;
                return (
                  <button
                    key={option.value}
                    onClick={() => filter.onChange(option.value)}
                    className={cn(
                      "px-3 py-1.5 rounded-full text-caption font-semibold transition-all duration-200",
                      "whitespace-nowrap min-h-[32px]",
                      isSelected
                        ? "bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-amber-500/20"
                        : "bg-secondary dark:bg-card text-muted-foreground border border-transparent hover:border-primary/40 dark:hover:border-primary/30 hover:text-foreground"
                    )}
                  >
                    {option.label}
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {/* Clear all filters button */}
        {hasActiveFilters && onClearAll && (
          <button
            onClick={onClearAll}
            className="flex items-center gap-1 px-3 py-1.5 rounded-full text-caption font-medium bg-destructive/10 dark:bg-destructive/20 text-destructive hover:bg-destructive/20 dark:hover:bg-destructive/30 transition-colors flex-shrink-0 ml-2 border border-destructive/30"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>

      {/* Active filters count */}
      {hasActiveFilters && (
        <div className="mt-2 text-caption text-muted-foreground">
          {filters.filter(f => f.selected !== 'all').length} filter(s) active
        </div>
      )}
    </div>
  );
}

