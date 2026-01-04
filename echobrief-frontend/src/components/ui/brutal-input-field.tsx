import * as React from "react";
import { BrutalInput, BrutalInputProps } from "./brutal-input";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BrutalInputFieldProps extends BrutalInputProps {
  label?: string;
  icon?: LucideIcon;
  containerClassName?: string;
}

const BrutalInputField = React.forwardRef<HTMLInputElement, BrutalInputFieldProps>(
  ({ label, icon: Icon, containerClassName, className, ...props }, ref) => {
    return (
      <div className={containerClassName}>
        {label && (
          <label className="block text-sm font-bold uppercase mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          <BrutalInput
            ref={ref}
            className={cn(
              Icon ? "pl-11" : "",
              "peer transition-all duration-200 ease-in-out",
              className
            )}
            {...props}
          />
          {Icon && (
            <Icon className="absolute left-3 top-1/2 -mt-2.5 w-5 h-5 text-muted-foreground pointer-events-none transition-all duration-200 ease-in-out peer-focus:-translate-x-0.5 peer-focus:-translate-y-0.5" />
          )}
        </div>
      </div>
    );
  }
);
BrutalInputField.displayName = "BrutalInputField";

export { BrutalInputField };
