import streamlit as st
import groq
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time
# ── API Key ───────────────────────────────────────────────────────────────────
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

PHASES = [
    {"num": 1, "icon": "🤖", "label": "AI Mentor",        "sub": "Plan your journey"},
    {"num": 2, "icon": "🎓", "label": "Profile & Unis",   "sub": "Evaluate & match"},
    {"num": 3, "icon": "💰", "label": "Finance",           "sub": "Loans & ROI"},
    {"num": 4, "icon": "🏠", "label": "Accommodation",    "sub": "Find your home"},
    {"num": 5, "icon": "📋", "label": "Full Report",      "sub": "Download summary"},
]

COUNTRIES = ["USA 🇺🇸", "UK 🇬🇧", "Canada 🇨🇦", "Australia 🇦🇺", "Germany 🇩🇪",
             "France 🇫🇷", "Netherlands 🇳🇱", "Ireland 🇮🇪"]
DEGREES = [
    "MS Computer Science", "MS Data Science", "MS Artificial Intelligence",
    "MS Electrical Engineering", "MS Mechanical Engineering", "MBA",
    "MS Finance", "MS Information Systems", "MS Cybersecurity",
    "MS Biotechnology", "MS Public Health", "MS Education Technology",
]

st.set_page_config(
    page_title="Study Abroad AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; scroll-behavior: smooth; }

/* ════ KEYFRAMES ════ */
@keyframes fadeUp    { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn    { from { opacity:0; } to { opacity:1; } }
@keyframes slideRight{ from { opacity:0; transform:translateX(-10px); } to { opacity:1; transform:translateX(0); } }
@keyframes pulseGlow { 0%,100%{box-shadow:0 4px 20px rgba(102,126,234,0.08),inset 0 1px 0 rgba(255,255,255,0.55);} 50%{box-shadow:0 4px 24px rgba(102,126,234,0.2),0 0 0 5px rgba(102,126,234,0.06),inset 0 1px 0 rgba(255,255,255,0.55);} }
@keyframes progressFill { from { width:0%; } }
@keyframes shimmer   { 0%{background-position:-400px 0;} 100%{background-position:400px 0;} }
@keyframes floatBadge{ 0%,100%{transform:translateY(0);} 50%{transform:translateY(-3px);} }
@keyframes rankPop   { from{opacity:0;transform:scale(0.7) translateY(8px);} to{opacity:1;transform:scale(1) translateY(0);} }

/* ════ GLOBAL ════ */
.stApp { background: #f8f7ff; }
.main .block-container { animation: fadeUp 0.42s cubic-bezier(0.22,1,0.36,1) both; padding-top:1.5rem; }
div[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #f0edff 0%, #ede9fe 50%, #f5f3ff 100%);
    padding-top: 0.5rem;
}
div[data-testid="stSidebarContent"] * { color: #1e1b4b !important; }
.stApp { background: #f8f7ff; }
section[data-testid="stSidebar"] { border-right: 1.5px solid rgba(102,126,234,0.13); box-shadow: 4px 0 24px rgba(102,126,234,0.06); }

/* ── PHASE STEPS ── */
.phase-step {
    border-radius: 14px; padding: 0.75rem 1rem; margin: 5px 0;
    transition: all 0.25s; border: 1px solid transparent;
    display: flex; align-items: center; gap: 0.75rem;
}
.phase-step.active {
    background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.1));
    border-color: rgba(102,126,234,0.45);
    box-shadow: 0 4px 16px rgba(102,126,234,0.12);
}
.phase-step.done { background: rgba(5,150,105,0.08); border-color: rgba(5,150,105,0.3); }
.phase-step.locked { opacity: 0.4; }
.phase-step:hover:not(.locked) { transform: translateX(3px); background: rgba(102,126,234,0.06); }
.step-icon  { font-size: 1.4rem; flex-shrink: 0; }
.step-num   { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; }
.step-title { font-size: 0.9rem; font-weight: 700; color: #312e81; }
.step-sub   { font-size: 0.68rem; color: #94a3b8; }
.step-check { margin-left: auto; font-size: 1rem; color: #059669; }

/* ── PROGRESS BAR ── */
.prog-bar-wrap { background: rgba(102,126,234,0.12); border-radius: 50px; height: 7px; margin: 0.8rem 0 1.2rem; overflow: hidden; }
.prog-bar-fill { height: 100%; border-radius: 50px; background: linear-gradient(90deg,#667eea,#764ba2,#059669); transition: width 0.5s; }

/* ── HERO ── */
.hero-phase {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 60%, #4f46e5 100%);
    border: none; border-radius: 20px;
    padding: 2rem 2.5rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(102,126,234,0.3);
}
.hero-phase::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(ellipse at top right, rgba(255,255,255,0.15) 0%, transparent 60%);
}
.hero-phase .phase-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.35);
    border-radius: 50px; padding: 0.3rem 0.9rem;
    font-size: 0.72rem; font-weight: 700; color: white;
    letter-spacing: 0.06em; margin-bottom: 0.8rem; position: relative;
}
.hero-phase h1 {
    font-size: 2rem; font-weight: 900; position: relative;
    color: white; -webkit-text-fill-color: white;
    margin: 0 0 0.4rem; letter-spacing: -0.02em;
}
.hero-phase p { font-size: 0.9rem; color: rgba(255,255,255,0.85); margin: 0; position: relative; }
.hero-phase strong { color: white; }

/* ── RANKING BADGE ── */
.rank-card {
    background: white;
    border: 2px solid rgba(102,126,234,0.3); border-radius: 20px;
    padding: 1.5rem 1.8rem; text-align: center;
    box-shadow: 0 8px 32px rgba(102,126,234,0.12);
}
.rank-card .rank-label { font-size: 0.68rem; color: #667eea; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.rank-card .rank-num   { font-size: 3rem; font-weight: 900; color: #4f46e5; line-height: 1.1; }
.rank-card .rank-name  { font-size: 0.85rem; color: #64748b; margin-top: 4px; }
.rank-card .rank-tier  { display: inline-block; margin-top: 10px; background: rgba(102,126,234,0.1); border: 1px solid rgba(102,126,234,0.3); border-radius: 50px; padding: 3px 14px; font-size: 0.72rem; font-weight: 700; color: #667eea; }

/* ── RESULT CARDS ── */
.result-card {
    background: white;
    border: 1px solid rgba(102,126,234,0.15); border-radius: 18px;
    padding: 1.4rem; margin: 0.6rem 0; transition: all 0.25s;
    box-shadow: 0 2px 12px rgba(102,126,234,0.06);
}
.result-card:hover { border-color: rgba(102,126,234,0.35); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(102,126,234,0.1); }
.result-card h3 { font-size: 1rem; font-weight: 700; color: #1e1b4b; margin: 0 0 0.6rem; }
.result-card p  { font-size: 0.83rem; color: #64748b; line-height: 1.65; margin: 0; }

/* ── UNI CARD ── */
.uni-card { background: white; border-radius: 20px; overflow: hidden; margin: 8px 0; box-shadow: 0 4px 20px rgba(102,126,234,0.1); transition: all 0.25s; border: 1px solid rgba(102,126,234,0.1); }
.uni-card:hover { transform: translateY(-4px); box-shadow: 0 12px 36px rgba(102,126,234,0.18); }
.uni-card .uc-bar  { height: 4px; }
.uni-card .uc-body { padding: 1.2rem 1.3rem; }
.uni-card .uc-name { font-size: 0.95rem; font-weight: 700; color: #1e1b4b; margin-bottom: 10px; line-height: 1.4; }
.uni-card .uc-fees { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin-top: 8px; }
.uni-card .uc-fee  { background: #f8f7ff; border-radius: 8px; padding: 0.4rem 0.5rem; text-align: center; border: 1px solid rgba(102,126,234,0.08); }
.uni-card .uc-fee-lbl { font-size: 0.58rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.uni-card .uc-fee-val { font-size: 0.85rem; font-weight: 800; }

/* ── FIN CARD ── */
.fin-card { background: white; border-radius: 16px; overflow: hidden; margin: 6px 0; border: 1px solid rgba(102,126,234,0.12); box-shadow: 0 4px 16px rgba(102,126,234,0.07); transition: all 0.22s; }
.fin-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(102,126,234,0.14); }
.fin-card .fc-top  { height: 3px; }
.fin-card .fc-body { padding: 1rem 1.2rem; }
.fin-card .fc-tag  { font-size: 0.63rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; border-radius: 50px; padding: 3px 10px; display: inline-block; margin-bottom: 8px; }
.fin-card .fc-name { font-size: 0.9rem; font-weight: 700; color: #1e1b4b; margin-bottom: 5px; }
.fin-card .fc-desc { font-size: 0.77rem; color: #64748b; line-height: 1.55; margin-bottom: 8px; }
.fin-card .fc-amt  { font-size: 1.05rem; font-weight: 900; }

/* ── ACCOM CARD ── */
.accom-card { background: white; border: 1px solid rgba(59,130,246,0.2); border-radius: 16px; padding: 1.2rem 1.4rem; margin: 6px 0; transition: all 0.22s; box-shadow: 0 2px 12px rgba(59,130,246,0.06); }
.accom-card:hover { border-color: rgba(59,130,246,0.4); box-shadow: 0 8px 24px rgba(59,130,246,0.1); transform: translateY(-2px); }

/* ── REPORT CARD ── */
.report-section {
    background: white; border: 1px solid rgba(102,126,234,0.12);
    border-radius: 16px; padding: 1.5rem 1.8rem; margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(102,126,234,0.06);
}
.report-section h3 { font-size: 1rem; font-weight: 800; color: #4f46e5; margin: 0 0 1rem; border-bottom: 2px solid rgba(102,126,234,0.12); padding-bottom: 0.5rem; }

/* ════ BUTTONS ════ */
.stButton > button { background:linear-gradient(135deg,#667eea 0%,#764ba2 100%) !important; color:white !important; border:none !important; border-radius:14px !important; padding:0.7rem 2rem !important; font-weight:700 !important; font-family:'Inter',sans-serif !important; font-size:0.95rem !important; transition:all 0.3s cubic-bezier(0.22,1,0.36,1) !important; box-shadow:0 4px 20px rgba(102,126,234,0.3),0 1px 4px rgba(102,126,234,0.2) !important; letter-spacing:0.01em !important; }
.stButton > button:hover { transform:translateY(-3px) scale(1.02) !important; box-shadow:0 8px 32px rgba(102,126,234,0.4),0 2px 8px rgba(102,126,234,0.2) !important; }
.stButton > button:active { transform:translateY(0) scale(0.98) !important; box-shadow:0 2px 8px rgba(102,126,234,0.2) !important; transition:all 0.1s !important; }
.stDownloadButton > button { background:linear-gradient(135deg,#059669 0%,#047857 100%) !important; color:white !important; border:none !important; border-radius:14px !important; padding:0.78rem 2.5rem !important; font-weight:800 !important; font-size:1rem !important; box-shadow:0 4px 20px rgba(5,150,105,0.28),0 1px 4px rgba(5,150,105,0.15) !important; transition:all 0.3s cubic-bezier(0.22,1,0.36,1) !important; }
.stDownloadButton > button:hover { transform:translateY(-3px) scale(1.02) !important; box-shadow:0 8px 32px rgba(5,150,105,0.38),0 2px 8px rgba(5,150,105,0.2) !important; }
.stDownloadButton > button:active { transform:translateY(0) scale(0.98) !important; transition:all 0.1s !important; }

/* ════ FORM INPUTS ════ */
.stTextInput > div > div > input { background:white !important; color:#1e1b4b !important; border:1.5px solid rgba(102,126,234,0.22) !important; border-radius:12px !important; transition:all 0.28s cubic-bezier(0.22,1,0.36,1) !important; box-shadow:0 1px 4px rgba(102,126,234,0.04) !important; }
.stTextInput > div > div > input:focus { border-color:#667eea !important; box-shadow:0 0 0 4px rgba(102,126,234,0.1),0 2px 8px rgba(102,126,234,0.08) !important; }
.stTextInput > div > div > input::placeholder { color:#c4c8d4 !important; }
.stSelectbox > div > div { background:white !important; border:1.5px solid rgba(102,126,234,0.22) !important; border-radius:12px !important; color:#1e1b4b !important; transition:all 0.28s cubic-bezier(0.22,1,0.36,1) !important; }
.stNumberInput > div > div > input { background:white !important; color:#1e1b4b !important; border:1.5px solid rgba(102,126,234,0.22) !important; border-radius:12px !important; transition:all 0.28s ease !important; }

/* ════ METRICS ════ */
div[data-testid="stMetric"] { background:white; border:1.5px solid rgba(102,126,234,0.1); border-radius:16px; padding:0.8rem 1rem; box-shadow:0 2px 10px rgba(102,126,234,0.05); transition:all 0.3s cubic-bezier(0.22,1,0.36,1); animation:fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) both; }
div[data-testid="stMetric"]:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(102,126,234,0.1); }
div[data-testid="stMetricValue"] { color:#1e1b4b !important; }
div[data-testid="stMetricLabel"] { color:#64748b !important; }

/* ════ TABS ════ */
.stTabs [data-baseweb="tab-list"] { background:rgba(102,126,234,0.06); border-radius:14px; padding:5px; gap:3px; box-shadow:inset 0 2px 6px rgba(102,126,234,0.06); }
.stTabs [data-baseweb="tab"] { border-radius:10px; color:#64748b; font-weight:600; transition:all 0.25s cubic-bezier(0.22,1,0.36,1); font-size:0.87rem; }
.stTabs [data-baseweb="tab"]:hover { color:#4f46e5; background:rgba(102,126,234,0.06) !important; }
.stTabs [aria-selected="true"] { background:white !important; color:#4f46e5 !important; box-shadow:0 3px 12px rgba(102,126,234,0.15),0 1px 4px rgba(102,126,234,0.08) !important; font-weight:700 !important; }

/* ════ ALERTS ════ */
div[data-testid="stAlert"] { border-radius:14px !important; border-left-width:4px !important; animation:fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) both; }

/* ════ MISC ════ */
.section-header { font-size:1.25rem; font-weight:800; background:linear-gradient(135deg,#667eea 0%,#a78bfa 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:1.6rem 0 0.9rem; letter-spacing:-0.01em; animation:fadeUp 0.35s cubic-bezier(0.22,1,0.36,1) both; }
.divider { height:1.5px; background:linear-gradient(90deg,transparent 0%,rgba(102,126,234,0.18) 40%,rgba(167,139,250,0.2) 60%,transparent 100%); margin:1.8rem 0; border:none; animation:fadeIn 0.5s ease both; }
.info-pill { display:inline-flex; align-items:center; gap:6px; background:rgba(102,126,234,0.07); border:1.5px solid rgba(102,126,234,0.18); border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; color:#4f46e5; font-weight:600; margin:3px; transition:all 0.25s cubic-bezier(0.22,1,0.36,1); animation:fadeIn 0.4s ease both; }
.info-pill:hover { background:rgba(102,126,234,0.13); transform:scale(1.04); }
.tip-box { background:linear-gradient(135deg,#fffbeb,#fef3c7); border:1.5px solid #fcd34d; border-radius:14px; padding:0.9rem 1.15rem; font-size:0.84rem; color:#78350f; margin:6px 0; line-height:1.6; box-shadow:0 2px 10px rgba(251,191,36,0.1); transition:all 0.25s cubic-bezier(0.22,1,0.36,1); animation:fadeUp 0.4s cubic-bezier(0.22,1,0.36,1) both; }
.tip-box:hover { box-shadow:0 6px 20px rgba(251,191,36,0.16); transform:translateY(-2px); }
/* ════ METRIC VALUE SIZE ════ */
div[data-testid="stMetricValue"] { font-size: 1rem !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "phase":     1,
        "max_phase": 1,
        "data": {
            "student_name":   "",
            "current_uni":    "",
            "country":        None,
            "degree":         None,
            "phase1_result":  None,
            "uni_ranking":    None,
            "profile":        {},
            "phase2_result":  None,
            "selected_uni":   None,
            "selected_uni_obj": None,
            "phase3_result":  None,
            "phase4_result":  None,
        }
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ════════════════════════════════════════════════════════════════════════════
# GROQ HELPERS
# ════════════════════════════════════════════════════════════════════════════
def groq_client():
    return groq.Groq(api_key=GROQ_API_KEY)

def call_groq(prompt: str, max_tokens: int = 900, temp: float = 0.4) -> str:
    client = groq_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temp,
    )
    return resp.choices[0].message.content.strip()

def parse_json(raw: str):
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def clean_country(country: str) -> str:
    for flag in [" 🇺🇸"," 🇬🇧"," 🇨🇦"," 🇦🇺"," 🇩🇪"," 🇫🇷"," 🇳🇱"," 🇮🇪"]:
        country = country.replace(flag, "")
    return country.strip()

# ────────────────────────────────────────────────────────────────────────────
# Phase 1 AI — country/degree guidance (no university input)
# ────────────────────────────────────────────────────────────────────────────
def ai_phase1(country: str, degree: str) -> dict:
    cc = clean_country(country)
    prompt = f"""
You are an expert study-abroad advisor with accurate, up-to-date knowledge of university admission requirements.
Student wants to study "{degree}" in "{cc}".

Before listing exam requirements, use ACCURATE knowledge:
- English proficiency tests (IELTS/TOEFL/PTE/Duolingo) are required at virtually all universities for non-native English speakers.
- GRE requirements vary by university — be precise:
  * Universities that have DROPPED GRE for MS CS (optional/not required): Stanford, MIT, Harvard, Berkeley, Columbia, Cornell, Yale
  * Universities that STILL REQUIRE GRE for MS CS: CMU (Carnegie Mellon), Georgia Tech, UIUC, Purdue, Texas A&M, Boston University, Northeastern, USC, NYU, Arizona State
  * When GRE is required at MOST universities in a country for a given degree, list it as "required"
  * When GRE is optional at many top schools but required at others, list it as "optional" with a clear note
- Only list an exam as "required" if the majority of universities for this degree+country mandate it.

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "country_guide": {{
    "overview": "<2-3 sentence overview of studying {degree} in {cc}>",
    "demand": "<job demand for this field in {cc}>",
    "avg_salary": "<average starting salary in local currency and INR equivalent>",
    "cost_of_living": "<monthly estimated living cost in local currency and INR>",
    "pros": ["<pro1>", "<pro2>", "<pro3>"],
    "cons": ["<con1>", "<con2>"]
  }},
  "exams": {{
    "required": ["<e.g. TOEFL or IELTS for English proficiency>"],
    "optional": ["<e.g. GRE — required at CMU/GaTech/UIUC but optional at Stanford/MIT/Berkeley>"],
    "notes": "<precise note — mention which major universities require GRE and which have waived it>"
  }},
  "passport": {{
    "documents": ["<doc1>", "<doc2>", "<doc3>", "<doc4>", "<doc5>"],
    "steps": ["<step1>", "<step2>", "<step3>", "<step4>"],
    "timeline": "<estimated time to get passport>"
  }},
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
"""
    raw = call_groq(prompt, max_tokens=900)
    return parse_json(raw)

# ────────────────────────────────────────────────────────────────────────────
# University World Ranking lookup (called in Phase 2)
# ────────────────────────────────────────────────────────────────────────────
def ai_ranking(uni_name: str) -> dict:
    prompt = f"""
You are an expert on global university rankings.
Look up the world ranking of "{uni_name}" (an Indian university/college).

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "name": "{uni_name}",
  "world_rank": "<e.g. #301-400 QS 2024 or Unranked>",
  "national_rank": "<rank within India if known>",
  "tier": "<Tier 1 (Top 100)|Tier 2 (101-500)|Tier 3 (501+)|Unranked>",
  "known_for": "<what the university is known for>",
  "ranking_source": "<QS World University Rankings 2024 or similar>",
  "rank_impact": "<how this rank affects admission chances at foreign universities>"
}}
"""
    raw = call_groq(prompt, max_tokens=400, temp=0.2)
    return parse_json(raw)

# ────────────────────────────────────────────────────────────────────────────
# Phase 2 AI
# ────────────────────────────────────────────────────────────────────────────
def ai_phase2(profile: dict) -> dict:
    prompt = f"""
You are an expert university admission consultant. Evaluate this Indian student profile and recommend universities.
Profile: {json.dumps(profile)}

Respond ONLY with valid JSON (no markdown):
{{
  "profile_score": {{
    "overall": <integer 0-100>,
    "academics": <integer 0-100>,
    "exams": <integer 0-100>,
    "experience": <integer 0-100>,
    "documents": <integer 0-100>,
    "research": <integer 0-100>
  }},
  "eligibility_summary": "<2-3 sentence overall assessment>",
  "universities": [
    {{
      "name": "<University Name>",
      "type": "<Public|Private>",
      "country": "<country>",
      "tier": "<Ambitious|Moderate|Safe>",
      "eligibility": "<Eligible|Conditional|Not Eligible>",
      "match_score": <integer 0-100>,
      "tuition_inr_lakhs": <number>,
      "living_inr_lakhs": <number per year>,
      "total_inr_lakhs": <number for full course>,
      "notes": "<short note on why this match>"
    }}
  ],
  "missing_exams": ["<exam if required but not given>"],
  "suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"]
}}
Include 8 universities: mix of 3 Ambitious, 3 Moderate, 2 Safe. Mix Public and Private.
"""
    raw = call_groq(prompt, max_tokens=1400, temp=0.3)
    return parse_json(raw)

# ────────────────────────────────────────────────────────────────────────────
# Phase 3 AI
# ────────────────────────────────────────────────────────────────────────────
def ai_phase3(country: str, degree: str, university: str, total_cost: float, profile: dict) -> dict:
    cc = clean_country(country)
    prompt = f"""
You are a financial advisor for Indian students studying abroad.
Student: studying "{degree}" at "{university}" in "{cc}".
Total program cost: Rs.{total_cost} Lakhs. Profile: {json.dumps(profile)}.

Respond ONLY with valid JSON (no markdown):
{{
  "scholarships": [
    {{
      "name": "<Scholarship Name>",
      "type": "<Government|University|International|Private>",
      "amount": "<amount in INR or USD>",
      "eligibility": "<brief eligibility>",
      "link": "<website URL>",
      "color": "<hex color like #818cf8>"
    }}
  ],
  "loans": [
    {{
      "bank": "<Bank Name>",
      "rate": "<interest rate>",
      "max_amount": "<max loan amount>",
      "features": "<key feature>",
      "link": "<website>"
    }}
  ],
  "roi": {{
    "total_cost_lakhs": <number>,
    "scholarship_saving_lakhs": <number>,
    "net_cost_lakhs": <number>,
    "expected_salary_inr_lakhs_yr": <number>,
    "payback_years": <number>,
    "5yr_net_gain_lakhs": <number>,
    "roi_verdict": "<Excellent|Good|Moderate|Poor>"
  }},
  "best_value_note": "<which scholarship+loan combination gives best value>"
}}
Include 5 scholarships (mix types) and 3 loan options.
"""
    raw = call_groq(prompt, max_tokens=1200, temp=0.3)
    return parse_json(raw)

# ────────────────────────────────────────────────────────────────────────────
# Phase 4 AI
# ────────────────────────────────────────────────────────────────────────────
def ai_phase4(university: str, country: str) -> dict:
    cc = clean_country(country)
    prompt = f"""
You are an accommodation advisor for international students.
Student is going to "{university}" in "{cc}".

Respond ONLY with valid JSON (no markdown):
{{
  "hostel": {{
    "available": <true|false>,
    "name": "<hostel/dorm name if available>",
    "cost_per_month_inr": <number>,
    "inclusions": ["<inclusion1>", "<inclusion2>", "<inclusion3>"],
    "apply_link": "<university housing portal URL>",
    "notes": "<waiting list? guarantee? etc.>"
  }},
  "rentals": [
    {{
      "type": "<Studio|1BHK|Shared Apartment|PG>",
      "area": "<nearby area/neighborhood name>",
      "cost_per_month_inr": <number>,
      "distance_to_campus": "<distance in km or miles>",
      "pros": "<key advantage>",
      "listing_site": "<e.g. Zillow, Rightmove, SpareRoom>"
    }}
  ],
  "tips": ["<tip1>", "<tip2>", "<tip3>"],
  "best_recommendation": "<which option is best and why>"
}}
Include 3-4 rental options of different types and price ranges.
"""
    raw = call_groq(prompt, max_tokens=1000, temp=0.3)
    return parse_json(raw)

# ════════════════════════════════════════════════════════════════════════════
# REPORT GENERATOR
# ════════════════════════════════════════════════════════════════════════════
def build_html_report(d: dict) -> str:
    name      = d.get("student_name", "Student")
    cur_uni   = d.get("current_uni", "N/A")
    country   = d.get("country", "N/A")
    degree    = d.get("degree", "N/A")
    r1        = d.get("phase1_result") or {}
    p2        = d.get("phase2_result") or {}
    p3        = d.get("phase3_result") or {}
    p4        = d.get("phase4_result") or {}
    sel_uni   = d.get("selected_uni", "N/A")
    sel_obj   = d.get("selected_uni_obj") or {}
    uni_info  = r1.get("university_info", {})
    cg        = r1.get("country_guide", {})
    exams     = r1.get("exams", {})
    scores    = p2.get("profile_score", {})
    roi       = p3.get("roi", {})
    hostel    = p4.get("hostel", {})
    dt        = datetime.now().strftime("%B %d, %Y %H:%M")

    def li_html(items): return "".join(f"<li>{i}</li>" for i in items)
    def schol_rows():
        rows = ""
        for s in p3.get("scholarships", []):
            rows += f"<tr><td>{s.get('name','')}</td><td>{s.get('type','')}</td><td>{s.get('amount','')}</td></tr>"
        return rows
    def loan_rows():
        rows = ""
        for l in p3.get("loans", []):
            rows += f"<tr><td>{l.get('bank','')}</td><td>{l.get('rate','')}</td><td>{l.get('max_amount','')}</td></tr>"
        return rows
    def uni_rows():
        rows = ""
        for u in p2.get("universities", []):
            rows += f"<tr><td>{u.get('name','')}</td><td>{u.get('type','')}</td><td>{u.get('tier','')}</td><td>{u.get('eligibility','')}</td><td>₹{u.get('tuition_inr_lakhs','?')}L</td><td>₹{u.get('total_inr_lakhs','?')}L</td></tr>"
        return rows

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Study Abroad Report — {name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', sans-serif; background: #080615; color: #e2e8f0; line-height: 1.6; }}
  .page {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}

  /* COVER */
  .cover {{ background: linear-gradient(135deg,#0f0c29,#302b63,#24243e); border-radius: 20px; padding: 3rem 2.5rem; margin-bottom: 2rem; text-align: center; border: 1px solid rgba(102,126,234,0.3); }}
  .cover .emoji {{ font-size: 4rem; margin-bottom: 1rem; }}
  .cover h1 {{ font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg,#e2e8f0,#a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }}
  .cover .sub {{ color: #94a3b8; font-size: 0.95rem; }}
  .cover .meta {{ margin-top: 1.5rem; display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; }}
  .cover .meta-item {{ background: rgba(102,126,234,0.12); border: 1px solid rgba(102,126,234,0.3); border-radius: 50px; padding: 0.35rem 1rem; font-size: 0.8rem; color: #a5b4fc; font-weight: 600; }}

  /* SECTIONS */
  .section {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.8rem 2rem; margin: 1.2rem 0; }}
  .section h2 {{ font-size: 1.1rem; font-weight: 800; color: #818cf8; border-bottom: 1px solid rgba(102,126,234,0.2); padding-bottom: 0.6rem; margin-bottom: 1rem; }}
  .section p  {{ font-size: 0.88rem; color: #94a3b8; margin-bottom: 0.5rem; }}

  /* SCORE GRID */
  .score-grid {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 0.8rem; margin-top: 0.8rem; }}
  .score-box {{ background: rgba(102,126,234,0.1); border: 1px solid rgba(102,126,234,0.25); border-radius: 12px; padding: 0.8rem; text-align: center; }}
  .score-box .s-val {{ font-size: 1.6rem; font-weight: 900; color: #a5b4fc; }}
  .score-box .s-lbl {{ font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}

  /* ROI GRID */
  .roi-grid {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 0.8rem; margin-top: 0.8rem; }}
  .roi-box {{ background: rgba(52,211,153,0.07); border: 1px solid rgba(52,211,153,0.2); border-radius: 12px; padding: 0.8rem 1rem; }}
  .roi-box .r-val {{ font-size: 1.3rem; font-weight: 900; color: #34d399; }}
  .roi-box .r-lbl {{ font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; }}

  /* TABLE */
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 0.8rem; }}
  th {{ background: rgba(102,126,234,0.15); color: #a5b4fc; padding: 0.5rem 0.8rem; text-align: left; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }}
  td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #94a3b8; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(102,126,234,0.05); }}

  /* LIST */
  ul {{ padding-left: 1.2rem; color: #94a3b8; font-size: 0.87rem; }}
  ul li {{ margin: 5px 0; }}

  /* RANK BADGE */
  .rank-badge {{ display: inline-block; background: linear-gradient(135deg,#1e1b4b,#312e81); border: 2px solid rgba(129,140,248,0.5); border-radius: 12px; padding: 0.8rem 1.5rem; margin: 0.8rem 0; }}
  .rank-badge .rb-rank {{ font-size: 1.8rem; font-weight: 900; color: #a5b4fc; }}
  .rank-badge .rb-lbl  {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; }}

  /* FOOTER */
  .footer {{ text-align: center; margin-top: 2rem; padding: 1.5rem; border-top: 1px solid rgba(255,255,255,0.06); color: #334155; font-size: 0.75rem; }}
  .pill {{ display: inline-block; background: rgba(102,126,234,0.12); border: 1px solid rgba(102,126,234,0.3); border-radius: 50px; padding: 2px 10px; font-size: 0.72rem; color: #a5b4fc; font-weight: 600; margin: 2px; }}
  .verdict {{ display: inline-block; padding: 0.4rem 1.2rem; border-radius: 50px; font-weight: 800; font-size: 0.9rem; background: linear-gradient(135deg,#34d399,#059669); color: white; }}
</style>
</head>
<body>
<div class="page">

  <!-- COVER -->
  <div class="cover">
    <div class="emoji">🎓</div>
    <h1>Study Abroad Report</h1>
    <div class="sub">AI-Powered Study Abroad Assistant &nbsp;·&nbsp; Poonawalla Fincorp Hackathon</div>
    <div class="meta">
      <div class="meta-item">👤 {name}</div>
      <div class="meta-item">🏫 {cur_uni}</div>
      <div class="meta-item">🌍 {clean_country(country)}</div>
      <div class="meta-item">📚 {degree}</div>
      <div class="meta-item">📅 Generated: {dt}</div>
    </div>
  </div>

  <!-- PHASE 1: PLANNING -->
  <div class="section">
    <h2>Phase 1 — Planning & AI Mentor</h2>
    <p><strong style="color:#e2e8f0;">Current University:</strong> {cur_uni}</p>
    <div class="rank-badge">
      <div class="rb-lbl">World Ranking</div>
      <div class="rb-rank">{uni_info.get('world_rank','N/A')}</div>
      <div style="font-size:0.75rem;color:#818cf8;margin-top:3px;">{uni_info.get('ranking_source','QS World Rankings')}</div>
    </div>
    <p style="margin-top:0.5rem;"><span class="pill">{uni_info.get('tier','N/A')}</span> &nbsp; {uni_info.get('known_for','')}</p>
    <p style="margin-top:0.8rem;"><strong style="color:#e2e8f0;">Rank Impact:</strong> {uni_info.get('rank_impact','')}</p>
    <hr style="border:1px solid rgba(255,255,255,0.06);margin:1rem 0;">
    <p><strong style="color:#e2e8f0;">Destination:</strong> {clean_country(country)} &nbsp;|&nbsp; <strong style="color:#e2e8f0;">Degree:</strong> {degree}</p>
    <p><strong style="color:#e2e8f0;">Overview:</strong> {cg.get('overview','')}</p>
    <p><strong style="color:#e2e8f0;">Avg Salary:</strong> {cg.get('avg_salary','N/A')} &nbsp;|&nbsp; <strong style="color:#e2e8f0;">Monthly Living:</strong> {cg.get('cost_of_living','N/A')}</p>
    <p style="margin-top:0.8rem;"><strong style="color:#e2e8f0;">Required Exams:</strong> {', '.join(exams.get('required',[]))}</p>
    <p><strong style="color:#e2e8f0;">Optional Exams:</strong> {', '.join(exams.get('optional',[]))}</p>
  </div>

  <!-- PHASE 2: PROFILE -->
  <div class="section">
    <h2>Phase 2 — Profile Evaluation</h2>
    <p>{p2.get('eligibility_summary','')}</p>
    <div class="score-grid">
      <div class="score-box"><div class="s-val">{scores.get('overall','—')}</div><div class="s-lbl">Overall</div></div>
      <div class="score-box"><div class="s-val">{scores.get('academics','—')}</div><div class="s-lbl">Academics</div></div>
      <div class="score-box"><div class="s-val">{scores.get('exams','—')}</div><div class="s-lbl">Exams</div></div>
      <div class="score-box"><div class="s-val">{scores.get('experience','—')}</div><div class="s-lbl">Experience</div></div>
      <div class="score-box"><div class="s-val">{scores.get('documents','—')}</div><div class="s-lbl">Documents</div></div>
      <div class="score-box"><div class="s-val">{scores.get('research','—')}</div><div class="s-lbl">Research</div></div>
    </div>
    <hr style="border:1px solid rgba(255,255,255,0.06);margin:1rem 0;">
    <p><strong style="color:#e2e8f0;">Selected University:</strong> {sel_uni} &nbsp;·&nbsp; Total Cost: <strong style="color:#34d399;">₹{sel_obj.get('total_inr_lakhs','?')} Lakhs</strong></p>
    <table>
      <thead><tr><th>University</th><th>Type</th><th>Tier</th><th>Eligibility</th><th>Tuition</th><th>Total (Course)</th></tr></thead>
      <tbody>{uni_rows()}</tbody>
    </table>
  </div>

  <!-- PHASE 3: FINANCE -->
  <div class="section">
    <h2>Phase 3 — Finance: Scholarships, Loans & ROI</h2>
    <div class="roi-grid">
      <div class="roi-box"><div class="r-val">₹{roi.get('total_cost_lakhs','?')}L</div><div class="r-lbl">Total Cost</div></div>
      <div class="roi-box"><div class="r-val">₹{roi.get('scholarship_saving_lakhs','?')}L</div><div class="r-lbl">Scholarship Savings</div></div>
      <div class="roi-box"><div class="r-val">₹{roi.get('net_cost_lakhs','?')}L</div><div class="r-lbl">Net Cost</div></div>
      <div class="roi-box"><div class="r-val">₹{roi.get('expected_salary_inr_lakhs_yr','?')}L/yr</div><div class="r-lbl">Expected Salary</div></div>
      <div class="roi-box"><div class="r-val">{roi.get('payback_years','?')} yrs</div><div class="r-lbl">Payback Period</div></div>
      <div class="roi-box"><div class="r-val">₹{roi.get('5yr_net_gain_lakhs','?')}L</div><div class="r-lbl">5-Year Net Gain</div></div>
    </div>
    <p style="margin-top:1rem;">ROI Verdict: <span class="verdict">{roi.get('roi_verdict','Good')}</span></p>
    <hr style="border:1px solid rgba(255,255,255,0.06);margin:1rem 0;">
    <p><strong style="color:#e2e8f0;">Scholarships</strong></p>
    <table>
      <thead><tr><th>Name</th><th>Type</th><th>Amount</th></tr></thead>
      <tbody>{schol_rows()}</tbody>
    </table>
    <hr style="border:1px solid rgba(255,255,255,0.06);margin:1rem 0;">
    <p><strong style="color:#e2e8f0;">Loan Options</strong></p>
    <table>
      <thead><tr><th>Bank</th><th>Interest Rate</th><th>Max Amount</th></tr></thead>
      <tbody>{loan_rows()}</tbody>
    </table>
  </div>

  <!-- PHASE 4: ACCOMMODATION -->
  <div class="section">
    <h2>Phase 4 — Accommodation</h2>
    {"<p><strong style='color:#34d399;'>✅ On-Campus Hostel Available</strong> — " + hostel.get('name','') + " — ₹" + str(hostel.get('cost_per_month_inr','?')) + "/month</p>" if hostel.get('available') else "<p><strong style='color:#f87171;'>❌ On-Campus Hostel Unavailable</strong> — consider nearby rentals.</p>"}
    <p style="margin-top:0.6rem;">{hostel.get('notes','')}</p>
    <hr style="border:1px solid rgba(255,255,255,0.06);margin:1rem 0;">
    <p><strong style="color:#e2e8f0;">Rental Options</strong></p>
    <ul>
      {"".join([f'<li><strong>{r.get("type","")}</strong> — {r.get("area","")} — ₹{r.get("cost_per_month_inr","?")}/mo — {r.get("distance_to_campus","")} from campus</li>' for r in p4.get('rentals',[])])}
    </ul>
    <p style="margin-top:1rem;"><strong style="color:#e2e8f0;">Best Recommendation:</strong> {p4.get('best_recommendation','')}</p>
  </div>

  <div class="footer">
    <p>🎓 Study Abroad AI Assistant &nbsp;·&nbsp; Built for Poonawalla Fincorp Hackathon &nbsp;·&nbsp; Report generated on {dt}</p>
    <p style="margin-top:4px;">This report is AI-generated and should be supplemented with official university and visa guidance.</p>
  </div>

</div>
</body>
</html>"""
    return html

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1.2rem 0 0.8rem;">
        <div style="font-size:2.5rem; margin-bottom:0.3rem;">🎓</div>
        <div style="font-size:1.1rem; font-weight:900; color:white; letter-spacing:-0.01em;">Study Abroad AI</div>
        <div style="font-size:0.7rem; color:#64748b; margin-top:2px;">AI-Powered Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    completed = st.session_state["max_phase"] - 1
    prog_pct  = int((completed / 5) * 100)
    st.markdown(f"""
    <div style="padding:0 0.5rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#64748b;margin-bottom:4px;">
            <span>PROGRESS</span><span>{completed}/5 Phases</span>
        </div>
        <div class="prog-bar-wrap">
            <div class="prog-bar-fill" style="width:{prog_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    d_sb = st.session_state["data"]
    if d_sb.get("student_name"):
        st.markdown(f"<div style='text-align:center;font-size:0.85rem;font-weight:700;color:#e2e8f0;padding:0.3rem 0;'>👤 {d_sb['student_name']}</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.65rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 0.5rem 0.3rem;'>YOUR JOURNEY</div>", unsafe_allow_html=True)

    for ph in PHASES:
        n         = ph["num"]
        is_active = (st.session_state["phase"] == n)
        is_done   = (n < st.session_state["max_phase"])
        is_locked = (n > st.session_state["max_phase"])

        css_cls    = "active" if is_active else ("done" if is_done else ("locked" if is_locked else ""))
        check_html = "<span class='step-check'>✅</span>" if is_done else ("🔒" if is_locked else "")

        st.markdown(f"""
        <div class="phase-step {css_cls}" id="phase-{n}">
            <div class="step-icon">{ph['icon']}</div>
            <div>
                <div class="step-num">Phase {n}</div>
                <div class="step-title">{ph['label']}</div>
                <div class="step-sub">{ph['sub']}</div>
            </div>
            {check_html}
        </div>
        """, unsafe_allow_html=True)

        if not is_locked and not is_active:
            if st.button(f"Go to Phase {n}", key=f"nav_{n}", use_container_width=True):
                st.session_state["phase"] = n
                st.rerun()

    st.markdown("<hr style='border:1px solid rgba(255,255,255,0.07);margin:1rem 0;'>", unsafe_allow_html=True)

    if d_sb.get("country"):
        st.markdown(f"<div class='info-pill'>🌍 {clean_country(d_sb['country'])}</div>", unsafe_allow_html=True)
    if d_sb.get("degree"):
        st.markdown(f"<div class='info-pill'>📚 {d_sb['degree'][:20]}</div>", unsafe_allow_html=True)
    if d_sb.get("selected_uni"):
        st.markdown(f"<div class='info-pill'>🏛️ {d_sb['selected_uni'][:20]}</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding-top:1rem;font-size:0.63rem;color:#334155;">
        Built for Poonawalla Fincorp Hackathon
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
phase = st.session_state["phase"]

# ────────────────────────────────────────────────────────────────────────────
# PHASE 1 — AI Mentor + University Ranking
# ────────────────────────────────────────────────────────────────────────────
if phase == 1:
    st.markdown("""
    <div class="hero-phase">
        <div class="phase-badge">📍 Phase 1 of 5 &nbsp;·&nbsp; Planning Stage</div>
        <h1>🤖 AI Study Abroad Mentor</h1>
        <p>Tell us your name, preferred country, and degree — our AI will craft a country guide, exam roadmap, and passport checklist. Your university's world ranking is checked in Phase 2.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("<div class='section-header'>👤 About You</div>", unsafe_allow_html=True)
        with st.container(border=True):
            student_name = st.text_input("📛 Your Full Name",
                value=st.session_state["data"].get("student_name", ""),
                placeholder="e.g. Priya Sharma")

        st.markdown("<div class='section-header'>🌍 Destination & Degree</div>", unsafe_allow_html=True)
        with st.container(border=True):
            country = st.selectbox("🌍 Preferred Country", COUNTRIES,
                index=COUNTRIES.index(st.session_state["data"]["country"]) if st.session_state["data"]["country"] in COUNTRIES else 0)
            degree  = st.selectbox("🎓 Desired Master's Program", DEGREES,
                index=DEGREES.index(st.session_state["data"]["degree"]) if st.session_state["data"]["degree"] in DEGREES else 0)

            st.markdown("<br>", unsafe_allow_html=True)
            go_btn = st.button("🤖 Generate AI Guidance →", use_container_width=True)

            if go_btn:
                if not student_name.strip():
                    st.error("Please enter your name.")
                else:
                    st.session_state["data"]["student_name"] = student_name.strip()
                    st.session_state["data"]["country"]      = country
                    st.session_state["data"]["degree"]       = degree
                    with st.spinner("🌐 AI is crafting your personalised country guide…"):
                        try:
                            result = ai_phase1(country, degree)
                            st.session_state["data"]["phase1_result"] = result
                        except Exception as e:
                            st.error(f"AI Error: {e}")
                            st.stop()
                    st.rerun()

    with col_info:
        st.markdown("<div class='section-header'>📋 What you'll get</div>", unsafe_allow_html=True)
        for item in [
            ("🌍", "Country & Degree Guide",   "Demand, salaries, cost of living, pros & cons"),
            ("📝", "Exam Roadmap",             "Which exams are required vs optional"),
            ("📄", "Passport Checklist",       "Documents, steps & timeline from Passport Seva"),
            ("💡", "Pro Tips",                "Insider advice from advisor AI"),
        ]:
            st.markdown(f"""
            <div class='result-card' style='display:flex;gap:1rem;align-items:flex-start;'>
                <div style='font-size:1.6rem;'>{item[0]}</div>
                <div><h3>{item[1]}</h3><p>{item[2]}</p></div>
            </div>
            """, unsafe_allow_html=True)

    # ── Results ──
    res = st.session_state["data"].get("phase1_result")
    if res:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        name_disp = st.session_state["data"].get("student_name", "")
        st.markdown(f"<div class='section-header'>✨ {name_disp}'s Personalised Guide — {clean_country(st.session_state['data']['country'])} · {st.session_state['data']['degree']}</div>", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🌍 Country Guide", "📝 Exam Requirements", "📄 Passport Steps", "💡 Pro Tips"])

        with tab1:
            cg = res.get("country_guide", {})
            st.markdown(f"""<div class='result-card'><h3>Overview</h3><p>{cg.get('overview','')}</p></div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("📈 Job Demand",        cg.get("demand", "High"))
            c2.metric("💵 Avg Starting Salary", cg.get("avg_salary", "N/A"))
            c3.metric("🏠 Monthly Living",    cg.get("cost_of_living", "N/A"))
            col_p, col_c = st.columns(2)
            with col_p:
                st.markdown("**✅ Pros**")
                for p in cg.get("pros", []):
                    st.markdown(f"<div class='tip-box'>✅ {p}</div>", unsafe_allow_html=True)
            with col_c:
                st.markdown("**⚠️ Cons**")
                for c in cg.get("cons", []):
                    st.markdown(f"<div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);border-radius:12px;padding:0.85rem 1.1rem;font-size:0.85rem;color:#fca5a5;margin:6px 0;line-height:1.55;'>⚠️ {c}</div>", unsafe_allow_html=True)

        with tab2:
            ex = res.get("exams", {})
            st.markdown(f"""<div class='result-card'><h3>📌 Notes</h3><p>{ex.get('notes','')}</p></div>""", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            with r1:
                st.markdown("**🔴 Required Exams**")
                for e in ex.get("required", []):
                    st.markdown(f"<div style='background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.3);border-radius:10px;padding:0.6rem 1rem;margin:5px 0;font-weight:600;color:#fca5a5;font-size:0.87rem;'>⚡ {e}</div>", unsafe_allow_html=True)
            with r2:
                st.markdown("**🟡 Optional Exams**")
                for e in ex.get("optional", []):
                    st.markdown(f"<div style='background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);border-radius:10px;padding:0.6rem 1rem;margin:5px 0;font-weight:600;color:#fde68a;font-size:0.87rem;'>📋 {e}</div>", unsafe_allow_html=True)

        with tab3:
            pp = res.get("passport", {})
            st.metric("⏱️ Timeline", pp.get("timeline", "4–6 weeks"))
            st.markdown("**📂 Documents Required**")
            doc_cols = st.columns(2)
            for i, doc in enumerate(pp.get("documents", [])):
                with doc_cols[i % 2]:
                    st.markdown(f"<div class='tip-box'>📄 {doc}</div>", unsafe_allow_html=True)
            st.markdown("**🪜 Application Steps**")
            for i, step in enumerate(pp.get("steps", []), 1):
                st.markdown(f"""
                <div style='display:flex;gap:1rem;align-items:flex-start;margin:8px 0;background:rgba(102,126,234,0.07);border:1px solid rgba(102,126,234,0.2);border-radius:12px;padding:0.75rem 1rem;'>
                    <div style='background:linear-gradient(135deg,#667eea,#764ba2);color:white;font-weight:900;font-size:0.8rem;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;flex-shrink:0;'>{i}</div>
                    <div style='font-size:0.87rem;color:#c7d2fe;line-height:1.55;'>{step}</div>
                </div>
                """, unsafe_allow_html=True)

        with tab4:
            for tip in res.get("tips", []):
                st.markdown(f"<div class='tip-box'>💡 {tip}</div>", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_btn = st.columns([3, 1])[1]
        with col_btn:
            if st.button("Proceed to Phase 2 — Profile & Universities →", use_container_width=True):
                st.session_state["phase"]     = 2
                st.session_state["max_phase"] = max(2, st.session_state["max_phase"])
                st.rerun()

# ────────────────────────────────────────────────────────────────────────────
elif phase == 2:
    d    = st.session_state["data"]
    cc   = clean_country(d.get("country") or "USA 🇺🇸")
    degr = d.get("degree") or "MS Computer Science"
    name = d.get("student_name", "Student")

    st.markdown(f"""
    <div class="hero-phase">
        <div class="phase-badge">📍 Phase 2 of 5 &nbsp;·&nbsp; {cc} · {degr}</div>
        <h1>🎓 Profile Evaluation & University Match</h1>
        <p>Hi <strong>{name}</strong>! Enter your academic profile. Our AI will score your application and match you to public & private universities with full fee details.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):
        st.markdown("<div class='section-header'>🎓 Academic Background</div>", unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        with a1:
            cgpa        = st.number_input("CGPA (out of 10)", 0.0, 10.0, 7.5, 0.1)
            backlogs    = st.number_input("Backlogs", 0, 20, 0)
        with a2:
            work_exp    = st.number_input("Work Experience (years)", 0.0, 20.0, 1.0, 0.5)
            internships = st.number_input("Internships Completed", 0, 10, 1)
        with a3:
            research    = st.number_input("Research Papers Published", 0, 20, 0)

        # ── Dynamic Exam Scores (based on Phase 1 AI exam requirements) ──
        p1_exams     = (st.session_state["data"].get("phase1_result") or {}).get("exams", {})
        req_exams    = p1_exams.get("required", [])
        opt_exams    = p1_exams.get("optional", [])
        all_exams    = req_exams + [e for e in opt_exams if e not in req_exams]

        # Fallback if Phase 1 not done yet
        if not all_exams:
            all_exams = ["IELTS", "GRE"]

        # Score ranges for known exams
        EXAM_RANGES = {
            "GRE":       ("number", 260,  340,  310,  1),
            "GMAT":      ("number", 200,  800,  650,  10),
            "IELTS":     ("float",  0.0,  9.0,  7.0,  0.5),
            "TOEFL":     ("number", 0,    120,  90,   1),
            "PTE":       ("number", 10,   90,   65,   1),
            "DUOLINGO":  ("number", 10,   160,  110,  5),
            "SAT":       ("number", 400,  1600, 1200, 10),
            "ACT":       ("number", 1,    36,   24,   1),
        }

        st.markdown("<div class='section-header'>📝 Exam Scores — Commonly Required for your course & country</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.3);border-radius:12px;
                    padding:0.7rem 1rem;margin-bottom:0.8rem;font-size:0.82rem;color:#fde68a;line-height:1.5;'>
            <strong>⚠️ Note:</strong> Exam requirements <strong>vary by university</strong>.
            For example, <strong>Stanford, MIT, CMU</strong> no longer require GRE for MS CS (made optional/waived since 2022).
            Always verify on each university's official admissions page before applying.
        </div>
        """, unsafe_allow_html=True)
        if p1_exams.get("notes"):
            st.caption(f"ℹ️ {p1_exams['notes']}")

        exam_scores  = {}
        exam_widgets = []
        ex_cols = st.columns(3)
        for i, exam_name in enumerate(all_exams):
            key_upper = exam_name.upper().split("/")[0].strip()   # e.g. "IELTS/TOEFL" → "IELTS"
            is_req    = exam_name in req_exams
            label     = f"{exam_name}{' ✳️' if is_req else ' (optional)'}"
            with ex_cols[i % 3]:
                opt = st.selectbox(label, ["Score entered", "Not Given"], key=f"exam_opt_{i}")
                if key_upper in EXAM_RANGES:
                    kind, mn, mx, default, step = EXAM_RANGES[key_upper]
                    if kind == "float":
                        val = st.number_input(f"{exam_name} Score", float(mn), float(mx), float(default), float(step),
                                             key=f"exam_val_{i}", disabled=(opt == "Not Given"))
                    else:
                        val = st.number_input(f"{exam_name} Score", int(mn), int(mx), int(default),
                                             key=f"exam_val_{i}", disabled=(opt == "Not Given"))
                else:
                    val = st.text_input(f"{exam_name} Score", placeholder="Enter score",
                                       key=f"exam_val_{i}", disabled=(opt == "Not Given"))
                exam_widgets.append((exam_name, opt, val))

        st.markdown("<div class='section-header'>📄 Application Documents</div>", unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1:
            sop_qual    = st.selectbox("SOP Quality", ["Strong – clear goals & achievements", "Average – needs polish", "Weak – vague/generic"])
        with d2:
            lor_count   = st.number_input("Number of LORs", 0, 5, 2)
            lor_qual    = st.selectbox("LOR Strength", ["Strong", "Average", "Weak"])
        with d3:
            resume_qual = st.selectbox("Resume Quality", ["Strong – detailed projects & skills", "Average – standard format", "Weak – incomplete"])

        submitted = st.form_submit_button("🤖 Evaluate My Profile & Find Universities →", use_container_width=True)

    if submitted:
        # Build dynamic exam_scores dict from widget values
        exam_scores_dict = {
            name: (val if opt == "Score entered" else "Not Given")
            for name, opt, val in exam_widgets
        }
        saved_uni = d.get("current_uni", "").strip()
        profile = {
            "student_name":    name,
            "target_country":  cc,
            "target_degree":   degr,
            "cgpa":            cgpa,
            "backlogs":        backlogs,
            "work_exp_yrs":    work_exp,
            "internships":     internships,
            "research_papers": research,
            "university":      saved_uni,
            "exam_scores":     exam_scores_dict,
            "sop":             sop_qual,
            "lor_count":       lor_count,
            "lor_quality":     lor_qual,
            "resume":          resume_qual,
        }
        st.session_state["data"]["profile"] = profile
        with st.spinner("🤖 AI is evaluating your profile, matching universities & fetching your college ranking…"):
            try:
                result = ai_phase2(profile)
                st.session_state["data"]["phase2_result"] = result
                if saved_uni:
                    ranking = ai_ranking(saved_uni)
                    st.session_state["data"]["uni_ranking"] = ranking
            except Exception as e:
                st.error(f"AI Error: {e}")
                st.stop()
        st.rerun()

    p2_res = st.session_state["data"].get("phase2_result")
    if p2_res:
        # ── University Ranking Card ──
        uni_rnk = st.session_state["data"].get("uni_ranking")
        if uni_rnk:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>🏅 Your University World Ranking</div>", unsafe_allow_html=True)
            tier_color = {"Tier 1 (Top 100)": "#34d399", "Tier 2 (101-500)": "#818cf8", "Tier 3 (501+)": "#fbbf24", "Unranked": "#94a3b8"}.get(uni_rnk.get("tier",""), "#818cf8")
            rk1, rk2, rk3 = st.columns([1, 1, 2], gap="large")
            with rk1:
                st.markdown(f"""
                <div class="rank-card">
                    <div class="rank-label">🏅 World Ranking</div>
                    <div class="rank-num" style="color:{tier_color};">{uni_rnk.get('world_rank','N/A')}</div>
                    <div class="rank-name">{uni_rnk.get('name','')}</div>
                    <div class="rank-tier" style="color:{tier_color};background:{tier_color}18;border-color:{tier_color}44;">{uni_rnk.get('tier','')}</div>
                    <div style="font-size:0.67rem;color:#64748b;margin-top:8px;">Source: {uni_rnk.get('ranking_source','QS World Rankings')}</div>
                </div>
                """, unsafe_allow_html=True)
            with rk2:
                st.markdown(f"""
                <div class="result-card">
                    <h3>🎯 National Rank</h3>
                    <p>{uni_rnk.get('national_rank','N/A')}</p>
                </div>
                <div class="result-card" style="margin-top:8px;">
                    <h3>📚 Known For</h3>
                    <p>{uni_rnk.get('known_for','')}</p>
                </div>
                """, unsafe_allow_html=True)
            with rk3:
                st.markdown(f"""
                <div style="background:rgba(248,113,113,0.07);border:1px solid rgba(248,113,113,0.2);border-radius:14px;padding:1.1rem 1.3rem;height:100%;">
                    <div style="font-size:0.72rem;color:#f87171;font-weight:700;margin-bottom:6px;">⚡ HOW THIS RANK AFFECTS YOUR ADMISSIONS</div>
                    <div style="font-size:0.87rem;color:#fca5a5;line-height:1.6;">{uni_rnk.get('rank_impact','')}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        scores  = p2_res.get("profile_score", {})
        overall = scores.get("overall", 70)
        sc_color = "#34d399" if overall >= 75 else ("#fbbf24" if overall >= 55 else "#f87171")

        st.markdown("<div class='section-header'>📊 Your Profile Score</div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns([1, 2], gap="large")

        with sc1:
            st.markdown(f"""
            <div style="text-align:center;padding:2rem 1.5rem;
                        background:linear-gradient(135deg,{sc_color}12,{sc_color}06);
                        border:2px solid {sc_color};border-radius:20px;
                        box-shadow:0 8px 32px {sc_color}20;">
                <div style="font-size:0.72rem;color:{sc_color};font-weight:700;text-transform:uppercase;letter-spacing:0.12em;">Overall Score</div>
                <div style="font-size:4.5rem;font-weight:900;color:{sc_color};line-height:1.1;">{overall}</div>
                <div style="font-size:0.8rem;color:{sc_color};font-weight:600;opacity:0.8;">out of 100</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='result-card' style='margin-top:0.8rem;'><p>{p2_res.get('eligibility_summary','')}</p></div>", unsafe_allow_html=True)

        with sc2:
            cats = ["Academics", "Exams", "Experience", "Documents", "Research"]
            vals = [scores.get("academics",70), scores.get("exams",70), scores.get("experience",70), scores.get("documents",70), scores.get("research",50)]
            fig_r = go.Figure(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself",
                line=dict(color=sc_color, width=2),
                fillcolor=f"rgba({int(sc_color[1:3],16)},{int(sc_color[3:5],16)},{int(sc_color[5:7],16)},0.18)"
            ))
            fig_r.update_layout(
                polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(255,255,255,0.08)",color="#64748b"),bgcolor="rgba(0,0,0,0)",angularaxis=dict(color="#94a3b8")),
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8",family="Inter"),
                height=280, margin=dict(t=20,b=20,l=20,r=20), showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)

        missing = p2_res.get("missing_exams", [])
        if missing:
            st.warning(f"⚠️ Missing required exams: **{', '.join(missing)}** — this reduces eligibility at some universities.")

        # Universities
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🏫 Matched Universities</div>", unsafe_allow_html=True)
        unis = p2_res.get("universities", [])
        tier_cfg = {
            "Ambitious": ("#f87171","linear-gradient(90deg,#f87171,#ef4444)","rgba(248,113,113,0.28)"),
            "Moderate":  ("#818cf8","linear-gradient(90deg,#818cf8,#6366f1)","rgba(129,140,248,0.28)"),
            "Safe":      ("#34d399","linear-gradient(90deg,#34d399,#10b981)","rgba(52,211,153,0.28)"),
        }
        elig_cfg = {
            "Eligible":     ("✅","#34d399","rgba(52,211,153,0.12)"),
            "Conditional":  ("⚠️","#fbbf24","rgba(251,191,36,0.12)"),
            "Not Eligible": ("❌","#f87171","rgba(248,113,113,0.12)"),
        }
        for tier_name, tab in zip(["Ambitious","Moderate","Safe"], st.tabs(["🚀 Ambitious","🎯 Moderate","✅ Safe"])):
            with tab:
                tier_unis = [u for u in unis if u.get("tier") == tier_name]
                if not tier_unis:
                    st.info(f"No {tier_name} universities returned."); continue
                color, bar, bdr = tier_cfg.get(tier_name, tier_cfg["Moderate"])
                cols_u = st.columns(min(3, len(tier_unis)), gap="small")
                for i, uni in enumerate(tier_unis):
                    e_icon, e_color, e_bg = elig_cfg.get(uni.get("eligibility","Eligible"), elig_cfg["Eligible"])
                    with cols_u[i % len(cols_u)]:
                        st.markdown(f"""
                        <div class="uni-card">
                            <div class="uc-bar" style="background:{bar};"></div>
                            <div class="uc-body">
                                <div style="font-size:0.6rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:{color};background:{color}18;border:1px solid {bdr};border-radius:50px;display:inline-block;padding:3px 10px;margin-bottom:8px;">
                                    {"🏛️ Public" if uni.get("type")=="Public" else "🏢 Private"}
                                </div>
                                <div class="uc-name">🎓 {uni.get('name','')}</div>
                                <div style="display:inline-flex;align-items:center;gap:4px;border-radius:50px;padding:3px 10px;font-size:0.68rem;font-weight:700;color:{e_color};background:{e_bg};border:1px solid {bdr};margin-bottom:8px;">{e_icon} {uni.get('eligibility','')}</div>
                                <div style="font-size:0.75rem;color:#64748b;margin-bottom:6px;">Match: <strong style="color:{color};">{uni.get('match_score',70)}%</strong></div>
                                <div style="font-size:0.72rem;color:#94a3b8;margin-bottom:10px;line-height:1.5;">{uni.get('notes','')}</div>
                                <div class="uc-fees">
                                    <div class="uc-fee"><div class="uc-fee-lbl">Tuition</div><div class="uc-fee-val" style="color:#818cf8;">₹{uni.get('tuition_inr_lakhs','?')}L</div></div>
                                    <div class="uc-fee"><div class="uc-fee-lbl">Living/yr</div><div class="uc-fee-val" style="color:#fbbf24;">₹{uni.get('living_inr_lakhs','?')}L</div></div>
                                    <div class="uc-fee"><div class="uc-fee-lbl">Total</div><div class="uc-fee-val" style="color:#34d399;">₹{uni.get('total_inr_lakhs','?')}L</div></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>💡 AI Suggestions</div>", unsafe_allow_html=True)
        for sug in p2_res.get("suggestions", []):
            st.markdown(f"<div class='tip-box'>💡 {sug}</div>", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🎯 Select Your Target University</div>", unsafe_allow_html=True)
        uni_names = [u["name"] for u in unis]
        if uni_names:
            sel_uni = st.selectbox("Choose university to proceed with:", uni_names)
            sel_obj = next((u for u in unis if u["name"] == sel_uni), None)
            if sel_obj:
                st.markdown(f"""
                <div style='background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.3);border-radius:14px;padding:1rem 1.3rem;display:flex;gap:1.5rem;flex-wrap:wrap;'>
                    <div><span style='color:#64748b;font-size:0.7rem;'>Selected:</span> <strong style='color:#e2e8f0;'>{sel_obj['name']}</strong></div>
                    <div><span style='color:#64748b;font-size:0.7rem;'>Total Cost:</span> <strong style='color:#34d399;'>₹{sel_obj.get('total_inr_lakhs','?')} Lakhs</strong></div>
                    <div><span style='color:#64748b;font-size:0.7rem;'>Tier:</span> <strong style='color:#818cf8;'>{sel_obj.get('tier','')}</strong></div>
                </div>
                """, unsafe_allow_html=True)
            col_p2 = st.columns([3,1])[1]
            with col_p2:
                if st.button("Proceed to Phase 3 — Finance & ROI →", use_container_width=True):
                    st.session_state["data"]["selected_uni"]     = sel_uni
                    st.session_state["data"]["selected_uni_obj"] = sel_obj
                    st.session_state["phase"]     = 3
                    st.session_state["max_phase"] = max(3, st.session_state["max_phase"])
                    st.rerun()

# ────────────────────────────────────────────────────────────────────────────
# PHASE 3 — Finance
# ────────────────────────────────────────────────────────────────────────────
elif phase == 3:
    d       = st.session_state["data"]
    cntry   = d.get("country") or "USA 🇺🇸"
    degr    = d.get("degree") or "MS Computer Science"
    sel_uni = d.get("selected_uni") or "Your University"
    sel_obj = d.get("selected_uni_obj") or {}
    total   = sel_obj.get("total_inr_lakhs", 60)

    st.markdown(f"""
    <div class="hero-phase">
        <div class="phase-badge">📍 Phase 3 of 5 &nbsp;·&nbsp; {sel_uni}</div>
        <h1>💰 Scholarships, Loans & ROI</h1>
        <p>Discover scholarships, compare education loans, and see your Return on Investment for studying <strong>{degr}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    p3_res = d.get("phase3_result")
    if not p3_res:
        if st.button("🤖 Generate Financial Plan →", use_container_width=False):
            with st.spinner("💰 AI is building your financial plan…"):
                try:
                    result = ai_phase3(cntry, degr, sel_uni, total, d.get("profile",{}))
                    st.session_state["data"]["phase3_result"] = result
                except Exception as e:
                    st.error(f"AI Error: {e}"); st.stop()
            st.rerun()
    else:
        schols = p3_res.get("scholarships", [])
        loans  = p3_res.get("loans", [])
        roi    = p3_res.get("roi", {})
        tab_s, tab_l, tab_r = st.tabs(["🎓 Scholarships", "🏦 Education Loans", "📊 ROI Analysis"])

        with tab_s:
            st.markdown("<div class='section-header'>🎓 Available Scholarships</div>", unsafe_allow_html=True)
            type_col = {"Government":"#34d399","University":"#818cf8","International":"#fbbf24","Private":"#f472b6"}
            s_cols = st.columns(3, gap="small")
            for i, sch in enumerate(schols):
                c = sch.get("color") or type_col.get(sch.get("type",""), "#818cf8")
                with s_cols[i % 3]:
                    st.markdown(f"""
                    <div class="fin-card">
                        <div class="fc-top" style="background:linear-gradient(90deg,{c},{c}66);"></div>
                        <div class="fc-body">
                            <div class="fc-tag" style="color:{c};background:{c}18;border:1px solid {c}44;">{sch.get('type','')}</div>
                            <div class="fc-name">🏆 {sch.get('name','')}</div>
                            <div class="fc-desc">{sch.get('eligibility','')}</div>
                            <div class="fc-amt" style="color:{c};">{sch.get('amount','')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if sch.get("link"):
                        st.markdown(f"<a href='{sch['link']}' target='_blank' style='font-size:0.72rem;color:#667eea;'>🔗 Apply →</a>", unsafe_allow_html=True)

        with tab_l:
            st.markdown("<div class='section-header'>🏦 Education Loan Options</div>", unsafe_allow_html=True)
            l_colors = ["#34d399","#818cf8","#fbbf24"]
            l_cols = st.columns(len(loans) if loans else 1, gap="small")
            for i, loan in enumerate(loans):
                lc = l_colors[i % len(l_colors)]
                with l_cols[i % len(l_cols)]:
                    st.markdown(f"""
                    <div class="fin-card">
                        <div class="fc-top" style="background:linear-gradient(90deg,{lc},{lc}66);"></div>
                        <div class="fc-body">
                            <div style="font-size:1.6rem;margin-bottom:6px;">🏦</div>
                            <div class="fc-name">{loan.get('bank','')}</div>
                            <div class="fc-amt" style="color:{lc};">{loan.get('rate','')}</div>
                            <div class="fc-desc" style="margin-top:4px;">Max: {loan.get('max_amount','')}</div>
                            <div class="fc-desc">{loan.get('features','')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if loan.get("link"):
                        st.markdown(f"<a href='{loan['link']}' target='_blank' style='font-size:0.72rem;color:#667eea;'>🔗 Apply →</a>", unsafe_allow_html=True)

        with tab_r:
            st.markdown("<div class='section-header'>📊 Return on Investment</div>", unsafe_allow_html=True)
            vc = {"Excellent":"#34d399","Good":"#818cf8","Moderate":"#fbbf24","Poor":"#f87171"}
            rc = vc.get(roi.get("roi_verdict","Good"),"#818cf8")
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("Total Cost",         f"₹{roi.get('total_cost_lakhs','?')}L")
            r2.metric("Scholarship Savings",f"₹{roi.get('scholarship_saving_lakhs','?')}L")
            r3.metric("Net Cost",           f"₹{roi.get('net_cost_lakhs','?')}L")
            r4.metric("Salary/yr",          f"₹{roi.get('expected_salary_inr_lakhs_yr','?')}L")
            rr1,rr2 = st.columns(2)
            rr1.metric("Payback Period", f"{roi.get('payback_years','?')} years")
            rr2.metric("5-Year Net Gain",f"₹{roi.get('5yr_net_gain_lakhs','?')}L")
            st.markdown(f"""<div style="text-align:center;margin:1rem 0;background:linear-gradient(135deg,{rc}12,{rc}06);border:2px solid {rc};border-radius:16px;padding:1rem;">
                <div style="font-size:0.72rem;color:{rc};font-weight:700;text-transform:uppercase;letter-spacing:0.1em;">ROI Verdict</div>
                <div style="font-size:2.5rem;font-weight:900;color:{rc};">{roi.get('roi_verdict','')}</div>
            </div>""", unsafe_allow_html=True)
            # Chart
            sy = roi.get("expected_salary_inr_lakhs_yr",20); nc = roi.get("net_cost_lakhs",40)
            yrs_p = list(range(1,8))
            fig_roi = go.Figure()
            fig_roi.add_trace(go.Scatter(x=yrs_p,y=[round(sy*y,1) for y in yrs_p],name="Cumulative Earnings (₹L)",mode="lines+markers",line=dict(color="#34d399",width=3),fill="tozeroy",fillcolor="rgba(52,211,153,0.08)"))
            fig_roi.add_trace(go.Scatter(x=yrs_p,y=[nc]*7,name="Net Cost (₹L)",mode="lines",line=dict(color="#f87171",width=2,dash="dash")))
            fig_roi.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#94a3b8",family="Inter"),xaxis=dict(title="Years After Graduation",gridcolor="rgba(255,255,255,0.05)"),yaxis=dict(title="₹ Lakhs",gridcolor="rgba(255,255,255,0.05)"),legend=dict(orientation="h",y=-0.2),margin=dict(t=20,b=20),height=300)
            st.plotly_chart(fig_roi, use_container_width=True)
            if p3_res.get("best_value_note"):
                st.markdown(f"<div class='tip-box'>💡 {p3_res['best_value_note']}</div>", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_p3 = st.columns([3,1])[1]
        with col_p3:
            if st.button("Proceed to Phase 4 — Accommodation →", use_container_width=True):
                st.session_state["phase"]     = 4
                st.session_state["max_phase"] = max(4, st.session_state["max_phase"])
                st.rerun()

# ────────────────────────────────────────────────────────────────────────────
# PHASE 4 — Accommodation
# ────────────────────────────────────────────────────────────────────────────
elif phase == 4:
    d       = st.session_state["data"]
    sel_uni = d.get("selected_uni") or "Your University"
    cntry   = d.get("country") or "USA 🇺🇸"

    st.markdown(f"""
    <div class="hero-phase">
        <div class="phase-badge">📍 Phase 4 of 5 &nbsp;·&nbsp; {sel_uni}</div>
        <h1>🏠 Accommodation Assistance</h1>
        <p>Discover on-campus housing and nearby rental options near <strong>{sel_uni}</strong> — compared by cost, distance, and comfort.</p>
    </div>
    """, unsafe_allow_html=True)

    p4_res = d.get("phase4_result")
    if not p4_res:
        if st.button("🤖 Find Accommodation Options →", use_container_width=False):
            with st.spinner("🏠 AI is finding the best accommodation for you…"):
                try:
                    result = ai_phase4(sel_uni, cntry)
                    st.session_state["data"]["phase4_result"] = result
                except Exception as e:
                    st.error(f"AI Error: {e}"); st.stop()
            st.rerun()
    else:
        hostel  = p4_res.get("hostel", {})
        rentals = p4_res.get("rentals", [])

        st.markdown("<div class='section-header'>🏫 On-Campus Housing</div>", unsafe_allow_html=True)
        if hostel.get("available"):
            h1, h2 = st.columns([2,1], gap="large")
            with h1:
                st.markdown(f"""
                <div class='result-card' style='border-color:rgba(52,211,153,0.35);'>
                    <div style='display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem;'>
                        <span style='font-size:2rem;'>🏠</span>
                        <div><h3 style='margin:0;'>{hostel.get('name','University Housing')}</h3>
                        <span style='font-size:0.72rem;color:#34d399;font-weight:700;'>✅ Available</span></div>
                    </div>
                    <p style='margin-bottom:0.8rem;'>{hostel.get('notes','')}</p>
                    <div style='display:flex;flex-wrap:wrap;gap:6px;'>
                        {''.join([f"<span class='info-pill'>✔ {inc}</span>" for inc in hostel.get('inclusions',[])])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with h2:
                st.markdown(f"""
                <div style='text-align:center;background:rgba(52,211,153,0.08);border:2px solid rgba(52,211,153,0.4);border-radius:18px;padding:2rem 1rem;'>
                    <div style='font-size:0.7rem;color:#34d399;font-weight:700;text-transform:uppercase;'>Monthly Cost</div>
                    <div style='font-size:2.5rem;font-weight:900;color:#34d399;'>₹{hostel.get('cost_per_month_inr','?')}<span style='font-size:1rem;'>/mo</span></div>
                </div>
                """, unsafe_allow_html=True)
                if hostel.get("apply_link"):
                    st.markdown(f"<br><a href='{hostel['apply_link']}' target='_blank' style='display:block;text-align:center;background:linear-gradient(135deg,#34d399,#10b981);color:white;padding:0.6rem;border-radius:10px;font-weight:700;font-size:0.85rem;text-decoration:none;'>Apply for Hostel →</a>", unsafe_allow_html=True)
        else:
            st.markdown("""<div class='result-card' style='border-color:rgba(248,113,113,0.35);'>
                <div style='display:flex;align-items:center;gap:0.8rem;'>
                    <span style='font-size:2rem;'>🏫</span>
                    <div><h3 style='margin:0;color:#fca5a5;'>On-Campus Housing Unavailable / Full</h3>
                    <p style='margin:4px 0 0;'>Check nearby rental options below.</p></div>
                </div></div>""", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🏢 Nearby Rental Options</div>", unsafe_allow_html=True)
        rc_pal = ["#818cf8","#fbbf24","#f472b6","#60a5fa"]
        r_cols = st.columns(min(4, len(rentals)) if rentals else 1, gap="small")
        for i, rent in enumerate(rentals):
            rc_c = rc_pal[i % len(rc_pal)]
            r_rgb = f"{int(rc_c[1:3],16)},{int(rc_c[3:5],16)},{int(rc_c[5:7],16)}"
            with r_cols[i % len(r_cols)]:
                st.markdown(f"""
                <div class="accom-card" style="border-color:rgba({r_rgb},0.3);">
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.7rem;'>
                        <div><div style='font-size:1rem;font-weight:800;color:#f1f5f9;'>{rent.get('type','')}</div>
                        <div style='font-size:0.75rem;color:#64748b;'>📍 {rent.get('area','')}</div></div>
                        <div style='text-align:right;'>
                            <div style='font-size:1.2rem;font-weight:900;color:{rc_c};'>₹{rent.get('cost_per_month_inr','?')}</div>
                            <div style='font-size:0.65rem;color:#64748b;'>/month</div>
                        </div>
                    </div>
                    <div style='font-size:0.78rem;color:#94a3b8;margin-bottom:6px;'>🚌 {rent.get('distance_to_campus','')} from campus</div>
                    <div style='font-size:0.78rem;color:#a5b4fc;margin-bottom:8px;'>✨ {rent.get('pros','')}</div>
                    <div style='font-size:0.7rem;color:#475569;'>List on: {rent.get('listing_site','')}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>💡 Accommodation Tips</div>", unsafe_allow_html=True)
        for tip in p4_res.get("tips", []):
            st.markdown(f"<div class='tip-box'>💡 {tip}</div>", unsafe_allow_html=True)
        if p4_res.get("best_recommendation"):
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(102,126,234,0.12),rgba(118,75,162,0.12));border:2px solid rgba(102,126,234,0.4);border-radius:16px;padding:1.2rem 1.5rem;margin-top:1rem;'>
                <div style='font-size:0.8rem;color:#a5b4fc;font-weight:700;margin-bottom:6px;'>🏆 AI RECOMMENDATION</div>
                <div style='font-size:0.9rem;color:#e2e8f0;line-height:1.6;'>{p4_res['best_recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_p4 = st.columns([3,1])[1]
        with col_p4:
            if st.button("Proceed to Phase 5 — Full Report →", use_container_width=True):
                st.session_state["phase"]     = 5
                st.session_state["max_phase"] = max(5, st.session_state["max_phase"])
                st.rerun()

# ────────────────────────────────────────────────────────────────────────────
# PHASE 5 — Full Report & Download
# ────────────────────────────────────────────────────────────────────────────
elif phase == 5:
    d    = st.session_state["data"]
    name = d.get("student_name", "Student")

    st.markdown(f"""
    <div class="hero-phase" style="background:linear-gradient(135deg,#0a2016,#0f2a1e,#0a1628);">
        <div class="phase-badge" style="background:rgba(52,211,153,0.15);border-color:rgba(52,211,153,0.4);color:#34d399;">🏆 Journey Complete &nbsp;·&nbsp; Phase 5 of 5</div>
        <h1>📋 Your Complete Study Abroad Report</h1>
        <p>All 4 phases completed, <strong>{name}</strong>! Here is your full personalised summary — review it below and download as HTML.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary stats row ──
    p2_res  = d.get("phase2_result") or {}
    p3_res  = d.get("phase3_result") or {}
    scores  = p2_res.get("profile_score", {})
    roi     = p3_res.get("roi", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 Profile Score",    f"{scores.get('overall','—')}/100")
    m2.metric("🏛️ Target Uni",       (d.get("selected_uni") or "N/A")[:18]+"…" if len(d.get("selected_uni") or "") > 18 else (d.get("selected_uni") or "N/A"))
    m3.metric("💰 Net Cost",         f"₹{roi.get('net_cost_lakhs','?')}L")
    m4.metric("📈 5-Yr Gain",        f"₹{roi.get('5yr_net_gain_lakhs','?')}L")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Inline Report Preview ──
    st.markdown("<div class='section-header'>📄 Report Preview</div>", unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2, gap="large")

    with col_r1:
        # Phase 1 Summary
        st.markdown("""<div class="report-section"><h3>📍 Phase 1 — Planning</h3>""", unsafe_allow_html=True)
        p1r = d.get("phase1_result") or {}
        cg  = p1r.get("country_guide", {})
        ex = p1r.get("exams", {})
        st.markdown(f"**📝 Required Exams:** {', '.join(ex.get('required',[]))}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Phase 3 Summary
        st.markdown("""<div class="report-section"><h3>💰 Phase 3 — Finance</h3>""", unsafe_allow_html=True)
        verdict_emoji = {"Excellent":"🌟","Good":"✅","Moderate":"⚠️","Poor":"❌"}.get(roi.get("roi_verdict",""),"")
        st.markdown(f"""
| Metric | Value |
|--------|-------|
| Total Cost | ₹{roi.get('total_cost_lakhs','?')} Lakhs |
| Scholarship Savings | ₹{roi.get('scholarship_saving_lakhs','?')} Lakhs |
| Net Cost | ₹{roi.get('net_cost_lakhs','?')} Lakhs |
| Expected Salary/yr | ₹{roi.get('expected_salary_inr_lakhs_yr','?')} Lakhs |
| Payback Period | {roi.get('payback_years','?')} years |
| 5-Year Net Gain | ₹{roi.get('5yr_net_gain_lakhs','?')} Lakhs |
| ROI Verdict | {verdict_emoji} {roi.get('roi_verdict','N/A')} |
""")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        # Phase 2 Summary
        st.markdown("""<div class="report-section"><h3>🎓 Phase 2 — Profile & Universities</h3>""", unsafe_allow_html=True)
        st.markdown(f"**Overall Score:** {scores.get('overall','—')}/100")
        ms1, ms2, ms3 = st.columns(3)
        ms1.metric("Academics", scores.get("academics","—"))
        ms2.metric("Exams",     scores.get("exams","—"))
        ms3.metric("Experience",scores.get("experience","—"))
        st.markdown(f"**Selected:** {d.get('selected_uni','N/A')}  \n**Total Cost:** ₹{(d.get('selected_uni_obj') or {}).get('total_inr_lakhs','?')} Lakhs")
        unis_count = len(p2_res.get("universities",[]))
        st.markdown(f"**Universities Analysed:** {unis_count}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Phase 4 Summary
        st.markdown("""<div class="report-section"><h3>🏠 Phase 4 — Accommodation</h3>""", unsafe_allow_html=True)
        p4r    = d.get("phase4_result") or {}
        hostel = p4r.get("hostel", {})
        status = "✅ Available" if hostel.get("available") else "❌ Not Available"
        st.markdown(f"**On-Campus Hostel:** {status}")
        if hostel.get("available"):
            st.markdown(f"**{hostel.get('name','')}** — ₹{hostel.get('cost_per_month_inr','?')}/month")
        rentals = p4r.get("rentals",[])
        if rentals:
            st.markdown(f"**Rental Options Available:** {len(rentals)}")
            st.markdown(f"**Cheapest Option:** ₹{min(r.get('cost_per_month_inr',0) for r in rentals)}/month")
        if p4r.get("best_recommendation"):
            st.markdown(f"**AI Recommendation:** {p4r['best_recommendation'][:120]}…")
        st.markdown("</div>", unsafe_allow_html=True)



    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Restart ──
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 2rem;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);border:1px solid rgba(102,126,234,0.4);border-radius:20px;box-shadow:0 12px 50px rgba(102,126,234,0.2);">
        <div style="font-size:3rem;margin-bottom:0.5rem;">🎓</div>
        <div style="font-size:1.6rem;font-weight:900;background:linear-gradient(135deg,#e2e8f0,#a5b4fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem;">All 5 Phases Complete!</div>
        <div style="font-size:0.9rem;color:#94a3b8;">You have a complete, AI-powered study abroad plan. Best of luck!</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Start a New Journey", use_container_width=False):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
