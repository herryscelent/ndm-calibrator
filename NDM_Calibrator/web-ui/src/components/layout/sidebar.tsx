import { ChevronsLeft, ChevronsRight, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { navItems } from "@/components/navigation/config";
import type { PageKey } from "@/components/navigation/config";

interface SidebarProps {
  current: PageKey;
  collapsed: boolean;
  onNavigate: (key: PageKey) => void;
  onToggleCollapse: () => void;
}

function NavButton({
  icon: Icon,
  label,
  active,
  collapsed,
  onClick,
}: {
  icon: LucideIcon;
  label: string;
  active: boolean;
  collapsed: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      title={collapsed ? label : undefined}
      className={cn(
        "group relative flex w-full items-center gap-3 rounded-[6px] px-3 py-2 text-[13px] transition-colors duration-150",
        collapsed && "justify-center px-0",
        active
          ? "bg-surface-selected text-text-primary font-medium"
          : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
      )}
    >
      {active ? (
        <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r bg-accent" />
      ) : null}
      <Icon
        className={cn(
          "h-[18px] w-[18px] shrink-0 transition-colors",
          active ? "text-accent" : "text-text-muted group-hover:text-text-secondary"
        )}
      />
      {!collapsed ? <span className="truncate">{label}</span> : null}
    </button>
  );
}

export function Sidebar({
  current,
  collapsed,
  onNavigate,
  onToggleCollapse,
}: SidebarProps) {
  const workflow = navItems.filter((n) => n.section === "workflow");
  const app = navItems.filter((n) => n.section === "app");

  return (
    <aside
      className="flex h-full flex-col border-r border-border bg-sidebar"
      style={{ width: collapsed ? 68 : 220, transition: "width 160ms ease" }}
    >
      <div className="flex flex-1 flex-col overflow-y-auto px-2 py-3">
        {!collapsed ? (
          <div className="px-3 pb-2 text-[11px] font-medium uppercase tracking-wide text-text-muted">
            工作流
          </div>
        ) : (
          <div className="pb-2" />
        )}
        <nav className="flex flex-col gap-0.5">
          {workflow.map((item) => (
            <NavButton
              key={item.key}
              icon={item.icon}
              label={item.label}
              active={current === item.key}
              collapsed={collapsed}
              onClick={() => onNavigate(item.key)}
            />
          ))}
        </nav>

        {!collapsed ? (
          <div className="px-3 pb-2 pt-4 text-[11px] font-medium uppercase tracking-wide text-text-muted">
            应用
          </div>
        ) : (
          <div className="pt-4" />
        )}
        <nav className="flex flex-col gap-0.5">
          {app.map((item) => (
            <NavButton
              key={item.key}
              icon={item.icon}
              label={item.label}
              active={current === item.key}
              collapsed={collapsed}
              onClick={() => onNavigate(item.key)}
            />
          ))}
        </nav>
      </div>

      <div className="border-t border-border p-2">
        <button
          onClick={onToggleCollapse}
          title={collapsed ? "展开侧边栏" : "折叠侧边栏"}
          className={cn(
            "flex w-full items-center gap-3 rounded-[6px] px-3 py-2 text-[13px] text-text-secondary transition-colors hover:bg-surface-hover",
            collapsed && "justify-center px-0"
          )}
        >
          {collapsed ? (
            <ChevronsRight className="h-[18px] w-[18px]" />
          ) : (
            <>
              <ChevronsLeft className="h-[18px] w-[18px]" />
              <span>折叠</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
