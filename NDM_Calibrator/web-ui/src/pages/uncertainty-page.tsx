import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Badge } from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { PageHeader } from "@/components/common/page-header";
import { MetricCard } from "@/components/metrics/metric-card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/common/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/common/tabs";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import { bootstrap, multistart } from "@/data/mock/bootstrap";

export function UncertaintyPage({ onToast }: { onToast: (msg: string) => void }) {
  const [selParam, setSelParam] = useState<string>("k");
  const dist = bootstrap.distributions[selParam as keyof typeof bootstrap.distributions];

  const histData = dist.bins.map((b, i) => ({ bin: b, count: dist.counts[i] }));
  const multistartData = multistart.kSamples.map((v, i) => ({
    start: i + 1,
    k: v,
    c: multistart.cSamples[i],
  }));

  return (
    <div>
      <PageHeader
        title="可信度分析"
        description="多起点稳定性与 Bootstrap 参数可信度区间。"
      />

      <Tabs defaultValue="multistart">
        <TabsList>
          <TabsTrigger value="multistart">多起点分析</TabsTrigger>
          <TabsTrigger value="bootstrap">Bootstrap</TabsTrigger>
        </TabsList>

        {/* ---------------- Multi-start ---------------- */}
        <TabsContent value="multistart">
          <div className="mb-5 grid grid-cols-2 gap-3 xl:grid-cols-4">
            <MetricCard label="起点数" value={String(multistart.starts)} />
            <MetricCard label="成功次数" value={String(multistart.successful)} />
            <MetricCard label="成功率" value={multistart.successRate} />
            <MetricCard label="最佳 RMSE" value={multistart.bestRMSE.toFixed(4)} />
          </div>

          <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <div className="rounded-lg border border-border bg-surface p-5">
              <h3 className="mb-3 text-[15px] font-semibold text-text-primary">
                参数分布（多起点）
              </h3>
              <div className="h-[260px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={multistartData} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                    <XAxis dataKey="start" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                    <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={44} domain={[0, 3]} />
                    <Tooltip content={<ChartTooltip />} />
                    <Bar dataKey="k" name="k" fill={chartColors.measured} radius={[2, 2, 0, 0]} />
                    <Bar dataKey="c" name="c" fill={chartColors.bootstrap} radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-[15px] font-semibold text-text-primary">运行结果</h3>
              <div className="overflow-x-auto rounded-lg border border-border">
                <table className="w-full min-w-[320px] text-[13px]">
                  <thead>
                    <tr className="border-b border-border bg-surface-secondary">
                      {["起点", "k", "c"].map((h) => (
                        <th key={h} className="px-4 py-2 text-left font-medium text-text-secondary">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {multistartData.map((r) => (
                      <tr key={r.start} className="border-b border-border/60 last:border-b-0 hover:bg-surface-hover">
                        <td className="px-4 py-1.5 text-tabular text-text-muted">{r.start}</td>
                        <td className="px-4 py-1.5 text-tabular text-text-primary">{r.k.toFixed(3)}</td>
                        <td className="px-4 py-1.5 text-tabular text-text-primary">{r.c.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* ---------------- Bootstrap ---------------- */}
        <TabsContent value="bootstrap">
          <div className="mb-5 grid grid-cols-2 gap-3 sm:flex sm:items-center">
            <MetricCard label="Bootstrap 样本数" value={String(bootstrap.samples)} />
            <MetricCard label="随机种子" value={String(bootstrap.seed)} />
            <MetricCard label="状态" value="已完成" />
          </div>

          <div className="mb-5 overflow-x-auto rounded-lg border border-border">
            <table className="w-full min-w-[560px] text-[13px]">
              <thead>
                <tr className="border-b border-border bg-surface-secondary">
                  {["参数", "估计值", "中位数", "P2.5", "P97.5"].map((h) => (
                    <th key={h} className="px-4 py-2 text-left font-medium text-text-secondary">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bootstrap.rows.map((r) => (
                  <tr key={r.parameter} className="border-b border-border/60 last:border-b-0 hover:bg-surface-hover">
                    <td className="px-4 py-2 font-mono text-text-primary">{r.parameter}</td>
                    <td className="px-4 py-2 text-tabular text-text-primary">{r.estimate.toFixed(3)}</td>
                    <td className="px-4 py-2 text-tabular text-text-primary">{r.median.toFixed(3)}</td>
                    <td className="px-4 py-2 text-tabular text-text-secondary">{r.p2_5.toFixed(2)}</td>
                    <td className="px-4 py-2 text-tabular text-text-secondary">{r.p97_5.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[13px] text-text-secondary">参数:</span>
            <Select value={selParam} onValueChange={setSelParam}>
              <SelectTrigger className="h-9 w-32 text-[13px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="k">k</SelectItem>
                <SelectItem value="c">c</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="secondary" size="sm" onClick={() => onToast("Bootstrap 已重新运行（演示）")}>
              重新运行
            </Button>
          </div>

          <div className="mt-4 rounded-lg border border-border bg-surface p-5">
            <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="text-[15px] font-semibold text-text-primary">
                Bootstrap 参数分布 · {selParam}
              </h3>
              <div className="flex items-center gap-2 text-xs text-text-muted">
                <span className="text-tabular">中位数 {dist.median.toFixed(3)}</span>
                <span className="text-tabular">[{dist.lo.toFixed(2)}, {dist.hi.toFixed(2)}]</span>
                <Badge variant="info">95% 百分位区间</Badge>
              </div>
            </div>
            <div className="h-[240px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={histData} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                  <XAxis dataKey="bin" tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} />
                  <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={36} />
                  <Tooltip content={<ChartTooltip />} />
                  <Bar dataKey="count" name="频数" fill={chartColors.bootstrap} radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
