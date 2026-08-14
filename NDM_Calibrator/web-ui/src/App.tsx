import { useCallback, useEffect, useRef, useState } from "react";
import { CheckCircle2 } from "lucide-react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import type { PageKey } from "@/components/navigation/config";
import { topbarProjectName } from "@/components/layout/topbar";
import { DashboardPage } from "@/pages/dashboard-page";
import { DataPage } from "@/pages/data-page";
import { ModelPage } from "@/pages/model-page";
import { ParametersPage } from "@/pages/parameters-page";
import { IdentificationPage } from "@/pages/identification-page";
import { CalibrationPage } from "@/pages/calibration-page";
import { DiagnosticsPage } from "@/pages/diagnostics-page";
import { UncertaintyPage } from "@/pages/uncertainty-page";
import { ExportPage } from "@/pages/export-page";
import { SettingsPage } from "@/pages/settings-page";
import { AboutPage } from "@/pages/about-page";

function Toast({ message }: { message: string }) {
  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-[8px] bg-text-primary px-4 py-2.5 text-[13px] text-background shadow-lg">
      <CheckCircle2 className="h-4 w-4 text-success" />
      {message}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<PageKey>(
    () => (window.location.hash.replace("#", "") as PageKey) || "dashboard"
  );
  const [collapsed, setCollapsed] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2600);
  }, []);

  useEffect(() => {
    const onHash = () => {
      const h = window.location.hash.replace("#", "") as PageKey;
      if (h && h !== page) setPage(h);
    };
    window.addEventListener("hashchange", onHash);
    return () => {
      window.removeEventListener("hashchange", onHash);
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, [page]);

  const navigate = useCallback((k: PageKey) => {
    window.location.hash = k;
    setPage(k);
  }, []);

  return (
    <div className="flex h-full flex-col">
      <Topbar projectName={topbarProjectName} onSave={() => showToast("Project saved")} />
      <div className="flex min-h-0 flex-1">
        <Sidebar
          current={page}
          collapsed={collapsed}
          onNavigate={navigate}
          onToggleCollapse={() => setCollapsed((c) => !c)}
        />
        <main className="min-w-0 flex-1 overflow-y-auto" style={{ padding: "28px" }}>
          {page === "dashboard" && <DashboardPage onNavigate={navigate} />}
          {page === "data" && <DataPage />}
          {page === "model" && <ModelPage onToast={showToast} />}
          {page === "parameters" && <ParametersPage onToast={showToast} />}
          {page === "identification" && <IdentificationPage onToast={showToast} />}
          {page === "calibration" && <CalibrationPage />}
          {page === "diagnostics" && <DiagnosticsPage />}
          {page === "uncertainty" && <UncertaintyPage onToast={showToast} />}
          {page === "export" && <ExportPage onToast={showToast} />}
          {page === "settings" && <SettingsPage />}
          {page === "about" && <AboutPage />}
        </main>
      </div>
      {toast ? <Toast message={toast} /> : null}
    </div>
  );
}
