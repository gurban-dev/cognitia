import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Sun, Moon, LogOut } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { SidebarTrigger } from "./ui/sidebar";
import { useAuth } from "@/contexts/AuthContext";

export default function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();

  useEffect(() => {
    const isDark = localStorage.getItem("theme") === "dark";

    setDarkMode(isDark);

    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  const toggleTheme = () => {
    const isDark = !darkMode;

    setDarkMode(isDark);

    document.documentElement.classList.toggle("dark", isDark);

    localStorage.setItem("theme", isDark ? "dark" : "light");
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const displayName = user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email : '';

  return (
    <header className="
      sticky top-0 z-50 w-full border-b
      bg-background/95 backdrop-blur
      supports-[backdrop-filter]:bg-background/60
      shadow-md
    ">
      <div className="
        flex items-center
        justify-between px-4
        py-3 md:px-6
      ">
        {/* Left: Sidebar + Brand */}
        <div className="flex items-center gap-4">
          <SidebarTrigger />

          <span className="text-xl font-bold tracking-tight">
            <span className="text-primary">Prompt</span>ify
          </span>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="hover:bg-muted transition"
          >
            {darkMode ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* Auth Controls */}
          {isAuthenticated && (
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="hover:shadow-sm"
              >
                <LogOut className="h-4 w-4 mr-1" />
                <span className="hidden sm:inline">Sign Out</span>
              </Button>

              {/* Avatar */}
              <Avatar className="
                h-8 w-8 ring-1 ring-muted-foreground/10
                hover:ring-2 transition cursor-pointer
              ">
                <AvatarImage 
                  src={`https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=random`} 
                  alt={displayName} 
                />
                <AvatarFallback>{getInitials(displayName)}</AvatarFallback>
              </Avatar>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
