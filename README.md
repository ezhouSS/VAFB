# VFB Pain Heat Map — Streamlit App

Interactive current-state pain heat map for the Virginia Farm Bureau CRM Transformation engagement.

## Files

| File | What it is | Do you edit it? |
|------|-----------|----------------|
| `data.py` | All scores, notes, personas, stages | **YES — after every interview** |
| `app.py` | UI layer, layout, interactivity | No |
| `requirements.txt` | Python dependencies | No |

---

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Opens at http://localhost:8501

---

## Deploying to Streamlit Community Cloud (free, shareable link)

1. Push this folder to a GitHub repository (can be private)
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Click "New app"
5. Select your repo, branch, and set the main file path to `app.py`
6. Click Deploy — you'll get a shareable URL in ~2 minutes

**Auto-redeploy:** Every time you push a change to `data.py`, the live app updates automatically within ~30 seconds. No manual redeploy needed.

---

## Updating Scores After Interviews

Open `data.py` and find the persona you just interviewed. Update:

```python
"status": "validated",   # change from "hypothesis" to "validated"
"scores": {
    "aware":   1,   # update these based on what you heard
    "join":    4,   # 0=None, 1=Low, 2=Medium, 3=High, 4=Critical
    "inforce": 3,
    "service": 2,
    "renew":   4,
},
"notes": {
    "join": {
        "pain":       "What they told you the pain actually is",
        "workaround": "How they handle it today",
        "data_gap":   "Your data engineering assessment of the gap",
    },
    # ... update other stages
},
```

Save → commit → push → done. The live link updates automatically.

---

## Adding a New Persona

Copy any existing persona block in `data.py`, change the `id`, `role`, `subtitle`, `system`, `color`, and fill in scores/notes. The grid adds the new row automatically.

## Adding a New Journey Stage

Add a new dict to the `STAGES` list:
```python
{"id": "offboard", "label": "Offboard / Lapse", "desc": "Member or policy cancellation"},
```
Then add `"offboard": 0` to every persona's `scores` dict and a matching `notes` entry.

---

## Interview Order (recommended)

| # | Stakeholder | Duration | Your focus |
|---|------------|----------|------------|
| 1 | Patrick Caine (CIO) | 60 min | System architecture, API availability, identity bridge |
| 2 | Karen (Dir. BizSol) | 60 min | Data ownership, Personify governance, reconciliation process |
| 3 | Jenny Glen (CRM Dev) | 45 min | Finys data model, schema docs, integration constraints |
| 4 | Ray Leonard (Agent) | 45 min | Finys day-to-day, spreadsheet workarounds |
| 5 | Bob Brown (Rel. Mgr) | 45 min | Personify pain, cross-system gaps |
| 6 | Jason (Sales) | 45 min | Pipeline data staleness, export workflows |
| 7 | Bill (VP Mktg) | 60 min | Campaign data, attribution, member segment quality |
| 8 | Todd Cornell (Sponsor) | 30 min | Synthesize findings, surface governance decisions |
