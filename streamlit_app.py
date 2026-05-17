import asyncio, sys, os, tempfile
import streamlit as st
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "backend"))

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_ROOT / "backend" / ".env")
except Exception:
    pass

st.set_page_config(
    page_title="CareerLens AI",
    layout="wide",
    page_icon="◈",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Mono:wght@300;400;500&family=Outfit:wght@200;300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080A0F !important;
    color: #E8E0D4 !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 50% -10%, rgba(183,147,89,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 80% 80%, rgba(120,80,180,0.07) 0%, transparent 60%),
        #080A0F !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #0A0C11 !important;
    border-right: 1px solid rgba(183,147,89,0.08) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── This is the key fix: give the main block real side padding ── */
.block-container {
    padding: 0 6rem 4rem 6rem !important;
    max-width: 1280px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D0F14; }
::-webkit-scrollbar-thumb { background: #B7935A; border-radius: 2px; }

/* ── Hero Section ── */
.hero-wrapper {
    position: relative;
    padding: 100px 80px 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.hero-wrapper::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        repeating-linear-gradient(
            0deg, transparent, transparent 79px,
            rgba(183,147,89,0.04) 80px
        ),
        repeating-linear-gradient(
            90deg, transparent, transparent 79px,
            rgba(183,147,89,0.04) 80px
        );
    pointer-events: none;
}

.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.4em;
    color: #B7935A;
    text-transform: uppercase;
    margin-bottom: 28px;
    opacity: 0.9;
}

.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(52px, 7vw, 96px);
    font-weight: 300;
    line-height: 0.95;
    color: #F0E8DC;
    text-align: center;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.hero-title em {
    font-style: italic;
    color: #B7935A;
}

.hero-subtitle {
    font-family: 'Outfit', sans-serif;
    font-weight: 200;
    font-size: 16px;
    color: rgba(232,224,212,0.55);
    text-align: center;
    letter-spacing: 0.08em;
    margin-top: 24px;
    margin-bottom: 56px;
    max-width: 480px;
}

/* ── Upload Zone ── */
.upload-zone-wrapper {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
}

[data-testid="stFileUploader"] {
    background: rgba(183,147,89,0.04) !important;
    border: 1px solid rgba(183,147,89,0.25) !important;
    border-radius: 2px !important;
    padding: 40px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(183,147,89,0.6) !important;
    background: rgba(183,147,89,0.07) !important;
}

[data-testid="stFileUploader"] label {
    color: rgba(232,224,212,0.7) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.1em !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    color: rgba(232,224,212,0.5) !important;
    font-size: 13px !important;
}

/* ── Country Select ── */
[data-testid="stSelectbox"] > div {
    background: rgba(13,15,20,0.8) !important;
    border: 1px solid rgba(183,147,89,0.3) !important;
    border-radius: 2px !important;
    color: #E8E0D4 !important;
}

[data-testid="stSelectbox"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.3em !important;
    color: rgba(183,147,89,0.8) !important;
    text-transform: uppercase !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid rgba(183,147,89,0.6) !important;
    color: #B7935A !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.35em !important;
    text-transform: uppercase !important;
    padding: 14px 48px !important;
    border-radius: 1px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

[data-testid="stButton"] button:hover {
    background: rgba(183,147,89,0.12) !important;
    border-color: #B7935A !important;
    color: #D4AF72 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(183,147,89,0.15) !important;
}

/* ── Spinners / Progress ── */
[data-testid="stSpinner"] {
    color: #B7935A !important;
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #B7935A, #D4AF72) !important;
    border-radius: 0 !important;
}

[data-testid="stProgress"] > div {
    background: rgba(183,147,89,0.12) !important;
    border-radius: 0 !important;
    height: 3px !important;
}

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(183,147,89,0.15) !important;
    margin: 64px 0 !important;
}

/* ── Metric Cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: rgba(183,147,89,0.12);
    border: 1px solid rgba(183,147,89,0.12);
    margin-bottom: 56px;
}

.metric-card {
    background: #0D0F14;
    padding: 44px 48px;
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(183,147,89,0.4), transparent);
}

.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.35em;
    color: rgba(183,147,89,0.7);
    text-transform: uppercase;
    margin-bottom: 12px;
}

.metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 42px;
    font-weight: 300;
    color: #F0E8DC;
    line-height: 1;
}

.metric-unit {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #B7935A;
    margin-left: 4px;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: baseline;
    gap: 20px;
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(183,147,89,0.15);
}

.section-number {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: rgba(183,147,89,0.5);
    letter-spacing: 0.1em;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    font-weight: 300;
    color: #F0E8DC;
    letter-spacing: -0.01em;
}

/* ── Skill Tags ── */
.skill-tag {
    display: inline-block;
    background: rgba(183,147,89,0.08);
    border: 1px solid rgba(183,147,89,0.2);
    color: rgba(232,224,212,0.85);
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.05em;
    padding: 7px 16px;
    margin: 4px;
    transition: all 0.2s ease;
}

.skill-tag:hover {
    background: rgba(183,147,89,0.15);
    border-color: rgba(183,147,89,0.5);
    color: #D4AF72;
}

.skill-tag-highlight {
    background: rgba(183,147,89,0.18);
    border-color: rgba(183,147,89,0.5);
    color: #D4AF72;
}

/* ── Role Cards ── */
.role-card {
    background: linear-gradient(135deg, rgba(183,147,89,0.06) 0%, rgba(13,15,20,0.9) 100%);
    border: 1px solid rgba(183,147,89,0.2);
    border-left: 3px solid #B7935A;
    padding: 22px 28px;
    margin-bottom: 10px;
    font-family: 'Outfit', sans-serif;
    font-weight: 300;
    font-size: 15px;
    color: #E8E0D4;
    letter-spacing: 0.03em;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.role-card::before {
    content: '◈';
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(183,147,89,0.3);
    font-size: 14px;
}

/* ── Job Cards ── */
.job-card {
    background: rgba(13,15,20,0.9);
    border: 1px solid rgba(183,147,89,0.12);
    padding: 40px 44px;
    margin-bottom: 16px;
    position: relative;
    transition: all 0.3s ease;
}

.job-card:hover {
    border-color: rgba(183,147,89,0.35);
    background: rgba(183,147,89,0.03);
}

.job-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.job-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 22px;
    font-weight: 400;
    color: #F0E8DC;
    line-height: 1.2;
    margin-bottom: 4px;
}

.job-company {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #B7935A;
    letter-spacing: 0.1em;
}

.job-location {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(232,224,212,0.4);
    letter-spacing: 0.08em;
    margin-top: 2px;
}

.match-badge {
    background: rgba(183,147,89,0.12);
    border: 1px solid rgba(183,147,89,0.35);
    color: #D4AF72;
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    white-space: nowrap;
    letter-spacing: 0.05em;
}

.skill-match {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 4px 10px;
    margin: 2px;
    display: inline-block;
}

.skill-match-good {
    background: rgba(80,180,120,0.1);
    border: 1px solid rgba(80,180,120,0.3);
    color: rgba(80,220,140,0.9);
}

.skill-match-missing {
    background: rgba(220,80,80,0.08);
    border: 1px solid rgba(220,80,80,0.25);
    color: rgba(240,100,100,0.9);
}

/* ── Market Heatmap ── */
.heatmap-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 1px solid rgba(183,147,89,0.07);
}

