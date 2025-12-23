"use client";

import { useState, useEffect } from "react";
import { Search, X, SlidersHorizontal } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { getTags, type Tag } from "@/lib/api";

export interface FilterState {
  type?: string;
  q?: string;
  min_score?: number;
  tag?: number;
  date_range?: string;
}

interface FiltersProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

export function Filters({ filters, onChange }: FiltersProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [searchValue, setSearchValue] = useState(filters.q || "");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await getTags();
        setTags(data);
      } catch {
        // User might not be logged in
      }
    };
    fetchTags();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onChange({ ...filters, q: searchValue || undefined });
  };

  const clearFilters = () => {
    setSearchValue("");
    onChange({});
  };

  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Search by title, company, or summary..."
              className="pl-9"
            />
          </div>
          <Button type="submit" variant="secondary">
            Search
          </Button>
        </form>

        {/* Quick Filters */}
        <div className="flex gap-2">
          <Select
            value={filters.date_range || "all"}
            onValueChange={(value) =>
              onChange({ ...filters, date_range: value === "all" ? undefined : value })
            }
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Time" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={filters.min_score?.toString() || "0"}
            onValueChange={(value) =>
              onChange({ ...filters, min_score: value === "0" ? undefined : parseInt(value) })
            }
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Min Score" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0">Any Score</SelectItem>
              <SelectItem value="40">40+ Score</SelectItem>
              <SelectItem value="60">60+ Score</SelectItem>
              <SelectItem value="70">70+ Score</SelectItem>
              <SelectItem value="80">80+ Score</SelectItem>
            </SelectContent>
          </Select>

          {/* Advanced Filters Dialog */}
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2">
                <SlidersHorizontal className="h-4 w-4" />
                <span className="hidden sm:inline">Filters</span>
                {activeFilterCount > 0 && (
                  <Badge variant="secondary" className="ml-1">
                    {activeFilterCount}
                  </Badge>
                )}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Filter Items</DialogTitle>
              </DialogHeader>
              <div className="space-y-6 py-4">
                {/* Tags Filter */}
                {tags.length > 0 && (
                  <div className="space-y-2">
                    <Label>Filter by Tag</Label>
                    <Select
                      value={filters.tag?.toString() || "all"}
                      onValueChange={(value) =>
                        onChange({ ...filters, tag: value === "all" ? undefined : parseInt(value) })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select tag" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Tags</SelectItem>
                        {tags.map((tag) => (
                          <SelectItem key={tag.id} value={tag.id.toString()}>
                            <div className="flex items-center gap-2">
                              {tag.color && (
                                <div
                                  className="w-3 h-3 rounded-full"
                                  style={{ backgroundColor: tag.color }}
                                />
                              )}
                              {tag.name}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <Separator />

                {/* Clear Filters */}
                <Button
                  variant="outline"
                  onClick={() => {
                    clearFilters();
                    setIsOpen(false);
                  }}
                  className="w-full"
                >
                  <X className="h-4 w-4 mr-2" />
                  Clear All Filters
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          {activeFilterCount > 0 && (
            <Button variant="ghost" size="icon" onClick={clearFilters} title="Clear all filters">
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {filters.q && (
            <Badge variant="secondary" className="gap-1">
              Search: {filters.q}
              <button
                onClick={() => {
                  setSearchValue("");
                  onChange({ ...filters, q: undefined });
                }}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.date_range && (
            <Badge variant="secondary" className="gap-1">
              {filters.date_range === "24h" ? "Last 24 hours" :
               filters.date_range === "7d" ? "Last 7 days" : "Last 30 days"}
              <button
                onClick={() => onChange({ ...filters, date_range: undefined })}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.min_score && (
            <Badge variant="secondary" className="gap-1">
              Score ≥ {filters.min_score}
              <button
                onClick={() => onChange({ ...filters, min_score: undefined })}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.tag && (
            <Badge variant="secondary" className="gap-1">
              Tag: {tags.find((t) => t.id === filters.tag)?.name}
              <button
                onClick={() => onChange({ ...filters, tag: undefined })}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}

