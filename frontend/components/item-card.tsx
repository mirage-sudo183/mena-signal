"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  Star, 
  ExternalLink, 
  Tag as TagIcon, 
  EyeOff, 
  Building2,
  DollarSign,
  MapPin,
  TrendingUp
} from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from "@/components/ui/tooltip";
import { type Item, addFavorite, removeFavorite, hideItem } from "@/lib/api";
import { 
  formatRelativeDate, 
  formatCurrency, 
  getScoreClass, 
  truncate,
  cn 
} from "@/lib/utils";

interface ItemCardProps {
  item: Item;
  onUpdate?: () => void;
}

export function ItemCard({ item, onUpdate }: ItemCardProps) {
  const [isFavorited, setIsFavorited] = useState(item.is_favorited);
  const [isHidden, setIsHidden] = useState(item.hidden);
  const [loading, setLoading] = useState(false);

  const handleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setLoading(true);
    try {
      if (isFavorited) {
        await removeFavorite(item.id);
        setIsFavorited(false);
      } else {
        await addFavorite(item.id);
        setIsFavorited(true);
      }
      onUpdate?.();
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleHide = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await hideItem(item.id);
      setIsHidden(true);
      onUpdate?.();
    } catch (error) {
      console.error("Failed to hide item:", error);
    }
  };

  if (isHidden) {
    return null;
  }

  const score = item.mena_analysis?.fit_score ?? 0;
  const scoreVariant = score >= 70 ? "success" : score >= 40 ? "warning" : "danger";

  return (
    <TooltipProvider>
      <Link href={`/item/${item.id}`}>
        <Card className="group hover:border-primary/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5 animate-fade-in">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="text-xs">
                    {item.type === "funding" ? (
                      <><DollarSign className="h-3 w-3 mr-1" /> Funding</>
                    ) : (
                      <><Building2 className="h-3 w-3 mr-1" /> Company</>
                    )}
                  </Badge>
                  {item.source && (
                    <span className="text-xs text-muted-foreground">
                      {item.source.name}
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {formatRelativeDate(item.published_at)}
                  </span>
                </div>
                <h3 className="font-semibold text-lg leading-tight line-clamp-2 group-hover:text-primary transition-colors">
                  {item.title}
                </h3>
                {item.company_name && (
                  <p className="text-sm text-muted-foreground mt-1 flex items-center gap-1">
                    <Building2 className="h-3 w-3" />
                    {item.company_name}
                  </p>
                )}
              </div>
              
              {/* Score Badge */}
              <div className="flex flex-col items-end gap-2">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Badge 
                      variant={scoreVariant}
                      className="text-lg font-bold px-3 py-1 cursor-help"
                    >
                      {score}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent side="left" className="max-w-xs">
                    <p className="font-semibold mb-1">MENA Fit Score</p>
                    <p className="text-xs text-muted-foreground">
                      {score >= 70 ? "High potential for MENA market" :
                       score >= 40 ? "Moderate MENA market fit" :
                       "Lower MENA market applicability"}
                    </p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pb-3">
            {/* Funding Details */}
            {item.funding_details && (
              <div className="flex flex-wrap gap-2 mb-3">
                {item.funding_details.amount_usd && (
                  <Badge variant="secondary" className="gap-1">
                    <DollarSign className="h-3 w-3" />
                    {formatCurrency(item.funding_details.amount_usd)}
                  </Badge>
                )}
                {item.funding_details.round_type && (
                  <Badge variant="secondary" className="gap-1">
                    <TrendingUp className="h-3 w-3" />
                    {item.funding_details.round_type.replace("_", " ").toUpperCase()}
                  </Badge>
                )}
                {item.funding_details.geography && (
                  <Badge variant="secondary" className="gap-1">
                    <MapPin className="h-3 w-3" />
                    {item.funding_details.geography}
                  </Badge>
                )}
              </div>
            )}

            {/* Summary */}
            {item.summary && (
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                {item.summary}
              </p>
            )}

            {/* MENA Analysis Summary */}
            {item.mena_analysis?.mena_summary && (
              <div className="rounded-lg bg-secondary/30 p-3 border border-primary/10">
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">MENA Insight:</span>{" "}
                  {truncate(item.mena_analysis.mena_summary, 150)}
                </p>
              </div>
            )}

            {/* Tags */}
            {item.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {item.tags.map((tag) => (
                  <Badge 
                    key={tag.id} 
                    variant="outline" 
                    className="text-xs"
                    style={{ 
                      borderColor: tag.color || undefined,
                      color: tag.color || undefined 
                    }}
                  >
                    {tag.name}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>

          <CardFooter className="pt-3 border-t gap-2">
            <Button
              variant={isFavorited ? "default" : "outline"}
              size="sm"
              onClick={handleFavorite}
              disabled={loading}
              className={cn(
                "gap-1",
                isFavorited && "bg-primary hover:bg-primary/90"
              )}
            >
              <Star className={cn("h-4 w-4", isFavorited && "fill-current")} />
              {isFavorited ? "Saved" : "Save"}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleHide}
              className="gap-1"
            >
              <EyeOff className="h-4 w-4" />
              Hide
            </Button>

            <div className="flex-1" />

            <Button
              variant="ghost"
              size="sm"
              className="gap-1"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.open(item.url, "_blank");
              }}
            >
              <ExternalLink className="h-4 w-4" />
              Source
            </Button>
          </CardFooter>
        </Card>
      </Link>
    </TooltipProvider>
  );
}

