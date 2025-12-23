import { Skeleton } from "@/components/ui/skeleton";

export function SkeletonRow() {
  return (
    <div className="flex items-start gap-5 px-6 py-5 border-b border-border/40 last:border-0 animate-pulse-soft">
      {/* Score skeleton */}
      <Skeleton className="h-8 w-[60px] rounded-xl" />
      
      {/* Content skeleton */}
      <div className="flex-1 space-y-3">
        <Skeleton className="h-4 w-3/4 rounded-lg" />
        <Skeleton className="h-3 w-1/3 rounded-lg" />
        <Skeleton className="h-3 w-full rounded-lg" />
      </div>
      
      {/* Action skeleton */}
      <Skeleton className="h-9 w-9 rounded-xl" />
    </div>
  );
}

export function SkeletonList({ count = 8 }: { count?: number }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonRow key={i} />
      ))}
    </div>
  );
}
