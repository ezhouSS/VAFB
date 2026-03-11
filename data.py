# =============================================================================
# VFB PAIN HEATMAP — DATA FILE
# =============================================================================
# This is the ONLY file you need to edit between interviews.
# Update scores (0–4) and notes after each stakeholder conversation.
#
# SCORE GUIDE:
#   0 = None      (no pain observed)
#   1 = Low       (minor friction, not blocking)
#   2 = Medium    (noticeable pain, workarounds exist)
#   3 = High      (significant pain, impacts productivity)
#   4 = Critical  (blocking, major data/process gap)
# =============================================================================

# ── JOURNEY STAGES ────────────────────────────────────────────────────────────
# Add, remove, or rename stages here. The grid will update automatically.
STAGES = [
    {"id": "aware",    "label": "Aware",            "desc": "Member/customer first learns about VFB"},
    {"id": "join",     "label": "Join / Buy",        "desc": "Joins as member or purchases a policy"},
    {"id": "inforce",  "label": "Policy in Force",   "desc": "Active relationship — ongoing management"},
    {"id": "service",  "label": "Service Event",     "desc": "Claim, change request, or support interaction"},
    {"id": "renew",    "label": "Renewal / Expand",  "desc": "Policy renewal or cross-sell opportunity"},
]

# ── PERSONAS ──────────────────────────────────────────────────────────────────
# Each persona has:
#   - id:       unique key (no spaces)
#   - role:     display name
#   - subtitle: name + title
#   - system:   which system they primarily use
#   - color:    hex color for the row label
#   - is_emma:  True = highlight as your row (data engineer view)
#   - status:   "hypothesis" = pre-interview | "validated" = post-interview
#   - scores:   pain score per stage id (0–4)
#   - notes:    detail per stage — pain, workaround, data_gap
#               Set any field to "" if not yet known.
# =============================================================================

