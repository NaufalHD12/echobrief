import { useTheme } from "next-themes";
import { Toaster as Sonner, toast } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme();

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      position="top-right"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-[3px] group-[.toaster]:border-foreground group-[.toaster]:shadow-brutal",
          description: "group-[.toast]:text-muted-foreground",
          actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground group-[.toast]:border-[2px] group-[.toast]:border-foreground",
          cancelButton: "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground group-[.toast]:border-[2px] group-[.toast]:border-foreground",
          success: "group-[.toaster]:bg-success group-[.toaster]:text-success-foreground",
          error: "group-[.toaster]:bg-destructive group-[.toaster]:text-destructive-foreground",
        },
      }}
      {...props}
    />
  );
};

export { Toaster, toast };
