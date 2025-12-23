"use client";

import { 
  Wallet, 
  Languages, 
  Scale, 
  GitBranch, 
  Clock 
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ScoreBreakdownProps {
  rubric: {
    budget_buyer_exists: number;
    localization_arabic_bilingual: number;
    regulatory_friction: number;
    distribution_path: number;
    time_to_revenue: number;
  };
}

const rubricItems = [
  {
    key: "budget_buyer_exists" as const,
    label: "Budget Buyer Exists",
    description: "MENA buyers with budget for this solution",
    icon: Wallet,
  },
  {
    key: "localization_arabic_bilingual" as const,
    label: "Localization Ease",
    description: "Arabic/bilingual adaptation requirements",
    icon: Languages,
  },
  {
    key: "regulatory_friction" as const,
    label: "Regulatory Path",
    description: "Higher score = easier regulatory compliance",
    icon: Scale,
  },
  {
    key: "distribution_path" as const,
    label: "Distribution Path",
    description: "Clear go-to-market channels in MENA",
    icon: GitBranch,
  },
  {
    key: "time_to_revenue" as const,
    label: "Time to Revenue",
    description: "Speed to generate MENA revenue",
    icon: Clock,
  },
];

export function ScoreBreakdown({ rubric }: ScoreBreakdownProps) {
  return (
    <div className="space-y-4">
      {rubricItems.map((item) => {
        const score = rubric[item.key];
        const percentage = (score / 20) * 100;
        
        return (
          <div key={item.key} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <item.icon className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium text-sm">{item.label}</span>
              </div>
              <span className="font-bold text-sm">{score}/20</span>
            </div>
            <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className={cn(
                  "h-full transition-all duration-500",
                  percentage >= 70 ? "bg-emerald-500" :
                  percentage >= 40 ? "bg-amber-500" :
                  "bg-red-500"
                )}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">{item.description}</p>
          </div>
        );
      })}
    </div>
  );
}

