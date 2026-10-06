import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  sub?: string;
  className?: string;
}

/** Compact KPI card: small label + tabular value. */
export function MetricCard({ label, value, sub, className }: MetricCardProps) {
  return (
    <div
      className={cn(
        "flex min-w-0 flex-col gap-0.5 rounded-lg border border-border bg-surface px-4 py-3 sm:min-w-[140px]",
        className
      )}
    >
      <span className="text-xs text-text-secondary">{label}</span>
      <span className="text-[24px] font-semibold leading-tight text-text-primary text-tabular">
        {value}
      </span>
      {sub ? <span className="text-xs text-text-muted">{sub}</span> : null}
    </div>
  );
}
