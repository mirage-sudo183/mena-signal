import { cn } from "@/lib/utils";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-lg bg-muted animate-pulse", className)}
      {...props}
    />
  );
}

export { Skeleton };
