"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Star, 
  Database,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onNavigate?: () => void;
}

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/favorites", label: "Favorites", icon: Star },
  { href: "/settings/sources", label: "Sources", icon: Database },
];

export function Sidebar({ onNavigate }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-border/50 px-6">
        <Link 
          href="/" 
          className="flex items-center gap-3 transition-opacity hover:opacity-80"
          onClick={onNavigate}
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground shadow-soft">
            <Zap className="h-5 w-5 text-background" />
          </div>
          <div className="flex flex-col">
            <span className="text-[15px] font-semibold tracking-tight">MENA Signal</span>
            <span className="text-[11px] text-muted-foreground">AI Funding Intel</span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6">
        <div className="space-y-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-[14px] font-medium transition-all duration-150",
                  isActive 
                    ? "bg-foreground/[0.06] text-foreground" 
                    : "text-muted-foreground hover:bg-foreground/[0.04] hover:text-foreground"
                )}
              >
                <item.icon className={cn(
                  "h-[18px] w-[18px] transition-colors",
                  isActive ? "text-foreground" : "text-muted-foreground"
                )} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-border/50 px-6 py-5">
        <p className="text-[12px] text-muted-foreground/70">
          Track AI funding with MENA market analysis
        </p>
      </div>
    </div>
  );
}
