/** Chart series tokens — single source for line colours across all charts. */
export const chartColors = {
  measured: "#356fe5",
  simulated: "#c0613f",
  residual: "#b7791f",
  sensitivity: "#687482",
  bootstrap: "#27875a",
  grid: "#e6ebf1",
  accent: "#356fe5",
};

export interface ChartTooltipEntry {
  name: string;
  value: number | string;
  color?: string;
}

/** Shared tooltip content for Recharts. */
export function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-[6px] border border-border bg-surface px-3 py-2 shadow-sm">
      {label !== undefined ? (
        <div className="mb-1 text-xs font-medium text-text-primary">{label}</div>
      ) : null}
      <div className="space-y-0.5">
        {payload.map((p: any, i: number) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span
              className="h-2 w-2 rounded-full"
              style={{ background: p.color ?? p.stroke ?? chartColors.accent }}
            />
            <span className="text-text-secondary">{p.name}:</span>
            <span className="font-medium text-text-primary text-tabular">{p.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ChartGrid(props: { vertical?: boolean }) {
  return {
    strokeDasharray: "3 3",
    stroke: chartColors.grid,
    ...(props.vertical ? { vertical: true } : {}),
  };
}
