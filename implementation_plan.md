# COMP6940 Project Implementation Plan
## Delay Cause Attribution in U.S. Airline Operations

---

## 1. Project Direction

We will **reuse the previous project’s pipeline** but **reframe the objective**:

From:
> Predicting whether a flight is delayed

To:
> Explaining *why* delays happen and grouping airports by delay behavior

Core pillars:
- Delay cause attribution (MAIN ANALYSIS)
- Airport clustering using K-Means (MAIN ML COMPONENT)
- Clean, strong visualizations (EDA + dashboard)
- Streamlit dashboard for presentation

We will **NOT use XGBoost modeling as a core component**

---

## 2. Notebook-Level Implementation (CLEAR KEEP / ADD / REMOVE)

---

# 🔹 Notebook 1: `01_data_cleaning_preprocessing.ipynb`

## Goal
Produce a clean, feature-rich dataset used across the entire project

---

## ✅ KEEP (almost everything)
- Missing value handling (delay columns → fill with 0)
- Dropping empty columns
- `FlightDate` conversion to datetime
- Time conversion (HHMM → usable format)
- State cleaning / normalization
- Keeping negative delay values (early arrivals)

---

## ➕ ADD

### Time-based features
```python
Year
Quarter
Month
DayOfWeek
Season
```

### Delay indicators
```python
IsArrivalDelayed = (ArrDelay > 0)
IsDepartureDelayed = (DepDelay > 0)
```

### Delay aggregation
```python
TotalCauseDelay = CarrierDelay + WeatherDelay + NASDelay + SecurityDelay + LateAircraftDelay
```

### Binary flags (optional for analysis)
```python
HasCarrierDelay
HasWeatherDelay
HasNASDelay
HasSecurityDelay
HasLateAircraftDelay
```

### Other useful features
```python
Route = Origin + "-" + Dest
DepHour
ArrHour
```

---

## ❌ REMOVE
- Nothing significant

---

## Output
```text
cleaned_flight_data.csv
```

---

# 🔹 Notebook 2: `02_exploratory_analysis.ipynb`

## Goal
Understand patterns and guide the main analysis

---

## ✅ KEEP
- Monthly delay trends
- Airline comparisons
- Airport/state-level patterns
- Arrival vs departure delay relationships
- Correlation heatmap

---

## ➕ ADD
- Clear narrative flow:
  1. How big is the dataset?
  2. How common are delays?
  3. When do delays occur?
  4. Which airlines/airports are most affected?

- Add short insight text under each plot

---

## ❌ REMOVE / REDUCE
- Redundant plots
- Generic visuals not tied to delays
- Overly descriptive stats with no insight

---

## Charts to include
- Monthly average arrival delay
- Monthly delayed flight counts
- Delay by day of week
- Delay by hour of day
- Top 10 airlines by delay
- Top 10 airports by delay
- Correlation heatmap

---

## Reuse Level
~60–70% (needs restructuring, not rewriting)

---

# 🔹 Notebook 3: `03_delay_cause_attribution.ipynb`
*(Refactored from `delay_feature_analysis.ipynb`)*

---

## Goal
**THIS IS THE CORE NOTEBOOK**

Explain:
- Which delay causes dominate
- How delay causes vary across airlines, airports, and time

---

## ✅ KEEP
- All delay columns:
```text
CarrierDelay
WeatherDelay
NASDelay
SecurityDelay
LateAircraftDelay
```

- Any calculations already using these

---

## ➕ ADD (CRITICAL)

### A. Overall attribution
- Total delay minutes by cause
- % contribution of each cause

---

### B. By Airline
Group by airline:
- Avg delay per cause
- Total delay per cause
- % contribution per cause

---

### C. By Airport
Group by `Origin`:
- Avg delay per cause
- Delay rate
- Dominant delay cause

---

### D. By Time
Group by:
- Month
- Season

Compute:
- Avg delay by cause
- Total delay by cause

---

### E. Optional (high-value)
- Route-level delay analysis

---

## ❌ REMOVE
- Binary logic:
```python
HasDelayX
```

- Prediction framing:
- “this predicts delay”
- classification-style conclusions

---

## Charts
- Stacked bar: delay causes by airline
- Stacked bar: delay causes by airport
- Heatmap: month vs delay cause
- Heatmap: season vs delay cause
- Top airports by each delay type
- Overall delay cause contribution chart

---

## Outputs
```text
delay_cause_summary.csv
airport_delay_summary.csv
airline_delay_summary.csv
seasonal_delay_summary.csv
```

---

