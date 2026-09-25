"""
Plotly interactive charts module for Pakistan Population Analytics Dashboard.
Implements all 24 required charts with consistent modern design, hover templates,
and robust empty-state handling.
"""

from typing import Optional, List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# Brand and theme colors
PALETTE = {
    "primary": "#2563EB",       # Royal Blue
    "secondary": "#0D9488",     # Teal
    "accent": "#F59E0B",        # Amber
    "danger": "#EF4444",        # Crimson
    "purple": "#8B5CF6",        # Violet
    "emerald": "#10B981",       # Emerald
    "rural": "#059669",         # Forest Green
    "urban": "#3B82F6",         # Sky Blue
    "male": "#1D4ED8",          # Navy
    "female": "#EC4899",        # Pink
    "transgender": "#8B5CF6",   # Purple
    "bg_card": "rgba(255, 255, 255, 0.05)",
}

PLOT_TEMPLATE = "plotly_white"


def empty_figure(message: str = "No data available for the selected filters.") -> go.Figure:
    """Returns a clean empty figure with a friendly message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#64748B")
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        height=320,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig


# 1. Population by Province
def chart_population_by_province(df: pd.DataFrame) -> go.Figure:
    if df.empty or "PROVINCE" not in df.columns:
        return empty_figure()
    grouped = df.groupby("PROVINCE")["Combined Population"].sum().reset_index()
    grouped = grouped.sort_values(by="Combined Population", ascending=True)
    
    fig = px.bar(
        grouped,
        x="Combined Population",
        y="PROVINCE",
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="Blues",
        title="Total Population by Province"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Combined Population",
        yaxis_title="Province",
        coloraxis_showscale=False,
        height=360,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 2. Population by Division
def chart_population_by_division(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if df.empty or "DIVISION" not in df.columns:
        return empty_figure()
    grouped = df.groupby("DIVISION")["Combined Population"].sum().reset_index()
    grouped = grouped.sort_values(by="Combined Population", ascending=False).head(top_n)
    grouped = grouped.sort_values(by="Combined Population", ascending=True)

    fig = px.bar(
        grouped,
        x="Combined Population",
        y="DIVISION",
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="Viridis",
        title=f"Top {len(grouped)} Divisions by Population"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Combined Population",
        yaxis_title="Division",
        coloraxis_showscale=False,
        height=max(360, len(grouped) * 26),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 3. Population by District
def chart_population_by_district(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if df.empty or "DISTRICT" not in df.columns:
        return empty_figure()
    grouped = df.groupby("DISTRICT")["Combined Population"].sum().reset_index()
    grouped = grouped.sort_values(by="Combined Population", ascending=False).head(top_n)
    grouped = grouped.sort_values(by="Combined Population", ascending=True)

    fig = px.bar(
        grouped,
        x="Combined Population",
        y="DISTRICT",
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="Teal",
        title=f"Top {len(grouped)} Districts by Population"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Combined Population",
        yaxis_title="District",
        coloraxis_showscale=False,
        height=max(360, len(grouped) * 26),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 4. Population by Sub Division
def chart_population_by_subdivision(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    if df.empty or "SUB DIVISION" not in df.columns:
        return empty_figure()
    grouped = df.sort_values(by="Combined Population", ascending=False).head(top_n)
    grouped = grouped.sort_values(by="Combined Population", ascending=True)

    fig = px.bar(
        grouped,
        x="Combined Population",
        y="SUB DIVISION",
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="Purples",
        title=f"Top {len(grouped)} Sub Divisions (Tehsils) by Population"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Combined Population",
        yaxis_title="Sub Division",
        coloraxis_showscale=False,
        height=max(360, len(grouped) * 26),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 5. Rural vs Urban Population
def chart_rural_vs_urban_bar(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)[["Rural Total Population", "Urban Total Population"]].sum().reset_index()
    grouped["Combined"] = grouped["Rural Total Population"] + grouped["Urban Total Population"]
    grouped = grouped.sort_values(by="Combined", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Rural Population",
        x=grouped[group_by],
        y=grouped["Rural Total Population"],
        marker_color=PALETTE["rural"],
        hovertemplate="<b>%{x}</b><br>Rural: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Urban Population",
        x=grouped[group_by],
        y=grouped["Urban Total Population"],
        marker_color=PALETTE["urban"],
        hovertemplate="<b>%{x}</b><br>Urban: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=f"Rural vs Urban Population by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Population",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 6. Rural vs Urban Population Share (Donut / Pie)
def chart_rural_vs_urban_donut(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    rural = df["Rural Total Population"].sum()
    urban = df["Urban Total Population"].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=["Rural Population", "Urban Population"],
        values=[rural, urban],
        hole=0.55,
        marker=dict(colors=[PALETTE["rural"], PALETTE["urban"]]),
        textinfo="label+percent",
        hoverinfo="label+value+percent",
        textfont_size=13
    )])
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="National Rural vs Urban Population Share",
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


# 7. Male vs Female Population
def chart_male_vs_female_bar(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)[["Total Male Population", "Total Female Population"]].sum().reset_index()
    grouped["Total"] = grouped["Total Male Population"] + grouped["Total Female Population"]
    grouped = grouped.sort_values(by="Total", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Male",
        x=grouped[group_by],
        y=grouped["Total Male Population"],
        marker_color=PALETTE["male"],
        hovertemplate="<b>%{x}</b><br>Male: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Female",
        x=grouped[group_by],
        y=grouped["Total Female Population"],
        marker_color=PALETTE["female"],
        hovertemplate="<b>%{x}</b><br>Female: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=f"Male vs Female Population by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Population",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 8. Gender Composition (Stacked bar chart)
def chart_gender_composition_stacked(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)[["Total Male Population", "Total Female Population", "Total Transgender Population"]].sum().reset_index()
    total = grouped["Total Male Population"] + grouped["Total Female Population"] + grouped["Total Transgender Population"]
    grouped["Male_Pct"] = (grouped["Total Male Population"] / total * 100).round(2)
    grouped["Female_Pct"] = (grouped["Total Female Population"] / total * 100).round(2)
    grouped["Trans_Pct"] = (grouped["Total Transgender Population"] / total * 100).round(4)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Male %",
        x=grouped[group_by],
        y=grouped["Male_Pct"],
        marker_color=PALETTE["male"],
        hovertemplate="<b>%{x}</b><br>Male: %{y:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Female %",
        x=grouped[group_by],
        y=grouped["Female_Pct"],
        marker_color=PALETTE["female"],
        hovertemplate="<b>%{x}</b><br>Female: %{y:.2f}%<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="stack",
        title=f"Gender Composition (%) by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Percentage (%)",
        yaxis_range=[0, 100],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 9. Transgender Population Comparison
def chart_transgender_comparison(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns or "Total Transgender Population" not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)[["Total Transgender Population", "Combined Population"]].sum().reset_index()
    grouped = grouped.sort_values(by="Total Transgender Population", ascending=True)

    fig = px.bar(
        grouped,
        x="Total Transgender Population",
        y=group_by,
        orientation="h",
        text_auto=True,
        color="Total Transgender Population",
        color_continuous_scale="Purp",
        title=f"Transgender Population by {group_by.title()}"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Recorded Transgender Population",
        yaxis_title=group_by.title(),
        coloraxis_showscale=False,
        height=350,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Transgender Population: %{x:,}<extra></extra>")
    return fig


# 10. Population Density by Region
def chart_density_by_region(df: pd.DataFrame, group_by: str = "PROVINCE", top_n: int = 15) -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    
    # Calculate density at the aggregated level
    grouped = df.groupby(group_by).agg({
        "Combined Population": "sum",
        "Area (sq.km)": "sum"
    }).reset_index()
    grouped = grouped[grouped["Area (sq.km)"] > 0]
    grouped["Density"] = (grouped["Combined Population"] / grouped["Area (sq.km)"]).round(2)
    grouped = grouped.sort_values(by="Density", ascending=False).head(top_n)
    grouped = grouped.sort_values(by="Density", ascending=True)

    fig = px.bar(
        grouped,
        x="Density",
        y=group_by,
        orientation="h",
        text_auto=".1f",
        color="Density",
        color_continuous_scale="Reds",
        title=f"Population Density (People per sq.km) by {group_by.title()}"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Population Density (people/sq.km)",
        yaxis_title=group_by.title(),
        coloraxis_showscale=False,
        height=max(360, len(grouped) * 26),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Density: %{x:,.2f} per sq.km<extra></extra>")
    return fig


# 11. Annual Growth Rate by Region
def chart_growth_rate_by_region(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    
    # Clean out extreme placeholders (>=50%)
    valid = df[(df["ANNUAL GROWTH RATE (RURAL)"] < 50) | (df["ANNUAL GROWTH RATE (URBAN)"] < 50)].copy()
    if valid.empty:
        valid = df.copy()

    # Recalculate 1998-Current annualized growth rate for region
    grouped = valid.groupby(group_by).agg({
        "Combined Population": "sum",
        "1998 Total Population": "sum"
    }).reset_index()
    
    # 19-year compound annual growth rate from 1998 to 2017: (P2017 / P1998)^(1/19) - 1
    # or direct population percentage growth
    grouped["Growth_Pct"] = ((grouped["Combined Population"] - grouped["1998 Total Population"]) / grouped["1998 Total Population"].replace(0, np.nan) * 100).round(2)
    grouped = grouped.sort_values(by="Growth_Pct", ascending=True)

    fig = px.bar(
        grouped,
        x="Growth_Pct",
        y=group_by,
        orientation="h",
        text_auto=".1f",
        color="Growth_Pct",
        color_continuous_scale="Sunset",
        title=f"Overall Population Growth % (1998–Current) by {group_by.title()}"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Total Growth Percentage (%)",
        yaxis_title=group_by.title(),
        coloraxis_showscale=False,
        height=360,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Growth: %{x:.2f}%<extra></extra>")
    return fig


# 12. Rural Annual Growth Rate vs Urban Annual Growth Rate
def chart_rural_vs_urban_growth(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    
    # Filter out placeholder 100.0 growth records
    r_valid = df[df["ANNUAL GROWTH RATE (RURAL)"] < 50]
    u_valid = df[df["ANNUAL GROWTH RATE (URBAN)"] < 50]

    r_mean = r_valid.groupby(group_by)["ANNUAL GROWTH RATE (RURAL)"].mean().reset_index()
    u_mean = u_valid.groupby(group_by)["ANNUAL GROWTH RATE (URBAN)"].mean().reset_index()
    merged = pd.merge(r_mean, u_mean, on=group_by, how="outer").fillna(0)
    merged = merged.sort_values(by="ANNUAL GROWTH RATE (URBAN)", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Rural Avg Growth Rate",
        x=merged[group_by],
        y=merged["ANNUAL GROWTH RATE (RURAL)"].round(2),
        marker_color=PALETTE["rural"],
        hovertemplate="<b>%{x}</b><br>Rural Growth: %{y:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Urban Avg Growth Rate",
        x=merged[group_by],
        y=merged["ANNUAL GROWTH RATE (URBAN)"].round(2),
        marker_color=PALETTE["urban"],
        hovertemplate="<b>%{x}</b><br>Urban Growth: %{y:.2f}%<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=f"Rural vs Urban Annual Growth Rate (%) by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Annual Growth Rate (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 13. 1998 Population vs Current Population
def chart_1998_vs_current(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)[["1998 Total Population", "Combined Population"]].sum().reset_index()
    grouped = grouped.sort_values(by="Combined Population", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="1998 Population",
        x=grouped[group_by],
        y=grouped["1998 Total Population"],
        marker_color="#94A3B8",
        hovertemplate="<b>%{x}</b><br>1998: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Current Population",
        x=grouped[group_by],
        y=grouped["Combined Population"],
        marker_color=PALETTE["primary"],
        hovertemplate="<b>%{x}</b><br>Current: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=f"1998 vs Current Population Comparison by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Population",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 14. Population Growth (Absolute Increase)
def chart_population_growth_bars(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    grouped = df.groupby(group_by)["Population Change from 1998"].sum().reset_index()
    grouped = grouped.sort_values(by="Population Change from 1998", ascending=True)

    fig = px.bar(
        grouped,
        x="Population Change from 1998",
        y=group_by,
        orientation="h",
        text_auto=".2s",
        color="Population Change from 1998",
        color_continuous_scale="Tealgrn",
        title=f"Absolute Population Growth (1998 to Current) by {group_by.title()}"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Absolute Population Increase",
        yaxis_title=group_by.title(),
        coloraxis_showscale=False,
        height=360,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Increase: +%{x:,.0f}<extra></extra>")
    return fig


# 15. Population vs Area Scatter Plot
def chart_population_vs_area_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Area (sq.km)" not in df.columns or "Combined Population" not in df.columns:
        return empty_figure()
    valid = df[df["Area (sq.km)"] > 0].copy()

    fig = px.scatter(
        valid,
        x="Area (sq.km)",
        y="Combined Population",
        color="PROVINCE" if "PROVINCE" in valid.columns else None,
        hover_name="SUB DIVISION" if "SUB DIVISION" in valid.columns else None,
        hover_data={"DISTRICT": True, "Area (sq.km)": ":,.1f", "Combined Population": ":,.0f"},
        size="Combined Population",
        size_max=35,
        title="Sub Division Population vs Geographic Area (sq.km)"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Area (sq. km)",
        yaxis_title="Combined Population",
        height=420,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig


# 16. Population Density vs Growth Rate Scatter Plot
def chart_density_vs_growth_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Population Density (sq.km)" not in df.columns:
        return empty_figure()
    valid = df[(df["Population Density (sq.km)"] > 0) & (df["Population Growth Percentage"] > -50) & (df["Population Growth Percentage"] < 300)].copy()

    fig = px.scatter(
        valid,
        x="Population Density (sq.km)",
        y="Population Growth Percentage",
        color="PROVINCE" if "PROVINCE" in valid.columns else None,
        hover_name="SUB DIVISION" if "SUB DIVISION" in valid.columns else None,
        hover_data={"DISTRICT": True, "Population Density (sq.km)": ":,.1f", "Population Growth Percentage": ":.2f%"},
        title="Population Density vs 1998–Current Population Growth %"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Population Density (people/sq.km)",
        yaxis_title="Growth % since 1998",
        height=420,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig


# 17. Average Household Size
def chart_avg_household_size(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    
    # Filter valid household sizes > 0
    valid = df[df["Weighted Avg Household Size"] > 0].copy()
    if valid.empty:
        return empty_figure("No valid household size records available.")
    
    grouped = valid.groupby(group_by).apply(
        lambda g: (g["Weighted Avg Household Size"] * g["Combined Population"]).sum() / g["Combined Population"].sum()
    ).reset_index(name="Avg_Household_Size")
    grouped = grouped.sort_values(by="Avg_Household_Size", ascending=True)

    fig = px.bar(
        grouped,
        x="Avg_Household_Size",
        y=group_by,
        orientation="h",
        text_auto=".2f",
        color="Avg_Household_Size",
        color_continuous_scale="YlGnBu",
        title=f"Average Household Size (Persons per House) by {group_by.title()}"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Average Household Size (Persons)",
        yaxis_title=group_by.title(),
        coloraxis_showscale=False,
        height=360,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Avg Household Size: %{x:.2f} persons<extra></extra>")
    return fig


# 18. Sex Ratio Comparison (Rural vs Urban)
def chart_sex_ratio_comparison(df: pd.DataFrame, group_by: str = "PROVINCE") -> go.Figure:
    if df.empty or group_by not in df.columns:
        return empty_figure()
    
    grouped = df.groupby(group_by).agg({
        "MALE (RURAL)": "sum",
        "FEMALE (RURAL)": "sum",
        "MALE (URBAN)": "sum",
        "FEMALE (URBAN)": "sum"
    }).reset_index()

    f_rural = grouped["FEMALE (RURAL)"].replace(0, np.nan)
    f_urban = grouped["FEMALE (URBAN)"].replace(0, np.nan)
    
    grouped["Rural_Sex_Ratio"] = (grouped["MALE (RURAL)"] / f_rural * 100).round(2)
    grouped["Urban_Sex_Ratio"] = (grouped["MALE (URBAN)"] / f_urban * 100).round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Rural Sex Ratio",
        x=grouped[group_by],
        y=grouped["Rural_Sex_Ratio"],
        marker_color=PALETTE["rural"],
        hovertemplate="<b>%{x}</b><br>Rural Sex Ratio: %{y:.2f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="Urban Sex Ratio",
        x=grouped[group_by],
        y=grouped["Urban_Sex_Ratio"],
        marker_color=PALETTE["urban"],
        hovertemplate="<b>%{x}</b><br>Urban Sex Ratio: %{y:.2f}<extra></extra>"
    ))
    # Add parity line at 100
    fig.add_hline(y=100, line_dash="dash", line_color="#94A3B8", annotation_text="Parity (100)", annotation_position="top left")

    fig.update_layout(
        template=PLOT_TEMPLATE,
        barmode="group",
        title=f"Sex Ratio Comparison (Males per 100 Females) by {group_by.title()}",
        xaxis_title=group_by.title(),
        yaxis_title="Sex Ratio (Males per 100 Females)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


# 19. Top 10 Most Populated Regions
def chart_top_n_populated(df: pd.DataFrame, n: int = 10, region_col: str = "SUB DIVISION") -> go.Figure:
    if df.empty or region_col not in df.columns:
        return empty_figure()
    top = df.sort_values(by="Combined Population", ascending=False).head(n)
    top = top.sort_values(by="Combined Population", ascending=True)

    fig = px.bar(
        top,
        x="Combined Population",
        y=region_col,
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="Blues",
        title=f"Top {len(top)} Most Populated {region_col.title()}s"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Population",
        yaxis_title=region_col.title(),
        coloraxis_showscale=False,
        height=max(360, len(top) * 28),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 20. Bottom 10 Least Populated Regions
def chart_bottom_n_populated(df: pd.DataFrame, n: int = 10, region_col: str = "SUB DIVISION") -> go.Figure:
    if df.empty or region_col not in df.columns:
        return empty_figure()
    bottom = df[df["Combined Population"] > 0].sort_values(by="Combined Population", ascending=True).head(n)

    fig = px.bar(
        bottom,
        x="Combined Population",
        y=region_col,
        orientation="h",
        text_auto=".2s",
        color="Combined Population",
        color_continuous_scale="OrRd",
        title=f"Bottom {len(bottom)} Least Populated {region_col.title()}s"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Population",
        yaxis_title=region_col.title(),
        coloraxis_showscale=False,
        height=max(360, len(bottom) * 28),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>")
    return fig


# 21. Top 10 Highest Growth Regions
def chart_top_n_growth(df: pd.DataFrame, n: int = 10, region_col: str = "SUB DIVISION") -> go.Figure:
    if df.empty or region_col not in df.columns:
        return empty_figure()
    
    # Filter valid growth rate records < 50%
    valid = df[(df["ANNUAL GROWTH RATE (URBAN)"] < 50) | (df["ANNUAL GROWTH RATE (RURAL)"] < 50)].copy()
    valid["Max_Growth"] = valid[["ANNUAL GROWTH RATE (RURAL)", "ANNUAL GROWTH RATE (URBAN)"]].max(axis=1)
    top = valid.sort_values(by="Max_Growth", ascending=False).head(n)
    top = top.sort_values(by="Max_Growth", ascending=True)

    fig = px.bar(
        top,
        x="Max_Growth",
        y=region_col,
        orientation="h",
        text_auto=".2f",
        color="Max_Growth",
        color_continuous_scale="Viridis",
        title=f"Top {len(top)} Highest Annual Growth Regions (%)"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Growth Rate (%)",
        yaxis_title=region_col.title(),
        coloraxis_showscale=False,
        height=max(360, len(top) * 28),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Growth: %{x:.2f}%<extra></extra>")
    return fig


# 22. Top 10 Lowest Growth Regions
def chart_bottom_n_growth(df: pd.DataFrame, n: int = 10, region_col: str = "SUB DIVISION") -> go.Figure:
    if df.empty or region_col not in df.columns:
        return empty_figure()
    
    valid = df[(df["ANNUAL GROWTH RATE (RURAL)"] > 0) | (df["ANNUAL GROWTH RATE (URBAN)"] > 0)].copy()
    valid["Min_Growth"] = valid[["ANNUAL GROWTH RATE (RURAL)", "ANNUAL GROWTH RATE (URBAN)"]].replace(0, np.nan).min(axis=1)
    valid = valid.dropna(subset=["Min_Growth"])
    bottom = valid.sort_values(by="Min_Growth", ascending=True).head(n)
    bottom = bottom.sort_values(by="Min_Growth", ascending=False)

    fig = px.bar(
        bottom,
        x="Min_Growth",
        y=region_col,
        orientation="h",
        text_auto=".2f",
        color="Min_Growth",
        color_continuous_scale="Reds_r",
        title=f"Top {len(bottom)} Slowest Growing Regions (%)"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Growth Rate (%)",
        yaxis_title=region_col.title(),
        coloraxis_showscale=False,
        height=max(360, len(bottom) * 28),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Growth: %{x:.2f}%<extra></extra>")
    return fig


# 23. Top 10 Highest Population Density Regions
def chart_top_n_density(df: pd.DataFrame, n: int = 10, region_col: str = "SUB DIVISION") -> go.Figure:
    if df.empty or region_col not in df.columns or "Population Density (sq.km)" not in df.columns:
        return empty_figure()
    valid = df[df["Population Density (sq.km)"] > 0].sort_values(by="Population Density (sq.km)", ascending=False).head(n)
    valid = valid.sort_values(by="Population Density (sq.km)", ascending=True)

    fig = px.bar(
        valid,
        x="Population Density (sq.km)",
        y=region_col,
        orientation="h",
        text_auto=".1f",
        color="Population Density (sq.km)",
        color_continuous_scale="Plotly3",
        title=f"Top {len(valid)} Highest Density {region_col.title()}s"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Density (people/sq.km)",
        yaxis_title=region_col.title(),
        coloraxis_showscale=False,
        height=max(360, len(valid) * 28),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Density: %{x:,.1f} per sq.km<extra></extra>")
    return fig


# 24. Rural Dominant vs Urban Dominant Regions
def chart_rural_vs_urban_dominant_regions(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Dominance Category" not in df.columns:
        return empty_figure()
    counts = df["Dominance Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]

    color_map = {
        "Rural Dominant": PALETTE["rural"],
        "100% Rural": "#047857",
        "Urban Dominant": PALETTE["urban"],
        "100% Urban": "#1E40AF",
        "Balanced": "#F59E0B"
    }

    fig = px.bar(
        counts,
        x="Category",
        y="Count",
        color="Category",
        color_discrete_map=color_map,
        text_auto=True,
        title="Distribution of Sub Divisions by Settlement Dominance"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title="Settlement Type",
        yaxis_title="Number of Sub Divisions",
        showlegend=False,
        height=360,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Sub Divisions: %{y:,}<extra></extra>")
    return fig


# Correlation Heatmap
def chart_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    if corr_df.empty:
        return empty_figure()

    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Pearson Correlation Heatmap of Demographic Indicators"
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=520,
        margin=dict(l=40, r=40, t=60, b=50)
    )
    return fig


# Distribution Histogram
def chart_distribution_histogram(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    if df.empty or column not in df.columns:
        return empty_figure()
    s = df[column].dropna()
    if s.empty:
        return empty_figure()

    fig = px.histogram(
        df,
        x=column,
        nbins=40,
        marginal="box",
        color_discrete_sequence=[PALETTE["primary"]],
        title=title
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        xaxis_title=column,
        yaxis_title="Frequency",
        height=380,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig
