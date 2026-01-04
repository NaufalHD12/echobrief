import { Link } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { Headphones, Menu, X, LayoutDashboard } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background border-b-[3px] border-foreground">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center group-hover:shadow-brutal-hover group-hover:-translate-x-0.5 group-hover:-translate-y-0.5 transition-all">
              <Headphones className="w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight">EchoBrief</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="font-medium hover:text-secondary transition-colors">
              Features
            </a>
            <a href="#pricing" className="font-medium hover:text-secondary transition-colors">
              Pricing
            </a>
            <a href="#how-it-works" className="font-medium hover:text-secondary transition-colors">
              How It Works
            </a>
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <Link to="/dashboard">
                <BrutalButton size="sm">
                  <LayoutDashboard className="w-4 h-4 mr-2" />
                  Dashboard
                </BrutalButton>
              </Link>
            ) : (
              <>
                <Link to="/auth">
                  <BrutalButton variant="outline" size="sm">
                    Login
                  </BrutalButton>
                </Link>
                <Link to="/auth?mode=register">
                  <BrutalButton size="sm">
                    Get Started
                  </BrutalButton>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden w-10 h-10 border-[3px] border-foreground bg-background flex items-center justify-center shadow-brutal"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t-[3px] border-foreground animate-slide-in">
            <div className="flex flex-col gap-3">
              <a 
                href="#features" 
                className="font-medium py-2 hover:text-secondary"
                onClick={() => setIsOpen(false)}
              >
                Features
              </a>
              <a 
                href="#pricing" 
                className="font-medium py-2 hover:text-secondary"
                onClick={() => setIsOpen(false)}
              >
                Pricing
              </a>
              <a 
                href="#how-it-works" 
                className="font-medium py-2 hover:text-secondary"
                onClick={() => setIsOpen(false)}
              >
                How It Works
              </a>
              <div className="flex gap-3 pt-3">
                {user ? (
                  <Link to="/dashboard" className="flex-1">
                    <BrutalButton size="sm" className="w-full">
                      <LayoutDashboard className="w-4 h-4 mr-2" />
                      Dashboard
                    </BrutalButton>
                  </Link>
                ) : (
                  <>
                    <Link to="/auth" className="flex-1">
                      <BrutalButton variant="outline" size="sm" className="w-full">
                        Login
                      </BrutalButton>
                    </Link>
                    <Link to="/auth?mode=register" className="flex-1">
                      <BrutalButton size="sm" className="w-full">
                        Get Started
                      </BrutalButton>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};
