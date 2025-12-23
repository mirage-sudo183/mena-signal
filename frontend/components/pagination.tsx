"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages: (number | string)[] = [];
  
  // Always show first page
  pages.push(1);
  
  // Show ellipsis if needed
  if (page > 3) {
    pages.push("...");
  }
  
  // Show pages around current page
  for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
    if (!pages.includes(i)) {
      pages.push(i);
    }
  }
  
  // Show ellipsis if needed
  if (page < totalPages - 2) {
    pages.push("...");
  }
  
  // Always show last page
  if (totalPages > 1 && !pages.includes(totalPages)) {
    pages.push(totalPages);
  }

  return (
    <div className="flex items-center justify-center gap-1">
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {pages.map((p, i) =>
        typeof p === "number" ? (
          <Button
            key={i}
            variant={p === page ? "default" : "outline"}
            size="icon"
            onClick={() => onPageChange(p)}
          >
            {p}
          </Button>
        ) : (
          <span key={i} className="px-2 text-muted-foreground">
            {p}
          </span>
        )
      )}

      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}

