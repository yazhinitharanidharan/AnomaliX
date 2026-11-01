"""Design system and shared presentation helpers for AnomaliX."""

from __future__ import annotations

import html
import textwrap

import streamlit as st

PALETTE = {
    "taupe": "#A09B85",
    "blush": "#F3E0D9",
    "charcoal": "#242321",
    "offwhite": "#FAF8F5",
    "grey": "#77746D",
    "border": "#DED9D0",
    "surface": "#FFFDFA",
    "surface_alt": "#F4F0E8",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --ax-taupe: #A09B85;
    --ax-blush: #F3E0D9;
    --ax-charcoal: #242321;
    --ax-offwhite: #FAF8F5;
    --ax-grey: #77746D;
    --ax-border: #DED9D0;
    --ax-surface: #FFFDFA;
    --ax-surface-alt: #F4F0E8;
    --ax-sidebar-line: rgba(250, 248, 245, 0.12);
}

html, body, [class*="css"] {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background: var(--ax-offwhite);
    color: var(--ax-charcoal);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    display: none;
}

#MainMenu, footer, [data-testid="stDecoration"] {
    visibility: hidden;
}

[data-testid="stAppViewBlockContainer"] {
    max-width: 1240px;
    padding: 2.4rem 3rem 4.5rem;
}

[data-testid="stSidebar"] {
    background: var(--ax-charcoal);
    border-right: 1px solid #37352f;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.4rem 1.05rem 1.5rem;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #DDD7CA;
}

.ax-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.72rem;
    padding: 0.4rem 0.35rem 1.15rem;
    border-bottom: 1px solid var(--ax-sidebar-line);
    margin-bottom: 1.15rem;
}

.ax-brand-mark {
    flex: 0 0 auto;
    width: 40px;
    height: 40px;
}

.ax-wordmark {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.42rem;
    font-weight: 500;
    letter-spacing: -0.035em;
    line-height: 1;
    color: #FAF8F5;
}

.ax-wordmark span {
    color: var(--ax-blush);
}

.ax-brand-tagline {
    color: #9E998C;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 0.38rem;
    line-height: 1.35;
}

.ax-nav-label {
    color: #8E897C;
    font-size: 0.61rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    padding: 0.2rem 0.75rem 0.55rem;
}

/* Sidebar navigation: hide radio marks, use full-width editorial nav rows. */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0.18rem;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%;
    padding: 0.64rem 0.78rem;
    border: 1px solid transparent;
    border-radius: 9px;
    transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    display: none;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    color: #CFC9BB;
    font-size: 0.855rem;
    font-weight: 500;
    line-height: 1.3;
    margin: 0;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(160, 155, 133, 0.16);
    border-color: rgba(160, 155, 133, 0.2);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: var(--ax-blush);
    border-color: var(--ax-blush);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: var(--ax-charcoal);
    font-weight: 700;
}

.ax-sidebar-status {
    margin-top: 1.4rem;
    padding: 0.95rem 1rem;
    border: 1px solid var(--ax-sidebar-line);
    border-radius: 11px;
    background: rgba(250, 248, 245, 0.035);
}

.ax-sidebar-status-title {
    color: #8E897C;
    font-size: 0.61rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
}

.ax-sidebar-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
    font-size: 0.77rem;
    color: #CFC9BB;
    padding: 0.18rem 0;
}

.ax-sidebar-status-row strong {
    color: #FAF8F5;
    font-weight: 600;
    font-size: 0.74rem;
    text-align: right;
}

.ax-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 0.45rem;
    background: #8E897C;
    vertical-align: 1px;
}

.ax-dot.is-ready {
    background: #B7BE9E;
    box-shadow: 0 0 0 3px rgba(183, 190, 158, 0.14);
}

.ax-dot.is-waiting {
    background: #C9A98F;
}

.ax-dot.is-missing {
    background: #B98C80;
}

