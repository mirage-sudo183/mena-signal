"use client";

import { useState, useEffect } from "react";
import { formatDistanceToNow, format } from "date-fns";
import { 
  ExternalLink, 
  Star, 
  Calendar,
  Globe,
  Building,
  TrendingUp,
  MessageSquare,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { 
  Sheet, 
  SheetContent, 
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { ScorePill } from "./score-pill";
import { cn } from "@/lib/utils";
import { 
  type Item, 
  getItem, 
  addFavorite, 
  removeFavorite,
  addNote 
} from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface ItemDrawerProps {
  itemId: number | null;
  open: boolean;
  onClose: () => void;
  initialFavorite?: boolean;
  onFavoriteChange?: (itemId: number, isFavorite: boolean) => void;
}

export function ItemDrawer({ 
  itemId, 
  open, 
  onClose,
  initialFavorite = false,
  onFavoriteChange 
}: ItemDrawerProps) {
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(false);
  const [favorite, setFavorite] = useState(initialFavorite);
  const [noteText, setNoteText] = useState("");
  const [savingNote, setSavingNote] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (itemId && open) {
      setLoading(true);
      getItem(itemId)
        .then((data) => {
          setItem(data);
          setFavorite(initialFavorite);
        })
        .catch((err) => {
          console.error("Failed to load item:", err);
          toast({
            title: "Error",
            description: "Failed to load item details",
            variant: "destructive",
          });
        })
        .finally(() => setLoading(false));
    }
  }, [itemId, open, initialFavorite, toast]);

  const handleFavoriteClick = async () => {
    if (!item) return;
    
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
    }
  };

  const handleSaveNote = async () => {
    if (!item || !noteText.trim()) return;
    
    setSavingNote(true);
    try {
      await addNote(item.id, noteText);
      setNoteText("");
      toast({
        title: "Note saved",
        description: "Your note has been added",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save note. Please sign in.",
        variant: "destructive",
      });
    } finally {
      setSavingNote(false);
    }
  };

  const score = item?.mena_analysis?.fit_score ?? null;
  const rubric = item?.mena_analysis?.rubric_json;

  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-xl border-l-0 p-0">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-xl border-b border-border/50">
          <SheetHeader className="p-6">
            <div className="flex items-start justify-between gap-4">
              <SheetTitle className="text-left text-[18px] font-semibold leading-snug pr-8">
                {loading ? "Loading..." : item?.title}
              </SheetTitle>
            </div>
          </SheetHeader>
        </div>

        {item && !loading && (
          <div className="p-6 space-y-8">
            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-4 text-[13px] text-muted-foreground">
              {item.company_name && (
                <div className="flex items-center gap-2">
                  <Building className="h-4 w-4" />
                  <span className="font-medium text-foreground">{item.company_name}</span>
                </div>
              )}
              {item.published_at && (
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>{format(new Date(item.published_at), "MMM d, yyyy")}</span>
                </div>
              )}
              {item.source && (
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  <span>{item.source.name}</span>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <Button
                variant={favorite ? "default" : "outline"}
                onClick={handleFavoriteClick}
                className="h-10 gap-2 rounded-xl text-[14px]"
              >
                <Star className={cn("h-4 w-4", favorite && "fill-current")} />
                {favorite ? "Saved" : "Save"}
              </Button>
              <Button
                variant="outline"
                asChild
                className="h-10 gap-2 rounded-xl text-[14px]"
              >
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  View Source
                </a>
              </Button>
            </div>

            <Separator className="bg-border/50" />

            {/* MENA Analysis */}
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="flex items-center gap-2 text-[14px] font-semibold uppercase tracking-wide text-muted-foreground">
                  <TrendingUp className="h-4 w-4" />
                  MENA Fit Analysis
                </h3>
                {score !== null && <ScorePill score={score} size="lg" />}
              </div>
              
              {item.mena_analysis?.mena_summary && (
                <div className="rounded-xl bg-muted/50 p-4 border border-border/50">
                  <p className="text-[14px] leading-relaxed text-foreground/90">
                    {item.mena_analysis.mena_summary}
                  </p>
                </div>
              )}

              {/* Rubric breakdown */}
              {rubric && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-[12px] font-medium uppercase tracking-wide text-muted-foreground">
                    Score Breakdown
                  </h4>
                  <div className="space-y-2.5">
                    {Object.entries(rubric).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between gap-4">
                        <span className="text-[13px] text-muted-foreground capitalize">
                          {key.replace(/_/g, " ")}
                        </span>
                        <div className="flex items-center gap-3">
                          <div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted">
                            <div 
                              className="h-full rounded-full bg-foreground/60 transition-all duration-500"
                              style={{ width: `${(value as number) * 5}%` }}
                            />
                          </div>
                          <span className="w-5 text-right text-[13px] tabular-nums font-medium">
                            {value as number}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>

            <Separator className="bg-border/50" />

            {/* Summary */}
            {item.summary && (
              <>
                <section className="space-y-3">
                  <h3 className="text-[14px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Summary
                  </h3>
                  <p className="text-[14px] leading-relaxed text-foreground/80">
                    {item.summary}
                  </p>
                </section>
                <Separator className="bg-border/50" />
              </>
            )}

            {/* Funding Details */}
            {item.funding_details && (
              <>
                <section className="space-y-4">
                  <h3 className="text-[14px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Funding Details
                  </h3>
                  <dl className="grid grid-cols-2 gap-4 text-[14px]">
                    {item.funding_details.round_type && (
                      <div className="space-y-1">
                        <dt className="text-muted-foreground">Round</dt>
                        <dd className="font-medium capitalize">{item.funding_details.round_type}</dd>
                      </div>
                    )}
                    {item.funding_details.amount_usd && (
                      <div className="space-y-1">
                        <dt className="text-muted-foreground">Amount</dt>
                        <dd className="font-medium">
                          ${(item.funding_details.amount_usd / 1000000).toFixed(1)}M
                        </dd>
                      </div>
                    )}
                    {item.funding_details.geography && (
                      <div className="space-y-1">
                        <dt className="text-muted-foreground">Geography</dt>
                        <dd className="font-medium">{item.funding_details.geography}</dd>
                      </div>
                    )}
                  </dl>
                </section>
                <Separator className="bg-border/50" />
              </>
            )}

            {/* Add Note */}
            <section className="space-y-4">
              <h3 className="flex items-center gap-2 text-[14px] font-semibold uppercase tracking-wide text-muted-foreground">
                <MessageSquare className="h-4 w-4" />
                Add Note
              </h3>
              <Textarea
                placeholder="Write your thoughts about this opportunity..."
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                className="min-h-24 resize-none rounded-xl border-border/60 text-[14px] placeholder:text-muted-foreground/50"
              />
              <Button 
                onClick={handleSaveNote}
                disabled={!noteText.trim() || savingNote}
                className="h-10 rounded-xl text-[14px]"
              >
                {savingNote ? "Saving..." : "Save Note"}
              </Button>
            </section>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="p-6 space-y-6">
            <div className="h-4 w-3/4 animate-pulse rounded-lg bg-muted" />
            <div className="h-4 w-1/2 animate-pulse rounded-lg bg-muted" />
            <div className="h-24 w-full animate-pulse rounded-xl bg-muted" />
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
