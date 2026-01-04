import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const brutalCardVariants = cva(
  "border-[3px] border-foreground bg-card transition-all duration-150",
  {
    variants: {
      variant: {
        default: "shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5",
        static: "shadow-brutal",
        primary: "bg-primary shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5",
        secondary: "bg-secondary shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5",
        accent: "bg-accent shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5",
        success: "bg-success shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5",
      },
      padding: {
        none: "p-0",
        sm: "p-4",
        default: "p-6",
        lg: "p-8",
      },
    },
    defaultVariants: {
      variant: "default",
      padding: "default",
    },
  }
);

export interface BrutalCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof brutalCardVariants> {}

const BrutalCard = React.forwardRef<HTMLDivElement, BrutalCardProps>(
  ({ className, variant, padding, ...props }, ref) => {
    return (
      <div
        className={cn(brutalCardVariants({ variant, padding, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
BrutalCard.displayName = "BrutalCard";

export { BrutalCard, brutalCardVariants };
