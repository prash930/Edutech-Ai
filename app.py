import streamlit as st
import groq
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ── API Key ───────────────────────────────────────────────────────────────────
GROQ_API_KEY =os.getenv("GROQ_API_KEY")

PAGES = ["🏠 Home", "🤖 AI Mentor", "📊 ROI Calculator", "🎯 Admission Predictor", "💰 Education Loan"]

st.set_page_config(
    page_title="Path to your Future",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── SIDEBAR ── */
div[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    padding-top: 1rem;
}
div[data-testid="stSidebarContent"] * { color: #e2e8f0 !important; }
div[data-testid="stSidebarContent"] .stRadio > label { color: #94a3b8 !important; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stSidebarContent"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 0.55rem 1rem;
    margin: 3px 0;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.2s;
    cursor: pointer;
}
div[data-testid="stSidebarContent"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(102,126,234,0.25);
    border-color: rgba(102,126,234,0.5);
}

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 60%, #f64f59 100%);
    padding: 3rem 2.5rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(102,126,234,0.4);
}
.hero-banner::before {
    content: "";
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-banner h1 { font-size: 3rem; font-weight: 900; margin: 0; letter-spacing: -0.02em; position: relative; }
.hero-banner p  { font-size: 1.15rem; opacity: 0.9; margin: 0.75rem 0 0; font-weight: 400; position: relative; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
    position: relative;
}

/* ── STAT CARDS ── */
.stat-card {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    border: 1px solid rgba(102,126,234,0.3);
    border-radius: 16px;
    padding: 1.5rem 1.2rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(102,126,234,0.25); }
.stat-card .s-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-card .s-val  { font-size: 2rem; font-weight: 800; color: white; }
.stat-card .s-lbl  { font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }
.stat-card .s-sub  { font-size: 0.7rem; color: #64748b; margin-top: 2px; }

/* ── FEATURE CARDS ── */
.feat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px;
    padding: 1.8rem;
    height: 100%;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}
.feat-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
}
.feat-card:hover {
    border-color: rgba(102,126,234,0.4);
    box-shadow: 0 12px 40px rgba(102,126,234,0.15);
    transform: translateY(-3px);
}
.feat-card h3 { margin: 0 0 0.6rem; font-size: 1.1rem; font-weight: 700; }
.feat-card p  { font-size: 0.85rem; opacity: 0.7; line-height: 1.6; margin: 0 0 1.2rem; }
.feat-btn {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white !important;
    padding: 0.5rem 1.2rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.2s;
}
.feat-btn:hover { opacity: 0.88; transform: scale(1.03); }

/* ── CHAT BUBBLES ── */
.chat-bubble-user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.5rem 0;
    max-width: 78%;
    margin-left: auto;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(102,126,234,0.3);
}
.chat-bubble-bot {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e2e8f0;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.5rem 0;
    max-width: 85%;
    font-size: 0.9rem;
    line-height: 1.65;
}

