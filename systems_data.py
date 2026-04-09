"""
VAFB System Map Data Layer
Drop this into data.py or import it as a module.
Each system entry captures: teams, headcount, functions, gaps, workarounds, integrations, severity.
Severity scale: 1 (low friction) - 5 (critical gap)
"""

SYSTEMS = [
    {
        "id": "finys",
        "name": "Finys",
        "category": "Policy, Billing & Claims",
        "owner": "Catherine Reid / Jenny Glenn",
        "teams_using": [
            "Underwriting (Scott Denoon, Ed Baumgartner, Ben Ashby)",
            "Claims (Laurie Gannon, David Jewell)",
            "Policy Services",
            "Countryway Insurance (partial migration in progress)",
        ],
        "approx_headcount": 40,
        "core_functions": [
            "Policy administration",
            "Billing",
            "Claims processing",
        ],
        "known_gaps": [
            "No clean linkage to Personify member records — no universal member ID",
            "Countryway mid-migration creates parallel operational complexity",
            "Functionality built but not signed off before going to production (delivery governance gap)",
            "Incomplete product dimensions blocking downstream automation",
        ],
        "workarounds": [
            "Manual reconciliation between Finys and Personify to match member/policyholder records",
            "Staff maintain shadow spreadsheets to track policy status during Countryway migration",
            "Claims and underwriting staff toggle between Finys and ImageRight for document context",
        ],
        "integrations": {
            "confirmed": ["ImageRight (document management)", "ODS (reporting extract)"],
            "unconfirmed": ["Personify (no confirmed linkage)", "Countryway AS400 (partial, mid-migration)"],
        },
        "severity": 4,
        "notes": "Central system of record for P&C operations but isolated from member identity layer. Migration complexity at Countryway is a live risk.",
    },
    {
        "id": "personify",
        "name": "Personify / ThreeSixty",
        "category": "Membership Management",
        "owner": "Karen Clarke",
        "teams_using": [
            "Membership / Federation operations",
            "Field Services (Robert, Daryl Butler)",
            "Communications (Kathy, Alice)",
            "Fundraising (Christy)",
        ],
        "approx_headcount": 20,
        "core_functions": [
            "Locality and region membership tracking",
            "Member engagement and communication history",
            "Event and chapter management",
        ],
        "known_gaps": [
            "No integration with Finys — member and policyholder records not cleanly linked",
            "No universal member ID strategy across VAFB entities",
            "HEA/healthcare cluster not represented — no named data owner or confirmed system tie-in",
            "Member data quality issues (duplicates, incomplete records) limit reliable 360 view",
        ],
        "workarounds": [
            "Staff manually cross-reference Personify and Finys records using name/address matching",
            "Field staff maintain local contact lists outside the system",
            "Marketing runs campaigns off HubSpot lists that don't reflect current Personify membership status",
        ],
        "integrations": {
            "confirmed": ["HubSpot (marketing, partial sync)"],
            "unconfirmed": ["Finys (no confirmed linkage)", "NetSuite (financial reconciliation unclear)"],
        },
        "severity": 5,
        "notes": "The absence of a Personify-Finys link is the central master data governance challenge. This is ground zero for the Member 360 gap.",
    },
    {
        "id": "countryway",
        "name": "Countryway Connection / AS400 / Garvin Allen",
        "category": "Legacy Underwriting Stack",
        "owner": "Theresa Richardson (Technical Lead); William Skorzyk (VP)",
        "teams_using": [
            "Countryway Underwriting",
            "Countryway Sales (Stacy Lister)",
            "Countryway Claims (David Jewell)",
            "Countryway Customer Service (Paula Chavis)",
        ],
        "approx_headcount": 15,
        "core_functions": [
            "Countryway-specific policy underwriting",
            "Legacy billing and claims for Countryway book of business",
            "Agent/producer management",
        ],
        "known_gaps": [
            "Semi-autonomous — no confirmed integration to core IS & EDM layer",
            "Mid-migration to Finys creates parallel system operation and data duplication risk",
            "No visibility into Countryway data from VAFB IS & EDM governance layer",
            "Unclear data ownership and stewardship during and after migration",
        ],
        "workarounds": [
            "Countryway staff operate dual workflows — legacy stack and Finys simultaneously",
            "Manual data reconciliation between AS400 and Finys during migration window",
            "No automated reporting — staff pull manual extracts for leadership visibility",
        ],
        "integrations": {
            "confirmed": [],
            "unconfirmed": ["Finys (migration in progress, not complete)", "ODS (not confirmed)"],
        },
        "severity": 4,
        "notes": "Key investigation area. Semi-autonomous operation with no confirmed IS & EDM integration is a governance blind spot. Migration risk is live.",
    },
    {
        "id": "hubspot",
        "name": "HubSpot",
        "category": "Marketing / CRM",
        "owner": "Kyle Shover / Mike Bolino (Marketing)",
        "teams_using": [
            "Marketing (Kyle Shover, Mike Bolino)",
            "Sales (Ray Leonard)",
            "Countryway Marketing (William Skorzyk, partial)",
        ],
        "approx_headcount": 8,
        "core_functions": [
            "Email and campaign marketing",
            "Lead and contact management",
            "Sales pipeline tracking",
        ],
        "known_gaps": [
            "Contact lists not reliably synced with Personify membership data",
            "No connection to Finys — marketing has no visibility into policyholder status or claims history",
            "Countryway marketing operates largely independently — no unified campaign view",
            "No firmographic or member-segment data feeding in from ODS",
        ],
        "workarounds": [
            "Marketing manually exports and imports lists from Personify to HubSpot for campaigns",
            "Sales staff check Finys separately before member outreach — no unified view",
            "Campaigns sometimes reach lapsed or duplicate members due to stale list data",
        ],
        "integrations": {
            "confirmed": ["Personify (partial, manual or scheduled sync)"],
            "unconfirmed": ["Finys (no connection)", "ODS (no connection)", "NetSuite (not confirmed)"],
        },
        "severity": 3,
        "notes": "HubSpot is a symptom of the Member 360 gap — marketing operates on a partial view of the member base. Upstream data quality fixes in Personify/Finys would flow through here.",
    },
    {
        "id": "supporting",
        "name": "NetSuite / ImageRight / ODS",
        "category": "Finance, Documents & Analytics",
        "owner": "Kim Boos (ODS); Jacki Picco (NetSuite/Accounting); Catherine Reid (ImageRight)",
        "teams_using": [
            "Accounting / Finance (Jacki Picco, Jason Hart)",
            "Data Services / Analytics (Kim Boos)",
            "Claims and Underwriting (ImageRight)",
            "Product / Actuarial (Shail Depura, David Tenembaum) — ODS consumers",
        ],
        "approx_headcount": 12,
        "core_functions": [
            "NetSuite: Financial management and general ledger",
            "ImageRight: Document management and storage",
            "ODS: Operational data store for analytics and reporting",
        ],
        "known_gaps": [
            "ODS is a reporting layer, not a master data layer — quality depends on upstream Finys/Personify data",
            "Incorrect warehouse item classification in upstream systems creates downstream ODS errors",
            "Missing product dimensions blocking shipping/fulfillment automation",
            "Self-service data access is limited — analysts submit requests rather than query directly",
            "NetSuite financial reconciliation to member/policy data is unclear",
        ],
        "workarounds": [
            "Actuarial and product teams maintain their own Excel models because ODS data is unreliable for self-service",
            "Accounting staff manually reconcile NetSuite entries against Finys billing extracts",
            "ImageRight used as a workaround for document context that Finys doesn't surface natively",
        ],
        "integrations": {
            "confirmed": ["Finys → ODS (extract)", "Finys → ImageRight (document link)"],
            "unconfirmed": ["Personify → ODS (not confirmed)", "NetSuite ↔ Finys (reconciliation method unclear)"],
        },
        "severity": 3,
        "notes": "ODS quality is a downstream reflection of Finys/Personify gaps. Fixing master data upstream is a prerequisite to ODS being useful for self-service analytics.",
    },
]


def get_system_by_id(system_id):
    return next((s for s in SYSTEMS if s["id"] == system_id), None)


def get_systems_by_severity(min_severity=1):
    return sorted(
        [s for s in SYSTEMS if s["severity"] >= min_severity],
        key=lambda x: x["severity"],
        reverse=True,
    )


def get_all_workarounds():
    """Flatten all workarounds across systems for a consolidated view."""
    result = []
    for s in SYSTEMS:
        for w in s["workarounds"]:
            result.append({"system": s["name"], "severity": s["severity"], "workaround": w})
    return result


def get_integration_gaps():
    """Return all unconfirmed integrations across systems."""
    result = []
    for s in SYSTEMS:
        for gap in s["integrations"].get("unconfirmed", []):
            result.append({"system": s["name"], "gap": gap, "severity": s["severity"]})
    return result
