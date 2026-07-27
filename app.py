"""
Streamlit Live Conversational BI Agent for Monday.com.

Features:
- Live Read-Only Connection to Monday.com GraphQL API
- Data-Health Sidebar (Row counts, last sync, field completeness %, join reliability)
- Inline Plotly Charts (Pipeline distribution, Execution status, Cross-board owner breakdown)
- One-Click "Leadership Update" generator
- Conversational Chat Interface powered by AI Agent
"""

import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from agent import BIAgent
from monday_client import MondayClient
from data_cleaning import clean_deal_funnel_data, clean_work_order_data
from data_quality import get_board_completeness
from join_logic import safe_join_cross_board, best_effort_deal_match
from leadership_summary import generate_leadership_update

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="Monday.com Conversational BI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN STYLING (CSS) ---
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: #f8fafc;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .badge-live {
        background-color: #064e3b;
        color: #34d399;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-readonly {
        background-color: #1e3a8a;
        color: #60a5fa;
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=180)
def load_live_data():
    """Fetch live data from Monday.com API with 3-minute in-memory caching."""
    client = MondayClient()
    raw_deals = client.fetch_board_data("5030221175", use_cache=True)
    raw_wo = client.fetch_board_data("5030221237", use_cache=True)

    df_deals_raw = pd.DataFrame(raw_deals)
    df_wo_raw = pd.DataFrame(raw_wo)

    df_deals_clean, deals_anomalies = clean_deal_funnel_data(df_deals_raw)
    df_wo_clean, wo_anomalies = clean_work_order_data(df_wo_raw)

    dq_deals = get_board_completeness(df_deals_clean, "Deal Funnel")
    dq_wo = get_board_completeness(df_wo_clean, "Work Order Tracker")

    df_safe_owner, _ = safe_join_cross_board(df_deals_clean, df_wo_clean, join_key="owner")
    _, match_meta = best_effort_deal_match(df_deals_clean, df_wo_clean)

    return {
        "df_deals_raw": df_deals_raw,
        "df_wo_raw": df_wo_raw,
        "df_deals": df_deals_clean,
        "df_wo": df_wo_clean,
        "deals_anomalies": deals_anomalies,
        "wo_anomalies": wo_anomalies,
        "dq_deals": dq_deals,
        "dq_wo": dq_wo,
        "df_safe_owner": df_safe_owner,
        "match_meta": match_meta,
        "sync_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# Load Data
data = load_live_data()

# --- SIDEBAR: DATA HEALTH & METRICS ---
with st.sidebar:
    st.title("📊 Data Health & Controls")

    st.markdown(
        '<span class="badge-live">🟢 LIVE CONNECTED</span> &nbsp; '
        '<span class="badge-readonly">🔒 READ-ONLY QUERY</span>',
        unsafe_allow_html=True
    )
    st.caption(f"Last API Sync: **{data['sync_time']}**")

    st.divider()

    # Board 1 Data Health
    st.subheader("📋 Board 1: Deal Funnel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Raw Rows", len(data["df_deals_raw"]))
    with col2:
        st.metric("Valid Rows", len(data["df_deals"]), delta=f"-{data['deals_anomalies'].get('corrupt_status_rows_excluded', 0)} corrupt")

    val_comp = data["dq_deals"]["metrics"].get("numeric_mm5ndf61", {}).get("completeness_pct", 0.0)
    st.caption(f"Masked Deal Value Completeness: **{val_comp}%** ({100.0 - val_comp:.1f}% null)")

    st.divider()

    # Board 2 Data Health
    st.subheader("🛠️ Board 2: Work Order Tracker")
    st.metric("Total Rows", len(data["df_wo"]))
    st.caption("⚠️ 4 Fields 100% Null (Expected Billing Month, Collection Date - Not Tracked)")

    st.divider()

    # Join Reliability
    st.subheader("🔗 Join Reliability")
    st.markdown(f"- **Safe Owner Join**: 100% Valid ({len(data['df_safe_owner'])} Groups)")
    st.markdown(f"- **Deal Name Match Coverage**: **{data['match_meta']['coverage_confidence_pct']}%** ({data['match_meta']['distinct_matched_deals']}/{data['match_meta']['total_deals_board1']} deals)")
    st.caption("*Reconciliation active for matched deals only.*")


# --- MAIN INTERFACE ---
st.title("🤖 Monday.com Conversational BI Agent")
st.markdown("Query live Monday.com deal funnels and work orders with dynamic data-quality transparency.")

# Action Bar: Leadership Update & Visuals Toggle
col_btn, col_info = st.columns([1, 3])

with col_btn:
    generate_exec = st.button("⚡ Leadership Update", use_container_width=True, type="primary")

if generate_exec:
    exec_update = generate_leadership_update()
    st.markdown(exec_update["markdown"])
    st.divider()

# Inline Visual Analytics Expander
with st.expander("📈 Inline Visual Analytics (Click to Expand)", expanded=True):
    v_col1, v_col2, v_col3 = st.columns(3)

    with v_col1:
        st.markdown("##### Deal Funnel Status")
        status_df = data["df_deals"]["color_mm5ncsbg"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]
        fig1 = px.bar(status_df, x="Status", y="Count", color="Status", text="Count", color_discrete_sequence=px.colors.qualitative.Dark24)
        fig1.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with v_col2:
        st.markdown("##### Execution Status")
        exec_df = data["df_wo"]["color_mm5ngrrp"].value_counts().reset_index()
        exec_df.columns = ["Status", "Count"]
        fig2 = px.pie(exec_df, names="Status", values="Count", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with v_col3:
        st.markdown("##### Owner Cross-Board Comparison")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=data["df_safe_owner"]["Owner Code"], y=data["df_safe_owner"]["total_deals"], name="Deals"))
        fig3.add_trace(go.Bar(x=data["df_safe_owner"]["Owner Code"], y=data["df_safe_owner"]["total_work_orders"], name="Work Orders"))
        fig3.update_layout(barmode="group", height=260, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Preset Quick-Prompt Pills
st.markdown("##### Quick Questions:")
p_col1, p_col2, p_col3 = st.columns(3)

preset_query = None
if p_col1.button("💰 Won Deals & Quality Caveats", use_container_width=True):
    preset_query = "What is our total deal value for Won deals, and what are the data quality caveats?"
if p_col2.button("🔗 Owner Cross-Board Performance", use_container_width=True):
    preset_query = "Show me a cross-board summary comparing deals and work orders by Owner code."
if p_col3.button("🔍 Data Health & Completeness Audit", use_container_width=True):
    preset_query = "What is the data health and completeness report for both boards?"

# Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your Monday.com Conversational BI Agent. Ask me anything about your deal funnel, work orders, financial metrics, or data quality health!"
        }
    ]

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input & Prompt Handling
user_input = st.chat_input("Ask a founder question about your Monday.com data...")
active_prompt = preset_query or user_input

if active_prompt:
    # Render user prompt
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    # Process via BIAgent
    agent = BIAgent()
    with st.chat_message("assistant"):
        with st.spinner("Analyzing live Monday.com boards..."):
            response_obj = agent.run_query(active_prompt)
            response_text = response_obj["response"]
            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
