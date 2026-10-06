import { BadgeCheck } from "lucide-react";

import { Badge } from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { PageHeader } from "@/components/common/page-header";
import { model } from "@/data/mock/model";

export function ModelPage({ onToast }: { onToast: (msg: string) => void }) {
  return (
    <div>
      <PageHeader
        title="模型定义"
        description="定义状态方程、输入、参数以及观测输出。"
        actions={
          <Button
            onClick={() => onToast("模型验证通过")}
            title="验证模型"
          >
            验证模型
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        {/* Model structure */}
        <div className="rounded-lg border border-border bg-surface p-5">
          <h3 className="mb-4 text-[15px] font-semibold text-text-primary">模型结构</h3>

          <div className="space-y-4">
            <div>
              <div className="mb-1.5 text-xs font-medium uppercase tracking-wide text-text-muted">
                状态变量
              </div>
              {model.states.map((s) => (
                <div key={s.name} className="flex items-center justify-between rounded-[6px] px-2 py-1.5 text-[13px] hover:bg-surface-hover">
                  <span className="font-mono text-text-primary">{s.name}</span>
                  <span className="text-text-muted">{s.description}</span>
                </div>
              ))}
            </div>

            <div>
              <div className="mb-1.5 text-xs font-medium uppercase tracking-wide text-text-muted">
                输入
              </div>
              {model.inputs.map((s) => (
                <div key={s.name} className="flex items-center justify-between rounded-[6px] px-2 py-1.5 text-[13px] hover:bg-surface-hover">
                  <span className="font-mono text-text-primary">{s.name}</span>
                  <span className="text-text-muted">{s.description}</span>
                </div>
              ))}
            </div>

            <div>
              <div className="mb-1.5 text-xs font-medium uppercase tracking-wide text-text-muted">
                参数
              </div>
              {model.parameters.map((s) => (
                <div key={s.name} className="flex items-center justify-between rounded-[6px] px-2 py-1.5 text-[13px] hover:bg-surface-hover">
                  <span className="font-mono text-text-primary">{s.name}</span>
                  <span className="text-text-muted">{s.description}</span>
                </div>
              ))}
            </div>

            <div>
              <div className="mb-1.5 text-xs font-medium uppercase tracking-wide text-text-muted">
                输出
              </div>
              <div className="rounded-[6px] px-2 py-1.5 font-mono text-[13px] text-text-primary">
                {model.outputs[0]}
              </div>
            </div>
          </div>
        </div>

        {/* Equation editor */}
        <div className="rounded-lg border border-border bg-surface p-5">
          <h3 className="mb-4 text-[15px] font-semibold text-text-primary">方程编辑</h3>
          <div className="overflow-hidden rounded-lg border border-border">
            <div className="flex items-center gap-1.5 border-b border-border bg-surface-secondary px-3 py-2">
              <span className="h-2.5 w-2.5 rounded-full bg-text-disabled" />
              <span className="h-2.5 w-2.5 rounded-full bg-text-disabled" />
              <span className="h-2.5 w-2.5 rounded-full bg-text-disabled" />
            </div>
            <pre className="max-w-full overflow-x-auto bg-surface p-4 font-mono text-[13px] leading-7 text-text-primary">
              {model.equations.map((eq) => (
                <div key={eq.label} className="flex">
                  <span className="mr-4 select-none text-text-disabled">{eq.label}</span>
                  <span className="text-text-primary">= {eq.expr}</span>
                </div>
              ))}
              <div className="mt-1 flex">
                <span className="mr-4 select-none text-text-disabled">y</span>
                <span className="text-text-primary">= {model.outputs[0].slice(4)}</span>
              </div>
            </pre>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <Badge variant="success">
              <BadgeCheck className="h-3.5 w-3.5" />
              {model.validMessage}
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}
