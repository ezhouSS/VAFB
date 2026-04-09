"""
VAFB System Map — Streamlit Page
Add this as pages/system_map.py in your existing Streamlit app,
or run standalone with: streamlit run system_map.py
"""

import streamlit as st
import pandas as pd
from systems_data import SYSTEMS, get_all_workarounds, get_integration_gaps

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="VAFB System Map", layout="wide")

SEVERITY_COLOR = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}
SEVERITY_LABEL = {1: "Low", 2: "Minor", 3: "Moderate", 4: "High", 5: "Critical"}

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🗺️ VAFB System Map")
st.caption("Systems · Teams · Gaps · Workarounds — Internal synthesis draft")
st.divider()

# ── View toggle ──────────────────────────────────────────────────────────────
view = st.radio(
    "View",
    ["System Cards", "Workaround Inventory", "Integration Gaps"],
    horizontal=True,
)
st.divider()

# ════════════════════════════════════════════════════════════════════════════
# VIEW 1: SYSTEM CARDS
# ════════════════════════════════════════════════════════════════════════════
if view == "System Cards":

    # Severity filter
    min_sev = st.slider("Minimum severity", 1, 5, 1)
    filtered = [s for s in SYSTEMS if s["severity"] >= min_sev]
    st.caption(f"Showing {len(filtered)} of {len(SYSTEMS)} systems")
    st.write("")

    for system in sorted(filtered, key=lambda x: x["severity"], reverse=True):
        sev_icon = SEVERITY_COLOR[system["severity"]]
        sev_label = SEVERITY_LABEL[system["severity"]]

        with st.expander(
            f"{sev_icon} **{system['name']}** — {system['category']}  |  Severity: {sev_label}",
            expanded=system["severity"] >= 4,
        ):
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Owner**")
                st.write(system["owner"])

                st.markdown("**Teams Using This System**")
                for t in system["teams_using"]:
                    st.write(f"• {t}")
                st.write(f"*~{system['approx_headcount']} people*")

                st.markdown("**Core Functions**")
                for f in system["core_functions"]:
                    st.write(f"• {f}")

            with col2:
                st.markdown("**⚠️ Known Gaps**")
                for g in system["known_gaps"]:
                    st.write(f"• {g}")

                st.markdown("**🔧 Workarounds in Use**")
                for w in system["workarounds"]:
                    st.write(f"• {w}")

            # Integration status
            st.markdown("**🔗 Integrations**")
            int_col1, int_col2 = st.columns(2)
            with int_col1:
                st.markdown("*Confirmed*")
                confirmed = system["integrations"].get("confirmed", [])
                if confirmed:
                    for c in confirmed:
                        st.write(f"✅ {c}")
                else:
                    st.write("None confirmed")
            with int_col2:
                st.markdown("*Unconfirmed / Gaps*")
                for u in system["integrations"].get("unconfirmed", []):
                    st.write(f"❓ {u}")

            if system.get("notes"):
                st.info(f"📝 {system['notes']}")

# ════════════════════════════════════════════════════════════════════════════
# VIEW 2: WORKAROUND INVENTORY
# ════════════════════════════════════════════════════════════════════════════
elif view == "Workaround Inventory":
    st.markdown("### All Workarounds by System")
    st.caption("Every manual process, shadow spreadsheet, and compensating behavior across the landscape.")
    st.write("")

    workarounds = get_all_workarounds()
    df = pd.DataFrame(workarounds)
    df["severity_label"] = df["severity"].map(SEVERITY_LABEL)
    df["icon"] = df["severity"].map(SEVERITY_COLOR)
    df["display"] = df["icon"] + " " + df["severity_label"]

    # Summary metric
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Workarounds", len(df))
    col2.metric("Systems Affected", df["system"].nunique())
    col3.metric("High/Critical Systems", len(df[df["severity"] >= 4]["system"].unique()))

    st.write("")

    # Group by system
    for system_name in df["system"].unique():
        subset = df[df["system"] == system_name]
        sev = subset["severity"].iloc[0]
        icon = SEVERITY_COLOR[sev]
        label = SEVERITY_LABEL[sev]

        with st.expander(f"{icon} **{system_name}** ({label}) — {len(subset)} workaround(s)", expanded=sev >= 4):
            for _, row in subset.iterrows():
                st.write(f"🔧 {row['workaround']}")

    st.write("")
    st.markdown("#### Full Table")
    display_df = df[["system", "severity_label", "workaround"]].rename(
        columns={"system": "System", "severity_label": "Severity", "workaround": "Workaround"}
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# VIEW 3: INTEGRATION GAPS
# ════════════════════════════════════════════════════════════════════════════
elif view == "Integration Gaps":
    st.markdown("### Unconfirmed Integrations & Connection Gaps")
    st.caption("These are the seams where data falls through. Gaps marked ❓ need validation in workshops.")
    st.write("")

    gaps = get_integration_gaps()
    df = pd.DataFrame(gaps)
    df["severity_label"] = df["severity"].map(SEVERITY_LABEL)
    df["icon"] = df["severity"].map(SEVERITY_COLOR)

    col1, col2 = st.columns(2)
    col1.metric("Total Unconfirmed Connections", len(df))
    col2.metric("Systems with Gaps", df["system"].nunique())

    st.write("")

    # Highlight the Personify-Finys gap prominently
    st.error(
        "🚨 **Critical gap: Personify ↔ Finys** — No universal member ID. "
        "This is the root cause of the Member 360 problem at VAFB."
    )
    st.write("")

    for system_name in df["system"].unique():
        subset = df[df["system"] == system_name]
        sev = subset["severity"].iloc[0]
        icon = SEVERITY_COLOR[sev]

        with st.expander(f"{icon} **{system_name}** — {len(subset)} unconfirmed connection(s)", expanded=sev >= 4):
            for _, row in subset.iterrows():
                st.write(f"❓ {row['gap']}")

    st.write("")
    st.markdown("#### Full Table")
    display_df = df[["system", "severity_label", "gap"]].rename(
        columns={"system": "System", "severity_label": "Severity", "gap": "Unconfirmed Integration / Gap"}
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ Internal draft — data sourced from stakeholder interviews. Validate in workshops before sharing externally.")
