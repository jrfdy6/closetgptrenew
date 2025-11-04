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
    <div className="sticky top-0 z-30 bg-[#FAFAF9] dark:bg-[#1A1510] pb-4 -mx-4 px-4 border-b border-gray-200/50 dark:border-[#3D2F24]">
      {/* Horizontal scrollable filter pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {filters.map((filter) => (
          <div key={filter.label} className="flex items-center gap-1.5 flex-shrink-0">
            <span className="text-caption text-gray-600 dark:text-[#8A827A] font-medium">
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
                      "px-3 py-1.5 rounded-full text-caption font-medium transition-all duration-200",
                      "whitespace-nowrap min-h-[32px]",
                      isSelected
                        ? "gradient-primary text-white shadow-md shadow-[#FFB84C]/20"
                        : "bg-gray-100 dark:bg-[#3D2F24] text-gray-700 dark:text-[#C4BCB4] hover:bg-gray-200 dark:hover:bg-[#3D2F24]/80"
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
            className="flex items-center gap-1 px-3 py-1.5 rounded-full text-caption font-medium bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-950/30 transition-colors flex-shrink-0 ml-2"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>

      {/* Active filters count */}
      {hasActiveFilters && (
        <div className="mt-2 text-caption text-gray-600 dark:text-[#8A827A]">
          {filters.filter(f => f.selected !== 'all').length} filter(s) active
        </div>
      )}
    </div>
  );
}

