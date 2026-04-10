"""
VAFB Dependency Map — Streamlit Page
Save as pages/dependency_map.py in your VAFB Streamlit app.
Requires: plotly, networkx, streamlit
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import math

# ── Import systems data ───────────────────────────────────────────────────────
from systems_data import SYSTEMS
from data import PERSONAS

st.set_page_config(page_title="VAFB Dependency Map", layout="wide")

# ── Shared constants ──────────────────────────────────────────────────────────
SEVERITY_COLOR = {
    1: "#4caf50",
    2: "#8bc34a",
    3: "#ff9800",
    4: "#f44336",
    5: "#b71c1c",
}
SEVERITY_LABEL = {1: "Low", 2: "Minor", 3: "Moderate", 4: "High", 5: "Critical"}
SEVERITY_ICON  = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}

# ── Dependency data ───────────────────────────────────────────────────────────
# (source_id, target_id, label, confirmed)
SYSTEM_EDGES = [
    ("personify",        "hubspot",          "Member lists → campaigns",              True),
    ("personify",        "finys",            "Member ↔ Policyholder link",            False),
    ("personify",        "ods",              "Member data → ODS",                     False),
    ("finys",            "ods",              "Policy/claims → ODS extract",           True),
    ("finys",            "imageright",       "Documents → ImageRight",                True),
    ("finys",            "netsuite",         "Billing → NetSuite (unclear)",          False),
    ("countryway",       "finys",            "Migration in progress",                 False),
    ("countryway",       "ods",              "Reporting → ODS (unconfirmed)",         False),
    ("hubspot",          "finys",            "No connection (gap)",                   False),
    ("hubspot",          "ods",              "No ODS feed (gap)",                     False),
    # Brokerage cluster — isolated, no integration to core systems
    ("nexsure",          "personify",        "Manual entry only (gap)",               False),
    ("nexsure",          "finys",            "No integration (gap)",                  False),
    ("applied_rater",    "nexsure",          "Quote → brokerage mgmt",                True),
    ("carrier_portals",  "nexsure",          "Commission data → Nexsure",             True),
    # Claims vendor cluster — no Finys integration
    ("finys",            "claimant_locator", "Claims contact data (separate system)", False),
    ("claimant_locator", "personify",        "No integration (gap)",                  False),
    ("himarly",          "finys",            "No integration (gap)",                  False),
    ("first_call",       "finys",            "Limited access — no phone search",      False),
    # External data providers
    ("lexisnexis",       "finys",            "Prior loss data for underwriting decisions", True),
]

# System short names for display
SYS_LABEL = {s["id"]: s["name"].split("/")[0].strip() for s in SYSTEMS}
SYS_LABEL["ods"]              = "ODS / Analytics"
SYS_LABEL["netsuite"]         = "NetSuite"
SYS_LABEL["imageright"]       = "ImageRight"
SYS_LABEL["nexsure"]          = "Nexsure"
SYS_LABEL["applied_rater"]    = "Applied Rater"
SYS_LABEL["carrier_portals"]  = "Carrier Portals"
SYS_LABEL["claimant_locator"] = "Claimant Locator"
SYS_LABEL["himarly"]          = "HiMarly"
SYS_LABEL["first_call"]       = "First Call"
SYS_LABEL["lexisnexis"]       = "LexisNexis"

SYS_LOOKUP = {s["id"]: s for s in SYSTEMS}
# Lightweight proxy entries for split nodes so SYS_LOOKUP works in Tab 1
SYS_LOOKUP["ods"]        = {**SYS_LOOKUP["supporting"], "id": "ods",
                             "name": "ODS / Analytics", "category": "Analytics & Reporting"}
SYS_LOOKUP["netsuite"]   = {**SYS_LOOKUP["supporting"], "id": "netsuite",
                             "name": "NetSuite", "category": "Finance & Payments"}
SYS_LOOKUP["imageright"] = {**SYS_LOOKUP["supporting"], "id": "imageright",
                             "name": "ImageRight", "category": "Document Management"}
# Brokerage cluster proxies
_brokerage_proxy = {"severity": 3, "owner": "IAS (Tammy Hoard)", "known_gaps": [], "workarounds": []}
SYS_LOOKUP["nexsure"]         = {**_brokerage_proxy, "id": "nexsure",
                                   "name": "Nexsure", "category": "Brokerage Management"}
SYS_LOOKUP["applied_rater"]   = {**_brokerage_proxy, "id": "applied_rater",
                                   "name": "Applied Rater", "category": "Brokerage Quoting"}
SYS_LOOKUP["carrier_portals"] = {**_brokerage_proxy, "id": "carrier_portals",
                                   "name": "Carrier Portals", "category": "Brokerage / 3rd Party"}
# Claims vendor proxies
_vendor_proxy = {"severity": 2, "owner": "Claims / 3rd party", "known_gaps": [], "workarounds": []}
SYS_LOOKUP["claimant_locator"] = {**_vendor_proxy, "id": "claimant_locator",
                                    "name": "Claimant Locator", "category": "Claims Contact Data"}
SYS_LOOKUP["himarly"]          = {**_vendor_proxy, "id": "himarly",
                                    "name": "HiMarly", "category": "Customer Texting"}
SYS_LOOKUP["first_call"]       = {**_vendor_proxy, "id": "first_call",
                                    "name": "First Call", "category": "After-hours Claims"}
# External data provider proxies
_ext_proxy = {"severity": 2, "owner": "Underwriting / 3rd party", "known_gaps": [], "workarounds": []}
SYS_LOOKUP["lexisnexis"]       = {**_ext_proxy, "id": "lexisnexis",
                                    "name": "LexisNexis", "category": "External Data Provider"}
# Team → systems they depend on
# Source: data.py PERSONAS — systems with score > 0, mapped to dependency map node IDs
# Averages: non-zero scores only (matches heat map display)
TEAM_SYSTEM_DEPS = [
    ("Underwriting",               ["personify", "finys", "imageright", "ods", "countryway"],                                          15),
    ("Claims",                     ["personify", "finys", "imageright", "ods", "countryway", "claimant_locator"],                      10),
    ("Policy Services",            ["personify", "finys", "imageright", "ods", "countryway"],                                           8),
    ("Membership & Field Services",["personify", "finys", "ods", "netsuite", "hubspot"],                                                8),
    ("Marketing",                  ["personify", "finys", "ods", "hubspot", "nexsure"],                                                 8),
    ("Sales / Field Agents",       ["personify", "finys", "imageright", "ods", "hubspot", "nexsure", "countryway"],                     5),
    ("Countryway Ops",             ["personify", "finys", "imageright", "ods", "netsuite", "countryway"],                              15),
    ("IS / Data Services",         ["personify", "finys", "imageright", "ods", "netsuite", "hubspot", "nexsure", "countryway"],         4),
    ("Accounting / Products",      ["personify", "finys", "ods", "netsuite", "countryway"],                                             6),
    ("Federation / Special Programs",["personify", "finys", "ods", "netsuite", "hubspot"],                                              2),
    ("Healthcare",                 ["personify", "ods"],                                                                                 3),
    ("Grain Operations",           ["personify", "ods", "netsuite"],                                                                    2),
    ("Meadow Event Farm",          ["personify", "ods", "netsuite"],                                                                    2),
]

# Workaround → upstream root cause system
WORKAROUND_CHAINS = [
    {
        "root_system": "personify",
        "root_gap": "No universal member ID / no Finys linkage",
        "workaround": "Manual name/address matching between Personify and Finys",
        "teams_affected": ["Underwriting", "Claims", "Marketing", "Sales / Field Agents"],
        "downstream_systems": ["finys", "hubspot", "ods"],
    },
    {
        "root_system": "personify",
        "root_gap": "Stale / unsynced member data in HubSpot",
        "workaround": "Marketing manually exports Personify lists into HubSpot before campaigns",
        "teams_affected": ["Marketing", "Sales / Field Agents"],
        "downstream_systems": ["hubspot"],
    },
    {
        "root_system": "personify",
        "root_gap": "Contact data often 5+ years out of date",
        "workaround": "Claims team uses Claimant Locator as fallback — two separate systems, not linked",
        "teams_affected": ["Claims"],
        "downstream_systems": ["claimant_locator"],
    },
    {
        "root_system": "finys",
        "root_gap": "Delivery governance gap — functionality in prod without sign-off",
        "workaround": "Shadow spreadsheets to track policy status during Countryway migration",
        "teams_affected": ["Policy Services", "Countryway Ops"],
        "downstream_systems": ["countryway", "ods"],
    },
    {
        "root_system": "finys",
        "root_gap": "Finys doesn't surface document context natively",
        "workaround": "Claims/underwriting staff toggle between Finys and ImageRight manually",
        "teams_affected": ["Claims", "Underwriting"],
        "downstream_systems": ["ods"],
    },
    {
        "root_system": "finys",
        "root_gap": "No brokerage quoting integration — agents re-enter data manually",
        "workaround": "Agents quote brokerage in separate carrier portals, then manually re-key into Finys / Personify",
        "teams_affected": ["IAS Brokerage", "Sales / Field Agents", "Training"],
        "downstream_systems": ["nexsure", "personify"],
    },
    {
        "root_system": "finys",
        "root_gap": "No CRM pipeline or renewal visibility for agents",
        "workaround": "Field agents maintain personal Excel spreadsheets for prospect tracking — lost when agent leaves",
        "teams_affected": ["Sales / Field Agents", "Training"],
        "downstream_systems": [],
    },
    {
        "root_system": "countryway",
        "root_gap": "No IS & EDM integration — no automated reporting",
        "workaround": "Staff pull manual extracts for leadership visibility",
        "teams_affected": ["Countryway Ops", "Data / Analytics"],
        "downstream_systems": ["ods"],
    },
    {
        "root_system": "countryway",
        "root_gap": "Mid-migration dual-system operation",
        "workaround": "Countryway staff run parallel workflows in AS400 and Finys simultaneously",
        "teams_affected": ["Countryway Ops"],
        "downstream_systems": ["finys"],
    },
    {
        "root_system": "ods",
        "root_gap": "ODS data unreliable due to upstream classification errors",
        "workaround": "Actuarial and product teams maintain their own Excel models",
        "teams_affected": ["Product / Actuarial", "Data / Analytics"],
        "downstream_systems": [],
    },
    {
        "root_system": "ods",
        "root_gap": "ODS reports have hidden filters from past migrations — payment data missing, discrepancies up to $100Ks",
        "workaround": "Claims manager manually pulls from 2–3 systems monthly (~6 hrs/month for a single incurred development report)",
        "teams_affected": ["Claims", "Sales Analytics"],
        "downstream_systems": [],
    },
    {
        "root_system": "ods",
        "root_gap": "NetSuite ↔ Finys reconciliation unclear",
        "workaround": "Accounting manually reconciles NetSuite entries against Finys billing extracts",
        "teams_affected": ["Accounting / Finance"],
        "downstream_systems": ["finys"],
    },
    {
        "root_system": "nexsure",
        "root_gap": "Brokerage data invisible at enterprise level — 15 years of history untracked",
        "workaround": "Sales Analytics manually consolidates commission data from carrier portals via Excel",
        "teams_affected": ["IAS Brokerage", "Sales Analytics"],
        "downstream_systems": ["ods"],
    },
]


# ── Layout ────────────────────────────────────────────────────────────────────
st.title("🔗 VAFB Dependency Map")
st.caption("System flows · Team impact · Workaround chains — Internal synthesis draft")
st.divider()

tab1, tab2, tab3 = st.tabs([
    "📡 System → System Flow",
    "👥 System → Team Impact",
    "🗺️ Acquisition Flow",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: SYSTEM → SYSTEM FLOW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### System Data Flow")
    st.caption("Solid lines = confirmed integrations · Dashed = unconfirmed / gaps · Click a node to explore")

    # ── People data ────────────────────────────────────────────────────────
    SYSTEM_PEOPLE = {
        "finys": {
            "enter":   [("Ed Baumgartner", "Policy Services"), ("Ben Ashby", "Underwriting"),
                        ("Scott Denoon", "VP Underwriting"), ("Agents", "Policy entry")],
            "manage":  [("Catherine Reid", "System owner"), ("Jenny Glenn", "Co-owner"),
                        ("Theresa Richardson", "Tech / migration"), ("Kim Boos", "Data Services")],
            "consume": [("Laurie Gannon", "Claims"), ("David Jewell", "Claims (home/auto)"),
                        ("George Webster", "Digital product"), ("Paula Chavis", "Customer Service")],
        },
        "personify": {
            "enter":   [("County agents", "Member intake"), ("Field reps", "Membership"),
                        ("Bobby Goodwin", "OneCallNow"), ("Daryl Butler", "Field Services")],
            "manage":  [("Karen Clarke", "System owner"), ("Jake Whitlow", "Governance lead"),
                        ("Kim Boos", "Data Services")],
            "consume": [("Kyle Shover", "Marketing"), ("Mike Bolino", "Marketing"),
                        ("Ray Leonard", "Sales"), ("George Webster", "Digital / member view")],
        },
        "countryway": {
            "enter":   [("Stacy Lister", "CW Sales"), ("Paula Chavis", "Customer Service"),
                        ("David Jewell", "Claims (farm)"), ("CW Agents", "Logins · commissions")],
            "manage":  [("Theresa Richardson", "Migration owner"), ("Kim Boos", "Data Services"),
                        ("Jennifer McBride", "Data engineering")],
            "consume": [("Stacy Lister", "Sales dashboard"), ("Scott Denoon", "VP Underwriting"),
                        ("William Skorzyk", "VP Marketing & Sales")],
        },
        "hubspot": {
            "enter":   [("Kyle Shover", "Primary owner (manual pull)"), ("Mike Bolino", "Marketing ops")],
            "manage":  [("Kyle Shover", "System owner"), ("Mike Bolino", "Marketing ops")],
            "consume": [("Kyle Shover", "Marketing campaigns"), ("Ray Leonard", "Sales"),
                        ("William Skorzyk", "VP Marketing & Sales"), ("Bob Brown", "Exec lens")],
        },
        "ods": {
            "enter":   [("Kim Boos", "ODS owner — no direct field entry")],
            "manage":  [("Kim Boos", "ODS owner"), ("Jennifer McBride", "Data engineering"),
                        ("Jake Whitlow", "Governance")],
            "consume": [("Jake Whitlow", "Governance reporting"), ("Karen Clarke", "Ad hoc reports"),
                        ("Sarah Person", "Product + Actuarial"), ("Shail Depura", "VP Product"),
                        ("Chuck Salerno", "Accounting"), ("Jacki Picco", "Finance")],
        },
        "netsuite": {
            "enter":   [("Jacki Picco", "Accounting PM"), ("Jason Hart", "Management Consultant"),
                        ("Chuck Salerno", "Accounting")],
            "manage":  [("Jacki Picco", "System PM"), ("Kim Boos", "Data Services"),
                        ("Jennifer McBride", "Data engineering")],
            "consume": [("Jacki Picco", "Finance reporting"), ("Chuck Salerno", "Accounting"),
                        ("Bob Brown", "Exec financial view"), ("Jake Whitlow", "Governance / audit")],
        },
        "imageright": {
            "enter":   [("Catherine Reid", "Policy Services"), ("Paula Chavis", "Customer Service"),
                        ("Agents", "Doc upload")],
            "manage":  [("Theresa Richardson", "All systems / tech"), ("Catherine Reid", "System owner")],
            "consume": [("Paula Chavis", "Customer Service"), ("Laurie Gannon", "Claims"),
                        ("David Jewell", "Claims"), ("Ben Ashby", "Underwriting")],
        },
        "nexsure": {
            "enter":   [("Tammy Hoard", "IAS Brokerage"), ("Corey Fleet", "IAS Brokerage"),
                        ("Rob Urema", "IAS Brokerage")],
            "manage":  [("Tammy Hoard", "System lead")],
            "consume": [("Ray Leonard", "Sales"), ("Agents", "Brokerage quotes")],
        },
        "applied_rater": {
            "enter":   [("Tammy Hoard", "IAS quoting"), ("Corey Fleet", "IAS quoting")],
            "manage":  [("Tammy Hoard", "System lead")],
            "consume": [("Agents", "Comparative quotes"), ("IAS Brokerage", "Placement")],
        },
        "carrier_portals": {
            "enter":   [("Tammy Hoard", "IAS"), ("Corey Fleet", "IAS"), ("Rob Urema", "IAS")],
            "manage":  [("Tammy Hoard", "Carrier relationship mgmt")],
            "consume": [("Agents", "Brokerage placement"), ("Sales Analytics", "Commission data")],
        },
        "claimant_locator": {
            "enter":   [("Claims team", "FNOL intake")],
            "manage":  [("Ann Baskett", "Claims Admin")],
            "consume": [("Dwayne", "CS Manager"), ("David Jewell", "Property claims"),
                        ("First Call", "After-hours — limited access")],
        },
        "himarly": {
            "enter":   [("Claims team", "Outbound texts")],
            "manage":  [("Dwayne", "CS Manager")],
            "consume": [("Ann Baskett", "Customer comms"), ("Claims adjusters", "Field comms")],
        },
        "first_call": {
            "enter":   [("First Call staff", "After-hours FNOL")],
            "manage":  [("Ann Baskett", "Vendor relationship")],
            "consume": [("Dwayne", "Overflow call handling")],
        },
        "lexisnexis": {
            "enter":   [("LexisNexis", "External data feed")],
            "manage":  [("Underwriting team", "Vendor relationship")],
            "consume": [("Ben Ashby", "Underwriting"), ("Scott Denoon", "VP Underwriting")],
        },
    }

    # ── Node layout & styles ───────────────────────────────────────────────
    NODE_POS = {
        # Core systems — top two rows
        "personify":        (0.2,  2.2),
        "finys":            (3.2,  2.2),
        "countryway":       (0.2,  0.5),
        "hubspot":          (6.4,  2.2),
        "ods":              (6.4,  0.5),
        "netsuite":         (3.2,  0.5),
        "imageright":       (6.4, -1.2),
        # Brokerage cluster — bottom left
        "nexsure":          (0.2, -1.2),
        "applied_rater":    (0.2, -2.9),
        "carrier_portals":  (3.2, -2.9),
        # Claims vendor cluster — bottom right
        "claimant_locator": (6.4, -2.9),
        "himarly":          (6.4, -4.4),
        "first_call":       (3.2, -4.4),
        # External data providers — far right
        "lexisnexis":       (9.0,  0.5),
    }
    NODE_STYLE = {
        "personify":        {"fill": "#E1F5EE", "line": "#0F6E56", "text": "#085041"},
        "finys":            {"fill": "#FAECE7", "line": "#993C1D", "text": "#712B13"},
        "countryway":       {"fill": "#F1EFE8", "line": "#5F5E5A", "text": "#2C2C2A"},
        "hubspot":          {"fill": "#FAEEDA", "line": "#854F0B", "text": "#633806"},
        "ods":              {"fill": "#EEEDFE", "line": "#534AB7", "text": "#3C3489"},
        "netsuite":         {"fill": "#E6F1FB", "line": "#185FA5", "text": "#0C447C"},
        "imageright":       {"fill": "#FAECE7", "line": "#993C1D", "text": "#712B13"},
        # Brokerage — coral
        "nexsure":          {"fill": "#FAECE7", "line": "#D85A30", "text": "#993C1D"},
        "applied_rater":    {"fill": "#FAECE7", "line": "#D85A30", "text": "#993C1D"},
        "carrier_portals":  {"fill": "#FAECE7", "line": "#D85A30", "text": "#993C1D"},
        # Claims vendors — purple
        "claimant_locator": {"fill": "#EEEDFE", "line": "#7F77DD", "text": "#3C3489"},
        "himarly":          {"fill": "#EEEDFE", "line": "#7F77DD", "text": "#3C3489"},
        "first_call":       {"fill": "#EEEDFE", "line": "#7F77DD", "text": "#3C3489"},
        # External data providers — green
        "lexisnexis":       {"fill": "#F0FDF4", "line": "#166534", "text": "#14532D"},
    }
    NODE_SUBTITLE = {
        "personify":        "Member · relationship",
        "finys":            "Policy · billing · claims",
        "countryway":       "AS400 · CW Conn · Garvin",
        "hubspot":          "Marketing · CRM",
        "ods":              "Analytics · reporting",
        "netsuite":         "Financials · payments",
        "imageright":       "Policy docs · dec pages",
        "nexsure":          "Brokerage management",
        "applied_rater":    "Comparative rater",
        "carrier_portals":  "Travelers, Progressive…",
        "claimant_locator": "Claims contact data",
        "himarly":          "Texting platform",
        "first_call":       "After-hours claims",
        "lexisnexis":       "Prior loss · underwriting",
    }
    # Map each node id to a scatter trace index (built below)
    NODE_TRACE_IDX = {}
    W, H = 2.2, 0.75

    # ── Session state ──────────────────────────────────────────────────────
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    if "selected_team" not in st.session_state:
        st.session_state.selected_team = None

    # ── Team filter UI ─────────────────────────────────────────────────────
    # Build lookup: team name → system ids
    TEAM_DEPS_MAP = {t: set(deps) for t, deps, _ in TEAM_SYSTEM_DEPS}
    # Pain averages: computed live from PERSONAS non-zero scores
    def _avg_pain(persona):
        vals = [v for v in persona["scores"].values() if v > 0]
        return round(sum(vals) / len(vals), 2) if vals else 0.0
    TEAM_PAIN_AVG = {p["role"]: _avg_pain(p) for p in PERSONAS}

    col_filter, col_clear = st.columns([5, 1])
    with col_filter:
        sorted_teams = sorted(TEAM_DEPS_MAP.keys(), key=lambda t: -TEAM_PAIN_AVG.get(t, 0))
        team_options = ["— All systems —"] + sorted_teams
        current_team = st.session_state.selected_team
        default_idx  = team_options.index(current_team) if current_team in team_options else 0
        chosen = st.selectbox(
            "Filter by team",
            options=team_options,
            index=default_idx,
            key="team_selectbox",
            help="Ranked high to low by avg pain score. Highlight only the systems this team depends on.",
            format_func=lambda t: t if t.startswith("—") else f"{t}  [avg {TEAM_PAIN_AVG.get(t, '—')}]",
        )
    with col_clear:
        st.write("")  # vertical align
        if st.button("✕ Clear", key="clear_team_filter", use_container_width=True):
            st.session_state.selected_team = None
            st.session_state.selected_node = None
            st.rerun()

    # Sync selectbox → session state
    new_team = None if chosen.startswith("—") else chosen
    if new_team != st.session_state.selected_team:
        st.session_state.selected_team  = new_team
        st.session_state.selected_node  = None   # reset node selection when team changes
        st.rerun()

    sel_team  = st.session_state.selected_team
    sel_nodes = TEAM_DEPS_MAP.get(sel_team, set()) if sel_team else set()

    sel = st.session_state.selected_node

    # Which nodes are "related" to the selected one?
    def related_nodes(node_id):
        connected = set()
        for src, tgt, _, _ in SYSTEM_EDGES:
            if src == node_id: connected.add(tgt)
            if tgt == node_id: connected.add(src)
        return connected

    related = related_nodes(sel) if sel else set()

    # Active highlight set: team filter takes precedence over node click
    # if both are set, intersect (show team systems + clicked node's neighbours)
    def _is_active(nid):
        if sel_team and sel:
            return nid in sel_nodes or nid == sel or nid in related
        if sel_team:
            return nid in sel_nodes
        if sel:
            return nid == sel or nid in related
        return True  # no filter

    def _edge_active(src, tgt):
        if sel_team and sel:
            team_edge   = src in sel_nodes and tgt in sel_nodes
            node_edge   = src == sel or tgt == sel
            return team_edge or node_edge
        if sel_team:
            return src in sel_nodes and tgt in sel_nodes
        if sel:
            return src == sel or tgt == sel
        return True  # no filter

    # ── Build figure ───────────────────────────────────────────────────────
    shapes, annotations, traces = [], [], []

    # Region outlines
    for label, x0, x1 in [("VAFB core", -0.1, 5.6), ("External / vendor", 6.1, 9.0), ("External data", 8.7, 11.4)]:
        shapes.append(dict(
            type="rect", x0=x0, y0=-5.25, x1=x1, y1=3.3,
            fillcolor="rgba(0,0,0,0)",
            line=dict(color="#e0e0e0", width=1, dash="dot"),
            layer="below",
        ))
        annotations.append(dict(
            x=x0+0.12, y=3.15, text=label, showarrow=False,
            xanchor="left", yanchor="top",
            font=dict(size=11, color="#ccc"),
        ))
    # Brokerage cluster label
    annotations.append(dict(
        x=-0.1, y=-0.9, text="Brokerage (IAS — isolated)", showarrow=False,
        xanchor="left", yanchor="top",
        font=dict(size=10, color="#D85A30"),
    ))
    # Claims vendors cluster label
    annotations.append(dict(
        x=6.1, y=-2.6, text="Claims vendors (unintegrated)", showarrow=False,
        xanchor="left", yanchor="top",
        font=dict(size=10, color="#7F77DD"),
    ))

    # Count how many teams depend on each system
    _team_counts = {}
    for _team, _deps, _hc in TEAM_SYSTEM_DEPS:
        for _sid in _deps:
            _team_counts[_sid] = _team_counts.get(_sid, 0) + 1

    # Per-node dimensions: single-team systems get a smaller box
    def _node_dims(nid):
        count = _team_counts.get(nid, 0)
        if count <= 1:
            return 1.6, 0.55   # small: w, h
        return W, H             # full size

    # Edge traces — highlight connected, dim unconnected
    for src, tgt, lbl, confirmed in SYSTEM_EDGES:
        sw, sh = _node_dims(src)
        tw, th = _node_dims(tgt)
        cx0 = NODE_POS[src][0] + sw / 2
        cy0 = NODE_POS[src][1] + sh / 2
        cx1 = NODE_POS[tgt][0] + tw / 2
        cy1 = NODE_POS[tgt][1] + th / 2

        active = _edge_active(src, tgt)
        no_filter = not sel_team and not sel

        if no_filter or active:
            color   = "#22c55e" if confirmed else "#e53935"
            width   = 3 if active and not no_filter else (2 if confirmed else 1.5)
            opacity = 1.0
        else:
            color   = "#ccc"
            width   = 1
            opacity = 0.18

        dash = "solid" if confirmed else "dot"
        traces.append(go.Scatter(
            x=[cx0, cx1, None], y=[cy0, cy1, None],
            mode="lines",
            line=dict(width=width, color=color, dash=dash),
            opacity=opacity,
            hoverinfo="text", hovertext=lbl,
            showlegend=False,
        ))

    # Node boxes + clickable scatter points
    for nid, (x, y) in NODE_POS.items():
        c = NODE_STYLE[nid]
        nw, nh = _node_dims(nid)

        no_filter = not sel_team and not sel
        active    = _is_active(nid)
        is_sel    = nid == sel
        in_team   = nid in sel_nodes

        if no_filter or active:
            fill         = c["fill"]
            border_color = c["line"]
            border_width = 3.5 if is_sel else (2.5 if in_team and sel_team else 1.5)
            node_opacity = 1.0
        else:
            fill         = "#f5f5f5"
            border_color = "#ddd"
            border_width = 1.0
            node_opacity = 0.18

        shapes.append(dict(
            type="rect", x0=x, y0=y, x1=x+nw, y1=y+nh,
            fillcolor=fill,
            line=dict(color=border_color, width=border_width),
            layer="above",
            opacity=node_opacity,
        ))

        text_color = c["text"] if node_opacity == 1.0 else "#bbb"
        sub_color  = c["line"]  if node_opacity == 1.0 else "#ccc"
        font_size  = 13 if nw >= W else 10
        sub_size   = 10 if nw >= W else 8

        annotations.append(dict(
            x=x+nw/2, y=y+nh*0.68,
            text=f"<b>{SYS_LABEL[nid]}</b>",
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(size=font_size, color=text_color),
        ))
        annotations.append(dict(
            x=x+nw/2, y=y+nh*0.28,
            text=NODE_SUBTITLE[nid],
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(size=sub_size, color=sub_color),
        ))

        # Invisible scatter for click detection — customdata carries node id
        NODE_TRACE_IDX[nid] = len(traces)
        traces.append(go.Scatter(
            x=[x+nw/2], y=[y+nh/2],
            mode="markers",
            marker=dict(size=60 if nw < W else 80, color="rgba(0,0,0,0)"),
            hoverinfo="text",
            hovertext=(
                f"<b>{SYS_LABEL[nid]}</b><br>"
                f"{SYS_LOOKUP[nid]['category']}<br>"
                f"Severity: {SEVERITY_LABEL[SYS_LOOKUP[nid]['severity']]}<br>"
                f"Owner: {SYS_LOOKUP[nid]['owner']}<br>"
                f"Teams depending on this: {_team_counts.get(nid, 0)}"
            ),
            customdata=[nid],
            showlegend=False,
        ))

    # Legend
    traces += [
        go.Scatter(x=[None], y=[None], mode="lines",
                   line=dict(width=2, color="#22c55e", dash="solid"), name="✅ Confirmed"),
        go.Scatter(x=[None], y=[None], mode="lines",
                   line=dict(width=2, color="#e53935", dash="dot"), name="❓ Unconfirmed / gap"),
    ]

    # ── Pain callout badges ───────────────────────────────────────────────
    # When a team is selected: numbered badges appear on that team's systems,
    # ranked 1 = highest pain score descending. Tooltip = the team's actual
    # pain note for that system cell, sourced from data.py PERSONAS.
    # When no team is selected: badges are hidden entirely.

    # Pain data: built live from PERSONAS — score, pain note, workaround per (team, system)
    # Any edit to data.py is automatically reflected here on next Streamlit reload.
    TEAM_SYSTEM_PAIN = {
        (p["role"], sid): {
            "score":      p["scores"].get(sid, 0),
            "pain":       p["notes"].get(sid, {}).get("pain", ""),
            "workaround": p["notes"].get(sid, {}).get("workaround", ""),
        }
        for p in PERSONAS
        for sid in p["scores"]
    }

        # Score → badge color (mirrors heat map palette)
    BADGE_COLORS = {
        4: "#DC2626",   # critical — red
        3: "#EA580C",   # high — orange-red
        2: "#D97706",   # medium — amber
        1: "#CA8A04",   # low — yellow-amber
    }
    BADGE_R = 0.18

    if sel_team:
        # Build ranked list: systems this team has pain scores for, desc by score
        team_pain_entries = [
            (sys_id, data)
            for (team, sys_id), data in TEAM_SYSTEM_PAIN.items()
            if team == sel_team and data["score"] > 0 and sys_id in NODE_POS
        ]
        # Sort descending by score, then stable by node position for ties
        team_pain_entries.sort(key=lambda x: -x[1]["score"])

        # Assign rank numbers (ties get same rank)
        ranked = []
        prev_score = None
        rank = 0
        for sys_id, data in team_pain_entries:
            if data["score"] != prev_score:
                rank += 1
                prev_score = data["score"]
            ranked.append((rank, sys_id, data))

        for rank_num, sys_id, data in ranked:
            ax, ay = NODE_POS[sys_id]
            nw, nh  = _node_dims(sys_id)
            bx = ax + nw
            by = ay + nh
            score   = data["score"]
            pain    = data["pain"] or "No pain note recorded"
            wkaround = data["workaround"]
            tooltip = (
                f"<b>#{rank_num} — Score {score}/4</b><br>"
                f"<b>{SYS_LABEL.get(sys_id, sys_id)}</b> · {sel_team}<br>"
                f"{pain}"
                + (f"<br><i>Workaround: {wkaround}</i>" if wkaround else "")
            )
            col = BADGE_COLORS.get(score, "#DC2626")

            shapes.append(dict(
                type="circle",
                x0=bx - BADGE_R, y0=by - BADGE_R,
                x1=bx + BADGE_R, y1=by + BADGE_R,
                fillcolor=col,
                line=dict(color="white", width=1.5),
                layer="above",
                opacity=1.0,
            ))
            annotations.append(dict(
                x=bx, y=by,
                text=f"<b>{rank_num}</b>",
                showarrow=False,
                xanchor="center", yanchor="middle",
                font=dict(size=10, color="white"),
            ))
            traces.append(go.Scatter(
                x=[bx], y=[by],
                mode="markers",
                marker=dict(size=20, color="rgba(0,0,0,0)"),
                hoverinfo="text",
                hovertext=tooltip,
                showlegend=False,
            ))

    fig_map = go.Figure(data=traces)
    fig_map.update_layout(
        shapes=shapes,
        annotations=annotations,
        height=720,
        margin=dict(l=10, r=10, t=20, b=30),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 11.6]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-5.3, 3.4]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="left", x=0),
        hovermode="closest",
        clickmode="event",
    )

    # ── Capture click events ───────────────────────────────────────────────
    event = st.plotly_chart(
        fig_map,
        use_container_width=True,
        on_select="rerun",
        key="dep_map_chart",
    )

    # Process click: extract node id from customdata
    if event and event.get("selection") and event["selection"].get("points"):
        pt = event["selection"]["points"][0]
        clicked_id = pt.get("customdata")
        if clicked_id and clicked_id in NODE_POS:
            if st.session_state.selected_node == clicked_id:
                st.session_state.selected_node = None  # toggle off
            else:
                st.session_state.selected_node = clicked_id
            st.rerun()

    if sel_team:
        st.caption(f"Showing **{sel_team}** system footprint — click a node to explore its connections · click ✕ Clear to reset")
        avg = TEAM_PAIN_AVG.get(sel_team, "—")
        team_sys_labels = ", ".join(SYS_LABEL.get(s, s) for s in sorted(sel_nodes) if s in SYS_LABEL)
        st.info(
            f"**{sel_team}** · avg pain score **{avg} / 4** · "
            f"depends on: {team_sys_labels}",
            icon="👥",
        )
    elif sel:
        st.caption(f"Showing connections for **{SYS_LABEL[sel]}** — click again to deselect")
    else:
        st.caption("Filter by team above, or click any system node to highlight its connections")

    # ── System detail panel ────────────────────────────────────────────────
    st.divider()
    st.markdown("#### System detail")

    # All nodes on the map, not just SYSTEMS list
    sys_options = list(NODE_POS.keys())
    # If a node was clicked, sync the dropdown to it
    if sel and sel in sys_options:
        default_idx = sys_options.index(sel)
    else:
        default_idx = st.session_state.get("dep_map_sys_select_idx", 0)

    col_sel, _ = st.columns([2, 3])
    with col_sel:
        selected_sys = st.selectbox(
            "Select a system to inspect",
            options=sys_options,
            index=default_idx,
            format_func=lambda x: SYS_LABEL.get(x, x),
            key="dep_map_sys_select",
        )

    # Keep dropdown index in sync for next render
    st.session_state["dep_map_sys_select_idx"] = sys_options.index(selected_sys)

    s   = SYS_LOOKUP[selected_sys]
    sev = s["severity"]
    ppl = SYSTEM_PEOPLE.get(selected_sys, {"enter": [], "manage": [], "consume": []})

    col_meta, col_flows = st.columns([2, 3], gap="large")

    with col_meta:
        st.markdown(f"**{SEVERITY_ICON[sev]} {s['name']}**")
        st.caption(f"{s['category']}  \nOwner: {s['owner']}  \nSeverity: `{SEVERITY_LABEL[sev]}`")
        st.divider()
        connected_out = [(tgt, lbl, conf) for src, tgt, lbl, conf in SYSTEM_EDGES if src == selected_sys]
        connected_in  = [(src, lbl, conf) for src, tgt, lbl, conf in SYSTEM_EDGES if tgt == selected_sys]
        if connected_in:
            st.markdown("**⬆️ Receives from**")
            for src, lbl, conf in connected_in:
                icon = "✅" if conf else "❓"
                st.write(f"{icon} {SYS_LABEL.get(src, src)} — *{lbl}*")
        if connected_out:
            st.markdown("**⬇️ Feeds into**")
            for tgt, lbl, conf in connected_out:
                icon = "✅" if conf else "❓"
                st.write(f"{icon} {SYS_LABEL.get(tgt, tgt)} — *{lbl}*")

    with col_flows:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Enter**")
            for name, role in ppl["enter"]:
                st.markdown(f"**{name}**  \n{role}")
        with c2:
            st.markdown("**Manage**")
            for name, role in ppl["manage"]:
                st.markdown(f"**{name}**  \n{role}")
        with c3:
            st.markdown("**Consume**")
            for name, role in ppl["consume"]:
                st.markdown(f"**{name}**  \n{role}")
        st.divider()
        st.markdown("**⚠️ Key gaps**")
        for g in s["known_gaps"]:
            st.write(f"• {g}")
        st.markdown("**🔧 Workarounds**")
        for w in s["workarounds"]:
            st.write(f"• {w}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: SYSTEM → TEAM IMPACT
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("#### Team Dependency Heatmap")
        st.caption("How many systems each team depends on, weighted by severity")

        import plotly.express as px
        import pandas as pd

        # Build matrix: rows = teams, cols = systems
        sys_ids   = [s["id"] for s in SYSTEMS]
        sys_names = [SYS_LABEL[i] for i in sys_ids]
        team_names = [t[0] for t in TEAM_SYSTEM_DEPS]

        matrix = []
        for team, deps, hc in TEAM_SYSTEM_DEPS:
            row = []
            for sid in sys_ids:
                if sid in deps:
                    sev = SYS_LOOKUP[sid]["severity"]
                    row.append(sev)
                else:
                    row.append(0)
            matrix.append(row)

        df_heat = pd.DataFrame(matrix, index=team_names, columns=sys_names)

        fig2 = go.Figure(go.Heatmap(
            z=df_heat.values,
            x=sys_names,
            y=team_names,
            colorscale=[
                [0,   "#f5f5f5"],
                [0.2, "#fff9c4"],
                [0.4, "#ffcc02"],
                [0.6, "#ff9800"],
                [0.8, "#f44336"],
                [1.0, "#b71c1c"],
            ],
            zmin=0, zmax=5,
            text=[[str(v) if v > 0 else "" for v in row] for row in df_heat.values],
            texttemplate="%{text}",
            hovertemplate="<b>%{y}</b> depends on <b>%{x}</b><br>Severity: %{z}<extra></extra>",
            showscale=True,
            colorbar=dict(
                title="Severity",
                tickvals=[0, 1, 2, 3, 4, 5],
                ticktext=["None", "Low", "Minor", "Moderate", "High", "Critical"],
            ),
        ))

        fig2.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(side="top", tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig2, use_container_width=True)

    with right:
        st.markdown("#### Team Impact Detail")
        selected_team = st.selectbox(
            "Select a team",
            options=[t[0] for t in TEAM_SYSTEM_DEPS],
        )

        team_data = next(t for t in TEAM_SYSTEM_DEPS if t[0] == selected_team)
        _, deps, hc = team_data

        st.markdown(f"**{selected_team}**")
        st.caption(f"~{hc} people · depends on {len(deps)} system(s)")
        st.divider()

        total_sev = sum(SYS_LOOKUP[d]["severity"] for d in deps)
        avg_sev   = total_sev / len(deps) if deps else 0
        max_sev   = max((SYS_LOOKUP[d]["severity"] for d in deps), default=0)

        c1, c2 = st.columns(2)
        c1.metric("Systems depended on", len(deps))
        c2.metric("Max severity exposure", f"{SEVERITY_LABEL[max_sev]}")

        st.markdown("**Systems this team relies on**")
        for d in sorted(deps, key=lambda x: SYS_LOOKUP[x]["severity"], reverse=True):
            s   = SYS_LOOKUP[d]
            sev = s["severity"]
            st.markdown(
                f"{SEVERITY_ICON[sev]} **{SYS_LABEL[d]}** ({SEVERITY_LABEL[sev]})  \n"
                f"<small>Owner: {s['owner']}</small>",
                unsafe_allow_html=True,
            )
            # Show gaps relevant to this team
            for g in s["known_gaps"][:2]:
                st.write(f"  ↳ {g}")

        st.divider()
        st.markdown("**Workarounds this team likely uses**")
        for chain in WORKAROUND_CHAINS:
            if selected_team in chain["teams_affected"] and chain["root_system"] in deps:
                st.write(f"🔧 {chain['workaround']}")
                st.caption(f"Root cause: {SYS_LABEL[chain['root_system']]} — {chain['root_gap']}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4: ACT 1 — ACQUISITION FLOW
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### Current-State Member & Customer Acquisition Flow")
    st.caption("Solid = working · Orange = degraded · Red dashed = broken/missing · Gray dashed = manual · Click a node to explore connections")

    # ── Node definitions ─────────────────────────────────────────────────
    # (id, label, subtitle, x_center, y_center, w, h, fill, line, text_color)
    # Layout: 4 rows top-to-bottom. x/y in data coords (0..10 × 0..10)
    ACT1_NODES = [
        # Entry channels — y=8.5
        ("agent",         "Agent / MSS",       "Quote · bind · enroll",          1.2,  8.5, 2.0, 0.75, "#E1F5EE", "#0F6E56", "#085041"),
        ("web",           "VFB.com quote",     "Self-service quote",              3.8,  8.5, 2.0, 0.75, "#E1F5EE", "#0F6E56", "#085041"),
        ("product_buyer", "Product buyer",     "Enters member ID",                6.2,  8.5, 2.0, 0.75, "#E1F5EE", "#0F6E56", "#085041"),
        ("event_buyer",   "Event buyer",       "Ticket purchase",                 8.8,  8.5, 2.0, 0.75, "#E1F5EE", "#0F6E56", "#085041"),
        # Core systems — y=5.5
        ("personify",     "Personify",         "Member profile · billing",        2.0,  5.5, 2.4, 0.85, "#E6F1FB", "#185FA5", "#0C447C"),
        ("finys",         "FINYS",             "Quotes · policies · claims",      5.0,  5.5, 2.4, 0.85, "#FAECE7", "#993C1D", "#712B13"),
        ("netsuite",      "NetSuite",          "Products · payments",             8.0,  5.5, 2.4, 0.85, "#EEEDFE", "#534AB7", "#3C3489"),
        # Supporting systems — y=2.5
        ("ods",           "ODS",               "Reporting layer",                 1.2,  2.5, 2.0, 0.75, "#F1EFE8", "#5F5E5A", "#2C2C2A"),
        ("etix",          "Etix",              "Event ticketing",                 3.8,  2.5, 2.0, 0.75, "#F1EFE8", "#5F5E5A", "#2C2C2A"),
        ("agtech",      "Agtech",          "Grain operations",                6.2,  2.5, 2.0, 0.75, "#F1EFE8", "#5F5E5A", "#2C2C2A"),
        ("excel",         "Excel / manual",    "Shadow workarounds",              8.8,  2.5, 2.0, 0.75, "#F1EFE8", "#5F5E5A", "#2C2C2A"),
    ]

    # ── Edge definitions ─────────────────────────────────────────────────
    ACT1_EDGES = [
        ("agent",         "personify",  "Creates / updates member profile",       "working"),
        ("web",           "finys",      "Quote + customer info",                  "working"),
        ("product_buyer", "netsuite",   "Purchase + member ID entered",           "working"),
        ("event_buyer",   "etix",       "Ticket purchase",                        "working"),
        ("personify",     "finys",      "Real-time search — DOB loss bug",        "degraded"),
        ("personify",     "finys",      "Nightly sync — no retry",                "broken"),
        ("finys",         "ods",        "Nightly policy / quote feed",            "working"),
        ("netsuite",      "personify",  "Missing: no membership validation",      "broken"),
        ("etix",          "personify",  "Missing: no real-time verification",     "broken"),
        ("agtech",      "personify",  "Isolated: no corporate member tie",      "broken"),
        ("agtech",      "finys",      "Isolated: no insurance / customer tie",  "broken"),
        ("agent",         "finys",      "Manual re-entry when lookup fails",      "manual"),
        ("etix",          "excel",      "Manual export / reconcile",              "manual"),
    ]

    A1_EDGE_STYLE = {
        "working":  {"color": "#22c55e", "width": 2.5, "dash": "solid",   "label": "✅ Working"},
        "degraded": {"color": "#f59e0b", "width": 3.5, "dash": "solid",   "label": "⚠️ Degraded"},
        "broken":   {"color": "#e53935", "width": 2.0, "dash": "dot",     "label": "❌ Broken / missing"},
        "manual":   {"color": "#9ca3af", "width": 1.5, "dash": "dashdot", "label": "🔧 Manual bridge"},
    }

    NODE_DETAIL_A1 = {
        "agent":         "County agents and MSS create member profiles in Personify and enter policies into FINYS. When the Personify lookup fails, agents hand-type all customer data directly into FINYS — creating duplicate records that may never be reconciled.",
        "web":           "VFB.com feeds quote and customer info directly into FINYS in real time. Lead data should flow onward to ODS dashboards but the linkage is unconfirmed.",
        "product_buyer": "Product buyers enter a member ID in NetSuite at point of purchase, but NetSuite cannot validate that ID against Personify in real time. Any ID is accepted on trust.",
        "event_buyer":   "Event buyers purchase tickets through Etix. Member discounts cannot be verified in real time — post-event manual exports are the only reconciliation mechanism.",
        "personify":     "Primary identity record for all VAFB members. ~100k associate members have no policy tie-back. 70% of active members missing DOB. Placeholder IDs (999999/000000) permanently orphan policies.",
        "finys":         "Primary insurance processing system for quotes, policies, billing, and claims. Receives data from agents, web, and Personify. Feeds ODS nightly. No direct integration with brokerage or grain.",
        "netsuite":      "Products division hub for inventory, pricing, and payment processing. No integration with Personify for membership validation — any ID accepted on trust.",
        "ods":           "Operational Data Store — reporting layer fed by FINYS nightly. Data trust issues due to upstream Personify ↔ FINYS identity gaps and hidden filters causing $100K+ discrepancies.",
        "etix":          "Third-party event ticketing platform. No real-time connection to Personify for membership verification. Post-event reconciliation requires manual CSV exports.",
        "agtech":      "Grain merchandising system — fully siloed. No integration with Personify or FINYS. Grain customers cannot be identified as Farm Bureau members. ~40 hrs/week manual data entry burden.",
        "excel":         "Shadow spreadsheets maintained across multiple teams: demographics filtering, agent prospect pipelines, Etix reconciliation exports. Prevalent across every interview group.",
    }

    A1_EDGE_ICONS = {"working": "✅", "degraded": "⚠️", "broken": "❌", "manual": "🔧"}

    # ── Session state ─────────────────────────────────────────────────────
    if "act1_selected" not in st.session_state:
        st.session_state.act1_selected = None
    act1_sel = st.session_state.act1_selected

    # Build lookup dicts
    NODE_BOX  = {n[0]: n for n in ACT1_NODES}
    NODE_LABEL = {n[0]: n[1] for n in ACT1_NODES}

    def a1_connected(nid):
        c = set()
        for s, t, *_ in ACT1_EDGES:
            if s == nid: c.add(t)
            if t == nid: c.add(s)
        return c

    a1_related = a1_connected(act1_sel) if act1_sel else set()

    # ── Build figure ──────────────────────────────────────────────────────
    shapes_a1, annots_a1, traces_a1 = [], [], []

    # Tier label annotations
    for y_tier, lbl_tier in [(8.5, "Entry channels"), (5.5, "Core systems"), (2.5, "Supporting systems")]:
        annots_a1.append(dict(
            x=-0.1, y=y_tier + 0.55, text=lbl_tier, showarrow=False,
            xanchor="left", yanchor="bottom",
            font=dict(size=11, color="#9ca3af"),
        ))

    # Tier separator lines
    for y_sep in [4.3, 7.3]:
        shapes_a1.append(dict(
            type="line", x0=-0.1, x1=10.1, y0=y_sep, y1=y_sep,
            line=dict(color="#e5e7eb", width=0.8, dash="dot"), layer="below",
        ))

    import numpy as np

    def bezier_curve(p0, p1, p2, p3, n=40):
        """Cubic Bézier from p0 to p3 with control points p1, p2."""
        t = np.linspace(0, 1, n)
        x = ((1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] +
             3*(1-t)*t**2 * p2[0] + t**3 * p3[0])
        y = ((1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] +
             3*(1-t)*t**2 * p2[1] + t**3 * p3[1])
        return list(x) + [None], list(y) + [None]

    # Per-edge unique lateral offsets so parallel edges fan out
    # Pre-count how many edges share each node-pair
    pair_counter = {}
    for src, tgt, lbl, etype in ACT1_EDGES:
        pk = (min(src, tgt), max(src, tgt))
        pair_counter[pk] = pair_counter.get(pk, 0) + 1

    pair_idx = {}
    for edge_i, (src, tgt, lbl, etype) in enumerate(ACT1_EDGES):
        ns = NODE_BOX[src]
        nt = NODE_BOX[tgt]
        es = A1_EDGE_STYLE[etype]

        sx, sy = ns[3], ns[4]
        tx, ty = nt[3], nt[4]
        sw, sh = ns[5], ns[6]
        tw, th = nt[5], nt[6]

        hover_txt = (f"<b>{NODE_LABEL[src]}</b> → <b>{NODE_LABEL[tgt]}</b><br>"
                     f"{lbl}<br><i>{es['label']}</i>")

        is_selected_edge = act1_sel and (src == act1_sel or tgt == act1_sel)
        opacity = 1.0 if (act1_sel is None or is_selected_edge) else 0.08

        pk = (min(src, tgt), max(src, tgt))
        n_parallel = pair_counter.get(pk, 1)
        idx = pair_idx.get(pk, 0)
        pair_idx[pk] = idx + 1

        # Fan offset: spread parallel edges symmetrically around centre
        if n_parallel > 1:
            fan = (idx - (n_parallel - 1) / 2) * 0.22
        else:
            fan = 0.0

        same_tier = abs(sy - ty) < 1.0

        if same_tier:
            # Same-tier: cubic Bézier arcing downward between the tiers
            # Exit bottom of source, enter bottom of target, control points dip down
            if sy >= 5.0:
                dip = 3.8 - idx * 0.35   # between core and supporting
            else:
                dip = 1.5 - idx * 0.25   # below supporting row

            p0 = (sx + fan, sy - sh / 2)
            p3 = (tx + fan, ty - th / 2)
            p1 = (sx + fan, dip)
            p2 = (tx + fan, dip)
            cx_arr, cy_arr = sx + fan, dip + 0.05  # near target for arrowhead direction

        else:
            # Cross-tier: cubic Bézier, exit bottom of source, enter top of target
            # Control points extend vertically from each endpoint — gives S-curve
            p0 = (sx + fan, sy - sh / 2)
            p3 = (tx + fan, ty + th / 2)
            dy = abs(sy - ty)
            ctrl_stretch = dy * 0.55
            p1 = (sx + fan, sy - sh / 2 - ctrl_stretch)
            p2 = (tx + fan, ty + th / 2 + ctrl_stretch)
            cx_arr = tx + fan
            cy_arr = ty + th / 2 + 0.12

        path_x, path_y = bezier_curve(p0, p1, p2, p3)

        traces_a1.append(go.Scatter(
            x=path_x, y=path_y,
            mode="lines",
            line=dict(color=es["color"], width=es["width"], dash=es["dash"]),
            opacity=opacity,
            hoverinfo="text",
            hovertext=hover_txt,
            hoverlabel=dict(bgcolor="white", font_size=12),
            showlegend=False,
        ))

        # Arrowhead: use pixel-offset tangent from the last two curve points
        # path_x[-2]/path_y[-2] = last real point (= p3)
        # path_x[-3]/path_y[-3] = second-to-last real point
        ex, ey = path_x[-2], path_y[-2]   # arrowhead tip (= p3)
        bx, by = path_x[-3], path_y[-3]   # point just before tip

        # dx/dy gives the incoming direction; scale to a fixed pixel length
        import math
        ddx = ex - bx
        ddy = ey - by
        dlen = math.sqrt(ddx**2 + ddy**2) or 1
        # ax/ay are pixel offsets FROM the tip BACK along the tangent (20px)
        px_ax = -(ddx / dlen) * 20
        px_ay = -(ddy / dlen) * 20

        annots_a1.append(dict(
            x=ex, y=ey,
            ax=px_ax, ay=px_ay,
            xref="x", yref="y",
            axref="pixel", ayref="pixel",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.0,
            arrowwidth=max(es["width"] * 0.9, 1.8),
            arrowcolor=es["color"],
            opacity=opacity,
            text="",
        ))

    # Legend traces
    for etype, es in A1_EDGE_STYLE.items():
        traces_a1.append(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=es["color"], width=es["width"], dash=es["dash"]),
            name=es["label"], showlegend=True,
        ))

    # Node boxes
    for nid, label, sub, cx, cy, w, h, fill, line_col, text_col in ACT1_NODES:
        x0, x1 = cx - w / 2, cx + w / 2
        y0, y1 = cy - h / 2, cy + h / 2

        if act1_sel is None:
            node_opacity = 1.0
            bw = 1.5
            bc = line_col
        elif nid == act1_sel:
            node_opacity = 1.0
            bw = 3.5
            bc = line_col
        elif nid in a1_related:
            node_opacity = 1.0
            bw = 2.5
            bc = line_col
        else:
            node_opacity = 0.2
            bw = 1.0
            bc = "#ddd"
            fill = "#f5f5f5"
            text_col = "#bbb"

        shapes_a1.append(dict(
            type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=fill,
            line=dict(color=bc, width=bw),
            opacity=node_opacity,
            layer="above",
        ))

        annots_a1.append(dict(
            x=cx, y=cy + h * 0.15,
            text=f"<b>{label}</b>",
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(size=13, color=text_col),
        ))
        annots_a1.append(dict(
            x=cx, y=cy - h * 0.2,
            text=sub,
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(size=10, color=line_col if node_opacity == 1.0 else "#ccc"),
        ))

        # Invisible scatter for click
        traces_a1.append(go.Scatter(
            x=[cx], y=[cy],
            mode="markers",
            marker=dict(size=max(w, h) * 40, color="rgba(0,0,0,0)"),
            hoverinfo="text",
            hovertext=f"<b>{label}</b><br>{sub}",
            customdata=[nid],
            showlegend=False,
        ))

    fig_a1 = go.Figure(data=traces_a1)
    fig_a1.update_layout(
        shapes=shapes_a1,
        annotations=annots_a1,
        height=640,
        margin=dict(l=10, r=10, t=10, b=50),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 10.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.6, 10.0]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="left", x=0,
                    font=dict(size=11)),
        hovermode="closest",
        clickmode="event",
    )

    # ── Render + capture click ────────────────────────────────────────────
    event_a1 = st.plotly_chart(fig_a1, use_container_width=True, on_select="rerun", key="act1_flow_chart")

    if event_a1 and event_a1.get("selection") and event_a1["selection"].get("points"):
        pt = event_a1["selection"]["points"][0]
        clicked = pt.get("customdata")
        if clicked and clicked in NODE_BOX:
            if st.session_state.act1_selected == clicked:
                st.session_state.act1_selected = None
            else:
                st.session_state.act1_selected = clicked
            st.rerun()

    if act1_sel:
        st.caption(f"Showing connections for **{NODE_LABEL[act1_sel]}** — click again to deselect")
    else:
        st.caption("Click any node to highlight its connections")

    # ── Detail panel ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### Node detail")

    if act1_sel:
        node_meta = NODE_BOX[act1_sel]
        nid, label, sub, cx, cy, w, h, fill, line_col, text_col = node_meta
        flows_out = [(tgt, lbl, et) for src, tgt, lbl, et in ACT1_EDGES if src == act1_sel]
        flows_in  = [(src, lbl, et) for src, tgt, lbl, et in ACT1_EDGES if tgt == act1_sel]

        col_info, col_out, col_in = st.columns([2, 1.5, 1.5], gap="large")
        with col_info:
            st.markdown(f"**{label}**")
            st.caption(sub)
            st.divider()
            st.write(NODE_DETAIL_A1.get(act1_sel, "—"))
        with col_out:
            st.markdown("**⬇️ Sends data to**")
            if flows_out:
                for tgt, lbl, et in flows_out:
                    icon = A1_EDGE_ICONS[et]
                    st.write(f"{icon} **{NODE_LABEL.get(tgt, tgt)}**")
                    st.caption(f"  {lbl}")
            else:
                st.write("*No outbound flows mapped*")
        with col_in:
            st.markdown("**⬆️ Receives data from**")
            if flows_in:
                for src, lbl, et in flows_in:
                    icon = A1_EDGE_ICONS[et]
                    st.write(f"{icon} **{NODE_LABEL.get(src, src)}**")
                    st.caption(f"  {lbl}")
            else:
                st.write("*No inbound flows mapped*")

        if st.button("✕ Deselect", key="act1_deselect"):
            st.session_state.act1_selected = None
            st.rerun()
    else:
        st.markdown(
            "<div style='background:white;border:1px dashed #E5E5E0;border-radius:10px;"
            "padding:14px 18px;text-align:center;color:#9CA3AF;font-size:12px;'>"
            "Click any node to see its inbound and outbound data flows</div>",
            unsafe_allow_html=True,
        )


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ Internal draft — validate with Jake / Kim / Karen in workshops before sharing externally.")