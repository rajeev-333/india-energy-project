# India Electricity Analysis — End-to-End Data Engineering Project

An end-to-end data engineering project built on real Kaggle datasets covering
India's state-wise electricity consumption (2013–2024) and monthly generation,
capacity, and CO₂ emissions (2019–2025).

---

## Project Architecture

```
Raw CSVs (Kaggle)
      ↓
etl_pipeline.py     ← Extract → Transform → Load
      ↓
india_energy.db     ← SQLite Star Schema (5 tables)
      ↓
sql_analysis.py     ← 5 Business Questions answered in SQL
      ↓
dashboard.py        ← Interactive Plotly Dash Dashboard
```

---

## What This Project Covers

| Skill | Detail |
|---|---|
| ETL Pipeline | Cleaning, reshaping (wide→long), null handling |
| Database Design | SQLite Star Schema with 1 dim + 4 fact tables |
| SQL | GROUP BY, JOIN, Window aggregation, subqueries |
| Data Visualisation | Plotly Dash interactive dashboard |
| Real Data | 3,707 daily rows + 226,896 monthly rows |

---

## Datasets

Download both datasets from Kaggle and place them in the project root:

| File | Kaggle Link |
|---|---|
| `Indias_Electricity_Consumption_Dataset.csv` | [State-wise Daily Consumption](https://www.kaggle.com/datasets/twinkle0705/state-wise-power-consumption-in-india) |
| `india_monthly_electricity.csv` | [Monthly Electricity 2019–2025](https://www.kaggle.com/datasets/anoopjohny/comprehensive-india-electricity-data-2019-2025) |

> ⚠️ The CSV files are NOT included in this repo (too large for GitHub).
> You must download them from Kaggle manually.

---

## Folder Structure

```
india_energy_project/
├── Indias_Electricity_Consumption_Dataset.csv   ← download from Kaggle
├── india_monthly_electricity.csv                ← download from Kaggle
├── Dash_look.jpg                                 ← Visualisation of how dashboard would look
├── etl_pipeline.py                              ← Step 1: ETL
├── sql_analysis.py                              ← Step 2: SQL queries
├── dashboard.py                                 ← Step 3: Dashboard
├── requirements.txt                             ← Python dependencies
├── .gitignore
└── README.md
```

---

## How to Run

### 1. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/india_energy_project.git
cd india_energy_project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the datasets from Kaggle
Place both CSV files in the project root folder (same folder as the .py files).

### 4. Run ETL Pipeline (creates the database)
```bash
python etl_pipeline.py
```
This creates `india_energy.db` with 5 tables and 140,000+ rows.

### 5. Run SQL Analysis
```bash
python sql_analysis.py
```
Prints 5 business insights directly in the terminal.

### 6. Launch the Dashboard
```bash
python dashboard.py
```
Open your browser at **http://127.0.0.1:8050**

---

## The 5 Business Insights (SQL Results)

1. **National demand grew 3×** — from 421,623 MU (2013) to 1,228,437 MU (2024)
2. **Maharashtra is #1** — 1.65 million MU all-time, followed by UP and Gujarat
3. **Solar surged +189%** — from 92,535 GWh (2019) to 267,590 GWh (2024)
4. **Bihar most carbon-intensive** — 815 gCO₂/kWh average in 2024
5. **June is peak demand month** — 3,795 MU/day avg due to summer cooling load

---

## Database Schema

```
dim_states
(State, State code, State type)
          |
          |──── fact_daily_consumption   (Date, State, Year, Month, Consumption_MU)
          |──── fact_monthly_generation  (Date, State, Year, Month, Generation_GWh)
          |──── fact_fuel_generation     (Date, State, Year, Month, Fuel_Type, Generation_GWh)
          └──── fact_emissions           (Date, State, Year, Month, Emissions_ktCO2, CO2_Intensity)
```

---

## Tech Stack

- **Python 3.11+**
- **Pandas** — data manipulation and ETL
- **SQLite3** — lightweight database (built into Python)
- **Plotly + Dash** — interactive web dashboard
- **NumPy** — numerical operations

---

## Author

**Rajeev Gupta**  
M.Tech — Electrical Engineering | Power Systems  
[GitHub](https://github.com/YOUR_USERNAME)

---

## License

MIT License — free to use, modify, and distribute.
