import pandas as pd
import numpy as np
import sqlite3
import warnings
warnings.filterwarnings("ignore")

print("=" * 55)
print("  STEP 1: EXTRACT — Reading CSV files")
print("=" * 55)

df1 = pd.read_csv("Indias_Electricity_Consumption_Dataset.csv", index_col=0)
df2 = pd.read_csv("india_monthly_electricity.csv")
print(f"Dataset 1 loaded: {df1.shape[0]} rows x {df1.shape[1]} columns")
print(f"Dataset 2 loaded: {df2.shape[0]} rows x {df2.shape[1]} columns")

print("\n" + "=" * 55)
print("  STEP 2: TRANSFORM — Cleaning Dataset 1")
print("=" * 55)

df1["Dates"] = pd.to_datetime(df1["Dates"])

# Drop unusable/non-state columns
df1.drop(columns=["Pondy", "Tripura", "Essar steel"], inplace=True)
print("Dropped: Pondy, Tripura, Essar steel")

# Merge DD + DNH
df1["Dadra & Daman"] = df1["DD"].fillna(0) + df1["DNH"].fillna(0)
df1.drop(columns=["DD", "DNH"], inplace=True)
print("Merged DD + DNH -> Dadra & Daman")

# Fill missing values with median
state_cols = [c for c in df1.columns if c not in ["Dates", "Total Consumption"]]
for col in state_cols:
    if df1[col].isnull().any():
        df1[col].fillna(df1[col].median(), inplace=True)
print("Filled missing values with column medians")

# Recalculate total
df1["Total Consumption"] = df1[state_cols].sum(axis=1)

# Add time features
df1["Year"]       = df1["Dates"].dt.year
df1["Month"]      = df1["Dates"].dt.month
df1["Month_Name"] = df1["Dates"].dt.strftime("%b")

# Wide -> Long (melt)
df1_long = df1.melt(
    id_vars=["Dates", "Year", "Month", "Month_Name"],
    value_vars=state_cols,
    var_name="State",
    value_name="Consumption_MU"
).rename(columns={"Dates": "Date"})

print(f"Wide -> Long complete: {len(df1_long):,} rows")

print("\n" + "=" * 55)
print("  STEP 3: TRANSFORM — Cleaning Dataset 2")
print("=" * 55)

df2.drop(columns=["Country", "Country code"], inplace=True)
df2["Date"]  = pd.to_datetime(df2["Date"])
df2["Year"]  = df2["Date"].dt.year
df2["Month"] = df2["Date"].dt.month

# Total generation per state per month
df2_gen = df2[
    (df2["Category"] == "Electricity generation") &
    (df2["Subcategory"] == "Total") &
    (df2["Variable"] == "Total Generation") &
    (df2["Unit"] == "GWh")
][["Date","Year","Month","State","State code","State type","Value","YoY % change"]].copy()
df2_gen.rename(columns={"Value": "Generation_GWh", "YoY % change": "YoY_pct"}, inplace=True)

# Fuel-wise generation
df2_fuel = df2[
    (df2["Category"] == "Electricity generation") &
    (df2["Subcategory"] == "Fuel") &
    (df2["Variable"].isin(["Coal","Solar","Wind","Hydro","Nuclear","Bioenergy"])) &
    (df2["Unit"] == "GWh")
][["Date","Year","Month","State","State code","Variable","Value"]].copy()
df2_fuel.rename(columns={"Variable": "Fuel_Type", "Value": "Generation_GWh"}, inplace=True)

# Emissions
df2_emit = df2[
    (df2["Category"] == "Power sector emissions") &
    (df2["Subcategory"] == "Total") &
    (df2["Variable"] == "Total emissions") &
    (df2["Unit"] == "ktCO2")
][["Date","Year","Month","State","State code","Value"]].rename(columns={"Value":"Emissions_ktCO2"})

df2_co2i = df2[
    (df2["Category"] == "Power sector emissions") &
    (df2["Subcategory"] == "CO2 intensity") &
    (df2["Unit"] == "gCO2/kWh")
][["Date","Year","Month","State","State code","Value"]].rename(columns={"Value":"CO2_Intensity"})

df2_emissions = df2_emit.merge(df2_co2i, on=["Date","Year","Month","State","State code"], how="left")

print(f"Generation table:  {len(df2_gen):,} rows")
print(f"Fuel table:        {len(df2_fuel):,} rows")
print(f"Emissions table:   {len(df2_emissions):,} rows")

print("\n" + "=" * 55)
print("  STEP 4: LOAD — Building SQLite Database")
print("=" * 55)

conn = sqlite3.connect("india_energy.db")
for t in ["dim_states","fact_daily_consumption","fact_monthly_generation","fact_fuel_generation","fact_emissions"]:
    conn.execute(f"DROP TABLE IF EXISTS {t}")

df2_gen[["State","State code","State type"]].drop_duplicates().to_sql("dim_states", conn, if_exists="replace", index=False)
df1_long[["Date","State","Year","Month","Consumption_MU"]].to_sql("fact_daily_consumption", conn, if_exists="replace", index=False)
df2_gen[["Date","State","State code","Year","Month","Generation_GWh","YoY_pct"]].to_sql("fact_monthly_generation", conn, if_exists="replace", index=False)
df2_fuel[["Date","State","State code","Year","Month","Fuel_Type","Generation_GWh"]].to_sql("fact_fuel_generation", conn, if_exists="replace", index=False)
df2_emissions[["Date","State","State code","Year","Month","Emissions_ktCO2","CO2_Intensity"]].to_sql("fact_emissions", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Database 'india_energy.db' created with 5 tables:")
print("  - dim_states")
print("  - fact_daily_consumption  (118,624 rows)")
print("  - fact_monthly_generation (2,937 rows)")
print("  - fact_fuel_generation    (17,476 rows)")
print("  - fact_emissions          (2,937 rows)")
print("\nETL COMPLETE! Run sql_analysis.py next.")