.heatmap-rank {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(183,147,89,0.4);
    width: 24px;
    flex-shrink: 0;
}

.heatmap-skill {
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    color: rgba(232,224,212,0.85);
    flex: 1;
}

.heatmap-bar-wrapper {
    width: 120px;
    height: 3px;
    background: rgba(183,147,89,0.1);
    flex-shrink: 0;
}

.heatmap-bar {
    height: 100%;
    background: linear-gradient(90deg, #B7935A, #D4AF72);
}

.heatmap-count {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #B7935A;
    width: 28px;
    text-align: right;
    flex-shrink: 0;
}

/* ── Missing Skills ── */
.missing-skill-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border: 1px solid rgba(220,80,80,0.15);
    background: rgba(220,80,80,0.04);
    margin-bottom: 6px;
}

.missing-skill-name {
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    color: rgba(232,224,212,0.85);
}

.missing-skill-freq {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(220,100,100,0.8);
    letter-spacing: 0.08em;
}

/* ── Apply Button ── */
.apply-link {
    display: inline-block;
    background: transparent;
    border: 1px solid rgba(183,147,89,0.4);
    color: #B7935A;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    padding: 10px 28px;
    text-decoration: none;
    transition: all 0.2s ease;
    margin-top: 20px;
}

.apply-link:hover {
    background: rgba(183,147,89,0.1);
    border-color: #B7935A;
    color: #D4AF72;
}

/* ── Discovered Roles ── */
.discovered-role {
    background: rgba(120,80,180,0.06);
    border: 1px solid rgba(120,80,180,0.2);
    border-left: 2px solid rgba(150,100,200,0.6);
    padding: 14px 20px;
    margin-bottom: 6px;
    font-family: 'Outfit', sans-serif;
    font-size: 14px;
    color: rgba(232,224,212,0.85);
    letter-spacing: 0.03em;
}

/* ── ROI Items ── */
.roi-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border: 1px solid rgba(80,160,200,0.15);
    background: rgba(80,160,200,0.04);
    margin-bottom: 6px;
}

.roi-skill { font-family: 'Outfit', sans-serif; font-size: 14px; color: rgba(232,224,212,0.85); }
.roi-uplift { font-family: 'DM Mono', monospace; font-size: 13px; color: rgba(100,180,220,0.9); }

/* ── Score Bar ── */
.score-wrapper {
    margin: 24px 0;
}