.ax-version {
    color: #777267;
    font-size: 0.64rem;
    letter-spacing: 0.08em;
    margin-top: 1rem;
    padding-left: 0.75rem;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    color: #DDD7CA;
    border: 1px solid #4A473F;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.5rem 0.8rem;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--ax-taupe);
    color: #FAF8F5;
    background: rgba(160, 155, 133, 0.12);
}

/* Typography */
h1, h2, h3, h4 {
    font-family: 'Fraunces', Georgia, serif !important;
    color: var(--ax-charcoal);
    letter-spacing: -0.025em;
    font-weight: 500 !important;
}

h1 { font-size: clamp(2.15rem, 4vw, 3.5rem) !important; line-height: 1.04 !important; }
h2 { font-size: clamp(1.5rem, 2.5vw, 2.1rem) !important; line-height: 1.15 !important; }
h3 { font-size: 1.28rem !important; }

p, li, label, .stMarkdown {
    color: #393732;
    line-height: 1.62;
}

[data-testid="stCaptionContainer"] p,
.ax-muted {
    color: var(--ax-grey) !important;
}

.ax-eyebrow {
    color: var(--ax-grey);
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.ax-eyebrow.on-dark {
    color: #A9A396;
}

.ax-section-head {
    margin: 0 0 1.15rem;
}

.ax-section-head h2 {
    margin: 0;
}

.ax-section-head p {
    color: var(--ax-grey);
    max-width: 680px;
    margin: 0.5rem 0 0;
    font-size: 0.94rem;
}

/* Hero */
.ax-hero {
    position: relative;
    padding: clamp(1.8rem, 4vw, 3.4rem);
    border: 1px solid var(--ax-border);
    border-radius: 20px;
    background:
        radial-gradient(circle at 82% 18%, rgba(243, 224, 217, 0.92) 0, rgba(243, 224, 217, 0) 38%),
        linear-gradient(135deg, #FFFDFA 0%, #F7F2EA 100%);
    overflow: hidden;
    margin-bottom: 1.4rem;
}

.ax-hero::after {
    content: "";
    position: absolute;
    right: -68px;
    bottom: -110px;
    width: 290px;
    height: 290px;
    border: 1px solid rgba(160, 155, 133, 0.28);
    border-radius: 50%;
    pointer-events: none;
}

.ax-hero-grid {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1.45fr) minmax(260px, 0.75fr);
    gap: 2.2rem;
    align-items: end;
}

.ax-hero-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(2.25rem, 4.6vw, 4rem);
    line-height: 1.02;
    letter-spacing: -0.045em;
    color: var(--ax-charcoal);
    margin: 0;
    max-width: 760px;
}

.ax-hero-title em {
    color: #827D6C;
    font-style: italic;
    font-weight: 400;
}

.ax-hero-copy {
    color: #5F5C54;
    font-size: 1rem;
    max-width: 590px;
    margin: 1.05rem 0 0;
}

.ax-hero-side {
    padding: 1.3rem 1.35rem;
    border-radius: 14px;
    background: var(--ax-charcoal);
    color: var(--ax-offwhite);
    align-self: stretch;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 210px;
}

.ax-hero-side .ax-eyebrow {
    color: #A9A396;
    margin-bottom: 0.9rem;
}

.ax-hero-side-title {
    font-family: 'Fraunces', Georgia, serif;
    color: #FAF8F5;
    font-size: 1.35rem;
    line-height: 1.18;
    letter-spacing: -0.02em;
    margin: 0;
}

.ax-hero-side-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.42rem;
    margin-top: 1.15rem;
}

.ax-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.3rem 0.6rem;
    border: 1px solid rgba(250, 248, 245, 0.16);
    border-radius: 999px;
    color: #D8D2C5;
    font-size: 0.66rem;
    letter-spacing: 0.04em;
    white-space: nowrap;
}