## Reuse Level
~50% (logic reused, purpose transformed)

---

# 🔹 Notebook 4: `modeling.ipynb`

---

## ❌ REMOVE FROM MAIN PROJECT

This notebook is:
- supervised prediction (XGBoost)
- not part of proposal
- not required for grading

---

## ✅ OPTIONAL USE
- reference feature engineering ideas
- include as appendix only if needed

---

## Verdict
**DO NOT INCLUDE in core workflow**

---

# 🔹 Notebook 5: `04_airport_clustering.ipynb` (NEW)

---

## Goal
Implement **K-Means clustering of airports**

---

## ➕ ADD (ENTIRE NOTEBOOK)

---

### Step 1: Aggregate airport features

Group by `Origin`:

```text
FlightsCount
DelayedFlightRate
AvgArrDelay
AvgCarrierDelay
AvgWeatherDelay
AvgNASDelay
AvgSecurityDelay
AvgLateAircraftDelay
CarrierShare
WeatherShare
NASShare
SecurityShare
LateAircraftShare
```

---

### Step 2: Filter small airports
- remove low-frequency airports
- e.g. FlightsCount > 5000

---

### Step 3: Standardize
```python
StandardScaler
```

---

### Step 4: Choose K
- Elbow method
- Silhouette score

Test:
```text
k = 2 to 8
```

---

### Step 5: Run KMeans

---

### Step 6: Interpret clusters

For each cluster:
- size
- average profile
- dominant delay type
- sample airports

Example labels:
- Weather-sensitive airports
- NAS congestion hubs
- Late aircraft propagation hubs
- Low-delay airports
- Carrier-driven delay airports

---

### Step 7: Visualization
- PCA (2D projection)

---

## Charts
- Elbow curve
- Silhouette plot
- PCA scatter (colored clusters)
- Cluster centroid comparison
- Cluster size distribution
- Representative airports table

---

## Outputs
```text
airport_delay_profiles.csv
airport_clusters.csv
cluster_summary.csv
```

---

# 🔹 Notebook 6: `05_dashboard_data_prep.ipynb` (NEW)

---

## Goal
Precompute all data needed for Streamlit

---

## ➕ ADD

Generate:
- airline summaries
- airport summaries
- monthly trends
- seasonal summaries
- cluster outputs

---

## Outputs
```text
dashboard_airline_summary.csv
dashboard_airport_summary.csv
dashboard_monthly_summary.csv
dashboard_seasonal_summary.csv
dashboard_cluster_summary.csv
dashboard_cluster_centroids.csv
```

---

# 3. Streamlit Dashboard Plan

---

## Sidebar Filters
- airline
- origin airport
- destination airport
- month
- season
- delay cause

---

## Page 1: Overview

### KPIs
- total flights
- % delayed
- avg delay
- dominant delay cause
- number of airports
- number of clusters

### Charts
- overall delay cause breakdown
- monthly trend line
- seasonal heatmap

---

## Page 2: Delay Cause Explorer

### Charts
- stacked bar: airline vs delay cause
- heatmap: month vs cause
- trend lines
- top airlines table

---

## Page 3: Airport Analysis

### Charts
- airport delay profile
- top airports by cause
- comparison vs average

---

## Page 4: Clustering Insights

### Charts
- PCA scatter
- cluster centroid comparison
- cluster size distribution
- airport lookup (cluster + explanation)

---

## Page 5: Key Findings

- top insights
- cluster interpretations
- conclusions

---

# 4. Visual Design

- clean layout
- consistent colors for delay types
- minimal text
- strong charts
- use Plotly where useful

---

# 5. What NOT to Spend Time On

- ❌ rebuilding XGBoost model
- ❌ excessive EDA
- ❌ extra ML models beyond KMeans
- ❌ overly complex dashboard
- ❌ backend engineering

---

# 6. Work Plan

## Phase 1
- finalize cleaning notebook
- refine EDA

## Phase 2
- build attribution notebook
- build clustering notebook

## Phase 3
- prepare dashboard data
- build Streamlit app

## Phase 4
- export visuals
- write report
- prepare presentation

---

# 7. Final Scope

## Core
- cleaning notebook
- EDA notebook
- delay attribution notebook
- clustering notebook
- dashboard + data prep

## Optional
- modeling notebook (appendix only)

---

# 8. Bottom Line

- reuse cleaning almost fully
- reuse EDA selectively
- refactor delay analysis into attribution
- drop predictive modeling
- add clustering as main ML
- present everything via Streamlit

This is the **fastest, cleanest, and most aligned approach** for your project.