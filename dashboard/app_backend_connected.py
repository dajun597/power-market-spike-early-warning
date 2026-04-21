import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent if (BASE_DIR / 'src').exists() is False else BASE_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.backend.model_prediction import SpikePredictor


st.set_page_config(page_title="Spike Risk Dashboard", layout="wide")

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

st.title("Spike Risk Dashboard")
st.caption("Module 1: Trading-style Spike Risk Monitor")


# ======================
# 1. Read raw input data
# ======================
@st.cache_data
def load_raw_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    if "time" not in df.columns:
        raise KeyError("Uploaded CSV must contain 'time' column.")

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df


# ======================
# 2. Run backend prediction
# ======================
@st.cache_data(show_spinner=False)
def run_prediction(raw_df: pd.DataFrame) -> pd.DataFrame:
    predictor = SpikePredictor()
    pred_df = predictor.predict(raw_df)

    pred_df = pred_df.copy()
    pred_df["time"] = pd.to_datetime(pred_df["time"])
    pred_df = pred_df.sort_values("time").reset_index(drop=True)

    # unify names for dashboard display
    if "spike_precentage" in pred_df.columns:
        pred_df = pred_df.rename(columns={"spike_precentage": "probability"})

    if "is_spike" in pred_df.columns:
        pred_df = pred_df.rename(columns={"is_spike": "pred_spike"})

    if "risk_level" in pred_df.columns:
        pred_df["risk_level"] = pred_df["risk_level"].astype(str).str.upper()

    return pred_df


# ======================
# 3. Plot function
# ======================
def make_probability_chart(data: pd.DataFrame, title: str, show_text: bool = False):
    fig = go.Figure()

    color_map = {
        "LOW": "lightblue",
        "MODERATE": "green",
        "MEDIUM": "orange",
        "HIGH": "red",
        "VERY HIGH": "purple",
    }

    fig.add_trace(
        go.Scatter(
            x=data["time"],
            y=data["probability"],
            mode="lines",
            name="Spike Probability",
            line=dict(width=1.6, color="black"),
        )
    )

    levels = ["LOW", "MODERATE", "MEDIUM", "HIGH", "VERY HIGH"]
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
                        color=color_map[level],
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
            bgcolor="rgba(255,255,255,0.6)",
        ),
        margin=dict(l=18, r=10, t=30, b=18),
        title_font=dict(size=13),
        font=dict(size=10),
    )

    return fig


# ======================
# 4. Signal card
# ======================
def signal_card(label, value, value_size="28px"):
    st.markdown(
        f"""
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
    """,
        unsafe_allow_html=True,
    )


# ======================
# 5. Upload raw file
# ======================
uploaded_file = st.file_uploader("Upload your raw input dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        raw_df = load_raw_data(uploaded_file)
        df = run_prediction(raw_df)

        latest_time = df["time"].max()

        today_start = latest_time.normalize()
        week_start = latest_time - pd.Timedelta(days=6)
        month_start = latest_time - pd.Timedelta(days=29)

        today_df = df[(df["time"] >= today_start) & (df["time"] <= latest_time)].copy()
        week_df = df[(df["time"] >= week_start) & (df["time"] <= latest_time)].copy()
        month_df = df[(df["time"] >= month_start) & (df["time"] <= latest_time)].copy()

        latest_row = df.iloc[-1]

        left_col, right_col = st.columns([2, 1], gap="small")

        with left_col:
            st.markdown("### Spike Risk Charts")

            st.plotly_chart(
                make_probability_chart(today_df, "Today", show_text=True),
                use_container_width=True,
            )

            st.plotly_chart(
                make_probability_chart(week_df, "Week", show_text=False),
                use_container_width=True,
            )

            st.plotly_chart(
                make_probability_chart(month_df, "Month", show_text=False),
                use_container_width=True,
            )

        with right_col:
            st.markdown("### Live Signal Panel")
            signal_card("Current Spike Probability", f"{latest_row['probability']:.3f}")
            signal_card("Current Risk Level", f"{latest_row['risk_level']}")
            signal_card("Net Imbalance Volume", f"{latest_row['NetImbalanceVolume']:.2f}")

            st.markdown("---")
            st.markdown("#### Demand")
            if "demand_prediction" in latest_row.index:
                signal_card(
                    "Latest Demand Forecast",
                    f"{latest_row['demand_prediction']:.2f}",
                    value_size="24px",
                )
            else:
                signal_card("Latest Demand Forecast", "N/A", value_size="24px")

        with st.expander("Preview predicted dataset"):
            st.dataframe(df.tail(50), use_container_width=True)

    except Exception as e:
        st.error(str(e))
else:
    st.info("Please upload a CSV file first.")
