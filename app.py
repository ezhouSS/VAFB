"""
VFB System Pain Heat Map — Streamlit App
=========================================
X axis: Systems (with functional descriptions)
Y axis: Teams / Personas

Run locally:   streamlit run app.py
"""

import streamlit as st
import pandas as pd
import re
import os
from data import (
    STAGES, PERSONAS, HEAT_COLORS,
    APP_TITLE, APP_SUBTITLE, APP_CLIENT, OBSERVATIONS
)

DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__) or "."), "data.py")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_CLIENT} · System Pain Heat Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #FAFAF7; }
    .vfb-header {
        background: #1A5C38;
        border-bottom: 4px solid #C8A84B;
        padding: 18px 28px 14px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    .vfb-header h1 { color: white; margin: 0 0 4px; font-size: 22px; }
    .vfb-header p  { color: rgba(255,255,255,0.65); margin: 0; font-size: 12px; }
    .vfb-tag {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 11px;
        color: rgba(255,255,255,0.85);
        margin-right: 6px;
        margin-top: 6px;
    }
    .detail-pain       { background: #FFF1F2; border: 1.5px solid #FECACA; border-radius: 9px; padding: 14px; }
    .detail-workaround { background: #FFFBEB; border: 1.5px solid #FCD34D; border-radius: 9px; padding: 14px; }
    .detail-datagap    { background: #F0FDFA; border: 1.5px solid #5EEAD4; border-radius: 9px; padding: 14px; }
    .detail-label      { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .edit-panel {
        background: white;
        border: 2px solid #C8A84B;
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 12px;
    }
    .obs-box {
        background: #F0FDFA;
        border: 1.5px solid rgba(13,148,136,0.3);
        border-radius: 10px;
        padding: 14px 18px;
    }
    .block-container { padding-top: 1rem; }
    /* Tighter column headers for system labels */
    .sys-header {
        font-size: 10px;
        font-weight: 700;
        color: #1A5C38;
        text-align: center;
        padding: 4px 2px;
        line-height: 1.3;
    }
    .sys-desc {
        font-size: 8px;
        color: #9CA3AF;
        font-weight: 400;
    }
    .cell-0 + div button { background:#F8FAF8 !important; border:1.5px solid #D1D5DB !important; color:#9CA3AF !important; font-style:italic !important; }
    .cell-1 + div button { background:#FEF9C3 !important; border:1.5px solid #FCD34D80 !important; color:#854D0E !important; }
    .cell-2 + div button { background:#FED7AA !important; border:1.5px solid #FB923C80 !important; color:#9A3412 !important; }
    .cell-3 + div button { background:#FECACA !important; border:1.5px solid #F8717180 !important; color:#7F1D1D !important; }
    .cell-4 + div button { background:#FCA5A5 !important; border:1.5px solid #DC2626 !important; color:#450A0A !important; }
    .cell-sel + div button { box-shadow:0 0 0 3px rgba(0,0,0,0.18) !important; border-width:2.5px !important; }
    div[class^="cell-"] + div button, div[class*=" cell-"] + div button {
        border-radius:8px !important; font-size:13px !important; font-weight:700 !important;
        min-height:62px !important; padding:10px 6px !important; cursor:pointer !important; width:100% !important;
    }
    div[class^="cell-"] + div button:hover { filter:brightness(0.94) !important; }
</style>
""", unsafe_allow_html=True)


# ── Save to data.py ───────────────────────────────────────────────────────────

def save_cell(persona_id, stage_id, new_score, new_pain, new_workaround, new_datagap, new_status):
    """Surgically update a single persona/stage cell in data.py."""
    with open(DATA_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    in_target_persona = False
    in_scores = False
    in_notes = False
    in_target_note = False
    brace_depth = 0
    persona_entry_depth = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        brace_depth += line.count("{") - line.count("}")

        if not in_target_persona:
            if re.search(r'"id"\s*:\s*"' + re.escape(persona_id) + r'"', line):
                in_target_persona = True
                persona_entry_depth = brace_depth
            new_lines.append(line)
            i += 1
            continue

        if persona_entry_depth is not None and brace_depth < persona_entry_depth:
            in_target_persona = False
            in_scores = False
            in_notes = False
            in_target_note = False
            persona_entry_depth = None
            new_lines.append(line)
            i += 1
            continue

        if re.match(r'\s*"status"\s*:', line):
            indent = len(line) - len(line.lstrip())
            new_lines.append(" " * indent + '"status": "' + new_status + '",\n')
            i += 1
            continue

        if re.match(r'\s*"scores"\s*:', line):
            in_scores = True
            in_notes = False
            new_lines.append(line)
            i += 1
            continue

        if in_scores:
            if re.match(r'\s*"' + re.escape(stage_id) + r'"\s*:', line):
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + '"' + stage_id + '":   ' + str(new_score) + ',\n')
                i += 1
                continue
            if stripped in ("},", "}"):
                in_scores = False

        if re.match(r'\s*"notes"\s*:', line):
            in_notes = True
            in_scores = False
            new_lines.append(line)
            i += 1
            continue

        if in_notes and not in_target_note:
            if re.match(r'\s*"' + re.escape(stage_id) + r'"\s*:', line):
                in_target_note = True
            new_lines.append(line)
            i += 1
            continue

        if in_target_note:
            if re.match(r'\s*"pain"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_pain.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                new_lines.append(" " * indent + '"pain":       "' + escaped + '",\n')
                i += 1
                continue
            if re.match(r'\s*"workaround"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_workaround.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                new_lines.append(" " * indent + '"workaround": "' + escaped + '",\n')
                i += 1
                continue
            if re.match(r'\s*"data_gap"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_datagap.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                new_lines.append(" " * indent + '"data_gap":   "' + escaped + '",\n')
                in_target_note = False
                i += 1
                continue

        new_lines.append(line)
        i += 1

    with open(DATA_FILE, "w") as f:
        f.writelines(new_lines)


def save_observations(new_obs_list):
    with open(DATA_FILE, "r") as f:
        src = f.read()
    lines = ["OBSERVATIONS = ["]
    for item in new_obs_list:
        escaped = item.replace("\\", "\\\\").replace('"', '\\"')
        lines.append('    "' + escaped + '",')
    lines.append("]")
    new_block = "\n".join(lines)
    src = re.sub(r"OBSERVATIONS\s*=\s*\[.*?\]", new_block, src, flags=re.DOTALL)
    with open(DATA_FILE, "w") as f:
        f.write(src)


# ── Helpers ───────────────────────────────────────────────────────────────────

def avg_score(scores):
    # Treat score 0 ("N/A" in UI) as non-applicable for averages.
    vals = [v for v in scores.values() if isinstance(v, (int, float)) and v > 0]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 1)

def build_dataframe():
    rows = []
    for p in PERSONAS:
        row = {"Team": p["role"], "Primary Systems": f"[{p['system']}]"}
        for s in STAGES:
            row[s["label"]] = p["scores"][s["id"]]
        avg = avg_score(p["scores"])
        row["Avg"] = avg if avg is not None else "N/A"
        rows.append(row)
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🗺️ Heat Map Controls")
    st.markdown("---")

    edit_mode = st.toggle(
        "✏️ Edit Mode",
        value=False,
        help="Turn on to edit scores and notes directly. Changes save to data.py automatically."
    )

    if edit_mode:
        st.markdown(
            "<div style='background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;"
            "padding:10px;font-size:12px;color:#92400E;margin-bottom:4px;'>"
            "<strong>✏️ Edit Mode ON</strong><br>"
            "Click any ✏️ button in the grid to open the edit panel. "
            "Hit 💾 Save — changes write directly to data.py."
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    persona_options = ["All Teams"] + [p["role"] for p in PERSONAS]
    selected_persona_filter = st.selectbox("Filter by Team", persona_options)

    st.markdown("---")
    st.markdown("**Pain Score Legend**")
    for score, h in HEAT_COLORS.items():
        st.markdown(
            f"<span style='display:inline-block;width:12px;height:12px;border-radius:50%;"
            f"background:{h['dot']};margin-right:6px;vertical-align:middle;'></span>"
            f"<span style='font-size:13px;font-weight:600;color:{h['text']};'>{score} — {h['label']}</span>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("**Interview Status**")
    for p in PERSONAS:
        badge = (
            "<span style='background:#D1FAE5;color:#065F46;font-size:9px;font-weight:700;"
            "padding:1px 6px;border-radius:4px;border:1px solid #6EE7B7;'>✅ Validated</span>"
            if p["status"] == "validated" else
            "<span style='background:#FEF3C7;color:#92400E;font-size:9px;font-weight:700;"
            "padding:1px 6px;border-radius:4px;border:1px solid #FCD34D;'>🔵 Hypothesis</span>"
        )
        st.markdown(
            f"<div style='margin-bottom:6px;font-size:12px;'>"
            f"<strong>{p['role']}</strong> {badge}</div>",
            unsafe_allow_html=True
        )


# ── Header ────────────────────────────────────────────────────────────────────

mode_tag = "✏️ Edit Mode ON — click any cell to edit" if edit_mode else "🔵 Click for details"
st.markdown(f"""
<div class="vfb-header">
    <h1>🗺️ {APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
    <div style="margin-top:8px;">
<span class="vfb-tag">{mode_tag}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Filter ────────────────────────────────────────────────────────────────────

visible_personas = list(PERSONAS)
if selected_persona_filter != "All Teams":
    visible_personas = [p for p in visible_personas if p["role"] == selected_persona_filter]

if not visible_personas:
    st.warning("No teams match the current filters.")
    st.stop()


# ── Grid ──────────────────────────────────────────────────────────────────────

st.markdown("### Current-State System Pain Heat Map")
if edit_mode:
    st.caption("✏️ Edit Mode — click ✏️ on any cell to open the edit panel below.")
else:
    st.caption("Rows = teams · Columns = systems · Click any cell to see pain detail, workaround, and data gap.")

# Column widths: team label + one per system + avg
col_widths = [2.0] + [1.05] * len(STAGES) + [0.6]
header_cols = st.columns(col_widths)

header_cols[0].markdown(
    "<div style='font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;"
    "letter-spacing:0.08em;padding:4px 0;'>Team</div>",
    unsafe_allow_html=True
)
for i, s in enumerate(STAGES):
    header_cols[i + 1].markdown(
        f"<div style='font-size:10px;font-weight:700;color:#1A5C38;text-align:center;"
        f"padding:4px 2px;line-height:1.3;'>{s['label']}<br>"
        f"<span style='font-size:8px;color:#9CA3AF;font-weight:400;'>{s['desc']}</span></div>",
        unsafe_allow_html=True
    )
header_cols[-1].markdown(
    "<div style='font-size:10px;font-weight:700;color:#6B7280;text-align:center;padding:4px 0;'>Avg</div>",
    unsafe_allow_html=True
)
st.markdown("<hr style='margin:4px 0 8px;border-color:#E5E5E0;'>", unsafe_allow_html=True)

# ── Handle query-param cell clicks ───────────────────────────────────────────
qp = st.query_params.get("sel", None)
if qp:
    if st.session_state.get("selected_cell") and (
        st.session_state["selected_cell"]["persona_id"] + "__" +
        st.session_state["selected_cell"]["stage_id"] == qp
    ):
        st.session_state["selected_cell"] = None
    else:
        parts = qp.split("__", 1)
        if len(parts) == 2:
            st.session_state["selected_cell"] = {"persona_id": parts[0], "stage_id": parts[1]}
    st.query_params.clear()
    st.rerun()

selected_cell = st.session_state.get("selected_cell", None)

for p in visible_personas:
    row_cols    = st.columns(col_widths)
    bg           = "white"
    border_color = "#E5E5E0"
    p_color      = p["color"]

    you_badge = ""
    status_badge = (
        "<span style='background:#D1FAE5;color:#065F46;font-size:9px;font-weight:700;"
        "padding:1px 6px;border-radius:4px;border:1px solid #6EE7B7;'>✅</span>"
        if p["status"] == "validated" else
        "<span style='background:#FEF3C7;color:#92400E;font-size:9px;font-weight:700;"
        "padding:1px 6px;border-radius:4px;border:1px solid #FCD34D;'>🔵</span>"
    )

    row_cols[0].markdown(
        f"<div style='background:{bg};border-radius:8px;padding:8px 10px;border:1px solid {border_color};'>"
        f"<div style='display:flex;align-items:center;gap:4px;'>"
        f"<span style='width:8px;height:8px;border-radius:50%;background:{p_color};"
        f"display:inline-block;flex-shrink:0;'></span>"
        f"<strong style='font-size:12px;'>{p['role']}</strong>{you_badge} {status_badge}</div>"
        f"<div style='font-size:10px;color:#6B7280;margin-left:13px;margin-top:2px;'>{p['subtitle']}</div>"
        f"<div style='font-size:9px;color:{p_color};margin-left:13px;font-weight:600;'>[{p['system']}]</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    for i, s in enumerate(STAGES):
        score = p["scores"][s["id"]]
        h     = HEAT_COLORS[score]
        is_selected = (
            selected_cell is not None
            and selected_cell["persona_id"] == p["id"]
            and selected_cell["stage_id"]   == s["id"]
        )
        warn       = "⚠ " if score == 4 else ""
        cell_label = h["label"] if score > 0 else "N/A"
        sel_border = f"2.5px solid {p_color}" if is_selected else f"1.5px solid {h['dot']}80"
        sel_shadow = f"0 0 0 3px {p_color}30" if is_selected else "none"
        txt_color  = "#9CA3AF" if score == 0 else h["text"]
        font_style = "italic" if score == 0 else "normal"
        qp_val     = f"{p['id']}__{s['id']}"

        # Single styled <a> tag — no button, no ghost, full color control
        row_cols[i + 1].markdown(
            f"<a href='?sel={qp_val}' target='_self' style='"
            f"display:flex;align-items:center;justify-content:center;"
            f"background:{h['bg']};"
            f"border:{sel_border};"
            f"border-radius:8px;"
            f"box-shadow:{sel_shadow};"
            f"min-height:62px;"
            f"padding:10px 6px;"
            f"text-decoration:none;"
            f"cursor:pointer;"
            f"font-size:13px;font-weight:700;"
            f"color:{txt_color};"
            f"font-style:{font_style};"
            f"'>{warn}{cell_label}</a>",
            unsafe_allow_html=True
        )

    # Row average
    r_avg = avg_score(p["scores"])
    if r_avg is None:
        row_cols[-1].markdown(
            "<div style='background:#F8FAF8;border:1.5px solid #D1D5DB;"
            "border-radius:8px;text-align:center;padding:10px 4px;min-height:62px;"
            "display:flex;align-items:center;justify-content:center;'>"
            "<span style='font-size:14px;font-weight:800;color:#9CA3AF;font-style:italic;'>N/A</span></div>",
            unsafe_allow_html=True
        )
    else:
        h_avg = HEAT_COLORS[round(r_avg)]
        row_cols[-1].markdown(
            f"<div style='background:{h_avg['bg']};border:1.5px solid {h_avg['dot']};"
            f"border-radius:8px;text-align:center;padding:10px 4px;min-height:62px;"
            f"display:flex;align-items:center;justify-content:center;'>"
            f"<span style='font-size:14px;font-weight:800;color:{h_avg['text']};'>{r_avg}</span></div>",
            unsafe_allow_html=True
        )
    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)


# ── System (column) averages ──────────────────────────────────────────────────

if selected_persona_filter == "All Teams":
    st.markdown("<hr style='margin:8px 0 4px;border-color:#E5E5E0;'>", unsafe_allow_html=True)
    avg_cols = st.columns(col_widths)
    avg_cols[0].markdown(
        "<div style='font-size:10px;font-weight:700;color:#6B7280;text-transform:uppercase;"
        "letter-spacing:0.08em;padding:8px 10px;'>System Avg</div>",
        unsafe_allow_html=True
    )
    for i, s in enumerate(STAGES):
        sys_scores = [p["scores"][s["id"]] for p in PERSONAS if p["scores"][s["id"]] > 0]
        if not sys_scores:
            avg_cols[i + 1].markdown(
                "<div style='background:#F8FAF8;border:1.5px solid #D1D5DB;"
                "border-radius:8px;text-align:center;padding:8px 4px;'>"
                "<span style='font-size:13px;font-weight:800;color:#9CA3AF;font-style:italic;'>N/A</span></div>",
                unsafe_allow_html=True
            )
        else:
            s_avg = round(sum(sys_scores) / len(sys_scores), 1)
            h = HEAT_COLORS[round(s_avg)]
            avg_cols[i + 1].markdown(
                f"<div style='background:{h['bg']};border:1.5px solid {h['dot']};"
                f"border-radius:8px;text-align:center;padding:8px 4px;'>"
                f"<span style='font-size:13px;font-weight:800;color:{h['text']};'>{s_avg}</span></div>",
                unsafe_allow_html=True
            )
    avg_cols[-1].markdown("")


# ── Detail / Edit panel ───────────────────────────────────────────────────────

selected_cell = st.session_state.get("selected_cell", None)

if selected_cell:
    persona = next((p for p in PERSONAS if p["id"] == selected_cell["persona_id"]), None)
    stage   = next((s for s in STAGES   if s["id"] == selected_cell["stage_id"]),   None)

    if persona and stage:
        note  = persona["notes"][stage["id"]]
        score = persona["scores"][stage["id"]]
        h     = HEAT_COLORS[score]

        st.markdown("---")
        edit_badge = (
            " <span style='background:#FEF3C7;color:#92400E;font-size:11px;font-weight:700;"
            "padding:2px 10px;border-radius:10px;border:1px solid #FCD34D;'>✏️ Editing</span>"
            if edit_mode else ""
        )
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;'>"
            f"<span style='width:10px;height:10px;border-radius:50%;background:{persona['color']};"
            f"display:inline-block;'></span>"
            f"<strong style='font-size:15px;'>{persona['role']}</strong>"
            f"<span style='color:#6B7280;'>→</span>"
            f"<strong style='font-size:15px;'>{stage['label']}</strong>"
            f"<span style='font-size:10px;color:#9CA3AF;'>({stage['desc']})</span>"
            f"<span style='background:{h['bg']};color:{h['text']};border:1px solid {h['dot']};"
            f"font-size:11px;font-weight:800;padding:2px 10px;border-radius:10px;'>{h['label']} Pain</span>"
            f"{edit_badge}</div>",
            unsafe_allow_html=True
        )

        if edit_mode:
            score_labels = {0: "0 — None", 1: "1 — Low", 2: "2 — Medium", 3: "3 — High", 4: "4 — Critical ⚠"}
            col_score, col_status = st.columns([2, 1])
            with col_score:
                new_score = st.select_slider(
                    "Pain Score",
                    options=[0, 1, 2, 3, 4],
                    value=score,
                    format_func=lambda x: score_labels[x],
                    key=f"edit_score_{persona['id']}_{stage['id']}"
                )
            with col_status:
                new_status = st.selectbox(
                    "Interview Status",
                    options=["hypothesis", "validated"],
                    index=0 if persona["status"] == "hypothesis" else 1,
                    key=f"edit_status_{persona['id']}_{stage['id']}"
                )

            new_pain = st.text_area(
                "🔴 Pain Point",
                value=note.get("pain", ""),
                height=90,
                key=f"edit_pain_{persona['id']}_{stage['id']}"
            )
            new_workaround = st.text_area(
                "🟡 Current Workaround",
                value=note.get("workaround", ""),
                height=90,
                key=f"edit_wa_{persona['id']}_{stage['id']}"
            )
            new_datagap = st.text_area(
                "🩵 Data Gap",
                value=note.get("data_gap", ""),
                height=90,
                key=f"edit_dg_{persona['id']}_{stage['id']}"
            )

            save_col, cancel_col, _ = st.columns([1, 1, 4])
            with save_col:
                if st.button("💾 Save", type="primary", use_container_width=True):
                    try:
                        save_cell(
                            persona["id"], stage["id"],
                            new_score, new_pain, new_workaround, new_datagap, new_status
                        )
                        st.session_state["selected_cell"] = None
                        st.success("✅ Saved! Reloading...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save failed: {e}")
            with cancel_col:
                if st.button("✕ Cancel", use_container_width=True):
                    st.session_state["selected_cell"] = None
                    st.rerun()

        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f"<div class='detail-pain'>"
                    f"<div class='detail-label' style='color:#B91C1C;'>🔴 Pain Point</div>"
                    f"<div style='font-size:13px;line-height:1.6;'>{note.get('pain') or '—'}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"<div class='detail-workaround'>"
                    f"<div class='detail-label' style='color:#92400E;'>🟡 Current Workaround</div>"
                    f"<div style='font-size:13px;line-height:1.6;'>{note.get('workaround') or '—'}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with c3:
                st.markdown(
                    f"<div class='detail-datagap'>"
                    "<div class='detail-label' style='color:#0D9488;'>🩵 Data Gap</div>"
                    f"<div style='font-size:13px;line-height:1.6;'>{note.get('data_gap') or '—'}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            if st.button("✕ Close", key="close_detail"):
                st.session_state["selected_cell"] = None
                st.rerun()

else:
    prompt = (
        "✏️ Click any ✏️ button in the grid to edit that cell's score and notes"
        if edit_mode else
        "👆 Click for details"
    )
    st.markdown(
        f"<div style='background:white;border:1px dashed #E5E5E0;border-radius:10px;"
        f"padding:14px 18px;text-align:center;color:#9CA3AF;font-size:12px;margin-top:8px;'>"
        f"{prompt}</div>",
        unsafe_allow_html=True
    )


# ── Key observations ──────────────────────────────────────────────────────────

editing_obs = st.session_state.get("editing_observations", False)

st.markdown("---")
obs_col, obs_btn_col = st.columns([8, 1])
with obs_col:
    st.markdown(
        f"<div style='font-size:11px;font-weight:800;color:#0D9488;"
        f"text-transform:uppercase;letter-spacing:0.08em;'>"
        "🎯 Key Data Engineering Observations</div>",
        unsafe_allow_html=True
    )

if edit_mode and not editing_obs:
    with obs_btn_col:
        if st.button("✏️ Edit", key="obs_edit_btn"):
            st.session_state["editing_observations"] = True
            st.session_state["obs_draft"] = list(OBSERVATIONS)
            st.rerun()

if editing_obs and edit_mode:
    st.markdown("<div style='background:white;border:2px solid #C8A84B;border-radius:12px;padding:18px 20px;margin-top:10px;'>", unsafe_allow_html=True)
    draft = st.session_state.get("obs_draft", list(OBSERVATIONS))
    new_draft = []
    for idx, obs in enumerate(draft):
        row_col, del_col = st.columns([10, 1])
        with row_col:
            updated = st.text_area(f"Observation {idx + 1}", value=obs, height=80,
                                   key=f"obs_text_{idx}", label_visibility="collapsed")
            new_draft.append(updated)
        with del_col:
            if st.button("🗑", key=f"obs_del_{idx}"):
                draft.pop(idx)
                st.session_state["obs_draft"] = draft
                st.rerun()
    st.session_state["obs_draft"] = new_draft
    if st.button("➕ Add observation", key="obs_add"):
        st.session_state["obs_draft"].append("")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    save_col2, cancel_col2, _ = st.columns([1, 1, 5])
    with save_col2:
        if st.button("💾 Save observations", type="primary", use_container_width=True):
            filtered = [o.strip() for o in new_draft if o.strip()]
            try:
                save_observations(filtered)
                st.session_state["editing_observations"] = False
                st.session_state.pop("obs_draft", None)
                st.success("✅ Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")
    with cancel_col2:
        if st.button("✕ Cancel", key="obs_cancel", use_container_width=True):
            st.session_state["editing_observations"] = False
            st.session_state.pop("obs_draft", None)
            st.rerun()
else:
    items_html = "".join(f"<li style='margin-bottom:6px;'>{obs}</li>" for obs in OBSERVATIONS)
    st.markdown(
        f"<div class='obs-box' style='margin-top:8px;'>"
        f"<ul style='margin:0;padding-left:18px;font-size:12px;line-height:1.8;color:#1A1A1A;'>"
        f"{items_html}"
        f"</ul></div>",
        unsafe_allow_html=True
    )


# ── Export ────────────────────────────────────────────────────────────────────

st.markdown("---")
with st.expander("📥 Export scores as CSV"):
    df  = build_dataframe()
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download heat map scores (.csv)",
        data=csv,
        file_name="vafb_system_pain_heatmap.csv",
        mime="text/csv",
    )
    st.dataframe(df, use_container_width=True)