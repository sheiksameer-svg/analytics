"""
Pakistan Population & Demographic Analytics Dashboard
Main Streamlit Application
"""

from pathlib import Path
import io
import pandas as pd
import numpy as np
import streamlit as st

# Custom modules
from modules.data_loader import load_dataset, find_default_dataset_path, inspect_raw_structure
from modules.preprocessing import clean_and_derive_metrics, get_data_quality_report
from modules.analytics import (
    compute_kpis, compute_descriptive_stats, compute_correlation_matrix,
    detect_outliers, aggregate_by_hierarchy, get_top_bottom_rankings
)
import modules.charts as charts
from modules.insights import generate_data_insights


# Page Configuration
st.set_page_config(
    page_title="Pakistan Population & Demographic Analytics",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Styles
css_path = Path("assets/style.css")
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Caching Ingestion & Preprocessing
@st.cache_data(show_spinner=False)
def load_and_preprocess(source_path_or_bytes):
    raw_df, meta = load_dataset(source_path_or_bytes)
    cleaned_df = clean_and_derive_metrics(raw_df)
    quality_report = get_data_quality_report(raw_df, cleaned_df)
    return raw_df, cleaned_df, meta, quality_report


# Header Component
def render_header(kpis, geo_scope_text):
    st.markdown(
        f"""
        <div class="dash-header">
            <h1>🇵🇰 Pakistan Population & Demographic Analytics Dashboard</h1>
            <p>Interactive Data Analytics of Rural, Urban, Gender, Growth and Geographic Population Patterns</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# KPI Card Component
def render_kpi_cards(kpis, geo_scope_text):
    st.markdown(
        f"""
        <div class="filter-badge-bar">
            <span>📍 <strong>Active Geographic Scope:</strong></span>
            <span class="filter-badge">{geo_scope_text}</span>
            <span class="filter-badge">{kpis['subdivisions_count']} Sub Divisions</span>
            <span class="filter-badge">{kpis['districts_count']} Districts</span>
            <span class="filter-badge">{kpis['divisions_count']} Divisions</span>
            <span class="filter-badge">{kpis['provinces_count']} Provinces</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Population</div>
                <div class="kpi-value">{kpis['total_population']:,}</div>
                <div class="kpi-sub">Across {kpis['subdivisions_count']} Sub Divisions</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card rural">
                <div class="kpi-label">Rural Population</div>
                <div class="kpi-value">{kpis['rural_population']:,}</div>
                <div class="kpi-sub">{kpis['rural_share_pct']:.1f}% of Total Population</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card urban">
                <div class="kpi-label">Urban Population</div>
                <div class="kpi-value">{kpis['urban_population']:,}</div>
                <div class="kpi-sub">{kpis['urbanization_pct']:.1f}% Urbanization Rate</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card density">
                <div class="kpi-label">Population Density</div>
                <div class="kpi-value">{kpis['population_density']:,.1f}</div>
                <div class="kpi-sub">People / sq.km (Area: {kpis['total_area']:,.0f} km²)</div>
            </div>
            """, unsafe_allow_html=True
        )

    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.markdown(
            f"""
            <div class="kpi-card male">
                <div class="kpi-label">Male Population</div>
                <div class="kpi-value">{kpis['male_population']:,}</div>
                <div class="kpi-sub">{kpis['male_pct']:.1f}% (Sex Ratio: {kpis['sex_ratio']:.1f})</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k6:
        st.markdown(
            f"""
            <div class="kpi-card female">
                <div class="kpi-label">Female Population</div>
                <div class="kpi-value">{kpis['female_population']:,}</div>
                <div class="kpi-sub">{kpis['female_pct']:.1f}% of Total Population</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k7:
        growth_sign = "+" if kpis['pop_change_1998'] >= 0 else ""
        st.markdown(
            f"""
            <div class="kpi-card growth">
                <div class="kpi-label">Change from 1998</div>
                <div class="kpi-value">{growth_sign}{kpis['pop_change_1998']:,}</div>
                <div class="kpi-sub">{growth_sign}{kpis['growth_pct_1998']:.1f}% Growth (Avg: {kpis['avg_growth_rate']:.2f}%/yr)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with k8:
        st.markdown(
            f"""
            <div class="kpi-card trans">
                <div class="kpi-label">Transgender & Household</div>
                <div class="kpi-value">{kpis['transgender_population']:,}</div>
                <div class="kpi-sub">Transgender ({kpis['transgender_pct']:.3f}%) | Avg HH: {kpis['avg_household_size']:.2f}</div>
            </div>
            """, unsafe_allow_html=True
        )


def main():
    # 1. Dataset Selection / Detection
    default_path = find_default_dataset_path()
    
    # Sidebar: Data Source & Filtering
    st.sidebar.title("🎛️ Dashboard Controls")
    
    with st.sidebar.expander("📁 Data Source Selection", expanded=False):
        uploaded_file = st.file_uploader("Upload Replacement CSV", type=["csv"])
        if uploaded_file is not None:
            source = uploaded_file
            st.success(f"Loaded uploaded file: {uploaded_file.name}")
        elif default_path:
            source = default_path
            st.info(f"Using default dataset: `{default_path.name}`")
        else:
            st.error("No dataset found. Please place `dataset.csv` in `data/` or upload one.")
            st.stop()

    try:
        raw_df, cleaned_df, meta, quality_report = load_and_preprocess(source)
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("filt_"):
                del st.session_state[key]
        st.rerun()

    # 2. Connected Cascading Hierarchy Filters
    st.sidebar.markdown("### 🏛️ Geographic Hierarchy")

    # Province Filter
    provinces_available = sorted(cleaned_df["PROVINCE"].dropna().unique().tolist())
    selected_provinces = st.sidebar.multiselect(
        "Province(s)",
        options=provinces_available,
        default=[],
        key="filt_province",
        placeholder="All Provinces"
    )

    # Filter by Province first to get available Divisions
    df_step1 = cleaned_df.copy()
    if selected_provinces:
        df_step1 = df_step1[df_step1["PROVINCE"].isin(selected_provinces)]

    # Division Filter
    divisions_available = sorted(df_step1["DIVISION"].dropna().unique().tolist())
    selected_divisions = st.sidebar.multiselect(
        "Division(s)",
        options=divisions_available,
        default=[],
        key="filt_division",
        placeholder="All Divisions"
    )

    # Filter by Division to get available Districts
    df_step2 = df_step1.copy()
    if selected_divisions:
        df_step2 = df_step2[df_step2["DIVISION"].isin(selected_divisions)]

    # District Filter
    districts_available = sorted(df_step2["DISTRICT"].dropna().unique().tolist())
    selected_districts = st.sidebar.multiselect(
        "District(s)",
        options=districts_available,
        default=[],
        key="filt_district",
        placeholder="All Districts"
    )

    # Filter by District to get available Sub Divisions
    df_step3 = df_step2.copy()
    if selected_districts:
        df_step3 = df_step3[df_step3["DISTRICT"].isin(selected_districts)]

    # Sub Division Filter
    subdivisions_available = sorted(df_step3["SUB DIVISION"].dropna().unique().tolist())
    selected_subdivisions = st.sidebar.multiselect(
        "Sub Division(s) / Tehsils",
        options=subdivisions_available,
        default=[],
        key="filt_subdivision",
        placeholder="All Sub Divisions"
    )

    # Apply Sub Division Filter
    filtered_df = df_step3.copy()
    if selected_subdivisions:
        filtered_df = filtered_df[filtered_df["SUB DIVISION"].isin(selected_subdivisions)]

    # Top-N Rankings Setting
    st.sidebar.markdown("### 📊 Display & Ranking")
    top_n_choice = st.sidebar.selectbox(
        "Top-N Item Count",
        options=[5, 10, 15, 20, 50, "All"],
        index=2,
        key="filt_top_n"
    )
    top_n_val = len(filtered_df) if top_n_choice == "All" else int(top_n_choice)

    # Additional Numerical Filters
    with st.sidebar.expander("🎯 Advanced Range Filters", expanded=False):
        # Population Range
        min_pop = int(cleaned_df["Combined Population"].min())
        max_pop = int(cleaned_df["Combined Population"].max())
        pop_range = st.slider(
            "Population Range",
            min_value=min_pop,
            max_value=max_pop,
            value=(min_pop, max_pop),
            step=10000,
            key="filt_pop_range"
        )
        filtered_df = filtered_df[
            (filtered_df["Combined Population"] >= pop_range[0]) &
            (filtered_df["Combined Population"] <= pop_range[1])
        ]

        # Area Range
        valid_areas = cleaned_df[cleaned_df["Area (sq.km)"] > 0]["Area (sq.km)"]
        min_area = float(valid_areas.min()) if not valid_areas.empty else 0.0
        max_area = float(valid_areas.max()) if not valid_areas.empty else 10000.0
        area_range = st.slider(
            "Area (sq.km) Range",
            min_value=float(min_area),
            max_value=float(max_area),
            value=(float(min_area), float(max_area)),
            step=100.0,
            key="filt_area_range"
        )
        filtered_df = filtered_df[
            (filtered_df["Area (sq.km)"] >= area_range[0]) &
            (filtered_df["Area (sq.km)"] <= area_range[1])
        ]

        # Settlement Dominance Filter
        dom_types = ["All"] + sorted(cleaned_df["Dominance Category"].dropna().unique().tolist())
        selected_dom = st.selectbox("Settlement Dominance", options=dom_types, key="filt_dom")
        if selected_dom != "All":
            filtered_df = filtered_df[filtered_df["Dominance Category"] == selected_dom]

    # Calculate Current Geographic Scope Description
    if selected_subdivisions:
        geo_scope_text = f"Sub Division(s): {', '.join(selected_subdivisions[:2])}{'...' if len(selected_subdivisions) > 2 else ''}"
    elif selected_districts:
        geo_scope_text = f"District(s): {', '.join(selected_districts[:2])}{'...' if len(selected_districts) > 2 else ''}"
    elif selected_divisions:
        geo_scope_text = f"Division(s): {', '.join(selected_divisions[:2])}{'...' if len(selected_divisions) > 2 else ''}"
    elif selected_provinces:
        geo_scope_text = f"Province(s): {', '.join(selected_provinces)}"
    else:
        geo_scope_text = "National (All Pakistan)"

    # Compute KPIs
    kpis = compute_kpis(filtered_df)

    # Render Header & KPIs
    render_header(kpis, geo_scope_text)
    render_kpi_cards(kpis, geo_scope_text)

    # Empty State Warning
    if filtered_df.empty:
        st.warning("⚠️ No data available for the currently selected filter combinations. Please broaden your selection or click 'Reset All Filters'.")
        st.stop()

    # Dynamic Hierarchical Grouping Level
    # If a specific province is filtered, charts default to Division/District
    if len(selected_districts) > 0:
        default_geo_col = "SUB DIVISION"
    elif len(selected_divisions) > 0:
        default_geo_col = "DISTRICT"
    elif len(selected_provinces) > 0:
        default_geo_col = "DIVISION"
    else:
        default_geo_col = "PROVINCE"

    # 3. Main Dashboard Tabs
    tabs = st.tabs([
        "📊 Overview",
        "👥 Population Analysis",
        "🌾 Rural vs Urban",
        "⚖️ Gender Analysis",
        "📈 Growth Trends",
        "🗺️ Geographic & Density",
        "🏠 Household Structure",
        "🔬 Advanced Analytics",
        "💡 Data Insights",
        "🛡️ Data Quality",
        "📑 Data Explorer & Export"
    ])

    # -------------------------------------------------------------
    # TAB 1: OVERVIEW
    # -------------------------------------------------------------
    with tabs[0]:
        st.markdown('<div class="section-title">📊 Executive Summary & Demographic Landscape</div>', unsafe_allow_html=True)
        col_ov1, col_ov2 = st.columns([3, 2])
        
        with col_ov1:
            st.plotly_chart(charts.chart_population_by_province(filtered_df), use_container_width=True)
            st.plotly_chart(charts.chart_rural_vs_urban_bar(filtered_df, group_by=default_geo_col), use_container_width=True)

        with col_ov2:
            st.plotly_chart(charts.chart_rural_vs_urban_donut(filtered_df), use_container_width=True)
            st.plotly_chart(charts.chart_gender_composition_stacked(filtered_df, group_by=default_geo_col), use_container_width=True)

        # Regional Aggregation Summary Table
        st.markdown(f'<div class="section-title">🏛️ Aggregated Summary by {default_geo_col.title()}</div>', unsafe_allow_html=True)
        agg_table = aggregate_by_hierarchy(filtered_df, default_geo_col)
        st.dataframe(
            agg_table,
            use_container_width=True,
            column_config={
                "Combined Population": st.column_config.NumberColumn(format="%d"),
                "Rural Total Population": st.column_config.NumberColumn(format="%d"),
                "Urban Total Population": st.column_config.NumberColumn(format="%d"),
                "Total Male Population": st.column_config.NumberColumn(format="%d"),
                "Total Female Population": st.column_config.NumberColumn(format="%d"),
                "Area (sq.km)": st.column_config.NumberColumn(format="%.1f"),
                "Population Density (sq.km)": st.column_config.NumberColumn(format="%.1f"),
                "Urbanization Percentage": st.column_config.NumberColumn(format="%.2f%%"),
                "Overall Sex Ratio": st.column_config.NumberColumn(format="%.2f"),
                "Population Growth Percentage": st.column_config.NumberColumn(format="%.2f%%"),
            },
            hide_index=True
        )

    # -------------------------------------------------------------
    # TAB 2: POPULATION ANALYSIS
    # -------------------------------------------------------------
    with tabs[1]:
        st.markdown('<div class="section-title">👥 Multi-Level Population Distribution</div>', unsafe_allow_html=True)
        
        col_pop1, col_pop2 = st.columns(2)
        with col_pop1:
            st.plotly_chart(charts.chart_population_by_province(filtered_df), use_container_width=True,key="population_by_province")
            st.plotly_chart(charts.chart_population_by_district(filtered_df, top_n=top_n_val), use_container_width=True,key="population_by_district",)

        with col_pop2:
            st.plotly_chart(charts.chart_population_by_division(filtered_df, top_n=top_n_val), use_container_width=True,key="population_by_division")
            st.plotly_chart(charts.chart_population_by_subdivision(filtered_df, top_n=top_n_val), use_container_width=True,key="population_by_subdivision")

        st.markdown('<div class="section-title">🌐 Population vs Geographic Area</div>', unsafe_allow_html=True)
        st.plotly_chart(charts.chart_population_vs_area_scatter(filtered_df), use_container_width=True,key="population_vs_area")

    # -------------------------------------------------------------
    # TAB 3: RURAL VS URBAN
    # -------------------------------------------------------------
    with tabs[2]:
        st.markdown('<div class="section-title">🌾 Rural vs Urban Demographics & Urbanization Patterns</div>', unsafe_allow_html=True)
        
        col_ru1, col_ru2 = st.columns([3, 2])
        with col_ru1:
            st.plotly_chart(charts.chart_rural_vs_urban_bar(filtered_df, group_by=default_geo_col), use_container_width=True,key="rural_vs_urban_bar")
            st.plotly_chart(charts.chart_rural_vs_urban_growth(filtered_df, group_by=default_geo_col), use_container_width=True,key="rural_vs_urban_growth")

        with col_ru2:
            st.plotly_chart(charts.chart_rural_vs_urban_donut(filtered_df), use_container_width=True,key="rural_vs_urban_donut")
            st.plotly_chart(charts.chart_rural_vs_urban_dominant_regions(filtered_df), use_container_width=True,key="rural_vs_urban_dominant_regions")

        # Classification Table
        st.markdown('<div class="section-title">📋 Settlement Classification Breakdown</div>', unsafe_allow_html=True)
        dom_breakdown = filtered_df["Dominance Category"].value_counts().reset_index()
        dom_breakdown.columns = ["Settlement Type", "Sub Divisions Count"]
        dom_breakdown["Share %"] = (dom_breakdown["Sub Divisions Count"] / len(filtered_df) * 100).round(2)
        st.dataframe(dom_breakdown, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 4: GENDER ANALYSIS
    # -------------------------------------------------------------
    with tabs[3]:
        st.markdown('<div class="section-title">⚖️ Gender Composition, Sex Ratios & Inclusivity</div>', unsafe_allow_html=True)
        
        col_gen1, col_gen2 = st.columns(2)
        with col_gen1:
            st.plotly_chart(charts.chart_male_vs_female_bar(filtered_df, group_by=default_geo_col), use_container_width=True,key="male_vs_female_bar")
            st.plotly_chart(charts.chart_sex_ratio_comparison(filtered_df, group_by=default_geo_col), use_container_width=True,key="sex_ratio_comparison")

        with col_gen2:
            st.plotly_chart(charts.chart_gender_composition_stacked(filtered_df, group_by=default_geo_col), use_container_width=True,key="gender_composition_stacked")
            st.plotly_chart(charts.chart_transgender_comparison(filtered_df, group_by=default_geo_col), use_container_width=True,key="transgender_comparison")

        # Gender Gap Metrics Callout
        st.markdown(
            f"""
            > **Gender Parity Summary:** Within the filtered scope, **Total Males: {kpis['male_population']:,}** ({kpis['male_pct']}%) 
            > and **Total Females: {kpis['female_population']:,}** ({kpis['female_pct']}%), resulting in a net male surplus of 
            > **{kpis['male_population'] - kpis['female_population']:,} individuals** (Sex Ratio: **{kpis['sex_ratio']} males per 100 females**).
            """
        )

    # -------------------------------------------------------------
    # TAB 5: GROWTH TRENDS
    # -------------------------------------------------------------
    with tabs[4]:
        st.markdown('<div class="section-title">📈 Historical Evolution & Growth Rates (1998 vs Current)</div>', unsafe_allow_html=True)
        
        col_gr1, col_gr2 = st.columns(2)
        with col_gr1:
            st.plotly_chart(charts.chart_1998_vs_current(filtered_df, group_by=default_geo_col), use_container_width=True)
            st.plotly_chart(charts.chart_growth_rate_by_region(filtered_df, group_by=default_geo_col), use_container_width=True)

        with col_gr2:
            st.plotly_chart(charts.chart_population_growth_bars(filtered_df, group_by=default_geo_col), use_container_width=True)
            st.plotly_chart(charts.chart_density_vs_growth_scatter(filtered_df), use_container_width=True)

    # -------------------------------------------------------------
    # TAB 6: GEOGRAPHIC & DENSITY
    # -------------------------------------------------------------
    with tabs[5]:
        st.markdown('<div class="section-title">🗺️ Spatial Density & Regional Extremes</div>', unsafe_allow_html=True)
        st.plotly_chart(charts.chart_density_by_region(filtered_df, group_by=default_geo_col, top_n=top_n_val), use_container_width=True)

        col_rnk1, col_rnk2 = st.columns(2)
        with col_rnk1:
            st.plotly_chart(charts.chart_top_n_populated(filtered_df, n=top_n_val), use_container_width=True)
            st.plotly_chart(charts.chart_top_n_growth(filtered_df, n=top_n_val), use_container_width=True)
            st.plotly_chart(charts.chart_top_n_density(filtered_df, n=top_n_val), use_container_width=True)

        with col_rnk2:
            st.plotly_chart(charts.chart_bottom_n_populated(filtered_df, n=top_n_val), use_container_width=True)
            st.plotly_chart(charts.chart_bottom_n_growth(filtered_df, n=top_n_val), use_container_width=True)

    # -------------------------------------------------------------
    # TAB 7: HOUSEHOLD STRUCTURE
    # -------------------------------------------------------------
    with tabs[6]:
        st.markdown('<div class="section-title">🏠 Household Demographics & Family Size</div>', unsafe_allow_html=True)
        
        col_hh1, col_hh2 = st.columns(2)
        with col_hh1:
            st.plotly_chart(charts.chart_avg_household_size(filtered_df, group_by=default_geo_col), use_container_width=True)
        with col_hh2:
            st.plotly_chart(
                charts.chart_distribution_histogram(
                    filtered_df[filtered_df["Weighted Avg Household Size"] > 0],
                    column="Weighted Avg Household Size",
                    title="Distribution of Average Household Sizes"
                ),
                use_container_width=True
            )

    # -------------------------------------------------------------
    # TAB 8: ADVANCED ANALYTICS
    # -------------------------------------------------------------
    with tabs[7]:
        st.markdown('<div class="section-title">🔬 Statistical Distributions, Correlations & Outlier Audit</div>', unsafe_allow_html=True)
        
        st.markdown("#### 1. Descriptive Statistics")
        desc_df = compute_descriptive_stats(filtered_df)
        st.dataframe(desc_df, use_container_width=True, hide_index=True)

        st.markdown("#### 2. Pearson Correlation Matrix")
        st.caption("ℹ️ *Statistical Note: Correlation reflects linear association between recorded metrics, not causal impact.*")
        corr_matrix = compute_correlation_matrix(filtered_df)
        st.plotly_chart(charts.chart_correlation_heatmap(corr_matrix), use_container_width=True)

        st.markdown("#### 3. Statistical Outlier Detection")
        col_sel_outlier = st.selectbox(
            "Select Variable for Outlier Inspection",
            options=["Combined Population", "Population Density (sq.km)", "Area (sq.km)", "Population Growth Percentage"],
            index=0
        )
        outlier_method = st.radio("Outlier Detection Method", options=["IQR (Interquartile Range)", "Z-score (Std Dev)"], horizontal=True)
        method_key = "iqr" if "IQR" in outlier_method else "zscore"
        threshold_val = 1.5 if method_key == "iqr" else 2.5

        outliers = detect_outliers(filtered_df, col_sel_outlier, method=method_key, threshold=threshold_val)
        if not outliers.empty:
            st.write(f"Detected **{len(outliers)} outliers** in `{col_sel_outlier}`:")
            cols_show = [c for c in ["PROVINCE", "DISTRICT", "SUB DIVISION", col_sel_outlier, "Outlier_Type", "Lower_Bound", "Upper_Bound"] if c in outliers.columns]
            st.dataframe(outliers[cols_show], use_container_width=True, hide_index=True)
        else:
            st.info(f"No statistical outliers detected in `{col_sel_outlier}` using {outlier_method}.")

    # -------------------------------------------------------------
    # TAB 9: AUTOMATED DATA INSIGHTS
    # -------------------------------------------------------------
    with tabs[8]:
        st.markdown('<div class="section-title">💡 Automated Data Insights Engine</div>', unsafe_allow_html=True)
        st.caption("These statements are automatically evaluated and generated directly from the filtered census dataset.")

        insights = generate_data_insights(filtered_df, scope_title=geo_scope_text)
        
        for ins in insights:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-header">
                        <span class="insight-category">{ins['icon']} {ins['category']} &bull; {ins['title']}</span>
                        <span class="insight-stat">{ins['stat']}</span>
                    </div>
                    <div class="insight-body">{ins['description']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------
    # TAB 10: DATA QUALITY AUDIT
    # -------------------------------------------------------------
    with tabs[9]:
        st.markdown('<div class="section-title">🛡️ Data Quality, Verification & Anomaly Audit</div>', unsafe_allow_html=True)
        
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        col_q1.metric("Total Rows", quality_report["total_rows"])
        col_q2.metric("Raw Columns", quality_report["total_columns"])
        col_q3.metric("Missing Values", quality_report["total_missing_cells"])
        col_q4.metric("Duplicate Rows", quality_report["total_duplicates"])

        st.markdown("#### Documented Data Anomalies in the Official Dataset")
        for anom in quality_report["anomalies"]:
            severity_icon = "⚠️" if anom["severity"] in ["High", "Medium"] else "ℹ️"
            st.markdown(
                f"""
                <div class="quality-box">
                    <strong>{severity_icon} [{anom['severity']}] {anom['type']} ({anom['count']} affected rows)</strong><br>
                    {anom['details']}
                </div>
                """,
                unsafe_allow_html=True
            )
            if anom.get("examples"):
                st.caption("Sample affected records:")
                st.dataframe(pd.DataFrame(anom["examples"]), use_container_width=True, hide_index=True)

        st.markdown("#### Zero-Value Audit across Numerical Columns")
        zero_rows = []
        for col, info in quality_report["zeros_by_column"].items():
            zero_rows.append({
                "Column": col,
                "Zero Count": info["count"],
                "Percentage (%)": f"{info['pct']:.2f}%",
                "Explanation": "Natural zero for 100% urban/rural areas or recording artifact"
            })
        st.dataframe(pd.DataFrame(zero_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 11: DATA EXPLORER & EXPORT
    # -------------------------------------------------------------
    with tabs[10]:
        st.markdown('<div class="section-title">📑 Detailed Data Explorer & Export Center</div>', unsafe_allow_html=True)
        
        # Search & Column Selector
        col_exp1, col_exp2 = st.columns([2, 1])
        with col_exp1:
            search_query = st.text_input("🔍 Search Sub Division, District, or Province", placeholder="Type to filter rows...")
        with col_exp2:
            export_mode = st.radio("Dataset Version for Display", options=["Cleaned Analytical Data (51 Cols)", "Original Raw Data (21 Cols)"], horizontal=True)

        active_table = cleaned_df if "Cleaned" in export_mode else raw_df
        # Apply search query
        if search_query:
            mask = active_table.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
            display_df = active_table[mask]
        else:
            # Filter active table to current geographic selection
            if selected_subdivisions:
                display_df = active_table[active_table["SUB DIVISION"].isin(selected_subdivisions)]
            elif selected_districts:
                display_df = active_table[active_table["DISTRICT"].isin(selected_districts)]
            elif selected_divisions:
                display_df = active_table[active_table["DIVISION"].isin(selected_divisions)]
            elif selected_provinces:
                display_df = active_table[active_table["PROVINCE"].isin(selected_provinces)]
            else:
                display_df = active_table

        # Column selection
        all_cols = display_df.columns.tolist()
        default_cols = [
            "PROVINCE", "DIVISION", "DISTRICT", "SUB DIVISION",
            "Combined Population", "Rural Total Population", "Urban Total Population",
            "Urbanization Percentage", "Area (sq.km)", "Population Density (sq.km)",
            "Total Male Population", "Total Female Population", "Overall Sex Ratio",
            "Population Growth Percentage"
        ] if "Cleaned" in export_mode else all_cols[:12]
        
        selected_cols = st.multiselect("Visible Columns", options=all_cols, default=[c for c in default_cols if c in all_cols])
        
        st.dataframe(
            display_df[selected_cols],
            use_container_width=True,
            height=450,
            hide_index=True
        )

        st.caption(f"Displaying **{len(display_df):,} rows** out of {len(active_table):,} total rows.")

        # Download / Export Section
        st.markdown("#### 📥 Download Center")
        d1, d2, d3, d4 = st.columns(4)
        
        with d1:
            csv_filtered = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Filtered Data (CSV)",
                data=csv_filtered,
                file_name="pakistan_population_filtered.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with d2:
            csv_full = cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Full Cleaned Dataset (CSV)",
                data=csv_full,
                file_name="pakistan_population_full_analytical.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with d3:
            stats_csv = compute_descriptive_stats(filtered_df).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Analytical Summary (CSV)",
                data=stats_csv,
                file_name="descriptive_statistics_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

        with d4:
            kpi_df = pd.DataFrame([kpis])
            kpi_csv = kpi_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download KPI Summary (CSV)",
                data=kpi_csv,
                file_name="kpi_summary.csv",
                mime="text/csv",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
