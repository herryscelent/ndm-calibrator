import { useState } from "react";
import {
  type ColumnDef,
  type CellContext,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowUpDown, Upload } from "lucide-react";
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
import { Input } from "@/components/common/input";
import { PageHeader } from "@/components/common/page-header";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/common/select";
import { chartColors, ChartTooltip } from "@/components/charts/chart-theme";
import {
  columnMappings,
  dataRows,
  dataSummary,
  type RawRow,
} from "@/data/mock/timeSeries";

const cellNum = (c: CellContext<RawRow, unknown>) => {
  const v = Number(c.getValue());
  return <span className="text-tabular">{Number.isInteger(v) ? v : v.toFixed(3)}</span>;
};

const columns: ColumnDef<RawRow>[] = [
  {
    accessorKey: "time",
    header: "time",
    cell: (c) => <span className="text-tabular">{Number(c.getValue()).toFixed(1)}</span>,
  },
  {
    accessorKey: "u",
    header: "u",
    cell: cellNum,
  },
  {
    accessorKey: "position",
    header: "position",
    cell: cellNum,
  },
  {
    accessorKey: "velocity",
    header: "velocity",
    cell: cellNum,
  },
];

export function DataPage() {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [roleMap, setRoleMap] = useState<Record<string, string>>(
    Object.fromEntries(columnMappings.map((m) => [m.column, m.role]))
  );
  const [plotSeries, setPlotSeries] = useState<"position" | "velocity">("position");

  const table = useReactTable({
    data: dataRows,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const plotData = dataRows.map((r) => ({
    t: r.time,
    u: r.u,
    position: r.position,
    velocity: r.velocity,
  }));

  return (
    <div>
      <PageHeader
        title="数据管理"
        description="导入、检查并映射动态系统实验数据。"
        actions={
          <>
            <Button variant="secondary">
              <Upload className="h-4 w-4" /> 导入 CSV
            </Button>
            <Button variant="secondary">
              <Upload className="h-4 w-4" /> 导入 Excel
            </Button>
          </>
        }
      />

      {/* Data summary */}
      <div className="mb-5 flex flex-wrap items-center gap-3 text-[13px] text-text-secondary">
        <span className="text-text-primary font-medium text-tabular">
          {dataSummary.rows.toLocaleString()} 行
        </span>
        <span className="text-border-strong">|</span>
        <span>{dataSummary.columns} 列</span>
        <span className="text-border-strong">|</span>
        <span className="text-tabular">{dataSummary.missing} 个缺失值</span>
        <span className="text-border-strong">|</span>
        <span>时长 {dataSummary.durationMin} 分钟</span>
        <div className="flex w-full gap-2 sm:ml-auto sm:w-auto">
          <Button variant="ghost" size="sm">选择范围</Button>
          <Button variant="ghost" size="sm">处理缺失值</Button>
          <Button variant="ghost" size="sm">重置</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-5">
        {/* Data table */}
        <div className="xl:col-span-3">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-[15px] font-semibold text-text-primary">数据预览</h3>
            <Input
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="筛选…"
              className="h-8 w-44 text-[13px]"
            />
          </div>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full min-w-[560px] text-[13px]">
              <thead>
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id} className="border-b border-border bg-surface-secondary">
                    {hg.headers.map((h) => (
                      <th
                        key={h.id}
                        className="px-3 py-2 text-left font-medium text-text-secondary"
                        onClick={h.column.getToggleSortingHandler()}
                      >
                        <span className="inline-flex items-center gap-1 cursor-pointer select-none">
                          {flexRender(h.column.columnDef.header, h.getContext())}
                          {h.column.getCanSort() ? (
                            <ArrowUpDown className="h-3 w-3 text-text-muted" />
                          ) : null}
                        </span>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-border/60 transition-colors last:border-b-0 hover:bg-surface-hover"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-1.5 text-text-primary">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Column mapping + plot */}
        <div className="flex flex-col gap-5 xl:col-span-2">
          <div>
            <h3 className="mb-2 text-[15px] font-semibold text-text-primary">字段映射</h3>
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full min-w-[320px] text-[13px]">
                <thead>
                  <tr className="border-b border-border bg-surface-secondary">
                    <th className="px-3 py-2 text-left font-medium text-text-secondary">字段</th>
                    <th className="px-3 py-2 text-left font-medium text-text-secondary">角色</th>
                  </tr>
                </thead>
                <tbody>
                  {columnMappings.map((m) => (
                    <tr key={m.column} className="border-b border-border/60 last:border-b-0">
                      <td className="px-3 py-1.5 font-mono text-text-primary">{m.column}</td>
                      <td className="px-3 py-1.5">
                        <Select value={roleMap[m.column]} onValueChange={(v) => setRoleMap({ ...roleMap, [m.column]: v })}>
                          <SelectTrigger className="h-8 w-full text-[13px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {["Time", "Input", "Output", "State", "Ignore"].map((r) => (
                              <SelectItem key={r} value={r}>
                                <span className="flex items-center gap-2">
                                  <Badge
                                    variant={
                                      r === "Time"
                                        ? "info"
                                        : r === "Output"
                                          ? "success"
                                          : r === "Input"
                                            ? "default"
                                            : "neutral"
                                    }
                                  >
                                    {r}
                                  </Badge>
                                  {{ Time: "时间", Input: "输入", Output: "输出", State: "状态", Ignore: "忽略" }[r]}
                                </span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex-1">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-[15px] font-semibold text-text-primary">数据曲线</h3>
              <Select value={plotSeries} onValueChange={(v) => setPlotSeries(v as "position" | "velocity")}>
                <SelectTrigger className="h-8 w-36 text-[13px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="position">输出 · position</SelectItem>
                  <SelectItem value="velocity">状态 · velocity</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="rounded-lg border border-border bg-surface p-4">
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={plotData} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                    <XAxis
                      dataKey="t"
                      tick={{ fontSize: 11, fill: "#929caa" }}
                      tickLine={false}
                      axisLine={{ stroke: "#dde3ea" }}
                    />
                    <YAxis tick={{ fontSize: 11, fill: "#929caa" }} tickLine={false} axisLine={{ stroke: "#dde3ea" }} width={44} />
                    <Tooltip content={<ChartTooltip />} />
                    <Line type="monotone" dataKey="u" name="输入 (u)" stroke={chartColors.measured} strokeWidth={1.5} dot={false} />
                    <Line
                      type="monotone"
                      dataKey={plotSeries}
                      name={plotSeries === "position" ? "position" : "velocity"}
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
    </div>
  );
}
