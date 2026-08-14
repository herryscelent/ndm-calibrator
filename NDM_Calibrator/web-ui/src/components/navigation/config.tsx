import type { LucideIcon } from "lucide-react";
import {
  Activity,
  Database,
  Download,
  FunctionSquare,
  Info,
  LayoutDashboard,
  LineChart,
  Play,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";

export type PageKey =
  | "dashboard"
  | "data"
  | "model"
  | "parameters"
  | "identification"
  | "calibration"
  | "diagnostics"
  | "uncertainty"
  | "export"
  | "settings"
  | "about";

export interface NavItem {
  key: PageKey;
  label: string;
  icon: LucideIcon;
  section: "workflow" | "app";
}

export const navItems: NavItem[] = [
  { key: "dashboard", label: "项目首页", icon: LayoutDashboard, section: "workflow" },
  { key: "data", label: "数据管理", icon: Database, section: "workflow" },
  { key: "model", label: "模型定义", icon: FunctionSquare, section: "workflow" },
  { key: "parameters", label: "参数配置", icon: SlidersHorizontal, section: "workflow" },
  { key: "identification", label: "参数辨识", icon: Play, section: "workflow" },
  { key: "calibration", label: "模型校准", icon: LineChart, section: "workflow" },
  { key: "diagnostics", label: "诊断分析", icon: Activity, section: "workflow" },
  { key: "uncertainty", label: "可信度分析", icon: ShieldCheck, section: "workflow" },
  { key: "export", label: "结果导出", icon: Download, section: "workflow" },
  { key: "settings", label: "设置", icon: Settings, section: "app" },
  { key: "about", label: "关于", icon: Info, section: "app" },
];
