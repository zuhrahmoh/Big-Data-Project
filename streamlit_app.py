"""Streamlit dashboard for Delay Cause Attribution in U.S. Airline Operations."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path("processed_data")

DELAY_CAUSE_COLORS = {
    "CarrierDelay": "#3b82f6",
    "WeatherDelay": "#06b6d4",
    "NASDelay": "#10b981",
    "SecurityDelay": "#a855f7",
    "LateAircraftDelay": "#ec4899",
}

CLUSTER_PALETTE = [
    "#3b82f6",
    "#ec4899",
    "#10b981",
    "#a855f7",
    "#06b6d4",
    "#db2777",
    "#84cc16",
    "#fde68a",
]

PLOTLY_TEMPLATE = "plotly_white"

CAUSE_LABELS = {
    "CarrierDelay": "Carrier",
    "WeatherDelay": "Weather",
    "NASDelay": "NAS",
    "SecurityDelay": "Security",
    "LateAircraftDelay": "Late Aircraft",
}

AIRLINE_NAMES = {
    "9E": "Endeavor Air",
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "EV": "ExpressJet",
    "F9": "Frontier Airlines",
    "G4": "Allegiant Air",
    "HA": "Hawaiian Airlines",
    "MQ": "Envoy Air",
    "NK": "Spirit Airlines",
    "OH": "PSA Airlines",
    "OO": "SkyWest Airlines",
    "UA": "United Airlines",
    "VX": "Virgin America",
    "WN": "Southwest Airlines",
    "XE": "ExpressJet (XE)",
    "YV": "Mesa Airlines",
    "YX": "Republic Airways",
}


st.set_page_config(
    page_title="U.S. Airline Delay Attribution",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
:root {
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --accent-green:  #10b981;
    --accent-purple: #a855f7;
    --accent-pink:   #ec4899;
}

/* Sidebar: tinted gradient overlay that works on both light and dark themes */
[data-testid="stSidebar"] {
    background-image: linear-gradient(
        180deg,
        rgba(59, 130, 246, 0.10) 0%,
        rgba(168, 85, 247, 0.10) 55%,
        rgba(236, 72, 153, 0.10) 100%
    );
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px;
}
[data-testid="stSidebar"] [role="radiogroup"] > label {
    padding: 8px 10px;
    border-radius: 10px;
    transition: background 0.15s ease;
    border-left: 3px solid transparent;
}
[data-testid="stSidebar"] [role="radiogroup"] > label p {
    font-size: 0.95rem;
    font-weight: 500;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    background: rgba(59, 130, 246, 0.14);
    border-left-color: var(--accent-blue);
}
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(
        90deg,
        rgba(59, 130, 246, 0.22),
        rgba(168, 85, 247, 0.20),
        rgba(236, 72, 153, 0.18)
    );
    border-left-color: var(--accent-purple);
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0 0 0.25rem 0;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple) 55%, var(--accent-pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: inherit;
    opacity: 0.65;
    font-size: 0.95rem;
    margin-bottom: 0.6rem;
}
.hero-blurb {
    background: linear-gradient(
        135deg,
        rgba(59, 130, 246, 0.10),
        rgba(168, 85, 247, 0.09),
        rgba(236, 72, 153, 0.09)
    );
    border: 1px solid rgba(168, 85, 247, 0.30);
    border-left: 4px solid var(--accent-purple);
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 1rem;
    color: inherit;
    line-height: 1.55;
}

.kpi-card {
    position: relative;
    background: rgba(127, 127, 127, 0.07);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 14px;
    padding: 18px 18px 14px 18px;
    color: inherit;
    overflow: hidden;
    height: 100%;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--card-accent, var(--accent-blue));
}
.kpi-card .kpi-label {
    color: inherit;
    opacity: 0.65;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}
.kpi-card .kpi-value {
    color: inherit;
    font-size: 1.85rem;
    font-weight: 700;
    margin-top: 4px;
    line-height: 1.1;
}
.kpi-card .kpi-sub {
    color: var(--card-accent, currentColor);
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 4px;
}

.section-card {
    background: rgba(127, 127, 127, 0.07);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 14px;
    padding: 18px 20px;
    color: inherit;
    height: 100%;
}
.section-card.accent-purple { border-left: 4px solid var(--accent-purple); }
.section-card.accent-cyan   { border-left: 4px solid var(--accent-cyan); }
.section-card h4 {
    margin: 0 0 10px 0;
    font-size: 1.05rem;
    color: inherit;
}
.section-card ol,
.section-card ul,
.section-card li,
.section-card p {
    color: inherit;
    opacity: 0.9;
}
.section-card a {
    color: var(--accent-cyan);
    text-decoration: none;
}
.section-card a:hover { text-decoration: underline; }

.pipeline {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    margin-top: 6px;
}
.pipeline .step {
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #ffffff;
    white-space: nowrap;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.18);
}
.pipeline .arrow {
    opacity: 0.55;
    font-weight: 700;
}
.pipeline .step.s1 { background: var(--accent-blue); }
.pipeline .step.s2 { background: var(--accent-cyan); }
.pipeline .step.s3 { background: var(--accent-green); }
.pipeline .step.s4 { background: var(--accent-purple); }
.pipeline .step.s5 { background: var(--accent-pink); }
.pipeline .step.s6 { background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)); }

.cause-chips { margin-top: 6px; }
.cause-chip {
    display: inline-block;
    padding: 4px 10px;
    margin: 3px 4px 3px 0;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #ffffff;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", color: str = "#3b82f6") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card" style="--card-accent: {color};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f"{sub_html}"
        f"</div>"
    )


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def md_bold_to_html(text: str) -> str:
    import re
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def render_insight_card(title: str, items: list[str], closing: str | None = None) -> None:
    bullets = "".join(
        f'<li style="margin-bottom:6px;">{md_bold_to_html(item)}</li>' for item in items
    )
    closing_html = (
        f'<p style="margin:12px 0 0 0; line-height:1.55;">{md_bold_to_html(closing)}</p>'
        if closing
        else ""
    )
    st.markdown(
        '<div class="hero-blurb" style="margin-top:0.5rem;">'
        f'<div style="font-weight:600; font-size:1rem; margin-bottom:10px;">{title}</div>'
        f'<ul style="margin:0; padding-left:18px; line-height:1.55;">{bullets}</ul>'
        f"{closing_html}"
        "</div>",
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_all() -> dict[str, pd.DataFrame]:
    return {
        "airline": load_csv("airline_delay_summary.csv"),
        "airport_clusters": load_csv("airport_clusters.csv"),
        "airport_profiles": load_csv("airport_delay_profiles.csv"),
        "airport_summary": load_csv("airport_delay_summary.csv"),
        "cluster_summary": load_csv("cluster_summary.csv"),
        "delay_cause": load_csv("delay_cause_summary.csv"),
        "seasonal": load_csv("seasonal_delay_summary.csv"),
    }


def first_present(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def format_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{int(round(float(value))):,}"


def format_float(value: float | int | None, digits: int = 2, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.{digits}f}{suffix}"


def format_pct(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value) * 100:.{digits}f}%"


def pretty_cause(name: str) -> str:
    return CAUSE_LABELS.get(name, name.replace("Delay", "").strip() or name)


def pretty_airline(code: str) -> str:
    name = AIRLINE_NAMES.get(code)
    return f"{code} – {name}" if name else code


def render_overview(data: dict[str, pd.DataFrame]) -> None:
    render_hero(
        "Delay Cause Attribution in U.S. Airline Operations",
        "COMP6940 — Big Data and Data Visualization Project",
    )

    st.markdown(
        '<div class="hero-blurb">'
        "Flight delays are a major operational challenge for airlines, airports, and passengers. "
        "This project analyses roughly <b>2 million</b> records from the U.S. Bureau of Transportation "
        "Statistics' <i>Carrier On-Time Performance</i> dataset to identify the dominant causes of delay "
        "and to understand how those causes vary across <b>airlines</b>, <b>airports</b>, and <b>time periods</b>."
        '<div class="cause-chips" style="margin-top:10px;">'
        '<span class="cause-chip" style="background:#3b82f6;">Carrier</span>'
        '<span class="cause-chip" style="background:#06b6d4;">Weather</span>'
        '<span class="cause-chip" style="background:#10b981;">NAS</span>'
        '<span class="cause-chip" style="background:#a855f7;">Security</span>'
        '<span class="cause-chip" style="background:#ec4899;">Late Aircraft</span>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    airline = data["airline"]
    delay_cause = data["delay_cause"]
    airport_summary = data["airport_summary"]
    airport_profiles = data["airport_profiles"]

    total_flights = None
    if not airport_summary.empty and "flights" in airport_summary.columns:
        total_flights = airport_summary["flights"].sum()
    elif not airport_profiles.empty and "FlightsCount" in airport_profiles.columns:
        total_flights = airport_profiles["FlightsCount"].sum()
    elif not airline.empty and "flights" in airline.columns:
        total_flights = airline["flights"].sum()

    avg_delay = None
    if not airport_profiles.empty and {"AvgArrDelay", "FlightsCount"}.issubset(airport_profiles.columns):
        weights = airport_profiles["FlightsCount"]
        if weights.sum() > 0:
            avg_delay = (airport_profiles["AvgArrDelay"] * weights).sum() / weights.sum()
    elif not airline.empty and {"mean_arr_delay", "flights"}.issubset(airline.columns):
        weights = airline["flights"]
        if weights.sum() > 0:
            avg_delay = (airline["mean_arr_delay"] * weights).sum() / weights.sum()

    delay_rate = None
    if not airport_summary.empty and {"delay_rate", "flights"}.issubset(airport_summary.columns):
        weights = airport_summary["flights"]
        if weights.sum() > 0:
            delay_rate = (airport_summary["delay_rate"] * weights).sum() / weights.sum()
    elif not airport_profiles.empty and {"DelayedFlightRate", "FlightsCount"}.issubset(airport_profiles.columns):
        weights = airport_profiles["FlightsCount"]
        if weights.sum() > 0:
            delay_rate = (airport_profiles["DelayedFlightRate"] * weights).sum() / weights.sum()
    elif not airline.empty and {"delay_rate", "flights"}.issubset(airline.columns):
        weights = airline["flights"]
        if weights.sum() > 0:
            delay_rate = (airline["delay_rate"] * weights).sum() / weights.sum()

    dominant_cause = None
    if not delay_cause.empty and "delay_cause" in delay_cause.columns:
        ranked = delay_cause.sort_values("share_of_attributed_delay", ascending=False)
        if not ranked.empty:
            top = ranked.iloc[0]
            dominant_cause = (
                pretty_cause(str(top["delay_cause"])),
                float(top.get("share_of_attributed_delay", float("nan"))),
            )

    dom_label, dom_share = (dominant_cause if dominant_cause is not None else ("—", None))
    dom_color = DELAY_CAUSE_COLORS.get(
        next((k for k, v in CAUSE_LABELS.items() if v == dom_label), ""),
        "#a855f7",
    )

    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            kpi_card("Flights analysed", format_int(total_flights), "U.S. domestic", "#3b82f6"),
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            kpi_card("Avg arrival delay", format_float(avg_delay, suffix=" min"), "weighted by flights", "#06b6d4"),
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            kpi_card("Delay rate", format_pct(delay_rate), "share of delayed flights", "#10b981"),
            unsafe_allow_html=True,
        )
    with cols[3]:
        sub = format_pct(dom_share) + " of attributed delay" if dom_share is not None else ""
        st.markdown(
            kpi_card("Dominant delay cause", dom_label, sub, dom_color),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.25, 1])
    with left:
        airlines_count = len(airline) if not airline.empty else "—"
        airports_count = len(airport_summary) if not airport_summary.empty else "—"
        st.markdown(
            f"""
