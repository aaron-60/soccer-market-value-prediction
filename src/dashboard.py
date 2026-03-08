"""
Football Player Market Value Analysis - Interactive Dashboard
Built with Plotly Dash
"""
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input, dash_table

# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "processed", "powerbi")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
players = pd.read_csv(os.path.join(DATA, "players.csv"))
stats = pd.read_csv(os.path.join(DATA, "player_stats.csv"))
clubs = pd.read_csv(os.path.join(DATA, "clubs.csv"))
leagues = pd.read_csv(os.path.join(DATA, "leagues.csv"))
predictions = pd.read_csv(os.path.join(DATA, "predictions.csv"))

# Merge stats into players for richer tooltips
players = players.merge(stats, on="player_id", how="left")

# Country name fixes for plotly (plotly uses standard English country names)
COUNTRY_MAP = {
    "Turkiye": "Turkey", "Türkiye": "Turkey", "T\u00fcrkiye": "Turkey",
    "Korea, South": "South Korea", "Korea, North": "North Korea",
    "Cote d'Ivoire": "Ivory Coast", "Côte d'Ivoire": "Ivory Coast",
    "DR Congo": "Congo", "Congo DR": "Congo",
    "Cape Verde": "Cabo Verde",
    "St. Kitts & Nevis": "Saint Kitts and Nevis",
    "Trinidad and Tobago": "Trinidad and Tobago",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "North Macedonia": "Macedonia",
}
players["country_clean"] = players["nationality"].replace(COUNTRY_MAP)

# ---------------------------------------------------------------------------
# Pre-compute aggregations
# ---------------------------------------------------------------------------
# Country summary
country_agg = (
    players.groupby("country_clean")
    .agg(
        player_count=("player_id", "count"),
        total_value=("market_value", "sum"),
        avg_value=("market_value", "mean"),
        top_value=("market_value", "max"),
    )
    .reset_index()
    .rename(columns={"country_clean": "country"})
    .sort_values("player_count", ascending=False)
)

# Club summary (top 20)
club_agg = (
    players.groupby("current_club_name")
    .agg(
        total_value=("market_value", "sum"),
        player_count=("player_id", "count"),
        avg_value=("market_value", "mean"),
    )
    .reset_index()
    .sort_values("total_value", ascending=False)
    .head(20)
)

# Position breakdown
position_agg = (
    players[players["position"] != "Missing"]
    .groupby("position")
    .agg(count=("player_id", "count"), total_value=("market_value", "sum"))
    .reset_index()
)

# KPI values
total_players = len(players)
total_market_value = players["market_value"].sum()
avg_market_value = players["market_value"].mean()

# Most / Least valuable
most_valuable = players.nlargest(1, "market_value").iloc[0]
least_valuable = players[players["market_value"] > 0].nsmallest(1, "market_value").iloc[0]

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0e1117",
    "card": "#1a1f2e",
    "card_border": "#2d3548",
    "text": "#e0e0e0",
    "text_muted": "#8b95a5",
    "accent": "#4fc3f7",
    "accent2": "#81c784",
    "accent3": "#ffb74d",
    "accent4": "#e57373",
    "grid": "#1e2738",
}

POSITION_COLORS = {
    "Attack": "#e57373",
    "Midfield": "#4fc3f7",
    "Defender": "#81c784",
    "Defense": "#81c784",
    "Goalkeeper": "#ffb74d",
    "Unknown": "#90a4ae",
}

# ---------------------------------------------------------------------------
# Helper: format currency
# ---------------------------------------------------------------------------
def fmt_eur(val):
    if val >= 1e9:
        return f"\u20ac{val/1e9:.1f}B"
    if val >= 1e6:
        return f"\u20ac{val/1e6:.1f}M"
    if val >= 1e3:
        return f"\u20ac{val/1e3:.0f}K"
    return f"\u20ac{val:.0f}"


# ---------------------------------------------------------------------------
# Build figures
# ---------------------------------------------------------------------------

