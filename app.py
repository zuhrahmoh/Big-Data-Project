"""
Streamlit dashboard for delay cause attribution and airport clusters.

Dependencies: streamlit, pandas, plotly
Run from this directory:  streamlit run app.py

Precompute files by running notebook 05_dashboard_data_prep.ipynb (writes under `dashboard_data/`).
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dashboard_data"

CAUSES = [
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
]
CAUSE_LABELS = {
    "CarrierDelay": "Carrier",
    "WeatherDelay": "Weather",
    "NASDelay": "NAS",
    "SecurityDelay": "Security",
    "LateAircraftDelay": "Late aircraft",
}
CAUSE_COLORS = {
    "CarrierDelay": "#1f77b4",
    "WeatherDelay": "#ff7f0e",
    "NASDelay": "#2ca02c",
    "SecurityDelay": "#d62728",
    "LateAircraftDelay": "#9467bd",
}


@st.cache_data
def load_tables() -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    mapping = {
        "airline": "dashboard_airline_summary.csv",
        "airport": "dashboard_airport_summary.csv",
        "monthly": "dashboard_monthly_summary.csv",
        "seasonal": "dashboard_seasonal_summary.csv",
        "cluster": "dashboard_cluster_summary.csv",
        "centroids": "dashboard_cluster_centroids.csv",
        "clusters_scatter": "airport_clusters.csv",
    }
    for key, name in mapping.items():
        p = ROOT / name
        if p.exists():
            out[key] = pd.read_csv(p)
        else:
            out[key] = pd.DataFrame()
    return out


def cause_totals_from_airline(air: pd.DataFrame) -> pd.Series:
    if len(air) == 0:
        return pd.Series(0.0, index=list(CAUSES))
    cols = [f"total_{c}" for c in CAUSES if f"total_{c}" in air.columns]
    s = air[cols].sum()
    return s.rename({f"total_{c}": c for c in CAUSES})


def main() -> None:
    st.set_page_config(page_title="Flight delay attribution", layout="wide")
    data = load_tables()

    missing = [
        n
        for n in (
            "dashboard_airline_summary.csv",
            "dashboard_airport_summary.csv",
            "dashboard_monthly_summary.csv",
            "dashboard_seasonal_summary.csv",
        )
        if not (ROOT / n).exists()
    ]
    if missing:
        st.error("Missing dashboard data files: " + ", ".join(missing))
        st.info("Run `05_dashboard_data_prep.ipynb` in this folder, then refresh.")
        st.stop()

    air = data["airport"]
    ap_o = air[air["role"] == "Origin"] if "role" in air.columns else air
    ap_d = air[air["role"] == "Dest"] if "role" in air.columns else pd.DataFrame()

    st.sidebar.header("Filters")
    d_air = data["airline"]
    all_airlines = sorted(d_air["airline"].dropna().astype(str).unique().tolist()) if len(d_air) else []
    sel_airline = st.sidebar.selectbox("Airline", ["All"] + all_airlines)

    origins = sorted(ap_o["airport"].dropna().astype(str).unique().tolist()) if len(ap_o) else []
    sel_origin = st.sidebar.selectbox("Origin airport", ["All"] + origins)

    dests = sorted(ap_d["airport"].dropna().astype(str).unique().tolist()) if len(ap_d) else origins
    _ = st.sidebar.selectbox("Destination airport", ["All"] + dests)

    months = list(range(1, 13))
    sel_month = st.sidebar.selectbox("Month", ["All"] + [str(m) for m in months])

    _ = st.sidebar.selectbox("Season", ["All"] + ["Winter", "Spring", "Summer", "Autumn"])

    _ = st.sidebar.selectbox("Highlight delay cause", ["All"] + [CAUSE_LABELS[c] for c in CAUSES])

    page = st.sidebar.radio(
        "Page",
        ("Overview", "Delay causes", "Airports", "Clusters", "Key findings"),
    )

    d_month = data["monthly"]
    d_sea = data["seasonal"]
    d_clu = data["cluster"]
    d_cent = data["centroids"]
    d_scat = data["clusters_scatter"]

    air_f = d_air if sel_airline == "All" else d_air[d_air["airline"] == sel_airline]
    if len(air_f) == 0:
        air_f = d_air

    total_flights = int(air_f["flights"].sum())
    if air_f["pct_delayed"].notna().any():
        pct_del = float((air_f["flights"] * air_f["pct_delayed"]).sum() / max(total_flights, 1))
    else:
        pct_del = float("nan")
    if air_f["avg_arr_delay"].notna().any():
        avg_del = float((air_f["flights"] * air_f["avg_arr_delay"]).sum() / max(total_flights, 1))
    else:
        avg_del = float("nan")
    totals = cause_totals_from_airline(air_f)
    dom_cause = totals.idxmax() if totals.sum() > 0 else None
    n_ap = int(ap_o["airport"].nunique()) if len(ap_o) else 0
    n_clu = int(d_clu["cluster"].nunique()) if len(d_clu) and "cluster" in d_clu.columns else 0

    if page == "Overview":
        st.title("Overview")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Flights (filtered)", f"{total_flights:,}")
        c2.metric(
            "% arrival delayed",
            f"{100 * pct_del:.1f}%" if not math.isnan(pct_del) else "N/A",
        )
        c3.metric(
            "Avg arrival delay (min)",
            f"{avg_del:.1f}" if not math.isnan(avg_del) else "N/A",
        )
        c4.metric("Dominant cause", CAUSE_LABELS.get(dom_cause, "—") if dom_cause else "—")
        c5.metric("Origin airports", f"{n_ap:,}")
        c6.metric("Clusters", f"{n_clu}")

        left, right = st.columns(2)
        with left:
            if totals.sum() > 0:
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=[CAUSE_LABELS.get(c, c) for c in totals.index],
                            values=totals.values,
                            marker=dict(colors=[CAUSE_COLORS.get(c, "#888") for c in totals.index]),
                            hole=0.35,
                        )
                    ]
                )
                fig.update_layout(title="Attributed delay minutes (filtered slice)")
                st.plotly_chart(fig, use_container_width=True)
        with right:
            if len(d_month) and d_month["avg_arr_delay"].notna().any():
                fig2 = px.line(
                    d_month,
                    x="Month",
                    y="avg_arr_delay",
                    markers=True,
                    title="Avg arrival delay by month (network)",
                )
                if sel_month != "All":
                    fig2.add_vline(x=int(sel_month), line_dash="dash", line_color="gray")
                st.plotly_chart(fig2, use_container_width=True)
            elif len(d_month):
                st.caption("Avg arrival delay by month is not in the dashboard export (add it in upstream notebooks if needed).")

        if len(d_sea):
            heat = d_sea.set_index("Season")[[f"total_{c}" for c in CAUSES]].T
            heat.index = [CAUSE_LABELS.get(c.replace("total_", ""), c) for c in heat.index]
            fig3 = px.imshow(
                heat,
                labels=dict(x="Season", y="Cause", color="Minutes"),
                title="Season × cause (total minutes, network)",
                aspect="auto",
                color_continuous_scale="YlOrRd",
            )
            st.plotly_chart(fig3, use_container_width=True)

    elif page == "Delay causes":
        st.title("Delay cause explorer")
        top_n = st.slider("Top airlines by flights", 5, 25, 12)
        top_air = d_air.nlargest(top_n, "flights")
        melt = top_air.melt(
            id_vars=["airline"],
            value_vars=[f"total_{c}" for c in CAUSES],
            var_name="cause",
            value_name="minutes",
        )
        melt["cause"] = melt["cause"].str.replace("total_", "").map(lambda x: CAUSE_LABELS.get(x, x))
        fig = px.bar(
            melt,
            x="airline",
            y="minutes",
            color="cause",
            title="Attributed delay minutes by airline (stacked)",
            color_discrete_map={CAUSE_LABELS[c]: CAUSE_COLORS[c] for c in CAUSES},
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(d_month):
            mheat = d_month.set_index("Month")[[f"total_{c}" for c in CAUSES]].T
            mheat.index = [CAUSE_LABELS[c] for c in CAUSES]
            fig2 = px.imshow(
                mheat,
                labels=dict(x="Month", y="Cause", color="Minutes"),
                title="Month × cause (total minutes)",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig2, use_container_width=True)

        if len(d_month) and d_month["pct_delayed"].notna().any():
            fig3 = px.line(
                d_month,
                x="Month",
                y="pct_delayed",
                markers=True,
                title="Share of flights arrival-delayed by month",
            )
            st.plotly_chart(fig3, use_container_width=True)
        elif len(d_month):
            st.caption("Monthly delay rate not in dashboard export.")

        st.subheader("Airline table (filtered)")
        st.dataframe(air_f.sort_values("flights", ascending=False), use_container_width=True)

    elif page == "Airports":
        st.title("Airport analysis")
        ap_view = ap_o.copy()
        if sel_origin != "All":
            ap_view = ap_view[ap_view["airport"] == sel_origin]

        col1, col2 = st.columns(2)
        with col1:
            cause_for_top = st.selectbox("Rank origins by total minutes", CAUSES, format_func=lambda c: CAUSE_LABELS[c])
            topk = ap_o.nlargest(15, f"total_{cause_for_top}")
            fig = px.bar(
                topk,
                x=f"total_{cause_for_top}",
                y="airport",
                orientation="h",
                title=f"Top origins — {CAUSE_LABELS[cause_for_top]}",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            net = ap_o[[f"share_{c}" for c in CAUSES]].mean()
            if len(ap_view) == 1:
                row = ap_view.iloc[0]
                labels = [CAUSE_LABELS[c] for c in CAUSES]
                vals_a = [float(row[f"share_{c}"]) for c in CAUSES]
                vals_n = [float(net[f"share_{c}"]) for c in CAUSES]
                fig2 = go.Figure(
                    data=[
                        go.Bar(
                            name="This airport",
                            x=labels,
                            y=vals_a,
                            marker_color=[CAUSE_COLORS[c] for c in CAUSES],
                        ),
                        go.Bar(name="Network avg", x=labels, y=vals_n, marker_color="#bbbbbb"),
                    ]
                )
                fig2.update_layout(barmode="group", title="Share mix vs network")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.caption("Select a single origin in the sidebar to compare its cause mix to the network average.")

        pick = sel_origin if sel_origin != "All" else st.selectbox("Airport profile", ap_o.nlargest(20, "flights")["airport"])
        prof = ap_o[ap_o["airport"] == pick].iloc[0] if pick in ap_o["airport"].values else None
        if prof is not None:
            shares = {CAUSE_LABELS[c]: prof[f"share_{c}"] for c in CAUSES}
            fig3 = go.Figure(go.Bar(x=list(shares.keys()), y=list(shares.values()), marker_color=[CAUSE_COLORS[c] for c in CAUSES]))
            fig3.update_layout(title=f"Cause share mix — {pick} (origin)")
            st.plotly_chart(fig3, use_container_width=True)

    elif page == "Clusters":
        st.title("Clustering insights")
        if len(d_scat) == 0:
            st.warning("Run notebook 04 and 05 so `airport_clusters.csv` and dashboard cluster files exist.")
        else:
            fig = px.scatter(
                d_scat,
                x="pc1",
                y="pc2",
                color=d_scat["cluster"].astype(str),
                hover_name="Origin",
                hover_data=["FlightsCount", "DelayedFlightRate", "AvgArrDelay"],
                title="Airports (PCA of standardized delay features)",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)

        if len(d_cent):
            pivot = d_cent.pivot(index="metric", columns="cluster", values="value")
            fig2 = go.Figure()
            for col in pivot.columns.astype(str):
                fig2.add_trace(go.Bar(name=f"Cluster {col}", x=pivot.index.astype(str), y=pivot[col]))
            fig2.update_layout(barmode="group", title="Centroid profiles (original units)", xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)

        if len(d_clu):
            vc = d_clu.set_index("cluster")["n_airports"]
            fig3 = px.bar(x=vc.index.astype(str), y=vc.values, labels={"x": "Cluster", "y": "Airports"}, title="Cluster sizes")
            st.plotly_chart(fig3, use_container_width=True)

        if len(ap_o) and "cluster" in ap_o.columns:
            look = st.selectbox("Airport lookup", sorted(ap_o["airport"].unique()))
            hit = ap_o[ap_o["airport"] == look]
            if len(hit):
                r = hit.iloc[0]
                st.write(
                    f"**{look}** (origin): cluster **{r.get('cluster', '—')}**, "
                    f"flights {int(r['flights'])}, delay rate {100 * float(r['pct_delayed']):.1f}%"
                )

    else:
        st.title("Key findings")
        st.markdown(
            "Summaries below are driven by `dashboard_data/dashboard_cluster_summary.csv` "
            "and the other dashboard slices. Refine filters in the sidebar to scope KPIs on the Overview page."
        )
        if len(d_clu):
            for _, row in d_clu.iterrows():
                st.markdown(
                    f"- **Cluster {int(row['cluster'])}** — {int(row['n_airports'])} airports; "
                    f"dominant attributed type: **{row.get('dominant_delay_type', '')}**; "
                    f"examples: {row.get('sample_airports', '')}"
                )
        else:
            st.info("No cluster summary available yet.")


if __name__ == "__main__":
    main()
