import { Link } from "react-router-dom";
import { Headphones, Twitter, Github, Linkedin } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-foreground text-background border-t-[3px] border-foreground">
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
          {/* Brand */}
          <div className="space-y-4 max-w-sm">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary border-[3px] border-background shadow-[4px_4px_0px_0px_hsl(var(--background))] flex items-center justify-center">
                <Headphones className="w-5 h-5 text-foreground" />
              </div>
              <span className="text-xl font-bold">EchoBrief</span>
            </Link>
            <p className="text-sm opacity-80">
              Transform breaking news into personalized audio podcasts with AI.
            </p>
          </div>

          {/* Product Links */}
          <div className="flex items-center gap-6 text-sm">
            <a href="#features" className="opacity-80 hover:opacity-100 transition-opacity">Features</a>
            <a href="#pricing" className="opacity-80 hover:opacity-100 transition-opacity">Pricing</a>
            <a href="#how-it-works" className="opacity-80 hover:opacity-100 transition-opacity">How It Works</a>
          </div>
        </div>

        <div className="border-t-[2px] border-background/30 mt-8 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm opacity-80">
            © 2026 EchoBrief. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="w-10 h-10 border-[2px] border-background flex items-center justify-center hover:bg-primary hover:border-foreground hover:text-foreground transition-all">
              <Twitter className="w-4 h-4" />
            </a>
            <a href="#" className="w-10 h-10 border-[2px] border-background flex items-center justify-center hover:bg-primary hover:border-foreground hover:text-foreground transition-all">
              <Github className="w-4 h-4" />
            </a>
            <a href="#" className="w-10 h-10 border-[2px] border-background flex items-center justify-center hover:bg-primary hover:border-foreground hover:text-foreground transition-all">
              <Linkedin className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