def make_map(position_filter="All"):
    df = players.copy()
    if position_filter != "All":
        df = df[df["position"] == position_filter]

    agg = (
        df.groupby("country_clean")
        .agg(
            player_count=("player_id", "count"),
            total_value=("market_value", "sum"),
            avg_value=("market_value", "mean"),
        )
        .reset_index()
        .rename(columns={"country_clean": "country"})
    )
    agg["value_label"] = agg["total_value"].apply(fmt_eur)
    agg["avg_label"] = agg["avg_value"].apply(fmt_eur)

    fig = px.scatter_geo(
        agg,
        locations="country",
        locationmode="country names",
        size="player_count",
        color="total_value",
        hover_name="country",
        hover_data={
            "player_count": True,
            "value_label": True,
            "avg_label": True,
            "total_value": False,
            "country": False,
        },
        color_continuous_scale="Viridis",
        size_max=40,
        projection="natural earth",
        labels={
            "player_count": "Players",
            "value_label": "Total Value",
            "avg_label": "Avg Value",
        },
    )
    fig.update_geos(
        bgcolor=COLORS["bg"],
        landcolor="#1a2332",
        oceancolor="#0a0f1a",
        lakecolor="#0a0f1a",
        coastlinecolor="#2d3548",
        countrycolor="#2d3548",
        showframe=False,
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        coloraxis_colorbar=dict(
            title="Total Value",
            tickformat=",.0s",
            tickprefix="\u20ac",
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=420,
    )
    return fig


def make_club_bar():
    fig = px.bar(
        club_agg,
        x="total_value",
        y="current_club_name",
        orientation="h",
        color="total_value",
        color_continuous_scale=["#1a237e", "#4fc3f7"],
        labels={"total_value": "Market Value", "current_club_name": "Club"},
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], size=11),
        yaxis=dict(autorange="reversed", gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"], tickformat=",.0s", tickprefix="\u20ac"),
        coloraxis_showscale=False,
        margin=dict(l=10, r=20, t=30, b=30),
        height=420,
        showlegend=False,
    )
    return fig


def make_position_donut():
    fig = px.pie(
        position_agg,
        values="count",
        names="position",
        hole=0.55,
        color="position",
        color_discrete_map=POSITION_COLORS,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont_size=12,
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        margin=dict(l=10, r=10, t=30, b=10),
        height=340,
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{total_players:,}</b><br>Players",
                x=0.5, y=0.5, font_size=16,
                font_color=COLORS["text"],
                showarrow=False,
            )
        ],
    )
    return fig


def make_prediction_scatter():
    sample = predictions.sample(min(3000, len(predictions)), random_state=42)
    fig = px.scatter(
        sample,
        x="market_value",
        y="predicted",
        color="position_group",
        hover_name="player_name",
        hover_data={"current_club_name": True, "age": True},
        opacity=0.6,
        color_discrete_map={
            "Attacker": "#e57373",
            "Defender": "#81c784",
            "Goalkeeper": "#ffb74d",
            "Unknown": "#90a4ae",
        },
        labels={
            "market_value": "Actual Value (\u20ac)",
            "predicted": "Predicted Value (\u20ac)",
            "position_group": "Position",
        },
    )
    # Perfect prediction line
    max_val = max(sample["market_value"].max(), sample["predicted"].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines",
            line=dict(color="#ffffff", dash="dash", width=1),
            name="Perfect Prediction",
            showlegend=True,
        )
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], size=11),
        xaxis=dict(gridcolor=COLORS["grid"], tickformat=",.0s", tickprefix="\u20ac"),
        yaxis=dict(gridcolor=COLORS["grid"], tickformat=",.0s", tickprefix="\u20ac"),
        margin=dict(l=10, r=10, t=30, b=30),
        height=340,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Football Player Market Value Analysis"

# KPI card style
def kpi_card(title, value, color=COLORS["accent"]):
    return html.Div(
        [
            html.Div(value, style={
                "fontSize": "28px", "fontWeight": "700", "color": color,
                "lineHeight": "1.2",
            }),
            html.Div(title, style={
                "fontSize": "12px", "color": COLORS["text_muted"],
                "marginTop": "4px", "textTransform": "uppercase",
                "letterSpacing": "1px",
            }),
        ],
        style={
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "8px",
            "padding": "20px",
            "textAlign": "center",
            "flex": "1",
            "minWidth": "180px",
        },
    )


