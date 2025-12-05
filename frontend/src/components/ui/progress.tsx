"use client";

import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
      "relative h-1 w-full overflow-hidden rounded-full bg-[#3D2F24]",
      className
    )}
    {...props}
  >
    <motion.div
      className="h-full w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400]"
      initial={{ width: 0 }}
      animate={{ width: `${value || 0}%` }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    />
  </ProgressPrimitive.Root>
));
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress }; 