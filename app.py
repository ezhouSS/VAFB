"""
VFB Pain Heat Map — Streamlit App
==================================
Run locally:   streamlit run app.py
"""

import streamlit as st
import pandas as pd
import re
import os
from data import (
    STAGES, PERSONAS, HEAT_COLORS,
    APP_TITLE, APP_SUBTITLE, APP_CLIENT, EMMA_LABEL
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.py")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_CLIENT} · Pain Heat Map",
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
            # Detect entry into our target persona block
            if re.search(r'"id"\s*:\s*"' + re.escape(persona_id) + r'"', line):
                in_target_persona = True
                persona_entry_depth = brace_depth
            new_lines.append(line)
            i += 1
            continue

        # Check if we've exited the persona block
        if persona_entry_depth is not None and brace_depth < persona_entry_depth:
            in_target_persona = False
            in_scores = False
            in_notes = False
            in_target_note = False
            persona_entry_depth = None
            new_lines.append(line)
            i += 1
            continue

        # Update status
        if re.match(r'\s*"status"\s*:', line):
            indent = len(line) - len(line.lstrip())
            new_lines.append(" " * indent + '"status": "' + new_status + '",\n')
            i += 1
            continue

        # Enter scores block
        if re.match(r'\s*"scores"\s*:', line):
            in_scores = True
            in_notes = False
            new_lines.append(line)
            i += 1
            continue

        # Inside scores — update target stage
        if in_scores:
            if re.match(r'\s*"' + re.escape(stage_id) + r'"\s*:', line):
                indent = len(line) - len(line.lstrip())
                new_lines.append(" " * indent + '"' + stage_id + '":   ' + str(new_score) + ',\n')
                i += 1
                continue
            if stripped in ("},", "}"):
                in_scores = False

        # Enter notes block
        if re.match(r'\s*"notes"\s*:', line):
            in_notes = True
            in_scores = False
            new_lines.append(line)
            i += 1
            continue

        # Inside notes — find target stage note
        if in_notes and not in_target_note:
            if re.match(r'\s*"' + re.escape(stage_id) + r'"\s*:', line):
                in_target_note = True
            new_lines.append(line)
            i += 1
            continue

        # Inside target stage note — update the three fields
        if in_target_note:
            if re.match(r'\s*"pain"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_pain.replace("\\", "\\\\").replace('"', '\\"')
                new_lines.append(" " * indent + '"pain":       "' + escaped + '",\n')
                i += 1
                continue
            if re.match(r'\s*"workaround"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_workaround.replace("\\", "\\\\").replace('"', '\\"')
                new_lines.append(" " * indent + '"workaround": "' + escaped + '",\n')
                i += 1
                continue
            if re.match(r'\s*"data_gap"\s*:', line):
                indent = len(line) - len(line.lstrip())
                escaped = new_datagap.replace("\\", "\\\\").replace('"', '\\"')
                new_lines.append(" " * indent + '"data_gap":   "' + escaped + '",\n')
                in_target_note = False
                i += 1
                continue

        new_lines.append(line)
        i += 1

    with open(DATA_FILE, "w") as f:
        f.writelines(new_lines)


# ── Helpers ───────────────────────────────────────────────────────────────────

def avg_score(scores):
    vals = list(scores.values())
    return round(sum(vals) / len(vals), 1)

def build_dataframe():
    rows = []
    for p in PERSONAS:
        row = {"Persona": p["role"], "System": f"[{p['system']}]"}
        for s in STAGES:
            row[s["label"]] = p["scores"][s["id"]]
        row["Avg"] = avg_score(p["scores"])
        rows.append(row)
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🗺️ Heat Map Controls")
    st.markdown("---")

    edit_mode = st.toggle(
        "✏️ Edit Mode",
        value=False,
        help="Turn on to edit scores and notes directly in the dashboard. Changes save to data.py automatically."
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

    persona_options = ["All Personas"] + [p["role"] for p in PERSONAS]
    selected_persona_filter = st.selectbox("Filter by Persona", persona_options)

    st.markdown("---")
    highlight_critical  = st.toggle("⚠ Highlight Critical Only", value=False)
    show_validated_only = st.toggle("✅ Validated Interviews Only", value=False)

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
        if p["status"] == "validated":
            badge = "<span style='background:#D1FAE5;color:#065F46;font-size:9px;font-weight:700;padding:1px 6px;border-radius:4px;border:1px solid #6EE7B7;'>✅ Validated</span>"
        else:
            badge = "<span style='background:#FEF3C7;color:#92400E;font-size:9px;font-weight:700;padding:1px 6px;border-radius:4px;border:1px solid #FCD34D;'>🔵 Hypothesis</span>"
        st.markdown(
            f"<div style='margin-bottom:6px;font-size:12px;'><strong>{p['role']}</strong> {badge}</div>",
            unsafe_allow_html=True
        )


# ── Header ────────────────────────────────────────────────────────────────────

mode_tag = "✏️ Edit Mode ON — click any cell to edit" if edit_mode else "🔵 Click any cell for detail"
st.markdown(f"""
<div class="vfb-header">
    <h1>🗺️ {APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
    <div style="margin-top:8px;">
        <span class="vfb-tag">🟢 YOU LEAD = Data &amp; Systems row</span>
        <span class="vfb-tag">{mode_tag}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Filter ────────────────────────────────────────────────────────────────────

visible_personas = list(PERSONAS)
if selected_persona_filter != "All Personas":
    visible_personas = [p for p in visible_personas if p["role"] == selected_persona_filter]
if show_validated_only:
    visible_personas = [p for p in visible_personas if p["status"] == "validated"]
if highlight_critical:
    visible_personas = [p for p in visible_personas if any(v == 4 for v in p["scores"].values())]

if not visible_personas:
    st.warning("No personas match the current filters.")
    st.stop()


# ── Grid ──────────────────────────────────────────────────────────────────────

st.markdown("### Current-State Pain Heat Map")
if edit_mode:
    st.caption("✏️ Edit Mode — click ✏️ on any cell to open the edit panel below.")
else:
    st.caption("Click → on any cell to see the detail panel. Toggle Edit Mode in the sidebar to update scores and notes.")

# Headers
header_cols = st.columns([2.2] + [1] * len(STAGES) + [0.7])
header_cols[0].markdown(
    "<div style='font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;"
    "letter-spacing:0.08em;padding:4px 0;'>Persona</div>",
    unsafe_allow_html=True
)
for i, s in enumerate(STAGES):
    header_cols[i + 1].markdown(
        f"<div style='font-size:10px;font-weight:700;color:#1A5C38;text-align:center;"
        f"padding:4px 2px;line-height:1.3;'>{s['label']}<br>"
        f"<span style='font-size:8.5px;color:#9CA3AF;font-weight:400;'>{s['desc']}</span></div>",
        unsafe_allow_html=True
    )
header_cols[-1].markdown(
    "<div style='font-size:10px;font-weight:700;color:#6B7280;text-align:center;padding:4px 0;'>Avg</div>",
    unsafe_allow_html=True
)
st.markdown("<hr style='margin:4px 0 8px;border-color:#E5E5E0;'>", unsafe_allow_html=True)

selected_cell = st.session_state.get("selected_cell", None)

for p in visible_personas:
    row_cols = st.columns([2.2] + [1] * len(STAGES) + [0.7])
    bg           = "#F0FDFA" if p["is_emma"] else "white"
    border_color = "#CCFBF1" if p["is_emma"] else "#E5E5E0"
    p_color      = p["color"]

    you_badge = (
        "<span style='background:#0D9488;color:white;font-size:9px;font-weight:800;"
        "padding:1px 6px;border-radius:4px;margin-left:6px;'>YOU</span>"
        if p["is_emma"] else ""
    )
    if p["status"] == "validated":
        status_badge = "<span style='background:#D1FAE5;color:#065F46;font-size:9px;font-weight:700;padding:1px 6px;border-radius:4px;border:1px solid #6EE7B7;'>✅</span>"
    else:
        status_badge = "<span style='background:#FEF3C7;color:#92400E;font-size:9px;font-weight:700;padding:1px 6px;border-radius:4px;border:1px solid #FCD34D;'>🔵</span>"

    row_cols[0].markdown(
        f"<div style='background:{bg};border-radius:8px;padding:8px 10px;border:1px solid {border_color};'>"
        f"<div style='display:flex;align-items:center;gap:4px;'>"
        f"<span style='width:8px;height:8px;border-radius:50%;background:{p_color};display:inline-block;flex-shrink:0;'></span>"
        f"<strong style='font-size:12px;'>{p['role']}</strong>{you_badge} {status_badge}</div>"
        f"<div style='font-size:10px;color:#6B7280;margin-left:13px;margin-top:2px;'>{p['subtitle']}</div>"
        f"<div style='font-size:9px;color:{p_color};margin-left:13px;font-weight:600;'>[{p['system']}]</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    for i, s in enumerate(STAGES):
        score = p["scores"][s["id"]]
        h     = HEAT_COLORS[score]
        cell_key = f"cell_{p['id']}_{s['id']}"
        is_selected = (
            selected_cell is not None
            and selected_cell["persona_id"] == p["id"]
            and selected_cell["stage_id"]   == s["id"]
        )

        sel_color  = "#0D9488" if p["is_emma"] else p_color
        border     = f"2.5px solid {sel_color}" if is_selected else f"1.5px solid {h['dot']}80"
        glow       = f"0 0 0 3px {p_color}30"  if is_selected else "none"
        dot_shadow = "0 0 6px " + h["dot"] + "80" if score >= 3 else "none"

        dot_html   = (
            f"<div style='width:11px;height:11px;border-radius:50%;background:{h['dot']};"
            f"margin:0 auto 3px;box-shadow:{dot_shadow};'></div>"
        ) if score > 0 else ""
        warn       = "⚠" if score == 4 else ""
        label_html = f"<div style='font-size:10px;font-weight:700;color:{h['text']};'>{h['label'] if score > 0 else '—'}</div>"
        warn_html  = f"<div style='font-size:9px;color:{h['text']};font-weight:800;'>{warn}</div>" if warn else ""

        row_cols[i + 1].markdown(
            f"<div style='background:{h['bg']};border:{border};border-radius:8px;"
            f"padding:8px 4px;text-align:center;min-height:52px;display:flex;flex-direction:column;"
            f"align-items:center;justify-content:center;box-shadow:{glow};'>"
            f"{dot_html}{label_html}{warn_html}</div>",
            unsafe_allow_html=True
        )

        btn_label = "✏️" if edit_mode else "→"
        if row_cols[i + 1].button(btn_label, key=cell_key, use_container_width=True):
            if is_selected:
                st.session_state["selected_cell"] = None
            else:
                st.session_state["selected_cell"] = {"persona_id": p["id"], "stage_id": s["id"]}
            st.rerun()

    # Row average
    r_avg   = avg_score(p["scores"])
    h_avg   = HEAT_COLORS[round(r_avg)]
    row_cols[-1].markdown(
        f"<div style='background:{h_avg['bg']};border:1.5px solid {h_avg['dot']};"
        f"border-radius:8px;text-align:center;padding:10px 4px;min-height:52px;"
        f"display:flex;align-items:center;justify-content:center;'>"
        f"<span style='font-size:14px;font-weight:800;color:{h_avg['text']};'>{r_avg}</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)


# ── Stage averages ────────────────────────────────────────────────────────────

if selected_persona_filter == "All Personas":
    st.markdown("<hr style='margin:8px 0 4px;border-color:#E5E5E0;'>", unsafe_allow_html=True)
    avg_cols = st.columns([2.2] + [1] * len(STAGES) + [0.7])
    avg_cols[0].markdown(
        "<div style='font-size:10px;font-weight:700;color:#6B7280;text-transform:uppercase;"
        "letter-spacing:0.08em;padding:8px 10px;'>Stage Avg</div>",
        unsafe_allow_html=True
    )
    for i, s in enumerate(STAGES):
        stage_scores = [p["scores"][s["id"]] for p in PERSONAS]
        s_avg  = round(sum(stage_scores) / len(stage_scores), 1)
        h      = HEAT_COLORS[round(s_avg)]
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
            f"<span style='width:10px;height:10px;border-radius:50%;background:{persona['color']};display:inline-block;'></span>"
            f"<strong style='font-size:15px;'>{persona['role']}</strong>"
            f"<span style='color:#6B7280;'>→</span>"
            f"<strong style='font-size:15px;'>{stage['label']}</strong>"
            f"<span style='background:{h['bg']};color:{h['text']};border:1px solid {h['dot']};"
            f"font-size:11px;font-weight:800;padding:2px 10px;border-radius:10px;'>{h['label']} Pain</span>"
            f"{edit_badge}</div>",
            unsafe_allow_html=True
        )

        if edit_mode:
            # ── EDIT FORM ─────────────────────────────────────────────────────
            score_labels = {
                0: "0 — None",
                1: "1 — Low",
                2: "2 — Medium",
                3: "3 — High",
                4: "4 — Critical ⚠"
            }

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
                f"🩵 Data Gap ({EMMA_LABEL})",
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
            # ── READ-ONLY DETAIL ──────────────────────────────────────────────
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
                    f"<div class='detail-label' style='color:#0D9488;'>🩵 Data Gap ({EMMA_LABEL})</div>"
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
        "👆 Click any → button in the grid to see the pain detail, workaround, and data gap"
    )
    st.markdown(
        f"<div style='background:white;border:1px dashed #E5E5E0;border-radius:10px;"
        f"padding:14px 18px;text-align:center;color:#9CA3AF;font-size:12px;margin-top:8px;'>"
        f"{prompt}</div>",
        unsafe_allow_html=True
    )


# ── Key observations ──────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    f"<div class='obs-box'>"
    f"<div style='font-size:11px;font-weight:800;color:#0D9488;"
    f"text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>"
    f"🎯 {EMMA_LABEL}'s Key Data Engineering Observations</div>"
    f"<ul style='margin:0;padding-left:18px;font-size:12px;line-height:1.8;color:#1A1A1A;'>"
    f"<li><strong>Join/Buy and Policy in Force</strong> are the hottest stages — "
    f"the Finys ↔ Personify identity bridge gap is the root cause of both</li>"
    f"<li><strong>Renewal/Expand</strong> is critical for Ray, Jason, and Bill — "
    f"no event-driven pipeline exists out of Finys today</li>"
    f"<li><strong>Bob's Service Event</strong> is the only critical cell in that column — "
    f"claims data is completely dark to the relationship management side</li>"
    f"<li><strong>Jenny's row</strong> is the technical debt layer — no Finys API means "
    f"none of the high-pain items can be solved without her foundational work first</li>"
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
        file_name="vfb_pain_heatmap_scores.csv",
        mime="text/csv",
    )
    st.dataframe(df, use_container_width=True)
