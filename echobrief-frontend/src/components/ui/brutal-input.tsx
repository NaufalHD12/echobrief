import * as React from "react";
import { cn } from "@/lib/utils";

export interface BrutalInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const BrutalInput = React.forwardRef<HTMLInputElement, BrutalInputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-12 w-full border-[3px] border-foreground bg-background px-4 py-2 text-base font-medium shadow-brutal transition-all placeholder:text-muted-foreground focus:outline-none focus:shadow-brutal-hover focus:-translate-x-0.5 focus:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
BrutalInput.displayName = "BrutalInput";

export { BrutalInput };
