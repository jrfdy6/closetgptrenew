"use client";

import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";
import { motion, useReducedMotion } from "framer-motion";

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => {
  const reduceMotion = useReducedMotion();
  const boundedValue = typeof value === 'number' && Number.isFinite(value) ? Math.max(0, Math.min(value, 100)) : null;
  return (
  <ProgressPrimitive.Root
    ref={ref}
    value={boundedValue}
    className={cn(
      "relative h-1 w-full overflow-hidden rounded-full bg-muted",
      className
    )}
    {...props}
  >
    <motion.div
      className="h-full w-full gradient-copper-gold"
      initial={reduceMotion ? false : { width: 0 }}
      animate={{ width: `${boundedValue ?? 0}%` }}
      transition={{ duration: reduceMotion ? 0 : 0.3, ease: "easeOut" }}
    />
  </ProgressPrimitive.Root>
);
});
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress }; 