/* ── OFFER BOX ── */
.offer-box {
    background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.12));
    border: 2px solid #667eea;
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    margin-top: 1rem;
    box-shadow: 0 8px 32px rgba(102,126,234,0.2);
}
.offer-box h2 { color: #667eea; font-size: 3rem; font-weight: 900; margin: 0.5rem 0; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.5rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.2s, transform 0.2s !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3) !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* ── QUICK PROMPT PILLS ── */
.qpill-btn .stButton > button {
    background: rgba(102,126,234,0.15) !important;
    border: 1px solid rgba(102,126,234,0.4) !important;
    color: #a5b4fc !important;
    border-radius: 50px !important;
    font-size: 0.78rem !important;
    padding: 0.35rem 0.9rem !important;
    box-shadow: none !important;
}
.qpill-btn .stButton > button:hover {
    background: rgba(102,126,234,0.3) !important;
}

/* ── MISC ── */
.section-title {
    font-size: 1.5rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 1.2rem;
    letter-spacing: -0.01em;
}
.divider-grad {
    height: 2px;
    background: linear-gradient(90deg, #667eea33, #764ba266, #667eea33);
    border: none;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "_nav_page" not in st.session_state:
    st.session_state["_nav_page"] = PAGES[0]
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI study-abroad mentor. Ask me anything about universities, courses, scholarships, visa, or education loans!"}
    ]
if "loan_step" not in st.session_state:
    st.session_state.loan_step = 1
if "loan_data" not in st.session_state:
    st.session_state.loan_data = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2.5rem">🎓</div>
        <div style="font-size:1.2rem; font-weight:800; color:white; letter-spacing:-0.01em;">Path to your Future</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid rgba(255,255,255,0.08); margin:0.8rem 0'>", unsafe_allow_html=True)

    _selected = st.radio("Navigate", PAGES, index=PAGES.index(st.session_state["_nav_page"]))
    if _selected != st.session_state["_nav_page"]:
        st.session_state["_nav_page"] = _selected
        st.rerun()

    st.markdown("<hr style='border:1px solid rgba(255,255,255,0.08); margin:0.8rem 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding-bottom:1rem;">
        <div style="font-size:0.68rem; color:#64748b;">Built for Poonawalla Fincorp Hackathon</div>
    </div>
    """, unsafe_allow_html=True)

page = st.session_state["_nav_page"]

# ── Data ──────────────────────────────────────────────────────────────────────
ROI_DATA = {
    "USA":       {"MS Computer Science": (60, 130000, 0.82), "MBA": (80, 120000, 0.70), "MS Data Science": (55, 125000, 0.78), "MS Finance": (65, 115000, 0.68), "Nursing/Healthcare": (40, 90000, 0.85)},
    "UK":        {"MS Computer Science": (45, 95000,  0.75), "MBA": (60, 100000, 0.65), "MS Data Science": (42, 90000,  0.72), "MS Finance": (50, 95000,  0.65), "Nursing/Healthcare": (35, 75000,  0.80)},
    "Canada":    {"MS Computer Science": (40, 85000,  0.80), "MBA": (55, 90000,  0.68), "MS Data Science": (38, 82000,  0.76), "MS Finance": (45, 80000,  0.65), "Nursing/Healthcare": (32, 70000,  0.85)},
    "Australia": {"MS Computer Science": (42, 88000,  0.78), "MBA": (52, 85000,  0.66), "MS Data Science": (40, 85000,  0.74), "MS Finance": (48, 82000,  0.64), "Nursing/Healthcare": (35, 72000,  0.82)},
    "Germany":   {"MS Computer Science": (20, 75000,  0.70), "MBA": (30, 80000,  0.62), "MS Data Science": (18, 72000,  0.68), "MS Finance": (25, 70000,  0.60), "Nursing/Healthcare": (15, 60000,  0.75)},
}
USD_TO_INR = 83

# ── AI helpers ────────────────────────────────────────────────────────────────
def get_groq_client():
    return groq.Groq(api_key=GROQ_API_KEY)

def chat_with_groq(messages):
    client = get_groq_client()
    system = (
        "You are Path to your Future, a friendly and expert study-abroad mentor for Indian students. "
        "Help with: university selection, course recommendations, GRE/GMAT/IELTS prep, visa guidance, "
        "scholarships, SOP writing tips, and education loans. "
        "Keep responses concise (under 200 words), practical, and encouraging. "
        "Use ₹ for Indian rupees and $ for foreign currency when relevant."
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content

def admission_predict_groq(profile: dict) -> dict:
    client = get_groq_client()
    prompt = f"""
You are an expert university admission consultant. Given this student profile, predict admission chances.
Profile: {json.dumps(profile)}

Respond ONLY with a valid JSON object (no markdown, no explanation) with these exact keys:
{{
  "overall_score": <integer 0-100>,
  "chance_label": "<Excellent|Good|Moderate|Low>",
  "gpa_score": <integer 0-100>,
  "test_score": <integer 0-100>,
  "experience_score": <integer 0-100>,
  "eligible_universities": [
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}},
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}},
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}},
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}},
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}},
    {{"name": "<University Name>", "match_score": <integer 0-100>, "tier": "<Reach|Match|Safe>"}}
  ],
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def nav_to(target):
    st.session_state["_nav_page"] = target
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ AI-Powered · Hackathon Edition</div>
        <h1>Path to your Future</h1>
        <p>Your intelligent gateway to global education, financing & career success</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("🧑‍🎓", "12,400+", "Students Helped", "across India"),
        ("💰", "₹32L", "Avg Loan Disbursed", "per student"),
        ("🎯", "91%", "Placement Rate", "within 6 months"),
        ("🏛️", "500+", "Partner Universities", "worldwide"),
    ]
    colors = ["#818cf8", "#34d399", "#f87171", "#fbbf24"]
    for col, (icon, val, lbl, sub), color in zip([s1, s2, s3, s4], stats, colors):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="s-icon">{icon}</div>
                <div class="s-val" style="color:{color}">{val}</div>
                <div class="s-lbl">{lbl}</div>
                <div class="s-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>What can EduPath AI do for you?</div>", unsafe_allow_html=True)

    # ── Feature cards ──
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=False):
            st.markdown("""
            <div class="feat-card">
                <h3>🤖 AI Mentor</h3>
                <p>Chat with an LLM-powered mentor trained on study-abroad knowledge. Get instant answers on universities, SOP, visa, scholarships & more.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Chatting →", key="home_chat", use_container_width=True):
                nav_to("🤖 AI Mentor")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=False):
            st.markdown("""
            <div class="feat-card">
                <h3>🎯 Admission Predictor</h3>
                <p>Enter your GPA, test scores, and experience. Get AI-predicted admission chances with target and safety university recommendations.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Predict My Chances →", key="home_admit", use_container_width=True):
                nav_to("🎯 Admission Predictor")

    with col2:
        with st.container(border=False):
            st.markdown("""
            <div class="feat-card">
                <h3>📊 ROI Calculator</h3>
                <p>Compare education cost vs expected salary returns for different countries and courses. Make data-driven, informed decisions.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Calculate ROI →", key="home_roi", use_container_width=True):
                nav_to("📊 ROI Calculator")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=False):
            st.markdown("""
            <div class="feat-card">
                <h3>💰 Education Loan</h3>
                <p>Get a personalized loan offer in 3 steps. Instant eligibility check, competitive interest rates, and easy EMI options.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Apply for Loan →", key="home_loan", use_container_width=True):
                nav_to("💰 Education Loan")

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🌍 Popular Destinations at a Glance</div>", unsafe_allow_html=True)

    dest_data = pd.DataFrame({
        "Country":           ["USA 🇺🇸", "UK 🇬🇧", "Canada 🇨🇦", "Australia 🇦🇺", "Germany 🇩🇪"],
        "Avg Cost (₹L)":     [60, 45, 40, 42, 20],
        "Avg Salary (₹L/yr)": [108, 79, 70, 73, 62],
        "Admission Rate (%)": [82, 75, 80, 78, 70],
    })

    c_left, c_right = st.columns([3, 2])
    with c_left:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Avg Cost (₹L)", x=dest_data["Country"], y=dest_data["Avg Cost (₹L)"],
            marker=dict(color="#818cf8", opacity=0.9),
        ))
        fig.add_trace(go.Bar(
            name="Avg Salary/yr (₹L)", x=dest_data["Country"], y=dest_data["Avg Salary (₹L/yr)"],
            marker=dict(color="#34d399", opacity=0.9),
        ))
        fig.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            title=dict(text="Cost vs Expected Annual Salary by Country (₹ Lakhs)", font=dict(size=14, color="#e2e8f0")),
            legend=dict(orientation="h", y=-0.15, font=dict(color="#94a3b8")),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(t=45, b=20, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        fig_donut = go.Figure(go.Pie(
            labels=dest_data["Country"],
            values=dest_data["Admission Rate (%)"],
            hole=0.55,
            marker=dict(colors=["#818cf8", "#f472b6", "#34d399", "#fbbf24", "#60a5fa"]),
            textinfo="label+percent",
            textfont=dict(color="white", size=11),
        ))
        fig_donut.update_layout(
            title=dict(text="Avg Admission Rate by Country", font=dict(size=14, color="#e2e8f0")),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            showlegend=False,
            margin=dict(t=45, b=10, l=10, r=10),
            annotations=[dict(text="Admit<br>Rate", x=0.5, y=0.5, font=dict(size=13, color="#e2e8f0"), showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: AI MENTOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Mentor":
    # ── Header ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
                border-radius:16px; padding:1.5rem 2rem; margin-bottom:1.2rem;
                border:1px solid rgba(129,140,248,0.25);">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="font-size:2.5rem;">🤖</div>
            <div>
                <div style="font-size:1.4rem; font-weight:800; color:#e2e8f0; letter-spacing:-0.01em;">AI Study Abroad Mentor</div>
                <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">⚡ Powered by Groq · LLaMA 3.3 70B · Ask anything about studying abroad</div>
            </div>
            <div style="margin-left:auto; background:rgba(52,211,153,0.15); border:1px solid rgba(52,211,153,0.4);
                        border-radius:50px; padding:0.25rem 0.75rem; font-size:0.72rem; color:#34d399; font-weight:600;">
                🟢 Online
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick prompts ──
    st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.6rem;'>⚡ Quick Prompts</div>", unsafe_allow_html=True)
    qcols = st.columns(4)
    quick = [
        "🌍 Best countries for MS CS 2025?",
        "📝 GRE score for top US unis?",
        "💼 MBA UK vs USA — ROI?",
        "🏦 Education loan tips: Canada?",
    ]
    for i, q in enumerate(quick):
        with qcols[i]:
            if st.button(q, key=f"qp{i}", use_container_width=True):
                clean_q = q.split(" ", 1)[1] if q[0] in "🌍📝💼🏦" else q
                st.session_state.messages.append({"role": "user", "content": clean_q})
                with st.spinner("Thinking..."):
                    reply = chat_with_groq(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)

    # ── Chat history using native st.chat_message ──
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

    # ── Input row ──
    st.markdown("<br>", unsafe_allow_html=True)
    col_inp, col_btn = st.columns([6, 1])
    with col_inp:
        user_input = st.chat_input("Ask me anything about studying abroad…")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking…"):
                try:
                    reply = chat_with_groq(st.session_state.messages)
                except Exception as e:
                    reply = f"❌ Error: {str(e)}"
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.messages = [{"role": "assistant", "content": "👋 Chat cleared! How can I help you?"}]
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: ROI CALCULATOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 ROI Calculator":
    st.markdown("<h2 style='font-weight:800; letter-spacing:-0.02em;'>📊 Education ROI Calculator</h2>", unsafe_allow_html=True)
    st.caption("Compare cost of education vs expected salary returns")

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("Your Profile")
            country  = st.selectbox("🌍 Destination Country", list(ROI_DATA.keys()))
            course   = st.selectbox("📚 Course", list(ROI_DATA[country].keys()))
            savings  = st.number_input("💵 Savings (₹ Lakhs)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
            loan     = st.number_input("🏦 Loan Amount (₹ Lakhs)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
            duration = st.slider("📅 Course Duration (years)", 1, 4, 2)

    cost_l, salary_usd, admit_rate = ROI_DATA[country][course]
    salary_inr_l = round(salary_usd * USD_TO_INR / 100000, 1)
    total_cost   = cost_l
    annual_save  = round(salary_inr_l * 0.3, 1)
    payoff_yrs   = round(loan / annual_save, 1) if annual_save > 0 else 99
    gain_5yr     = round(salary_inr_l * 5 - total_cost, 1)
    roi_score    = min(99, max(30, int(60 + gain_5yr / max(total_cost, 1) * 20)))

    with col2:
        # Metric row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Cost", f"₹{total_cost}L")
        m2.metric("Expected Salary", f"₹{salary_inr_l}L/yr")
        m3.metric("Loan Payoff", f"{payoff_yrs} yrs")
        m4, m5, m6 = st.columns(3)
        m4.metric("5-Year Net Gain", f"₹{gain_5yr}L", delta="Profitable" if gain_5yr > 0 else "Loss")
        m5.metric("ROI Score", f"{roi_score}/100")
        m6.metric("Admission Chance", f"{int(admit_rate*100)}%")



    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2, gap="large")
    with ch1:
        st.subheader("📈 Salary Growth vs Loan Balance (5 Years)")
        years = list(range(1, 6))
        salaries = [round(salary_inr_l * (1.08 ** y), 2) for y in years]
        loan_remaining = [max(0, round(loan - annual_save * y, 1)) for y in years]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=years, y=salaries, name="Annual Salary (₹L)", mode="lines+markers",
            line=dict(color="#34d399", width=3),
            marker=dict(size=8, color="#34d399"),
            fill="tozeroy", fillcolor="rgba(52,211,153,0.1)"
        ))
        fig2.add_trace(go.Bar(
            x=years, y=loan_remaining, name="Loan Remaining (₹L)",
            marker_color="#f472b6", opacity=0.7
        ))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(title="Year", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="₹ Lakhs", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(orientation="h", y=-0.2),
            margin=dict(t=20, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with ch2:
        st.subheader(f"🌍 Country Comparison — {course}")
        comp_rows = []
        for c in ROI_DATA:
            if course in ROI_DATA[c]:
                cst, sal, adm = ROI_DATA[c][course]
                sal_inr = round(sal * USD_TO_INR / 100000, 1)
                comp_rows.append({
                    "Country": c, "Cost (₹L)": cst,
                    "Salary (₹L/yr)": sal_inr,
                    "Admission %": int(adm * 100),
                    "5-Yr ROI (₹L)": round(sal_inr * 5 - cst, 1)
                })
        comp_df = pd.DataFrame(comp_rows).sort_values("5-Yr ROI (₹L)", ascending=False).reset_index(drop=True)

        fig_comp = px.bar(
            comp_df, x="Country", y="5-Yr ROI (₹L)",
            color="5-Yr ROI (₹L)",
            color_continuous_scale=["#f472b6", "#818cf8", "#34d399"],
            text="5-Yr ROI (₹L)",
        )
        fig_comp.update_traces(texttemplate="%{text}L", textposition="outside")
        fig_comp.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            coloraxis_showscale=False,
            margin=dict(t=20, b=10),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
    st.subheader("📋 Full Comparison Table")
    st.dataframe(comp_df, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: ADMISSION PREDICTOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Admission Predictor":
    st.markdown("<h2 style='font-weight:800; letter-spacing:-0.02em;'>🎯 AI Admission Predictor</h2>", unsafe_allow_html=True)
    st.caption("Get AI-powered admission chances and university recommendations")

    with st.form("admit_form"):
        st.subheader("Your Academic Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            gpa      = st.number_input("GPA / CGPA (out of 10)", 0.0, 10.0, 7.5, 0.1)
            backlogs = st.number_input("Number of Backlogs", 0, 20, 0)
        with c2:
            gre   = st.number_input("GRE Score (260–340, 0 if NA)", 0, 340, 310)
            ielts = st.number_input("IELTS Score (0 if NA)", 0.0, 9.0, 7.0, 0.5)
        with c3:
            work_exp = st.number_input("Work Experience (years)", 0.0, 10.0, 1.0, 0.5)
            research = st.number_input("Research Papers Published", 0, 20, 0)

        st.subheader("Target Details")
        d1, d2, d3 = st.columns(3)
        with d1:
            target_country = st.selectbox("Target Country", ["USA", "UK", "Canada", "Australia", "Germany"])
        with d2:
            target_course = st.selectbox("Course", ["MS Computer Science", "MBA", "MS Data Science", "MS Finance", "Nursing/Healthcare"])
        with d3:
            uni_tier = st.selectbox("Target University Tier", ["Top 10", "Top 50", "Top 100", "Any"])

        internships = st.number_input("Internships Completed", 0, 10, 1)
        predict_btn = st.form_submit_button("🔮 Predict My Chances", use_container_width=True)

    if predict_btn:
        profile = {
            "gpa": gpa, "backlogs": backlogs, "gre": gre, "ielts": ielts,
            "work_experience_years": work_exp, "research_papers": research,
            "internships": internships, "target_country": target_country,
            "target_course": target_course, "university_tier": uni_tier
        }
        with st.spinner("🤖 AI is analyzing your profile..."):
            try:
                result = admission_predict_groq(profile)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        score = result.get("overall_score", 70)
        label = result.get("chance_label", "Good")
        color_map = {"Excellent": "#34d399", "Good": "#818cf8", "Moderate": "#fbbf24", "Low": "#f87171"}
        color = color_map.get(label, "#818cf8")

        st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2], gap="large")

        with col1:
            st.markdown(f"""
            <div style="text-align:center; padding:2.5rem 1.5rem; background:linear-gradient(135deg,{color}18,{color}08);
                        border:2px solid {color}; border-radius:20px; box-shadow: 0 8px 32px {color}30;">
                <div style="font-size:0.8rem; color:{color}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Admission Chance</div>
                <div style="font-size:5rem; font-weight:900; color:{color}; line-height:1.1;">{score}%</div>
                <div style="font-size:1.3rem; font-weight:700; color:{color};">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            g1, g2, g3 = st.columns(3)
            g1.metric("GPA Score",   f"{result.get('gpa_score', 70)}/100")
            g2.metric("Test Score",  f"{result.get('test_score', 70)}/100")
            g3.metric("Experience",  f"{result.get('experience_score', 70)}/100")

            cats = ["GPA", "Test Scores", "Experience", "Research", "Internships"]
            vals = [
                result.get("gpa_score", 70), result.get("test_score", 70),
                result.get("experience_score", 70),
                min(100, research * 25 + 50), min(100, internships * 20 + 40)
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself",
                line=dict(color=color, width=2),
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2)"
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)", color="#64748b"),
                    bgcolor="rgba(0,0,0,0)",
                    angularaxis=dict(color="#94a3b8"),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                height=280, margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
        st.markdown("### 🎓 Universities You're Eligible For")

        eligible = result.get("eligible_universities", [])
        tier_colors = {
            "Reach": ("#f87171", "rgba(248,113,113,0.12)"),
            "Match": ("#818cf8", "rgba(129,140,248,0.12)"),
            "Safe":  ("#34d399", "rgba(52,211,153,0.12)"),
        }
        tier_icons = {"Reach": "🚀", "Match": "🎯", "Safe": "✅"}

        if eligible:
            cols = st.columns(3)
            for idx, uni in enumerate(eligible):
                name  = uni.get("name", "Unknown")
                score = uni.get("match_score", 70)
                tier  = uni.get("tier", "Match")
                bdr, bg = tier_colors.get(tier, tier_colors["Match"])
                icon = tier_icons.get(tier, "🎯")
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background:linear-gradient(145deg,#1e1b4b,#0f0c29);
                                border:1px solid {bdr}25; border-radius:20px; overflow:hidden;
                                margin:8px 0; box-shadow:0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px {bdr}15;">
                        <div style="height:3px; background:linear-gradient(90deg,{bdr},{bdr}44,transparent);"></div>
                        <div style="padding:1.3rem 1.4rem;">
                            <div style="display:inline-flex; align-items:center; gap:5px;
                                        background:{bdr}18; border:1px solid {bdr}45;
                                        border-radius:50px; padding:3px 11px; margin-bottom:14px;">
                                <span>{icon}</span>
                                <span style="font-size:0.65rem; font-weight:800; color:{bdr};
                                             text-transform:uppercase; letter-spacing:0.1em;">{tier}</span>
                            </div>
                            <div style="font-size:1rem; font-weight:700; color:#f1f5f9;
                                        line-height:1.4; margin-bottom:16px; min-height:2.8rem;">
                                🏛️ {name}
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
                                <span style="font-size:0.65rem; color:#475569; font-weight:600;
                                             text-transform:uppercase; letter-spacing:0.07em;">Eligibility Match</span>
                                <span style="font-size:1.4rem; font-weight:900; color:{bdr};
                                             line-height:1;">{score}%</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.05); border-radius:50px; height:8px; overflow:hidden;">
                                <div style="width:{score}%; height:100%; border-radius:50px;
                                            background:linear-gradient(90deg,{bdr}88,{bdr});
                                            box-shadow:0 0 10px {bdr}66;"></div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No university data returned. Try re-running the prediction.")

        st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)
        st.markdown("### 💡 Tips to Improve Your Profile")
        for i, tip in enumerate(result.get("tips", []), 1):
            st.markdown(f"""<div style='padding:0.75rem 1rem; background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); border-radius:10px; margin:6px 0; font-size:0.9rem;'>✨ <strong>Tip {i}:</strong> {tip}</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: EDUCATION LOAN
# ════════════════════════════════════════════════════════════════════════════
# PAGE: SCHOLARSHIPS & LOANS
# ════════════════════════════════════════════════════════════════════════════
elif page == "💰 Education Loan":
    st.markdown("""
    <div class="hero-banner" style="padding:2rem 2.5rem; margin-bottom:1.5rem;">
        <div class="hero-badge">🎓 Curated for Indian Students</div>
        <h1 style="font-size:2rem;">💰 Scholarships & Education Loans</h1>
        <p>Government scholarships & top lenders — all in one place</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Extra CSS for this page ──
    st.markdown("""
    <style>
    .schol-card {
        background: linear-gradient(145deg, #1e1b4b, #0f0c29);
        border: 1px solid rgba(129,140,248,0.22);
        border-radius: 20px; overflow: hidden;
        margin: 8px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        transition: transform 0.22s, box-shadow 0.22s;
        height: 100%;
    }
    .schol-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(102,126,234,0.18); }
    .schol-card .sc-top  { height: 4px; }
    .schol-card .sc-body { padding: 1.2rem 1.4rem; }
    .schol-card .sc-tag  {
        display: inline-block;
        border-radius: 50px; padding: 3px 11px; font-size: 0.62rem;
        font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em;
        margin-bottom: 10px;
    }
    .schol-card .sc-name { font-size: 0.97rem; font-weight: 700; color: #f1f5f9; line-height: 1.4; margin-bottom: 8px; }
    .schol-card .sc-desc { font-size: 0.78rem; color: #94a3b8; line-height: 1.55; margin-bottom: 12px; }
    .schol-card .sc-amt  { font-size: 1.1rem; font-weight: 800; margin-bottom: 4px; }
    .schol-card .sc-link {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important; text-decoration: none;
        padding: 0.38rem 1rem; border-radius: 8px;
        font-size: 0.75rem; font-weight: 700;
        margin-top: 8px; transition: opacity 0.2s;
    }
    .schol-card .sc-link:hover { opacity: 0.82; }
    .loan-card {
        background: linear-gradient(145deg, #0f172a, #1e1b4b);
        border: 1px solid rgba(52,211,153,0.2);
        border-radius: 20px; overflow: hidden;
        margin: 8px 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        transition: transform 0.22s, box-shadow 0.22s;
        height: 100%;
    }
    .loan-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(52,211,153,0.12); }
    .loan-card .lc-top  { height: 4px; }
    .loan-card .lc-body { padding: 1.2rem 1.4rem; }
    .loan-card .lc-logo { font-size: 1.7rem; margin-bottom: 6px; }
    .loan-card .lc-name { font-size: 1rem; font-weight: 800; color: #f1f5f9; margin-bottom: 4px; }
    .loan-card .lc-rate { font-size: 1.2rem; font-weight: 900; margin-bottom: 2px; }
    .loan-card .lc-max  { font-size: 0.75rem; color: #64748b; margin-bottom: 8px; }
    .loan-card .lc-feat { font-size: 0.75rem; color: #94a3b8; line-height: 1.55; margin-bottom: 10px; }
    .loan-card .lc-link {
        display: inline-block;
        background: linear-gradient(135deg, #34d399, #059669);
        color: white !important; text-decoration: none;
        padding: 0.38rem 1rem; border-radius: 8px;
        font-size: 0.75rem; font-weight: 700;
        margin-top: 6px; transition: opacity 0.2s;
    }
    .loan-card .lc-link:hover { opacity: 0.82; }
    </style>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 1 — GOVERNMENT SCHOLARSHIPS
    # ════════════════════════════════════════════
    st.markdown("<div class='section-title'>🏛️ Government Scholarships for Indian Students</div>", unsafe_allow_html=True)

    scholarships = [
        {
            "name": "National Overseas Scholarship (NOS)",
            "tag": "Central Govt", "tag_color": "#818cf8", "bar": "linear-gradient(90deg,#818cf8,#a78bfa)",
            "desc": "For SC/ST/OBC students pursuing Masters or PhD abroad. Covers tuition, living, travel & contingency.",
            "amount": "Up to ₹25 Lakhs/yr",
            "amount_color": "#818cf8",
            "link": "https://nosmsje.gov.in/",
            "link_text": "Apply on nosmsje.gov.in →",
        },
        {
            "name": "Dr. Ambedkar Foundation International Scholarship",
            "tag": "Central Govt", "tag_color": "#f472b6", "bar": "linear-gradient(90deg,#f472b6,#ec4899)",
            "desc": "For SC students from economically weaker sections to pursue higher education abroad at Masters level.",
            "amount": "Up to $15,000/yr",
            "amount_color": "#f472b6",
            "link": "https://ambedkarfoundation.nic.in/",
            "link_text": "Visit ambedkarfoundation.nic.in →",
        },
        {
            "name": "ICCR Scholarship Scheme",
            "tag": "Govt of India", "tag_color": "#fbbf24", "bar": "linear-gradient(90deg,#fbbf24,#f59e0b)",
            "desc": "Indian Council for Cultural Relations offers scholarships for study in partner countries including Russia, China, France, Germany.",
            "amount": "Full Tuition + Stipend",
            "amount_color": "#fbbf24",
            "link": "https://a2ascholarships.iccr.gov.in/",
            "link_text": "Apply on iccr.gov.in →",
        },
        {
            "name": "Maulana Azad National Fellowship (MANF)",
            "tag": "Ministry of Minority", "tag_color": "#34d399", "bar": "linear-gradient(90deg,#34d399,#10b981)",
            "desc": "For minority community students (Muslim, Christian, Buddhist, Sikh, Jain, Parsi) for integrated 5-yr M.Phil/PhD.",
            "amount": "₹31,000/mo (JRF) + contingency",
            "amount_color": "#34d399",
            "link": "https://manf.ugc.ac.in/",
            "link_text": "Apply on manf.ugc.ac.in →",
        },
        {
            "name": "PM Scholarship Scheme (PMSS)",
            "tag": "Central Govt", "tag_color": "#60a5fa", "bar": "linear-gradient(90deg,#60a5fa,#3b82f6)",
            "desc": "For wards of ex-servicemen and widows of defence personnel pursuing technical/professional courses abroad.",
            "amount": "₹3,000 – ₹36,000/yr",
            "amount_color": "#60a5fa",
            "link": "https://ksb.gov.in/pm-scholarship.htm",
            "link_text": "Apply on ksb.gov.in →",
        },
        {
            "name": "Begum Hazrat Mahal National Scholarship",
            "tag": "Minority Affairs", "tag_color": "#fb923c", "bar": "linear-gradient(90deg,#fb923c,#f97316)",
            "desc": "For meritorious girls from minority communities studying in Class 9–12 in India (stepping stone to higher ed).",
            "amount": "₹5,000 – ₹6,000/yr",
            "amount_color": "#fb923c",
            "link": "https://scholarships.gov.in/",
            "link_text": "Apply on scholarships.gov.in →",
        },
    ]

    scols = st.columns(3, gap="medium")
    for i, s in enumerate(scholarships):
        with scols[i % 3]:
            st.markdown(f"""
            <div class="schol-card">
                <div class="sc-top" style="background:{s['bar']};"></div>
                <div class="sc-body">
                    <div class="sc-tag" style="background:{s['tag_color']}18; border:1px solid {s['tag_color']}55; color:{s['tag_color']};">{s['tag']}</div>
                    <div class="sc-name">🏛️ {s['name']}</div>
                    <div class="sc-desc">{s['desc']}</div>
                    <div class="sc-amt" style="color:{s['amount_color']};">{s['amount']}</div>
                    <br><a class="sc-link" href="{s['link']}" target="_blank">{s['link_text']}</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 2 — LOAN PROVIDERS
    # ════════════════════════════════════════════
    st.markdown("<div class='section-title'>🏦 Education Loan Providers</div>", unsafe_allow_html=True)

    loans = [
        {
            "logo": "🏦", "name": "State Bank of India (SBI)",
            "rate": "8.15% p.a.", "rate_color": "#34d399",
            "bar": "linear-gradient(90deg,#34d399,#10b981)",
            "max_amt": "Up to ₹1.5 Crore (overseas)",
            "features": "✔ Scholar Loan for top institutes\n✔ No collateral up to ₹7.5L\n✔ Repayment up to 15 years\n✔ 0.50% concession for girl students",
            "link": "https://sbi.co.in/web/personal-banking/loans/education-loan",
            "link_text": "Apply on SBI →",
        },
        {
            "logo": "🏛️", "name": "Bank of Baroda (Baroda Scholar)",
            "rate": "9.70% p.a.", "rate_color": "#818cf8",
            "bar": "linear-gradient(90deg,#818cf8,#a78bfa)",
            "max_amt": "Up to ₹80 Lakh (overseas)",
            "features": "✔ Exclusively for top global universities\n✔ Smart loan for IIT/IIM/NIT\n✔ 15-yr repayment period\n✔ Online application available",
            "link": "https://www.bankofbaroda.in/personal-banking/loans/education-loan/baroda-scholar",
            "link_text": "Apply on Bank of Baroda →",
        },
        {
            "logo": "🏢", "name": "HDFC Credila",
            "rate": "9.50%+ p.a.", "rate_color": "#fbbf24",
            "bar": "linear-gradient(90deg,#fbbf24,#f59e0b)",
            "max_amt": "Up to ₹1 Crore (no upper limit for select)",
            "features": "✔ Specialised education loan NBFC\n✔ 100% tuition + living expenses\n✔ No collateral for select profiles\n✔ Fast approval in 3–5 days",
            "link": "https://www.hdfccredila.com/",
            "link_text": "Apply on HDFC Credila →",
        },
        {
            "logo": "💳", "name": "Avanse Financial Services",
            "rate": "10.50%+ p.a.", "rate_color": "#f472b6",
            "bar": "linear-gradient(90deg,#f472b6,#ec4899)",
            "max_amt": "No upper limit",
            "features": "✔ Covers 100% of education cost\n✔ Accepts offer letter for pre-visa loan\n✔ 125+ countries supported\n✔ Flexible repayment options",
            "link": "https://www.avanse.com/",
            "link_text": "Apply on Avanse →",
        },
        {
            "logo": "🌐", "name": "Prodigy Finance",
            "rate": "From 7.7% p.a.", "rate_color": "#60a5fa",
            "bar": "linear-gradient(90deg,#60a5fa,#3b82f6)",
            "max_amt": "Up to $220,000 (USD)",
            "features": "✔ 100% online — no Indian co-signer\n✔ No collateral required\n✔ Repay from abroad in local currency\n✔ 750+ global universities supported",
            "link": "https://prodigyfinance.com/",
            "link_text": "Apply on Prodigy Finance →",
        },
        {
            "logo": "🏦", "name": "Axis Bank Education Loan",
            "rate": "13.70% p.a.", "rate_color": "#fb923c",
            "bar": "linear-gradient(90deg,#fb923c,#f97316)",
            "max_amt": "Up to ₹75 Lakh (overseas)",
            "features": "✔ Fast processing & online tracking\n✔ Moratorium period during study\n✔ Tax benefit under Sec 80E\n✔ No prepayment charges",
            "link": "https://www.axisbank.com/retail/loans/education-loan",
            "link_text": "Apply on Axis Bank →",
        },
    ]

    lcols = st.columns(3, gap="medium")
    for i, l in enumerate(loans):
        with lcols[i % 3]:
            st.markdown(f"""
            <div class="loan-card">
                <div class="lc-top" style="background:{l['bar']};"></div>
                <div class="lc-body">
                    <div class="lc-logo">{l['logo']}</div>
                    <div class="lc-name">{l['name']}</div>
                    <div class="lc-rate" style="color:{l['rate_color']};">{l['rate']}</div>
                    <div class="lc-max">{l['max_amt']}</div>
                    <div class="lc-feat">{l['features'].replace(chr(10), '<br>')}</div>
                    <a class="lc-link" href="{l['link']}" target="_blank">{l['link_text']}</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='divider-grad'></div>", unsafe_allow_html=True)

    # ── Tips banner ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(102,126,234,0.1),rgba(118,75,162,0.1));
                border:1px solid rgba(102,126,234,0.3); border-radius:16px; padding:1.5rem 2rem;">
        <div style="font-size:1rem; font-weight:800; color:#a78bfa; margin-bottom:0.8rem;">💡 Quick Tips to Boost Your Approval Chances</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem 2rem; font-size:0.82rem; color:#94a3b8; line-height:1.7;">
            <div>✅ Maintain a CGPA above 7.5 — lenders offer better rates</div>
            <div>✅ Apply to scholarship portals <strong style="color:#e2e8f0;">before</strong> the loan to reduce principal</div>
            <div>✅ Having collateral (property/FD) reduces interest by 0.5–1%</div>
            <div>✅ Loan interest is <strong style="color:#e2e8f0;">100% tax-deductible</strong> under Section 80E</div>
            <div>✅ Pre-admission loans from Avanse/HDFC help with visa approval</div>
            <div>✅ Compare multiple lenders — even 0.5% difference saves ₹2–3L over tenure</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