def section_title(text):
    return html.H3(
        text,
        style={
            "color": COLORS["text"], "fontSize": "16px", "fontWeight": "600",
            "marginBottom": "12px", "marginTop": "0",
        },
    )


card_style = {
    "backgroundColor": COLORS["card"],
    "border": f"1px solid {COLORS['card_border']}",
    "borderRadius": "8px",
    "padding": "16px",
}

# Top 15 most valuable for the table
top_players_df = players.nlargest(15, "market_value")[
    ["player_name", "current_club_name", "age", "position", "sub_position",
     "nationality", "market_value", "peak_market_value"]
].copy()
top_players_df["market_value_fmt"] = top_players_df["market_value"].apply(fmt_eur)
top_players_df["peak_fmt"] = top_players_df["peak_market_value"].apply(fmt_eur)

# Bottom 10 (least valuable with value > 0)
bottom_players_df = players[players["market_value"] > 0].nsmallest(10, "market_value")[
    ["player_name", "current_club_name", "age", "position",
     "nationality", "market_value"]
].copy()
bottom_players_df["market_value_fmt"] = bottom_players_df["market_value"].apply(fmt_eur)

# Top predicted
top_predicted = predictions.nlargest(15, "predicted")[
    ["player_name", "current_club_name", "age", "position_group",
     "market_value", "predicted", "error_pct"]
].copy()
top_predicted["actual_fmt"] = top_predicted["market_value"].apply(fmt_eur)
top_predicted["predicted_fmt"] = top_predicted["predicted"].apply(fmt_eur)
top_predicted["error_fmt"] = top_predicted["error_pct"].apply(lambda x: f"{x:+.1f}%")


