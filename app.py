import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os
from dotenv import load_dotenv


st.set_page_config(
    page_title="Olist Delivery Audit",
    page_icon="📦",
    layout="wide",
)

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

def get_metric(label):
    row = business_summary[business_summary["Metric"] == label]
    return row["Value"].values[0] if len(row) else "N/A"

direct_at_risk = get_metric("Estimated Direct Revenue at Risk")


load_dotenv()
groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
client = Groq(api_key=groq_key) if groq_key else None

def build_context():
    # Detect correct column names dynamically
    late_col   = "late_rate_pct" if "late_rate_pct" in seller_df.columns else "late_rate"
    review_col = "avg_review_score" if "avg_review_score" in seller_df.columns else "avg_review"

    return f"""
You are a data analyst assistant for an e-commerce delivery performance audit of Olist (Brazil, 2017-2018).
Answer questions using ONLY the data provided below. Always cite specific numbers.
Never make up figures. If the answer isn't in the data, say so clearly.

OVERALL BUSINESS & RISK SUMMARY:
{business_summary.to_string(index=False)}

SELLER SUMMARY (top 10 by GMV):
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
- Revenue at risk: {direct_at_risk}
"""

def ask_groq(messages):
    if not client:
        return "⚠️ Groq API key not configured. Add GROQ_API_KEY to your `.env` or Streamlit Secrets."
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": build_context()}] + messages,
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )
    return response.choices[0].message.content


with st.sidebar:
    st.title("📦 Olist Audit")
    st.info("Brazilian E-Commerce Analysis\n2017 – 2018")
    page = st.selectbox(
        "Navigation",
        ["Executive Summary", "Seller Intelligence", "Geographic Analysis", "Power BI Dashboard", "Ask the Data"]
    )
    st.divider()
    st.caption("Built with SQL + Python + Streamlit")


if page == "Executive Summary":
    st.header("Executive Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", f"{total_orders:,}")
    c2.metric("Late Rate", f"{late_rate:.1f}%", delta=f"{late_orders:,} late", delta_color="inverse")
    c3.metric("Critical Sellers", critical_ct, delta="Action Required", delta_color="inverse")
    c4.metric("Revenue at Risk", direct_at_risk)

    st.divider()

    col_trend, col_donut = st.columns([2, 1])

    # Detect month column
    month_col = "order_month" if "order_month" in monthly_df.columns else monthly_df.columns[0]
    late_pct_col = "late_rate_pct" if "late_rate_pct" in monthly_df.columns else "late_rate"

    with col_trend:
        with st.container(border=True):
            st.subheader("Monthly Late Rate Trend")
            fig = px.line(monthly_df, x=month_col, y=late_pct_col, markers=True)
            fig.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0),
                              xaxis_title="", yaxis_title="Late Rate %")
            st.plotly_chart(fig, use_container_width=True)

    with col_donut:
        with st.container(border=True):
            st.subheader("Order Reliability")
            fig_d = px.pie(
                values=[total_orders - late_orders, late_orders],
                names=["On-Time", "Late"],
                hole=0.55,
                color_discrete_sequence=["#2ecc71", "#e74c3c"]
            )
            fig_d.update_layout(height=350, showlegend=True, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_d, use_container_width=True)

    st.divider()

    with st.container(border=True):
        st.subheader("Review Score vs. Delivery Delay")
        # Detect columns
        delay_col  = "delay_bucket" if "delay_bucket" in bucket_df.columns else bucket_df.columns[0]
        count_col  = "order_count"  if "order_count"  in bucket_df.columns else bucket_df.columns[1]
        review_col = "avg_review_score" if "avg_review_score" in bucket_df.columns else (
                     "avg_review" if "avg_review" in bucket_df.columns else bucket_df.columns[2])
        fig_b = px.bar(
            bucket_df.sort_values(delay_col), x=delay_col, y=count_col,
            color=review_col, color_continuous_scale="RdYlGn",
            labels={delay_col: "Delay Bucket", count_col: "Orders", review_col: "Avg Review"}
        )
        fig_b.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_b, use_container_width=True)


