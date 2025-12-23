"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";
import {
  ArrowLeft,
  ExternalLink,
  Star,
  Tag as TagIcon,
  MessageSquare,
  Building,
  Calendar,
  Globe,
  TrendingUp,
  Loader2,
  Plus,
  X,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ScorePill } from "@/components/score-pill";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  getItem,
  getTags,
  createTag,
  assignTags,
  addNote,
  deleteNote,
  addFavorite,
  removeFavorite,
  type Item,
  type Tag,
} from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";

export default function ItemDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [userTags, setUserTags] = useState<Tag[]>([]);
  
  // Note state
  const [newNote, setNewNote] = useState("");
  const [addingNote, setAddingNote] = useState(false);
  
  // Tag state
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [newTagName, setNewTagName] = useState("");
  const [creatingTag, setCreatingTag] = useState(false);

  const fetchItem = useCallback(async () => {
    try {
      const data = await getItem(Number(params.id));
      setItem(data);
      setSelectedTagIds(data.tags.map((t) => t.id));
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load item.",
        variant: "destructive",
      });
      router.push("/");
    } finally {
      setLoading(false);
    }
  }, [params.id, router, toast]);

  const fetchTags = useCallback(async () => {
    try {
      const data = await getTags();
      setUserTags(data);
    } catch {
      // User might not be logged in
    }
  }, []);

  useEffect(() => {
    fetchItem();
    fetchTags();
  }, [fetchItem, fetchTags]);

  const handleFavorite = async () => {
    if (!item) return;
    try {
      if (item.is_favorited) {
        await removeFavorite(item.id);
      } else {
        await addFavorite(item.id);
      }
      setItem({ ...item, is_favorited: !item.is_favorited });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update favorite. Are you logged in?",
        variant: "destructive",
      });
    }
  };

  const handleAddNote = async () => {
    if (!item || !newNote.trim()) return;
    setAddingNote(true);
    try {
      const note = await addNote(item.id, newNote.trim());
      setItem({
        ...item,
        notes: [note, ...item.notes],
      });
      setNewNote("");
      toast({ title: "Note added" });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add note. Are you logged in?",
        variant: "destructive",
      });
    } finally {
      setAddingNote(false);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!item) return;
    try {
      await deleteNote(noteId);
      setItem({
        ...item,
        notes: item.notes.filter((n) => n.id !== noteId),
      });
      toast({ title: "Note deleted" });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete note.",
        variant: "destructive",
      });
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    setCreatingTag(true);
    try {
      const tag = await createTag(newTagName.trim());
      setUserTags([...userTags, tag]);
      setSelectedTagIds([...selectedTagIds, tag.id]);
      setNewTagName("");
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Failed to create tag.";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setCreatingTag(false);
    }
  };

  const handleSaveTags = async () => {
    if (!item) return;
    try {
      await assignTags(item.id, selectedTagIds);
      const updatedTags = userTags.filter((t) => selectedTagIds.includes(t.id));
      setItem({ ...item, tags: updatedTags });
      setTagDialogOpen(false);
      toast({ title: "Tags updated" });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update tags.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-32">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </AppShell>
    );
  }

  if (!item) {
    return null;
  }

  const score = item.mena_analysis?.fit_score ?? null;
  const rubric = item.mena_analysis?.rubric_json;

  return (
    <AppShell>
      <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Back link */}
        <Link 
          href="/" 
          className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Header */}
            <div>
              <h1 className="text-2xl font-semibold leading-tight mb-4">{item.title}</h1>

              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                {item.company_name && (
                  <div className="flex items-center gap-1.5">
                    <Building className="h-3.5 w-3.5" />
                    <span className="font-medium text-foreground">{item.company_name}</span>
                  </div>
                )}
                {item.published_at && (
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{format(new Date(item.published_at), "MMM d, yyyy")}</span>
                  </div>
                )}
                {item.source && (
                  <div className="flex items-center gap-1.5">
                    <Globe className="h-3.5 w-3.5" />
                    <span>{item.source.name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={item.is_favorited ? "default" : "outline"}
                size="sm"
                onClick={handleFavorite}
                className="gap-2"
              >
                <Star className={cn("h-4 w-4", item.is_favorited && "fill-current")} />
                {item.is_favorited ? "Saved" : "Save"}
              </Button>

              <Dialog open={tagDialogOpen} onOpenChange={setTagDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    <TagIcon className="h-4 w-4" />
                    Tags ({item.tags.length})
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Manage Tags</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      {userTags.map((tag) => (
                        <Badge
                          key={tag.id}
                          variant={selectedTagIds.includes(tag.id) ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => {
                            if (selectedTagIds.includes(tag.id)) {
                              setSelectedTagIds(selectedTagIds.filter((id) => id !== tag.id));
                            } else {
                              setSelectedTagIds([...selectedTagIds, tag.id]);
                            }
                          }}
                        >
                          {tag.name}
                        </Badge>
                      ))}
                    </div>

                    <Separator />

                    <div className="flex gap-2">
                      <Input
                        placeholder="New tag name"
                        value={newTagName}
                        onChange={(e) => setNewTagName(e.target.value)}
                      />
                      <Button onClick={handleCreateTag} disabled={creatingTag} size="icon">
                        {creatingTag ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Plus className="h-4 w-4" />
                        )}
                      </Button>
                    </div>

                    <Button onClick={handleSaveTags} className="w-full">
                      Save Tags
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>

              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                asChild
              >
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  View Source
                </a>
              </Button>
            </div>

            {/* Tags Display */}
            {item.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {item.tags.map((tag) => (
                  <Badge key={tag.id} variant="secondary">
                    {tag.name}
                  </Badge>
                ))}
              </div>
            )}

            {/* Funding Details */}
            {item.funding_details && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="text-sm font-medium mb-3">Funding Details</h3>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  {item.funding_details.round_type && (
                    <>
                      <dt className="text-muted-foreground">Round</dt>
                      <dd className="font-medium capitalize">{item.funding_details.round_type}</dd>
                    </>
                  )}
                  {item.funding_details.amount_usd && (
                    <>
                      <dt className="text-muted-foreground">Amount</dt>
                      <dd className="font-medium">
                        ${(item.funding_details.amount_usd / 1000000).toFixed(1)}M
                      </dd>
                    </>
                  )}
                  {item.funding_details.geography && (
                    <>
                      <dt className="text-muted-foreground">Geography</dt>
                      <dd className="font-medium">{item.funding_details.geography}</dd>
                    </>
                  )}
                </dl>
              </div>
            )}

            {/* Summary */}
            {item.summary && (
              <div className="rounded-lg border bg-card p-4">
                <h3 className="text-sm font-medium mb-2">Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.summary}</p>
              </div>
            )}

            {/* Notes */}
            <div className="rounded-lg border bg-card p-4">
              <h3 className="flex items-center gap-2 text-sm font-medium mb-4">
                <MessageSquare className="h-4 w-4" />
                Notes ({item.notes.length})
              </h3>

              <div className="space-y-3 mb-4">
                <Textarea
                  placeholder="Add a note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="min-h-20 resize-none"
                />
                <Button
                  onClick={handleAddNote}
                  disabled={addingNote || !newNote.trim()}
                  size="sm"
                >
                  {addingNote ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4 mr-2" />
                  )}
                  Add Note
                </Button>
              </div>

              {item.notes.length > 0 && (
                <>
                  <Separator className="my-4" />
                  <div className="space-y-3">
                    {item.notes.map((note) => (
                      <div
                        key={note.id}
                        className="group flex items-start gap-3 rounded-md bg-muted/50 p-3"
                      >
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{note.body}</p>
                          <p className="mt-2 text-xs text-muted-foreground">
                            {format(new Date(note.created_at), "MMM d, yyyy")}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => handleDeleteNote(note.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Sidebar - MENA Analysis */}
          <div className="space-y-6">
            <div className="sticky top-20 rounded-lg border bg-card p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="flex items-center gap-2 text-sm font-medium">
                  <TrendingUp className="h-4 w-4" />
                  MENA Fit Analysis
                </h3>
                {score !== null && <ScorePill score={score} />}
              </div>

              {item.mena_analysis?.mena_summary && (
                <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                  {item.mena_analysis.mena_summary}
                </p>
              )}

              {rubric && (
                <>
                  <Separator className="my-4" />
                  <h4 className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-3">
                    Score Breakdown
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(rubric).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground capitalize">
                          {key.replace(/_/g, " ")}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                            <div 
                              className="h-full rounded-full bg-primary transition-all"
                              style={{ width: `${(value as number) * 5}%` }}
                            />
                          </div>
                          <span className="w-4 text-right text-xs tabular-nums">
                            {value as number}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {item.mena_analysis?.model_name && (
                <p className="mt-4 text-center text-xs text-muted-foreground">
                  Analyzed by {item.mena_analysis.model_name}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
