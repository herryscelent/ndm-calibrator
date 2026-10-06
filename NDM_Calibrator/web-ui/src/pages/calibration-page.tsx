import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { PageHeader } from "@/components/common/page-header";
import { MetricCard } from "@/components/metrics/metric-card";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import { fitMetrics } from "@/data/mock/project";
import { measuredSimulated } from "@/data/mock/timeSeries";

const parameterResults = [
  { parameter: "k", estimate: "2.514", initial: "2.000", change: "+25.7%", fixed: false },
  { parameter: "c", estimate: "0.176", initial: "0.200", change: "-12.0%", fixed: false },
  { parameter: "m", estimate: "1.000", initial: "1.000", change: "固定", fixed: true },
];

export function CalibrationPage() {
  return (
    <div>
      <PageHeader
        title="模型校准"
        description="比较实验观测与当前辨识模型的拟合结果。"
      />

      {/* KPI cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 xl:grid-cols-4">
        <MetricCard label="RMSE" value={fitMetrics.RMSE.toFixed(4)} />
        <MetricCard label="MAE" value={fitMetrics.MAE.toFixed(4)} />
        <MetricCard label="R²" value={fitMetrics.R2.toFixed(4)} />
        <MetricCard label="运行时间" value={`${fitMetrics.Runtime.toFixed(2)} s`} />
      </div>

      {/* Main calibration plot */}
      <div className="rounded-lg border border-border bg-surface p-5">
        <h3 className="mb-4 text-[15px] font-semibold text-text-primary">
          实测 vs 模拟
        </h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={measuredSimulated} margin={{ top: 8, right: 20, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
              <XAxis
                dataKey="t"
                tick={{ fontSize: 11, fill: "#929caa" }}
                tickLine={false}
                axisLine={{ stroke: "#dde3ea" }}
                label={{ value: "时间 (s)", position: "insideBottom", offset: -2, fontSize: 11, fill: "#929caa" }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#929caa" }}
                tickLine={false}
                axisLine={{ stroke: "#dde3ea" }}
                label={{ value: "position (m)", angle: -90, position: "insideLeft", fontSize: 11, fill: "#929caa" }}
                width={50}
              />
              <Tooltip content={<ChartTooltip />} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line
                type="monotone"
                dataKey="measured"
                name="实测值"
                stroke={chartColors.measured}
                strokeWidth={1.5}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="simulated"
                name="模拟值"
                stroke={chartColors.simulated}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Parameter result table */}
      <div className="mt-6">
        <h3 className="mb-3 text-[15px] font-semibold text-text-primary">参数结果</h3>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[560px] text-[13px]">
            <thead>
              <tr className="border-b border-border bg-surface-secondary">
                {["参数", "估计值", "初值", "变化"].map((h) => (
                  <th key={h} className="px-4 py-2 text-left font-medium text-text-secondary">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {parameterResults.map((p) => (
                <tr key={p.parameter} className="border-b border-border/60 last:border-b-0 hover:bg-surface-hover">
                  <td className="px-4 py-2 font-mono text-text-primary">{p.parameter}</td>
                  <td className="px-4 py-2 text-tabular text-text-primary">{p.estimate}</td>
                  <td className="px-4 py-2 text-tabular text-text-secondary">{p.initial}</td>
                  <td
                    className={
                      p.fixed
                        ? "px-4 py-2 text-text-muted"
                        : p.change.startsWith("+")
                          ? "px-4 py-2 text-tabular text-success"
                          : "px-4 py-2 text-tabular text-warning"
                    }
                  >
                    {p.change}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
