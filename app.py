import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import time

# Auto-refresh every 5 minutes
st_autorefresh = st.empty()
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:  # 300 seconds = 5 min
    st.session_state.last_refresh = time.time()
    st.rerun()
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(page_title="Market Intelligence", layout="wide", page_icon="◈")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}
.main { background-color: #080c14; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }

/* Header */
.dashboard-header {
    border-bottom: 1px solid #1e293b;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.dashboard-title {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8;
}
.dashboard-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #475569;
    margin-top: 0.2rem;
}

/* Metric cards */
.metric-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 1rem 1.2rem;
}
.metric-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    color: #f1f5f9;
}
.metric-positive { color: #22c55e; }
.metric-negative { color: #ef4444; }
.metric-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    margin-top: 0.2rem;
}

/* Section headers */
.section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #475569;
    border-left: 2px solid #3b82f6;
    padding-left: 0.6rem;
    margin-bottom: 1rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e293b;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #f1f5f9 !important;
    border-bottom: 2px solid #3b82f6 !important;
    background: transparent !important;
}

/* Dataframe */
.dataframe { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }
[data-testid="stDataFrame"] { border: 1px solid #1e293b; border-radius: 6px; }

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────
now = datetime.today()
st.markdown(f"""
<div class="dashboard-header">
    <div class="dashboard-title">◈ Market Intelligence Terminal</div>
    <div class="dashboard-subtitle">LIVE DATA  ·  {now.strftime('%A, %B %d, %Y  ·  %H:%M')} LOCAL</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["SECTOR ROTATION", "EARNINGS TRACKER"])

# ── PLOTTING DEFAULTS ─────────────────────────────────────────
BG       = '#080c14'
CARD_BG  = '#0f172a'
BORDER   = '#1e293b'
TEXT     = '#e2e8f0'
MUTED    = '#475569'
GREEN    = '#22c55e'
RED      = '#ef4444'
BLUE     = '#3b82f6'

def style_ax(ax):
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    plt.setp(ax.get_xticklabels(), color=MUTED)
    plt.setp(ax.get_yticklabels(), color=MUTED)

# ════════════════════════════════════════════════════════════
# TAB 1 — SECTOR ROTATION
# ════════════════════════════════════════════════════════════
with tab1:
    sectors = {
        'XLF':  'Financials',   'XLV': 'Health Care',
        'XLE':  'Energy',       'XLI': 'Industrials',
        'XLY':  'Consumer Disc.', 'XLP': 'Consumer Staples',
        'XLU':  'Utilities',    'XLB': 'Materials',
        'XLRE': 'Real Estate',  'XLC': 'Comm. Services'
    }

    with st.spinner(""):
        end   = datetime.today()
        start = end - timedelta(days=90)
        raw    = yf.download(list(sectors.keys()), start=start, end=end, auto_adjust=True, progress=False)
        prices = raw['Close'].dropna(how='all').ffill()

def pct(df, d):
        if len(df) < d:
            return pd.Series([None] * len(df.columns), index=df.columns)
        return ((df.iloc[-1] - df.iloc[-d]) / df.iloc[-d] * 100).round(2)

    returns = pd.DataFrame({
        '1W': pct(prices, min(5, len(prices))),
        '1M': pct(prices, min(21, len(prices))),
        '3M': pct(prices, min(63, len(prices)))
    })

    returns.index = [sectors[t] for t in returns.index]
    returns = returns.sort_values('1M', ascending=False)

    # ── TOP METRIC CARDS ──
    best  = returns['1M'].idxmax()
    worst = returns['1M'].idxmin()
    avg   = returns['1M'].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Top Sector (1M)</div>
            <div class="metric-value metric-positive">{best}</div>
            <div class="metric-delta metric-positive">+{returns.loc[best,'1M']:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Worst Sector (1M)</div>
            <div class="metric-value metric-negative">{worst}</div>
            <div class="metric-delta metric-negative">{returns.loc[worst,'1M']:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        col = 'metric-positive' if avg > 0 else 'metric-negative'
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Avg Sector Return (1M)</div>
            <div class="metric-value {col}">{avg:+.2f}%</div>
            <div class="metric-delta {col}">Across {len(returns)} sectors</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        bullish = (returns['1M'] > 0).sum()
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Sectors Positive (1M)</div>
            <div class="metric-value">{bullish}<span style="font-size:0.9rem;color:{MUTED}">/{len(returns)}</span></div>
            <div class="metric-delta" style="color:{MUTED}">Breadth indicator</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── CHARTS ──
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown('<div class="section-label">Return Heatmap</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(CARD_BG)
        cmap = sns.diverging_palette(0, 130, s=85, l=45, as_cmap=True)
        sns.heatmap(returns, annot=True, fmt=".1f", cmap=cmap, center=0,
                    linewidths=1, linecolor=BG, ax=ax,
                    cbar_kws={'shrink': 0.7, 'pad': 0.02},
                    annot_kws={'size': 10, 'weight': '600', 'color': 'white'})
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(colors=MUTED, labelsize=9, length=0)
        plt.setp(ax.get_xticklabels(), color=MUTED, fontsize=9)
        plt.setp(ax.get_yticklabels(), color=TEXT, rotation=0, fontsize=9)
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(colors=MUTED, labelsize=8)
        cbar.outline.set_edgecolor(BORDER)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-label">1-Month Ranked Performance</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        fig2.patch.set_facecolor(BG)
        style_ax(ax2)
        sorted_1m = returns['1M'].sort_values()
        bar_colors = [GREEN if x > 0 else RED for x in sorted_1m]
        bars = ax2.barh(sorted_1m.index, sorted_1m.values,
                        color=bar_colors, height=0.55, edgecolor='none')
        for bar, val in zip(bars, sorted_1m.values):
            pad = 0.1 if val >= 0 else -0.1
            ha  = 'left' if val >= 0 else 'right'
            ax2.text(val + pad, bar.get_y() + bar.get_height()/2,
                     f'{val:+.1f}%', va='center', ha=ha,
                     color=TEXT, fontsize=8.5, fontweight='600',
                     fontfamily='monospace')
        ax2.axvline(0, color=BORDER, linewidth=1)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_xlabel('Return (%)', color=MUTED, fontsize=8)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig2, use_container_width=True)

    # ── DATA TABLE ──
    st.markdown('<div class="section-label" style="margin-top:1rem">Raw Data</div>', unsafe_allow_html=True)
    styled = returns.style\
        .format("{:+.2f}%")\
        .background_gradient(cmap='RdYlGn', axis=None, vmin=-10, vmax=10)\
        .set_properties(**{'font-family': 'JetBrains Mono', 'font-size': '12px'})
    st.dataframe(styled, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — EARNINGS TRACKER
# ════════════════════════════════════════════════════════════
with tab2:
    tickers = ['AAPL','MSFT','GOOGL','META','AMZN','NVDA','JPM','GS','WMT','TGT']
    earnings_data = []

    with st.spinner(""):
        for ticker in tickers:
            try:
                stock   = yf.Ticker(ticker)
                e       = stock.earnings_dates
                if e is None or e.empty: continue
                past    = e[e.index < pd.Timestamp.today(tz='America/New_York')]
                if past.empty: continue
                latest  = past.iloc[0]
                est     = latest.get('EPS Estimate')
                act     = latest.get('Reported EPS')
                surp    = latest.get('Surprise(%)')
                if pd.isna(est) or pd.isna(act): continue
                earnings_data.append({
                    'Ticker':        ticker,
                    'Date':          past.index[0].strftime('%Y-%m-%d'),
                    'EPS Est':       round(est, 2),
                    'EPS Actual':    round(act, 2),
                    'Surprise %':    round(surp, 2) if not pd.isna(surp) else round((act-est)/abs(est)*100, 2)
                })
            except: continue

    edf = pd.DataFrame(earnings_data).sort_values('Surprise %', ascending=False)

    # ── METRIC CARDS ──
    best_e  = edf.loc[edf['Surprise %'].idxmax()]
    worst_e = edf.loc[edf['Surprise %'].idxmin()]
    avg_e   = edf['Surprise %'].mean()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Biggest Beat</div>
            <div class="metric-value metric-positive">{best_e['Ticker']}</div>
            <div class="metric-delta metric-positive">+{best_e['Surprise %']:.1f}% surprise</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Smallest Beat</div>
            <div class="metric-value metric-negative">{worst_e['Ticker']}</div>
            <div class="metric-delta metric-negative">{worst_e['Surprise %']:+.1f}% surprise</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        col = 'metric-positive' if avg_e > 0 else 'metric-negative'
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Avg EPS Surprise</div>
            <div class="metric-value {col}">{avg_e:+.1f}%</div>
            <div class="metric-delta" style="color:{MUTED}">{len(edf)} companies tracked</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        st.markdown('<div class="section-label">EPS Surprise Ranking</div>', unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(5, 5))
        fig3.patch.set_facecolor(BG)
        style_ax(ax3)
        sorted_e = edf.sort_values('Surprise %', ascending=True)
        bar_colors = [GREEN if x > 0 else RED for x in sorted_e['Surprise %']]
        bars = ax3.barh(sorted_e['Ticker'], sorted_e['Surprise %'],
                        color=bar_colors, height=0.55, edgecolor='none')
        for bar, val in zip(bars, sorted_e['Surprise %']):
            pad = 0.5 if val >= 0 else -0.5
            ha  = 'left' if val >= 0 else 'right'
            ax3.text(val + pad, bar.get_y() + bar.get_height()/2,
                     f'{val:+.1f}%', va='center', ha=ha,
                     color=TEXT, fontsize=8.5, fontweight='600',
                     fontfamily='monospace')
        ax3.axvline(0, color=BORDER, linewidth=1)
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.set_xlabel('Surprise (%)', color=MUTED, fontsize=8)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig3, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-label">Estimated vs Reported EPS</div>', unsafe_allow_html=True)
        fig4, ax4 = plt.subplots(figsize=(7, 5))
        fig4.patch.set_facecolor(BG)
        style_ax(ax4)
        x     = np.arange(len(edf))
        w     = 0.32
        b1    = ax4.bar(x - w/2, edf['EPS Est'],    w, color=BLUE,  alpha=0.85, edgecolor='none', label='Estimate')
        b2    = ax4.bar(x + w/2, edf['EPS Actual'], w, color=GREEN, alpha=0.85, edgecolor='none', label='Actual')
        ax4.set_xticks(x)
        ax4.set_xticklabels(edf['Ticker'], color=MUTED, fontsize=8.5)
        ax4.set_ylabel('EPS ($)', color=MUTED, fontsize=8)
        ax4.legend(facecolor=CARD_BG, edgecolor=BORDER, labelcolor=MUTED, fontsize=8)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        for bar in b1:
            ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                     f'${bar.get_height():.2f}', ha='center', va='bottom',
                     color=BLUE, fontsize=7, fontfamily='monospace')
        for bar in b2:
            ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                     f'${bar.get_height():.2f}', ha='center', va='bottom',
                     color=GREEN, fontsize=7, fontfamily='monospace')
        plt.tight_layout(pad=0.5)
        st.pyplot(fig4, use_container_width=True)

    st.markdown('<div class="section-label" style="margin-top:1rem">Raw Data</div>', unsafe_allow_html=True)
    styled_e = edf.style\
        .format({'EPS Est': '${:.2f}', 'EPS Actual': '${:.2f}', 'Surprise %': '{:+.2f}%'})\
        .background_gradient(subset=['Surprise %'], cmap='RdYlGn', vmin=-20, vmax=100)\
        .set_properties(**{'font-family': 'JetBrains Mono', 'font-size': '12px'})
    st.dataframe(styled_e, use_container_width=True)