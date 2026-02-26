# final operator-tailored holistic stability report (pdf)

from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.lib import colors

from config import (
    RESULTS_DIR,
    SIM_DIR,
    RISK_DIR,
    EVENTS_DIR,
    XAI_DIR,
    COMPARE_DIR,
    DT_MIN,
    H_STEPS,
    PV_KWP,
    E_KWH,
    P_MAX_KW,
    SOC_MIN,
    SOC_MAX,
    SOC0,
    ETA_CH,
    ETA_DIS,
    ALPHA,
    BETA,
    GAMMA,
)

# input files created
METRICS_TXT = SIM_DIR / "metrics_summary.txt"
PRED_REACT_TXT = COMPARE_DIR / "predictive_vs_reactive_summary.txt"
TOP_DRIVERS_TXT = XAI_DIR / "top_drivers.txt"

# key figures created
QUICKLOOK_DIR = SIM_DIR / "quicklooks"
FIGS = [
    QUICKLOOK_DIR / "load_pv_net_full.png",
    QUICKLOOK_DIR / "soc_full.png",
    QUICKLOOK_DIR / "unserved_full.png",
    QUICKLOOK_DIR / "risk_index_full.png",
    RISK_DIR / "risk_index_exceedance.png",
    RISK_DIR / "unserved_exceedance.png",
    XAI_DIR / "fig5_shap_importance_horizontal.png",
]

# report output
REPORT_DIR = RESULTS_DIR / "report"
OUT_PDF = REPORT_DIR / "microgrid_stability_report.pdf"

def _read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")

def _parse_metrics_kv(text: str):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("==="):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            out.append((k.strip(), v.strip()))
    return out

def _kv_to_num_map(kv_rows):
    m = {}
    for k, v in kv_rows:
        v2 = v.strip()
        num = None
        try:
            tok = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", v2)
            if tok:
                num = float(tok[0])
        except Exception:
            num = None
        m[k] = num if num is not None else v2
    return m

def _read_top_drivers():
    text = _read_text_safe(TOP_DRIVERS_TXT).strip()
    if not text:
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[:5]

def _safe_add_image(story, img_path: Path, max_w_cm: float = 17.5):
    if not img_path.exists():
        story.append(Paragraph(f"- missing figure: {img_path.name}", _styles()["note"]))
        story.append(Spacer(1, 6))
        return

    max_w = max_w_cm * cm
    img = Image(str(img_path))
    iw, ih = img.imageWidth, img.imageHeight
    if iw > 0:
        scale = max_w / float(iw)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale

    story.append(KeepTogether([img, Spacer(1, 10)]))

def _styles():
    base = getSampleStyleSheet()
    if "sc_h1" not in base:
        base.add(ParagraphStyle(
            name="sc_h1",
            parent=base["Heading1"],
            spaceAfter=10,
            keepWithNext=1,
        ))
    if "sc_h2" not in base:
        base.add(ParagraphStyle(
            name="sc_h2",
            parent=base["Heading2"],
            spaceAfter=6,
            keepWithNext=1,
        ))
    if "sc_h3" not in base:
        base.add(ParagraphStyle(
            name="sc_h3",
            parent=base["Heading3"],
            spaceAfter=4,
            keepWithNext=1,
        ))
    if "mono" not in base:
        base.add(ParagraphStyle(
            name="mono",
            parent=base["BodyText"],
            fontName="Courier",
            fontSize=9,
            leading=11,
        ))
    if "note" not in base:
        base.add(ParagraphStyle(
            name="note",
            parent=base["BodyText"],
            textColor=colors.grey,
            fontSize=9,
            leading=11,
            keepWithNext=1,
        ))
    base["sc_h1"].keepWithNext = 1
    base["sc_h2"].keepWithNext = 1
    base["sc_h3"].keepWithNext = 1
    base["note"].keepWithNext = 1
    return base

