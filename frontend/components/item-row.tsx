"use client";

import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { Star, ExternalLink, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScorePill } from "./score-pill";
import { cn } from "@/lib/utils";
import { type Item, addFavorite, removeFavorite } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface ItemRowProps {
  item: Item;
  isFavorite?: boolean;
  onFavoriteChange?: (itemId: number, isFavorite: boolean) => void;
  onClick?: () => void;
}

export function ItemRow({ 
  item, 
  isFavorite = false, 
  onFavoriteChange,
  onClick 
}: ItemRowProps) {
  const [favorite, setFavorite] = useState(isFavorite);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);

    try {
      if (favorite) {
        await removeFavorite(item.id);
        setFavorite(false);
        onFavoriteChange?.(item.id, false);
      } else {
        await addFavorite(item.id);
        setFavorite(true);
        onFavoriteChange?.(item.id, true);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update favorite. Please sign in.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const score = item.mena_analysis?.fit_score ?? null;
  const summary = item.mena_analysis?.mena_summary;
  const publishedDate = item.published_at 
    ? formatDistanceToNow(new Date(item.published_at), { addSuffix: true })
    : null;

  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative flex cursor-pointer gap-5 px-6 py-5",
        "border-b border-border/40 last:border-0",
        "transition-colors duration-150 hover:bg-foreground/[0.02]",
        "focus-visible:outline-none focus-visible:bg-foreground/[0.03]"
      )}
      tabIndex={0}
      role="button"
      onKeyDown={(e) => e.key === "Enter" && onClick?.()}
    >
      {/* Score */}
      <div className="flex-shrink-0 pt-0.5">
        {score !== null ? (
          <ScorePill score={score} size="md" />
        ) : (
          <div className="flex h-8 w-[60px] items-center justify-center rounded-xl bg-muted text-[13px] text-muted-foreground">
            --
          </div>
        )}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1 space-y-2">
        {/* Title row */}
        <div className="flex items-start justify-between gap-4">
          <h3 className="text-[15px] font-medium leading-snug text-foreground line-clamp-1 group-hover:text-foreground/90">
            {item.title}
          </h3>
          
          {/* External link - shows on hover */}
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex-shrink-0 p-1.5 rounded-lg text-muted-foreground/50 opacity-0 transition-all hover:text-foreground hover:bg-foreground/5 group-hover:opacity-100"
            aria-label="Open original article"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px] text-muted-foreground">
          {item.company_name && (
            <>
              <span className="font-medium text-foreground/70">{item.company_name}</span>
              <span className="text-border">·</span>
            </>
          )}
          {item.source && (
            <>
              <span>{item.source.name}</span>
              <span className="text-border">·</span>
            </>
          )}
          {publishedDate && (
            <span>{publishedDate}</span>
          )}
        </div>

        {/* MENA Summary */}
        {summary && (
          <p className="text-[13px] leading-relaxed text-muted-foreground line-clamp-2 pr-8">
            {summary}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-shrink-0 items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "h-9 w-9 rounded-xl transition-all",
            favorite 
              ? "text-amber-500 hover:text-amber-600 hover:bg-amber-500/10" 
              : "text-muted-foreground/50 hover:text-muted-foreground hover:bg-foreground/5"
          )}
          onClick={handleFavoriteClick}
          disabled={loading}
          aria-label={favorite ? "Remove from favorites" : "Add to favorites"}
        >
          <Star className={cn("h-[18px] w-[18px]", favorite && "fill-current")} />
        </Button>
        
        <ChevronRight className="h-5 w-5 text-muted-foreground/30 transition-all group-hover:text-muted-foreground/50 group-hover:translate-x-0.5" />
      </div>
    </div>
  );
}