elif page == "Seller Intelligence":
    st.header("Seller Intelligence")

    # Compute late_rate_pct if not present
    if "late_rate_pct" not in seller_df.columns and "late_rate" not in seller_df.columns:
        seller_df["late_rate_pct"] = (seller_df["late_orders"] / seller_df["total_orders"] * 100).round(2)
    late_col = "late_rate_pct" if "late_rate_pct" in seller_df.columns else "late_rate"

    review_col = "avg_review_score" if "avg_review_score" in seller_df.columns else (
                 "avg_review" if "avg_review" in seller_df.columns else None)

    with st.expander("Filters", expanded=True):
        f1, f2 = st.columns(2)
        quadrant_opts = seller_df["quadrant"].dropna().unique().tolist()
        quadrant_filter = f1.multiselect("Performance Quadrant", options=quadrant_opts, default=quadrant_opts)
        min_orders = f2.slider("Minimum Orders", 10, 500, 50, step=10)

    filtered = seller_df[
        (seller_df["quadrant"].isin(quadrant_filter)) &
        (seller_df["total_orders"] >= min_orders)
    ]

    st.caption(f"Showing {len(filtered):,} sellers")

    col_scat, col_list = st.columns([3, 2])

    with col_scat:
        with st.container(border=True):
            st.subheader("Performance Quadrant Map")
            if review_col:
                fig_q = px.scatter(
                    filtered,
                    x=late_col, y=review_col,
                    size="total_gmv", color="quadrant",
                    hover_name="seller_id",
                    labels={late_col: "Late Rate (%)", review_col: "Avg Review Score"},
                    size_max=40,
                )
                fig_q.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_q, use_container_width=True)
            else:
                st.warning("Review score column not found in seller data.")

    with col_list:
        with st.container(border=True):
            st.subheader("High Risk Sellers")
            display_cols = ["seller_id", late_col, "total_orders", "total_gmv", "quadrant"]
            if review_col:
                display_cols.insert(2, review_col)
            display_cols = [c for c in display_cols if c in filtered.columns]
            st.dataframe(
                filtered[display_cols].sort_values(late_col, ascending=False).head(50),
                hide_index=True,
                use_container_width=True,
            )


elif page == "Geographic Analysis":
    st.header("Geographic Logistics Analysis")

    # Detect columns
    state_col   = "customer_state" if "customer_state" in state_df.columns else state_df.columns[0]
    late_col    = "late_rate_pct"   if "late_rate_pct"  in state_df.columns else "late_rate"
    freight_col = next((c for c in state_df.columns if "freight" in c.lower()), None)
    orders_col  = "total_orders"    if "total_orders"   in state_df.columns else None

    col_bar, col_scatter = st.columns(2)

    with col_bar:
        with st.container(border=True):
            st.subheader("Late Rate by State")
            fig_s = px.bar(
                state_df.sort_values(late_col),
                x=late_col, y=state_col,
                orientation="h",
                color=late_col,
                color_continuous_scale="Reds",
                labels={late_col: "Late Rate (%)", state_col: "State"},
            )
            fig_s.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
            st.plotly_chart(fig_s, use_container_width=True)

    with col_scatter:
        with st.container(border=True):
            st.subheader("Freight Cost vs. Late Rate")
            if freight_col:
                fig_fr = px.scatter(
                    state_df,
                    x=freight_col, y=late_col,
                    text=state_col,
                    size=orders_col if orders_col else None,
                    color=late_col,
                    color_continuous_scale="RdYlGn_r",
                    labels={freight_col: "Avg Freight Cost", late_col: "Late Rate (%)"},
                )
                fig_fr.update_traces(textposition="top center")
                fig_fr.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
                st.plotly_chart(fig_fr, use_container_width=True)
            else:
                st.warning("Freight cost column not found in state data.")
                st.dataframe(state_df, hide_index=True, use_container_width=True)



elif page == "Power BI Dashboard":
    st.header("Power BI Dashboard")
    st.caption("Olist Delivery Performance Audit — exported from Power BI")

    import glob
    image_files = sorted(glob.glob("assets/dashboard.png") + glob.glob("assets/dashboard_*.jpg"))

    if not image_files:
        st.info(
            "No dashboard images found."
            "**How to add your Power BI dashboard:**"
            "1. In Power BI, go to **File → Export → Export to PDF**, then convert pages to PNG"
            "   — or right-click any visual → **Copy → Copy as image**"
            "2. Save the images as ,  etc."
            "3. Place them in an  folder in your project root"
            "4. Reload the app",
            icon="📊"
        )
    else:
        for i, img_path in enumerate(image_files, 1):
            
            st.image(img_path, use_container_width=True)
            if i < len(image_files):
                st.divider()


elif page == "Ask the Data":
    st.header("AI Data Assistant")
    st.caption("Natural language queries grounded in the Olist audit data.")

    if not groq_key:
        st.warning("⚠️ Groq API key not found. Add GROQ_API_KEY to your `.env` or Streamlit Secrets.", icon="🔑")

    # Suggested questions
    suggestions = [
        "Which state has the worst late delivery rate?",
        "How many sellers are in the critical quadrant?",
        "Which month had the highest late rate?",
        "What happens to reviews when delivery is 7+ days late?",
    ]
    cols = st.columns(4)
    for i, s in enumerate(suggestions):
        if cols[i].button(s, use_container_width=True):
            st.session_state.setdefault("messages", [])
            st.session_state.messages.append({"role": "user", "content": s})

    st.divider()

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about sellers, states, delay trends..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate response for last unanswered user message
    msgs = st.session_state.messages
    if msgs and msgs[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                answer = ask_groq([{"role": m["role"], "content": m["content"]} for m in msgs])
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})