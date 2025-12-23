"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Menu, LogOut, User, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { getMe, logout, type User as UserType } from "@/lib/api";

interface TopBarProps {
  onMenuClick: () => void;
}

export function TopBar({ onMenuClick }: TopBarProps) {
  const router = useRouter();
  const [user, setUser] = useState<UserType | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
      } catch {
        setUser(null);
      }
    };
    fetchUser();
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-border/50 bg-background/80 px-6 backdrop-blur-xl">
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden -ml-2 h-10 w-10 rounded-xl"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Spacer for desktop */}
      <div className="hidden lg:block" />

      {/* Right side */}
      <div className="flex items-center gap-3">
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                className="h-10 gap-2 rounded-xl px-3 hover:bg-foreground/[0.04]"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-foreground/10">
                  <User className="h-4 w-4" />
                </div>
                <span className="hidden text-[14px] font-medium sm:inline-block max-w-40 truncate">
                  {user.email}
                </span>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 rounded-xl p-2">
              <div className="px-3 py-2">
                <p className="text-[14px] font-medium">{user.email}</p>
                <p className="text-[12px] text-muted-foreground">Signed in</p>
              </div>
              <DropdownMenuSeparator className="my-2" />
              <DropdownMenuItem 
                onClick={handleLogout} 
                className="rounded-lg text-destructive focus:text-destructive cursor-pointer"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button 
            onClick={() => router.push("/login")}
            className="h-10 rounded-xl px-5 text-[14px] font-medium"
          >
            Sign in
          </Button>
        )}
      </div>
    </header>
  );
}
