import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { 
  Headphones, 
  TrendingUp, 
  FileText, 
  Podcast, 
  Search, 
  User as UserIcon, 
  LogOut,
  Loader2
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  open: boolean;
}

export const Sidebar = ({ open }: SidebarProps) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    // Delay for visual feedback
    await new Promise(resolve => setTimeout(resolve, 1000));
    logout();
    navigate("/auth");
  };

  const menuItems = [
    { icon: TrendingUp, label: "Dashboard", path: "/dashboard" },
    { icon: FileText, label: "Articles", path: "/articles" },
    { icon: Podcast, label: "Podcasts", path: "/podcasts" },
    { icon: Search, label: "Search", path: "/search" },
    { icon: UserIcon, label: "Profile", path: "/profile" },
  ];

  return (
    <aside className={`fixed left-0 top-0 h-full w-64 bg-card border-r-[3px] border-foreground z-40 transform transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
      <div className="p-4">
        <Link to="/" className="flex items-center gap-2 mb-8">
          <div className="w-10 h-10 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center">
            <Headphones className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold">EchoBrief</span>
        </Link>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            
            return (
              <Link 
                key={item.path}
                to={item.path} 
                className={`flex items-center gap-3 px-4 py-3 border-[2px] transition-all font-medium ${
                  isActive 
                    ? "bg-primary border-foreground shadow-brutal font-bold" 
                    : "hover:bg-muted border-transparent hover:border-foreground"
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="p-4 bg-muted border-[2px] border-foreground mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-secondary border-[2px] border-foreground flex items-center justify-center font-bold overflow-hidden">
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
              ) : (
                user?.username?.substring(0, 2).toUpperCase() || "JD"
              )}
            </div>
            <div className="min-w-0">
              <p className="font-bold text-sm truncate">{user?.username || "Guest"}</p>
              <p className="text-xs text-muted-foreground capitalize">{user?.plan_type || "Free"} Plan</p>
            </div>
          </div>
        </div>
        <BrutalButton variant="outline" size="sm" className="w-full" onClick={handleLogout} disabled={isLoggingOut}>
          {isLoggingOut ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <LogOut className="w-4 h-4 mr-2" />
          )}
          {isLoggingOut ? "Logging out..." : "Logout"}
        </BrutalButton>
      </div>
    </aside>
  );
};