app.layout = html.Div(
    style={
        "backgroundColor": COLORS["bg"],
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', 'Roboto', sans-serif",
        "color": COLORS["text"],
        "padding": "24px",
    },
    children=[
        # Title
        html.H1(
            "Football Player Market Value Analysis",
            style={
                "textAlign": "center", "fontSize": "32px", "fontWeight": "700",
                "marginBottom": "6px", "color": "#ffffff",
            },
        ),
        html.P(
            "Interactive dashboard \u2014 31,078 players \u00b7 437 clubs \u00b7 44 leagues \u00b7 ML predictions",
            style={
                "textAlign": "center", "fontSize": "13px",
                "color": COLORS["text_muted"], "marginBottom": "24px",
            },
        ),

        # KPI Row
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
            children=[
                kpi_card("Total Players", f"{total_players:,}", COLORS["accent"]),
                kpi_card("Total Market Value", fmt_eur(total_market_value), COLORS["accent2"]),
                kpi_card("Avg Market Value", fmt_eur(avg_market_value), COLORS["accent3"]),
                kpi_card("Most Valuable", f"{most_valuable['player_name']}", COLORS["accent4"]),
                kpi_card("Highest Value", fmt_eur(most_valuable["market_value"]), "#ce93d8"),
            ],
        ),

        # Filter row
        html.Div(
            style={
                "display": "flex", "gap": "16px", "marginBottom": "24px",
                "alignItems": "center", "flexWrap": "wrap",
            },
            children=[
                html.Div([
                    html.Label("Filter by Position:", style={
                        "fontSize": "12px", "color": COLORS["text_muted"],
                        "marginBottom": "4px", "display": "block",
                    }),
                    dcc.Dropdown(
                        id="position-filter",
                        options=[{"label": "All Positions", "value": "All"}]
                        + [{"label": p, "value": p} for p in ["Attack", "Midfield", "Defense", "Goalkeeper"]],
                        value="All",
                        clearable=False,
                        style={"width": "200px", "backgroundColor": COLORS["card"], "color": "#000"},
                    ),
                ]),
                html.Div([
                    html.Label("League Tier:", style={
                        "fontSize": "12px", "color": COLORS["text_muted"],
                        "marginBottom": "4px", "display": "block",
                    }),
                    dcc.Dropdown(
                        id="tier-filter",
                        options=[{"label": "All Leagues", "value": "All"}]
                        + [{"label": t, "value": t} for t in ["Top 5", "Other"]],
                        value="All",
                        clearable=False,
                        style={"width": "200px", "backgroundColor": COLORS["card"], "color": "#000"},
                    ),
                ]),
            ],
        ),

        # Row 1: Map + Club Bar
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={**card_style, "flex": "3", "minWidth": "500px"},
                    children=[
                        section_title("Player Distribution by Nationality (Interactive Map)"),
                        dcc.Graph(id="world-map", config={"displayModeBar": False}),
                    ],
                ),
                html.Div(
                    style={**card_style, "flex": "2", "minWidth": "350px"},
                    children=[
                        section_title("Market Value by Club (Top 20)"),
                        dcc.Graph(id="club-bar", figure=make_club_bar(), config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),

        # Row 2: Position Donut + Prediction Scatter
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={**card_style, "flex": "1", "minWidth": "300px"},
                    children=[
                        section_title("Position Distribution"),
                        dcc.Graph(id="position-donut", figure=make_position_donut(), config={"displayModeBar": False}),
                    ],
                ),
                html.Div(
                    style={**card_style, "flex": "2", "minWidth": "450px"},
                    children=[
                        section_title("ML Prediction: Actual vs Predicted Market Value"),
                        dcc.Graph(id="pred-scatter", figure=make_prediction_scatter(), config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),

        # Row 3: Tables
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
            children=[
                # Most Valuable
                html.Div(
                    style={**card_style, "flex": "1", "minWidth": "450px"},
                    children=[
                        section_title("Most Valuable Players"),
                        dash_table.DataTable(
                            data=top_players_df.to_dict("records"),
                            columns=[
                                {"name": "Player", "id": "player_name"},
                                {"name": "Club", "id": "current_club_name"},
                                {"name": "Age", "id": "age"},
                                {"name": "Position", "id": "position"},
                                {"name": "Nationality", "id": "nationality"},
                                {"name": "Market Value", "id": "market_value_fmt"},
                                {"name": "Peak Value", "id": "peak_fmt"},
                            ],
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": "#1e2738",
                                "color": COLORS["accent"],
                                "fontWeight": "600",
                                "fontSize": "12px",
                                "border": "none",
                                "borderBottom": f"2px solid {COLORS['card_border']}",
                            },
                            style_cell={
                                "backgroundColor": COLORS["card"],
                                "color": COLORS["text"],
                                "fontSize": "12px",
                                "border": "none",
                                "borderBottom": f"1px solid {COLORS['card_border']}",
                                "padding": "8px 12px",
                                "textAlign": "left",
                            },
                            style_data_conditional=[
                                {"if": {"row_index": "odd"}, "backgroundColor": "#151b28"},
                            ],
                            page_size=15,
                        ),
                    ],
                ),
                # Predicted Values
                html.Div(
                    style={**card_style, "flex": "1", "minWidth": "450px"},
                    children=[
                        section_title("Predicted Market Value (ML Model)"),
                        dash_table.DataTable(
                            data=top_predicted.to_dict("records"),
                            columns=[
                                {"name": "Player", "id": "player_name"},
                                {"name": "Club", "id": "current_club_name"},
                                {"name": "Age", "id": "age"},
                                {"name": "Position", "id": "position_group"},
                                {"name": "Actual", "id": "actual_fmt"},
                                {"name": "Predicted", "id": "predicted_fmt"},
                                {"name": "Error", "id": "error_fmt"},
                            ],
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": "#1e2738",
                                "color": COLORS["accent2"],
                                "fontWeight": "600",
                                "fontSize": "12px",
                                "border": "none",
                                "borderBottom": f"2px solid {COLORS['card_border']}",
                            },
                            style_cell={
                                "backgroundColor": COLORS["card"],
                                "color": COLORS["text"],
                                "fontSize": "12px",
                                "border": "none",
                                "borderBottom": f"1px solid {COLORS['card_border']}",
                                "padding": "8px 12px",
                                "textAlign": "left",
                            },
                            style_data_conditional=[
                                {"if": {"row_index": "odd"}, "backgroundColor": "#151b28"},
                            ],
                            page_size=15,
                        ),
                    ],
                ),
            ],
        ),

        # Row 4: Least Valuable
        html.Div(
            style={**card_style, "marginBottom": "24px"},
            children=[
                section_title("Least Valuable Players (Market Value > \u20ac0)"),
                dash_table.DataTable(
                    data=bottom_players_df.to_dict("records"),
                    columns=[
                        {"name": "Player", "id": "player_name"},
                        {"name": "Club", "id": "current_club_name"},
                        {"name": "Age", "id": "age"},
                        {"name": "Position", "id": "position"},
                        {"name": "Nationality", "id": "nationality"},
                        {"name": "Market Value", "id": "market_value_fmt"},
                    ],
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#1e2738",
                        "color": COLORS["accent4"],
                        "fontWeight": "600",
                        "fontSize": "12px",
                        "border": "none",
                        "borderBottom": f"2px solid {COLORS['card_border']}",
                    },
                    style_cell={
                        "backgroundColor": COLORS["card"],
                        "color": COLORS["text"],
                        "fontSize": "12px",
                        "border": "none",
                        "borderBottom": f"1px solid {COLORS['card_border']}",
                        "padding": "8px 12px",
                        "textAlign": "left",
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#151b28"},
                    ],
                    page_size=10,
                ),
            ],
        ),

        # Footer
        html.Div(
            html.P(
                "Data source: Transfermarkt via Kaggle | ML Model: Random Forest Regressor",
                style={"textAlign": "center", "fontSize": "11px", "color": COLORS["text_muted"]},
            ),
            style={"marginTop": "16px", "paddingBottom": "24px"},
        ),
    ],
)


