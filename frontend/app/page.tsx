"use client";

import { useState, useEffect, useCallback } from "react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { FilterBar } from "@/components/filter-bar";
import { ItemRow } from "@/components/item-row";
import { ItemDrawer } from "@/components/item-drawer";
import { EmptyState } from "@/components/empty-state";
import { SkeletonList } from "@/components/skeleton-row";
import { Button } from "@/components/ui/button";
import { getItems, getFavorites, type Item } from "@/lib/api";
import { RefreshCw } from "lucide-react";

export default function DashboardPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set());

  // Filters
  const [search, setSearch] = useState("");
  const [dateRange, setDateRange] = useState("all");
  const [minScore, setMinScore] = useState(0);

  // Drawer
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchItems = useCallback(async (pageNum: number, reset = false) => {
    setLoading(true);
    try {
      const params: Record<string, string> = {
        page: pageNum.toString(),
        limit: "20",
        type: "funding",
      };

      if (search) params.q = search;
      if (minScore > 0) params.min_score = minScore.toString();

      const data = await getItems(params);
      
      if (reset) {
        setItems(data);
      } else {
        setItems((prev) => [...prev, ...data]);
      }
      
      setHasMore(data.length === 20);
    } catch (error) {
      console.error("Failed to fetch items:", error);
    } finally {
      setLoading(false);
    }
  }, [search, minScore]);

  const fetchFavorites = useCallback(async () => {
    try {
      const favs = await getFavorites();
      setFavoriteIds(new Set(favs.map((f: Item) => f.id)));
    } catch {
      // User might not be logged in
    }
  }, []);

  useEffect(() => {
    setPage(1);
    fetchItems(1, true);
    fetchFavorites();
  }, [search, minScore, fetchItems, fetchFavorites]);

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchItems(nextPage);
  };

  const handleReset = () => {
    setSearch("");
    setDateRange("all");
    setMinScore(0);
  };

  const handleItemClick = (itemId: number) => {
    setSelectedItemId(itemId);
    setDrawerOpen(true);
  };

  const handleFavoriteChange = (itemId: number, isFavorite: boolean) => {
    setFavoriteIds((prev) => {
      const next = new Set(prev);
      if (isFavorite) {
        next.add(itemId);
      } else {
        next.delete(itemId);
      }
      return next;
    });
  };

  const handleRefresh = () => {
    setPage(1);
    fetchItems(1, true);
  };

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl px-6 py-8 lg:px-8">
        {/* Header */}
        <PageHeader 
          title="Funding Intelligence" 
          description="Track AI funding rounds with MENA market analysis"
        >
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={loading}
            className="h-10 gap-2 rounded-xl border-border/60 text-[14px]"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </PageHeader>

        {/* Filter bar */}
        <div className="mt-8 mb-6">
          <FilterBar
            search={search}
            onSearchChange={setSearch}
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            minScore={minScore}
            onMinScoreChange={setMinScore}
            onReset={handleReset}
          />
        </div>

        {/* Item list */}
        <div className="rounded-2xl border border-border/60 bg-card shadow-soft overflow-hidden">
          {loading && items.length === 0 ? (
            <SkeletonList count={10} />
          ) : items.length === 0 ? (
            <EmptyState type="no-results" />
          ) : (
            <>
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

              {/* Load more */}
              {hasMore && (
                <div className="border-t border-border/40 p-5 text-center">
                  <Button
                    variant="ghost"
                    onClick={handleLoadMore}
                    disabled={loading}
                    className="h-10 rounded-xl text-[14px] font-medium"
                  >
                    {loading ? "Loading..." : "Load more"}
                  </Button>
                </div>
              )}
            </>
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
