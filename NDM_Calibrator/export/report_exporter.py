"""HTML analysis report export (publication-friendly, white background)."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from app.constants import APP_NAME_CN, APP_NAME_EN, APP_VERSION
from core.exceptions import NDMCError
from core.project import Project

# CJK-capable font for Chinese axis labels in report figures.
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False


def _embed_figure(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def export_html_report(project: Project, dest_dir: Path | str, checks: Dict[str, bool] | None = None) -> str:
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        raise NDMCError(f"目标目录不存在: {dest_dir}")

    def enabled(key: str) -> bool:
        return checks is None or checks.get(key, True)

    cal = project.results.get("calibration", {})
    ident = project.results.get("identification", {})
    boot = project.results.get("bootstrap", {})

    sections = []
    sections.append(f"<h1>{project.name}</h1><p>{project.description}</p>")
    if enabled("summary"):
        sections.append(_info_table([
            ("软件", f"{APP_NAME_CN} {APP_VERSION} ({APP_NAME_EN})"),
            ("生成时间", project.modified_at),
            ("数据来源", project.data_source or "—"),
            ("模型状态", ", ".join(project.model.states) if project.model else "—"),
            ("随机种子", str(ident.get("result", {}).get("seed"))),
        ]))

    # Data summary
    if project.experiment is not None and enabled("summary"):
        exp = project.experiment
        sections.append("<h2>数据摘要</h2>")
        sections.append(_info_table([
            ("样本数", str(exp.n_points)),
            ("输入变量", ", ".join(exp.inputs) or "—"),
            ("输出变量", ", ".join(exp.outputs) or "—"),
            ("时间范围", f"[{exp.time[0]:.4g}, {exp.time[-1]:.4g}]"),
        ]))

    # Model definition
    if project.model is not None and enabled("summary"):
        sections.append("<h2>模型定义</h2><pre>" + _model_text(project) + "</pre>")

    # Parameters
    if enabled("parameters"):
        sections.append("<h2>参数配置</h2>")
        param_rows = [[p.name, p.initial, p.lower, p.upper, "待辨识" if p.free else "固定"] for p in project.parameters]
        sections.append(_html_table(["参数", "初值", "下限", "上限", "状态"], param_rows))

    # Identification
    result = ident.get("result", {})
    if result and enabled("parameters"):
        sections.append("<h2>辨识算法与结果</h2>")
        rows = [
            ["算法", result.get("algorithm", "")],
            ["目标值", f"{result.get('objective_value')}"],
            ["用时 (s)", f"{result.get('runtime_seconds'):.2f}"],
            ["评估次数", str(result.get("n_evaluations"))],
            ["成功", str(result.get("success"))],
            ["种子", str(result.get("seed"))],
        ]
        sections.append(_info_table(rows))
        est_rows = [[k, f"{v:.6g}"] for k, v in result.get("parameters", {}).items()]
        sections.append("<h3>参数估计</h3>" + _html_table(["参数", "估计值"], est_rows))

    # Metrics
    metrics = cal.get("metrics", {}).get("summary", {})
    if metrics and enabled("metrics"):
        sections.append("<h2>拟合指标</h2>")
        sections.append(_info_table([[k, f"{v:.6g}"] for k, v in metrics.items()]))

    # Fit figure
    fit_img = _make_fit_figure(project) if enabled("simulation") else None
    if fit_img:
        sections.append("<h2>拟合曲线</h2>")
        sections.append(f'<img src="{fit_img}" style="max-width:100%"/>')

    # Residuals
    resid_img = _make_residual_figure(project) if enabled("residuals") else None
    if resid_img:
        sections.append("<h2>残差分析</h2>")
        sections.append(f'<img src="{resid_img}" style="max-width:100%"/>')

    # Identifiability
    if enabled("diagnostics") and (ident_vals := cal.get("identifiability")):
        sections.append("<h2>参数可辨识性</h2>")
        id_rows = [
            ("条件数", f"{ident_vals.get('condition_number', '—')}"),
            ("秩", str(ident_vals.get("rank", "—"))),
        ]
        for w in ident_vals.get("warnings", []):
            id_rows.append(("警告", w))
        sections.append(_info_table(id_rows))

    # Bootstrap
    if boot.get("parameters") and enabled("bootstrap"):
        sections.append("<h2>Bootstrap (percentile interval)</h2>")
        rows = []
        for name, info in boot["parameters"].items():
            rows.append([name, f"{info['mean']:.6g}", f"{info['median']:.6g}", f"{info['p2_5']:.6g}", f"{info['p97_5']:.6g}"])
        sections.append(_html_table(["参数", "均值", "中位数", "2.5%", "97.5%"], rows))

    html = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
        f"<title>{project.name} 分析报告</title>"
        "<style>body{font-family:'Segoe UI',sans-serif;margin:32px;color:#1F2328;background:#fff}"
        "h1{font-size:22px}h2{font-size:17px;border-bottom:1px solid #E2E5EA;padding-bottom:4px;margin-top:28px}"
        "h3{font-size:14px}table{border-collapse:collapse;margin:8px 0}th,td{border:1px solid #E2E5EA;padding:4px 10px;font-size:12px}"
        "th{background:#F0F1F3}pre{background:#F6F8FA;padding:12px;border-radius:6px;font-family:Consolas;font-size:12px}"
        "</style></head><body>"
        + "\n".join(sections)
        + "</body></html>"
    )
    out_path = dest_dir / f"{project.name}_report.html"
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)


def _make_fit_figure(project):
    if project.model is None or project.experiment is None:
        return None
    entry = project.results.get("identification", {})
    params = entry.get("result", {}).get("parameters")
    if not params:
        return None
    try:
        from identification.base import build_context

        ctx = build_context(project)
        theta = np.array([params[n] for n in ctx.free_names], dtype=float)
        predicted = ctx.predict_outputs(theta)
        first = project.model.outputs[0]
        fig, ax = plt.subplots(figsize=(8, 3.5))
        t = project.experiment.time
        ax.plot(t, ctx.measured_outputs()[first], "o", ms=3, label="Measured")
        ax.plot(t, predicted[first], "-", lw=1.5, label="Simulated")
        ax.set_xlabel("时间")
        ax.set_ylabel(first)
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return _embed_figure(fig)
    except Exception:
        return None


def _make_residual_figure(project):
    cal = project.results.get("calibration", {})
    if project.model is None or project.experiment is None:
        return None
    first = project.model.outputs[0]
    res = cal.get("residuals", {}).get(first)
    if res is None:
        return None
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(project.experiment.time, res, lw=1)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("时间")
    ax.set_ylabel("残差")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _embed_figure(fig)


def _model_text(project) -> str:
    m = project.model
    lines = [f"状态: {', '.join(m.states)}", f"输入: {', '.join(m.inputs) or '—'}",
             f"参数: {', '.join(m.parameters)}"]
    for st, expr in zip(m.states, m.rhs_exprs):
        lines.append(f"dx{st}/dt = {expr}")
    for out, expr in zip(m.outputs, m.output_exprs):
        lines.append(f"y_{out} = {expr}")
    return "\n".join(lines)


def _info_table(rows) -> str:
    return _html_table(["项", "值"], rows)


def _html_table(headers, rows) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