def _make_table(rows, col_widths_cm=(7.5, 9.5)):
    tbl = Table(rows, colWidths=[w * cm for w in col_widths_cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tbl

def _collect_top_events_table_and_stats():
    top_csv = EVENTS_DIR / "top_events.csv"
    if not top_csv.exists():
        return None, None

    import pandas as pd

    df = pd.read_csv(top_csv)
    if df.empty:
        return None, None

    cols = [c for c in ["timestamp", "unserved_kw", "risk_index", "soc_pre"] if c in df.columns]
    df2 = df[cols].head(5).copy()

    rows = [["top events", "value"]]
    for _, r in df2.iterrows():
        ts = str(r.get("timestamp", ""))
        un = r.get("unserved_kw", "")
        rk = r.get("risk_index", "")
        sc = r.get("soc_pre", "")
        rows.append([ts, f"unserved={un}  risk={rk}  soc_pre={sc}"])

    # stats for operator notes
    soc_vals = []
    if "soc_pre" in df2.columns:
        try:
            soc_vals = [float(x) for x in df2["soc_pre"].dropna().tolist()]
        except Exception:
            soc_vals = []

    stats = {
        "min_soc_pre": min(soc_vals) if soc_vals else None,
        "mean_soc_pre": (sum(soc_vals) / len(soc_vals)) if soc_vals else None,
    }

    return _make_table(rows, col_widths_cm=(6.2, 10.8)), stats


def _build_operator_notes(metrics_map, top_event_stats, top_drivers):
    notes = []

    # key numbers
    total_unserved_kwh = metrics_map.get("Total unserved energy (kWh)")
    pct_unserved_steps = metrics_map.get("Timesteps with unserved load (%)")
    pct_risk_steps = metrics_map.get("Timesteps flagged as risk events (%)")
    max_risk_index = metrics_map.get("Max risk index")
    max_unserved_kw = metrics_map.get("Max unserved power (kW)")

    # metrics
    if isinstance(total_unserved_kwh, float) and total_unserved_kwh > 0.0:
        notes.append("Unserved load happened: the system could not meet demand at some times")
        if isinstance(max_unserved_kw, float) and max_unserved_kw > 0:
            notes.append("Quick fix options: increase bess energy/power, reduce load peaks, or add generation headroom")

    if isinstance(pct_risk_steps, float) and pct_risk_steps >= 20.0:
        notes.append("Risk flags are frequent: the system is often close to its limits")

    # risk frequent but unserved rare => reserve stress more than outages
    if isinstance(pct_risk_steps, float) and isinstance(pct_unserved_steps, float):
        if pct_risk_steps >= 20.0 and pct_unserved_steps <= 2.0:
            notes.append("Reserve stress is common but outages are rare: consider a higher soc target or more bess headroom to reduce stress")

    # events + soc_pre
    if top_event_stats and top_event_stats.get("min_soc_pre") is not None:
        min_soc_pre = float(top_event_stats["min_soc_pre"])
        if min_soc_pre <= (SOC_MIN + 0.05):
            notes.append("Top stress events happen at low soc: consider higher soc0, a tighter soc_min, or larger bess energy")

    # top drivers
    if top_drivers:
        drivers_str = ", ".join(top_drivers)
        notes.append(f"Main drivers: {drivers_str}.")

        d0 = top_drivers[0].lower()
        if "Reserve energy deficit" in d0:
            notes.append("Reserve energy deficit is a key driver: bess energy may be too small, or soc_min is too high")
        if "reserve power deficit" in d0:
            notes.append("Reserve power deficit is a key driver: bess p_max may be too small for peak deficit moments")
        if "bess soc" in d0 or "soc" in d0:
            notes.append("Soc is a key driver: consider a higher soc target (soc0 / soc_min / soc_max) to keep more usable energy")

    # final action
    notes.append("To test changes: edit config.py, then run the pipeline again")

    return notes[:8]


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("creating pdf report")
    print(f"output: {OUT_PDF}")

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Microgrid stability report",
        author="Case study pipeline",
    )

    st = _styles()
    story = []

    # title
    story.append(Paragraph("Microgrid stability report", st["sc_h1"]))
    story.append(Paragraph("Operator summary", st["note"]))
    story.append(Spacer(1, 10))

    # config settings
    story.append(Paragraph("Run settings", st["sc_h2"]))
    settings_rows = [
        ["Parameter", "value"],
        ["Time step (min)", str(DT_MIN)],
        ["Forecast horizon (steps)", str(H_STEPS)],
        ["Forecast horizon (hours)", f"{(H_STEPS * DT_MIN) / 60.0:.2f}"],
        ["PV installed capacity (kWp)", str(PV_KWP)],
        ["BESS energy capacity (kWh)", str(E_KWH)],
        ["BESS power limit (kW)", str(P_MAX_KW)],
        ["SoC window", f"[{SOC_MIN}, {SOC_MAX}]"],
        ["Initial SoC", str(SOC0)],
        ["Charge efficiency", str(ETA_CH)],
        ["Discharge efficiency", str(ETA_DIS)],
        ["Risk weights (alpha, beta, gamma)", f"{ALPHA}, {BETA}, {GAMMA}"],
    ]
    story.append(_make_table(settings_rows))
    story.append(Spacer(1, 12))

    # key metrics summary
    story.append(Paragraph("Key metrics", st["sc_h2"]))
    metrics_text = _read_text_safe(METRICS_TXT)
    metrics_kv = []
    metrics_map = {}
    if metrics_text.strip():
        metrics_kv = _parse_metrics_kv(metrics_text)
        metrics_map = _kv_to_num_map(metrics_kv)
        rows = [["metric", "value"]] + metrics_kv[:30]
        story.append(_make_table(rows))
    else:
        story.append(Paragraph("- metrics file not found yet (run simulate_microgrid first)", st["note"]))
    story.append(Spacer(1, 12))

    # figures
    story.append(PageBreak())
    story.append(Paragraph("Main figures", st["sc_h2"]))
    story.append(Paragraph("These plots show what happened across the run", st["note"]))
    story.append(Spacer(1, 10))

    for p in FIGS:
        _safe_add_image(story, p)

    story.append(Spacer(1, 6))

    # events
    story.append(Paragraph("Top stress events", st["sc_h2"]))
    story.append(Paragraph("These are the biggest unserved-load events", st["note"]))
    story.append(Spacer(1, 8))

    top_tbl, top_stats = _collect_top_events_table_and_stats()
    if top_tbl is not None:
        story.append(top_tbl)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Event folders (plots):", st["BodyText"]))
        story.append(Spacer(1, 4))

        if EVENTS_DIR.exists():
            ev_folders = sorted([p for p in EVENTS_DIR.iterdir() if p.is_dir() and p.name.startswith("event_")])[:10]
            if ev_folders:
                for d in ev_folders:
                    story.append(Paragraph(f"- {d.name}", st["mono"]))
            else:
                story.append(Paragraph("- no event folders found yet", st["note"]))
        else:
            story.append(Paragraph("- events folder not found yet", st["note"]))
    else:
        story.append(Paragraph("- top_events.csv not found yet (run event_examples)", st["note"]))

    story.append(Spacer(1, 12))

    # predictive vs reactive
    story.append(Paragraph("Early-warning vs reactive comparison", st["sc_h2"]))
    pr_text = _read_text_safe(PRED_REACT_TXT)
    if pr_text.strip():
        lines = []
        for ln in pr_text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if len(ln) > 200:
                ln = ln[:200] + "..."
            lines.append(ln)
        story.append(Paragraph("<br/>".join(lines[:25]), st["mono"]))
    else:
        story.append(Paragraph("- predictive vs reactive summary not found (run predictive_vs_reactive)", st["note"]))
    story.append(Spacer(1, 12))

    # operator notes
    story.append(Paragraph("Operator notes", st["sc_h2"]))

    top_drivers = _read_top_drivers()
    notes = _build_operator_notes(metrics_map, top_stats, top_drivers)

    for n in notes:
        story.append(Paragraph(f"- {n}", st["BodyText"]))

    story.append(Spacer(1, 10))

    doc.build(story)

    print("report created!")
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()