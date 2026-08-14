import { PageHeader } from "@/components/common/page-header";
import { project } from "@/data/mock/project";

const stack = [
  "React",
  "TypeScript",
  "Vite",
  "shadcn/ui",
  "Tailwind CSS",
  "Recharts",
  "TanStack Table",
];

export function AboutPage() {
  return (
    <div>
      <PageHeader title="关于" description="软件信息与技术栈。" />
      <div className="max-w-xl rounded-lg border border-border bg-surface p-6">
        <h2 className="text-lg font-semibold text-text-primary">NDM Calibrator</h2>
        <p className="mt-1 text-[14px] text-text-secondary">
          非线性动态模型参数辨识与校准软件
        </p>
        <div className="mt-2 flex items-center gap-2 text-[13px] text-text-muted">
          <span>Prototype UI</span>
          <span>·</span>
          <span>Version 1.0</span>
        </div>

        <div className="mt-5 border-t border-border pt-4">
          <div className="mb-2 text-xs font-medium uppercase tracking-wide text-text-muted">
            技术栈
          </div>
          <div className="flex flex-wrap gap-2">
            {stack.map((s) => (
              <span
                key={s}
                className="rounded-[6px] border border-border bg-surface-secondary px-2.5 py-1 text-xs text-text-secondary"
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        <p className="mt-5 text-xs text-text-muted">
          Current mock project: {project.name} — synthetic demonstration data.
        </p>
      </div>
    </div>
  );
}
