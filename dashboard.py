import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
conn = sqlite3.connect("india_energy.db")
df_daily   = pd.read_sql("SELECT * FROM fact_daily_consumption", conn)
df_fuel    = pd.read_sql("SELECT * FROM fact_fuel_generation", conn)
df_emit    = pd.read_sql("SELECT * FROM fact_emissions", conn)
df_gen     = pd.read_sql("SELECT * FROM fact_monthly_generation", conn)
conn.close()

states  = sorted(df_daily["State"].unique())
years   = sorted(df_daily["Year"].unique())

app = Dash(__name__)

app.layout = html.Div([
    html.H1("India Electricity Dashboard",
            style={"textAlign":"center","fontFamily":"Arial","color":"#1f2937"}),
    html.P("Built with real Kaggle data | Datasets 1 & 2",
           style={"textAlign":"center","color":"#6b7280","fontFamily":"Arial"}),

    html.Div([
        html.Div([
            html.Label("Select Year Range:", style={"fontFamily":"Arial","fontWeight":"bold"}),
            dcc.RangeSlider(
                id="year-slider",
                min=int(df_daily["Year"].min()),
                max=int(df_daily["Year"].max()),
                step=1,
                value=[2015, 2024],
                marks={str(y): str(y) for y in years if y % 2 == 1},
                tooltip={"placement":"bottom"}
            )
        ], style={"width":"48%","display":"inline-block","padding":"0 20px"}),

        html.Div([
            html.Label("Select State:", style={"fontFamily":"Arial","fontWeight":"bold"}),
            dcc.Dropdown(
                id="state-dropdown",
                options=[{"label": s, "value": s} for s in states],
                value="Maharashtra",
                clearable=False
            )
        ], style={"width":"48%","display":"inline-block","padding":"0 20px"})
    ], style={"padding":"20px","backgroundColor":"#f9fafb","borderRadius":"8px","margin":"20px"}),

    html.Div([
        html.Div(dcc.Graph(id="chart-national"), style={"width":"50%","display":"inline-block"}),
        html.Div(dcc.Graph(id="chart-state"),    style={"width":"50%","display":"inline-block"}),
    ]),
    html.Div([
        html.Div(dcc.Graph(id="chart-fuel"),     style={"width":"50%","display":"inline-block"}),
        html.Div(dcc.Graph(id="chart-co2"),      style={"width":"50%","display":"inline-block"}),
    ])
], style={"backgroundColor":"#ffffff","maxWidth":"1400px","margin":"auto"})


@app.callback(
    Output("chart-national","figure"),
    Output("chart-state",   "figure"),
    Output("chart-fuel",    "figure"),
    Output("chart-co2",     "figure"),
    Input("year-slider",    "value"),
    Input("state-dropdown", "value")
)
def update_charts(year_range, state):
    y0, y1 = year_range

    # Chart 1: National annual demand
    nat = df_daily[(df_daily["Year"]>=y0) & (df_daily["Year"]<=y1)]
    nat_yr = nat.groupby("Year")["Consumption_MU"].sum().reset_index()
    fig1 = go.Figure(go.Scatter(
        x=nat_yr["Year"], y=(nat_yr["Consumption_MU"]/1e6).round(2),
        mode="lines+markers", fill="tozeroy", line=dict(width=3, shape="spline")
    ))
    fig1.update_layout(title="National Demand (million MU)",
                       xaxis_title="Year", yaxis_title="Million MU")

    # Chart 2: Selected state monthly trend
    st = df_daily[(df_daily["State"]==state) & (df_daily["Year"]>=y0) & (df_daily["Year"]<=y1)]
    st_mo = st.groupby(["Year","Month"])["Consumption_MU"].sum().reset_index()
    st_mo["Period"] = st_mo["Year"].astype(str) + "-" + st_mo["Month"].astype(str).str.zfill(2)
    fig2 = go.Figure(go.Scatter(
        x=st_mo["Period"], y=st_mo["Consumption_MU"].round(1),
        mode="lines", line=dict(width=2, color="#EF553B")
    ))
    fig2.update_layout(title=f"{state} — Monthly Consumption",
                       xaxis_title="Month", yaxis_title="MU")
    fig2.update_xaxes(tickangle=45, nticks=12)

    # Chart 3: Coal vs Solar vs Wind (indexed)
    fuel = df_fuel[(df_fuel["Fuel_Type"].isin(["Coal","Solar","Wind"])) &
                   (df_fuel["Year"]>=max(y0,2019)) & (df_fuel["Year"]<=y1)]
    fuel_yr = fuel.groupby(["Year","Fuel_Type"])["Generation_GWh"].sum().reset_index()
    pivot = fuel_yr.pivot(index="Year", columns="Fuel_Type", values="Generation_GWh")
    if len(pivot) > 0:
        base = pivot.iloc[0]
        indexed = (pivot / base * 100).reset_index()
        fig3 = go.Figure()
        colors = {"Coal":"#636EFA","Solar":"#FFA15A","Wind":"#00CC96"}
        dashes = {"Coal":"solid","Solar":"dot","Wind":"dash"}
        for fuel_type in ["Coal","Solar","Wind"]:
            if fuel_type in indexed.columns:
                fig3.add_trace(go.Scatter(
                    x=indexed["Year"], y=indexed[fuel_type].round(1),
                    mode="lines+markers", name=fuel_type,
                    line=dict(width=3, color=colors[fuel_type], dash=dashes[fuel_type])
                ))
        fig3.update_layout(title="Coal vs Solar vs Wind (Indexed)",
                           xaxis_title="Year", yaxis_title="Index (base year=100)")
    else:
        fig3 = go.Figure()
        fig3.update_layout(title="No fuel data in this range")

    # Chart 4: CO2 Intensity Top 10
    co2 = df_emit[(df_emit["Year"]>=y0) & (df_emit["Year"]<=y1) & (df_emit["CO2_Intensity"]>0)]
    co2_st = co2.groupby("State")["CO2_Intensity"].mean().reset_index().nlargest(10,"CO2_Intensity")
    co2_st = co2_st.sort_values("CO2_Intensity")
    fig4 = go.Figure(go.Bar(
        x=co2_st["CO2_Intensity"].round(1),
        y=co2_st["State"],
        orientation="h",
        marker_color=px.colors.sequential.Reds[2:][:len(co2_st)]
    ))
    fig4.update_layout(title=f"CO2 Intensity Top 10 ({y0}-{y1})",
                       xaxis_title="gCO2/kWh", yaxis_title="State")

    return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    print("Starting dashboard at http://127.0.0.1:8050")
    app.run(debug=False)
