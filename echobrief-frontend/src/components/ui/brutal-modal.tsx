import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { BrutalButton } from "@/components/ui/brutal-button";
import { cn } from "@/lib/utils";
import { Check, AlertTriangle, Info, X } from "lucide-react";

interface BrutalModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  variant?: "info" | "success" | "warning" | "error";
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
  showCancel?: boolean;
}

const variantConfig = {
  info: {
    icon: Info,
    iconClass: "text-primary",
    bgClass: "bg-primary/10",
  },
  success: {
    icon: Check,
    iconClass: "text-success",
    bgClass: "bg-success/10",
  },
  warning: {
    icon: AlertTriangle,
    iconClass: "text-warning",
    bgClass: "bg-warning/10",
  },
  error: {
    icon: X,
    iconClass: "text-destructive",
    bgClass: "bg-destructive/10",
  },
};

export function BrutalModal({
  open,
  onOpenChange,
  title,
  description,
  children,
  variant = "info",
  confirmText = "OK",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
  showCancel = false,
}: BrutalModalProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

  const handleConfirm = () => {
    onConfirm?.();
    onOpenChange(false);
  };

  const handleCancel = () => {
    onCancel?.();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="border-[3px] border-foreground shadow-brutal sm:max-w-md">
        <DialogHeader className="space-y-4">
          <div className="flex items-center gap-4">
            <div className={cn("w-12 h-12 border-[2px] border-foreground flex items-center justify-center", config.bgClass)}>
              <Icon className={cn("w-6 h-6", config.iconClass)} />
            </div>
            <DialogTitle className="text-xl font-bold">{title}</DialogTitle>
          </div>
          {description && (
            <DialogDescription className="text-base">{description}</DialogDescription>
          )}
        </DialogHeader>
        {children && <div className="py-4">{children}</div>}
        <DialogFooter className="gap-2 sm:gap-2">
          {showCancel && (
            <BrutalButton variant="outline" onClick={handleCancel}>
              {cancelText}
            </BrutalButton>
          )}
          <BrutalButton onClick={handleConfirm}>
            {confirmText}
          </BrutalButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
