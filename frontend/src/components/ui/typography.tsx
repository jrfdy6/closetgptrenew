"use client";

import { cn } from "@/lib/utils";
import { ReactNode } from "react";

// Base typography component with mobile responsiveness
interface TypographyProps {
  children: ReactNode;
  className?: string;
  as?: keyof JSX.IntrinsicElements;
}

export const Typography = ({ 
  children, 
  className = "", 
  as: Component = "div" 
}: TypographyProps) => (
  <Component className={cn("text-foreground", className)}>
    {children}
  </Component>
);

// Heading components with responsive sizing
interface HeadingProps extends TypographyProps {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
}

export const Heading = ({ 
  children, 
  className = "", 
  level = 1,
  as 
}: HeadingProps) => {
  const baseClasses = "font-semibold tracking-tight";
  const sizeClasses = {
    1: "text-2xl sm:text-3xl md:text-4xl lg:text-5xl",
    2: "text-xl sm:text-2xl md:text-3xl lg:text-4xl",
    3: "text-lg sm:text-xl md:text-2xl lg:text-3xl",
    4: "text-base sm:text-lg md:text-xl lg:text-2xl",
    5: "text-sm sm:text-base md:text-lg lg:text-xl",
    6: "text-xs sm:text-sm md:text-base lg:text-lg"
  };

  const Component = as || `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <Typography
      as={Component}
      className={cn(baseClasses, sizeClasses[level], className)}
    >
      {children}
    </Typography>
  );
};

// Text components with responsive sizing
interface TextProps extends TypographyProps {
  size?: "xs" | "sm" | "base" | "lg" | "xl" | "2xl";
  weight?: "normal" | "medium" | "semibold" | "bold";
  color?: "default" | "muted" | "primary" | "secondary" | "destructive";
  align?: "left" | "center" | "right" | "justify";
  leading?: "tight" | "normal" | "relaxed" | "loose";
}

export const Text = ({ 
  children, 
  className = "",
  size = "base",
  weight = "normal",
  color = "default",
  align = "left",
  leading = "normal",
  as = "p"
}: TextProps) => {
  const sizeClasses = {
    xs: "text-xs",
    sm: "text-sm",
    base: "text-base",
    lg: "text-lg",
    xl: "text-xl",
    "2xl": "text-xl sm:text-2xl"
  };

  const weightClasses = {
    normal: "font-normal",
    medium: "font-medium",
    semibold: "font-semibold",
    bold: "font-bold"
  };

  const colorClasses = {
    default: "text-foreground",
    muted: "text-muted-foreground",
    primary: "text-primary",
    secondary: "text-secondary-foreground",
    destructive: "text-destructive"
  };

  const alignClasses = {
    left: "text-left",
    center: "text-center",
    right: "text-right",
    justify: "text-justify"
  };

  const leadingClasses = {
    tight: "leading-tight",
    normal: "leading-normal",
    relaxed: "leading-relaxed",
    loose: "leading-loose"
  };

  return (
    <Typography
      as={as}
      className={cn(
        sizeClasses[size],
        weightClasses[weight],
        colorClasses[color],
        alignClasses[align],
        leadingClasses[leading],
        className
      )}
    >
      {children}
    </Typography>
  );
};

// Label component
interface LabelProps extends TypographyProps {
  required?: boolean;
  htmlFor?: string;
}

export const Label = ({ 
  children, 
  className = "",
  required = false,
  htmlFor,
  as = "label"
}: LabelProps) => (
  <Typography
    as={as}
    htmlFor={htmlFor}
    className={cn(
      "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className
    )}
  >
    {children}
    {required && <span className="text-destructive ml-1">*</span>}
  </Typography>
);

// Caption component for small text
export const Caption = ({ 
  children, 
  className = "",
  as = "p"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn("text-xs text-muted-foreground", className)}
  >
    {children}
  </Typography>
);

// Blockquote component
export const Blockquote = ({ 
  children, 
  className = "",
  as = "blockquote"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn(
      "mt-6 border-l-2 border-primary pl-6 italic text-muted-foreground",
      className
    )}
  >
    {children}
  </Typography>
);

// Code component
export const Code = ({ 
  children, 
  className = "",
  as = "code"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn(
      "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm",
      className
    )}
  >
    {children}
  </Typography>
);

// Pre component for code blocks
export const Pre = ({ 
  children, 
  className = "",
  as = "pre"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn(
      "overflow-x-auto rounded-lg border bg-muted p-4",
      className
    )}
  >
    {children}
  </Typography>
);

// List components
export const List = ({ 
  children, 
  className = "",
  as = "ul"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn("my-6 ml-6 list-disc [&>li]:mt-2", className)}
  >
    {children}
  </Typography>
);

export const OrderedList = ({ 
  children, 
  className = "",
  as = "ol"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn("my-6 ml-6 list-decimal [&>li]:mt-2", className)}
  >
    {children}
  </Typography>
);

// Link component
interface LinkProps extends TypographyProps {
  href?: string;
  external?: boolean;
  underline?: boolean;
}

export const Link = ({ 
  children, 
  className = "",
  href,
  external = false,
  underline = false,
  as = "a"
}: LinkProps) => (
  <Typography
    as={as}
    href={href}
    target={external ? "_blank" : undefined}
    rel={external ? "noopener noreferrer" : undefined}
    className={cn(
      "text-primary hover:text-primary/80 transition-colors",
      underline && "underline",
      className
    )}
  >
    {children}
    {external && (
      <span className="ml-1 inline-block">
        <svg
          className="h-3 w-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
          />
        </svg>
      </span>
    )}
  </Typography>
);

// Divider component
export const Divider = ({ 
  className = "",
  as = "hr"
}: Omit<TypographyProps, "children">) => (
  <Typography
    as={as}
    className={cn("border-t border-border my-4", className)}
  />
);

// Section component for content grouping
interface SectionProps extends TypographyProps {
  spacing?: "none" | "sm" | "md" | "lg" | "xl";
}

export const Section = ({ 
  children, 
  className = "",
  spacing = "md",
  as = "section"
}: SectionProps) => {
  const spacingClasses = {
    none: "",
    sm: "space-y-2",
    md: "space-y-4",
    lg: "space-y-6",
    xl: "space-y-8"
  };

  return (
    <Typography
      as={as}
      className={cn(spacingClasses[spacing], className)}
    >
      {children}
    </Typography>
  );
};

// Container component for responsive width
interface ContainerProps extends TypographyProps {
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  padding?: "none" | "sm" | "md" | "lg" | "xl";
}

export const Container = ({ 
  children, 
  className = "",
  maxWidth = "lg",
  padding = "md",
  as = "div"
}: ContainerProps) => {
  const maxWidthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    full: "max-w-full"
  };

  const paddingClasses = {
    none: "",
    sm: "px-2 sm:px-4",
    md: "px-4 sm:px-6",
    lg: "px-6 sm:px-8",
    xl: "px-8 sm:px-12"
  };

  return (
    <Typography
      as={as}
      className={cn(
        "mx-auto",
        maxWidthClasses[maxWidth],
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </Typography>
  );
};

// Truncate text component
export const Truncate = ({ 
  children, 
  className = "",
  lines = 1,
  as = "div"
}: TypographyProps & { lines?: number }) => {
  const lineClampClasses = {
    1: "line-clamp-1",
    2: "line-clamp-2",
    3: "line-clamp-3",
    4: "line-clamp-4",
    5: "line-clamp-5"
  };

  return (
    <Typography
      as={as}
      className={cn(lineClampClasses[lines as keyof typeof lineClampClasses], className)}
    >
      {children}
    </Typography>
  );
};

// Highlight text component
export const Highlight = ({ 
  children, 
  className = "",
  as = "mark"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn("bg-yellow-100 dark:bg-yellow-900/20 px-1 rounded", className)}
  >
    {children}
  </Typography>
);

// Keyboard shortcut component
export const Kbd = ({ 
  children, 
  className = "",
  as = "kbd"
}: TypographyProps) => (
  <Typography
    as={as}
    className={cn(
      "pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground",
      className
    )}
  >
    {children}
  </Typography>
); 