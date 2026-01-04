import React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface PageSizeSelectorProps {
  value: number;
  onChange: (value: number) => void;
  options?: number[];
  className?: string;
}

export const PageSizeSelector: React.FC<PageSizeSelectorProps> = ({
  value,
  onChange,
  options = [10, 20, 50, 100],
  className,
}) => {
  return (
    <div className={cn("relative inline-block", className)}>
      <select
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="appearance-none bg-card border-[2px] border-foreground px-4 py-2 pr-10 font-bold text-sm cursor-pointer shadow-brutal hover:bg-muted transition-all focus:outline-none focus:translate-x-0.5 focus:translate-y-0.5 focus:shadow-none"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option} per page
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" />
    </div>
  );
};
