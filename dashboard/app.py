import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Spike Risk Dashboard", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 0.6rem;
    padding-bottom: 0.4rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

h1, h2, h3, h4 {
    margin-bottom: 0.15rem !important;
}

div[data-testid="stPlotlyChart"] {
    margin-top: -8px;
    margin-bottom: -8px;
}
</style>
""", unsafe_allow_html=True)

st.title("Spike Risk Dashboard")
st.caption("Module 1: Trading-style Spike Risk Monitor")


# ======================
# 1. Read data
# ======================
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # unify names
    if "y_prob" in df.columns:
        df = df.rename(columns={"y_prob": "probability"})
    if "y_pred" in df.columns:
        df = df.rename(columns={"y_pred": "pred_spike"})

    if "risk_level" in df.columns:
        df["risk_level"] = df["risk_level"].astype(str).str.upper()

    return df


# ======================
# 2. Plot function
# ======================
def make_probability_chart(data, title, show_text=False):
    fig = go.Figure()

    color_map = {
        "LOW": "green",
        "MODERATE": "gold",
        "MEDIUM": "orange",
        "HIGH": "red",
    }

    # main line
    fig.add_trace(
        go.Scatter(
            x=data["time"],
            y=data["probability"],
            mode="lines",
            name="Spike Probability",
            line=dict(width=1.6, color="black")
        )
    )

    # coloured points by risk level
    levels = ["LOW", "MODERATE", "MEDIUM", "HIGH"]
    for level in levels:
        part = data[data["risk_level"] == level].copy()
        if not part.empty:
            fig.add_trace(
                go.Scatter(
                    x=part["time"],
                    y=part["probability"],
                    mode="markers+text" if show_text else "markers",
                    name=level,
                    text=part["probability"].round(3) if show_text else None,
                    textposition="top center",
                    marker=dict(
                        size=7 if level != "LOW" else 5,
                        color=color_map[level]
                    ),
                )
            )

    fig.update_layout(
        title=title,
        height=240,
        xaxis_title=None,
        yaxis_title="Prob.",
        yaxis=dict(range=[0, 1]),
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            font=dict(size=9),
            bgcolor="rgba(255,255,255,0.6)"
        ),
        margin=dict(l=18, r=10, t=30, b=18),
        title_font=dict(size=13),
        font=dict(size=10)
    )

    return fig


# ======================
# 3. Signal card
# ======================
def signal_card(label, value, value_size="28px"):
    st.markdown(f"""
    <div style="
        padding: 12px 14px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px;
        margin-bottom: 10px;
        background: rgba(255,255,255,0.03);
    ">
        <div style="font-size:12px; color:#9aa4b2;">{label}</div>
        <div style="font-size:{value_size}; font-weight:700; color:white;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ======================
# 4. Upload file
# ======================
uploaded_file = st.file_uploader("Upload your dashboard dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    latest_time = df["time"].max()

    # split today / week / month
    today_start = latest_time.normalize()
    week_start = latest_time - pd.Timedelta(days=6)
    month_start = latest_time - pd.Timedelta(days=29)

    today_df = df[(df["time"] >= today_start) & (df["time"] <= latest_time)].copy()
    week_df = df[(df["time"] >= week_start) & (df["time"] <= latest_time)].copy()
    month_df = df[(df["time"] >= month_start) & (df["time"] <= latest_time)].copy()

    latest_row = df.iloc[-1]

    # ======================
    # 5. Layout
    # ======================
    left_col, right_col = st.columns([2, 1], gap="small")

    # ---------- Left: charts ----------
    with left_col:
        st.markdown("### Spike Risk Charts")

        st.plotly_chart(
            make_probability_chart(today_df, "Today", show_text=True),
            use_container_width=True
        )

        st.plotly_chart(
            make_probability_chart(week_df, "Week", show_text=False),
            use_container_width=True
        )

        st.plotly_chart(
            make_probability_chart(month_df, "Month", show_text=False),
            use_container_width=True
        )

    # ---------- Right: live signal panel ----------
    with right_col:
        st.markdown("### Live Signal Panel")

        signal_card("Current Spike Probability", f"{latest_row['probability']:.3f}")
        signal_card("Current Risk Level", f"{latest_row['risk_level']}")
        signal_card("Net Imbalance Volume", f"{latest_row['NetImbalanceVolume']:.2f}")

        st.markdown("---")
        st.markdown("#### Demand")

        signal_card("Latest Demand Forecast", f"{latest_row['demand_prediction']:.2f}", value_size="24px")

else:
    st.info("Please upload a CSV file first.")