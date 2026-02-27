import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Vidyāpatha | AI Admissions",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────
#  CUSTOM CSS — Elegant Professional Light Mode
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* ── Page background ── */
.stApp {
    background: #f4f6fb !important;
    background-image: radial-gradient(ellipse at 20% 10%, rgba(99,102,241,0.07) 0%, transparent 55%),
                      radial-gradient(ellipse at 80% 90%, rgba(139,92,246,0.07) 0%, transparent 55%) !important;
}
.block-container {
    padding-top: 1.5rem !important;
}
header { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* ── Hero ── */
.hero-wrap { text-align:center; padding: 0.5rem 1rem 1.0rem; animation: fadeInDown 0.7s ease-out; }
.hero-title {
    font-size: 3.8rem; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #0ea5e9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
}
.hero-sub {
    font-size: 1.05rem; color: #64748b; font-weight: 400;
    margin-top: 0.6rem; letter-spacing: 0.3px;
}
.hero-divider {
    width: 80px; height: 3px; margin: 1.2rem auto 0;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 3px;
}

/* ── Form card ── */
div[data-testid="column"]:has(#form-marker) {
    background: #ffffff !important;
    border-radius: 20px !important;
    padding: 2.2rem 2.2rem 1.8rem !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
    box-shadow:
        0 1px 2px rgba(0,0,0,0.04),
        0 4px 12px rgba(99,102,241,0.07),
        0 20px 50px rgba(99,102,241,0.06) !important;
    animation: slideUp 0.6s ease-out 0.15s both;
}

/* ── Form heading ── */
div[data-testid="column"]:has(#form-marker) h3 {
    color: #1e1b4b !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    -webkit-text-fill-color: #1e1b4b !important;
}

/* ── Labels ── */
label, .stSelectbox label, .stNumberInput label {
    color: #374151 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
    -webkit-text-fill-color: #374151 !important;
    margin-bottom: 0.3rem !important;
}

/* ── Number inputs ── */
.stNumberInput input {
    background: #f9fafb !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    color: #111827 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stNumberInput input::placeholder {
    color: #9ca3af !important;
    font-weight: 400 !important;
    opacity: 1 !important;
}
.stNumberInput input:focus {
    border-color: #6366f1 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Number input +/- buttons ── */
.stNumberInput button {
    background: #6366f1 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
}

/* ── Selectbox styling ── */
div[data-baseweb="select"] > div {
    background: #f9fafb !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #6366f1 !important;
}

/* Force dark color on ALL text elements inside selectboxes */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] [aria-selected] {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}

/* Dropdown list items inside the menu portal */
ul[data-baseweb="menu"] li {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    font-size: 0.95rem !important;
    background-color: #ffffff;
}

/* Hover effect on dropdown list items */
ul[data-baseweb="menu"] li:hover {
    background-color: #f3f4f6 !important;
}

/* Dropdown arrow icon */
div[data-baseweb="select"] svg { fill: #6366f1 !important; }

/* ── Submit button ── */
button[kind="primary"] {
    width: 100%;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
    transition: all 0.3s ease !important;
    margin-top: 0.8rem;
}
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.45) !important;
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
}
button[kind="primary"]:active {
    transform: translateY(1px) scale(0.98) !important;
}

