import { ArrowRight, CheckCircle2 } from "lucide-react";
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

import { Badge } from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { PageHeader } from "@/components/common/page-header";
import { MetricCard } from "@/components/metrics/metric-card";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import type { PageKey } from "@/components/navigation/config";
import { fitMetrics, project } from "@/data/mock/project";
import { measuredSimulated } from "@/data/mock/timeSeries";

const workflowSteps: { key: PageKey; label: string }[] = [
  { key: "data", label: "数据管理" },
  { key: "model", label: "模型定义" },
  { key: "parameters", label: "参数配置" },
  { key: "identification", label: "参数辨识" },
  { key: "calibration", label: "模型校准" },
  { key: "diagnostics", label: "诊断分析" },
];

export function DashboardPage({ onNavigate }: { onNavigate: (k: PageKey) => void }) {
  return (
    <div>
      <PageHeader
        title="项目首页"
        description="查看当前模型、数据、参数辨识结果及整体工作流程。"
        actions={
          <>
            <Button variant="secondary" onClick={() => onNavigate("dashboard")}>
              新建项目
            </Button>
            <Button onClick={() => onNavigate("dashboard")}>打开项目</Button>
          </>
        }
      />

      {/* Project summary */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4 rounded-lg border border-border bg-surface px-5 py-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-[15px] font-semibold text-text-primary">{project.name}</h2>
            <Badge variant="success">
              <span className="h-1.5 w-1.5 rounded-full bg-success" />
              就绪
            </Badge>
          </div>
          <p className="mt-1 text-[13px] text-text-secondary">
            {project.description} · {project.tagline}
          </p>
          <p className="mt-0.5 text-xs text-text-muted">最后更新：{project.lastUpdated}</p>
        </div>
      </div>

      {/* Metric cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 xl:grid-cols-4">
        <MetricCard label="样本数" value={project.samples.toLocaleString()} />
        <MetricCard label="待辨识参数" value="2" />
        <MetricCard label="RMSE" value={fitMetrics.RMSE.toFixed(4)} />
        <MetricCard label="R²" value={fitMetrics.R2.toFixed(4)} />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        {/* Workflow */}
        <div className="xl:col-span-2">
          <h3 className="mb-3 text-[15px] font-semibold text-text-primary">工作流程</h3>
          <div className="border-t border-border pt-2">
            {workflowSteps.map((step, i) => (
              <div key={step.key}>
                <button
                  onClick={() => onNavigate(step.key)}
                  className="group flex w-full items-center gap-3 rounded-[6px] px-2 py-2 text-left transition-colors hover:bg-surface-hover"
                >
                  <CheckCircle2 className="h-[18px] w-[18px] shrink-0 text-accent" />
                  <span className="text-[13px] text-text-primary group-hover:text-accent">
                    {step.label}
                  </span>
                  <ArrowRight className="ml-auto h-3.5 w-3.5 text-text-muted opacity-0 transition-opacity group-hover:opacity-100" />
                </button>
                {i < workflowSteps.length - 1 ? (
                  <div className="ml-[17px] h-3 w-px bg-border" />
                ) : null}
              </div>
            ))}
          </div>
        </div>

        {/* Main result preview */}
        <div className="xl:col-span-3">
          <h3 className="mb-3 text-[15px] font-semibold text-text-primary">
            实测值与模拟值
          </h3>
          <div className="border-t border-border pt-2">
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={measuredSimulated} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
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
                    width={44}
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
                    strokeWidth={1.5}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
