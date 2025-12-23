import { cn } from "@/lib/utils";
import { Search, Star, Database, FileQuestion } from "lucide-react";

interface EmptyStateProps {
  type?: "no-results" | "no-favorites" | "no-sources" | "default";
  title?: string;
  description?: string;
  className?: string;
  children?: React.ReactNode;
}

const defaultContent = {
  "no-results": {
    icon: Search,
    title: "No results found",
    description: "Try adjusting your filters or search terms to find what you're looking for",
  },
  "no-favorites": {
    icon: Star,
    title: "No favorites yet",
    description: "Star items you find interesting to save them here for quick access",
  },
  "no-sources": {
    icon: Database,
    title: "No sources configured",
    description: "Add RSS feeds to start tracking AI funding news automatically",
  },
  default: {
    icon: FileQuestion,
    title: "Nothing here yet",
    description: "Check back later or try a different view",
  },
};

export function EmptyState({
  type = "default",
  title,
  description,
  className,
  children,
}: EmptyStateProps) {
  const content = defaultContent[type];
  const Icon = content.icon;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-20 text-center animate-fade-in",
        className
      )}
    >
      {/* Icon container */}
      <div className="relative mb-6">
        {/* Background decoration */}
        <div className="absolute inset-0 -m-3 rounded-full bg-muted/50 blur-xl" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl border border-border/50 bg-card shadow-soft">
          <Icon className="h-7 w-7 text-muted-foreground/70" />
        </div>
      </div>

      <h3 className="mb-2 text-[17px] font-semibold text-foreground">
        {title || content.title}
      </h3>
      <p className="mb-8 max-w-sm text-[14px] leading-relaxed text-muted-foreground">
        {description || content.description}
      </p>

      {children}
    </div>
  );
}
