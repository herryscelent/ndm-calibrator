import { useEffect, useRef, useState } from "react";
import { BadgeCheck, ChevronDown, Play, Square } from "lucide-react";
import {
  CartesianGrid,
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
import { Progress } from "@/components/common/progress";
import { Separator } from "@/components/common/separator";
import { cn } from "@/lib/utils";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import { bestParameters, convergence, identificationTimeline, type ConvergencePoint } from "@/data/mock/convergence";

type AlgoKey = "least_squares" | "nelder_mead" | "differential_evolution" | "multistart";
type RunState = "idle" | "running" | "completed";

const algorithms: { key: AlgoKey; label: string; detail: string }[] = [
  { key: "least_squares", label: "Least Squares", detail: "TRF / Dogbox" },
  { key: "nelder_mead", label: "Nelder-Mead", detail: "无梯度局部搜索" },
  { key: "differential_evolution", label: "Differential Evolution", detail: "全局搜索" },
  { key: "multistart", label: "Multi-start", detail: "多起点局部搜索" },
];

export function IdentificationPage({ onToast }: { onToast: (msg: string) => void }) {
  const [algo, setAlgo] = useState<AlgoKey>("least_squares");
  const [state, setState] = useState<RunState>("idle");
  const [progress, setProgress] = useState(0);
  const [evals, setEvals] = useState(0);
  const [objective, setObjective] = useState(convergence[0].objective);
  const [elapsed, setElapsed] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [chartData, setChartData] = useState<ConvergencePoint[]>([]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  function start() {
    setState("running");
    setProgress(0);
    setEvals(0);
    setObjective(convergence[0].objective);
    setElapsed(0);
    setChartData([]);
    let step = 0;
    timerRef.current = setInterval(() => {
      step += 1;
      const frac = step / 20;
      if (frac >= 1) {
        if (timerRef.current) clearInterval(timerRef.current);
        setProgress(100);
        setEvals(identificationTimeline.totalEvaluations);
        setObjective(identificationTimeline.bestObjective);
        setElapsed(identificationTimeline.elapsedSeconds);
        setChartData(convergence);
        setState("completed");
        onToast("Identification completed");
        return;
      }
      const idx = Math.min(convergence.length - 1, Math.floor(frac * convergence.length));
      setProgress(Math.round(frac * 100));
      setEvals(convergence[idx].evaluations);
      setObjective(convergence[idx].objective);
      setElapsed(+(frac * 1.72).toFixed(2));
      setChartData(convergence.slice(0, idx + 1));
    }, 180);
  }

  function cancel() {
    if (timerRef.current) clearInterval(timerRef.current);
    setState("idle");
    setProgress(0);
  }

  return (
    <div>
      <PageHeader
        title="参数辨识"
        description="选择求解算法并运行模型参数估计。"
        actions={
          state === "running" ? (
            <Button variant="danger" onClick={cancel}>
              <Square className="h-4 w-4" /> 取消
            </Button>
          ) : (
            <Button onClick={start} disabled={state === "completed" && false}>
              <Play className="h-4 w-4" /> 开始辨识
            </Button>
          )
        }
      />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-5">
        {/* Left: algorithm + settings */}
        <div className="space-y-5 xl:col-span-2">
          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">算法选择</h3>
            <div className="grid grid-cols-2 gap-2">
              {algorithms.map((a) => (
                <button
                  key={a.key}
                  onClick={() => setAlgo(a.key)}
                  className={cn(
                    "rounded-[8px] border px-3 py-2.5 text-left transition-colors duration-150",
                    algo === a.key
                      ? "border-accent/50 bg-surface-selected"
                      : "border-border bg-surface hover:bg-surface-hover"
                  )}
                >
                  <div className="text-[13px] font-medium text-text-primary">{a.label}</div>
                  <div className="mt-0.5 text-[11px] text-text-muted">{a.detail}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">算法设置</h3>
            <div className="space-y-2.5">
              {[
                ["Method", "TRF"],
                ["Max evaluations", "2000"],
                ["Tolerance", "1e-8"],
                ["Seed", "42"],
              ].map(([k, v]) => (
                <div key={k} className="flex items-center justify-between">
                  <span className="text-[13px] text-text-secondary">{k}</span>
                  <span className="font-mono text-[13px] text-text-primary">{v}</span>
                </div>
              ))}
            </div>
            <Separator className="my-3" />
            <button
              onClick={() => setShowAdvanced((s) => !s)}
              className="flex w-full items-center justify-between text-[13px] text-text-secondary hover:text-text-primary"
            >
              <span>Advanced</span>
              <ChevronDown
                className={cn("h-4 w-4 transition-transform duration-150", showAdvanced && "rotate-180")}
              />
            </button>
            {showAdvanced ? (
              <div className="mt-2 space-y-2.5 border-l-2 border-border pl-3">
                {[
                  ["rtol", "1e-6"],
                  ["atol", "1e-9"],
                  ["mutation", "0.5 – 1.0"],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-[13px] text-text-muted">{k}</span>
                    <span className="font-mono text-[13px] text-text-secondary">{v}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        {/* Right: runtime + convergence */}
        <div className="space-y-5 xl:col-span-3">
          <div className="rounded-lg border border-border bg-surface p-5">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-[15px] font-semibold text-text-primary">运行状态</h3>
              <Badge
                variant={state === "running" ? "running" : state === "completed" ? "success" : "neutral"}
              >
                {state === "idle" ? "Ready" : state === "running" ? "Running" : "Completed"}
              </Badge>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-text-muted">Evaluations</div>
                <div className="text-xl font-semibold text-text-primary text-tabular">
                  {evals.toLocaleString()}
                  <span className="text-sm font-normal text-text-muted"> / {identificationTimeline.maxEvaluations.toLocaleString()}</span>
                </div>
              </div>
              <div>
                <div className="text-xs text-text-muted">Best Objective</div>
                <div className="text-xl font-semibold text-text-primary text-tabular">
                  {objective.toFixed(4)}
                </div>
              </div>
              <div>
                <div className="text-xs text-text-muted">Elapsed</div>
                <div className="text-xl font-semibold text-text-primary text-tabular">
                  {elapsed.toFixed(2)} s
                </div>
              </div>
            </div>

            {state === "running" ? (
              <Progress value={progress} className="mt-4 h-1.5" />
            ) : null}
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-3 text-[15px] font-semibold text-text-primary">
              Objective vs Evaluations
            </h3>
            <div className="h-[240px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis
                    dataKey="evaluations"
                    tick={{ fontSize: 11, fill: "#929caa" }}
                    tickLine={false}
                    axisLine={{ stroke: "#dde3ea" }}
                    label={{ value: "Evaluations", position: "insideBottom", offset: -2, fontSize: 11, fill: "#929caa" }}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: "#929caa" }}
                    tickLine={false}
                    axisLine={{ stroke: "#dde3ea" }}
                    width={44}
                    scale="log"
                    domain={[0.003, 0.3]}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="objective"
                    name="Objective"
                    stroke={chartColors.measured}
                    strokeWidth={1.8}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {state === "completed" ? (
            <div className="flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-3">
              <Badge variant="success">
                <BadgeCheck className="h-3.5 w-3.5" /> Completed
              </Badge>
              <span className="text-[13px] text-text-secondary">最佳参数:</span>
              {Object.entries(bestParameters).map(([k, v]) => (
                <span key={k} className="font-mono text-[13px] text-text-primary">
                  {k} = {v.toFixed(3)}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
