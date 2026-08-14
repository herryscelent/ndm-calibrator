import { HelpCircle, Moon, Save, Settings } from "lucide-react";

import { Badge } from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { project } from "@/data/mock/project";

interface TopbarProps {
  projectName: string;
  onSave: () => void;
}

export function Topbar({ projectName, onSave }: TopbarProps) {
  return (
    <header className="flex h-12 shrink-0 items-center gap-4 border-b border-border bg-topbar px-4">
      <div className="flex items-center gap-2.5">
        <span className="text-[14px] font-semibold text-text-primary">NDM Calibrator</span>
      </div>
      <span className="h-4 w-px bg-border" />
      <div className="flex items-center gap-2 text-[13px] text-text-secondary">
        <span className="max-w-[280px] truncate" title={projectName}>
          {projectName}
        </span>
        <Badge variant="success">Saved</Badge>
      </div>

      <div className="ml-auto flex items-center gap-1">
        <Button variant="ghost" size="icon" onClick={onSave} title="保存项目">
          <Save className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="主题 (浅色)">
          <Moon className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="设置">
          <Settings className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="帮助">
          <HelpCircle className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}

export const topbarProjectName = project.name;
