"use client";

import { useState, useEffect, useCallback } from "react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { ItemRow } from "@/components/item-row";
import { ItemDrawer } from "@/components/item-drawer";
import { EmptyState } from "@/components/empty-state";
import { SkeletonList } from "@/components/skeleton-row";
import { Button } from "@/components/ui/button";
import { getFavorites, type Item } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function FavoritesPage() {
  const router = useRouter();
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set());

  // Drawer
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchFavorites = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getFavorites();
      setItems(data);
      setFavoriteIds(new Set(data.map((item: Item) => item.id)));
    } catch (error) {
      console.error("Failed to fetch favorites:", error);
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  const handleItemClick = (itemId: number) => {
    setSelectedItemId(itemId);
    setDrawerOpen(true);
  };

  const handleFavoriteChange = (itemId: number, isFavorite: boolean) => {
    if (!isFavorite) {
      setItems((prev) => prev.filter((item) => item.id !== itemId));
      setFavoriteIds((prev) => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });
    }
  };

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl px-6 py-8 lg:px-8">
        <PageHeader 
          title="Favorites" 
          description="Your saved funding opportunities"
        />

        {/* Item list */}
        <div className="mt-8 rounded-2xl border border-border/60 bg-card shadow-soft overflow-hidden">
          {loading ? (
            <SkeletonList count={8} />
          ) : items.length === 0 ? (
            <EmptyState type="no-favorites">
              <Button 
                onClick={() => router.push("/")} 
                variant="outline" 
                className="h-10 rounded-xl text-[14px]"
              >
                Browse funding news
              </Button>
            </EmptyState>
          ) : (
            <div className="stagger-children">
              {items.map((item) => (
                <ItemRow
                  key={item.id}
                  item={item}
                  isFavorite={favoriteIds.has(item.id)}
                  onFavoriteChange={handleFavoriteChange}
                  onClick={() => handleItemClick(item.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Item drawer */}
      <ItemDrawer
        itemId={selectedItemId}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        initialFavorite={selectedItemId ? favoriteIds.has(selectedItemId) : false}
        onFavoriteChange={handleFavoriteChange}
      />
    </AppShell>
  );
}
