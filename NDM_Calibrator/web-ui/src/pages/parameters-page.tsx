import { useState } from "react";
import { CircleCheck, CircleX, Plus, RotateCcw, Trash2 } from "lucide-react";

import { Badge } from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { PageHeader } from "@/components/common/page-header";
import { cn } from "@/lib/utils";
import { parameters, type ParamStatus, type ParameterConfig } from "@/data/mock/parameters";

function validateParam(p: ParameterConfig): string | null {
  if (p.status === "Fixed") return null;
  if (!(p.lower < p.initial && p.initial < p.upper)) {
    return "Initial value must be between lower and upper bounds.";
  }
  return null;
}

export function ParametersPage({ onToast }: { onToast: (msg: string) => void }) {
  const [rows, setRows] = useState<ParameterConfig[]>(() => parameters.map((p) => ({ ...p })));
  const [selected, setSelected] = useState<number | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const allValid = rows.every((p) => validateParam(p) === null);

  function update(rowIdx: number, field: keyof ParameterConfig, value: number | string) {
    const next = rows.map((r, i) =>
      i === rowIdx ? { ...r, [field]: value } : r
    );
    setRows(next);
    // Live validation
    const errs: Record<string, string> = {};
    next.forEach((p) => {
      const e = validateParam(p);
      if (e) errs[p.name] = e;
    });
    setErrors(errs);
  }

  function toggleStatus(rowIdx: number) {
    const r = rows[rowIdx];
    const next = rows.map((row, i) =>
      i === rowIdx
        ? { ...row, status: (r.status === "Free" ? "Fixed" : "Free") as ParamStatus }
        : row
    );
    setRows(next);
  }

  function removeSelected() {
    if (selected === null) return;
    setRows(rows.filter((_, i) => i !== selected));
    setSelected(null);
  }

  function resetAll() {
    setRows(parameters.map((p) => ({ ...p })));
    setErrors({});
  }

  return (
    <div>
      <PageHeader
        title="参数配置"
        description="设置参数初值、搜索边界及固定状态。"
        actions={
          <Button
            variant="secondary"
            onClick={() => {
              if (allValid) {
                setErrors({});
                onToast("All parameter settings are valid");
              }
            }}
          >
            验证参数
          </Button>
        }
      />

      {/* Toolbar */}
      <div className="mb-3 flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={() => onToast("Parameter added")}>
          <Plus className="h-4 w-4" /> Add
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={removeSelected}
          disabled={selected === null}
        >
          <Trash2 className="h-4 w-4" /> Remove
        </Button>
        <Button variant="ghost" size="sm" onClick={resetAll}>
          <RotateCcw className="h-4 w-4" /> Reset
        </Button>
      </div>

      {/* Parameter table */}
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="border-b border-border bg-surface-secondary">
              <th className="w-8 px-3 py-2" />
              {["Parameter", "Initial", "Lower", "Upper", "Status", "Unit"].map((h) => (
                <th key={h} className="px-3 py-2 text-left font-medium text-text-secondary">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((p, i) => {
              const err = errors[p.name];
              const isFixed = p.status === "Fixed";
              return (
                <tr
                  key={p.name}
                  onClick={() => setSelected(i)}
                  className={cn(
                    "cursor-pointer border-b border-border/60 last:border-b-0 transition-colors hover:bg-surface-hover",
                    selected === i && "bg-surface-selected"
                  )}
                >
                  <td className="px-3 py-2">
                    <span
                      className={cn(
                        "block h-3.5 w-3.5 rounded-full border",
                        selected === i ? "border-accent bg-accent" : "border-border-strong"
                      )}
                    />
                  </td>
                  <td className="px-3 py-2 font-mono text-text-primary">{p.name}</td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      disabled={isFixed}
                      value={Number.isNaN(p.initial) ? "" : p.initial}
                      onChange={(e) => update(i, "initial", parseFloat(e.target.value) || 0)}
                      className={cn(
                        "h-7 w-20 rounded-[6px] border px-2 text-right text-tabular focus:outline-none focus:ring-2 focus:ring-accent/40",
                        isFixed ? "border-border bg-surface-secondary text-text-muted" : "border-border bg-surface text-text-primary",
                        err && "border-danger"
                      )}
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      disabled={isFixed}
                      value={Number.isNaN(p.lower) ? "—" : p.lower}
                      onChange={(e) => update(i, "lower", parseFloat(e.target.value) || 0)}
                      className={cn(
                        "h-7 w-20 rounded-[6px] border px-2 text-right text-tabular focus:outline-none focus:ring-2 focus:ring-accent/40",
                        isFixed ? "border-border bg-surface-secondary text-text-muted" : "border-border bg-surface text-text-primary"
                      )}
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      disabled={isFixed}
                      value={Number.isNaN(p.upper) ? "—" : p.upper}
                      onChange={(e) => update(i, "upper", parseFloat(e.target.value) || 0)}
                      className={cn(
                        "h-7 w-20 rounded-[6px] border px-2 text-right text-tabular focus:outline-none focus:ring-2 focus:ring-accent/40",
                        isFixed ? "border-border bg-surface-secondary text-text-muted" : "border-border bg-surface text-text-primary"
                      )}
                    />
                  </td>
                  <td className="px-3 py-2">
                    <button onClick={() => toggleStatus(i)} title="切换 Free / Fixed">
                      <Badge variant={isFixed ? "neutral" : "default"}>
                        {isFixed ? "Fixed" : "Free"}
                      </Badge>
                    </button>
                  </td>
                  <td className="px-3 py-2 text-text-muted">{p.unit}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Validation status */}
      <div className="mt-3">
        {Object.keys(errors).length > 0 ? (
          <div className="flex items-start gap-2 rounded-[6px] border border-danger/40 bg-danger/5 px-3 py-2 text-[13px] text-danger">
            <CircleX className="mt-0.5 h-4 w-4 shrink-0" />
            <span>
              {Object.values(errors)[0]} (参数 {Object.keys(errors)[0]})
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-[6px] border border-success/40 bg-success/5 px-3 py-2 text-[13px] text-success">
            <CircleCheck className="h-4 w-4" />
            <span>All parameter settings are valid</span>
          </div>
        )}
      </div>
    </div>
  );
}
