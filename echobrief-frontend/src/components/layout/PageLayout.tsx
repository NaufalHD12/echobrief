import { useState } from "react";
import { Link } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";
import { Headphones, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface PageLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  /** Center content with max-width (for SearchPage) */
  centered?: boolean;
  /** Extra bottom padding (for Podcasts player) */
  extraBottomPadding?: boolean;
  /** Custom header action buttons */
  headerActions?: React.ReactNode;
  /** Hide page title */
  hideTitle?: boolean;
}

export const PageLayout = ({
  children,
  title,
  subtitle,
  centered = false,
  extraBottomPadding = false,
  headerActions,
  hideTitle = false,
}: PageLayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-background border-b-[3px] border-foreground">
        <div className="flex items-center justify-between px-4 h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary border-[2px] border-foreground shadow-brutal flex items-center justify-center">
              <Headphones className="w-4 h-4" />
            </div>
            <span className="font-bold">EchoBrief</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-10 h-10 border-[2px] border-foreground flex items-center justify-center"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <Sidebar open={sidebarOpen} />

      {/* Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-foreground/20 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className={cn(
        "lg:ml-64 pt-20 lg:pt-8 px-4 lg:px-8",
        extraBottomPadding ? "pb-32" : "pb-8"
      )}>
        <div className={centered ? "max-w-3xl mx-auto" : ""}>
          {/* Page Header */}
          {!hideTitle && title && (
            <div className={cn("mb-8", centered && "text-center")}>
              <div className={cn(
                "flex items-center justify-between",
                centered && "flex-col gap-4"
              )}>
                <div>
                  <h1 className="text-3xl lg:text-4xl font-bold mb-2">{title}</h1>
                  {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
                </div>
                {headerActions && (
                  <div className="flex gap-2">{headerActions}</div>
                )}
              </div>
            </div>
          )}

          {/* Page Content */}
          {children}
        </div>
      </main>
    </div>
  );
};