.score-track {
    height: 4px;
    background: rgba(183,147,89,0.12);
    position: relative;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    background: linear-gradient(90deg, #8B6914, #B7935A, #D4AF72);
    transition: width 1s ease;
}

.score-label {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: rgba(183,147,89,0.7);
    letter-spacing: 0.1em;
}

/* ── Alert & Success ── */
[data-testid="stAlert"] {
    background: rgba(183,147,89,0.06) !important;
    border: 1px solid rgba(183,147,89,0.25) !important;
    border-radius: 0 !important;
    color: rgba(232,224,212,0.8) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Main content wrapper ── */
.main-content {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 80px 100px;
}

/* ── Tabs-like section nav ── */
.nav-pill {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: rgba(183,147,89,0.6);
    padding: 6px 0;
    margin-right: 32px;
    border-bottom: 1px solid transparent;
}

.nav-pill.active {
    color: #B7935A;
    border-bottom-color: #B7935A;
}

/* ── Columns gap fix ── */
[data-testid="stHorizontalBlock"] { gap: 40px !important; }

/* ── Misc ── */
p, li { font-family: 'Outfit', sans-serif !important; font-weight: 300 !important; }
h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; font-weight: 300 !important; }

[data-testid="stMarkdownContainer"] p {
    color: rgba(232,224,212,0.75) !important;
    line-height: 1.7 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    display: block !important;
    background: #080A0F !important;
    border-right: 1px solid rgba(183,147,89,0.08) !important;
    min-width: 210px !important;
    max-width: 210px !important;
}
[data-testid="stSidebar"] > div {
            padding: 6px 0 !important; }
[data-testid="stSidebar"] .block-container { padding: 0 !important; max-width: 100% !important; }
/* Hide the ugly radio widget entirely */
[data-testid="stSidebar"] [data-testid="stRadio"] { display: none !important; }
/* Nav link buttons */
.nav-item {
    display: block;
    width: 100%;
    padding: 13px 28px;
    font-family: "DM Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(183,147,89,0.45);
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
    text-decoration: none;
}
.nav-item:hover {
    color: rgba(183,147,89,0.85);
    background: rgba(183,147,89,0.04);
    border-left-color: rgba(183,147,89,0.3);
}
.nav-item.active {
    color: #D4AF72;
    background: rgba(183,147,89,0.07);
    border-left-color: #B7935A;
}
.nav-icon { margin-right: 12px; font-size: 12px; opacity: 0.7; }
.nav-section-label {
    font-family: "DM Mono", monospace;
    font-size: 8px;
    letter-spacing: 0.35em;
    color: rgba(183,147,89,0.2);
    text-transform: uppercase;
    padding: 20px 28px 8px;
}
.sidebar-logo {
    padding: 22px 18px 16px;
    border-bottom: 1px solid rgba(183,147,89,0.08);
    margin-bottom: 8px;
}
.sidebar-footer {
    padding: 20px 28px;
    border-top: 1px solid rgba(183,147,89,0.06);
    margin-top: auto;
}
.sidebar-footer-label {
    font-family: "DM Mono", monospace;
    font-size: 8px;
    letter-spacing: 0.3em;
    color: rgba(183,147,89,0.2);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.sidebar-footer-text {
    font-family: "Outfit", sans-serif;
    font-size: 11px;
    color: rgba(232,224,212,0.2);
    line-height: 1.8;
}
.provider-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 14px;
    padding: 5px 12px;
    border: 1px solid rgba(80,200,80,0.15);
    background: rgba(80,200,80,0.05);
    font-family: "DM Mono", monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    color: rgba(100,220,100,0.7);
    text-transform: uppercase;
}
.provider-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: rgba(100,220,100,0.8);
    animation: pdot 2.5s ease-in-out infinite;
}
@keyframes pdot { 0%,100%{opacity:1;} 50%{opacity:0.2;} }
/* ===== TABS ===== */
[data-testid="stTabs"] [role="tablist"] { background: transparent !important; border-bottom: 1px solid rgba(183,147,89,0.12) !important; }
[data-testid="stTabs"] [role="tab"] { font-family: "DM Mono", monospace !important; font-size: 10px !important; letter-spacing: 0.25em !important; text-transform: uppercase !important; color: rgba(183,147,89,0.5) !important; padding: 12px 20px !important; border-radius: 0 !important; border: none !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #D4AF72 !important; border-bottom: 2px solid #B7935A !important; background: rgba(183,147,89,0.04) !important; }
/* ===== INPUTS ===== */
[data-testid="stTextArea"] textarea { background: rgba(13,15,20,0.9) !important; border: 1px solid rgba(183,147,89,0.2) !important; color: rgba(232,224,212,0.85) !important; border-radius: 0 !important; }
[data-testid="stTextInput"] input { background: rgba(13,15,20,0.9) !important; border: 1px solid rgba(183,147,89,0.2) !important; color: rgba(232,224,212,0.85) !important; border-radius: 0 !important; }
[data-testid="stRadio"] label { font-family: "DM Mono", monospace !important; font-size: 11px !important; color: rgba(232,224,212,0.7) !important; }
/* ===== SCORE CIRCLE ===== */
.score-circle-wrapper { display:flex; flex-direction:column; align-items:center; padding:40px; background:rgba(13,15,20,0.9); border:1px solid rgba(183,147,89,0.15); margin-bottom:24px; }
.score-big { font-family:"Cormorant Garamond",serif; font-size:80px; font-weight:300; line-height:1; }
.score-lbl { font-family:"DM Mono",monospace; font-size:10px; letter-spacing:0.3em; color:rgba(183,147,89,0.6); text-transform:uppercase; margin-top:8px; }
/* ===== DIMENSION BAR ===== */
.dim-row { display:flex; align-items:center; gap:16px; padding:14px 20px; border-bottom:1px solid rgba(183,147,89,0.06); }
.dim-lbl { font-family:"DM Mono",monospace; font-size:10px; letter-spacing:0.1em; color:rgba(232,224,212,0.55); text-transform:uppercase; width:140px; flex-shrink:0; }
.dim-track { flex:1; height:3px; background:rgba(183,147,89,0.1); }
.dim-fill  { height:100%; }
.dim-score { font-family:"DM Mono",monospace; font-size:12px; color:#D4AF72; width:36px; text-align:right; }
.dim-fb { font-family:"Outfit",sans-serif; font-size:12px; color:rgba(232,224,212,0.45); font-style:italic; padding:4px 20px 12px; }
/* ===== INTERVIEW Q ===== */
.iq { background:rgba(13,15,20,0.9); border:1px solid rgba(183,147,89,0.1); border-left:3px solid rgba(183,147,89,0.4); padding:24px 28px; margin-bottom:12px; }
.iq.hard { border-left-color:rgba(220,80,80,0.6); }
.iq.medium { border-left-color:rgba(212,175,114,0.6); }
.iq.easy { border-left-color:rgba(80,180,120,0.6); }
.iq-q { font-family:"Outfit",sans-serif; font-size:15px; color:#F0E8DC; margin-bottom:12px; }
.iq-a { font-family:"Outfit",sans-serif; font-size:13px; color:rgba(232,224,212,0.55); line-height:1.7; border-top:1px solid rgba(183,147,89,0.08); padding-top:12px; white-space:pre-wrap; }
.iq-badge { display:inline-block; font-family:"DM Mono",monospace; font-size:9px; letter-spacing:0.2em; text-transform:uppercase; padding:3px 10px; margin-bottom:10px; }
.b-hard   { background:rgba(220,80,80,0.08);  color:rgba(240,100,100,0.9); border:1px solid rgba(220,80,80,0.2); }
.b-medium { background:rgba(212,175,114,0.08);color:rgba(212,175,114,0.9); border:1px solid rgba(212,175,114,0.2); }
.b-easy   { background:rgba(80,180,120,0.08); color:rgba(80,220,140,0.9);  border:1px solid rgba(80,180,120,0.2); }
/* ===== SALARY ===== */
.sal-card { text-align:center; padding:28px 20px; background:rgba(13,15,20,0.9); border:1px solid rgba(183,147,89,0.1); }
.sal-val  { font-family:"Cormorant Garamond",serif; font-size:36px; font-weight:300; color:#D4AF72; }
.sal-lbl  { font-family:"DM Mono",monospace; font-size:9px; letter-spacing:0.3em; color:rgba(183,147,89,0.5); text-transform:uppercase; margin-top:6px; }
/* ===== CAREER PATH ===== */
.path-step { display:flex; gap:24px; padding:28px 0; border-bottom:1px solid rgba(183,147,89,0.08); }
.path-num  { width:44px; height:44px; border:1px solid rgba(183,147,89,0.3); display:flex; align-items:center; justify-content:center; font-family:"DM Mono",monospace; font-size:14px; color:#B7935A; flex-shrink:0; }
.path-title { font-family:"Cormorant Garamond",serif; font-size:22px; font-weight:300; color:#F0E8DC; margin-bottom:4px; }
.path-time  { font-family:"DM Mono",monospace; font-size:10px; letter-spacing:0.2em; color:rgba(183,147,89,0.6); text-transform:uppercase; margin-bottom:8px; }
.path-desc  { font-family:"Outfit",sans-serif; font-size:14px; color:rgba(232,224,212,0.55); margin-bottom:12px; }
/* ===== ROADMAP PILLS ===== */
.rpill { display:inline-block; padding:5px 13px; margin:3px; font-family:"DM Mono",monospace; font-size:11px; }
.r-now   { background:rgba(220,80,80,0.08);  border:1px solid rgba(220,80,80,0.2);  color:rgba(240,120,120,0.9); }
.r-short { background:rgba(212,175,114,0.08);border:1px solid rgba(212,175,114,0.2);color:rgba(212,175,114,0.9); }
.r-long  { background:rgba(80,160,200,0.08); border:1px solid rgba(80,160,200,0.2); color:rgba(100,180,220,0.9); }
/* ===== BULLET REWRITER ===== */
.bcompare { display:grid; grid-template-columns:1fr 1fr; gap:1px; background:rgba(183,147,89,0.08); margin-bottom:6px; }
.b-before { background:#080A0F; padding:18px 22px; font-family:"Outfit",sans-serif; font-size:13px; color:rgba(232,224,212,0.4); line-height:1.6; text-decoration:line-through; text-decoration-color:rgba(220,80,80,0.3); }
.b-after  { background:#080A0F; padding:18px 22px; font-family:"Outfit",sans-serif; font-size:13px; color:rgba(232,224,212,0.88); line-height:1.6; }
.b-why    { background:rgba(80,180,120,0.04); border:1px solid rgba(80,180,120,0.12); padding:7px 14px; font-family:"DM Mono",monospace; font-size:10px; color:rgba(80,220,140,0.7); margin-bottom:16px; }
/* ===== FIT VERDICT ===== */
.fit-verdict { font-family:"Cormorant Garamond",serif; font-size:26px; font-weight:300; padding:18px 24px; border:1px solid rgba(183,147,89,0.2); text-align:center; margin-bottom:20px; }
/* ===== STRENGTH / WEAKNESS ===== */
.s-item { display:flex; gap:12px; padding:11px 0; border-bottom:1px solid rgba(80,180,120,0.07); font-family:"Outfit",sans-serif; font-size:14px; color:rgba(232,224,212,0.8); }
.s-item::before { content:"\2713"; color:rgba(80,220,140,0.8); flex-shrink:0; }
.w-item { display:flex; gap:12px; padding:11px 0; border-bottom:1px solid rgba(220,80,80,0.07); font-family:"Outfit",sans-serif; font-size:14px; color:rgba(232,224,212,0.8); }
.w-item::before { content:"\25B3"; color:rgba(240,120,120,0.8); flex-shrink:0; }
/* ===== COVER LETTER ===== */
.cl-box { background:rgba(13,15,20,0.95); border:1px solid rgba(183,147,89,0.2); border-left:3px solid #B7935A; padding:40px 48px; font-family:"Outfit",sans-serif; font-size:15px; line-height:1.9; color:rgba(232,224,212,0.85); white-space:pre-wrap; }
/* ===== FEATURE CARDS ===== */
.feat-card { background:rgba(13,15,20,0.9); border:1px solid rgba(183,147,89,0.12); padding:24px 28px; margin-bottom:12px; }
.feat-title { font-family:"Cormorant Garamond",serif; font-size:18px; color:#F0E8DC; margin-bottom:8px; }
.feat-desc  { font-family:"Outfit",sans-serif; font-size:13px; color:rgba(232,224,212,0.45); }

/* ===== PROVIDER BADGE ===== */
.provider-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px;
    background: rgba(80,160,80,0.08);
    border: 1px solid rgba(80,200,80,0.2);
    font-family: "DM Mono", monospace;
    font-size: 10px; letter-spacing: 0.15em;
    color: rgba(100,220,100,0.85);
    text-transform: uppercase;
}
.provider-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(100,220,100,0.9); display: inline-block; animation: pulse-dot 2s ease-in-out infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* ── Sidebar nav buttons override ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    border-radius: 0 !important;

    color: rgba(183,147,89,0.55) !important;

    font-family: "DM Mono", monospace !important;
    font-size: 9px !important;        /* smaller */
    letter-spacing: 0.08em !important; /* MUCH tighter */

    text-transform: uppercase !important;
    text-align: left !important;

    padding: 7px 16px !important;     /* tighter spacing */

    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    color: rgba(212,175,114,0.9) !important;
    background: rgba(183,147,89,0.05) !important;
    border-left-color: rgba(183,147,89,0.35) !important;
}
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:active {
    color: #D4AF72 !important;
    background: rgba(183,147,89,0.08) !important;
    border-left-color: #B7935A !important;
    box-shadow: none !important;
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Backend ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_modules():
    try:
        from resume_processing.parser      import extract_text_from_pdf
        from resume_processing.skills      import extract_skills_from_text
        from resume_processing.experience  import detect_experience
        from role_inference.role_predictor import predict_roles
        from job_fetching.adzuna_client    import fetch_jobs_async, build_search_queries
        from analysis.skill_gap            import analyze_skill_gap
        from market_intelligence.intelligence_engine import generate_career_summary
        from matching.matcher              import rank_jobs_by_similarity
        from ai_features.llm_engine import (
            score_resume, generate_cover_letter, generate_interview_prep,
            rewrite_resume_bullets, extract_salary_intelligence,
            generate_career_path, analyse_job_fit, _used_provider,
        )
        return dict(
            extract_text=extract_text_from_pdf,
            extract_skills=extract_skills_from_text,
            detect_exp=detect_experience,
            predict_roles=predict_roles,
            fetch_jobs=fetch_jobs_async,
            build_queries=build_search_queries,
            skill_gap=analyze_skill_gap,
            career_summary=generate_career_summary,
            rank_jobs=rank_jobs_by_similarity,
            score_resume=score_resume,
            cover_letter=generate_cover_letter,
            interview_prep=generate_interview_prep,
            rewrite_bullets=rewrite_resume_bullets,
            salary_intel=extract_salary_intelligence,
            career_path=generate_career_path,
            job_fit=analyse_job_fit,
            active_provider=_used_provider,
        )
    except Exception as e:
        return {"error": str(e)}


async def _fetch_all_jobs(queries, country, fetch_fn, pages=4, per_page=20):
    tasks = [fetch_fn(q, country=country, pages=pages, results_per_page=per_page) for q in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    jobs = []
    for r in results:
        if isinstance(r, list):
            jobs.extend(r)
    seen, unique = set(), []
    for j in jobs:
        k = j.get("title","").lower() + "|" + str(j.get("company",{}).get("display_name","")).lower()
        if k not in seen:
            seen.add(k)
            unique.append(j)
    return unique


# ── UI helpers ────────────────────────────────────────────────────────────────
def _fmt(val, cur="USD"):
    if not isinstance(val, (int, float)): return "N/A"
    syms = {"INR": "₹", "GBP": "£", "EUR": "€"}
    s = syms.get(cur, "$")
    return f"{s}{val:,.0f}"

def sec(num, title):
    st.markdown(
        f'<div class="section-header"><span class="section-number">{num}</span>' +
        f'<span class="section-title">{title}</span></div>',
        unsafe_allow_html=True,
    )

def skill_tags(skills, cls="skill-tag"):
    html = "".join(f'<span class="{cls}">{s}</span>' for s in skills)
    st.markdown(f'<div style="line-height:2.4">{html}</div>', unsafe_allow_html=True)

def score_bar(score, label="Market Alignment Score"):
    pct = round(min(max(score, 0), 1) * 100)
    col = "#50C896" if pct >= 60 else "#D4AF72" if pct >= 35 else "#DC5050"
    st.markdown(
        f'<div class="score-wrapper">' +
        f'<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;' +
        f'color:rgba(183,147,89,.7);text-transform:uppercase;margin-bottom:10px;">{label}</div>' +
        f'<div class="score-track"><div class="score-fill" style="width:{pct}%;background:{col};"></div></div>' +
        f'<div class="score-label"><span>0%</span>' +
        f'<span style="color:{col};font-size:18px;font-weight:600;">{pct}%</span><span>100%</span></div></div>',
        unsafe_allow_html=True,
    )

def heatmap(items):
    if not items:
        return
    mx = max(c for _, c in items) or 1
    rows = ""
    for i, (sk, cnt) in enumerate(items, 1):
        w = round(cnt / mx * 100)
        rows += (
            f'<div class="heatmap-item">' +
            f'<span class="heatmap-rank">#{i:02d}</span>' +
            f'<span class="heatmap-skill">{sk}</span>' +
            f'<div class="heatmap-bar-wrapper"><div class="heatmap-bar" style="width:{w}%"></div></div>' +
            f'<span class="heatmap-count">{cnt}</span></div>'
        )
    st.markdown(rows, unsafe_allow_html=True)

def job_card(job, gap, mods, text, skills):
    title = job.get("title","N/A")
    co    = job.get("company",{}).get("display_name","N/A")
    loc   = job.get("location",{}).get("display_name","N/A")
    url   = job.get("redirect_url","#")
    sc    = job.get("match_score", 0)
    desc  = job.get("description","")
    bc    = "#50C896" if sc >= 60 else "#D4AF72" if sc >= 35 else "#aaa"

    mh = "".join(f'<span class="skill-match skill-match-good">{s}</span>' for s in (gap.get("strong_match") or [])[:6]) or '<span style="color:rgba(232,224,212,.3);font-size:11px;">—</span>'
    gh = "".join(f'<span class="skill-match skill-match-missing">{s}</span>' for s in (gap.get("missing") or [])[:6]) or '<span style="color:rgba(232,224,212,.3);font-size:11px;">None</span>'

    st.markdown(
        f'<div class="job-card">' +
        f'<div class="job-card-header">' +
        f'<div><div class="job-title">{title}</div><div class="job-company">{co.upper()}</div><div class="job-location">◎ {loc}</div></div>' +
        f'<div class="match-badge" style="color:{bc};border-color:{bc}40;">{sc:.0f}<span style="font-size:10px;opacity:.6">%</span></div>' +
        f'</div>' +
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:16px">' +
        f'<div><div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.3em;color:rgba(80,220,140,.7);text-transform:uppercase;margin-bottom:8px;">Matching Skills</div>{mh}</div>' +
        f'<div><div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.3em;color:rgba(240,100,100,.7);text-transform:uppercase;margin-bottom:8px;">Skill Gaps</div>{gh}</div>' +
        f'</div><a class="apply-link" href="{url}" target="_blank">Apply Now →</a></div>',
        unsafe_allow_html=True,
    )

    bk = f"fit_{hash(title+co)}"
    if st.button("◈ AI Fit Analysis", key=bk):
        with st.spinner("Analysing with Groq AI…"):
            fit = mods["job_fit"](text, title, desc, skills)
        if "error" not in fit:
            fs  = fit.get("fit_score", 0)
            fc  = "#50C896" if fs >= 70 else "#D4AF72" if fs >= 45 else "#DC5050"
            st.markdown(f'<div class="fit-verdict" style="color:{fc};">{fit.get("verdict","—")}  ·  {fs}% Fit</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(80,220,140,.6);text-transform:uppercase;margin-bottom:8px;">Why You Fit</div>', unsafe_allow_html=True)
                for w in fit.get("why_you_fit", []):
                    st.markdown(f'<div class="s-item">{w}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(240,100,100,.6);text-transform:uppercase;margin-bottom:8px;">Challenges</div>', unsafe_allow_html=True)
                for w in fit.get("why_you_might_struggle", []):
                    st.markdown(f'<div class="w-item">{w}</div>', unsafe_allow_html=True)
            if fit.get("standout_angle"):
                st.markdown(
                    f'<div style="background:rgba(183,147,89,.06);border:1px solid rgba(183,147,89,.2);padding:16px 20px;margin-top:12px;font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.8);font-style:italic;">◈ {fit["standout_angle"]}</div>',
                    unsafe_allow_html=True,
                )
            tone = st.radio("Cover letter tone", ["professional","conversational","bold"], horizontal=True, key=f"tone_{bk}")
            if st.button("◈ Generate Cover Letter", key=f"cl_{bk}"):
                with st.spinner("Writing with Groq AI…"):
                    letter = mods["cover_letter"](text, skills, title, co, desc, tone)
                st.markdown(f'<div class="cl-box">{letter}</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇ Download Cover Letter", letter,
                    file_name=f"cover_letter_{co.lower().replace(' ','_')}.txt",
                    mime="text/plain", key=f"dl_{bk}",
                )


# ── Load modules ──────────────────────────────────────────────────────────────
mods = load_modules()

# ── Sidebar ───────────────────────────────────────────────────────────────────
_PAGES = [
    ("Dashboard",       "\u25c8"),
    ("Resume Scorer",   "\u25a4"),
    ("Job Market",      "\u2299"),
    ("Salary Intel",    "\u25ce"),
    ("Career Path",     "\u2192"),
    ("Resume Rewriter", "\u2726"),
    ("Interview Coach", "\u25f7"),
]
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"

with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">' +
        '<div style="font-family:Cormorant Garamond,serif;font-size:22px;font-weight:300;' +
        'color:#F0E8DC;">Career<em style="color:#B7935A;font-style:italic;">Lens</em></div>' +
        '<div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:.45em;' +
        'color:rgba(183,147,89,.3);text-transform:uppercase;margin-top:6px;">AI Career Intelligence</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-section-label">Navigation</div>', unsafe_allow_html=True)
    for label, icon in _PAGES:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state["page"] = label
            st.rerun()
    try:
        prov = mods.get("active_provider", lambda: "Groq — Llama 3.3-70B")()
    except Exception:
        prov = "Groq — Llama 3.3-70B"
    model_name = prov.split("\u2014")[-1].strip() if "\u2014" in prov else prov.split("—")[-1].strip()
    st.markdown(
        '<div class="sidebar-footer">' +
        '<div class="sidebar-footer-label">Powered by</div>' +
        '<div class="sidebar-footer-text">Groq LPU \u00b7 Llama 3.3-70B<br>Sentence Transformers<br>Adzuna Jobs API</div>' +
        f'<div class="provider-pill"><span class="provider-dot"></span>{model_name}</div>' +
        '</div>',
        unsafe_allow_html=True,
    )

page = st.session_state["page"]


# ── Hero ──────────────────────────────────────────────────────────────────────
if page == "Dashboard":
    st.markdown(
        '<div class="hero-wrapper">' +
        '<div class="hero-eyebrow">◈ AI-Powered Career Intelligence</div>' +
        '<div class="hero-title">Discover Your<br><em>Next Role</em></div>' +
        '<div class="hero-subtitle">Upload your résumé. Groq AI scores it, finds live jobs, reveals skill gaps, and builds your personalised career roadmap.</div></div>',
        unsafe_allow_html=True,
    )


# ── Upload ────────────────────────────────────────────────────────────────────
cu, _ = st.columns([3, 2])
with cu:
    uploaded_file = st.file_uploader("RÉSUMÉ — PDF FORMAT", type=["pdf"], label_visibility="visible")

if not uploaded_file:
    st.markdown(
        '<div style="text-align:center;padding:60px;font-family:DM Mono,monospace;font-size:11px;letter-spacing:.2em;color:rgba(183,147,89,.3);text-transform:uppercase;">Upload a résumé to begin</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ── Parse ─────────────────────────────────────────────────────────────────────
if "error" in mods:
    st.error(f"Backend error: {mods['error']}")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    tmp.write(uploaded_file.read())
    resume_path = tmp.name

cache_key = f"parsed_{uploaded_file.name}_{uploaded_file.size}"
if cache_key not in st.session_state:
    with st.spinner("◈  Parsing résumé…"):
        try:
            result              = mods["extract_text"](resume_path)
            text                = result["text"]
            skills              = mods["extract_skills"](text)
            exp_years, exp_lvl  = mods["detect_exp"](text)
            roles               = mods["predict_roles"](text, skills, level=exp_lvl)
        except Exception as e:
            st.error(f"Parse error: {e}")
            st.stop()
    st.session_state[cache_key] = dict(text=text, skills=skills, exp_years=exp_years, exp_lvl=exp_lvl, roles=roles)
    st.session_state["jobs"]    = []
    st.session_state["report"]  = {}
    st.session_state["country"] = "in"

p        = st.session_state[cache_key]
text     = p["text"]
skills   = p["skills"]
exp_years= p["exp_years"]
exp_lvl  = p["exp_lvl"]
roles    = p["roles"]


# ════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown(
        f'<div class="metric-row">' +
        f'<div class="metric-card"><div class="metric-label">Skills Detected</div><div class="metric-value">{len(skills)}<span class="metric-unit">+</span></div></div>' +
        f'<div class="metric-card"><div class="metric-label">Predicted Roles</div><div class="metric-value">{len(roles)}</div></div>' +
        f'<div class="metric-card"><div class="metric-label">Experience Level</div><div class="metric-value" style="font-size:26px;padding-top:6px;">{exp_lvl}</div>' +
        f'<div style="font-family:DM Mono,monospace;font-size:11px;color:rgba(183,147,89,.5);margin-top:4px;">{exp_years}y detected</div></div></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        sec("01", "Extracted Skills")
        skill_tags(skills)
    with c2:
        sec("02", "Career Trajectory")
        for r in roles:
            st.markdown(f'<div class="role-card">{r.title()}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;color:rgba(183,147,89,.6);text-transform:uppercase;margin-bottom:24px;">AI Features Available</div>', unsafe_allow_html=True)

    feats = [
        ("📄","Resume Scorer","Groq grades your resume across 5 dimensions with specific actionable fixes"),
        ("🎯","Job Market","Live jobs with semantic matching + Groq AI fit analysis per job"),
        ("💰","Salary Intel","Groq estimates your market value + negotiation strategy"),
        ("🗺","Career Path","Personalised 3-step progression roadmap to senior level"),
        ("✍","Resume Rewriter","Groq rewrites your weakest bullets with impact metrics"),
        ("🎤","Interview Coach","Role-specific mock questions with model answers"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(feats):
        with cols[i % 3]:
            st.markdown(
                f'<div class="feat-card"><div style="font-size:24px;margin-bottom:12px;">{icon}</div>' +
                f'<div class="feat-title">{title}</div><div class="feat-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════
# RESUME SCORER
# ════════════════════════════════════════════════════════
elif page == "Resume Scorer":
    sec("AI", "Resume Intelligence Score")
    st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.5);margin-bottom:32px;">Groq AI grades your résumé across 5 professional dimensions and identifies specific improvements.</div>', unsafe_allow_html=True)

    skey = f"score_{cache_key}"
    if skey not in st.session_state:
        if st.button("◈  Score My Résumé with Groq AI"):
            with st.spinner("Groq is analysing your résumé…"):
                res = mods["score_resume"](text, skills, exp_lvl)
            st.session_state[skey] = res

    if skey in st.session_state:
        s = st.session_state[skey]
        if "error" in s:
            st.error(f"AI error: {s['error']}")
        else:
            overall = s.get("overall_score", 0)
            oc      = "#50C896" if overall >= 70 else "#D4AF72" if overall >= 50 else "#DC5050"
            cl, cr  = st.columns([1, 2])
            with cl:
                st.markdown(
                    f'<div class="score-circle-wrapper">' +
                    f'<div class="score-big" style="color:{oc};">{overall}</div>' +
                    f'<div class="score-lbl">Resume Score</div>' +
                    f'<div style="font-family:DM Mono,monospace;font-size:10px;color:rgba(232,224,212,.3);margin-top:16px;">/ 100</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.3em;color:rgba(80,220,140,.6);text-transform:uppercase;margin-bottom:12px;margin-top:20px;">Top Strengths</div>', unsafe_allow_html=True)
                for st_ in s.get("top_strengths", []):
                    st.markdown(f'<div class="s-item">{st_}</div>', unsafe_allow_html=True)
            with cr:
                dims = s.get("dimensions", {})
                for k, lbl in [("impact","Impact"),("clarity","Clarity"),("ats_compatibility","ATS Compat."),("skills_presentation","Skills Pres."),("structure","Structure")]:
                    d  = dims.get(k, {})
                    sc = d.get("score", 0)
                    fb = d.get("feedback","")
                    bc = "#50C896" if sc >= 7 else "#D4AF72" if sc >= 5 else "#DC5050"
                    st.markdown(
                        f'<div class="dim-row"><span class="dim-lbl">{lbl}</span>' +
                        f'<div class="dim-track"><div class="dim-fill" style="width:{sc*10}%;background:{bc};"></div></div>' +
                        f'<span class="dim-score">{sc}/10</span></div>' +
                        f'<div class="dim-fb">{fb}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("<hr>", unsafe_allow_html=True)
            cf, ca = st.columns(2)
            with cf:
                sec("!", "Critical Fixes")
                for fix in s.get("critical_fixes", []):
                    st.markdown(f'<div class="w-item">{fix}</div>', unsafe_allow_html=True)
                if s.get("missing_sections"):
                    st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(212,175,114,.6);text-transform:uppercase;margin-top:20px;margin-bottom:8px;">Missing Sections</div>', unsafe_allow_html=True)
                    for ms in s["missing_sections"]:
                        st.markdown(f'<div class="w-item">{ms}</div>', unsafe_allow_html=True)
            with ca:
                sec("ATS", "Missing Keywords")
                st.markdown('<div style="font-family:Outfit,sans-serif;font-size:13px;color:rgba(232,224,212,.4);margin-bottom:16px;">Add these to pass ATS filters:</div>', unsafe_allow_html=True)
                for kw in s.get("ats_keywords_missing", []):
                    st.markdown(f'<div class="missing-skill-item"><span class="missing-skill-name">{kw}</span></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# JOB MARKET
# ════════════════════════════════════════════════════════
elif page == "Job Market":
    sec("03", "Live Job Market")
    cc, cb, _ = st.columns([2, 2, 3])
    with cc:
        country = st.selectbox(
            "TARGET MARKET",
            ["in","us","gb","ca","au","de","sg"],
            format_func=lambda x: {
                "in":"🇮🇳 India","us":"🇺🇸 United States",
                "gb":"🇬🇧 United Kingdom","ca":"🇨🇦 Canada",
                "au":"🇦🇺 Australia","de":"🇩🇪 Germany",
                "sg":"🇸🇬 Singapore",
            }[x],
        )
    with cb:
        st.markdown("<br>", unsafe_allow_html=True)
        run_jobs = st.button("◈  Fetch Live Jobs")

    if run_jobs:
        with st.spinner("◈  Fetching live jobs…"):
            queries = mods["build_queries"](roles, skills, level=exp_lvl, max_queries=7)
            jobs    = asyncio.run(_fetch_all_jobs(queries, country, mods["fetch_jobs"]))
            if jobs:
                jobs = mods["rank_jobs"](text, jobs)
            report  = asyncio.run(mods["career_summary"](text, skills, roles, jobs))
        st.session_state["jobs"]    = jobs
        st.session_state["report"]  = report
        st.session_state["country"] = country

    jobs   = st.session_state.get("jobs", [])
    report = st.session_state.get("report", {})

    if jobs:
        score_bar(float(report.get("market_strength_score", 0)))
        st.markdown("<br>", unsafe_allow_html=True)
        ch, cm = st.columns(2)
        with ch:
            st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;color:rgba(183,147,89,.7);text-transform:uppercase;margin-bottom:20px;">Top Market Skills</div>', unsafe_allow_html=True)
            heatmap(report.get("top_market_skills", []))
        with cm:
            st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;color:rgba(220,80,80,.7);text-transform:uppercase;margin-bottom:20px;">High-Impact Skill Gaps</div>', unsafe_allow_html=True)
            for item in report.get("missing_high_impact_skills", []):
                st.markdown(f'<div class="missing-skill-item"><span class="missing-skill-name">{item["skill"]}</span><span class="missing-skill-freq">demand ×{item["market_frequency"]}</span></div>', unsafe_allow_html=True)
        roi = report.get("roi_simulation", [])
        if roi:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;color:rgba(80,160,200,.7);text-transform:uppercase;margin-bottom:16px;">Skill ROI Simulation</div>', unsafe_allow_html=True)
            for item in roi:
                sgn = "+" if item["improvement_percent"] >= 0 else ""
                st.markdown(f'<div class="roi-item"><span class="roi-skill">+ {item["skill"]}</span><span class="roi-uplift">↑ {sgn}{item["improvement_percent"]:.1f}% ranking uplift</span></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        sec("06", f"Top Opportunities  ·  {len(jobs)} Found")
        for job in jobs[:25]:
            gap = mods["skill_gap"](text, job.get("description",""))
            job_card(job, gap, mods, text, skills)
    elif not run_jobs:
        st.markdown('<div style="padding:40px;text-align:center;font-family:DM Mono,monospace;font-size:11px;letter-spacing:.2em;color:rgba(183,147,89,.3);text-transform:uppercase;">Select a market and click Fetch Live Jobs</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# SALARY INTEL
# ════════════════════════════════════════════════════════
elif page == "Salary Intel":
    sec("AI", "Salary Intelligence")
    st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.5);margin-bottom:32px;">Groq analyses market data and compensation benchmarks to estimate your precise market value.</div>', unsafe_allow_html=True)
    jobs = st.session_state.get("jobs", [])
    cr2, cc2, _ = st.columns([2, 2, 3])
    with cr2:
        tgt_role = st.selectbox("Role", options=roles or ["Software Engineer"])
    with cc2:
        tgt_country = st.selectbox("Market", ["in","us","gb","ca","au","de","sg"],
            format_func=lambda x: {"in":"🇮🇳 India","us":"🇺🇸 US","gb":"🇬🇧 UK","ca":"🇨🇦 Canada","au":"🇦🇺 Australia","de":"🇩🇪 Germany","sg":"🇸🇬 Singapore"}[x])
    salk = f"sal_{tgt_role}_{tgt_country}"
    if salk not in st.session_state:
        if st.button("◈  Estimate My Market Value"):
            with st.spinner("Groq is calculating compensation intelligence…"):
                sal = mods["salary_intel"](jobs, tgt_role, tgt_country)
            st.session_state[salk] = sal
    if salk in st.session_state:
        sal = st.session_state[salk]
        if "error" in sal:
            st.error(sal["error"])
        else:
            cur = sal.get("estimated_range", {}).get("currency", "USD")
            est = sal.get("estimated_range", {})
            pct = sal.get("percentiles", {})
            ca2, cb2, cc3 = st.columns(3)
            with ca2:
                st.markdown(f'<div class="sal-card"><div class="sal-val">{_fmt(est.get("min"), cur)}</div><div class="sal-lbl">Floor</div></div>', unsafe_allow_html=True)
            with cb2:
                st.markdown(f'<div class="sal-card" style="border-color:rgba(183,147,89,.35);"><div class="sal-val" style="font-size:48px;">{_fmt(sal.get("median"), cur)}</div><div class="sal-lbl">Median</div></div>', unsafe_allow_html=True)
            with cc3:
                st.markdown(f'<div class="sal-card"><div class="sal-val">{_fmt(est.get("max"), cur)}</div><div class="sal-lbl">Ceiling</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            sec("~", "Percentile Distribution")
            for lbl, pk, pw in [("25th percentile","p25",25),("50th","p50",50),("75th","p75",75),("90th","p90",90)]:
                st.markdown(
                    f'<div class="dim-row"><span class="dim-lbl">{lbl}</span>' +
                    f'<div class="dim-track"><div class="dim-fill" style="width:{pw}%;background:linear-gradient(90deg,#8B6914,#D4AF72);"></div></div>' +
                    f'<span class="dim-score" style="width:120px;">{_fmt(pct.get(pk,0), cur)}</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<hr>", unsafe_allow_html=True)
            cf2, ct2 = st.columns(2)
            with cf2:
                sec("↑", "Factors That Raise Salary")
                for f in sal.get("factors", []):
                    st.markdown(f'<div class="s-item">{f}</div>', unsafe_allow_html=True)
            with ct2:
                sec("◈", "Negotiation Tips")
                for tip in sal.get("negotiation_tips", []):
                    st.markdown(f'<div class="s-item">{tip}</div>', unsafe_allow_html=True)
            if sal.get("market_context"):
                st.markdown(f'<div style="background:rgba(183,147,89,.05);border:1px solid rgba(183,147,89,.15);padding:20px 24px;margin-top:24px;font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.65);line-height:1.7;">{sal["market_context"]}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# CAREER PATH
# ════════════════════════════════════════════════════════
elif page == "Career Path":
    sec("AI", "Career Progression Roadmap")
    st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.5);margin-bottom:32px;">Groq builds a personalised 3-step progression plan based on your current skills and experience level.</div>', unsafe_allow_html=True)
    tc = st.session_state.get("country", "in")
    pk = f"path_{exp_lvl}_{roles[0] if roles else 'x'}"
    if pk not in st.session_state:
        if st.button("◈  Generate My Career Roadmap"):
            with st.spinner("Groq is mapping your trajectory…"):
                path = mods["career_path"](roles, skills, exp_lvl, tc)
            st.session_state[pk] = path
    if pk in st.session_state:
        path = st.session_state[pk]
        if "error" in path:
            st.error(path["error"])
        else:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:20px;margin-bottom:32px;padding:20px 28px;background:rgba(183,147,89,.06);border:1px solid rgba(183,147,89,.2);">' +
                f'<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:.3em;color:rgba(183,147,89,.6);text-transform:uppercase;">Current Level</div>' +
                f'<div style="font-family:Cormorant Garamond,serif;font-size:22px;color:#F0E8DC;">{path.get("current_level", exp_lvl)} · {", ".join(roles[:2])}</div></div>',
                unsafe_allow_html=True,
            )
            sec("→", "Progression Steps")
            for step in path.get("progression", []):
                sh = "".join(f'<span class="skill-tag">{s}</span>' for s in step.get("skills_to_add",[])[:6])
                ch = "".join(f'<span class="rpill r-short">{c}</span>' for c in step.get("certifications",[])[:3])
                st.markdown(
                    f'<div class="path-step">' +
                    f'<div class="path-num">{step.get("step","")}</div>' +
                    f'<div style="flex:1"><div class="path-time">{step.get("timeline","")}</div>' +
                    f'<div class="path-title">{step.get("title","")}</div>' +
                    f'<div class="path-desc">{step.get("description","")}</div>' +
                    f'<div style="margin-bottom:8px;">{sh}</div>{f"<div>{ch}</div>" if ch else ""}</div>' +
                    f'<div style="text-align:right;flex-shrink:0;"><div style="font-family:Cormorant Garamond,serif;font-size:20px;color:#D4AF72;">${step.get("avg_salary_usd",0):,}</div>' +
                    f'<div style="font-family:DM Mono,monospace;font-size:9px;color:rgba(183,147,89,.5);">avg USD/yr</div></div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<hr>", unsafe_allow_html=True)
            sec("◈", "Skills Roadmap")
            road = path.get("skills_roadmap", {})
            ri, rs, rl = st.columns(3)
            with ri:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(220,80,80,.6);text-transform:uppercase;margin-bottom:12px;">Learn Now</div>', unsafe_allow_html=True)
                for sk in road.get("immediate",[]):
                    st.markdown(f'<div><span class="rpill r-now">{sk}</span></div>', unsafe_allow_html=True)
            with rs:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(212,175,114,.6);text-transform:uppercase;margin-bottom:12px;">3–6 Months</div>', unsafe_allow_html=True)
                for sk in road.get("short_term",[]):
                    st.markdown(f'<div><span class="rpill r-short">{sk}</span></div>', unsafe_allow_html=True)
            with rl:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(80,160,200,.6);text-transform:uppercase;margin-bottom:12px;">1–2 Years</div>', unsafe_allow_html=True)
                for sk in road.get("long_term",[]):
                    st.markdown(f'<div><span class="rpill r-long">{sk}</span></div>', unsafe_allow_html=True)
            if path.get("advice"):
                st.markdown(f'<div style="background:rgba(183,147,89,.05);border:1px solid rgba(183,147,89,.15);border-left:3px solid #B7935A;padding:24px 28px;margin-top:32px;font-family:Outfit,sans-serif;font-size:15px;color:rgba(232,224,212,.75);line-height:1.8;font-style:italic;">◈ {path["advice"]}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# RESUME REWRITER
# ════════════════════════════════════════════════════════
elif page == "Resume Rewriter":
    sec("AI", "Resume Bullet Rewriter")
    st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.5);margin-bottom:32px;">Groq identifies your 5 weakest bullet points and rewrites them with powerful action verbs and quantifiable impact.</div>', unsafe_allow_html=True)
    tgt_rw = st.selectbox("Optimise for role", options=roles + ["General Tech"])
    rwk = f"rw_{tgt_rw}_{cache_key}"
    if rwk not in st.session_state:
        if st.button("◈  Rewrite My Bullets"):
            with st.spinner("Groq is rewriting your résumé bullets…"):
                rw = mods["rewrite_bullets"](text, tgt_rw)
            st.session_state[rwk] = rw
    if rwk in st.session_state:
        rw = st.session_state[rwk]
        if "error" in rw:
            st.error(rw["error"])
        else:
            rewrites = rw.get("rewrites", [])
            if not rewrites:
                st.warning("No bullet points extracted. Ensure your résumé has bullet points.")
            for i, item in enumerate(rewrites, 1):
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(183,147,89,.5);text-transform:uppercase;margin-bottom:8px;margin-top:20px;">Bullet {i}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="bcompare">' +
                    f'<div class="b-before"><div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:.2em;color:rgba(220,80,80,.5);text-transform:uppercase;margin-bottom:8px;">Original</div>{item.get("original","")}</div>' +
                    f'<div class="b-after"><div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:.2em;color:rgba(80,220,140,.5);text-transform:uppercase;margin-bottom:8px;">Rewritten</div>{item.get("rewritten","")}</div></div>' +
                    f'<div class="b-why">◈ {item.get("improvement","")}</div>',
                    unsafe_allow_html=True,
                )
            if rw.get("general_advice"):
                st.markdown(f'<div style="background:rgba(183,147,89,.05);border:1px solid rgba(183,147,89,.15);padding:20px 24px;margin-top:24px;font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.65);line-height:1.7;">{rw["general_advice"]}</div>', unsafe_allow_html=True)
            improved = text
            for item in rewrites:
                if item.get("original") and item.get("rewritten"):
                    improved = improved.replace(item["original"], item["rewritten"], 1)
            st.download_button("⬇ Download Improved Resume Text", improved, file_name="resume_improved.txt", mime="text/plain")


# ════════════════════════════════════════════════════════
# INTERVIEW COACH
# ════════════════════════════════════════════════════════
elif page == "Interview Coach":
    sec("AI", "Interview Preparation Coach")
    st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.5);margin-bottom:32px;">Groq generates role-specific technical and behavioural questions with model answers tailored to your background.</div>', unsafe_allow_html=True)
    ir, ij = st.columns([1, 2])
    with ir:
        int_role = st.selectbox("Prepare for role", options=roles + ["Custom"])
    with ij:
        jd_txt = st.text_area("Paste job description (optional — improves question targeting)", height=100, placeholder="Paste JD here…")
    ik = f"int_{int_role}_{cache_key}"
    if ik not in st.session_state:
        if st.button("◈  Generate Interview Prep"):
            with st.spinner("Groq is building your coaching session…"):
                prep = mods["interview_prep"](int_role, skills, exp_lvl, jd_txt)
            st.session_state[ik] = prep
    if ik in st.session_state:
        prep = st.session_state[ik]
        if "error" in prep:
            st.error(prep["error"])
        else:
            t1, t2, t3, t4 = st.tabs(["Technical Questions","Behavioural Questions","Ask the Interviewer","Tips & Red Flags"])
            with t1:
                for q in prep.get("technical_questions", []):
                    diff = q.get("difficulty","medium")
                    st.markdown(
                        f'<div class="iq {diff}"><span class="iq-badge b-{diff}">{diff}</span>' +
                        f'<div class="iq-q">Q: {q.get("question","")}</div>' +
                        f'<div class="iq-a">▸ {q.get("model_answer","")}</div></div>',
                        unsafe_allow_html=True,
                    )
            with t2:
                for q in prep.get("behavioral_questions", []):
                    st.markdown(
                        f'<div class="iq medium"><span class="iq-badge b-medium">STAR Method</span>' +
                        f'<div class="iq-q">Q: {q.get("question","")}</div>' +
                        f'<div class="iq-a">▸ {q.get("model_answer","")}</div></div>',
                        unsafe_allow_html=True,
                    )
            with t3:
                st.markdown('<div style="font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.55);margin-bottom:20px;">Smart questions signal strategic thinking to interviewers:</div>', unsafe_allow_html=True)
                for q in prep.get("questions_to_ask_interviewer", []):
                    st.markdown(f'<div style="padding:16px 20px;border:1px solid rgba(183,147,89,.12);margin-bottom:8px;font-family:Outfit,sans-serif;font-size:14px;color:rgba(232,224,212,.8);">◈ {q}</div>', unsafe_allow_html=True)
            with t4:
                tp, rf = st.columns(2)
                with tp:
                    st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(80,220,140,.6);text-transform:uppercase;margin-bottom:12px;">Preparation Tips</div>', unsafe_allow_html=True)
                    for tip in prep.get("preparation_tips", []):
                        st.markdown(f'<div class="s-item">{tip}</div>', unsafe_allow_html=True)
                with rf:
                    st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:.2em;color:rgba(240,100,100,.6);text-transform:uppercase;margin-bottom:12px;">Red Flags to Avoid</div>', unsafe_allow_html=True)
                    for r in prep.get("red_flags_to_avoid", []):
                        st.markdown(f'<div class="w-item">{r}</div>', unsafe_allow_html=True)
            exp_txt = f"INTERVIEW PREP — {int_role}\n" + "="*50 + "\n\n"
            for q in prep.get("technical_questions", []):
                exp_txt += f"[{q.get('difficulty','').upper()}] {q.get('question','')}\n→ {q.get('model_answer','')}\n\n"
            for q in prep.get("behavioral_questions", []):
                exp_txt += f"[BEHAVIORAL] {q.get('question','')}\n→ {q.get('model_answer','')}\n\n"
            st.download_button("⬇ Export Interview Prep", exp_txt, file_name=f"interview_{int_role.lower().replace(' ','_')}.txt", mime="text/plain")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="border-top:1px solid rgba(183,147,89,.1);padding:32px 40px;margin-top:80px;' +
    'display:flex;justify-content:space-between;align-items:center;">' +
    '<span style="font-family:Cormorant Garamond,serif;font-size:18px;font-weight:300;color:rgba(183,147,89,.6);">CareerLens <em>AI</em></span>' +
    '<span style="font-family:DM Mono,monospace;font-size:10px;color:rgba(232,224,212,.2);letter-spacing:.2em;">Groq · SENTENCE TRANSFORMERS · ADZUNA · ESCO</span></div>',
    unsafe_allow_html=True,
)