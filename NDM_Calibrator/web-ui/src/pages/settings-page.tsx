import { useState } from "react";

import { Badge } from "@/components/common/badge";
import { PageHeader } from "@/components/common/page-header";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/common/select";

export function SettingsPage() {
  const [sidebar, setSidebar] = useState("expanded");
  const [grid, setGrid] = useState("on");
  const [precision, setPrecision] = useState("4");

  return (
    <div>
      <PageHeader title="设置" description="外观、界面与应用偏好。" />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        {/* Appearance */}
        <div className="rounded-lg border border-border bg-surface p-5">
          <h3 className="mb-4 text-[15px] font-semibold text-text-primary">外观</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-secondary">主题</span>
              <Badge variant="success">浅色</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-muted">深色</span>
              <Badge variant="neutral">后续支持</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-muted">跟随系统</span>
              <Badge variant="neutral">后续支持</Badge>
            </div>
          </div>
        </div>

        {/* UI */}
        <div className="rounded-lg border border-border bg-surface p-5">
          <h3 className="mb-4 text-[15px] font-semibold text-text-primary">界面</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-secondary">侧边栏</span>
              <Select value={sidebar} onValueChange={setSidebar}>
                <SelectTrigger className="h-8 w-32 text-[13px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="expanded">展开</SelectItem>
                  <SelectItem value="collapsed">折叠</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-secondary">图表网格</span>
              <Select value={grid} onValueChange={setGrid}>
                <SelectTrigger className="h-8 w-32 text-[13px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="on">开启</SelectItem>
                  <SelectItem value="off">关闭</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[13px] text-text-secondary">小数位数</span>
              <Select value={precision} onValueChange={setPrecision}>
                <SelectTrigger className="h-8 w-32 text-[13px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["2", "3", "4", "6"].map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
