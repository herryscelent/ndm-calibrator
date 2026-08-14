import { useState } from "react";
import { Download } from "lucide-react";

import { Button } from "@/components/common/button";
import { Checkbox } from "@/components/common/checkbox";
import { Input } from "@/components/common/input";
import { PageHeader } from "@/components/common/page-header";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/common/select";

const contentOptions = [
  "Project Summary",
  "Parameters",
  "Metrics",
  "Simulation",
  "Residuals",
  "Diagnostics",
  "Bootstrap",
];

const formats = ["Excel", "CSV", "HTML Report", "PNG Figures"];

export function ExportPage({ onToast }: { onToast: (msg: string) => void }) {
  const [checked, setChecked] = useState<Record<string, boolean>>(
    Object.fromEntries(contentOptions.map((c) => [c, true]))
  );
  const [format, setFormat] = useState("Excel");
  const [dest, setDest] = useState("C:\\projects\\ndm-calibrator\\export");
  const [result, setResult] = useState<string | null>(null);

  function run() {
    setResult(`Export completed · ${checked.Simulation ? "6" : "5"} files generated`);
    onToast("Export completed");
  }

  return (
    <div>
      <PageHeader
        title="结果导出"
        description="选择需要包含的分析内容和导出格式。"
      />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        {/* Content checkboxes */}
        <div className="rounded-lg border border-border bg-surface p-5">
          <h3 className="mb-4 text-[15px] font-semibold text-text-primary">导出内容</h3>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {contentOptions.map((c) => (
              <label
                key={c}
                className="flex cursor-pointer items-center gap-2.5 rounded-[6px] px-2 py-1.5 text-[13px] text-text-primary transition-colors hover:bg-surface-hover"
              >
                <Checkbox
                  checked={checked[c]}
                  onCheckedChange={(v) => setChecked({ ...checked, [c]: Boolean(v) })}
                />
                {c}
              </label>
            ))}
          </div>
        </div>

        {/* Format + destination */}
        <div className="space-y-5">
          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-4 text-[15px] font-semibold text-text-primary">格式</h3>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger className="w-full sm:w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {formats.map((f) => (
                  <SelectItem key={f} value={f}>{f}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="rounded-lg border border-border bg-surface p-5">
            <h3 className="mb-4 text-[15px] font-semibold text-text-primary">导出位置</h3>
            <div className="flex gap-2">
              <Input value={dest} onChange={(e) => setDest(e.target.value)} className="font-mono text-[13px]" />
              <Button variant="secondary" onClick={() => onToast("Select destination (mock)")}>
                浏览…
              </Button>
            </div>
          </div>

          <Button className="w-full" onClick={run}>
            <Download className="h-4 w-4" /> 导出结果
          </Button>

          {result ? (
            <div className="rounded-[6px] border border-success/40 bg-success/5 px-3 py-2 text-[13px] text-success">
              {result}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