.ax-chip.on-light {
    border-color: var(--ax-border);
    color: #5F5C54;
    background: rgba(255, 253, 250, 0.7);
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 999px;
    border: 1px solid var(--ax-charcoal);
    background: var(--ax-charcoal);
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    font-size: 0.86rem;
    padding: 0.62rem 1.25rem;
    transition: background 160ms ease, border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease;
    box-shadow: none;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
[data-testid="stBaseButton-primary"] > button,
div.stButton > button[kind="primary"] {
    background: #242321 !important;
    border-color: #242321 !important;
    color: #FAF8F5 !important;
}

.stButton > button[kind="primary"] *,
.stButton > button[data-testid="baseButton-primary"] *,
[data-testid="stBaseButton-primary"] > button *,
div.stButton > button[kind="primary"] * {
    color: #FAF8F5 !important;
    fill: #FAF8F5 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #3A3832;
    border-color: #3A3832;
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover,
[data-testid="stBaseButton-primary"] > button:hover,
div.stButton > button[kind="primary"]:hover {
    background: #3A3832 !important;
    border-color: #3A3832 !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover *,
.stButton > button[data-testid="baseButton-primary"]:hover *,
[data-testid="stBaseButton-primary"] > button:hover *,
div.stButton > button[kind="primary"]:hover * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

.stButton > button:focus:not(:active),
.stDownloadButton > button:focus:not(:active) {
    border-color: var(--ax-taupe);
    box-shadow: 0 0 0 3px rgba(160, 155, 133, 0.22);
}

.stButton > button[kind="primary"]:focus:not(:active),
.stButton > button[data-testid="baseButton-primary"]:focus:not(:active),
[data-testid="stBaseButton-primary"] > button:focus:not(:active),
div.stButton > button[kind="primary"]:focus:not(:active) {
    border-color: var(--ax-taupe) !important;
    color: #FAF8F5 !important;
    box-shadow: 0 0 0 3px rgba(160, 155, 133, 0.22);
}

.stButton > button[kind="primary"]:focus:not(:active) *,
.stButton > button[data-testid="baseButton-primary"]:focus:not(:active) *,
[data-testid="stBaseButton-primary"] > button:focus:not(:active) *,
div.stButton > button[kind="primary"]:focus:not(:active) * {
    color: #FAF8F5 !important;
}

.stButton > button:active,
.stDownloadButton > button:active {
    color: #FAF8F5 !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:active,
[data-testid="stBaseButton-primary"] > button:active,
div.stButton > button[kind="primary"]:active {
    color: #FAF8F5 !important;
}

.stButton > button[kind="primary"]:active *,
.stButton > button[data-testid="baseButton-primary"]:active *,
[data-testid="stBaseButton-primary"] > button:active *,
div.stButton > button[kind="primary"]:active * {
    color: #FAF8F5 !important;
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
[data-testid="stBaseButton-secondary"] > button {
    background: transparent !important;
    color: var(--ax-charcoal) !important;
    border-color: #CFC8BB !important;
}

.stButton > button[kind="secondary"] *,
.stButton > button[data-testid="baseButton-secondary"] *,
[data-testid="stBaseButton-secondary"] > button * {
    color: var(--ax-charcoal) !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
[data-testid="stBaseButton-secondary"] > button:hover {
    background: var(--ax-blush) !important;
    border-color: #DCC6BC !important;
    color: var(--ax-charcoal) !important;
}

.stButton > button[kind="secondary"]:hover *,
.stButton > button[data-testid="baseButton-secondary"]:hover *,
[data-testid="stBaseButton-secondary"] > button:hover * {
    color: var(--ax-charcoal) !important;
}

.stButton > button[kind="secondary"]:focus:not(:active),
.stButton > button[data-testid="baseButton-secondary"]:focus:not(:active),
[data-testid="stBaseButton-secondary"] > button:focus:not(:active) {
    color: var(--ax-charcoal) !important;
}

.stButton > button[kind="secondary"]:focus:not(:active) *,
.stButton > button[data-testid="baseButton-secondary"]:focus:not(:active) *,
[data-testid="stBaseButton-secondary"] > button:focus:not(:active) * {
    color: var(--ax-charcoal) !important;
}

.stButton > button:disabled,
.stDownloadButton > button:disabled,
.stButton > button[kind="primary"]:disabled,
.stButton > button[data-testid="baseButton-primary"]:disabled,
[data-testid="stBaseButton-primary"] > button:disabled {
    background: #6B6860 !important;
    border-color: #6B6860 !important;
    color: #C9C5BD !important;
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.stButton > button:disabled *,
.stDownloadButton > button:disabled *,
.stButton > button[kind="primary"]:disabled *,
.stButton > button[data-testid="baseButton-primary"]:disabled *,
[data-testid="stBaseButton-primary"] > button:disabled * {
    color: #C9C5BD !important;
    fill: #C9C5BD !important;
}

.stButton > button[kind="secondary"]:disabled,
.stButton > button[data-testid="baseButton-secondary"]:disabled,
[data-testid="stBaseButton-secondary"] > button:disabled {
    background: transparent !important;
    border-color: #B5B0A6 !important;
    color: #9B968C !important;
    opacity: 0.7;
}

.stButton > button[kind="secondary"]:disabled *,
.stButton > button[data-testid="baseButton-secondary"]:disabled *,
[data-testid="stBaseButton-secondary"] > button:disabled * {
    color: #9B968C !important;
}

.stDownloadButton > button {
    background: var(--ax-blush);
    border-color: #DEC8BE;
    color: var(--ax-charcoal) !important;
}

.stDownloadButton > button *,
.stDownloadButton > button:hover *,
.stDownloadButton > button:focus:not(:active) *,
.stDownloadButton > button:active * {
    color: var(--ax-charcoal) !important;
}

.stDownloadButton > button:hover {
    background: #ebd0c6;
    border-color: #D5B9AE;
    color: var(--ax-charcoal) !important;
}

.stDownloadButton > button:focus:not(:active) {
    color: var(--ax-charcoal) !important;
}

.stDownloadButton > button:active {
    color: var(--ax-charcoal) !important;
}

/* Upload */
[data-testid="stFileUploader"] {
    background: #FFFDFA;
    border: 1.5px dashed #C9C2B3;
    border-radius: 16px;
    padding: 0.7rem;
    transition: border-color 160ms ease, background 160ms ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--ax-taupe);
    background: #FFFBF6;
}

[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 0 !important;
    color: var(--ax-charcoal);
}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: var(--ax-grey) !important;
}

[data-testid="stFileUploader"] button {
    background: var(--ax-blush) !important;
    border: 1px solid #DEC8BE !important;
    color: var(--ax-charcoal) !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1rem !important;
}

[data-testid="stFileUploader"] button:hover {
    background: #ebd0c6 !important;
    border-color: #D5B9AE !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
    color: var(--ax-charcoal) !important;
    font-weight: 600;
}

/* Alerts and expanders */
[data-testid="stAlert"] {
    border-radius: 11px;
    border: 1px solid var(--ax-border);
    background: #FFFDFA;
}

[data-testid="stExpander"] {
    border: 1px solid var(--ax-border);
    border-radius: 12px;
    background: #FFFDFA;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    font-weight: 600;
    color: var(--ax-charcoal);
}

[data-testid="stExpander"] summary:hover {
    color: #5F5C54;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid var(--ax-border);
    border-radius: 12px;
    overflow: hidden;
    background: #FFFDFA;
}

[data-testid="stDataFrame"] [role="columnheader"] {
    background: #F1ECE3 !important;
    color: #3B3934 !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stTextInput"] input {
    border-radius: 9px;
    border-color: var(--ax-border);
    background: #FFFDFA;
}

/* Custom cards */
.ax-card {
    background: var(--ax-surface);
    border: 1px solid var(--ax-border);
    border-radius: 14px;
    padding: 1.25rem 1.35rem;
    height: 100%;
}

.ax-card.accent {
    background: linear-gradient(150deg, #FCF6F1 0%, #F3E0D9 100%);
    border-color: #E6D2C9;
}

.ax-card.dark {
    background: var(--ax-charcoal);
    border-color: var(--ax-charcoal);
}

.ax-card.dark h3,
.ax-card.dark p,
.ax-card.dark .ax-eyebrow {
    color: var(--ax-offwhite);
}

.ax-card h3 {
    font-size: 1.12rem !important;
    margin: 0 0 0.45rem;
}

.ax-card p {
    margin: 0;
    color: #625F57;
    font-size: 0.88rem;
}

.ax-step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid #CAC3B4;
    color: #6A665B;
    font-size: 0.68rem;
    font-weight: 700;
    margin-bottom: 0.9rem;
}

/* KPI cards */
.ax-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 0.2rem 0 1.4rem;
}

.ax-kpi {
    background: var(--ax-surface);
    border: 1px solid var(--ax-border);
    border-radius: 13px;
    padding: 1.1rem 1.15rem;
    min-height: 112px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.ax-kpi.tint {
    background: linear-gradient(155deg, #FFFDFA 0%, #F8EFE9 100%);
}

.ax-kpi.dark {
    background: var(--ax-charcoal);
    border-color: var(--ax-charcoal);
}

.ax-kpi-label {
    color: var(--ax-grey);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.ax-kpi-value {
    color: var(--ax-charcoal);
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(1.7rem, 3vw, 2.2rem);
    line-height: 1;
    letter-spacing: -0.03em;
    margin-top: 0.55rem;
}

.ax-kpi-note {
    color: #77746D;
    font-size: 0.7rem;
    margin-top: 0.45rem;
}

.ax-kpi.dark .ax-kpi-label,
.ax-kpi.dark .ax-kpi-note {
    color: #A9A396;
}

.ax-kpi.dark .ax-kpi-value {
    color: var(--ax-blush);
}

/* Status rows */
.ax-status-card {
    background: var(--ax-surface);
    border: 1px solid var(--ax-border);
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
}

.ax-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.58rem 0;
    border-bottom: 1px solid #ECE7DE;
    font-size: 0.82rem;
    color: #5F5C54;
}

.ax-status-row:last-child {
    border-bottom: 0;
    padding-bottom: 0;
}

.ax-status-row:first-of-type {
    padding-top: 0;
}

.ax-status-value {
    color: var(--ax-charcoal);
    font-weight: 600;
    text-align: right;
    max-width: 62%;
    overflow-wrap: anywhere;
}

.ax-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    background: var(--ax-surface-alt);
    color: #57544C;
    border: 1px solid var(--ax-border);
    font-size: 0.69rem;
    font-weight: 600;
    white-space: nowrap;
}

.ax-pill.ready {
    background: #EFF1E8;
    border-color: #D9DDCB;
    color: #565D43;
}

.ax-pill.waiting {
    background: #FAF0E9;
    border-color: #EBD7CA;
    color: #7B5B49;
}

.ax-pill.missing {
    background: #F7E9E5;
    border-color: #E7D0C8;
    color: #7E5146;
}

/* File summary strip */
.ax-file-strip {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    background: #FCF7F2;
    border: 1px solid #E8D9CF;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin: 0.2rem 0 1rem;
}

.ax-file-name {
    color: var(--ax-charcoal);
    font-size: 0.88rem;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.ax-file-meta {
    color: var(--ax-grey);
    font-size: 0.72rem;
}

.ax-file-stats {
    display: flex;
    gap: 1.1rem;
    color: #5F5C54;
    font-size: 0.73rem;
}

.ax-file-stats strong {
    color: var(--ax-charcoal);
}

/* Empty state */
.ax-empty {
    border: 1px solid var(--ax-border);
    border-radius: 16px;
    background:
        radial-gradient(circle at 90% 10%, rgba(243, 224, 217, 0.55) 0, rgba(243, 224, 217, 0) 35%),
        #FFFDFA;
    padding: 2.2rem;
    text-align: left;
}

.ax-empty h3 {
    margin: 0 0 0.45rem;
}

.ax-empty p {
    color: var(--ax-grey);
    max-width: 580px;
    margin: 0;
}

/* Charts */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: var(--ax-surface);
    border: 1px solid var(--ax-border);
    border-radius: 13px;
    padding: 0.55rem;
}

.ax-chart-title {
    color: var(--ax-charcoal);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0.2rem 0 -0.2rem 0.2rem;
}

.ax-chart-caption {
    color: var(--ax-grey);
    font-size: 0.7rem;
    margin: 0.15rem 0 0 0.2rem;
}

/* Footer */
.ax-footer {
    margin-top: 3rem;
    padding-top: 1.3rem;
    border-top: 1px solid var(--ax-border);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    color: var(--ax-grey);
    font-size: 0.69rem;
}

.ax-footer strong {
    color: var(--ax-charcoal);
    font-family: 'Fraunces', Georgia, serif;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: -0.01em;
}

.ax-divider {
    height: 1px;
    background: var(--ax-border);
    border: 0;
    margin: 2rem 0;
}

/* Responsive */
@media (max-width: 980px) {
    .ax-hero-grid {
        grid-template-columns: 1fr;
    }

    .ax-hero-side {
        min-height: 0;
    }

    .ax-kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    [data-testid="stAppViewBlockContainer"] {
        padding: 1.25rem 1.05rem 3rem;
    }

    .ax-hero {
        padding: 1.35rem;
        border-radius: 16px;
    }

    .ax-kpi-grid {
        grid-template-columns: 1fr;
    }

    .ax-kpi {
        min-height: 96px;
    }

    .ax-footer {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
"""


BRAND_MARK = """
<svg class="ax-brand-mark" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="1" y="1" width="42" height="42" rx="12" stroke="#A09B85" stroke-width="1.2"/>
    <path d="M13 30L22 12L31 30" stroke="#F3E0D9" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M13 30H31" stroke="#A09B85" stroke-width="1.1" stroke-linecap="round"/>
    <circle cx="22" cy="12" r="2.3" fill="#F3E0D9"/>
    <circle cx="13" cy="30" r="1.9" fill="#A09B85"/>
    <circle cx="31" cy="30" r="1.9" fill="#A09B85"/>
    <circle cx="22" cy="23.2" r="1.5" fill="#A09B85"/>
    <path d="M22 12V23.2M13 30L22 23.2L31 30" stroke="#A09B85" stroke-width="0.9" opacity="0.7"/>
</svg>
"""


def render_html(markup: str) -> None:
    """Render trusted internal HTML without source indentation leaking into output.

    Streamlit/CommonMark treats HTML lines indented by four or more spaces as
    code blocks, which is why indented multiline HTML used to appear as raw
    text. Every dynamic value interpolated into ``markup`` must already be
    escaped by the caller.
    """
    cleaned = "\n".join(
        line.strip() for line in textwrap.dedent(markup).strip().splitlines()
    )
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand() -> None:
    render_html(
        f"""
        <div class="ax-sidebar-brand">
            {BRAND_MARK}
            <div>
                <div class="ax-wordmark">Anomali<span>X</span></div>
                <div class="ax-brand-tagline">Intelligent Network<br>Anomaly Detection</div>
            </div>
        </div>
        """
    )


def sidebar_status(model_ready: bool, dataset_loaded: bool, result_count: int) -> None:
    model_class = "is-ready" if model_ready else "is-missing"
    model_text = "Model ready" if model_ready else "Unavailable"
    data_class = "is-ready" if dataset_loaded else "is-waiting"
    data_text = "Dataset loaded" if dataset_loaded else "Awaiting data"
    results_text = f"{result_count:,} records" if result_count else "Not run"

    render_html(
        f"""
        <div class="ax-sidebar-status">
            <div class="ax-sidebar-status-title">System status</div>
            <div class="ax-sidebar-status-row">
                <span><span class="ax-dot {model_class}"></span>Detection model</span>
                <strong>{model_text}</strong>
            </div>
            <div class="ax-sidebar-status-row">
                <span><span class="ax-dot {data_class}"></span>Dataset</span>
                <strong>{data_text}</strong>
            </div>
            <div class="ax-sidebar-status-row">
                <span>Last analysis</span>
                <strong>{results_text}</strong>
            </div>
        </div>
        <div class="ax-version">ANOMALIX / v1.0 · LOCAL</div>
        """
    )


def hero(
    model_ready: bool,
    dataset_loaded: bool,
    dataset_rows: int,
    result_count: int,
) -> None:
    if dataset_loaded:
        data_text = f"{dataset_rows:,} records ready"
    else:
        data_text = "No dataset loaded"

    if result_count:
        analysis_text = f"{result_count:,} analysed"
    else:
        analysis_text = "Analysis not run"

    model_text = "Isolation Forest online" if model_ready else "Model unavailable"
    model_class = "ready" if model_ready else "missing"

    render_html(
        f"""
        <div class="ax-hero">
            <div class="ax-hero-grid">
                <div>
                    <div class="ax-eyebrow">Network anomaly intelligence</div>
                    <div class="ax-hero-title">See the signal<br><em>before</em> it becomes a threat.</div>
                    <p class="ax-hero-copy">
                        AnomaliX reads network traffic records, applies a trained
                        Isolation Forest model, and surfaces the traffic that falls
                        outside normal behaviour. Upload a dataset to begin.
                    </p>
                </div>
                <div class="ax-hero-side">
                    <div>
                        <div class="ax-eyebrow">Workspace state</div>
                        <p class="ax-hero-side-title">A quiet view of<br>what needs attention.</p>
                    </div>
                    <div class="ax-hero-side-meta">
                        <span class="ax-pill {model_class}">{model_text}</span>
                        <span class="ax-chip">{data_text}</span>
                        <span class="ax-chip">{analysis_text}</span>
                    </div>
                </div>
            </div>
        </div>
        """
    )


def section_head(eyebrow: str, title: str, copy: str | None = None) -> None:
    copy_html = f"<p>{html.escape(copy)}</p>" if copy else ""
    render_html(
        f"""
        <div class="ax-section-head">
            <div class="ax-eyebrow">{html.escape(eyebrow)}</div>
            <h2>{html.escape(title)}</h2>
            {copy_html}
        </div>
        """
    )


def kpi_grid(items: list[dict[str, str]]) -> None:
    """Render KPI cards. Each item needs label, value, note, and optional tone."""
    cards = []
    for item in items:
        tone = item.get("tone", "")
        tone_class = f" {tone}" if tone else ""
        cards.append(
            f"""
            <div class="ax-kpi{tone_class}">
                <div>
                    <div class="ax-kpi-label">{html.escape(item['label'])}</div>
                    <div class="ax-kpi-value">{html.escape(item['value'])}</div>
                </div>
                <div class="ax-kpi-note">{html.escape(item.get('note', ''))}</div>
            </div>
            """
        )
    render_html(f'<div class="ax-kpi-grid">{"".join(cards)}</div>')


def file_strip(name: str, size_label: str, rows: int, columns: int) -> None:
    render_html(
        f"""
        <div class="ax-file-strip">
            <div>
                <div class="ax-file-name">{html.escape(name)}</div>
                <div class="ax-file-meta">Uploaded dataset · {html.escape(size_label)}</div>
            </div>
            <div class="ax-file-stats">
                <span><strong>{rows:,}</strong> records</span>
                <span><strong>{columns:,}</strong> columns</span>
            </div>
        </div>
        """
    )


def status_card(rows: list[tuple[str, str, str]]) -> None:
    """Rows are (label, value, state) where state is ready/waiting/missing."""
    row_html = []
    for label, value, state in rows:
        pill = f'<span class="ax-pill {state}">{html.escape(value)}</span>' if state else f'<span class="ax-status-value">{html.escape(value)}</span>'
        row_html.append(
            f'<div class="ax-status-row"><span>{html.escape(label)}</span>{pill}</div>'
        )
    render_html(f'<div class="ax-status-card">{"".join(row_html)}</div>')


def empty_state(title: str, copy: str) -> None:
    render_html(
        f"""
        <div class="ax-empty">
            <div class="ax-eyebrow">Nothing to display yet</div>
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(copy)}</p>
        </div>
        """
    )


def footer() -> None:
    render_html(
        """
        <div class="ax-footer">
            <strong>AnomaliX</strong>
            <span>Intelligent network anomaly detection · Built for careful analysis</span>
        </div>
        """
    )