<div class="section-card accent-purple">
  <h4>Methodology pipeline</h4>
  <div class="pipeline">
    <span class="step s1">Raw Data</span><span class="arrow">→</span>
    <span class="step s2">Cleaning</span><span class="arrow">→</span>
    <span class="step s3">Exploratory Analysis</span><span class="arrow">→</span>
    <span class="step s4">Delay Attribution</span><span class="arrow">→</span>
    <span class="step s5">Clustering</span><span class="arrow">→</span>
    <span class="step s6">Insights</span>
  </div>
  <ol style="margin-top:14px; line-height:1.55;">
    <li><b>Raw Data</b> — Carrier On-Time Performance dataset (~2M flights).</li>
    <li><b>Cleaning</b> — Handle missing values, format dates, validate delay fields.</li>
    <li><b>Exploratory Analysis</b> — Distributions of delays across airlines, airports, and time.</li>
    <li><b>Delay Attribution</b> — Aggregated analysis of carrier, weather, NAS, security and late-aircraft contributions.</li>
    <li><b>Clustering</b> — K-Means grouping of airports by delay-cause profile.</li>
    <li><b>Insights</b> — Visual analytics surfacing operational patterns.</li>
  </ol>
</div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
<div class="section-card accent-cyan">
  <h4>Dataset at a glance</h4>
  <ul style="margin:0; padding-left:18px; line-height:1.7;">
    <li><b>Source:</b> <a href="https://www.kaggle.com/datasets/mexwell/carrier-on-time-performance-dataset" target="_blank">Carrier On-Time Performance Dataset (Kaggle)</a></li>
    <li><b>Records:</b> ~2 million U.S. domestic flights</li>
    <li><b>Airlines covered:</b> {airlines_count}</li>
    <li><b>Airports profiled:</b> {airports_count}</li>
  </ul>
  <div class="cause-chips" style="margin-top:12px;">
    <span class="cause-chip" style="background:#3b82f6;">Carrier</span>
    <span class="cause-chip" style="background:#06b6d4;">Weather</span>
    <span class="cause-chip" style="background:#10b981;">NAS</span>
    <span class="cause-chip" style="background:#a855f7;">Security</span>
    <span class="cause-chip" style="background:#ec4899;">Late Aircraft</span>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )


