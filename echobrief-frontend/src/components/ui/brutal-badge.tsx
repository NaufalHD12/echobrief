import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const brutalBadgeVariants = cva(
  "inline-flex items-center border-[2px] border-foreground font-bold uppercase tracking-wide shadow-[2px_2px_0px_0px_hsl(var(--foreground))]",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        secondary: "bg-secondary text-secondary-foreground",
        accent: "bg-accent text-accent-foreground",
        success: "bg-success text-success-foreground",
        outline: "bg-background text-foreground",
      },
      size: {
        sm: "px-2 py-0.5 text-[10px]",
        default: "px-3 py-1 text-xs",
        lg: "px-4 py-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface BrutalBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof brutalBadgeVariants> {}

const BrutalBadge = React.forwardRef<HTMLSpanElement, BrutalBadgeProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <span
        className={cn(brutalBadgeVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
BrutalBadge.displayName = "BrutalBadge";

export { BrutalBadge, brutalBadgeVariants };
