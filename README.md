# Delay Cause Attribution in U.S. Airline Operations

COMP6940 — Big Data and Data Visualization Project

This project analyses ~2 million U.S. domestic flight records from the
[Carrier On-Time Performance Dataset](https://www.kaggle.com/datasets/mexwell/carrier-on-time-performance-dataset)
to identify the dominant causes of flight delays and to study how those causes
vary across airlines, airports, and time periods. An unsupervised K-Means model
groups airports by their delay-cause profile, and a Streamlit dashboard
communicates the findings.

## Group members

- Dillon Carl
- Elena Panchoo
- Eysah Ali
- Zuhrah Mohammed

## Repository layout

```
.
├── 01_data_cleaning_preprocessing.ipynb   # Ingestion, cleaning, feature prep
├── 02_exploratory_analysis.ipynb          # EDA across airlines/airports/time
├── 03_delay_cause_attribution.ipynb       # Cause attribution & summaries
├── 04_airport_clustering.ipynb            # K-Means clustering of airports
├── streamlit_app.py                       # Streamlit results dashboard
├── processed_data/                        # CSV summaries consumed by the app
├── requirements.txt
└── README.md
```

The raw and cleaned full-size CSVs (`airline_2m.csv`, `cleaned_flight_data.csv`)
are not committed because of their size; they are produced/consumed by the
notebooks. The dashboard reads only from `processed_data/`.

## Environment

- Python 3.10+
- Jupyter Notebook (or VS Code / Cursor with the Jupyter extension)

### Python dependencies

Install everything with:

```bash
pip install -r requirements.txt
```

`requirements.txt` covers the dashboard and analysis stack
(`streamlit`, `pandas`, `plotly`, `numpy`, `matplotlib`, `seaborn`).
Notebook `04_airport_clustering.ipynb` additionally requires
[`scikit-learn`](https://scikit-learn.org/) for `KMeans`, `PCA`,
`StandardScaler` and `silhouette_score`:

```bash
pip install scikit-learn
```

## Reproducing the results

1. Download `airline_2m.csv` from the Kaggle dataset linked above and place it
   at the repository root.
2. Run the notebooks in order:
   1. `01_data_cleaning_preprocessing.ipynb` — produces `cleaned_flight_data.csv`.
   2. `02_exploratory_analysis.ipynb`
   3. `03_delay_cause_attribution.ipynb` — writes airline / delay-cause /
      seasonal summaries into `processed_data/`.
   4. `04_airport_clustering.ipynb` — writes airport profiles, cluster
      assignments and cluster summaries into `processed_data/`.

## Dashboard

The Streamlit dashboard is deployed and available at:

<https://flight-delay-project.streamlit.app/>

It is organised into four pages via the sidebar:

1. **Project Overview** — abstract, dataset summary, KPI cards and methodology.
2. **Delay Cause Findings** — overall cause breakdown, by-airline and seasonal views.
3. **Airport Insights** — top airports, per-airport drill-down and full table.
4. **Airport Clustering** — K-Means cluster sizes, PCA scatter, cluster
   composition and per-cluster interpretation.

The app reads only the CSVs in `processed_data/`.

## Data source

Carrier On-Time Performance Dataset (U.S. Bureau of Transportation Statistics),
mirrored on Kaggle:
<https://www.kaggle.com/datasets/mexwell/carrier-on-time-performance-dataset>.
