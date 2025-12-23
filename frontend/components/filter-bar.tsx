"use client";

import { useState } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue 
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface FilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  dateRange: string;
  onDateRangeChange: (value: string) => void;
  minScore: number;
  onMinScoreChange: (value: number) => void;
  onReset: () => void;
  className?: string;
}

const dateRangeOptions = [
  { value: "all", label: "All time" },
  { value: "24h", label: "Last 24 hours" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
];

export function FilterBar({
  search,
  onSearchChange,
  dateRange,
  onDateRangeChange,
  minScore,
  onMinScoreChange,
  onReset,
  className,
}: FilterBarProps) {
  const [scoreValue, setScoreValue] = useState([minScore]);
  const hasFilters = search || dateRange !== "all" || minScore > 0;

  return (
    <div className={cn("flex flex-wrap items-center gap-3", className)}>
      {/* Search */}
      <div className="relative flex-1 min-w-56">
        <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground/60" />
        <Input
          placeholder="Search funding news..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="h-11 rounded-xl border-border/60 bg-background pl-11 pr-4 text-[14px] placeholder:text-muted-foreground/50 focus-visible:ring-1 focus-visible:ring-ring/30"
        />
      </div>

      {/* Date Range */}
      <Select value={dateRange} onValueChange={onDateRangeChange}>
        <SelectTrigger className="h-11 w-36 rounded-xl border-border/60 text-[14px]">
          <SelectValue placeholder="Date range" />
        </SelectTrigger>
        <SelectContent className="rounded-xl">
          {dateRangeOptions.map((option) => (
            <SelectItem 
              key={option.value} 
              value={option.value}
              className="rounded-lg text-[14px]"
            >
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Min Score */}
      <Popover>
        <PopoverTrigger asChild>
          <Button 
            variant="outline" 
            className={cn(
              "h-11 gap-2 rounded-xl border-border/60 text-[14px] font-medium",
              minScore > 0 && "border-foreground/20 bg-foreground/[0.03]"
            )}
          >
            <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
            <span>Min Score:</span>
            <span className="tabular-nums text-foreground">{minScore}</span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-72 rounded-xl p-5" align="end">
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <label className="text-[14px] font-medium">Minimum MENA Fit Score</label>
              <span className="text-[14px] tabular-nums font-medium">{scoreValue[0]}</span>
            </div>
            <Slider
              value={scoreValue}
              onValueChange={setScoreValue}
              onValueCommit={(v) => onMinScoreChange(v[0])}
              max={100}
              step={5}
              className="w-full"
            />
            <div className="flex justify-between text-[12px] text-muted-foreground">
              <span>0</span>
              <span>50</span>
              <span>100</span>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Reset */}
      {hasFilters && (
        <Button
          variant="ghost"
          onClick={onReset}
          className="h-11 gap-2 rounded-xl text-[14px] text-muted-foreground hover:text-foreground"
        >
          <X className="h-4 w-4" />
          Clear
        </Button>
      )}
    </div>
  );
}
