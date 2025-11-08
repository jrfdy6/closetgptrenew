import React from "react";
import { cn } from "@/lib/utils";

interface CarouselSlideProps {
  children: React.ReactNode;
  className?: string;
}

export default function CarouselSlide({ children, className }: CarouselSlideProps) {
  return <div className={cn("h-full", className)}>{children}</div>;
}

