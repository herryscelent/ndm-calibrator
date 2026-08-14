import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/common/badge";
import { PageHeader } from "@/components/common/page-header";
import { MetricCard } from "@/components/metrics/metric-card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/common/tabs";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import {
  correlation,
  identifiability,
  residualHistogram,
  residuals,
  residualSummary,
  sensitivity,
} from "@/data/mock/diagnostics";
import { cn } from "@/lib/utils";

const barColors = ["#e6ebf1", "#e6ebf1", "#e6ebf1", "#e6ebf1", "#c9d2dc", "#356fe5"];

export function DiagnosticsPage() {
  return (
    <div>
      <PageHeader title="诊断分析" description="残差分析、参数敏感性与可辨识性诊断。" />

      <Tabs defaultValue="residuals">
        <TabsList>
          <TabsTrigger value="residuals">Residuals</TabsTrigger>
          <TabsTrigger value="sensitivity">Sensitivity</TabsTrigger>
          <TabsTrigger value="identifiability">Identifiability</TabsTrigger>
          <TabsTrigger value="correlation">Correlation</TabsTrigger>
        </TabsList>

        {/* ---------------- Residuals ---------------- */}
        <TabsContent value="residuals">
          <div className="mb-5 grid grid-cols-2 gap-3 xl:grid-cols-4">
            <MetricCard label="Mean" value={residualSummary.mean.toFixed(4)} />
            <MetricCard label="Std" value={residualSummary.std.toFixed(4)} />
            <MetricCard label="Max Abs" value={residualSummary.maxAbs.toFixed(3)} />
            <MetricCard label="ACF Peak" value={residualSummary.acfPeak.toFixed(3)} />
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">Residual vs Time</h3>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={residuals} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis dataKey="t" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={44} />
                  <Tooltip content={<ChartTooltip />} />
                  <Line type="monotone" dataKey="residual" name="Residual" stroke={chartColors.residual} strokeWidth={1.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-5 rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">Residual Distribution</h3>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={residualHistogram} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                  <XAxis dataKey="bin" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={32} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="count" name="Count" radius={[3, 3, 0, 0]}>
                    {residualHistogram.map((_, i) => (
                      <Cell key={i} fill={barColors[i % barColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </TabsContent>

        {/* ---------------- Sensitivity ---------------- */}
        <TabsContent value="sensitivity">
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <div className="rounded-lg border border-border bg-surface p-5">
              <h3 className="mb-3 text-[15px] font-semibold text-text-primary">Normalized Sensitivity</h3>
              <div className="h-[220px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[
                      { name: "k", rms: sensitivity.k.rms },
                      { name: "c", rms: sensitivity.c.rms },
                    ]}
                    layout="vertical"
                    margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 13, fill: "#20252b" }} tickLine={false} axisLine={false} width={40} />
                    <Tooltip content={<ChartTooltip />} />
                    <Bar dataKey="rms" name="RMS Sensitivity" fill={chartColors.sensitivity} radius={[0, 3, 3, 0]} barSize={22} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="overflow-hidden rounded-lg border border-border">
              <table className="w-full text-[13px]">
                <thead>
                  <tr className="border-b border-border bg-surface-secondary">
                    {["Parameter", "Sensitivity", "Rank"].map((h) => (
                      <th key={h} className="px-4 py-2 text-left font-medium text-text-secondary">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(sensitivity).map(([name, s]) => (
                    <tr key={name} className="border-b border-border/60 last:border-b-0 hover:bg-surface-hover">
                      <td className="px-4 py-2.5 font-mono text-text-primary">{name}</td>
                      <td className="px-4 py-2.5 text-tabular text-text-primary">{s.rms.toFixed(2)}</td>
                      <td className="px-4 py-2.5 text-tabular text-text-secondary">{s.rank}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* ---------------- Identifiability ---------------- */}
        <TabsContent value="identifiability">
          <div className="mb-5 grid grid-cols-3 gap-3">
            <MetricCard label="Condition Number" value={identifiability.conditionNumber.toFixed(1)} />
            <MetricCard label="Rank" value={`${identifiability.rank} / ${identifiability.rankTotal}`} sub="Good" />
            <MetricCard label="Min Singular Value" value={identifiability.minSingularValue.toFixed(3)} />
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">Singular Values</h3>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={identifiability.singularValues.map((v, i) => ({ idx: `SV${i + 1}`, value: v }))}
                  margin={{ top: 8, right: 12, bottom: 8, left: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                  <XAxis dataKey="idx" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={44} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="value" name="Singular Value" fill={chartColors.measured} radius={[3, 3, 0, 0]} barSize={60} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 flex items-start gap-2 rounded-[6px] border border-success/40 bg-success/5 px-3 py-2 text-[13px] text-success">
            <Badge variant="success">Good</Badge>
            <span>{identifiability.note}</span>
          </div>
        </TabsContent>

        {/* ---------------- Correlation ---------------- */}
        <TabsContent value="correlation">
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <div className="rounded-lg border border-border bg-surface p-5">
              <h3 className="mb-4 text-[15px] font-semibold text-text-primary">
                Parameter Correlation
              </h3>
              {/* CSS-grid heatmap (small matrix) */}
              <div className="inline-block">
                <div
                  className="grid gap-1"
                  style={{ gridTemplateColumns: `repeat(${correlation.names.length + 1}, 56px)` }}
                >
                  <div />
                  {correlation.names.map((n) => (
                    <div key={n} className="pb-1 text-center font-mono text-xs text-text-secondary">{n}</div>
                  ))}
                  {correlation.names.map((row, i) => (
                    <>
                      <div key={`l${row}`} className="pr-2 font-mono text-xs text-text-secondary">{row}</div>
                      {correlation.matrix[i].map((v, j) => (
                        <div
                          key={`${i}-${j}`}
                          className={cn(
                            "flex h-11 items-center justify-center rounded-[6px] font-mono text-[13px]",
                            Math.abs(v) > 0.95
                              ? "bg-accent-subtle text-accent"
                              : v > 0.5
                                ? "bg-surface-hover text-text-primary"
                                : "bg-surface-secondary text-text-secondary"
                          )}
                        >
                          {v.toFixed(2)}
                        </div>
                      ))}
                    </>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-[15px] font-semibold text-text-primary">
                Highest parameter correlation
              </h3>
              <div className="flex items-center gap-3 rounded-lg border border-border bg-surface px-4 py-3">
                <span className="font-mono text-[13px] text-text-primary">
                  {correlation.highest.a} ↔ {correlation.highest.b}
                </span>
                <span className="text-lg font-semibold text-text-primary text-tabular">
                  {correlation.highest.value.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