/* ── Summary banner ── */
.summary-banner {
    background: linear-gradient(135deg, #eef2ff, #f5f3ff);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    color: #3730a3;
    font-weight: 500;
    line-height: 1.5;
}

/* ── College result cards ── */
.college-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.college-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(99,102,241,0.1);
}
.card-accent-bar {
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #0ea5e9);
}
.card-number {
    position: absolute; top: 1.2rem; right: 1.2rem;
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #fff; font-weight: 800; font-size: 0.9rem;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px rgba(99,102,241,0.3);
}
.inst-name {
    font-size: 1.2rem; font-weight: 700;
    color: #111827; margin-bottom: 0.3rem;
    padding-right: 3rem; line-height: 1.35;
}
.prog-name {
    font-size: 0.9rem; font-weight: 500; color: #4f46e5;
    margin-bottom: 1rem; letter-spacing: 0.2px;
}
.badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.2rem; }
.badge {
    padding: 0.28rem 0.75rem; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.2px;
}
.b-safe     { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
.b-likely   { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.b-risky    { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.b-unlikely { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.b-cat      { background: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }

.stats-row {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 0.8rem; padding: 1rem 0;
    border-top: 1px solid #f3f4f6;
    border-bottom: 1px solid #f3f4f6;
    margin-bottom: 1rem;
}
.stat-lbl { font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.6px; margin: 0; font-weight: 600; }
.stat-val  { font-size: 1.1rem; color: #111827; font-weight: 800; margin: 0.2rem 0 0; }

.reason-box {
    background: #f9fafb; border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.88rem; color: #374151; line-height: 1.55;
    border-left: 3px solid #6366f1;
}

/* ── Animations ── */
@keyframes fadeInDown {
    from { opacity:0; transform:translateY(-18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes slideUp {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0); }
}
.card-anim { animation: slideUp 0.5s ease-out both; }

/* ── Spinner ── */
.stSpinner > div { border-color: #6366f1 !important; }
/* Hide number input increment/decrement buttons */
.stNumberInput button {display:none;}
/* Fix selectbox text color */
.stSelectbox span, .stSelectbox [class*="singleValue"], .stSelectbox [class*="placeholder"] {
    color: #111827 !important; -webkit-text-fill-color: #111827 !important;
}
/* Grid layout for recommendation cards */
.cards-grid {display:grid; grid-template-columns:repeat(auto-fit, minmax(300px,1fr)); gap:1rem; margin-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  HERO SECTION
# ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">Vidyāpatha</div>
    <div class="hero-sub">Intelligent College Admissions Assistant &nbsp;·&nbsp; Powered by RAG &amp; JoSAA Data</div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────
CATEGORY_LIST = [
    "OPEN", "OBC-NCL", "SC", "ST", "EWS",
    "OPEN (PwD)", "OBC-NCL (PwD)", "SC (PwD)", "ST (PwD)", "EWS (PwD)"
]
BRANCH_LIST = [
    "Computer Science and Engineering",
    "Artificial Intelligence",
    "Data Science and Engineering",
    "Electronics and Communication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Mathematics and Computing",
    "Production and Industrial Engineering",
    "Metallurgical and Materials Engineering",
    "Biotechnology",
]
STATE_LIST = sorted([
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
    "Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir",
    "Jharkhand","Karnataka","Kerala","Ladakh","Madhya Pradesh","Maharashtra",
    "Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan",
    "Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand",
    "West Bengal",
])

# ─────────────────────────────────────────────────────
#  FORM — centered column
# ─────────────────────────────────────────────────────
_, col_m, _ = st.columns([0.5, 3.5, 0.5])

# ── Category rank info message ──────────────────────────────────────────────
OPEN_CATS  = {"OPEN", "OPEN (PwD)"}

with col_m:
    st.markdown('<div id="form-marker"></div>', unsafe_allow_html=True)
    st.markdown("### 🎓 Find Your Dream College")
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    c_cat, c_rank = st.columns(2)
    with c_cat:
        category = st.selectbox("Category", CATEGORY_LIST, index=None, placeholder="Select Category")

    # Toast effect for category change reminder
    if "prev_cat" not in st.session_state:
        st.session_state.prev_cat = category
    elif st.session_state.prev_cat != category:
        st.toast(f"Category changed! Please enter your appropriate rank.", icon="🔔")
        st.session_state.prev_cat = category

    if category is None:
        rank_label = "JEE Rank / Category Rank"
        rank_help  = "Please select a category first."
        is_open_cat = True
    else:
        is_open_cat = category in OPEN_CATS
        if is_open_cat:
            rank_label = "JEE Rank (CRL)"
            rank_help  = "Enter your Common Rank List (CRL) rank from JEE Main / Advanced."
        else:
            # If the user explicitly wants "CRL" in the text, we provide it dynamically
            # But the logic expects category rank, so let's make it clear dynamically:
            rank_label = f"{category} Category Rank (CRL)"
            rank_help  = (
                f"Enter your {category} category rank — NOT your JEE Main rank. "
                f"Your category rank is printed separately on the JEE scorecards. "
                f"For example, an ST student with JEE rank 15,000 may have an ST category rank of ~300–600."
            )
    
    with c_rank:
        rank = st.number_input(
            rank_label, min_value=1, max_value=2_000_000,
            value=None,
            step=1,
            placeholder="e.g. 15000",
            help=rank_help,
        )

    if category and not is_open_cat:
        st.info(
            f"ℹ️ **{category} Category Rank required.** "
            f"This is your rank *among {category} candidates only*, shown separately on your JEE scorecard — "
            f"not your overall CRL rank."
        )

    c3, c4 = st.columns(2)
    with c3:
        branch = st.selectbox("Preferred Branch", BRANCH_LIST, index=None, placeholder="Select Branch")
    with c4:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=None, placeholder="Select Gender")

    home_state = st.selectbox("Home State", STATE_LIST, index=None, placeholder="Select Home State")

    submitted = st.button("✦  Get My Recommendations", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────────────
if submitted:
    with st.spinner("Querying knowledge base & ranking colleges..."):
        time.sleep(0.3)
        try:
            if not all([category, rank, branch, gender, home_state]):
                st.warning("Please fill out all fields to continue.", icon="⚠️")
                st.stop()
                
            payload = {
                "rank": rank,
                "category": category,
                "branch": branch,
                "gender": gender,
                "home_state": home_state,
            }
            resp = requests.post("http://localhost:8000/recommend", json=payload, timeout=30)

            if resp.status_code == 200:
                data  = resp.json()
                recs  = data.get("recommendations", [])
                total = data.get("total_found", len(recs))

                if not recs:
                    st.warning(
                        "⚠️  No matching colleges found for your criteria. "
                        "Try a lower rank value or adjust your category / branch."
                    )
                else:
                    _, res_col, _ = st.columns([1, 2.2, 1])
                    with res_col:
                        st.markdown(f"""
                        <div class="summary-banner">
                            🎯 &nbsp;Found <strong>{total}</strong> eligible colleges in your range &nbsp;·&nbsp;
                            Showing top <strong>{len(recs)}</strong> &nbsp;·&nbsp;
                            <strong>{category}</strong> &nbsp;·&nbsp; Rank <strong>{rank:,}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        for i, rec in enumerate(recs):
                            prob       = rec.get("probability", 0)
                            label      = rec.get("probability_label", "Unknown")
                            c_rank     = int(rec.get("closing_rank", 0))
                            score      = rec.get("score", 0)
                            inst       = rec.get("institute", "—")
                            prog       = rec.get("branch", "—")
                            cat_disp   = rec.get("category", category)
                            reason     = rec.get("reason", "")

                            # Probability badge class
                            if prob >= 90:   bcls = "b-safe"
                            elif prob >= 75: bcls = "b-likely"
                            elif prob >= 40: bcls = "b-risky"
                            else:            bcls = "b-unlikely"

                            delay = 0.05 + i * 0.08
                            card_html = f"""
                            <div class="college-card card-anim" style="animation-delay:{delay:.2f}s">
                                <div class="card-accent-bar"></div>
                                <div class="card-number">#{i+1}</div>
                                <div class="inst-name">{inst}</div>
                                <div class="prog-name">{prog}</div>
                                <div class="badge-row">
                                    <span class="badge {bcls}">&#11044; {label} &mdash; {prob:.1f}%</span>
                                    <span class="badge b-cat">{cat_disp}</span>
                                </div>
                                <div class="stats-row">
                                    <div>
                                        <p class="stat-lbl">Your Rank</p>
                                        <p class="stat-val">{rank:,}</p>
                                    </div>
                                    <div>
                                        <p class="stat-lbl">Closing Rank</p>
                                        <p class="stat-val">{c_rank:,}</p>
                                    </div>
                                    <div>
                                        <p class="stat-lbl">AI Score</p>
                                        <p class="stat-val">{score:.1f}</p>
                                    </div>
                                </div>
                                <div class="reason-box">{reason}</div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.error(f"Backend error {resp.status_code}: {resp.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                "🚨 Cannot connect to backend. "
                "Make sure the FastAPI server is running on http://localhost:8000"
            )
        except Exception as e:
            st.error(f"Unexpected error: {e}")
