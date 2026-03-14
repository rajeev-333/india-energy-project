import pandas as pd
import sqlite3

conn = sqlite3.connect("india_energy.db")

print("=" * 55)
print("  5 SQL QUERIES ON INDIA ENERGY DATABASE")
print("=" * 55)

# Q1: National demand by year
print("\nQ1: National Electricity Demand by Year")
print("-" * 45)
q1 = pd.read_sql("""
    SELECT Year,
           ROUND(SUM(Consumption_MU), 0) AS Total_MU,
           ROUND(AVG(Consumption_MU), 1) AS Avg_Daily_MU
    FROM   fact_daily_consumption
    GROUP  BY Year
    ORDER  BY Year
""", conn)
print(q1.to_string(index=False))

# Q2: Top 10 states
print("\nQ2: Top 10 States by All-Time Consumption")
print("-" * 45)
q2 = pd.read_sql("""
    SELECT State,
           ROUND(SUM(Consumption_MU), 0) AS Total_MU
    FROM   fact_daily_consumption
    GROUP  BY State
    ORDER  BY Total_MU DESC
    LIMIT  10
""", conn)
print(q2.to_string(index=False))

# Q3: Coal vs Solar vs Wind
print("\nQ3: Coal vs Solar vs Wind (GWh per Year)")
print("-" * 45)
q3 = pd.read_sql("""
    SELECT Year,
           Fuel_Type,
           ROUND(SUM(Generation_GWh), 0) AS Total_GWh
    FROM   fact_fuel_generation
    WHERE  Fuel_Type IN ('Coal', 'Solar', 'Wind')
    GROUP  BY Year, Fuel_Type
    ORDER  BY Year, Fuel_Type
""", conn)
print(q3.to_string(index=False))

# Q4: CO2 intensity
print("\nQ4: Top 10 Most Carbon-Intensive States (2024)")
print("-" * 45)
q4 = pd.read_sql("""
    SELECT State,
           ROUND(AVG(CO2_Intensity), 1) AS Avg_CO2_gCO2kWh
    FROM   fact_emissions
    WHERE  Year = 2024
      AND  CO2_Intensity > 0
    GROUP  BY State
    ORDER  BY Avg_CO2_gCO2kWh DESC
    LIMIT  10
""", conn)
print(q4.to_string(index=False))

# Q5: Monthly seasonality
print("\nQ5: Average Daily Consumption by Month")
print("-" * 45)
q5 = pd.read_sql("""
    SELECT Month,
           ROUND(AVG(daily_total), 1) AS Avg_Daily_National_MU
    FROM (
        SELECT Date, Month, SUM(Consumption_MU) AS daily_total
        FROM   fact_daily_consumption
        GROUP  BY Date, Month
    )
    GROUP  BY Month
    ORDER  BY Month
""", conn)
print(q5.to_string(index=False))

conn.close()
print("\nSQL ANALYSIS COMPLETE! Run dashboard.py next.")
