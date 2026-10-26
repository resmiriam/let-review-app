import base64
import textwrap
import streamlit as st
from datetime import date
from pathlib import Path

from data.progress_db import (
    get_completed_lessons,
    mark_lesson_completed,
    initialize_database,
    create_learner,
    save_question,
    record_attempt,
    get_attempt_history,
    get_weak_topics,
    get_due_reviews,
    get_questions_for_review,
)

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------
initialize_database()

# Persistent learner ID for this single-user prototype.
# This keeps the same learner record when the app restarts.
DATA_DIR = Path(__file__).resolve().parent / "data"
LEARNER_ID_FILE = DATA_DIR / "learner_id.txt"
DATA_DIR.mkdir(parents=True, exist_ok=True)

if LEARNER_ID_FILE.exists():
    learner_id = int(LEARNER_ID_FILE.read_text().strip())
else:
    learner_id = create_learner("Orivan Learner")
    LEARNER_ID_FILE.write_text(str(learner_id))

if "learner_id" not in st.session_state:
    st.session_state.learner_id = learner_id

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="Orivan | AI-Powered LET Review",
    page_icon="♜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# BRAND DESIGN AND SHARED STYLES
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Merriweather:wght@400;700;900&display=swap');

:root {
    --navy: #14233B;
    --navy2: #223957;
    --blue: #D9BD80;
    --pale: #F5F0E5;
    --page: #F1F0EC;
    --ink: #263448;
    --muted: #788294;
    --border: #E7E2D8;
    --white: #FFFFFF;
    --green: #28765D;
}

.stApp {
    background: var(--page);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1320px;
    padding: 1.8rem 2.2rem 3rem;
}

h1, h2, h3 {
    font-family: 'Merriweather', Georgia, serif !important;
    color: var(--navy) !important;
    letter-spacing: -0.6px;
}

h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 700 !important; }

p, label, li {
    color: var(--ink);
}

/* Keep the sidebar toggle accessible; hide only toolbar action menus */
[data-testid="stToolbarActions"] {
    visibility: hidden !important;
    pointer-events: none !important;
}

/* Keep Streamlit's native sidebar toggle visible and styled */
header[data-testid="stHeader"] {
    height: 3.5rem !important;
    background: #F8F7F3 !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    color: #14233B !important;
    background: #F8F7F3 !important;
    border: 1px solid #D9BD80 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebarCollapsedControl"] svg {
    color: #14233B !important;
    fill: #14233B !important;
}

/* Visible white/gold sidebar collapse controls */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button svg,
[data-testid="stSidebar"] button svg path {
    color: #FFFFFF !important;
    fill: currentColor !important;
}
[data-testid="stSidebar"] button:hover {
    color: #D9BD80 !important;
    border-color: #D9BD80 !important;
}
[data-testid="stSidebar"] button:focus svg,
[data-testid="stSidebar"] button:hover svg {
    color: #D9BD80 !important;
}


/* ORIVAN sidebar navigation: square icons, no radio circles */
[data-testid="stSidebar"] [data-testid="stRadio"] input,
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    gap: 7px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    min-height: 54px !important;
    padding: 8px 12px !important;
    gap: 12px !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:last-child {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stRadio"] label .material-symbols-rounded {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    border-radius: 8px !important;
    background: #223957 !important;
    color: #FFFFFF !important;
    font-size: 24px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #2A3D56 !important;
    border-color: #D9BD80 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) .material-symbols-rounded {
    background: #D9BD80 !important;
    color: #14233B !important;
}

/* White sidebar collapse arrow while sidebar is open */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
    color: #FFFFFF !important;
    background: transparent !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg path,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    fill: none !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover svg,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover svg {
    color: #D9BD80 !important;
    stroke: #D9BD80 !important;
}


/* Workspace button navigation */

/* Force workspace navigation content to the left */
[data-testid="stSidebar"] [data-testid="stButton"] {
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 14px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button > div {
    width: 100% !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stButton"] > button .material-symbols-rounded {
    flex-shrink: 0 !important;
    margin-right: 8px !important;
}

/* Make both sidebar arrow controls white */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button svg,
[data-testid="stSidebar"] button svg path {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] button:hover svg,
[data-testid="stSidebar"] button:hover svg path {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
}
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] {
    color: #FFFFFF !important;
    background: transparent !important;
}
[data-testid="stSidebar"] button[kind="header"] svg,
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    fill: none !important;
}

[data-testid="stSidebar"] [data-testid="stButton"] > button {
    min-height: 52px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    gap: 12px !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 650 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stButton"] > button .material-symbols-rounded {
    font-size: 25px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #F5F0E5 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #223957 !important;
    border-color: #D9BD80 !important;
    color: #FFFFFF !important;
}

/* White collapse arrow on the open navy sidebar */
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebar"] button[aria-label*="Collapse"] {
    color: #FFFFFF !important;
    background: transparent !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] button[aria-label*="Collapse"] svg,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    fill: none !important;
    opacity: 1 !important;
}


/* Force both controls in the expanded sidebar header to white */
[data-testid="stSidebarHeader"] button,
[data-testid="stSidebarHeader"] button *,
[data-testid="stSidebarHeader"] button svg,
[data-testid="stSidebarHeader"] button svg path,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg path,
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] button[kind="header"] *,
[data-testid="stSidebar"] button[kind="header"] svg,
[data-testid="stSidebar"] button[kind="header"] svg path {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    opacity: 1 !important;
}
[data-testid="stSidebarHeader"] button:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
    color: #FFFFFF !important;
    background: #223957 !important;
}

/* ORIVAN sidebar: enforce readable light text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
    color: #F5F0E5 !important;
}
[data-testid="stSidebar"] .brand-name {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .brand-caption {
    color: #D9BD80 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button,
[data-testid="stSidebar"] [data-testid="stButton"] > button * {
    color: #F5F0E5 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] * {
    color: #FFFFFF !important;
}

/* ORIVAN NAVY SIDEBAR */

/* Ensure every Streamlit sidebar layer uses the reference navy */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
    background-color: #14233B !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    gap: 5px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #2A3D56 !important;
    border: 1px solid #D9BD80 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
    color: #D9BD80 !important;
}