def _airline_long(airline: pd.DataFrame) -> pd.DataFrame:
    cause_cols = [
        "carrier_delay",
        "weather_delay",
        "nas_delay",
        "security_delay",
        "late_aircraft_delay",
    ]
    available = [c for c in cause_cols if c in airline.columns]
    if not available or "Reporting_Airline" not in airline.columns:
        return pd.DataFrame()
    long = airline.melt(
        id_vars=["Reporting_Airline"],
        value_vars=available,
        var_name="cause",
        value_name="delay_minutes",
    )
    cause_map = {
        "carrier_delay": "CarrierDelay",
        "weather_delay": "WeatherDelay",
        "nas_delay": "NASDelay",
        "security_delay": "SecurityDelay",
        "late_aircraft_delay": "LateAircraftDelay",
    }
    long["cause"] = long["cause"].map(cause_map)
    long["cause_label"] = long["cause"].map(pretty_cause)
    long["airline_label"] = long["Reporting_Airline"].map(pretty_airline)
    return long


def render_delay_causes(data: dict[str, pd.DataFrame]) -> None:
    render_hero(
        "Delay Cause Findings",
        "How much of total delay each cause contributes, and how that varies by airline and time of year.",
    )

    delay_cause = data["delay_cause"].copy()
    airline = data["airline"].copy()
    seasonal = data["seasonal"].copy()

    st.subheader("Overall contribution of each delay cause")
    if not delay_cause.empty and {"delay_cause", "share_of_attributed_delay"}.issubset(delay_cause.columns):
        delay_cause["cause_label"] = delay_cause["delay_cause"].map(pretty_cause)
        fig = px.pie(
            delay_cause,
            names="cause_label",
            values="total_delay_minutes" if "total_delay_minutes" in delay_cause.columns else "share_of_attributed_delay",
            hole=0.55,
            color="delay_cause",
            color_discrete_map=DELAY_CAUSE_COLORS,
        )
        fig.update_traces(textposition="outside", textinfo="label+percent")
        fig.update_layout(
            showlegend=True,
            height=420,
            margin=dict(t=30, b=10, l=10, r=10),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Delay cause summary is unavailable.")

    st.markdown("---")

    st.subheader("Delay causes by airline")
    st.caption(
        "Shown: the **10 airlines with the highest cause-attributed delay per flight** "
        "(as ranked in `airline_delay_summary.csv`). Bars are total attributed delay minutes per cause."
    )
    long = _airline_long(airline)
    if long.empty:
        st.info("Airline-level cause data is unavailable.")
    else:
        rank_col = "cause_delay_per_flight" if "cause_delay_per_flight" in airline.columns else "flights"
        top_airlines = (
            airline.sort_values(rank_col, ascending=False)
            .head(10)["Reporting_Airline"]
            .tolist()
        )
        long = long[long["Reporting_Airline"].isin(top_airlines)]
        order = (
            long.groupby("Reporting_Airline")["delay_minutes"].sum().sort_values(ascending=False).index.tolist()
        )
        long["airline_label"] = pd.Categorical(
            long["airline_label"],
            categories=[pretty_airline(c) for c in order],
            ordered=True,
        )
        fig = px.bar(
            long,
            x="airline_label",
            y="delay_minutes",
            color="cause",
            color_discrete_map=DELAY_CAUSE_COLORS,
            labels={
                "airline_label": "Airline",
                "delay_minutes": "Total delay minutes",
                "cause": "Cause",
            },
        )
        fig.update_layout(
            barmode="stack",
            height=440,
            xaxis_tickangle=-30,
            margin=dict(t=30, b=10, l=10, r=10),
            legend_title_text="Delay cause",
            template=PLOTLY_TEMPLATE,
        )
        for trace in fig.data:
            trace.name = pretty_cause(trace.name)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("How delay causes vary through the year")
    if seasonal.empty or "time_grain" not in seasonal.columns:
        st.info("Seasonal summary is unavailable.")
    else:
        monthly = seasonal[seasonal["time_grain"] == "month"].copy()
        if not monthly.empty:
            monthly["month_num"] = pd.to_numeric(monthly["period"], errors="coerce")
            monthly = monthly.sort_values("month_num")
            month_names = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            ]
            monthly["month_label"] = monthly["month_num"].apply(
                lambda x: month_names[int(x) - 1] if pd.notna(x) and 1 <= int(x) <= 12 else str(x)
            )
            avg_cols = [c for c in monthly.columns if c.startswith("avg_") and c.replace("avg_", "") in DELAY_CAUSE_COLORS]
            if avg_cols:
                long_m = monthly.melt(
                    id_vars=["month_label", "month_num"],
                    value_vars=avg_cols,
                    var_name="cause",
                    value_name="avg_minutes",
                )
                long_m["cause"] = long_m["cause"].str.replace("avg_", "", regex=False)
                fig = px.line(
                    long_m.sort_values("month_num"),
                    x="month_label",
                    y="avg_minutes",
                    color="cause",
                    color_discrete_map=DELAY_CAUSE_COLORS,
                    markers=True,
                    labels={
                        "month_label": "Month",
                        "avg_minutes": "Average delay minutes per flight",
                        "cause": "Cause",
                    },
                )
                for trace in fig.data:
                    trace.name = pretty_cause(trace.name)
                fig.update_layout(
                    height=420,
                    margin=dict(t=30, b=10, l=10, r=10),
                    legend_title_text="Delay cause",
                    template=PLOTLY_TEMPLATE,
                )
                st.plotly_chart(fig, use_container_width=True)

        seasons = seasonal[seasonal["time_grain"] == "season"].copy()
        if not seasons.empty:
            avg_cols = [c for c in seasons.columns if c.startswith("avg_") and c.replace("avg_", "") in DELAY_CAUSE_COLORS]
            if avg_cols:
                long_s = seasons.melt(
                    id_vars=["period"],
                    value_vars=avg_cols,
                    var_name="cause",
                    value_name="avg_minutes",
                )
                long_s["cause"] = long_s["cause"].str.replace("avg_", "", regex=False)
                season_order = ["Winter", "Spring", "Summer", "Autumn"]
                long_s["period"] = pd.Categorical(long_s["period"], categories=season_order, ordered=True)
                long_s = long_s.sort_values("period")
                fig = px.bar(
                    long_s,
                    x="period",
                    y="avg_minutes",
                    color="cause",
                    barmode="group",
                    color_discrete_map=DELAY_CAUSE_COLORS,
                    labels={
                        "period": "Season",
                        "avg_minutes": "Average delay minutes per flight",
                        "cause": "Cause",
                    },
                )
                for trace in fig.data:
                    trace.name = pretty_cause(trace.name)
                fig.update_layout(
                    height=380,
                    margin=dict(t=30, b=10, l=10, r=10),
                    legend_title_text="Delay cause",
                    template=PLOTLY_TEMPLATE,
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    insights = []
    if not delay_cause.empty and "share_of_attributed_delay" in delay_cause.columns:
        ranked = delay_cause.sort_values("share_of_attributed_delay", ascending=False).head(2)
        if len(ranked) >= 2:
            insights.append(
                f"**{pretty_cause(ranked.iloc[0]['delay_cause'])}** and **{pretty_cause(ranked.iloc[1]['delay_cause'])}** "
                f"together account for "
                f"**{(ranked['share_of_attributed_delay'].head(2).sum()) * 100:.1f}%** of all attributed delay minutes — "
                "carrier and downstream knock-on effects dominate the delay landscape."
            )
    insights.append(
        "Cause composition varies meaningfully by airline: regional and ultra-low-cost carriers tilt toward "
        "**NAS** and **Late Aircraft** delays, while legacy carriers carry larger **Carrier** delay shares."
    )
    if not seasonal.empty and "time_grain" in seasonal.columns:
        monthly = seasonal[seasonal["time_grain"] == "month"]
        if not monthly.empty and "avg_LateAircraftDelay" in monthly.columns:
            insights.append(
                "Delays are markedly **seasonal** — average per-flight delays peak in the **summer** "
                "(Jun–Aug) and again in **December**, driven mainly by Late Aircraft and NAS effects."
            )
    render_insight_card("Key insights", insights)


def render_airport_insights(data: dict[str, pd.DataFrame]) -> None:
    render_hero(
        "Airport Insights",
        "Which airports experience the most delay, and what kinds of delays dominate at each.",
    )

    summary = data["airport_summary"].copy()
    profiles = data["airport_profiles"].copy()

    if summary.empty:
        st.info("Airport summary data is unavailable.")
        return

    airport_col = first_present(summary, ["Origin", "Airport", "IATA_CODE", "airport"])
    metric_col = first_present(summary, ["delay_rate", "avg_arr_delay", "AvgArrDelay", "total_delay"])
    if airport_col is None or metric_col is None:
        st.info("Could not detect airport identifier or delay metric columns.")
        return

    flights_col = first_present(summary, ["flights", "FlightsCount"])

    st.subheader("Top airports by delay")
    metric_options = {}
    if "delay_rate" in summary.columns:
        metric_options["Delay rate"] = "delay_rate"
    avg_options = [c for c in ["avg_arr_delay", "AvgArrDelay"] if c in summary.columns]
    if not avg_options:
        cause_avgs = [c for c in summary.columns if c.startswith("avg_") and c != "avg_SecurityDelay"]
        if cause_avgs:
            summary["avg_total_cause"] = summary[cause_avgs].sum(axis=1)
            metric_options["Avg cause delay (min/flight)"] = "avg_total_cause"
    else:
        metric_options["Avg arrival delay (min)"] = avg_options[0]
    total_cols = [c for c in summary.columns if c.startswith("total_") and c.endswith("Delay")]
    if total_cols:
        summary["total_attributed_delay"] = summary[total_cols].sum(axis=1)
        metric_options["Total attributed delay (min)"] = "total_attributed_delay"

    if not metric_options:
        metric_options[metric_col] = metric_col

    col_a, col_b = st.columns([1, 1])
    with col_a:
        metric_label = st.selectbox("Rank by", list(metric_options.keys()))
    with col_b:
        min_flights = 0
        if flights_col is not None:
            max_f = int(summary[flights_col].max())
            min_flights = st.slider(
                "Minimum flights",
                min_value=0,
                max_value=max_f,
                value=min(1000, max_f),
                step=100,
            )

    metric_field = metric_options[metric_label]
    filtered = summary.copy()
    if flights_col is not None:
        filtered = filtered[filtered[flights_col] >= min_flights]
    top_n = filtered.sort_values(metric_field, ascending=False).head(15)

    color_field = "dominant_cause" if "dominant_cause" in top_n.columns else None
    fig = px.bar(
        top_n.sort_values(metric_field, ascending=True),
        x=metric_field,
        y=airport_col,
        orientation="h",
        color=color_field,
        color_discrete_map=DELAY_CAUSE_COLORS if color_field else None,
        labels={metric_field: metric_label, airport_col: "Airport", "dominant_cause": "Dominant cause"},
    )
    fig.update_layout(height=520, margin=dict(t=30, b=10, l=10, r=10), template=PLOTLY_TEMPLATE)
    if color_field:
        for trace in fig.data:
            trace.name = pretty_cause(trace.name)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Drill into a specific airport")
    airports = sorted(summary[airport_col].dropna().unique().tolist())
    default_idx = airports.index("ATL") if "ATL" in airports else 0
    selected = st.selectbox("Airport", airports, index=default_idx)

    row = summary[summary[airport_col] == selected].iloc[0]

    avg_val = row.get("avg_arr_delay") if "avg_arr_delay" in summary.columns else row.get("AvgArrDelay")
    if avg_val is None or pd.isna(avg_val):
        cause_avgs = [c for c in summary.columns if c.startswith("avg_") and c != "avg_SecurityDelay"]
        if cause_avgs:
            avg_val = float(row[cause_avgs].sum())
    dominant = row.get("dominant_cause")
    dom_label_air = pretty_cause(str(dominant)) if pd.notna(dominant) else "—"
    dom_color_air = DELAY_CAUSE_COLORS.get(str(dominant), "#a855f7") if pd.notna(dominant) else "#a855f7"

    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            kpi_card(
                "Total flights",
                format_int(row.get(flights_col) if flights_col else None),
                "at this airport",
                "#3b82f6",
            ),
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            kpi_card("Avg delay", format_float(avg_val, suffix=" min"), "per flight", "#06b6d4"),
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            kpi_card("Delay rate", format_pct(row.get("delay_rate")), "share delayed", "#10b981"),
            unsafe_allow_html=True,
        )
    with cols[3]:
        st.markdown(
            kpi_card("Dominant cause", dom_label_air, "highest cause-attributed delay", dom_color_air),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    cause_avg_cols = [c for c in summary.columns if c.startswith("avg_") and c.replace("avg_", "") in DELAY_CAUSE_COLORS]
    if cause_avg_cols:
        cause_df = pd.DataFrame(
            {
                "cause": [c.replace("avg_", "") for c in cause_avg_cols],
                "avg_minutes": [float(row[c]) for c in cause_avg_cols],
            }
        )
        cause_df["cause_label"] = cause_df["cause"].map(pretty_cause)
        fig = px.bar(
            cause_df.sort_values("avg_minutes", ascending=True),
            x="avg_minutes",
            y="cause_label",
            orientation="h",
            color="cause",
            color_discrete_map=DELAY_CAUSE_COLORS,
            labels={"avg_minutes": "Avg delay minutes per flight", "cause_label": "Cause"},
            title=f"Delay cause profile – {selected}",
        )
        fig.update_layout(
            height=380,
            margin=dict(t=50, b=10, l=10, r=10),
            showlegend=False,
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Airport-level delay table")
    display_cols = [airport_col]
    for c in [flights_col, "delay_rate", "avg_arr_delay", "AvgArrDelay", "dominant_cause"]:
        if c and c in summary.columns and c not in display_cols:
            display_cols.append(c)
    display_cols += [c for c in summary.columns if c.startswith("avg_") and c not in display_cols]
    table = summary[display_cols].sort_values(
        "delay_rate" if "delay_rate" in display_cols else display_cols[1],
        ascending=False,
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    render_insight_card(
        "Why this matters",
        [
            "Airports differ in **both** how often delays occur and **what kinds** of delays they experience.",
            "Two airports with similar delay rates can have very different cause profiles, which motivates the "
            "clustering analysis on the next page.",
        ],
    )


def render_clustering(data: dict[str, pd.DataFrame]) -> None:
    render_hero(
        "Airport Clustering",
        "Airports grouped via K-Means on their delay-cause profiles "
        "(carrier, weather, NAS, security and late-aircraft shares plus delay rate).",
    )

    clusters = data["airport_clusters"].copy()
    cluster_summary = data["cluster_summary"].copy()

    if cluster_summary.empty:
        st.info("Cluster summary data is unavailable.")
        return

    cluster_summary["cluster_label"] = cluster_summary["cluster"].apply(lambda c: f"Cluster {int(c)}")

    cols = st.columns(2)
    with cols[0]:
        st.subheader("Airports per cluster")
        if "n_airports" in cluster_summary.columns:
            fig = px.bar(
                cluster_summary.sort_values("cluster"),
                x="cluster_label",
                y="n_airports",
                color="dominant_delay_type" if "dominant_delay_type" in cluster_summary.columns else None,
                color_discrete_map={
                    "LateAircraft": DELAY_CAUSE_COLORS["LateAircraftDelay"],
                    "Carrier": DELAY_CAUSE_COLORS["CarrierDelay"],
                    "Weather": DELAY_CAUSE_COLORS["WeatherDelay"],
                    "NAS": DELAY_CAUSE_COLORS["NASDelay"],
                    "Security": DELAY_CAUSE_COLORS["SecurityDelay"],
                },
                labels={"cluster_label": "Cluster", "n_airports": "# airports", "dominant_delay_type": "Dominant cause"},
                text="n_airports",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        st.subheader("Cluster scatter (PCA projection)")
        if not clusters.empty and {"pc1", "pc2", "cluster"}.issubset(clusters.columns):
            scatter_df = clusters.copy()
            scatter_df["cluster_label"] = scatter_df["cluster"].apply(lambda c: f"Cluster {int(c)}")
            cluster_order = [f"Cluster {int(c)}" for c in sorted(scatter_df["cluster"].unique())]
            cluster_color_map = {label: CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)] for i, label in enumerate(cluster_order)}
            fig = px.scatter(
                scatter_df,
                x="pc1",
                y="pc2",
                color="cluster_label",
                category_orders={"cluster_label": cluster_order},
                color_discrete_map=cluster_color_map,
                hover_name="Origin" if "Origin" in scatter_df.columns else None,
                size="FlightsCount" if "FlightsCount" in scatter_df.columns else None,
                labels={"pc1": "PC1", "pc2": "PC2", "cluster_label": "Cluster"},
            )
            fig.update_layout(height=400, margin=dict(t=30, b=10, l=10, r=10), template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("PCA coordinates not available.")

    st.markdown("---")

    st.subheader("Average delay-cause composition by cluster")
    share_cols = [c for c in cluster_summary.columns if c.startswith("centroid_") and c.endswith("Share")]
    if share_cols:
        long = cluster_summary.melt(
            id_vars=["cluster_label"],
            value_vars=share_cols,
            var_name="cause",
            value_name="share",
        )
        long["cause"] = long["cause"].str.replace("centroid_", "", regex=False).str.replace("Share", "Delay", regex=False)
        long["cause_label"] = long["cause"].map(pretty_cause)
        fig = px.bar(
            long,
            x="cluster_label",
            y="share",
            color="cause",
            barmode="group",
            color_discrete_map=DELAY_CAUSE_COLORS,
            labels={"cluster_label": "Cluster", "share": "Share of attributed delay", "cause": "Cause"},
        )
        for trace in fig.data:
            trace.name = pretty_cause(trace.name)
        fig.update_layout(
            height=440,
            margin=dict(t=30, b=10, l=10, r=10),
            legend_title_text="Delay cause",
            yaxis_tickformat=".0%",
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Airport ↔ cluster mapping")
    if clusters.empty:
        st.info("Airport-to-cluster mapping unavailable.")
    else:
        cluster_options = ["All"] + [f"Cluster {int(c)}" for c in sorted(clusters["cluster"].dropna().unique())]
        chosen = st.selectbox("Filter by cluster", cluster_options)
        view = clusters.copy()
        if chosen != "All":
            view = view[view["cluster"] == int(chosen.split(" ")[1])]
        display_cols = [c for c in ["Origin", "FlightsCount", "DelayedFlightRate", "AvgArrDelay", "cluster"] if c in view.columns]
        st.dataframe(
            view[display_cols].sort_values("cluster") if "cluster" in display_cols else view[display_cols],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    cluster_items: list[str] = []
    if "dominant_delay_type" in cluster_summary.columns:
        for _, r in cluster_summary.sort_values("cluster").iterrows():
            sample = str(r.get("sample_airports", ""))
            cluster_items.append(
                f"**Cluster {int(r['cluster'])}** ({int(r['n_airports'])} airports, dominant: "
                f"**{pretty_cause(str(r['dominant_delay_type']) + 'Delay')}**) — sample: {sample}"
            )
    closing = (
        "Overall, clusters represent **different operational patterns**: some are dominated by "
        "**Late Aircraft** delays (downstream knock-on effects at busy hubs), others by **Carrier** "
        "delays (operational issues at major mainline hubs), and a smaller group by **NAS / Weather** "
        "effects tied to congestion and regional weather exposure."
    )
    render_insight_card("Cluster interpretation", cluster_items, closing=closing)


def main() -> None:
    data = load_all()

    st.sidebar.markdown(
        '<div style="font-size:1.4rem; font-weight:700; '
        'background: linear-gradient(90deg,#3b82f6,#a855f7,#ec4899);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'background-clip:text; margin-bottom: 4px;">'
        "Flight Delay Atlas"
        "</div>"
        '<div style="opacity:0.7; font-size:0.85rem; margin-bottom: 14px;">'
        "Delay Cause Attribution in U.S. Airline Operations"
        "</div>",
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio(
        "Navigate",
        ["Project Overview", "Delay Cause Findings", "Airport Insights", "Airport Clustering"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown(
        '<hr style="margin: 18px 0; border: none; height:1px; '
        'background: linear-gradient(90deg, transparent, rgba(148,163,184,0.45), transparent);" />',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div style="font-size:0.8rem; opacity:0.85; line-height:1.55;">'
        "<b>COMP6940 Project</b><br>"
        "Big Data &amp; Data Visualization<br>"
        '<span style="opacity:0.65;">Data: Carrier On-Time Performance (BTS / Kaggle)</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    if page == "Project Overview":
        render_overview(data)
    elif page == "Delay Cause Findings":
        render_delay_causes(data)
    elif page == "Airport Insights":
        render_airport_insights(data)
    elif page == "Airport Clustering":
        render_clustering(data)


if __name__ == "__main__":
    main()
