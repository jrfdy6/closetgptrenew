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
    <div className="sticky top-0 z-30 bg-[#FAFAF9]/95 dark:bg-[#1A1510]/95 pb-4 -mx-4 px-4 border-b border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 backdrop-blur-xl">
      {/* Horizontal scrollable filter pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {filters.map((filter) => (
          <div key={filter.label} className="flex items-center gap-1.5 flex-shrink-0">
            <span className="text-caption text-[#57534E] dark:text-[#C4BCB4] font-medium">
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
                        ? "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white shadow-md shadow-amber-500/20"
                        : "bg-[#F5F0E8] dark:bg-[#2C2119] text-[#57534E] dark:text-[#C4BCB4] border border-transparent hover:border-[#FFB84C]/40 dark:hover:border-[#FFB84C]/30 hover:text-[#1C1917] dark:hover:text-[#F8F5F1]"
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
            className="flex items-center gap-1 px-3 py-1.5 rounded-full text-caption font-medium bg-[#FFF0EC] dark:bg-[#3D211F] text-[#FF6F61] hover:bg-[#FFE2DC] dark:hover:bg-[#4A2B29] transition-colors flex-shrink-0 ml-2 border border-[#FF6F61]/30"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>

      {/* Active filters count */}
      {hasActiveFilters && (
        <div className="mt-2 text-caption text-[#57534E] dark:text-[#C4BCB4]">
          {filters.filter(f => f.selected !== 'all').length} filter(s) active
        </div>
      )}
    </div>
  );
}

