import streamlit as st
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Delivery Intelligence",
    page_icon="📦",
    layout="centered",
)

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

if not groq_key:
    st.error("API key not found — add GROQ_API_KEY to `.env` or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=groq_key)

@st.cache_data
def load_data():
    seller_df   = pd.read_csv("outputs/pbi_seller_summary.csv")
    state_df    = pd.read_csv("outputs/pbi_state_summary.csv")
    monthly_df  = pd.read_csv("outputs/pbi_monthly_trend.csv")
    bucket_df   = pd.read_csv("outputs/pbi_delay_buckets.csv")
    biz_summary = pd.read_csv("outputs/business_summary.csv")
    return seller_df, state_df, monthly_df, bucket_df, biz_summary

seller_df, state_df, monthly_df, bucket_df, business_summary = load_data()

total_orders = seller_df["total_orders"].sum()
late_orders  = seller_df["late_orders"].sum()
late_rate    = late_orders / total_orders * 100
critical_ct  = len(seller_df[seller_df["quadrant"] == "Critical"])
gmv_at_risk  = seller_df.loc[seller_df["quadrant"] == "Critical", "total_gmv"].sum()

# Header
st.title("📦 Delivery Intelligence")
st.caption("Ask questions about delivery performance, sellers and revenue impact.")
st.divider()

# KPI strip
col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Late Delivery Rate", f"{late_rate:.1f}%", delta=f"{late_orders:,} late", delta_color="inverse")
col3.metric("Critical Sellers", critical_ct, delta=f"₹{gmv_at_risk:,.0f} GMV at risk", delta_color="inverse")
st.divider()
tab_ai, tab_dash = st.tabs([" AI Analyst", "📊 Visual Dashboard"])
with tab_ai:
    def build_context():
        return f"""
    You are a data analyst assistant for an e-commerce delivery performance audit.
    Answer questions using ONLY the data provided below. Always cite specific numbers.
    Never make up figures. If the answer isn't in the data, say so clearly.

    OVERALL BUSINESS & RISK SUMMARY:
    {business_summary.to_string(index=False)}

    SELLER SUMMARY (top 10 by GMV at risk):
    {seller_df.nlargest(10, "total_gmv").to_string(index=False)}

    STATE SUMMARY:
    {state_df.sort_values("late_rate_pct", ascending=False).to_string(index=False)}

    MONTHLY TREND:
    {monthly_df.to_string(index=False)}

    DELAY BUCKET ANALYSIS:
    {bucket_df.to_string(index=False)}

    KEY METRICS:
    - Total orders analyzed: {total_orders:,}
    - Overall late delivery rate: {late_rate:.1f}%
    - Critical quadrant sellers: {critical_ct}
    """

    def ask_data(question: str) -> str:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": build_context()},
                {"role": "user",   "content": question},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        return response.choices[0].message.content

    # Suggested questions
    st.subheader("Quick questions")
    suggestions = [
        "Which state has the worst late delivery rate?",
        "How many sellers are in the critical quadrant?",
        "What is the total revenue at risk?",
        "Which month had the highest late rate?",
        "What happens to reviews when delivery is 7+ days late?",
        "Which quadrant has the most GMV at risk?",
    ]

    col1, col2, col3 = st.columns(3)
    for i, s in enumerate(suggestions):
        if [col1, col2, col3][i % 3].button(s, use_container_width=True):
            st.session_state.question = s



# Input
    question = st.text_input(
        "Your question",
        value=st.session_state.get("question", ""),
        placeholder="e.g. Which sellers should we action immediately?",
    )

# Answer
    if question:
        with st.spinner("Analyzing..."):
            answer = ask_data(question)
        st.info(answer, icon="💡")
with tab_dash:
    st.subheader("Logistics Performance Visuals")
    
    # Row 1: Plotly Interactive Charts
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("**Revenue Impact Waterfall**")
        try:
            with open("outputs/revenue_impact.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=450)
        except FileNotFoundError:
            st.error("Revenue impact chart not found.")

    with row1_col2:
        st.markdown("**Seller Performance Quadrants**")
        try:
            with open("outputs/seller_quadrant.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=450)
        except FileNotFoundError:
            st.error("Seller quadrant chart not found.")

    st.divider()

    # Row 2: Static Python Visuals
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("**State-Level Heatmap**")
        try:
            st.image("outputs/state_heatmap.png", use_container_width=True)
        except FileNotFoundError:
            st.error("Heatmap image not found.")

    with row2_col2:
        st.markdown("**Review Score vs. Delay Duration**")
        
        st.image("outputs/delay_severity.png", use_container_width=True)