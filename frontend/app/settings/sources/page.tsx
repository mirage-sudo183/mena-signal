"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/use-toast";
import { getSources, createSource, toggleSource, type Source } from "@/lib/api";
import { Plus, Rss, Globe } from "lucide-react";

export default function SourcesSettingsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const { toast } = useToast();

  // New source form
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [newCategory, setNewCategory] = useState("funding");

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const data = await getSources();
      setSources(data);
    } catch (error) {
      console.error("Failed to fetch sources:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (sourceId: number, enabled: boolean) => {
    try {
      await toggleSource(sourceId, enabled);
      setSources((prev) =>
        prev.map((s) => (s.id === sourceId ? { ...s, enabled } : s))
      );
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update source",
        variant: "destructive",
      });
    }
  };

  const handleCreate = async () => {
    if (!newName.trim() || !newUrl.trim()) return;

    setCreating(true);
    try {
      const newSource = await createSource({
        name: newName,
        url: newUrl,
        type: "rss",
        category: newCategory,
        enabled: true,
      });
      setSources((prev) => [...prev, newSource]);
      setDialogOpen(false);
      setNewName("");
      setNewUrl("");
      toast({
        title: "Source added",
        description: `${newName} has been added to your sources`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create source",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl px-6 py-8 lg:px-8">
        <PageHeader 
          title="Sources" 
          description="Manage RSS feeds for funding news ingestion"
        >
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="h-10 gap-2 rounded-xl text-[14px]">
                <Plus className="h-4 w-4" />
                Add Source
              </Button>
            </DialogTrigger>
            <DialogContent className="rounded-2xl sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="text-[18px]">Add RSS Source</DialogTitle>
                <DialogDescription className="text-[14px]">
                  Add a new RSS feed to track funding news.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-5 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-[13px]">Name</Label>
                  <Input
                    id="name"
                    placeholder="TechCrunch AI"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="h-11 rounded-xl text-[14px]"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="url" className="text-[13px]">RSS URL</Label>
                  <Input
                    id="url"
                    placeholder="https://techcrunch.com/feed/"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    className="h-11 rounded-xl text-[14px]"
                  />
                </div>
              </div>
              <DialogFooter className="gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setDialogOpen(false)}
                  className="h-10 rounded-xl text-[14px]"
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleCreate} 
                  disabled={creating || !newName || !newUrl}
                  className="h-10 rounded-xl text-[14px]"
                >
                  {creating ? "Adding..." : "Add Source"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </PageHeader>

        {/* Sources list */}
        <div className="mt-8 rounded-2xl border border-border/60 bg-card shadow-soft overflow-hidden">
          {loading ? (
            <div className="divide-y divide-border/40">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center gap-5 px-6 py-5">
                  <Skeleton className="h-10 w-10 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-48 rounded-lg" />
                    <Skeleton className="h-3 w-72 rounded-lg" />
                  </div>
                  <Skeleton className="h-6 w-11 rounded-full" />
                </div>
              ))}
            </div>
          ) : sources.length === 0 ? (
            <EmptyState type="no-sources">
              <Button 
                onClick={() => setDialogOpen(true)} 
                className="h-10 gap-2 rounded-xl text-[14px]"
              >
                <Plus className="h-4 w-4" />
                Add your first source
              </Button>
            </EmptyState>
          ) : (
            <div className="divide-y divide-border/40 stagger-children">
              {sources.map((source) => (
                <div 
                  key={source.id} 
                  className="flex items-center gap-5 px-6 py-5 transition-colors hover:bg-foreground/[0.02]"
                >
                  {/* Icon */}
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-muted/60">
                    <Rss className="h-5 w-5 text-muted-foreground" />
                  </div>
                  
                  {/* Content */}
                  <div className="min-w-0 flex-1">
                    <h3 className="text-[15px] font-medium">{source.name}</h3>
                    <p className="mt-0.5 text-[13px] text-muted-foreground truncate">
                      {source.url}
                    </p>
                  </div>
                  
                  {/* Category badge */}
                  <div className="hidden sm:block">
                    <span className="inline-flex items-center rounded-lg bg-muted/60 px-2.5 py-1 text-[12px] font-medium text-muted-foreground capitalize">
                      {source.category || "general"}
                    </span>
                  </div>
                  
                  {/* Toggle */}
                  <Switch
                    checked={source.enabled}
                    onCheckedChange={(enabled) => handleToggle(source.id, enabled)}
                    aria-label={`Toggle ${source.name}`}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