PERSONAS = [

    # ── DATA & SYSTEMS (Emma) ─────────────────────────────────────────────────
    {
        "id": "data",
        "role": "Data & Systems",
        "subtitle": "Emma — Data Engineer / Governance",
        "system": "Both",
        "color": "#0D9488",
        "is_emma": True,
        "status": "hypothesis",   # change to "validated" after you confirm with Patrick + Jenny
        "scores": {
            "aware":   2,
            "join":    4,
            "inforce": 4,
            "service": 3,
            "renew":   3,
        },
        "notes": {
            "aware": {
                "pain":       "No unified data source for prospect tracking",
                "workaround": "—",
                "data_gap":   "Prospect data lives in spreadsheets, not Finys or Personify",
            },
            "join": {
                "pain":       "No shared member/policyholder ID between Finys and Personify",
                "workaround": "Manual name + address matching",
                "data_gap":   "CRITICAL: identity bridge does not exist — root cause of most downstream pain",
            },
            "inforce": {
                "pain":       "No system of record — Finys and Personify hold conflicting member data",
                "workaround": "Staff manually reconcile on case-by-case basis",
                "data_gap":   "No master data management process defined at VFB",
            },
            "service": {
                "pain":       "Claims data in Finys not visible to Personify relationship managers",
                "workaround": "Phone calls between departments",
                "data_gap":   "No real-time integration between claims and CRM layer",
            },
            "renew": {
                "pain":       "Renewal data in Finys not triggering outreach in Personify or CRM",
                "workaround": "Agent spreadsheets",
                "data_gap":   "No event-driven data pipeline for renewal triggers",
            },
        },
    },

    # ── RAY LEONARD — Insurance Agent ─────────────────────────────────────────
    {
        "id": "ray",
        "role": "Ray Leonard",
        "subtitle": "Insurance Agent",
        "system": "Finys",
        "color": "#2563EB",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   1,
            "join":    3,
            "inforce": 3,
            "service": 2,
            "renew":   4,
        },
        "notes": {
            "aware": {
                "pain":       "Limited visibility into which Personify members haven't bought a policy",
                "workaround": "Relies on referrals and county office walk-ins",
                "data_gap":   "No prospect pipeline from Personify member list into agent view",
            },
            "join": {
                "pain":       "Must open Finys and Personify separately to get full member picture at point of sale",
                "workaround": "Keeps browser tabs open side-by-side",
                "data_gap":   "No unified view at point of sale",
            },
            "inforce": {
                "pain":       "No proactive alerts when a member's situation changes (new vehicle, new property)",
                "workaround": "Relies on member calling in",
                "data_gap":   "No event triggers from Personify or Finys to agent workflow",
            },
            "service": {
                "pain":       "Has to re-enter information already in Finys when logging a service interaction",
                "workaround": "Accepts duplicate data entry",
                "data_gap":   "No CRM layer on top of Finys service module",
            },
            "renew": {
                "pain":       "No automated renewal reminder workflow — manually tracks in spreadsheet",
                "workaround": "Personal Excel tracker maintained outside any system",
                "data_gap":   "Renewal dates in Finys not exposed to any CRM or workflow tool",
            },
        },
    },

    # ── BOB BROWN — Relationship Manager ──────────────────────────────────────
    {
        "id": "bob",
        "role": "Bob Brown",
        "subtitle": "Relationship Manager",
        "system": "Personify",
        "color": "#16A34A",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   2,
            "join":    2,
            "inforce": 3,
            "service": 4,
            "renew":   3,
        },
        "notes": {
            "aware": {
                "pain":       "Can't see which members are also policyholders vs. members-only",
                "workaround": "Asks colleagues or checks Finys separately",
                "data_gap":   "Member ↔ policyholder linkage not surfaced in Personify",
            },
            "join": {
                "pain":       "No notification when a member converts to a policyholder",
                "workaround": "Finds out through agent conversation",
                "data_gap":   "No event fired from Finys to Personify on policy issuance",
            },
            "inforce": {
                "pain":       "Can't see policy status, coverage gaps, or renewal dates in Personify",
                "workaround": "Calls Jenny or Ray to look it up in Finys",
                "data_gap":   "Policy data not surfaced in member relationship view",
            },
            "service": {
                "pain":       "No visibility into open claims — finds out member is in distress after the fact",
                "workaround": "Relies on member calling him directly",
                "data_gap":   "Claims data completely siloed in Finys — no feed to Personify",
            },
            "renew": {
                "pain":       "Can't proactively reach out ahead of renewal — doesn't know when renewals are due",
                "workaround": "Relies on agent to loop him in",
                "data_gap":   "Renewal trigger not shared with relationship management side",
            },
        },
    },

    # ── JASON — Sales Enablement ───────────────────────────────────────────────
    {
        "id": "jason",
        "role": "Jason",
        "subtitle": "Sales Enablement",
        "system": "Both",
        "color": "#7C3AED",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   3,
            "join":    3,
            "inforce": 2,
            "service": 1,
            "renew":   3,
        },
        "notes": {
            "aware": {
                "pain":       "Pipeline data is stale — weekly exports mean leads are 5–7 days old",
                "workaround": "Manual weekly export from Personify",
                "data_gap":   "No real-time pipeline feed from either system",
            },
            "join": {
                "pain":       "No visibility into conversion rate from member to policyholder",
                "workaround": "Manual count from two separate reports",
                "data_gap":   "No joined metric bridging Finys and Personify conversion data",
            },
            "inforce": {
                "pain":       "Hard to identify cross-sell opportunities for existing policyholders",
                "workaround": "Ray manually reviews his own book of business",
                "data_gap":   "No propensity scoring or next-best-product logic",
            },
            "service": {
                "pain":       "Minimal involvement in service events",
                "workaround": "—",
                "data_gap":   "—",
            },
            "renew": {
                "pain":       "No consolidated view of renewal pipeline across all agents",
                "workaround": "Collects spreadsheets from each agent weekly",
                "data_gap":   "Renewal data fragmented per agent — no rollup in Finys or Personify",
            },
        },
    },

    # ── BILL — VP Marketing & Sales ───────────────────────────────────────────
    {
        "id": "bill",
        "role": "Bill",
        "subtitle": "VP Marketing & Sales",
        "system": "Both",
        "color": "#C8A84B",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   4,
            "join":    3,
            "inforce": 2,
            "service": 1,
            "renew":   3,
        },
        "notes": {
            "aware": {
                "pain":       "Campaign lists from Personify exports — always stale, no targeting by policy status",
                "workaround": "Weekly manual export, filtered in Excel",
                "data_gap":   "No real-time segment combining member + policyholder data",
            },
            "join": {
                "pain":       "No closed-loop reporting from marketing campaign to policy conversion",
                "workaround": "Estimates attribution manually",
                "data_gap":   "No campaign → conversion tracking across Personify and Finys",
            },
            "inforce": {
                "pain":       "Hard to measure member engagement vs. policy depth",
                "workaround": "Separate reporting from each system, joined in Excel",
                "data_gap":   "No unified member value or engagement score",
            },
            "service": {
                "pain":       "Limited marketing involvement in service journeys",
                "workaround": "—",
                "data_gap":   "—",
            },
            "renew": {
                "pain":       "Renewal campaigns sent without knowing which members are already in renewal workflow with agent",
                "workaround": "Accepts duplication and noise in campaigns",
                "data_gap":   "No signal from Finys renewal status to suppress or personalize Personify campaigns",
            },
        },
    },

    # ── KAREN — Director of Business Solutions ────────────────────────────────
    {
        "id": "karen",
        "role": "Karen",
        "subtitle": "Dir. Business Solutions",
        "system": "Personify",
        "color": "#1A5C38",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   1,
            "join":    3,
            "inforce": 4,
            "service": 2,
            "renew":   2,
        },
        "notes": {
            "aware": {
                "pain":       "Limited visibility into prospect pipeline",
                "workaround": "—",
                "data_gap":   "—",
            },
            "join": {
                "pain":       "New member onboarding not connected to insurance enrollment — two separate workflows",
                "workaround": "Manual handoff between membership and insurance teams",
                "data_gap":   "No integrated onboarding flow bridging Personify and Finys",
            },
            "inforce": {
                "pain":       "Personify member records and Finys policyholder records frequently out of sync (address, name, status)",
                "workaround": "Periodic manual reconciliation — time-consuming",
                "data_gap":   "No automated sync — critical data governance gap requiring system-of-record decision",
            },
            "service": {
                "pain":       "Business solutions team not always looped in on complex service events",
                "workaround": "Relies on escalation calls",
                "data_gap":   "No workflow routing from Finys service events to Personify",
            },
            "renew": {
                "pain":       "Renewal reporting requires pulling from both systems and joining manually",
                "workaround": "Analyst spends significant time on reconciliation",
                "data_gap":   "No consolidated renewal report across both systems",
            },
        },
    },

    # ── JENNY GLEN — CRM Developer ────────────────────────────────────────────
    {
        "id": "jenny",
        "role": "Jenny Glen",
        "subtitle": "CRM Developer",
        "system": "Finys",
        "color": "#EA580C",
        "is_emma": False,
        "status": "hypothesis",
        "scores": {
            "aware":   0,
            "join":    2,
            "inforce": 3,
            "service": 2,
            "renew":   3,
        },
        "notes": {
            "aware": {
                "pain":       "—",
                "workaround": "—",
                "data_gap":   "—",
            },
            "join": {
                "pain":       "No API for Finys — data sync requires scheduled batch jobs, causing latency",
                "workaround": "Batch ETL runs nightly",
                "data_gap":   "Real-time integration not currently possible without significant API development",
            },
            "inforce": {
                "pain":       "CRM customization requests backlogged — Finys configuration changes require significant dev effort",
                "workaround": "Workarounds built outside the system",
                "data_gap":   "Technical debt limiting ability to expose data to a new CRM layer",
            },
            "service": {
                "pain":       "Service event data not structured in a way that's easy to expose to external systems",
                "workaround": "Custom queries on request",
                "data_gap":   "No standardized data contract for service event feed",
            },
            "renew": {
                "pain":       "Renewal workflow logic is embedded in Finys — hard to extract or trigger external processes",
                "workaround": "Manual notification scripts",
                "data_gap":   "Renewal event not published as a data event — no pub/sub pattern exists",
            },
        },
    },

]

