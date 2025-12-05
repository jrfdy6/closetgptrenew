"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FFB84C] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:-translate-y-0.5 active:scale-[0.98]",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] shadow-md hover:shadow-lg hover:shadow-[#FFB84C]/30",
        destructive:
          "bg-destructive text-destructive-foreground shadow-md hover:bg-destructive/90 hover:shadow-lg hover:shadow-red-500/20",
        outline:
          "border border-[#3D2F24] bg-[#2C2119] text-[#F8F5F1] shadow-md hover:bg-[#3D2F24] hover:border-[#FFB84C] hover:shadow-lg hover:shadow-[#FFB84C]/20",
        secondary:
          "bg-[#3D2F24] text-[#F8F5F1] shadow-md hover:bg-[#3D2F24]/80 hover:shadow-lg",
        ghost: "hover:bg-[#3D2F24] hover:text-[#F8F5F1] text-[#C4BCB4]",
        link: "text-[#FFB84C] underline-offset-4 hover:underline hover:text-[#FF9400]",
      },
      size: {
        default: "h-11 min-h-[44px] px-4 py-2.5", // 44px minimum for mobile accessibility
        sm: "h-11 min-h-[44px] rounded-lg px-4 text-sm", // Increased from 32px to 44px for mobile
        lg: "h-12 min-h-[44px] rounded-xl px-8 text-base",
        icon: "h-11 w-11 min-h-[44px] min-w-[44px]", // 44px minimum for mobile
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants }; 