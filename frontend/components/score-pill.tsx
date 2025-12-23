"use client";

import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ScorePillProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

export function ScorePill({ score, size = "md", showLabel = false, className }: ScorePillProps) {
  const getScoreConfig = (s: number) => {
    if (s >= 70) return { 
      class: "score-high", 
      label: "High fit",
      barColor: "bg-[hsl(var(--score-high))]"
    };
    if (s >= 40) return { 
      class: "score-medium", 
      label: "Medium fit",
      barColor: "bg-[hsl(var(--score-medium))]"
    };
    return { 
      class: "score-low", 
      label: "Low fit",
      barColor: "bg-[hsl(var(--score-low))]"
    };
  };

  const config = getScoreConfig(score);

  const sizeClasses = {
    sm: "h-7 min-w-[52px] text-[12px] rounded-lg gap-1.5 px-2",
    md: "h-8 min-w-[60px] text-[13px] rounded-xl gap-2 px-2.5",
    lg: "h-10 min-w-[72px] text-[15px] rounded-xl gap-2.5 px-3",
  };

  const barSizes = {
    sm: "h-1 w-6",
    md: "h-1 w-8",
    lg: "h-1.5 w-10",
  };

  return (
    <TooltipProvider delayDuration={300}>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              "inline-flex items-center justify-center font-semibold tabular-nums transition-all",
              config.class,
              sizeClasses[size],
              className
            )}
          >
            <span>{score}</span>
            <div className={cn("rounded-full bg-current/20 overflow-hidden", barSizes[size])}>
              <div
                className={cn("h-full rounded-full transition-all duration-500", config.barColor)}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent 
          side="top" 
          className="rounded-xl px-3 py-2 text-[13px]"
        >
          <p className="font-medium">MENA Fit Score: {score}/100</p>
          <p className="text-muted-foreground">{config.label}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
