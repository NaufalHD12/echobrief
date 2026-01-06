import * as React from "react";
import { BrutalInput, BrutalInputProps } from "./brutal-input";
import { LucideIcon, Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BrutalInputFieldProps extends BrutalInputProps {
  label?: string;
  icon?: LucideIcon;
  containerClassName?: string;
}

const BrutalInputField = React.forwardRef<HTMLInputElement, BrutalInputFieldProps>(
  ({ label, icon: Icon, containerClassName, className, type, ...props }, ref) => {
    const [isPasswordVisible, setIsPasswordVisible] = React.useState(false);
    const isPasswordType = type === "password";
    const inputType = isPasswordType
      ? isPasswordVisible
        ? "text"
        : "password"
      : type;

    const togglePasswordVisibility = () => {
      setIsPasswordVisible(!isPasswordVisible);
    };


    const inputClassName = cn(
      Icon ? "pl-11" : "",
      isPasswordType ? "pr-11" : "",
      "peer transition-all duration-200 ease-in-out",
      className
    );

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
            type={inputType}
            className={inputClassName}
            {...props}
          />
          {Icon && (
            <Icon className="absolute left-3 top-1/2 -mt-2.5 w-5 h-5 text-muted-foreground pointer-events-none transition-all duration-200 ease-in-out peer-focus:-translate-x-0.5 peer-focus:-translate-y-0.5" />
          )}
          {isPasswordType && (
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="absolute right-3 top-1/2 -mt-2.5 w-5 h-5 text-muted-foreground hover:text-foreground transition-all duration-200 ease-in-out focus:outline-none peer-focus:-translate-x-0.5 peer-focus:-translate-y-0.5"
              tabIndex={-1}
            >
              {isPasswordVisible ? (
                <EyeOff className="w-5 h-5" />
              ) : (
                <Eye className="w-5 h-5" />
              )}
            </button>
          )}
        </div>
      </div>
    );
  }
);
BrutalInputField.displayName = "BrutalInputField";

export { BrutalInputField };
