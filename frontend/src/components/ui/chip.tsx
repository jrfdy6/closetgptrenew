"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const chipVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-full transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FFB84C] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-[#2C2119] border border-[#3D2F24] text-[#F8F5F1] hover:bg-[#3D2F24]",
        selected:
          "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] border-none text-[#1A1510] font-medium",
        mood:
          "bg-transparent border border-[#3D2F24] text-[#F8F5F1] hover:border-[#FFB84C]",
        moodSelected:
          "bg-[#3D2F24] border border-[#FFB84C] text-[#F8F5F1]",
        style:
          "bg-transparent border border-[#3D2F24] text-[#F8F5F1] hover:bg-[#3D2F24]",
        styleSelected:
          "bg-[#3D2F24] border border-[#FFB84C] text-[#F8F5F1]",
      },
      size: {
        default: "h-8 px-4 text-xs", // 32px height for occasion chips
        mood: "h-9 px-5 text-sm", // 36px height for mood chips
        style: "h-8 px-[18px] text-xs", // 32px height for style chips
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ChipProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof chipVariants> {
  selected?: boolean;
}

const Chip = React.forwardRef<HTMLButtonElement, ChipProps>(
  ({ className, variant, size, selected, ...props }, ref) => {
    // Auto-select variant based on selected state
    let finalVariant = variant;
    if (selected) {
      if (variant === "mood") finalVariant = "moodSelected";
      else if (variant === "style") finalVariant = "styleSelected";
      else if (variant === "default" || !variant) finalVariant = "selected";
    }

    return (
      <button
        className={cn(chipVariants({ variant: finalVariant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Chip.displayName = "Chip";

export { Chip, chipVariants };