# ---------------------------------------------------------------------------
# Callbacks for interactivity
# ---------------------------------------------------------------------------
@callback(
    Output("world-map", "figure"),
    Input("position-filter", "value"),
    Input("tier-filter", "value"),
)
def update_map(position, tier):
    df = players.copy()
    if position != "All":
        df = df[df["position"] == position]
    if tier != "All":
        df = df[df["league_tier"] == tier]

    agg = (
        df.groupby("country_clean")
        .agg(
            player_count=("player_id", "count"),
            total_value=("market_value", "sum"),
            avg_value=("market_value", "mean"),
        )
        .reset_index()
        .rename(columns={"country_clean": "country"})
    )
    agg["value_label"] = agg["total_value"].apply(fmt_eur)
    agg["avg_label"] = agg["avg_value"].apply(fmt_eur)

    fig = px.scatter_geo(
        agg,
        locations="country",
        locationmode="country names",
        size="player_count",
        color="total_value",
        hover_name="country",
        hover_data={
            "player_count": True,
            "value_label": True,
            "avg_label": True,
            "total_value": False,
            "country": False,
        },
        color_continuous_scale="Viridis",
        size_max=40,
        projection="natural earth",
        labels={
            "player_count": "Players",
            "value_label": "Total Value",
            "avg_label": "Avg Value",
        },
    )
    fig.update_geos(
        bgcolor=COLORS["bg"],
        landcolor="#1a2332",
        oceancolor="#0a0f1a",
        lakecolor="#0a0f1a",
        coastlinecolor="#2d3548",
        countrycolor="#2d3548",
        showframe=False,
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"]),
        coloraxis_colorbar=dict(
            title="Total Value",
            tickformat=",.0s",
            tickprefix="\u20ac",
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=420,
    )
    return fig


@callback(
    Output("club-bar", "figure"),
    Input("position-filter", "value"),
    Input("tier-filter", "value"),
)
def update_club_bar(position, tier):
    df = players.copy()
    if position != "All":
        df = df[df["position"] == position]
    if tier != "All":
        df = df[df["league_tier"] == tier]

    agg = (
        df.groupby("current_club_name")
        .agg(total_value=("market_value", "sum"))
        .reset_index()
        .sort_values("total_value", ascending=False)
        .head(20)
    )

    fig = px.bar(
        agg, x="total_value", y="current_club_name", orientation="h",
        color="total_value", color_continuous_scale=["#1a237e", "#4fc3f7"],
        labels={"total_value": "Market Value", "current_club_name": "Club"},
    )
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], size=11),
        yaxis=dict(autorange="reversed", gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"], tickformat=",.0s", tickprefix="\u20ac"),
        coloraxis_showscale=False,
        margin=dict(l=10, r=20, t=30, b=30),
        height=420,
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
