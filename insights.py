"""
Automated Data Insights engine for Pakistan Population Analytics Dashboard.
Dynamically computes facts, extremes, and demographic narratives strictly from filtered data.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd


def generate_data_insights(df: pd.DataFrame, scope_title: str = "Currently Selected Region") -> List[Dict[str, Any]]:
    """
    Generate dynamic analytical insights strictly calculated from the filtered dataset.
    Never hardcodes answers.
    """
    if df.empty:
        return [{
            "title": "No Data Available",
            "category": "Status",
            "icon": "⚠️",
            "description": "Please adjust filters to display demographic insights.",
            "stat": "N/A"
        }]

    insights: List[Dict[str, Any]] = []

    total_pop = df["Combined Population"].sum()
    rural_pop = df["Rural Total Population"].sum()
    urban_pop = df["Urban Total Population"].sum()
    urban_pct = (urban_pop / total_pop * 100) if total_pop > 0 else 0.0

    # 1. Most Populated Sub-division
    if "SUB DIVISION" in df.columns:
        max_pop_row = df.loc[df["Combined Population"].idxmax()]
        insights.append({
            "title": "Most Populated Administrative Unit",
            "category": "Population Extreme",
            "icon": "🏆",
            "stat": f"{max_pop_row['Combined Population']:,.0f} residents",
            "description": (
                f"**{max_pop_row['SUB DIVISION']}** ({max_pop_row.get('DISTRICT', '')}, {max_pop_row.get('PROVINCE', '')}) "
                f"is the most populous unit in this selection, holding "
                f"**{(max_pop_row['Combined Population'] / total_pop * 100):.2f}%** of the selected population."
            )
        })

    # 2. Least Populated Sub-division
    valid_pops = df[df["Combined Population"] > 0]
    if not valid_pops.empty and "SUB DIVISION" in df.columns:
        min_pop_row = valid_pops.loc[valid_pops["Combined Population"].idxmin()]
        insights.append({
            "title": "Least Populated Administrative Unit",
            "category": "Population Extreme",
            "icon": "📍",
            "stat": f"{min_pop_row['Combined Population']:,.0f} residents",
            "description": (
                f"**{min_pop_row['SUB DIVISION']}** ({min_pop_row.get('DISTRICT', '')}, {min_pop_row.get('PROVINCE', '')}) "
                f"has the lowest population count in this selection."
            )
        })

    # 3. Highest Density Region
    if "Population Density (sq.km)" in df.columns:
        valid_density = df[df["Population Density (sq.km)"] > 0]
        if not valid_density.empty:
            max_dens_row = valid_density.loc[valid_density["Population Density (sq.km)"].idxmax()]
            insights.append({
                "title": "Highest Population Density",
                "category": "Spatial Concentration",
                "icon": "🏢",
                "stat": f"{max_dens_row['Population Density (sq.km)']:,.1f} people/sq.km",
                "description": (
                    f"**{max_dens_row.get('SUB DIVISION', '')}** ({max_dens_row.get('DISTRICT', '')}) "
                    f"records the highest population concentration, with **{max_dens_row['Population Density (sq.km)']:,.1f}** "
                    f"people per square kilometer across an area of {max_dens_row.get('Area (sq.km)', 0):,.1f} sq.km."
                )
            })

    # 4. Rural vs Urban Dominance
    dominance_label = "Rural Dominant" if rural_pop > urban_pop else "Urban Dominant"
    dom_pct = (rural_pop / total_pop * 100) if rural_pop > urban_pop else (urban_pop / total_pop * 100)
    insights.append({
        "title": "Settlement Dominance Structure",
        "category": "Demographic Profile",
        "icon": "🌾" if rural_pop > urban_pop else "🏙️",
        "stat": f"{dominance_label} ({dom_pct:.1f}%)",
        "description": (
            f"The selected scope is **{dominance_label}**. Rural population totals **{rural_pop:,.0f}** ({(rural_pop/total_pop*100):.1f}%) "
            f"compared to Urban population of **{urban_pop:,.0f}** ({(urban_pop/total_pop*100):.1f}%)."
        )
    })

    # 5. Largest Absolute Population Increase Since 1998
    if "Population Change from 1998" in df.columns:
        valid_change = df[df["Population Change from 1998"] > 0]
        if not valid_change.empty:
            max_growth_row = valid_change.loc[valid_change["Population Change from 1998"].idxmax()]
            insights.append({
                "title": "Largest Absolute Growth Since 1998",
                "category": "Historical Expansion",
                "icon": "📈",
                "stat": f"+{max_growth_row['Population Change from 1998']:,.0f} people",
                "description": (
                    f"**{max_growth_row.get('SUB DIVISION', '')}** expanded by **{max_growth_row['Population Change from 1998']:,.0f}** "
                    f"residents between the 1998 census and the current census (a {max_growth_row.get('Population Growth Percentage', 0):.1f}% increase)."
                )
            })

    # 6. Highest Growth Rate
    if "ANNUAL GROWTH RATE (URBAN)" in df.columns and "ANNUAL GROWTH RATE (RURAL)" in df.columns:
        # Filter realistic rates < 50
        valid_gr = df[(df["ANNUAL GROWTH RATE (URBAN)"] < 50) | (df["ANNUAL GROWTH RATE (RURAL)"] < 50)].copy()
        if not valid_gr.empty:
            valid_gr["Peak_Growth"] = valid_gr[["ANNUAL GROWTH RATE (RURAL)", "ANNUAL GROWTH RATE (URBAN)"]].max(axis=1)
            peak_row = valid_gr.loc[valid_gr["Peak_Growth"].idxmax()]
            insights.append({
                "title": "Peak Annual Growth Rate",
                "category": "Rapid Expansion",
                "icon": "🚀",
                "stat": f"{peak_row['Peak_Growth']:.2f}% / year",
                "description": (
                    f"**{peak_row.get('SUB DIVISION', '')}** ({peak_row.get('DISTRICT', '')}) "
                    f"exhibits the fastest annual growth rate at **{peak_row['Peak_Growth']:.2f}%**."
                )
            })

    # 7. Gender Balance & Sex Ratio
    male_total = df["Total Male Population"].sum()
    female_total = df["Total Female Population"].sum()
    sex_ratio = (male_total / female_total * 100) if female_total > 0 else 0
    gender_gap = male_total - female_total
    insights.append({
        "title": "Gender Ratio & Demographic Gap",
        "category": "Gender Balance",
        "icon": "⚖️",
        "stat": f"Sex Ratio: {sex_ratio:.2f}",
        "description": (
            f"For every 100 females, there are **{sex_ratio:.2f} males** in the filtered scope. "
            f"The absolute male surplus stands at **{gender_gap:,.0f}** individuals."
        )
    })

    # 8. Highest Average Household Size
    if "Weighted Avg Household Size" in df.columns:
        valid_hh = df[df["Weighted Avg Household Size"] > 0]
        if not valid_hh.empty:
            max_hh_row = valid_hh.loc[valid_hh["Weighted Avg Household Size"].idxmax()]
            insights.append({
                "title": "Largest Household Size",
                "category": "Social Structure",
                "icon": "👨‍👩‍👧‍👦",
                "stat": f"{max_hh_row['Weighted Avg Household Size']:.2f} persons / home",
                "description": (
                    f"**{max_hh_row.get('SUB DIVISION', '')}** ({max_hh_row.get('DISTRICT', '')}, {max_hh_row.get('PROVINCE', '')}) "
                    f"has the largest average household size at **{max_hh_row['Weighted Avg Household Size']:.2f} persons per household**."
                )
            })

    # 9. Highest Urbanization Sub-Division
    if "Urbanization Percentage" in df.columns:
        valid_urb = df[df["Combined Population"] > 50000]
        if not valid_urb.empty:
            max_urb_row = valid_urb.loc[valid_urb["Urbanization Percentage"].idxmax()]
            insights.append({
                "title": "Highest Urban Concentration",
                "category": "Urbanization",
                "icon": "🏙️",
                "stat": f"{max_urb_row['Urbanization Percentage']:.1f}% Urban",
                "description": (
                    f"**{max_urb_row.get('SUB DIVISION', '')}** is **{max_urb_row['Urbanization Percentage']:.1f}% urban** "
                    f"with {max_urb_row.get('Urban Total Population', 0):,.0f} urban residents."
                )
            })

    # 10. Transgender Population Concentration
    if "Total Transgender Population" in df.columns:
        valid_trans = df[df["Total Transgender Population"] > 0]
        if not valid_trans.empty:
            max_trans_row = valid_trans.loc[valid_trans["Total Transgender Population"].idxmax()]
            insights.append({
                "title": "Highest Recorded Transgender Population",
                "category": "Demographic Inclusivity",
                "icon": "🏳️‍⚧️",
                "stat": f"{max_trans_row['Total Transgender Population']:,} recorded",
                "description": (
                    f"**{max_trans_row.get('SUB DIVISION', '')}** ({max_trans_row.get('DISTRICT', '')}) "
                    f"has the largest census-recorded transgender population in this view."
                )
            })

    return insights
