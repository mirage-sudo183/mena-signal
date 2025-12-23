import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, description, children, className }: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-4", className)}>
      <div className="space-y-1">
        <h1 className="text-[28px] font-semibold tracking-tight text-balance">{title}</h1>
        {description && (
          <p className="text-[15px] text-muted-foreground">{description}</p>
        )}
      </div>
      {children && <div className="flex items-center gap-3 mt-4 sm:mt-0">{children}</div>}
    </div>
  );
}