# ── HEAT COLOR SCALE ──────────────────────────────────────────────────────────
# Customize score → color mapping here.
# bg = cell background, text = text color, dot = indicator dot color
HEAT_COLORS = {
    0: {"bg": "#F8FAF8", "text": "#9CA3AF", "dot": "#D1D5DB", "label": "None"},
    1: {"bg": "#FEF9C3", "text": "#854D0E", "dot": "#FCD34D", "label": "Low"},
    2: {"bg": "#FED7AA", "text": "#9A3412", "dot": "#FB923C", "label": "Medium"},
    3: {"bg": "#FECACA", "text": "#7F1D1D", "dot": "#F87171", "label": "High"},
    4: {"bg": "#FCA5A5", "text": "#450A0A", "dot": "#DC2626", "label": "Critical"},
}

# ── APP METADATA ──────────────────────────────────────────────────────────────
APP_TITLE       = "VFB Current-State Pain Heat Map"
APP_SUBTITLE    = "CRM Transformation · Sprint 1 & 2 · Data Engineer View"
APP_CLIENT      = "Virginia Farm Bureau"
EMMA_LABEL      = "Emma"   # your name — appears in the YOU badge and data gap column

# ── KEY OBSERVATIONS ──────────────────────────────────────────────────────────
# Edit these from the dashboard (Edit Mode → click ✏️ next to any observation)
# or directly here. Add or remove items freely — the list updates automatically.
OBSERVATIONS = [
    "Example observations here",
]