[data-testid="stSidebar"] {
    background: #14233B !important;
    border-right: 1px solid #2D405A;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

[data-testid="stSidebar"] .brand-name {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .brand-caption {
    color: #D9BD80 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #D8E0EB !important;
}

[data-testid="stSidebar"] hr {
    border-color: #35465E !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 10px 12px;
    border-radius: 10px;
    margin: 4px 0;
    border: 1px solid transparent;
    font-weight: 600;
    transition: 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #223957 !important;
    border-color: #D9BD80 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span {
    color: #F5F0E5 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #2A3D56 !important;
    border-color: #D9BD80 !important;
}

.stButton > button {
    background: var(--navy);
    color: white !important;
    border: 1px solid var(--navy);
    border-radius: 10px;
    min-height: 44px;
    padding: 0.55rem 1.1rem;
    font-weight: 700;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: var(--blue);
    border-color: var(--blue);
    color: white !important;
    transform: translateY(-1px);
}

.stSelectbox [data-baseweb="select"],
.stDateInput input,
.stNumberInput input,
.stTextInput input,
.stTextArea textarea {
    border-radius: 10px;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px 20px;
    border: 1px solid var(--border);
    border-radius: 15px;
    box-shadow: 0 4px 14px rgba(24, 48, 79, 0.035);
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: var(--border);
}

.brand-logo {
    display: flex;
    align-items: center;
    gap: 11px;
    margin-bottom: 24px;
}

.logo-symbol {
    width: 46px;
    height: 46px;
    flex-shrink: 0;
    border-radius: 14px;
    background: linear-gradient(145deg, #14233B, #223957);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    box-shadow: 0 6px 16px rgba(35, 74, 120, 0.18);
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    color: var(--navy);
    font-size: 19px;
    font-weight: 800;
    line-height: 1.2;
}

.brand-caption {
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 1.2px;
    font-weight: 700;
    text-transform: uppercase;
    margin-top: 3px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 36px 38px;
    border-radius: 23px;
    background: linear-gradient(120deg, #14233B 0%, #223957 64%, #344C68 100%);
    color: white;
    margin: 4px 0 24px;
    box-shadow: 0 12px 28px rgba(20, 43, 74, 0.13);
}

.hero:before {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 50%;
    right: -55px;
    top: -105px;
}

.hero:after {
    content: "";
    position: absolute;
    width: 170px;
    height: 170px;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 50%;
    right: 55px;
    bottom: -120px;
}

.hero-eyebrow {
    color: #E7E2D8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 13px;
}

.hero-title {
    color: white;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(27px, 3.3vw, 39px);
    line-height: 1.18;
    font-weight: 800;
    letter-spacing: -1px;
    max-width: 650px;
    margin-bottom: 12px;
}

.hero-copy {
    color: #F5F0E5;
    font-size: 15px;
    line-height: 1.75;
    max-width: 620px;
}

.hero-pill {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.19);
    color: #F2F7FF;
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 17px;
}

.section-heading {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 28px 0 5px;
}

.section-subtitle {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 17px;
}

.subject-card {
    height: 100%;
    min-height: 225px;
    padding: 23px;
    background: white;
    border: 1px solid var(--border);
    border-radius: 17px;
    box-shadow: 0 4px 15px rgba(24,48,79,0.035);
}

.subject-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 19px;
}

.icon-blue { background: #F5F0E5; }
.icon-green { background: #F5F0E5; }
.icon-gold { background: #F5F0E5; }

.subject-title {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-size: 16px;
    font-weight: 800;
    line-height: 1.5;
    margin-bottom: 7px;
}

.subject-copy {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
}

.feature-card {
    height: 100%;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: white;
}

.feature-icon {
    font-size: 24px;
    margin-bottom: 12px;
}

.feature-title {
    color: var(--navy);
    font-weight: 800;
    font-size: 15px;
    margin-bottom: 7px;
}

.feature-copy {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
}

.ai-panel {
    padding: 25px;
    border: 1px solid #E7E2D8;
    border-radius: 18px;
    background: linear-gradient(130deg, #F8F7F3, #F8F7F3);
}

.ai-title {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 8px;
}

.ai-copy {
    color: #52657F;
    font-size: 13px;
    line-height: 1.8;
}

.small-tag {
    display: inline-block;
    border-radius: 30px;
    padding: 5px 10px;
    background: #F5F0E5;
    color: #244F85;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.footer-note {
    color: #8793A6;
    font-size: 11px;
    line-height: 1.7;
    padding-top: 15px;
}

@media (max-width: 768px) {
    .block-container { padding: 1rem; }
    .hero { padding: 26px 22px; border-radius: 17px; }
    .subject-card { min-height: 0; }
}

/* ORIVAN PREMIUM ACADEMIC DASHBOARD */
.orivan-hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(125deg, #14233B, #223957 72%, #29435D) !important;
    border: 1px solid rgba(217,189,128,.4) !important;
    border-radius: 22px !important;
    padding: 46px 48px 34px !important;
    margin: 8px 0 28px !important;
    box-shadow: 0 16px 38px rgba(20,35,59,.12);
}
.orivan-hero::after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    right: -70px;
    top: -90px;
    border: 1px solid rgba(217,189,128,.28);
    border-radius: 50%;
    box-shadow: 0 0 0 28px rgba(217,189,128,.04),
                0 0 0 58px rgba(217,189,128,.025);
    pointer-events: none;
}
.orivan-hero .hero-eyebrow {
    color: #D9BD80 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    margin-bottom: 20px !important;
}
.orivan-hero .hero-title {
    color: #FFFFFF !important;
    font-family: 'Merriweather', Georgia, serif !important;
    font-size: clamp(29px, 3.2vw, 43px) !important;
    font-weight: 700 !important;
    line-height: 1.4 !important;
    letter-spacing: -.8px !important;
    max-width: 760px;
    margin-bottom: 16px !important;
}
.orivan-hero .hero-copy {
    color: #E0E7F0 !important;
    font-size: 15px !important;
    line-height: 1.85 !important;
    max-width: 650px;
}
.hero-bottom-line {
    margin-top: 30px;
    padding-top: 17px;
    border-top: 1px solid rgba(255,255,255,.16);
    color: #D9BD80;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
}
.hero-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: 8px;
    border-radius: 50%;
    background: #D9BD80;
}
.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(217,189,128,.15), transparent 34%),
        radial-gradient(ellipse at 96% 18%, rgba(34,57,87,.10), transparent 32%),
        linear-gradient(135deg, #F1F0EC 0%, #F7F4ED 48%, #E9EDF1 100%) !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E7E2D8;
    border-radius: 15px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(20,35,59,.04);
}
[data-testid="stMetricLabel"] {
    color: #788294 !important;
    font-size: 12px !important;
}
[data-testid="stMetricValue"] {
    color: #14233B !important;
    font-weight: 750 !important;
}
.stButton > button {
    border-radius: 10px;
    border-color: #D9BD80;
    font-weight: 650;
}
.stButton > button[kind="primary"] {
    background: #14233B;
    color: #FFFFFF;
}
@media (max-width: 768px) {
    .orivan-hero {
        padding: 30px 24px 24px !important;
        border-radius: 16px !important;
    }
    .orivan-hero .hero-title { font-size: 29px !important; }
}


/* ORIVAN: visible white cursor across the workspace */
* :not(input):not(textarea):not([contenteditable="true"]) {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M4 2 L4 19 L8.5 14.5 L12 22 L15 20.5 L12 13.5 L18 13 Z' fill='white' stroke='%2314233B' stroke-width='1.5' stroke-linejoin='round'/%3E%3C/svg%3E") 4 2, auto !important;
}
input, textarea, [contenteditable="true"] {
    cursor: text !important;
}
button, a, [role="button"] {
    cursor: pointer !important;
}


/* Ensure sidebar section labels are readable on navy */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #FFFFFF !important;
    opacity: 1 !important;
}
\n
/* ORIVAN_PREMIUM_MOTION_V1 */

/* Gentle entrance for the main workspace */
@keyframes orivanContentEnter {
    from {
        opacity: 0;
        transform: translateY(7px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stApp [data-testid="stMainBlockContainer"] {
    animation: orivanContentEnter 420ms cubic-bezier(.2,.7,.2,1) both;
}

/* Refined buttons */
.stButton > button,
.stLinkButton > a,
[data-testid="stDownloadButton"] > button {
    transition:
        transform 180ms cubic-bezier(.2,.7,.2,1),
        box-shadow 220ms ease,
        border-color 180ms ease,
        background-color 180ms ease,
        color 180ms ease !important;
}

.stButton > button,
[data-testid="stDownloadButton"] > button {
    border-radius: 11px;
}

@media (hover: hover) and (pointer: fine) {
    .stButton > button:hover,
    .stLinkButton > a:hover,
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 18px rgba(20, 35, 59, 0.12);
    }
}

.stButton > button:active,
.stLinkButton > a:active,
[data-testid="stDownloadButton"] > button:active {
    transform: translateY(0) scale(.985);
}

/* Smooth, accessible form-field focus */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    transition:
        border-color 180ms ease,
        box-shadow 180ms ease;
}

.stApp input:focus,
.stApp textarea:focus {
    border-color: #B99A5C !important;
    box-shadow: 0 0 0 2px rgba(217, 189, 128, .20);
}

/* Honor reduced-motion preferences */
@media (prefers-reduced-motion: reduce) {
    .stApp [data-testid="stMainBlockContainer"] {
        animation: none !important;
    }

    .stButton > button,
    .stLinkButton > a,
    [data-testid="stDownloadButton"] > button,
    .stApp input,
    .stApp textarea,
    .stApp [data-baseweb="select"] > div {
        transition: none !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover,
    [data-testid="stDownloadButton"] > button:hover {
        transform: none !important;
    }
}


/* ORIVAN PREMIUM WORKSPACE: layered background and clearer surfaces */
.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(217,189,128,.15), transparent 34%),
        radial-gradient(ellipse at 96% 18%, rgba(34,57,87,.10), transparent 32%),
        linear-gradient(135deg, #F1F0EC 0%, #F7F4ED 48%, #E9EDF1 100%) !important;
}
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stMain"],
.stApp [data-testid="stMainBlockContainer"] {
    background: transparent !important;
}
.stApp [data-testid="stMetric"] {
    background: linear-gradient(145deg, #FFFEFA 0%, #F0EDE5 100%) !important;
    border: 1px solid #C9C1B2 !important;
    box-shadow: 0 7px 20px rgba(20,35,59,.08) !important;
}
.stApp [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #14233B !important;
    border-bottom-color: #A87925 !important;
}
.stApp div[data-testid="stExpander"] {
    border-color: #C9C1B2 !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "completed" not in st.session_state:
    st.session_state.completed = get_completed_lessons(
        st.session_state.learner_id
    )


# --------------------------------------------------
# LESSON LIBRARY
# These are starter examples, not a complete reviewer.
# --------------------------------------------------
lessons = {
    "Professional Education": {
        "Learning Theories": {
            "notes": textwrap.dedent("""
                ## 1. What are learning theories?

                Learning theories explain how people acquire knowledge, develop
                skills, and change their understanding or behavior. Teachers use
                these ideas to plan lessons, choose activities, and support learners.

                ## 2. Major theories and theorists

                ### Behaviorism
                **Key theorists:** B. F. Skinner, John B. Watson, and Ivan Pavlov.

                Behaviorism focuses on observable behavior and how the environment
                influences it.

                - **Classroom example:** A teacher praises a learner for completing
                  work on time. Praise may encourage the learner to repeat the behavior.
                - **Key idea:** Reinforcement can increase a behavior. Punishment
                  aims to decrease a behavior.
                - **Remember:** Focus on behavior and its consequences.

                ### Cognitivism
                **Key theorists:** Jean Piaget and other cognitive-learning scholars.

                Cognitivism examines mental processes such as attention, memory,
                understanding, and problem-solving.

                - **Classroom example:** A teacher organizes new information into
                  a diagram to help learners connect ideas and remember them.
                - **Key idea:** Learning involves mental processing, not only
                  observable behavior.
                - **Remember:** Focus on thinking, memory, and understanding.

                ### Constructivism
                **Key theorists:** Jean Piaget is associated with cognitive
                constructivism; Lev Vygotsky is associated with social constructivism.

                Constructivism emphasizes that learners actively develop
                understanding by connecting new experiences with prior knowledge.

                - **Classroom example:** Learners investigate why some objects
                  float and use their observations to develop explanations.
                - **Key idea:** Learners actively build understanding.
                - **Remember:** Focus on exploration, prior knowledge, and meaning.

                ### Social Learning Theory
                **Key theorist:** Albert Bandura.

                Social learning theory explains how people can learn by observing
                others and modeling their behavior. Observing a behavior does not
                guarantee that the learner will perform it.

                - **Classroom example:** A learner observes the teacher demonstrate
                  a respectful way to disagree and later uses that approach.
                - **Key idea:** Observation and modeling can support learning.
                - **Remember:** Focus on models, observation, and imitation.

                ## 3. Compare the theories

                - **Behaviorism:** Observable behavior and consequences.
                - **Cognitivism:** Mental processes and information processing.
                - **Constructivism:** Actively building understanding.
                - **Social learning:** Learning by observing and modeling others.

                ## 4. Quick memory aid

                - Behaviorism — behavior.
                - Cognitivism — thinking.
                - Constructivism — building understanding.
                - Social learning — observing others.

                ## 5. Check your understanding

                Ask yourself: What is the learner doing? What helps explain the
                learning? Look for the main process described in the situation.
            """).strip(),
            "question": (
                "Which perspective emphasizes learning by observing other people?"
            ),
            "choices": [
                "Social learning theory",
                "Behaviorism only",
                "Trial and error only",
                "Memorization only"
            ],
            "answer": "Social learning theory",
            "explanation": (
                "Social learning theory emphasizes observing and learning "
                "from other people's behavior."
            )
        },
        "Assessment": {
            "notes": textwrap.dedent("""
                ## 1. What is assessment?

                Assessment is the process of gathering and interpreting evidence
                about what learners know, understand, and can do. Teachers use
                the results to make decisions about instruction and learning.

                ## 2. Main purposes and types

                ### Diagnostic assessment
                Used to identify learners' prior knowledge, strengths, and
                learning needs before or early in instruction.

                **Example:** A teacher gives a short pre-test before starting
                a fractions lesson.

                ### Formative assessment
                Used during learning to identify progress and guide next steps.
                It is most useful when the evidence leads to feedback or changes
                in teaching and learning.

                **Example:** During a lesson, the teacher asks learners to solve
                one problem and uses their answers to decide what to reteach.

                ### Summative assessment
                Used to evaluate learning at the end of a unit, course, or
                instructional period.

                **Example:** A unit examination measures learning after the
                lessons have been completed.

                ## 3. Assessment for, as, and of learning

                - **Assessment for learning:** Evidence helps the teacher adjust
                  instruction and support learner progress.
                - **Assessment as learning:** Learners reflect on their progress,
                  monitor their understanding, and evaluate their work.
                - **Assessment of learning:** Evidence is used to judge or report
                  what learners have achieved.

                ## 4. Important assessment terms

                - **Validity:** How well an assessment measures what it is
                  intended to measure.
                - **Reliability:** The consistency of assessment results.
                - **Rubric:** Criteria, often with performance descriptions,
                  used to evaluate work.
                - **Feedback:** Information that helps learners understand what
                  they did well and what to improve.

                ## 5. Classroom example

                If many learners answer an exit question incorrectly, the teacher
                can review the concept, use a different explanation, and check
                understanding again. Assessment should inform a useful next step.

                ## 6. Remember

                - Before instruction: diagnostic.
                - During instruction: formative.
                - At the end of a learning period: summative.

                The timing alone does not determine the purpose. Consider how
                the evidence is used in the situation.
            """).strip(),
            "question": "What is the main purpose of formative assessment?",
            "choices": [
                "To guide teaching and improve learning",
                "To rank schools only",
                "To replace all classroom activities",
                "To give final grades only"
            ],
            "answer": "To guide teaching and improve learning",
            "explanation": (
                "Formative assessment provides information that teachers "
                "and students can use to improve learning while instruction "
                "is ongoing."
            )
        }
    },
    "General Education": {
        "Mathematics": {
            "notes": textwrap.dedent("""
                ## Understanding Percentages

                Let's learn percentages one small step at a time.
                You do not need to memorize everything immediately.
                Follow each example and understand why each step works.

                ### 1. What does percent mean?

                Percent means "per hundred." The symbol is %.

                Imagine a box with 100 small squares. Each square represents
                1 out of 100, or 1%.

                - 1% means 1 out of 100.
                - 50% means 50 out of 100, or one-half.
                - 100% means all 100 squares, or the whole thing.

                **Visual example: 50% means half**

                ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
                ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
                ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
                ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
                ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
                □ □ □ □ □ □ □ □ □ □
                □ □ □ □ □ □ □ □ □ □
                □ □ □ □ □ □ □ □ □ □
                □ □ □ □ □ □ □ □ □ □
                □ □ □ □ □ □ □ □ □ □

                ■ = the part being counted
                □ = the remaining part

                There are 50 filled squares out of 100, so the filled part is 50%.

                ### 2. Learn these useful equivalents

                | Percent | Fraction | Decimal |
                |---|---|---|
                | 10% | 1/10 | 0.10 |
                | 20% | 1/5 | 0.20 |
                | 25% | 1/4 | 0.25 |
                | 50% | 1/2 | 0.50 |
                | 75% | 3/4 | 0.75 |
                | 100% | 1 whole | 1.00 |

                Think of 25% as one-quarter and 50% as one-half.
                These familiar values can make mental math easier.

                ### 3. Change a percent into a decimal

                **Rule:** Divide the percentage by 100.

                Example: Change 8% into a decimal.

                Step 1: Start with 8%.

                Step 2: Divide 8 by 100.

                8 ÷ 100 = 0.08

                Step 3: Write the answer as a decimal.

                8% → divide by 100 → 0.08

                **Answer: 0.08**

                Why? A percent is a number out of 100. Dividing by 100
                changes it into its decimal form.

                ### 4. Change a decimal into a percent

                **Rule:** Multiply the decimal by 100.

                Example: Change 0.35 into a percentage.

                Step 1: Start with 0.35.

                Step 2: Multiply by 100.

                0.35 × 100 = 35

                Step 3: Add the percent symbol.

                0.35 → multiply by 100 → 35%

                **Answer: 35%**

                Remember:
                - Percent to decimal: divide by 100.
                - Decimal to percent: multiply by 100.

                ### 5. Understand the three parts of a percent problem

                Percent problems often use three parts:

                - **Percentage (P):** the part or amount.
                - **Rate (R):** the percent written as a decimal.
                - **Base (B):** the whole or total amount.

                The main formula is:

                **P = R × B**

                This means:

                Part = decimal rate × whole

                Example: Find 20% of 150.

                Step 1: Identify the rate and the base.

                Rate = 20% = 0.20
                Base = 150

                Step 2: Use the formula.

                P = R × B

                Step 3: Put the numbers into the formula.

                P = 0.20 × 150

                Step 4: Multiply.

                P = 30

                **Answer: 30**

                Why? Twenty percent means 20 out of every 100.
                Twenty percent of 150 is 30.

                ### 6. Find what percentage one number is of another

                **Problem:** A student got 36 correct answers out of 40.
                What percentage did the student get?

                Step 1: Find the part and the whole.

                Part = 36 correct answers
                Whole = 40 total questions

                Remember: the part is the amount we have.
                The whole is the total amount.

                Step 2: Divide the part by the whole.

                36 ÷ 40 = 0.9

                The decimal 0.9 tells us how much of the whole the student got.

                Step 3: Change the decimal into a percentage.

                0.9 × 100 = 90

                Step 4: Add the percent symbol.

                **Answer: 90%**

                Follow the arrows:

                36 correct out of 40
                         ↓
                36 ÷ 40 = 0.9
                         ↓
                0.9 × 100 = 90
                         ↓
                       90%

                ### 7. Find the whole number

                **Problem:** 15 is 30% of what number?

                We know the part is 15 and the rate is 30%.
                We need to find the whole.

                Step 1: Change 30% into a decimal.

                30 ÷ 100 = 0.30

                Step 2: Use the formula for finding the base.

                B = P ÷ R

                Step 3: Replace P with 15 and R with 0.30.

                B = 15 ÷ 0.30

                Step 4: Divide.

                B = 50

                **Answer: 50**

                Check your answer: 30% of 50 is 15.
                Since 0.30 × 50 = 15, the answer works.

                ### 8. Find a percentage of a number

                **Problem:** Find 25% of 80.

                Step 1: Change 25% into a decimal.

                25 ÷ 100 = 0.25

                Step 2: Multiply the decimal by the whole number.

                0.25 × 80 = 20

                **Answer: 20**

                Follow the arrows:

                25%
                 ↓ divide by 100
                0.25
                 ↓ multiply by 80
                20

                ### 9. Easy mental math shortcuts

                **Finding 10%:** Divide the number by 10.

                Example: 10% of 200 = 20.

                **Finding 5%:** Find 10%, then divide that answer by 2.

                Example:
                10% of 200 = 20
                Half of 20 = 10
                Therefore, 5% of 200 = 10.

                **Finding 1%:** Divide the number by 100.

                Example: 1% of 200 = 2.

                **Finding 15%:** Add 10% and 5%.

                10% of 200 = 20
                5% of 200 = 10
                20 + 10 = 30

                **Answer: 15% of 200 is 30.**

                ### 10. Common mistakes to avoid

                **Mistake 1: Forgetting to change the percent into a decimal.**

                To find 25% of 80, use 0.25 × 80, not 25 × 80.

                **Mistake 2: Mixing up the part and the whole.**

                When finding what percentage a part is of a whole,
                divide the part by the whole.

                **Mistake 3: Forgetting to multiply by 100.**

                If 36 ÷ 40 = 0.9, the percentage is 90%, not 0.9%.

                **Mistake 4: Using the wrong base.**

                For a percent increase or decrease, compare the change
                with the original amount.

                **Mistake 5: Adding two discounts as if they were one.**

                A 10% discount followed by another 10% discount is not
                a total 20% discount. The second discount is based on
                the reduced price.

                ### 11. Guided practice

                Try each question before opening the answer.

                **Question 1:** Write 8% as a decimal.

                Hint: Divide 8 by 100.

                **Answer:** 0.08

                **Question 2:** What is 20% of 150?

                Step 1: Change 20% to 0.20.
                Step 2: Multiply 0.20 × 150.

                **Answer:** 30

                **Question 3:** 18 out of 24 is what percent?

                Step 1: Divide 18 by 24 to get 0.75.
                Step 2: Multiply 0.75 by 100.

                **Answer:** 75%

                **Question 4:** 12 is 15% of what number?

                Step 1: Change 15% to 0.15.
                Step 2: Divide 12 by 0.15.

                **Answer:** 80

                **Question 5:** A ₱500 item has a 10% discount.
                What is the sale price?

                Step 1: Find the discount: 0.10 × ₱500 = ₱50.
                Step 2: Subtract the discount from the original price.
                ₱500 − ₱50 = ₱450.

                **Answer: ₱450**

                ### Remember these three rules

                - To find the part: P = R × B.
                - To find the rate: divide P by B, then multiply by 100.
                - To find the whole: B = P ÷ R.

                Take your time. Write down each step and check your answer.
            """).strip(),
            "question": "A student got 36 correct answers out of 40 items. What is the score in percent?",
            "choices": ["80%", "85%", "90%", "95%"],
            "answer": "90%",
            "explanation": "36 ÷ 40 = 0.9. Then 0.9 × 100 = 90%."
        }
    },
    "Major: Food and Service Management": {
        "Food Safety": {
            "notes": textwrap.dedent("""
                ## 1. What is food safety?

                Food safety means handling, preparing, storing, and serving food
                in ways that reduce the risk of foodborne illness.

                ## 2. Personal hygiene

                Food handlers should wash their hands properly, keep themselves
                and their work areas clean, and avoid handling food when illness
                or an uncovered wound could contaminate it.

                **Example:** Wash hands before preparing ready-to-eat food and
                after handling raw meat.

                ## 3. Cross-contamination

                Cross-contamination occurs when harmful microorganisms or other
                contaminants transfer from one food, surface, utensil, or hand
                to another.

                **Example:** Using the same unwashed cutting board for raw
                chicken and salad vegetables can transfer contamination.

                **Prevention:** Separate raw foods from ready-to-eat foods and
                clean and sanitize equipment appropriately between tasks.

                ## 4. Safe storage and temperature control

                Food should be stored and handled according to applicable food
                safety requirements. Perishable foods need appropriate temperature
                control, and storage practices should limit contamination.

                **Example:** Keep refrigerated foods at the required safe
                temperature and avoid leaving perishable food out longer than
                permitted by applicable guidance.

                Exact temperature limits and time rules should be verified using
                authoritative food-safety guidance for the food and situation.

                ## 5. Cleaning and sanitizing

                - **Cleaning:** Removes food residue, dirt, and other unwanted
                  material from a surface.
                - **Sanitizing:** Reduces microorganisms on a properly cleaned
                  surface to an appropriate level.

                Cleaning and sanitizing are related but are not interchangeable.

                ## 6. Key points to remember

                - Prevent contamination through hygiene and separation.
                - Use appropriate cleaning and sanitizing procedures.
                - Store food safely and control time and temperature.
                - Follow applicable food safety standards and workplace procedures.

                ## 7. Check your understanding

                Why should raw meat be kept separate from ready-to-eat food?

                Think about how microorganisms can transfer between foods,
                utensils, hands, and preparation surfaces.
            """).strip(),
            "question": (
                "Why should raw meat be kept separate from ready-to-eat food?"
            ),
            "choices": [
                "To prevent cross-contamination",
                "To make food sweeter",
                "To increase serving size",
                "To reduce the need for cleaning"
            ],
            "answer": "To prevent cross-contamination",
            "explanation": (
                "Separating raw meat from ready-to-eat food helps prevent "
                "harmful microorganisms from spreading."
            )
        }
    }
}


# --------------------------------------------------
# SIDEBAR BRAND AND NAVIGATION
# --------------------------------------------------
# ORIVAN_SIDEBAR_AUTOCLOSE_LISTENER
# Install a click listener before rendering the custom navigation buttons.
st.components.v1.html(
    """
    <script>
    (() => {
        try {
            const doc = window.parent.document;
            if (doc.__orivanSidebarAutoCloseInstalled) return;
            doc.__orivanSidebarAutoCloseInstalled = true;

            doc.addEventListener("click", (event) => {
                const navButton = event.target.closest(
                    '[data-testid="stSidebar"] [data-testid="stButton"] button'
                );
                if (!navButton) return;

                setTimeout(() => {
                    const collapse = doc.querySelector(
                        '[data-testid="stSidebarCollapseButton"]'
                    );
                    if (collapse) collapse.click();
                }, 100);
            }, true);
        } catch (error) {
            console.error("Orivan sidebar auto-close:", error);
        }
    })();
    </script>
    """,
    height=0,
)

# Apply requested navigation before creating the sidebar widget.
if st.session_state.pop("open_quiz_after_lesson", False):
    st.session_state["navigation_choice"] = "Practice Quiz"

with st.sidebar:
    with open("assets/orivan-logo.svg", "r", encoding="utf-8") as logo_file:
        logo_data = base64.b64encode(logo_file.read().encode("utf-8")).decode("ascii")

    st.markdown(f"""
    <div class="brand-logo">
        <img src="data:image/svg+xml;base64,{logo_data}" alt="Orivan logo" style="width:48px;height:48px;object-fit:contain;flex-shrink:0;">
        <div>
            <div class="brand-name">Orivan</div>
            <div class="brand-caption">Your review journey</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("GUEST ACCESS")

    guest_pages = [
        ("Welcome", "waving_hand"),
        ("Preview Reviewer", "menu_book"),
        ("Practice Quiz", "quiz"),
    ]

    # Guests can access only public pages until account access is implemented.
    if st.session_state.get("navigation_choice") not in {
        "Welcome", "Preview Reviewer", "Practice Quiz"
    }:
        st.session_state["navigation_choice"] = "Welcome"

    for item, icon_name in guest_pages:
        is_current = st.session_state["navigation_choice"] == item
        if st.button(
            item,
            key=f"workspace_nav_{item.lower().replace(' ', '_')}",
            icon=f":material/{icon_name}:",
            type="primary" if is_current else "secondary",
            use_container_width=True,
        ):
            st.session_state["navigation_choice"] = item
            st.rerun()

    page = st.session_state["navigation_choice"]


# --------------------------------------------------
# TOP HEADER
# --------------------------------------------------
if page != "Welcome":
    st.markdown(f"""
    <div class="brand-logo" style="margin-top:30px;">
        <img src="data:image/svg+xml;base64,{logo_data}" alt="Orivan logo" style="width:46px;height:46px;object-fit:contain;flex-shrink:0;">
        <div>
            <div class="brand-name">Orivan</div>
            <div class="brand-caption">Teacher Licensure Review Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if page == "Welcome":
    st.markdown(textwrap.dedent("""
    <style>
    [data-testid="stMainMenu"] { display: none !important; }

    /* ORIVAN LANDING PAGE FIX */
    header[data-testid="stHeader"] {
        background: #F8F7F3 !important;
        height: 3.75rem !important;
        min-height: 3.75rem !important;
    }
    [data-testid="stMainBlockContainer"] {
        padding-top: 1rem !important;
    }
    footer {
        display: none !important;
    }
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F8F7F3 !important;
    }
    .orivan-feature-copy {
        color: #26364D !important;
        font-weight: 700 !important;
    }
    .orivan-section-title {
        color: #14233B !important;
        font-weight: 800 !important;
    }
    .stButton > button {
        background: #14233B !important;
        color: #FFFFFF !important;
        border: 1px solid #D9BD80 !important;
        font-weight: 700 !important;
        min-height: 48px !important;
    }
    .stButton > button p,
    .stButton > button span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .stButton > button:hover {
        background: #29435D !important;
        color: #FFFFFF !important;
        border-color: #D9BD80 !important;
    }
    /* Sidebar remains visible across pages. */
    [data-testid="stAppViewBlockContainer"] {max-width:1180px;padding-top:1.5rem;}
    .orivan-nav {
        display:flex;align-items:center;gap:14px;
        padding:10px 0 20px;border-bottom:1px solid #D9BD80;
        margin-top:3mm;
        margin-bottom:34px;
    }
    .orivan-mark {
        width:48px;height:48px;display:flex;align-items:center;
        justify-content:center;border-radius:14px;
        background:linear-gradient(145deg,#E4C982,#D9BD80);
        color:#14233B;font-size:25px;
        box-shadow:0 5px 14px rgba(20,35,59,.16);
    }
    .orivan-word {font-size:28px;font-weight:900;color:#14233B;letter-spacing:1.8px;}
    .orivan-sub {font-size:11px;letter-spacing:1.7px;color:#84652F;font-weight:800;}
    .orivan-landing-hero {
        position:relative;overflow:hidden;
        background:
          radial-gradient(ellipse at 92% 8%,rgba(217,189,128,.22),transparent 34%),
          linear-gradient(125deg,#101D32 0%,#1B304C 52%,#344C68 100%);
        color:#fff;border:1px solid #D9BD80;
        border-radius:24px;padding:52px 48px 38px;
        box-shadow:0 20px 44px rgba(20,35,59,.20);
    }
    .orivan-kicker {color:#E4C982;font-size:11px;font-weight:800;letter-spacing:2.4px;margin-bottom:18px;}
    .orivan-headline {
        color:#fff;font-family:'Merriweather',Georgia,serif;
        font-size:clamp(32px,4vw,50px);line-height:1.3;
        font-weight:900;max-width:820px;margin-bottom:20px;
        text-shadow:0 2px 18px rgba(0,0,0,.12);
    }
    .orivan-intro {color:#F0F3F7;font-size:16px;line-height:1.9;max-width:700px;}
    .orivan-rule {height:2px;background:linear-gradient(90deg,#D9BD80,rgba(255,255,255,.12));margin:30px 0 18px;max-width:760px;}
    .orivan-motto {color:#E4C982;font-size:10px;font-weight:800;letter-spacing:1.5px;line-height:1.8;}
    .orivan-section-kicker {color:#84652F;font-size:11px;font-weight:900;letter-spacing:2.2px;margin:42px 0 9px;text-transform:uppercase;}
    .orivan-section-title {font-family:'Merriweather',Georgia,serif;color:#14233B;font-size:29px;font-weight:900;line-height:1.4;margin-bottom:22px;}
    .orivan-feature {
        position:relative;overflow:hidden;
        background:linear-gradient(145deg,#FFFFFF 0%,#FBF7EE 100%);
        border:1px solid #E7E2D8;border-top:3px solid #D9BD80;
        border-radius:16px;padding:23px 21px;min-height:164px;
        box-shadow:0 7px 20px rgba(20,35,59,.055);
        transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;
    }
    .orivan-feature:hover {
        transform:translateY(-3px);border-color:#D9BD80;
        box-shadow:0 13px 28px rgba(20,35,59,.11);
    }
    .orivan-feature-icon {
        display:inline-flex;align-items:center;justify-content:center;
        min-width:42px;height:39px;padding:0 10px;
        background:#F5F0E5;border:1px solid #D9BD80;border-radius:10px;
        font-size:19px;font-weight:900;color:#84652F;margin-bottom:15px;
    }
    .orivan-feature-title {font-size:17px;font-weight:850;color:#14233B;margin-bottom:8px;line-height:1.5;}
    .orivan-feature-copy {font-size:14px;line-height:1.8;color:#435167;font-weight:500;}
    .orivan-foot {
        text-align:center;color:#F5F0E5;font-size:11px;font-weight:900;
        letter-spacing:1.1px;padding:24px 18px;margin-top:36px;
        background:linear-gradient(100deg,#14233B,#2B405C);
        border:1px solid #D9BD80;border-radius:13px;line-height:1.8;
    }
    .orivan-landing-hero + div {margin-top:28px;}
    @media(max-width:700px) {
        .orivan-landing-hero {padding:32px 23px 27px;border-radius:18px;}
        .orivan-headline {font-size:31px;}
        .orivan-section-title {font-size:23px;}
        .orivan-feature {padding:19px 17px;min-height:0;}
        .orivan-nav {margin-bottom:22px;}
    }
    

    </style>
    <div class="orivan-nav">
        <div style="width:58px;height:58px;min-width:58px;background:#14233B;border-radius:12px;display:flex;align-items:center;justify-content:center;overflow:hidden;"><img src="data:image/svg+xml;base64,{logo_data}" alt="Orivan logo" style="width:48px;height:48px;object-fit:contain;"></div>
        <div>
            <div class="orivan-word">ORIVAN</div>
            <div class="orivan-sub">AI-POWERED LET REVIEW</div>
        </div>
    </div>
    <div class="orivan-landing-hero">
        <div class="orivan-kicker">YOUR JOURNEY TO THE TEACHING PROFESSION</div>
        <div class="orivan-headline">Prepare with purpose.<br>Become the teacher you aspire to be.</div>
        <div class="orivan-intro">
            An AI-powered LET review experience that lets you study at your own pace, practice what you’ve learned, and grow more confident with every topic.
        </div>
        <div class="orivan-rule"></div>
        <div class="orivan-motto">STUDY WITH PURPOSE &nbsp; · &nbsp; STAY ON TRACK &nbsp; · &nbsp; GROW WITH CONFIDENCE</div>
    </div>

    <!-- ORIVAN_BLUEPRINT_HIGHLIGHTS -->
    <div style="margin:30px 0 12px;padding:32px;background:linear-gradient(135deg,#FFFFFF 0%,#F5F0E5 100%);border:1px solid #D9BD80;border-left:5px solid #D9BD80;border-radius:18px;box-shadow:0 10px 28px rgba(20,35,59,.08);">
        <div style="color:#84652F;font-size:11px;font-weight:800;letter-spacing:2px;">WHY ORIVAN EXISTS</div>
        <div style="color:#14233B;font-family:Georgia,serif;font-size:27px;font-weight:800;line-height:1.4;margin:10px 0 12px;">
            A clearer, more flexible way to prepare for the LET.
        </div>
        <div style="color:#34445A;font-size:16px;line-height:1.8;">
            Make structured, understandable, adaptive LET preparation more accessible to people with different starting knowledge, schedules, and budgets.
        </div>
        <div style="margin-top:18px;padding:16px 18px;background:#F8F7F3;border-left:4px solid #D9BD80;border-radius:8px;color:#26364D;line-height:1.8;">
            <strong>Our promise:</strong> Know what to study, understand why an answer is right, identify what needs more work, and keep moving through the full curriculum without sacrificing essential rest.
        </div>
    </div>

    <div class="orivan-section-kicker">YOUR SIX-MONTH ROADMAP</div>
    <div class="orivan-section-title">One step at a time. A plan that adapts to you.</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;">
        <div class="orivan-feature"><div class="orivan-feature-icon">01</div><div class="orivan-feature-title">Week 1 · Start smart</div><div class="orivan-feature-copy">Set your routine, check your starting level, and identify learning gaps.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">02</div><div class="orivan-feature-title">Weeks 2–6 · Build foundations</div><div class="orivan-feature-copy">Learn key concepts with clear notes, examples, and guided practice.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">03</div><div class="orivan-feature-title">Weeks 7–14 · Cover the curriculum</div><div class="orivan-feature-copy">Continue through the required subjects while revisiting difficult topics.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">04</div><div class="orivan-feature-title">Weeks 15–19 · Apply your learning</div><div class="orivan-feature-copy">Connect concepts, solve problems, and work on recurring mistakes.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">05</div><div class="orivan-feature-title">Weeks 20–23 · Practice and repair</div><div class="orivan-feature-copy">Use mock exams and targeted practice to find gaps that remain.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">06</div><div class="orivan-feature-title">Weeks 24–26 · Consolidate</div><div class="orivan-feature-copy">Review key notes, practise with fresh questions, and protect your rest.</div></div>
    </div>
    <div style="margin:14px 0 0;color:#788294;font-size:12px;line-height:1.6;">
        
    </div>

    <div class="orivan-section-kicker">MADE FOR REAL LIFE</div>
    <div class="orivan-section-title">Your job and responsibilities matter, too.</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;">
        <div class="orivan-feature"><div class="orivan-feature-icon">◷</div><div class="orivan-feature-title">Choose your study time</div><div class="orivan-feature-copy">Plan around work, commute, meals, family responsibilities, and your preferred study days.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">↗</div><div class="orivan-feature-title">Set a realistic daily goal</div><div class="orivan-feature-copy">Choose a manageable amount of study. Four hours is an option, never a compulsory minimum.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">◎</div><div class="orivan-feature-title">Adjust when life happens</div><div class="orivan-feature-copy">Plan to reschedule missed sessions, shorten work on tired days, and keep your sleep protected.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">♧</div><div class="orivan-feature-title">Remember what needs review</div><div class="orivan-feature-copy">The planned system includes study reminders and spaced reviews for topics you need to revisit.</div></div>
    </div>

    <div class="orivan-section-kicker">A CLEAR PATH TO PREPARATION</div>
    <div class="orivan-section-title">Everything begins with one topic.</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;">
        <div class="orivan-feature"><div class="orivan-feature-icon">▤</div><div class="orivan-feature-title">Learn</div><div class="orivan-feature-copy">Read organized lessons, notes, and key concepts.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">✎</div><div class="orivan-feature-title">Practice</div><div class="orivan-feature-copy">Answer questions and understand the explanations.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">◎</div><div class="orivan-feature-title">Improve</div><div class="orivan-feature-copy">Find weak areas and revisit mistakes until you understand them.</div></div>
        <div class="orivan-feature"><div class="orivan-feature-icon">▥</div><div class="orivan-feature-title">Track progress</div><div class="orivan-feature-copy">Build a study history when progress saving is available through your account.</div></div>
    </div>
    <div class="orivan-foot" style="font-weight:800;">ORIVAN · TEACHER LICENSURE PREPARATION · BUILT FOR FUTURE EDUCATORS</div>
    """).replace("{logo_data}", logo_data), unsafe_allow_html=True)

    st.markdown("""
    <style>
    .planner-heading {
        background: linear-gradient(125deg,#14233B 0%,#223957 65%,#354B66 100%);
        border: 1px solid #D9BD80; border-radius: 20px;
        padding: 30px 32px; margin: 10px 0 22px;
        box-shadow: 0 12px 30px rgba(20,35,59,.12);
    }
    .planner-heading .eyebrow {
        color:#E4C982; letter-spacing:2.5px; font-size:11px;
        font-weight:800; text-transform:uppercase;
    }
    .planner-heading h2 {
        color:#FFFFFF !important; font-size:30px; line-height:1.3;
        margin:10px 0 !important;
    }
    .planner-heading p {
        color:#E7ECF2 !important; line-height:1.75; margin-bottom:0;
    }
    .planner-step {
        border-left:4px solid #D9BD80; padding:3px 0 3px 14px;
        margin:20px 0 12px; color:#14233B;
    }
    .planner-step small {
        display:block; color:#84652F; font-weight:800;
        letter-spacing:1.7px; font-size:10px; margin-bottom:4px;
    }
    .planner-step strong {font-size:20px;color:#14233B;}
    div[data-testid="stForm"] {
        background:linear-gradient(145deg,#FFFFFF,#FBF8F1);
        border:1px solid #E7E2D8; border-radius:18px;
        padding:20px 22px;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stRadio"] label,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stSelectSlider"] label,
    div[data-testid="stTimeInput"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stNumberInput"] label {
        color:#14233B !important; font-weight:700 !important;
    }
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea {
        border-radius:9px !important;
    }
    div[data-testid="stForm"] button[kind="primary"] {
        background:linear-gradient(110deg,#D9BD80,#D9BD80) !important;
        border:1px solid #D9BD80 !important; color:#14233B !important;
        font-weight:800 !important; min-height:48px;
    }
    .planner-note {
        border-radius:12px; padding:13px 16px; margin:10px 0;
        background:#F5F0E5; border:1px solid #E7E2D8;
        color:#39465A; line-height:1.65; font-size:13px;
    }

    /* ORIVAN PREMIUM STUDY PLANNER */
    .planner-heading {
        position:relative;
        overflow:hidden;
        padding:36px 38px;
        border-radius:22px;
        border:1px solid rgba(217,189,128,.8);
        background:
            radial-gradient(ellipse at 95% 0%, rgba(217,189,128,.22), transparent 38%),
            linear-gradient(130deg,#101C30 0%,#1B304C 58%,#304965 100%);
        box-shadow:0 18px 42px rgba(16,28,48,.18);
    }
    .planner-heading:after {
        content:"";
        display:block;
        width:74px;
        height:3px;
        margin-top:22px;
        border-radius:5px;
        background:linear-gradient(90deg,#FFF0B5,#B99553);
    }
    .planner-heading .eyebrow {
        display:inline-block;
        padding:7px 11px;
        border:1px solid rgba(217,189,128,.35);
        border-radius:7px;
        background:rgba(217,189,128,.09);
        color:#FFF0B5;
        letter-spacing:2px;
        font-size:10px;
    }
    .planner-heading h2 {
        font-size:clamp(27px,3vw,36px);
        letter-spacing:-.7px;
        margin:16px 0 12px !important;
    }
    .planner-heading p {
        max-width:760px;
        font-size:15px;
        line-height:1.9;
    }
    .planner-note {
        padding:16px 19px;
        margin:15px 0 24px;
        border:1px solid #E4D4AE;
        border-left:4px solid #D9BD80;
        border-radius:12px;
        background:linear-gradient(110deg,#FBF7ED,#FFFFFF);
        box-shadow:0 4px 15px rgba(20,35,59,.035);
    }
    .planner-step {
        position:relative;
        margin:30px 0 16px;
        padding:8px 0 8px 18px;
        border-left:3px solid #D9BD80;
    }
    .planner-step small {
        display:inline-block;
        margin-bottom:7px;
        padding:5px 9px;
        border-radius:5px;
        background:#F5F0E5;
        color:#84652F;
        font-size:10px;
        letter-spacing:1.8px;
    }
    .planner-step strong {
        display:block;
        font-size:19px;
        letter-spacing:-.2px;
        line-height:1.5;
        color:#14233B;
    }
    div[data-testid="stForm"] {
        padding:26px 28px;
        border:1px solid #E5DCCB;
        border-radius:20px;
        background:linear-gradient(145deg,#FFFFFF 0%,#FCFAF5 100%);
        box-shadow:0 12px 32px rgba(20,35,59,.055);
    }
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea,
    div[data-testid="stForm"] [data-baseweb="select"] > div {
        border-radius:10px !important;
    }
    div[data-testid="stForm"] button[kind="primary"],
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
        min-height:50px;
        border-radius:11px !important;
        background:linear-gradient(110deg,#E8D4A4 0%,#D9BD80 55%,#C5A363 100%) !important;
        border:1px solid #B99553 !important;
        box-shadow:0 5px 14px rgba(158,123,69,.18);
        transition:transform .18s ease,box-shadow .18s ease;
    }
    div[data-testid="stForm"] button[kind="primary"]:hover,
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
        box-shadow:0 8px 20px rgba(158,123,69,.25);
        transform:translateY(-1px);
    }
    @media(max-width:700px) {
        .planner-heading {padding:27px 22px;border-radius:17px;}
        div[data-testid="stForm"] {padding:18px 15px;border-radius:15px;}
        .planner-step strong {font-size:17px;}
    }
    
    /* ORIVAN planner: remove the default pink/red control accents */
    :root {
        --primary-color: #14233B;
    }
    .stApp {
        accent-color: #14233B;
    }
    div[data-testid="stForm"] input[type="checkbox"],
    div[data-testid="stForm"] input[type="radio"],
    div[data-testid="stForm"] input[type="range"],
    div[data-testid="stForm"] input[type="date"] {
        accent-color: #14233B !important;
        color-scheme: light;
    }
    div[data-testid="stForm"] [data-baseweb="slider"] [role="slider"] {
        background-color: #14233B !important;
        border-color: #D9BD80 !important;
        box-shadow: 0 0 0 2px #D9BD80 !important;
    }
    div[data-testid="stForm"] [data-baseweb="slider"] [data-testid="stSliderTrack"],
    div[data-testid="stForm"] [data-baseweb="slider"] > div > div > div {
        background-color: #14233B !important;
    }
    div[data-testid="stForm"] [data-baseweb="radio"] input:checked,
    div[data-testid="stForm"] [data-baseweb="checkbox"] input:checked {
        accent-color: #14233B !important;
    }
    div[data-testid="stForm"] [data-baseweb="tag"] {
        background-color: #F5F0E5 !important;
        border-color: #D9BD80 !important;
        color: #14233B !important;
    }
    div[data-testid="stForm"] button[kind="primary"],
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
        background: #14233B !important;
        background-image: none !important;
        border: 1px solid #B99553 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    div[data-testid="stForm"] button[kind="primary"] p,
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button p {
        color: #14233B !important;
    }


    /* ORIVAN Welcome planner: white, gold, and navy theme */
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #D9BD80 !important;
        border-radius: 18px !important;
        color: #14233B !important;
    }

    div[data-testid="stForm"] .planner-step {
        background: #FFFFFF !important;
        border: 1px solid #D9BD80 !important;
        border-left: 4px solid #D9BD80 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        color: #14233B !important;
    }

    div[data-testid="stForm"] .planner-step strong {
        color: #14233B !important;
    }

    div[data-testid="stForm"] .planner-step small {
        background: #FFFFFF !important;
        color: #84652F !important;
        border: 1px solid #D9BD80 !important;
    }

    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea,
    div[data-testid="stForm"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #14233B !important;
        border-color: #D9BD80 !important;
        border-radius: 9px !important;
    }

    div[data-testid="stForm"] label {
        color: #14233B !important;
    }

    div[data-testid="stForm"] input:focus,
    div[data-testid="stForm"] textarea:focus,
    div[data-testid="stForm"] [data-baseweb="select"] > div:focus-within {
        border-color: #B99553 !important;
        box-shadow: 0 0 0 2px rgba(185, 149, 83, 0.25) !important;
    }


    /* ORIVAN final white-gold-navy control fix */

    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        color: #14233B !important;
    }

    /* Text fields and date inputs */
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #14233B !important;
        -webkit-text-fill-color: #14233B !important;
        border: 1px solid #D9BD80 !important;
        color-scheme: light !important;
    }

    /* Dropdown control: override dark theme backgrounds */
    div[data-testid="stForm"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #14233B !important;
        border: 1px solid #D9BD80 !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] [data-baseweb="select"] input {
        background: #FFFFFF !important;
        color: #14233B !important;
        -webkit-text-fill-color: #14233B !important;
    }

    div[data-testid="stForm"] [data-baseweb="select"] span,
    div[data-testid="stForm"] [data-baseweb="select"] svg {
        color: #14233B !important;
        fill: #14233B !important;
    }

    /* Navy labels and headings */
    div[data-testid="stForm"] label,
    div[data-testid="stForm"] .planner-step strong {
        color: #14233B !important;
    }

    /* Replace the pink selected radio with navy and gold */
    div[data-testid="stForm"] [role="radio"][aria-checked="true"] {
        border-color: #14233B !important;
    }

    div[data-testid="stForm"] [role="radio"][aria-checked="true"] > div {
        background-color: #14233B !important;
        border-color: #D9BD80 !important;
    }

    div[data-testid="stForm"] input[type="radio"],
    div[data-testid="stForm"] input[type="checkbox"] {
        accent-color: #14233B !important;
    }

    /* Gold focus border */
    div[data-testid="stForm"] input:focus,
    div[data-testid="stForm"] textarea:focus,
    div[data-testid="stForm"] [data-baseweb="select"] > div:focus-within {
        border-color: #B99553 !important;
        box-shadow: 0 0 0 2px rgba(185, 149, 83, 0.25) !important;
    }

    /* White step cards */
    div[data-testid="stForm"] .planner-step {
        background: #FFFFFF !important;
        border: 1px solid #D9BD80 !important;
        border-left: 4px solid #D9BD80 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
    }

    </style>
    <div class="planner-heading">
      <div class="eyebrow">Your life. Your pace. Your future.</div>
      <h2>A plan that fits your life.</h2>
      <p>Tell ORIVAN about your work, responsibilities, rest, and available time.
      The goal is a realistic review routine—not an exhausting schedule you cannot maintain.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="planner-note">You can choose “Not applicable” wherever a responsibility does not apply. '
        'Your answers below are currently used for a preview only; they are not yet saved to an account.</div>',
        unsafe_allow_html=True,
    )

    with st.form("orivan_complete_study_planner"):
        st.markdown(
            '<div class="planner-step"><small>STEP 01</small><strong>Your current situation</strong></div>',
            unsafe_allow_html=True,
        )
        work_status = st.selectbox(
            "Which best describes you?",
            [
                "Employed full-time",
                "Employed part-time",
                "Working student",
                "Full-time student",
                "Self-employed"
            ],
            key="planner_work_status",
        )
        work_pattern = st.selectbox(
            "What is your usual work or school schedule?",
            [
                "Fixed daytime schedule", "Night shift",
                "Rotating or changing shifts", "Flexible hours",
                "Different schedule each day", "No work or school schedule",
                "Other / not sure"
            ],
            key="planner_work_pattern",
        )
        c1, c2 = st.columns(2)
        with c1:
            work_start = st.time_input(
                "Usual start time (if applicable)",
                value=__import__("datetime").time(8, 0),
                key="planner_work_start",
            )
        with c2:
            work_end = st.time_input(
                "Usual end time (if applicable)",
                value=__import__("datetime").time(17, 0),
                key="planner_work_end",
            )
        school_days = st.multiselect(
            "Which days are usually busy with work or school?",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            key="planner_busy_days",
        )

        st.markdown(
            '<div class="planner-step"><small>STEP 02</small><strong>Your other commitments</strong></div>',
            unsafe_allow_html=True,
        )
        commute = st.selectbox(
            "Daily travel or commute time",
            ["No commute", "Under 30 minutes", "30–60 minutes",
             "1–2 hours", "More than 2 hours", "Varies by day", "Not applicable"],
            key="planner_commute",
        )
        responsibilities = st.multiselect(
            "What else takes up your time?",
            [
                "Household chores", "Childcare or caregiving",
                "Church or community activities", "Family responsibilities",
                "Second job or side business", "Appointments or other commitments",
                "Exercise or personal activities", "None of these"
            ],
            key="planner_responsibilities",
        )
        responsibility_details = st.text_area(
            "Any regular commitments or days we should consider? (optional)",
            placeholder="Example: I help my family every Sunday morning.",
            key="planner_responsibility_details",
        )

        st.markdown(
            '<div class="planner-step"><small>STEP 03</small><strong>Your exam and review starting point</strong></div>',
            unsafe_allow_html=True,
        )
        exam_status = st.radio(
            "What do you know about your exam date?",
            [
                "My exam date is announced",
                "The exam date is not announced yet",
                "I want a flexible six-month plan"
            ],
            key="planner_exam_status",
        )
        exam_date = None
        if exam_status == "My exam date is announced":
            exam_date = st.date_input(
                "Target exam date",
                value=date.today(),
                min_value=date.today(),
                key="planner_target_exam_date",
            )
        starting_level = st.selectbox(
            "Where are you in your LET preparation?",
            [
                "Starting from scratch", "I have studied some topics",
                "I have reviewed before but need a fresh start",
                "I am reviewing and need more practice",
                "I am close to exam readiness"
            ],
            key="planner_starting_level",
        )
        weakest_subjects = st.multiselect(
            "Which areas would you like to prioritize?",
            [
                "General Education", "Professional Education",
                "Specialization / Majorship", "Mathematics",
                "English and communication", "Educational theories",
                "Assessment and evaluation", "I am not sure yet"
            ],
            key="planner_weakest_subjects",
        )

        st.markdown(
            '<div class="planner-step"><small>STEP 04</small><strong>Your study and rest routine</strong></div>',
            unsafe_allow_html=True,
        )
        available_days = st.multiselect(
            "Which days can you realistically study?",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday", "Wednesday", "Friday", "Saturday"],
            key="planner_available_days",
        )
        daily_hours = st.select_slider(
            "How much time can you usually study on an available day?",
            options=[0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6],
            value=1.5,
            format_func=lambda x: f"{x:g} hour" if x == 1 else f"{x:g} hours",
            key="planner_daily_hours",
        )
        session_style = st.radio(
            "How would you prefer to divide your study time?",
            [
                "One study session",
                "Two shorter sessions",
                "Several short sessions",
                "Let the planner suggest a routine"
            ],
            key="planner_session_style",
        )
        preferred_time = st.selectbox(
            "When do you usually have the most energy to study?",
            [
                "Early morning", "Morning", "Afternoon", "Evening",
                "Late night", "It changes by day", "Not sure yet"
            ],
            key="planner_preferred_time",
        )
        c1, c2 = st.columns(2)
        with c1:
            wake_time = st.time_input(
                "Usual wake-up time",
                value=__import__("datetime").time(6, 0),
                key="planner_wake_time",
            )
        with c2:
            bedtime = st.time_input(
                "Usual bedtime",
                value=__import__("datetime").time(22, 0),
                key="planner_bedtime",
            )
        sleep_goal = st.selectbox(
            "How much sleep would you like to protect each night?",
            ["6 hours", "7 hours", "8 hours", "9 hours", "It varies; help me plan rest"],
            index=2,
            key="planner_sleep_goal",
        )
        break_length = st.selectbox(
            "Preferred break between study sessions",
            ["5 minutes", "10 minutes", "15 minutes", "20 minutes", "30 minutes"],
            index=2,
            key="planner_break_length",
        )
        rest_days = st.multiselect(
            "Which days should normally stay free from planned study?",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            key="planner_rest_days",
        )

        st.markdown(
            '<div class="planner-step"><small>STEP 05</small><strong>Reminders and flexibility</strong></div>',
            unsafe_allow_html=True,
        )
        reminder_frequency = st.selectbox(
            "How often would you prefer a study reminder?",
            ["No reminders", "Once on study days", "Before each planned session", "Weekly planning reminder"],
            key="planner_reminder_frequency",
        )
        reminder_time = st.time_input(
            "Preferred reminder time",
            value=__import__("datetime").time(19, 0),
            key="planner_reminder_time",
        )
        tired_day = st.selectbox(
            "What should your plan suggest on a very tiring day?",
            [
                "Offer a shorter review", "Move the session to another available day",
                "Offer a rest day and adjust later", "Let me decide each time"
            ],
            key="planner_tired_day",
        )
        st.caption("Work times, sleep times, and commitments are planning inputs. Choose what best reflects your usual week; changing shifts can be handled more precisely in a future schedule editor.")

        submitted = st.form_submit_button(
            "Build my study-plan preview",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        study_days_final = [d for d in available_days if d not in rest_days]
        weekly_hours = daily_hours * len(study_days_final)
        st.session_state["welcome_plan_preview"] = {
            "work_status": work_status,
            "work_pattern": work_pattern,
            "work_start": work_start.strftime("%I:%M %p"),
            "work_end": work_end.strftime("%I:%M %p"),
            "busy_days": school_days,
            "commute": commute,
            "responsibilities": responsibilities,
            "responsibility_details": responsibility_details.strip(),
            "exam_status": exam_status,
            "exam_date": str(exam_date) if exam_date else None,
            "starting_level": starting_level,
            "weakest_subjects": weakest_subjects,
            "days": study_days_final,
            "rest_days": rest_days,
            "daily_hours": daily_hours,
            "weekly_hours": weekly_hours,
            "session_style": session_style,
            "preferred_time": preferred_time,
            "wake_time": wake_time.strftime("%I:%M %p"),
            "bedtime": bedtime.strftime("%I:%M %p"),
            "sleep_goal": sleep_goal,
            "break_length": break_length,
            "reminder_frequency": reminder_frequency,
            "reminder_time": reminder_time.strftime("%I:%M %p"),
            "tired_day": tired_day,
        }

    preview = st.session_state.get("welcome_plan_preview")
    if preview:
        import html

        def plan_text(value):
            return html.escape(str(value if value not in (None, "") else "Not specified"))

        def plan_list(values, empty="None selected"):
            return ", ".join(str(x) for x in values) if values else empty

        st.markdown("""
        <style>
        .plan-preview-shell {
            margin: 22px 0 26px;
            border: 1px solid #D9BD80;
            border-radius: 22px;
            overflow: hidden;
            background: #FFFFFF;
            box-shadow: 0 14px 36px rgba(20,35,59,.10);
        }
        .plan-preview-header {
            padding: 27px 30px 25px;
            background:
                radial-gradient(ellipse at 95% 0%, rgba(217,189,128,.18), transparent 38%),
                linear-gradient(125deg,#101D32,#14233B 58%,#2A405B);
            border-bottom: 1px solid #D9BD80;
        }
        .plan-preview-eyebrow {
            color: #D9BD80;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 2.4px;
            text-transform: uppercase;
            margin-bottom: 9px;
        }
        .plan-preview-title {
            color: #FFFFFF;
            font-family: Georgia,serif;
            font-size: clamp(25px,3vw,34px);
            font-weight: 600;
            line-height: 1.2;
            margin: 0 0 9px;
        }
        .plan-preview-subtitle {
            color: #E0E7F0;
            font-size: 14px;
            line-height: 1.7;
            margin: 0;
            max-width: 620px;
        }
        .plan-preview-body { padding: 23px; }
        .plan-preview-stat {
            height: 100%;
            min-height: 148px;
            padding: 20px;
            border-radius: 16px;
            background: linear-gradient(145deg,#FFFFFF,#F8F7F3);
            border: 1px solid #E7E2D8;
            border-top: 3px solid #D9BD80;
        }
        .plan-preview-stat-label {
            color: #536174;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .plan-preview-stat-value {
            color: #14233B;
            font-family: Georgia,serif;
            font-size: clamp(29px,3vw,38px);
            font-weight: 700;
            line-height: 1.25;
            margin: 12px 0 5px;
            overflow-wrap: anywhere;
        }
        .plan-preview-stat-note { color: #788294; font-size: 12px; line-height: 1.5; }
        .plan-preview-section-title {
            color: #14233B;
            font-family: Georgia,serif;
            font-size: 20px;
            font-weight: 700;
            margin: 25px 0 12px;
        }
        .plan-preview-grid {
            display: grid;
            grid-template-columns: repeat(3,minmax(0,1fr));
            gap: 12px;
            align-items: stretch;
        }
        .plan-preview-detail {
            min-width: 0;
            padding: 14px 15px;
            background: #FFFFFF;
            border: 1px solid #E7E2D8;
            border-radius: 12px;
        }
        .plan-preview-detail-label {
            color: #788294;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .plan-preview-detail-value {
            color: #14233B;
            font-size: 13px;
            font-weight: 650;
            line-height: 1.6;
            overflow-wrap: anywhere;
        }
        .plan-preview-priorities {
            margin-top: 12px;
            padding: 17px;
            background: #F8F7F3;
            border: 1px solid #E7E2D8;
            border-left: 4px solid #D9BD80;
            border-radius: 12px;
        }
        .plan-preview-notice {
            margin-top: 18px;
            padding: 15px 17px;
            background: #F5F0E5;
            border: 1px solid #D9BD80;
            border-radius: 12px;
            color: #39465A;
            font-size: 12px;
            line-height: 1.75;
        }
        @media(max-width:760px) {
            .plan-preview-grid {grid-template-columns: repeat(2,minmax(0,1fr));}
        }
        @media(max-width:480px) {
            .plan-preview-grid {grid-template-columns: 1fr;}
        }
        @media(max-width:600px) {
            .plan-preview-header {padding:22px 19px;}
            .plan-preview-body {padding:15px;}
            .plan-preview-grid {grid-template-columns:1fr;}
            .plan-preview-stat {min-height:125px;}
        }
        </style>
        """, unsafe_allow_html=True)

        weekly_hours = preview.get("weekly_hours", 0)
        daily_hours = preview.get("daily_hours", 0)
        study_days = plan_list(preview.get("days", []), "No study days selected")
        rest_days = plan_list(preview.get("rest_days", []), "No fixed rest days selected")
        responsibilities = plan_list(preview.get("responsibilities", []))
        priorities = plan_list(preview.get("weakest_subjects", []), "Not selected yet")

        details = [
            ("Work or study status", preview.get("work_status")),
            ("Schedule type", preview.get("work_pattern")),
            ("Commute", preview.get("commute")),
            ("Preferred study time", preview.get("preferred_time")),
            ("Study session style", preview.get("session_style")),
            ("Study days", study_days),
            ("Rest days", rest_days),
            ("Sleep goal", preview.get("sleep_goal")),
            ("Usual sleep window", f"{preview.get('bedtime', 'Not specified')} to {preview.get('wake_time', 'Not specified')}"),
            ("Tired-day preference", preview.get("tired_day")),
            ("Exam plan", preview.get("exam_status")),
            ("Reminder preference", f"{preview.get('reminder_frequency', 'Not specified')} · {preview.get('reminder_time', 'Not specified')}"),
        ]

        detail_html = "".join(
            '<div class="plan-preview-detail">'
            f'<div class="plan-preview-detail-label">{plan_text(label)}</div>'
            f'<div class="plan-preview-detail-value">{plan_text(value)}</div>'
            '</div>'
            for label, value in details
        )

        exam_date_html = ""
        if preview.get("exam_date"):
            exam_date_html = (
                '<div class="plan-preview-detail">'
                '<div class="plan-preview-detail-label">Target exam date</div>'
                f'<div class="plan-preview-detail-value">{plan_text(preview["exam_date"])}</div>'
                '</div>'
            )

        notes_html = ""
        if preview.get("responsibility_details"):
            notes_html = (
                '<div style="margin-top:12px">'
                '<div class="plan-preview-detail-label">Your notes</div>'
                f'<div class="plan-preview-detail-value">{plan_text(preview["responsibility_details"])}</div>'
                '</div>'
            )

        st.markdown(
            '<div class="plan-preview-shell">'
            '<div class="plan-preview-header">'
            '<div class="plan-preview-eyebrow">YOUR CURRENT SETTINGS · PERSONAL STUDY PROFILE</div>'
            '<div class="plan-preview-title">Your study-plan preview</div>'
            '<p class="plan-preview-subtitle">A clearer view of your goals, available time, and preferences—all in one place.</p>'
            '</div>'
            '<div class="plan-preview-body">'
            '<div class="plan-preview-grid">'
            '<div class="plan-preview-stat">'
            '<div class="plan-preview-stat-label">Weekly study goal</div>'
            f'<div class="plan-preview-stat-value">{plan_text(weekly_hours)} <span style="font-size:16px;font-family:Arial,sans-serif">hours</span></div>'
            '<div class="plan-preview-stat-note">Your planned study time across the week</div>'
            '</div>'
            '<div class="plan-preview-stat">'
            '<div class="plan-preview-stat-label">Daily study goal</div>'
            f'<div class="plan-preview-stat-value">{plan_text(daily_hours)} <span style="font-size:16px;font-family:Arial,sans-serif">hours</span></div>'
            '<div class="plan-preview-stat-note">Your selected study time on each study day</div>'
            '</div>'
            '</div>'
            '<div class="plan-preview-section-title">Your routine at a glance</div>'
            f'<div class="plan-preview-grid">{detail_html}{exam_date_html}</div>'
            '<div class="plan-preview-priorities">'
            '<div class="plan-preview-detail-label">Priority subjects</div>'
            f'<div class="plan-preview-detail-value">{plan_text(priorities)}</div>'
            '<div style="height:12px"></div>'
            '<div class="plan-preview-detail-label">Other commitments</div>'
            f'<div class="plan-preview-detail-value">{plan_text(responsibilities)}</div>'
            f'{notes_html}'
            '</div>'
            '<div class="plan-preview-notice"><strong>Prototype status:</strong> This is a summary of your preferences, not an automatically generated calendar. This version does not yet save these settings to an account, send notifications, or automatically reschedule missed sessions.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # ORIVAN_STUDY_BALANCE_RECOMMENDATIONS
    # Analyze the visitor's actual planner answers without changing
    # the saved quiz data or the existing study-plan form.
    if preview:
        st.markdown("---")
        st.markdown("### Study balance & recommendations")
        st.caption(
            "These suggestions use your answers to help you review "
            "your plan. They are planning guidance, not a test score."
        )

        suggestions = []
        warnings = []

        planned_days = preview.get("days", []) or []
        protected_rest_days = preview.get("rest_days", []) or []
        priorities_selected = preview.get("weakest_subjects", []) or []
        hours_per_day = float(preview.get("daily_hours", 0) or 0)
        hours_per_week = float(preview.get("weekly_hours", 0) or 0)

        overlapping_days = sorted(
            set(planned_days).intersection(protected_rest_days)
        )

        if not planned_days or hours_per_day <= 0:
            warnings.append(
                (
                    "Your study time needs attention",
                    "Choose at least one study day and allow some study "
                    "time, or revise the plan to fit your current routine."
                )
            )
        elif hours_per_week < 4:
            suggestions.append(
                (
                    "Build a consistent starting routine",
                    f"Your plan provides {hours_per_week:g} study hours "
                    "per week. If this fits your life, use that time "
                    "consistently and review your progress each week."
                )
            )
        elif hours_per_week > 25:
            warnings.append(
                (
                    "Review your weekly workload",
                    f"Your plan adds up to {hours_per_week:g} hours "
                    "per week. Check that this fits around work, sleep, "
                    "family responsibilities, and rest. Reduce it if "
                    "the schedule feels difficult to sustain."
                )
            )
        else:
            suggestions.append(
                (
                    "Protect your planned study time",
                    f"You have planned {hours_per_week:g} hours per week "
                    f"across {len(planned_days)} days. Treat these as "
                    "available study blocks, and adjust them when your "
                    "real schedule changes."
                )
            )

        if overlapping_days:
            warnings.append(
                (
                    "Your study and rest days overlap",
                    "These days are marked for both study and rest: "
                    + ", ".join(overlapping_days)
                    + ". Decide which days should be free and update "
                    "your selections."
                )
            )

        if not priorities_selected or "I am not sure yet" in priorities_selected:
            suggestions.append(
                (
                    "Find your priority subjects",
                    "Take a short diagnostic quiz in General Education, "
                    "Professional Education, and your Specialization / "
                    "Majorship. Use your results to decide which areas "
                    "need more practice."
                )
            )
        else:
            priority_text = ", ".join(
                item for item in priorities_selected
                if item != "I am not sure yet"
            )
            if priority_text:
                suggestions.append(
                    (
                        "Use your priorities to guide review",
                        "You selected: " + priority_text
                        + ". Give these areas focused practice, but keep "
                        "all three main LET subject areas in your weekly "
                        "review rotation."
                    )
                )

        starting_level = preview.get("starting_level", "")
        if starting_level == "Starting from scratch":
            suggestions.append(
                (
                    "Start with lessons before long tests",
                    "Build your foundation with lesson notes and worked "
                    "examples, then answer practice questions and review "
                    "your mistakes."
                )
            )
        elif starting_level == "I have studied some topics":
            suggestions.append(
                (
                    "Combine learning and practice",
                    "Study one topic at a time, answer practice questions, "
                    "and revisit concepts you find difficult."
                )
            )
        elif starting_level == "I have reviewed before but need a fresh start":
            suggestions.append(
                (
                    "Refresh your foundation",
                    "Begin with a short diagnostic quiz, then review "
                    "the lessons behind your incorrect answers."
                )
            )
        elif starting_level == "I am reviewing and need more practice":
            suggestions.append(
                (
                    "Use mistakes to guide your next session",
                    "Practice questions, check explanations, and return "
                    "to topics you miss. Keep reviewing the other subjects "
                    "so your preparation stays broad."
                )
            )
        elif starting_level == "I am close to exam readiness":
            suggestions.append(
                (
                    "Check readiness with timed practice",
                    "Use timed practice tests and review every mistake. "
                    "A self-reported readiness level is a starting point, "
                    "not proof of exam readiness."
                )
            )

        exam_date_value = preview.get("exam_date")
        if exam_date_value:
            try:
                target_date = date.fromisoformat(str(exam_date_value))
                days_remaining = (target_date - date.today()).days

                if days_remaining < 0:
                    warnings.append(
                        (
                            "Check your target exam date",
                            "The saved target date has passed. Update it "
                            "if you are preparing for a future examination."
                        )
                    )
                elif days_remaining <= 30:
                    warnings.append(
                        (
                            "Your target exam date is approaching",
                            f"There are {days_remaining} days until your "
                            "selected date. Focus on high-priority topics, "
                            "practice questions, and reviewing mistakes. "
                            "Keep enough time for rest."
                        )
                    )
                else:
                    suggestions.append(
                        (
                            "Plan around your target date",
                            f"You have {days_remaining} days until your "
                            "selected exam date. Divide that time among "
                            "learning, practice, and reviewing mistakes."
                        )
                    )
            except (TypeError, ValueError):
                suggestions.append(
                    (
                        "Confirm your exam date",
                        "Check that your target exam date is correct so "
                        "you can plan your review timeline."
                    )
                )
        elif preview.get("exam_status") == "The exam date is not announced yet":
            suggestions.append(
                (
                    "Prepare while waiting for the announcement",
                    "Use a flexible weekly routine and review all three "
                    "main LET subject areas while waiting for the official "
                    "exam date."
                )
            )
        else:
            suggestions.append(
                (
                    "Use a flexible six-month plan",
                    "Set weekly goals and check your progress regularly. "
                    "Adjust the plan when your schedule or review needs change."
                )
            )

        sleep_goal = str(preview.get("sleep_goal", ""))
        if sleep_goal == "6 hours":
            warnings.append(
                (
                    "Review your sleep goal",
                    "Six hours may be too little for many adults. Consider "
                    "whether you can protect 7–9 hours of sleep, and adjust "
                    "study time around your rest needs."
                )
            )
        elif sleep_goal in ("7 hours", "8 hours", "9 hours"):
            suggestions.append(
                (
                    "Protect sleep and recovery",
                    "Keep your chosen sleep goal in your schedule. Avoid "
                    "making up missed study time by repeatedly cutting sleep."
                )
            )
        else:
            suggestions.append(
                (
                    "Make rest part of the plan",
                    "Choose a realistic sleep routine and keep a little "
                    "flexibility for tiring days."
                )
            )

        if warnings:
            st.markdown("#### Items to review")
            for title, message in warnings:
                st.warning("**" + title + "**\n\n" + message)

        st.markdown("#### Suggested next steps")
        for index, (title, message) in enumerate(suggestions, start=1):
            with st.container(border=True):
                st.markdown(f"**{index:02d} · {title}**")
                st.write(message)

        st.caption(
            "These recommendations are based on your selected answers. "
            "The planner does not yet automatically generate a calendar "
            "or measure your subject mastery."
        )

    lessons_col, quiz_col = st.columns(2)
    with lessons_col:
        if st.button("Explore Lessons", type="primary", use_container_width=True):
            st.session_state["navigation_choice"] = "Preview Reviewer"
            st.rerun()
    with quiz_col:
        if st.button("Try a Practice Quiz", use_container_width=True):
            st.session_state["navigation_choice"] = "Practice Quiz"
            st.rerun()


elif page == "Preview Reviewer":
    import time
    from data.preview_quiz import PREVIEW_QUESTIONS

    st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important; max-width: 1120px;}
    .preview-kicker {color:#D9BD80;font-size:11px;font-weight:750;letter-spacing:2px;}
    .preview-hero {background:linear-gradient(125deg,#101C30,#263D5B);border:1px solid #D9BD80;border-radius:18px;padding:28px;margin:12px 0 26px;color:#fff;}
    .preview-hero h1 {color:#fff !important;font-family:Georgia,serif;font-size:clamp(27px,3vw,38px);margin:12px 0;}
    .preview-hero p {color:#E7ECF4;line-height:1.7;max-width:700px;}
    .preview-section-kicker {color:#9E7B45;font-size:11px;font-weight:800;letter-spacing:2px;margin-top:20px;}
    .preview-subject-card {height:148px;background:#14233B;border:1px solid #435875;border-radius:14px;padding:18px;color:#fff;display:flex;flex-direction:column;justify-content:center;}
    .preview-subject-card.selected {border:2px solid #D9BD80;background:linear-gradient(145deg,#1C304D,#14233B);}
    .preview-subject-card h3 {color:#fff !important;font-size:16px;margin:10px 0 6px;}
    .preview-subject-card p {color:#E5EAF2 !important;font-size:13px;line-height:1.5;margin:0;}
    .preview-panel {background:#fff;border:1px solid #E6E0D5;border-radius:15px;padding:20px;margin:10px 0;}
    .preview-note {background:#F5F2EB;border-left:4px solid #D9BD80;border-radius:8px;padding:14px 16px;color:#26364D;}
    .preview-cta {background:#14233B;border:1px solid #D9BD80;border-radius:15px;padding:22px;margin-top:24px;}
    .preview-cta h3 {color:#fff !important;font-family:Georgia,serif;}
    .preview-cta p {color:#E5EAF2 !important;}
    div[data-testid="stButton"] button {border-radius:9px;font-weight:650;}
    div[data-testid="stButton"] button[kind="primary"] {background:#14233B;color:#fff;border:1px solid #D9BD80;}
    div[data-testid="stButton"] button[kind="primary"] * {color:#fff !important;}

    .preview-subject-card h3 { margin-bottom:3px !important; }
    .preview-subject-card p { margin-top:0 !important; line-height:1.4 !important; }
    div[data-testid="stButton"] button { color:#FFFFFF !important; }
    div[data-testid="stButton"] button p,
    div[data-testid="stButton"] button span,
    div[data-testid="stButton"] button div {
        color:#FFFFFF !important;
    }
    div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] label {font-weight:650;}
    </style>
    <div class="preview-hero">
      <div style="display:flex;align-items:center;gap:14px;">
        <div><div class="preview-kicker">ORIVAN · GUEST ACCESS</div><h1>Preview Reviewer</h1></div>
      </div>
      <p>Explore sample learning materials and experience a timed practice preview for your LET preparation.</p>
      <div class="preview-kicker">LEARN · PRACTICE · REVIEW YOUR MISTAKES</div>
    </div>
    <div class="preview-section-kicker">STEP 1</div>
    <h2 style="font-family:Georgia,serif;color:#14233B;">Choose a subject area</h2>
    <p style="color:#536174;">Choose a section to explore its sample lesson and practice questions.</p>
    """.replace("{logo_data}", logo_data), unsafe_allow_html=True)

    subject_names = list(lessons.keys())
    subject_display = {
        "General Education": ("", "General Education", "Core knowledge and skills"),
        "Professional Education": ("", "Professional Education", "Teaching and learning"),
        "Major: Food and Service Management": ("", "Specialization / Majorship", "Your chosen major"),
    }

    if "preview_subject" not in st.session_state or st.session_state.preview_subject not in subject_names:
        st.session_state.preview_subject = subject_names[0]

    columns = st.columns(3, gap="medium")
    for index, name in enumerate(subject_names):
        icon, title, subtitle = subject_display.get(name, ("•", name, "Sample topics"))
        selected = st.session_state.preview_subject == name
        with columns[index]:
            st.markdown(
                f'<div class="preview-subject-card {"selected" if selected else ""}">'
                f'<h3 style="font-family:Georgia,\'Times New Roman\',serif;font-size:22px;font-weight:700;letter-spacing:-0.4px;color:#14233B;margin:8px 0 12px;">{title}</h3>'
                f'<p style="font-family:\'DM Sans\',Arial,sans-serif;font-size:14px;line-height:1.7;color:#536174;">{subtitle}</p></div>',
                unsafe_allow_html=True,
            )
            if st.button("Selected ✓" if selected else "Explore topics →",
                         key=f"preview_subject_btn_{index}", use_container_width=True):
                st.session_state.preview_subject = name
                st.rerun()

    selected_subject = st.session_state.preview_subject
    topic_names = list(lessons[selected_subject].keys())
    st.markdown('<div class="preview-section-kicker">STEP 2 · SAMPLE LESSON</div>', unsafe_allow_html=True)
    selected_topic = st.selectbox("Choose a sample topic", topic_names, key="preview_topic")
    lesson = lessons[selected_subject][selected_topic]

    st.markdown('<div class="preview-panel">', unsafe_allow_html=True)
    st.caption(subject_display.get(selected_subject, ("", selected_subject, ""))[1])
    st.markdown(f"## {selected_topic}")
    st.markdown(
        """
        <div style="
            display:flex;
            align-items:center;
            gap:10px;
            margin:8px 0 18px;
            padding:12px 16px;
            background:#F5F0E5;
            border:1px solid #E7D9B8;
            border-radius:10px;
        ">
            <span style="color:#9E7B45;font-size:19px;">✦</span>
            <div>
                <div style="color:#14233B;font-weight:700;font-size:13px;">
                    SAMPLE LESSON
                </div>
                <div style="color:#536174;font-size:13px;line-height:1.5;">
                    Explore the lesson format and learning materials available in ORIVAN.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    lesson_tab, practice_tab = st.tabs(["Lesson Notes", "Timed Practice Preview"])

    with lesson_tab:
        if selected_subject == "General Education" and selected_topic == "Mathematics":
            st.markdown("""
            <style>
            .vm-title {font-family:Georgia,serif;color:#14233B;font-size:27px;font-weight:700;margin:4px 0 5px;}
            .vm-sub {color:#46546A;font-size:14px;margin-bottom:18px;}
            .vm-card {background:linear-gradient(145deg,#FFFEFA 0%,#F0EDE5 100%);border:1px solid #BDB4A4;border-radius:16px;padding:18px;margin:12px 0;box-shadow:0 7px 20px rgba(20,35,59,.08);}
            .vm-label {font-size:11px;font-weight:800;letter-spacing:1.5px;color:#78551B;margin-bottom:8px;}
            .vm-number {font-family:Georgia,serif;font-size:32px;font-weight:700;color:#14233B;line-height:1.15;}
            .vm-small {font-size:13px;color:#36465C;line-height:1.55;}
            .vm-arrow {font-size:25px;color:#B59657;text-align:center;padding:2px;}
            .vm-equation {background:linear-gradient(135deg,#14233B,#263D5B);border:1px solid #A98239;border-radius:11px;padding:13px;text-align:center;font-size:20px;font-weight:750;color:#FFFDF7;box-shadow:0 4px 12px rgba(20,35,59,.12);}
            .vm-result {background:linear-gradient(135deg,#101C30,#263D5B);border:1px solid #B88A32;border-radius:14px;padding:18px;color:#FFFFFF;text-align:center;box-shadow:0 8px 20px rgba(20,35,59,.16);}
            .vm-result strong {display:block;font-family:Georgia,serif;font-size:38px;color:#F4D27C;}
            .vm-step {background:linear-gradient(145deg,#FFFEFA,#EAE6DC);border:1px solid #BDB4A4;border-radius:12px;padding:14px;margin:8px 0;box-shadow:0 4px 12px rgba(20,35,59,.06);}
            .vm-stepnum {display:inline-block;background:#14233B;color:#FFFFFF;border-radius:50%;width:27px;height:27px;line-height:27px;text-align:center;font-weight:800;margin-right:8px;}
            .vm-grid {display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:4px;max-width:390px;margin:14px auto;}
            .vm-cell {aspect-ratio:1;border-radius:4px;border:1px solid #AEB6C1;background:#FFFDF7;}
            .vm-cell.on {background:#B88A32;border-color:#79591F;}
            .vm-legend {display:flex;justify-content:center;gap:16px;flex-wrap:wrap;color:#36465C;font-size:12px;}
            .vm-dot {display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;}
            @media(max-width:500px){.vm-card{padding:13px}.vm-number{font-size:27px}.vm-grid{gap:3px}}
            </style>
            <div class="vm-title">Percentages, made visual</div>
            <div class="vm-sub">See it. Follow the steps. Then try it yourself.</div>
            <div class="vm-card">
              <div class="vm-label">01 · THE BIG IDEA</div>
              <div style="text-align:center;font-family:Georgia,serif;font-size:23px;font-weight:700;color:#14233B;">Percent means “out of 100”</div>
              <div class="vm-grid">__GRID__</div>
              <div class="vm-legend">
                <span><i class="vm-dot" style="background:#D9BD80"></i>50 colored squares</span>
                <span><i class="vm-dot" style="background:#F4F1EA;border:1px solid #DAD5CA"></i>50 empty squares</span>
              </div>
              <div class="vm-equation" style="margin-top:14px;">50 out of 100 = 50%</div>
              <div class="vm-small" style="text-align:center;margin-top:8px;">Each small square represents 1%.</div>
            </div>
            <div class="vm-label" style="margin-top:24px;">02 · WATCH A SOLUTION</div>
            <div style="font-family:Georgia,serif;font-size:23px;font-weight:700;color:#14233B;margin-bottom:8px;">A student got 36 out of 40 correct.</div>
            <div class="vm-card">
              <div class="vm-small">How do we find the score in percent?</div>
              <div style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;margin:16px 0;">
                <div style="background:#F5F0E5;border:1px solid #E7D9B8;border-radius:12px;padding:14px;text-align:center;min-width:105px;">
                  <div class="vm-small">CORRECT</div><div class="vm-number">36</div>
                </div>
                <div class="vm-arrow">÷</div>
                <div style="background:#F5F0E5;border:1px solid #E7D9B8;border-radius:12px;padding:14px;text-align:center;min-width:105px;">
                  <div class="vm-small">TOTAL</div><div class="vm-number">40</div>
                </div>
              </div>
              <div class="vm-arrow">↓</div>
              <div class="vm-equation">36 ÷ 40 = 0.9</div>
              <div class="vm-arrow">↓ multiply by 100</div>
              <div class="vm-result"><span>FINAL SCORE</span><strong>90%</strong>36 out of 40 answers are correct.</div>
            </div>
            """.replace("__GRID__", "".join(
                '<div class="vm-cell on"></div>' if i < 50
                else '<div class="vm-cell"></div>'
                for i in range(100)
            )), unsafe_allow_html=True)

            st.markdown("""
            <div class="vm-label" style="margin-top:24px;">03 · YOUR TURN</div>
            <div style="font-family:Georgia,serif;font-size:23px;font-weight:700;color:#14233B;">What is 25% of 80?</div>
            <div class="vm-sub">Reveal one step at a time. Follow along before moving on.</div>
            """, unsafe_allow_html=True)

            practice_key = "preview_visual_percent_step"
            if practice_key not in st.session_state:
                st.session_state[practice_key] = 1

            practice_steps = [
                ("Understand", "25% means 25 out of every 100.", "25 / 100"),
                ("Multiply", "Change 25% to a decimal, then multiply by 80.", "0.25 × 80 = 20"),
                ("Answer", "One quarter of 80 is 20.", "20"),
            ]

            for i, (title, description, equation) in enumerate(practice_steps, start=1):
                if i <= st.session_state[practice_key]:
                    st.markdown(
                        f'<div class="vm-step"><span class="vm-stepnum">{i}</span>'
                        f'<strong style="color:#14233B;">{title}</strong>'
                        f'<div style="margin:10px 0 7px 36px;color:#536174;">{description}</div>'
                        f'<div class="vm-equation" style="margin-left:36px;">{equation}</div></div>',
                        unsafe_allow_html=True,
                    )

            left, right = st.columns(2)
            with left:
                if st.session_state[practice_key] < 3:
                    if st.button("Reveal next step →", type="primary",
                                 use_container_width=True, key="preview_visual_percent_next"):
                        st.session_state[practice_key] += 1
                        st.rerun()
                else:
                    st.success("You completed all three steps!")
            with right:
                if st.button("Start again ↺", use_container_width=True,
                             key="preview_visual_percent_reset"):
                    st.session_state[practice_key] = 1
                    st.rerun()

            st.markdown("""
            <div class="vm-card">
              <div class="vm-label">REMEMBER THIS</div>
              <div class="vm-equation">Part ÷ Whole × 100 = Percent</div>
              <div class="vm-small" style="margin-top:10px;">First divide the part by the total. Then multiply by 100.</div>
            </div>
            """, unsafe_allow_html=True)
        elif selected_subject == "Professional Education" and selected_topic == "Learning Theories":
            st.html("""
            <style>
.lt-simple {
    background: #F4F0E7;
    border: 1px solid #E2D4B8;
    border-left: 4px solid #B9944D;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 10px 0 14px;
    color: #263244;
    font-size: 14px;
    line-height: 1.75;
}
.lt-simple strong, .lt-check-steps strong {
    color: #684B17;
    font-size: 11px;
    letter-spacing: .7px;
}
.lt-check-steps {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0;
}
.lt-check-steps > div {
    background: #FFFFFF;
    border: 1px solid #E2D4B8;
    border-radius: 10px;
    padding: 13px;
    color: #303B4B;
    font-size: 14px;
    line-height: 1.7;
}
.lt-check-example {
    background: #FFFFFF;
    border: 1px solid #E2D4B8;
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 12px;
    color: #303B4B;
    font-size: 14px;
    line-height: 1.75;
}
.lt-check-example > strong { color: #684B17; letter-spacing: .7px; font-size: 11px; }
.lt-check-example p { margin: 8px 0 0; color: #303B4B !important; }
@media(max-width:600px) {
    .lt-check-steps { grid-template-columns: 1fr; }
}
/* Keep the existing practice code, but hide its tab beside Lesson Notes. */
div[data-baseweb="tab-list"] > button:nth-child(2) {
    display: none !important;
}

            

.lt-intro {
    background: linear-gradient(135deg, #FFFDF8, #F4EBDD);
    color: #263244;
    border: 1px solid #D8BD83;
    border-radius: 16px;
    padding: 26px;
    margin: 12px 0 22px;
    box-shadow: 0 4px 14px rgba(45, 42, 34, 0.06);
}
.lt-intro h3 {
    color: #202C3D !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 30px;
    font-weight: 700;
    line-height: 1.3;
    margin: 0 0 12px;
}
.lt-intro p {
    color: #384659 !important;
    font-size: 16px;
    line-height: 1.8;
    margin: 0;
}
.lt-kicker {
    color: #80601E;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.3px;
    line-height: 1.6;
    margin: 22px 0 12px;
}
.lt-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}
.lt-card {
    background: #FFFFFF;
    border: 1px solid #E5DCCB;
    border-top: 4px solid #B9944D;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(45, 42, 34, 0.05);
    color: #263244;
}
.lt-head {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
}
.lt-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 38px;
    height: 38px;
    border-radius: 10px;
    background: #F2E7D1;
    color: #62491D;
    font-weight: 800;
    font-size: 13px;
}
.lt-card h4 {
    color: #202C3D !important;
    font-size: 21px;
    line-height: 1.35;
    margin: 0 0 5px;
}
.lt-theorist {
    color: #665B49;
    font-size: 13px;
    line-height: 1.6;
}
.lt-card p {
    color: #344154 !important;
    font-size: 15px;
    line-height: 1.75;
    margin: 8px 0 12px;
}
.lt-label {
    color: #80601E;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin: 16px 0 6px;
}
.lt-example {
    background: #F7F3EA;
    border-left: 3px solid #B9944D;
    border-radius: 0 8px 8px 0;
    color: #303B4B;
    padding: 12px 14px;
    font-size: 14px;
    line-height: 1.75;
}
.lt-memory {
    background: #FFFFFF;
    border: 1px solid #E5DCCB;
    border-radius: 14px;
    padding: 8px 18px;
}
.lt-row {
    display: grid;
    grid-template-columns: minmax(130px, 0.7fr) minmax(0, 1.5fr);
    gap: 14px;
    padding: 13px 4px;
    border-bottom: 1px solid #EEE7DB;
    color: #344154;
    font-size: 14px;
    line-height: 1.65;
}
.lt-row:last-child { border-bottom: 0; }
.lt-row strong { color: #202C3D; }
.lt-check {
    background: #F2E7D1;
    border: 1px solid #D8BD83;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 18px;
    color: #303B4B;
    font-size: 15px;
    line-height: 1.8;
}
.lt-check h4 {
    color: #202C3D !important;
    font-size: 18px;
    margin: 0 0 8px;
}
@media(max-width:600px) {
    .lt-grid { grid-template-columns: 1fr; }
    .lt-row { grid-template-columns: 1fr; gap: 3px; }
    .lt-intro { padding: 20px; }
    .lt-intro h3 { font-size: 25px; }
    .lt-card { padding: 17px; }
}
@media(max-width:600px){.lt-grid{grid-template-columns:1fr}.lt-row{grid-template-columns:1fr;gap:3px}}
            </style>
            <div class="lt-intro">
              <div style="color:#684B17;font-size:12px;font-weight:800;letter-spacing:1.2px;margin-bottom:8px">STUDY GUIDE · PROFESSIONAL EDUCATION</div>
              <h3>Understanding Learning Theories</h3>
              <p>Learning theories explain how people acquire knowledge, develop skills, and change their understanding or behavior. Teachers use them to plan lessons, select activities, and support learners.</p>
            </div>
            <div class="lt-kicker">01 · FOUR MAJOR THEORIES</div>
            <div class="lt-grid">
              <div class="lt-card">
                <div class="lt-head"><span class="lt-num">01</span><div><h4>Behaviorism</h4><div class="lt-theorist">B. F. Skinner · John B. Watson · Ivan Pavlov</div></div></div>
                <p>Focuses on observable behavior and how the environment influences it.</p>
                <div class="lt-simple"><strong>IN SIMPLE WORDS</strong><br>                People can change their behavior because of what happens after they act. Rewards may encourage a behavior, while punishment may discourage it.</div>
                <div class="lt-label">CLASSROOM EXAMPLE</div><div class="lt-example">A teacher praises a learner for completing work on time. Praise may encourage the learner to repeat the behavior.</div>
                <div class="lt-label">KEY IDEA</div><p>Reinforcement can increase a behavior. Punishment aims to decrease a behavior.</p>
                <div class="lt-label">REMEMBER</div><p>Focus on behavior and its consequences.</p>
              </div>
              <div class="lt-card">
                <div class="lt-head"><span class="lt-num">02</span><div><h4>Cognitivism</h4><div class="lt-theorist">Jean Piaget and cognitive-learning scholars</div></div></div>
                <p>Examines mental processes such as attention, memory, understanding, and problem-solving.</p>
                <div class="lt-simple"><strong>IN SIMPLE WORDS</strong><br>                Learning is not just about what a learner does. It is also about how the learner thinks, understands information, and remembers it.</div>
                <div class="lt-label">CLASSROOM EXAMPLE</div><div class="lt-example">A teacher uses a diagram to help learners connect new ideas and remember them.</div>
                <div class="lt-label">KEY IDEA</div><p>Learning involves mental processing, not only observable behavior.</p>
                <div class="lt-label">REMEMBER</div><p>Focus on thinking, memory, and understanding.</p>
              </div>
              <div class="lt-card">
                <div class="lt-head"><span class="lt-num">03</span><div><h4>Constructivism</h4><div class="lt-theorist">Jean Piaget · Lev Vygotsky</div></div></div>
                <p>Learners develop understanding by connecting new experiences with prior knowledge.</p>
                <div class="lt-simple"><strong>IN SIMPLE WORDS</strong><br>                Learners build knowledge by exploring, asking questions, and connecting new ideas to what they already know.</div>
                <div class="lt-label">CLASSROOM EXAMPLE</div><div class="lt-example">Learners investigate why some objects float and use observations to develop explanations.</div>
                <div class="lt-label">KEY IDEA</div><p>Learners actively build understanding through exploration and prior knowledge.</p>
                <div class="lt-label">REMEMBER</div><p>Focus on building meaning.</p>
              </div>
              <div class="lt-card">
                <div class="lt-head"><span class="lt-num">04</span><div><h4>Social Learning Theory</h4><div class="lt-theorist">Albert Bandura</div></div></div>
                <p>Explains how people can learn by observing others and modeling their behavior.</p>
                <div class="lt-simple"><strong>IN SIMPLE WORDS</strong><br>                People can learn by watching someone do something and then trying the same behavior themselves.</div>
                <div class="lt-label">CLASSROOM EXAMPLE</div><div class="lt-example">A learner observes a teacher demonstrate a respectful way to disagree and later uses that approach.</div>
                <div class="lt-label">KEY IDEA</div><p>Observation and modeling can support learning, but observing does not guarantee performing the behavior.</p>
                <div class="lt-label">REMEMBER</div><p>Focus on models and observation.</p>
              </div>
            </div>
            <div class="lt-kicker">02 · COMPARE AND REMEMBER</div>
            <div class="lt-memory">
              <div class="lt-row"><strong>Behaviorism</strong><span>Observable behavior and consequences</span></div>
              <div class="lt-row"><strong>Cognitivism</strong><span>Thinking, memory, and information processing</span></div>
              <div class="lt-row"><strong>Constructivism</strong><span>Actively building understanding</span></div>
              <div class="lt-row"><strong>Social learning</strong><span>Observing and modeling others</span></div>
            </div>
            <div class="lt-check">
              <h4>03 · How to answer a classroom situation</h4>
              <div class="lt-check-steps">
                <div><strong>STEP 1 · READ</strong><br>What is happening in the classroom?</div>
                <div><strong>STEP 2 · FIND THE CLUE</strong><br>Look for the action or learning process the situation emphasizes.</div>
                <div><strong>STEP 3 · MATCH</strong><br>Connect that clue to the theory that best explains it.</div>
                <div><strong>STEP 4 · EXPLAIN</strong><br>Use a detail from the situation to support your answer.</div>
              </div>
              <div class="lt-check-example">
                <strong>WORKED EXAMPLE</strong>
                <p><strong>Situation:</strong> A teacher praises a learner for finishing homework on time. The learner begins finishing homework regularly.</p>
                <p><strong>Clue:</strong> Praise encourages the learner to repeat a behavior.</p>
                <p><strong>Best match:</strong> Behaviorism.</p>
                <p><strong>Why?</strong> The situation focuses on how a consequence—praise—can influence behavior.</p>
              </div>
              <div class="lt-check-example">
                <strong>YOUR TURN · PRACTICE QUESTION</strong>
              </div>
            </div>
            """)

            st.markdown("""
            <style>
            /* Premium navy, cream, and muted gold poll theme */\n            /* Force white text on premium poll button */
            div[data-testid="stFormSubmitButton"] button,
            div[data-testid="stFormSubmitButton"] button p,
            div[data-testid="stFormSubmitButton"] button span {
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }
            div[data-testid="stFormSubmitButton"] button:hover,
            div[data-testid="stFormSubmitButton"] button:hover p,
            div[data-testid="stFormSubmitButton"] button:hover span {
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }

            div[data-testid="stFormSubmitButton"] button {
                background: #202C3D !important;
                color: #FFFFFF !important;
                border: 1px solid #202C3D !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                min-height: 48px !important;
                transition: background .18s ease, border-color .18s ease;
            }
            div[data-testid="stFormSubmitButton"] button:hover {
                background: #B28A3B !important;
                color: #202C3D !important;
                border-color: #B28A3B !important;
            }
            div[data-testid="stFormSubmitButton"] button:focus {
                box-shadow: 0 0 0 3px rgba(178, 138, 59, .25) !important;
            }
            .lt-poll-wrap { margin: 20px 0 12px; }
            .lt-poll-label {
                color: #79591D; font-size: 11px; font-weight: 800;
                letter-spacing: 1.5px; margin-bottom: 9px;
            }
            .lt-poll-question {
                color: #202C3D; font-size: 22px; font-weight: 750;
                line-height: 1.45; margin-bottom: 18px;
            }
            div[data-testid="stRadio"] > label { display: none; }
            div[data-testid="stRadio"] div[role="radiogroup"] {
                display: grid; grid-template-columns: repeat(2,minmax(0,1fr));
                gap: 12px;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] label {
                background: #FFFFFF; border: 1px solid #D8DEE7;
                border-radius: 14px; padding: 15px 17px;
                min-height: 64px; align-items: center;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
                background: #F7F0E1; border: 2px solid #B28A3B;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] label p {
                color: #202C3D; font-size: 15px; font-weight: 650;
            }
            @media(max-width:600px) {
                div[data-testid="stRadio"] div[role="radiogroup"] {
                    grid-template-columns: 1fr;
                }
                .lt-poll-question { font-size: 19px; }
            }
            </style>
            <div class="lt-poll-wrap">
              <div class="lt-poll-label">QUICK CHECK · 1 QUESTION</div>
              <div class="lt-poll-question">
                A learner watches the teacher demonstrate how to solve a problem,
                then copies the method. Which learning theory best explains this situation?
              </div>
            </div>
            """, unsafe_allow_html=True)

            answer_key = "lt_learning_theories_practice_answer"
            checked_key = "lt_learning_theories_practice_checked"
            retry_key = "lt_learning_theories_practice_retry"

            if retry_key not in st.session_state:
                st.session_state[retry_key] = 0

            options = [
                "A. Behaviorism",
                "B. Cognitivism",
                "C. Constructivism",
                "D. Social Learning Theory",
            ]

            with st.form(
                key=f"lt_theories_poll_form_{st.session_state[retry_key]}"
            ):
                selected_answer = st.radio(
                    "Choose one answer",
                    options,
                    key=f"{answer_key}_{st.session_state[retry_key]}",
                    index=None,
                    label_visibility="collapsed",
                )

                submitted = st.form_submit_button(
                    "Check answer",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if selected_answer is None:
                    st.warning("Select an answer before checking.")
                else:
                    st.session_state[checked_key] = selected_answer

            if checked_key in st.session_state:
                checked_answer = st.session_state[checked_key]

                if checked_answer == "D. Social Learning Theory":
                    st.success("Correct. You found the key clue.")
                    st.markdown(
                        "**Why this fits:** Social Learning Theory explains how "
                        "people can learn by observing others and modeling their actions."
                    )
                else:
                    st.warning("Not quite. Look again at what the learner does.")
                    st.markdown(
                        "**Hint:** The learner watches a demonstration and then copies "
                        "the method. Focus on learning by observing another person."
                    )
                    if st.button("Try again", key="lt_theories_try_again"):
                        st.session_state.pop(checked_key, None)
                        st.session_state[retry_key] += 1
                        st.rerun()

        else:
            st.markdown("### Study Notes")
            st.markdown(
                lesson.get("notes", "Study notes will appear here."),
                unsafe_allow_html=False,
            )
        st.markdown('<div class="preview-note"><strong>Study tip</strong><br>Identify the key concept, explain it in your own words, and connect it to an example.</div>', unsafe_allow_html=True)
        st.markdown("### How the full lesson can help")
        st.markdown("- Clear explanations of important terms\n- Worked examples or classroom scenarios\n- Practice with explanations\n- Review of missed questions and topics to revisit")
    st.markdown('</div>', unsafe_allow_html=True)

    with practice_tab:
        st.markdown("### A 15-question, 15-minute experience")
        st.write("Choose General Education or Professional Education. Each answer is checked before you continue. Questions below are illustrative practice items, not official LET questions.")
        quiz_subject = st.selectbox(
            "Practice subject",
            ["General Education", "Professional Education"],
            key="preview_quiz_subject",
        )
        quiz_items = PREVIEW_QUESTIONS[quiz_subject]
        prefix = "preview_exam_" + quiz_subject.replace(" ", "_")
        state_key = prefix + "_state"

        if st.button("Start / Restart 15-minute practice", type="primary", use_container_width=True,
                     key=prefix + "_start"):
            st.session_state[state_key] = {
                "started": True, "start_time": time.time(), "index": 0,
                "answers": {}, "checked": False, "finished": False,
            }

        state = st.session_state.get(state_key)
        if state and state.get("started"):
            @st.fragment(run_every="1s")
            def timed_preview():
                current_state = st.session_state.get(state_key)
                if not current_state or current_state.get("finished"):
                    return
                elapsed = int(time.time() - current_state["start_time"])
                remaining = max(0, 15 * 60 - elapsed)
                if remaining <= 0:
                    current_state["finished"] = True
                    st.session_state[state_key] = current_state
                    st.rerun()
                    return

                idx = current_state["index"]
                total = len(quiz_items)
                st.progress(min((idx + (1 if current_state.get("checked") else 0)) / total, 1.0))
                st.markdown(f"**Question {idx + 1} of {total}**")
                st.metric("Time remaining", f"{remaining // 60:02d}:{remaining % 60:02d}")
                q, options, answer_index, explanation = quiz_items[idx]
                st.markdown(f"### {q}")

                if not current_state.get("checked"):
                    choice = st.radio("Choose one answer", options, key=prefix + f"_choice_{idx}")
                    if st.button("Check answer", type="primary", key=prefix + f"_check_{idx}"):
                        current_state["answers"][idx] = options.index(choice)
                        current_state["checked"] = True
                        st.session_state[state_key] = current_state
                        st.rerun()
                else:
                    chosen_index = current_state["answers"][idx]
                    if chosen_index == answer_index:
                        st.success("Correct")
                    else:
                        st.error("Not quite — review the explanation.")
                    st.markdown("**Your answer**")
                    st.write(options[chosen_index])
                    st.markdown("**Correct answer**")
                    st.write(options[answer_index])
                    st.info(explanation)

                    if idx + 1 < total:
                        if st.button("Next question →", type="primary", key=prefix + f"_next_{idx}"):
                            current_state["index"] += 1
                            current_state["checked"] = False
                            st.session_state[state_key] = current_state
                            st.rerun()
                    else:
                        if st.button("Finish practice", type="primary", key=prefix + "_finish"):
                            current_state["finished"] = True
                            st.session_state[state_key] = current_state
                            st.rerun()

            timed_preview()

        state = st.session_state.get(state_key)
        if state and state.get("finished"):
            score = sum(
                1 for idx, selected in state["answers"].items()
                if selected == quiz_items[idx][2]
            )
            answered = len(state["answers"])
            st.markdown("### Practice results")
            st.metric("Score", f"{score} / {len(quiz_items)}")
            st.metric("Answered", f"{answered} / {len(quiz_items)}")
            st.progress(score / len(quiz_items))
            st.write("Use the explanations to identify topics you should revisit. This preview does not save results to your learner database.")

    st.markdown("""
    <div class="preview-cta">
      <h3>Ready to prepare with a plan?</h3>
      <p>Full access is planned to include more lessons, structured practice, explanations, and saved learning progress.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sign up for Full Access →", type="primary", use_container_width=True):
        st.info("Sign-up and login are not connected yet.")
    st.caption("Guest preview · Sample content only · Full account access is coming soon.")


elif page == "Dashboard":

    st.markdown("""
    <div class="hero orivan-hero">
        <div class="hero-eyebrow">ORIVAN · TEACHER LICENSURE PREPARATION</div>
        <div class="hero-title">
            Your journey to becoming<br>a teacher starts here.
        </div>
        <div class="hero-copy">
            Build your knowledge one topic at a time. Learn, practice,
            and understand your mistakes as you prepare for the LET.
        </div>
        <div class="hero-bottom-line">
            <span class="hero-dot"></span>
            STUDY WITH PURPOSE &nbsp; · &nbsp; STAY ON TRACK &nbsp; · &nbsp; GROW WITH CONFIDENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_lessons = sum(len(topics) for topics in lessons.values())
    total_answered = len(st.session_state.answers)
    total_completed = len(st.session_state.completed)

    m1, m2, m3 = st.columns(3)
    m1.metric("Available lessons", total_lessons)
    m2.metric("Questions answered", total_answered)
    m3.metric("Lessons completed", total_completed)

    st.markdown(
        '<div class="section-heading">Your learning areas</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Build your knowledge one subject at a time.</div>',
        unsafe_allow_html=True
    )

    subject_cards = [
        {
            "name": "General Education",
            "icon": "📐",
            "style": "icon-blue",
            "description": "Strengthen your general knowledge and problem-solving skills."
        },
        {
            "name": "Professional Education",
            "icon": "📘",
            "style": "icon-green",
            "description": "Review learning theories, assessment, and teaching principles."
        },
        {
            "name": "Major: Food and Service Management",
            "icon": "🍽️",
            "style": "icon-gold",
            "description": "Build your knowledge of food, service, and management topics."
        }
    ]

    columns = st.columns(3)

    for column, card in zip(columns, subject_cards):
        with column:
            st.markdown(f"""
            <div class="subject-card">
                <div class="subject-icon {card['style']}">
                    {card['icon']}
                </div>
                <div class="subject-title">{card['name']}</div>
                <div class="subject-copy">{card['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Choose your next step</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Study, test what you know, and check your progress.</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <div class="feature-title">Learn</div>
            <div class="feature-copy">
                Read your lesson notes and mark lessons as completed.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open lessons", key="dashboard_lessons",
                     use_container_width=True):
            st.session_state["navigation_choice"] = "Review Lessons"
            st.rerun()

    with b:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Practise</div>
            <div class="feature-copy">
                Answer questions, check explanations, and report your confidence.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start practice", key="dashboard_quiz",
                     use_container_width=True):
            st.session_state["navigation_choice"] = "Practice Quiz"
            st.rerun()

    with c:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Track progress</div>
            <div class="feature-copy">
                Review your answers and find topics that need more attention.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View progress", key="dashboard_progress",
                     use_container_width=True):
            st.session_state["navigation_choice"] = "My Progress"
            st.rerun()

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-panel">
        <div class="small-tag">PLANNED FEATURE</div>
        <div class="ai-title">Meet your future AI Study Coach</div>
        <div class="ai-copy">
            The long-term plan is to help you understand difficult lessons,
            identify recurring mistakes, revisit questions you guessed,
            and receive personalized practice across all three learning areas.
            AI features are not active in this version yet.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning(
        "Prototype notice: These are starter materials, not a complete "
        "or officially verified LET reviewer. Curriculum coverage and "
        "content accuracy still need to be checked."
    )


# --------------------------------------------------
# REVIEW LESSONS
# --------------------------------------------------
elif page == "Review Lessons":

    st.markdown(
        '<div class="section-heading">Review Lessons</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Choose a subject and topic to begin studying.</div>',
        unsafe_allow_html=True
    )

    subject = st.selectbox("Choose a subject", list(lessons.keys()))
    topic = st.selectbox("Choose a topic", list(lessons[subject].keys()))
    lesson = lessons[subject][topic]
    lesson_key = f"{subject}: {topic}"

    st.markdown(f"### 📘 {topic}")
    st.caption(subject)
    st.markdown("---")
    st.markdown("#### Study Notes")
    st.markdown(lesson["notes"], unsafe_allow_html=False)

    if lesson_key in st.session_state.completed:
        st.success("You have marked this lesson as completed.")

    if st.button("Mark lesson as completed"):
        mark_lesson_completed(
            st.session_state.learner_id, subject, topic
        )
        if lesson_key not in st.session_state.completed:
            st.session_state.completed.append(lesson_key)

        # Carry the studied lesson into Practice Quiz.
        st.session_state["quiz_subject"] = subject
        st.session_state["quiz_topic"] = topic
        st.session_state["open_quiz_after_lesson"] = True

        st.success("Lesson marked as completed!")
        st.rerun()



# --------------------------------------------------
# PRACTICE QUIZ — DATABASE CONNECTED
# --------------------------------------------------
elif page == "Practice Quiz":

    st.markdown(
        '<div class="section-heading">Practice Quiz</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Answer carefully. Your confidence matters, too.'
        '</div>',
        unsafe_allow_html=True
    )

    subject = st.selectbox(
        "Choose a subject",
        list(lessons.keys()),
        key="quiz_subject"
    )

    topic = st.selectbox(
        "Choose a topic",
        list(lessons[subject].keys()),
        key="quiz_topic"
    )

    question_data = lessons[subject][topic]
    question_key = f"{subject}::{topic}"

    # Register or update the question in the database.
    save_question(
        question_id=question_key,
        subject=subject,
        topic=topic,
        question_text=question_data["question"],
        correct_answer=question_data["answer"],
        explanation=question_data["explanation"]
    )

    # Premium ORIVAN practice screen
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(120deg,#101C30 0%,#1B2D46 100%);
            border:1px solid rgba(217,189,128,.48);
            border-radius:18px;
            padding:25px 26px;
            margin:8px 0 20px 0;
        ">
            <div style="
                color:#D9BD80;
                font-size:11px;
                font-weight:700;
                letter-spacing:2px;
                margin-bottom:10px;
            ">ORIVAN  /  LET REVIEW</div>
            <div style="
                color:#FFFFFF;
                font-size:27px;
                font-weight:700;
                line-height:1.25;
                margin-bottom:8px;
            ">Practice with purpose.</div>
            <div style="
                color:#D5DCE6;
                font-size:14px;
                line-height:1.6;
            ">Study the concept, answer the question, and track
            what needs more review.</div>
            <div style="
                display:inline-block;
                margin-top:17px;
                padding:6px 11px;
                border:1px solid rgba(217,189,128,.45);
                border-radius:20px;
                color:#F3DCA7;
                font-size:12px;
            ">{subject}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="margin:0 0 12px 2px;">
            <div style="
                color:#B08D51;
                font-size:11px;
                font-weight:700;
                letter-spacing:1.5px;
            ">YOUR CURRENT TOPIC</div>
            <div style="
                font-size:23px;
                font-weight:700;
                margin-top:4px;
            ">{topic}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 1: Study panel
    with st.container(border=True):
        st.markdown("##### 01  ·  STUDY THE CONCEPT")
        st.markdown("Review these notes before answering.")
        st.markdown("---")
        st.markdown(question_data["notes"])
        st.caption(
            "Study tip: identify the key idea and think of an example "
            "before moving to the question."
        )

    st.markdown("")

    # Step 2: Exam question panel
    with st.container(border=True):
        st.markdown("##### 02  ·  MOCK TEST")
        st.markdown(
            '<div style="color:#B08D51;font-size:11px;'
            'font-weight:700;letter-spacing:1.4px;'
            'margin-bottom:10px;">PRACTICE QUESTION</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-size:19px;font-weight:600;'
            f'line-height:1.65;margin-bottom:18px;">'
            f'{question_data["question"]}</div>',
            unsafe_allow_html=True
        )

        # ORIVAN_RECTANGULAR_ANSWER_CHOICES
        st.markdown(
            """
            <style>
            div[data-testid="stRadio"] div[role="radiogroup"] label {
                border: 1px solid #D8DEE8 !important;
                border-radius: 12px !important;
                padding: 14px 16px !important;
                margin: 0 0 10px 0 !important;
                background: #FFFFFF !important;
                width: 100% !important;
                box-sizing: border-box !important;
                transition: border-color 0.2s, background 0.2s;
            }

            div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
                border-color: #B08D51 !important;
                background: #FAF7F0 !important;
            }

            div[data-testid="stRadio"] div[role="radiogroup"]
            label:has(input:checked) {
                border: 2px solid #B08D51 !important;
                background: #F8F3E8 !important;
            }

            /* ORIVAN_CHECK_ANSWER_WHITE_TEXT */
            div[data-testid="stButton"] button {
                color: #FFFFFF !important;
            }

            
            /* ORIVAN_FORCE_PURE_WHITE_CHECK_ANSWER */
            div[data-testid="stButton"] button,
            div[data-testid="stButton"] button *,
            div[data-testid="stButton"] button p,
            div[data-testid="stButton"] button span {
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
                opacity: 1 !important;
            }
</style>
            """,
            unsafe_allow_html=True
        )

        choice = st.radio(
            "Choose the best answer",
            question_data["choices"],
            key=f"choice_{subject}_{topic}"
        )

        st.markdown("---")
        st.markdown("**How confident are you in your answer?**")
        st.caption(
            "Your confidence helps identify questions that may need "
            "more review—even when your answer is correct."
        )

        confidence = st.radio(
            "Confidence level",
            [
                "1 - Guessing",
                "2 - Somewhat sure",
                "3 - Very sure"
            ],
            horizontal=True,
            key=f"confidence_{subject}_{topic}",
            label_visibility="collapsed"
        )

    if st.button(
        "Check Answer",
        use_container_width=True,
        key=f"check_{subject}_{topic}"
    ):
        was_guessed = confidence.startswith("1")

        record_attempt(
            learner_id=st.session_state.learner_id,
            question_id=question_key,
            selected_answer=choice,
            was_guessed=was_guessed
        )

        is_correct = (
            str(choice).strip().casefold()
            == str(question_data["answer"]).strip().casefold()
        )

        # Keep feedback visible across Streamlit reruns.
        st.session_state.answers[question_key] = {
            "choice": choice,
            "correct": is_correct,
            "confidence": confidence,
            "was_guessed": was_guessed
        }

    # Display the saved feedback whenever this question is selected.
    saved_answer = st.session_state.answers.get(question_key)

    if saved_answer is not None:
        if saved_answer["correct"]:
            st.success("Correct! Well done.")
        else:
            st.error("Not quite. Review the explanation below.")

        st.markdown("**Your answer:**")
        st.write(saved_answer["choice"])

        st.markdown("**Correct answer:**")
        st.write(question_data["answer"])

        st.markdown("**Explanation:**")
        st.write(question_data["explanation"])

        if saved_answer.get("was_guessed", False):
            st.info(
                "You marked this as a guess. This question and topic "
                "should receive additional review, even if you answered "
                "correctly."
            )

    # Show saved review status for the selected topic.
    topic_records = [
        item
        for item in get_weak_topics(st.session_state.learner_id)
        if item["subject"] == subject and item["topic"] == topic
    ]

    if topic_records:
        progress = topic_records[0]

        st.markdown("---")
        st.markdown("#### Your saved topic progress")

        col1, col2, col3 = st.columns(3)
        col1.metric("Attempts", progress["total_attempts"])
        col2.metric("Mistakes", progress["total_mistakes"])
        col3.metric(
            "Correct streak",
            progress["consecutive_correct"]
        )

        if progress["next_review_at"]:
            st.caption(
                f"Next scheduled review: "
                f"{progress['next_review_at']}"
            )


    # END-OF-QUIZ REVIEW
    st.markdown("---")
    st.markdown("### End-of-Quiz Review")
    st.write(
        "Retry questions you answered incorrectly or correctly by guessing. "
        "Questions remain here until you answer correctly with confidence."
    )

    pending_reviews = []
    for saved_key, saved_data in st.session_state.answers.items():
        if not isinstance(saved_data, dict):
            continue
        if saved_data.get("correct") and not saved_data.get("was_guessed"):
            continue

        parts = saved_key.split("::", 1)
        if len(parts) != 2:
            continue

        saved_subject, saved_topic = parts
        saved_lesson = lessons.get(saved_subject, {}).get(saved_topic)
        if saved_lesson is not None:
            pending_reviews.append(
                (saved_key, saved_subject, saved_topic, saved_lesson)
            )

    if not pending_reviews:
        st.success(
            "No questions currently need another attempt. "
            "Keep practising to build your mastery."
        )
    else:
        st.write(f"Questions to retry: {len(pending_reviews)}")

        for review_key, review_subject, review_topic, review_lesson in pending_reviews:
            st.markdown(f"#### {review_topic}")
            st.caption(review_subject)
            st.write(review_lesson["question"])

            retry_choice = st.radio(
                "Choose your answer",
                review_lesson["choices"],
                key=f"end_review_choice_{review_key}",
            )

            retry_confidence = st.radio(
                "How confident are you?",
                ["1 - Guessing", "2 - Somewhat sure", "3 - Very sure"],
                horizontal=True,
                key=f"end_review_confidence_{review_key}",
            )

            if st.button(
                "Check Retry Answer",
                key=f"end_review_check_{review_key}",
                use_container_width=True,
            ):
                retry_guessed = retry_confidence.startswith("1")
                retry_correct = (
                    str(retry_choice).strip().casefold()
                    == str(review_lesson["answer"]).strip().casefold()
                )

                record_attempt(
                    learner_id=st.session_state.learner_id,
                    question_id=review_key,
                    selected_answer=retry_choice,
                    was_guessed=retry_guessed,
                )

                st.session_state.answers[review_key] = {
                    "choice": retry_choice,
                    "correct": retry_correct,
                    "confidence": retry_confidence,
                    "was_guessed": retry_guessed,
                }

                st.session_state.setdefault("end_review_results", {})[
                    review_key
                ] = {
                    "choice": retry_choice,
                    "correct": retry_correct,
                    "was_guessed": retry_guessed,
                }

            retry_result = st.session_state.get(
                "end_review_results", {}
            ).get(review_key)

            if retry_result is not None:
                if retry_result["correct"] and not retry_result["was_guessed"]:
                    st.success("Correct and confident. This question has left the immediate retry list.")
                elif retry_result["correct"]:
                    st.info("Correct, but you marked it as a guess. Try again with confidence.")
                else:
                    st.error("Not quite. This question will remain in the retry list.")

                st.write("**Correct answer:**", review_lesson["answer"])
                st.write("**Explanation:**", review_lesson["explanation"])


# Review Mistakes
elif page == "Review Mistakes":
    st.subheader("Review Mistakes")
    st.write(
        "Practise questions you answered incorrectly or guessed. "
        "Keep reviewing until you can answer confidently."
    )

    review_questions = get_questions_for_review(
        learner_id=st.session_state.learner_id,
        limit=20,
        due_only=False,
    )

    if not review_questions:
        st.success(
            "No questions need immediate review. "
            "Continue studying and practising new questions."
        )
    else:
        st.write(
            f"Questions available for review: {len(review_questions)}"
        )

        question_options = {
            f"{item['subject']} — {item['topic']}": item
            for item in review_questions
        }

        selected_label = st.selectbox(
            "Choose a question to review",
            list(question_options.keys()),
        )

        review_item = question_options[selected_label]
        review_id = review_item["question_id"]

        st.markdown(f"### {review_item['topic']}")
        st.write(review_item["question_text"])

        # Find the original lesson so we can reuse its answer choices.
        lesson_match = None

        for subject_name, topic_list in lessons.items():
            for topic_name, lesson_data in topic_list.items():
                if f"{subject_name}::{topic_name}" == review_id:
                    lesson_match = lesson_data
                    break
            if lesson_match:
                break

        if lesson_match is None:
            st.warning(
                "The original answer choices could not be found "
                "for this question."
            )
        else:
            review_choice = st.radio(
                "Choose your answer",
                lesson_match["choices"],
                key=f"review_choice_{review_id}",
            )

            review_confidence = st.radio(
                "How confident are you?",
                [
                    "1 - Guessing",
                    "2 - Somewhat sure",
                    "3 - Very sure",
                ],
                horizontal=True,
                key=f"review_confidence_{review_id}",
            )

            if st.button("Check Review Answer"):
                record_attempt(
                    learner_id=st.session_state.learner_id,
                    question_id=review_id,
                    selected_answer=review_choice,
                    was_guessed=review_confidence.startswith("1"),
                )

                if (
                    review_choice == lesson_match["answer"]
                    and not review_confidence.startswith("1")
                ):
                    st.success(
                        "Correct and confident! This question "
                        "has been answered correctly without guessing."
                    )
                elif review_choice == lesson_match["answer"]:
                    st.info(
                        "Your answer is correct, but you guessed. "
                        "Keep reviewing this question."
                    )
                else:
                    st.error("Not quite. Review the explanation below.")

                st.write(
                    "**Correct answer:**",
                    lesson_match["answer"],
                )
                st.write(
                    "**Explanation:**",
                    lesson_match["explanation"],
                )

                st.caption(
                    "Your attempt has been recorded. "
                    "The review list will update when the app refreshes."
                )

# --------------------------------------------------
# STUDY PLANNER
# --------------------------------------------------
elif page == "Study Planner":

    st.markdown(
        '<div class="section-heading">Your Study Planner</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Create a simple starting schedule that fits your day.</div>',
        unsafe_allow_html=True
    )

    exam_date = st.date_input(
        "Exam date, if known",
        value=None,
        min_value=date.today()
    )
    workday = st.checkbox("I work during the day")
    available_hours = st.slider(
        "Available study hours per day", 1, 6, 2
    )
    sleep_hours = st.slider(
        "Hours of sleep planned", 6, 10, 8
    )

    if st.button("Create my study plan", use_container_width=True):
        st.markdown("### Your suggested daily plan")

        if workday:
            first_session = available_hours // 2 + available_hours % 2
            second_session = available_hours // 2

            st.write("- After work: Rest for 30 minutes.")
            st.write(f"- Study session 1: {first_session} hour(s).")
            st.write("- Take a meal and rest break.")
            if second_session > 0:
                st.write(f"- Study session 2: {second_session} hour(s).")
        else:
            st.write(
                f"- Study for {available_hours} hour(s), "
                "divided into manageable sessions."
            )

        st.write(f"- Protect approximately {sleep_hours} hours for sleep.")
        st.write("- Include meals, personal responsibilities, and short breaks.")

        if exam_date:
            st.write(f"- Exam date entered: {exam_date}")

        st.caption(
            "This is a starter schedule. Later versions can account for "
            "your actual work hours, commute, and other responsibilities."
        )


# --------------------------------------------------
# MY PROGRESS
# --------------------------------------------------
elif page == "My Progress":
    st.markdown(
        '<div class="section-heading">My Progress</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Your saved practice results and topics that need more review.</div>',
        unsafe_allow_html=True
    )

    history = get_attempt_history(st.session_state.learner_id)
    weak_topics = get_weak_topics(st.session_state.learner_id)

    total = len(history)
    correct = sum(1 for item in history if item["is_correct"])
    accuracy = (correct / total * 100) if total else 0

    p1, p2, p3 = st.columns(3)
    p1.metric("Questions answered", total)
    p2.metric("Accuracy", f"{accuracy:.1f}%" if total else "—")
    p3.metric("Incorrect answers", total - correct)

    if total:
        st.markdown("#### Answer accuracy")
        st.progress(accuracy / 100)
        st.caption(
            f"{correct} correct answer(s) out of {total} saved attempts."
        )
    else:
        st.info(
            "Your saved practice results will appear here after you answer "
            "questions in Practice Quiz or Review Mistakes."
        )

    st.markdown("#### Topics to review")

    if weak_topics:
        for item in weak_topics:
            subject = item.get("subject", "Subject")
            topic = item.get("topic", "Topic")
            mistakes = item.get("total_mistakes", 0)
            attempts = item.get("total_attempts", 0)
            st.write(f"- **{subject} — {topic}**")
            st.caption(
                f"Mistakes: {mistakes} | Attempts: {attempts}"
            )
    else:
        st.success(
            "No topics are currently flagged in your saved topic records."
        )

    st.markdown("#### Recently answered questions")

    if history:
        for item in history[:10]:
            status = "Correct" if item["is_correct"] else "Needs review"
            st.write(
                f"- **{item.get('subject', 'Subject')} — "
                f"{item.get('topic', 'Topic')}**: {status}"
            )
            st.caption(
                f"Your answer: {item.get('selected_answer', 'Not recorded')} "
                f"| Date: {item.get('attempted_at', 'Not available')}"
            )

    st.caption(
        "Practice history and topic statistics are loaded from the saved "
        "database. Lesson completion is not yet stored permanently."
    )
