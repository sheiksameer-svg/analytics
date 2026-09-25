"""
Data preprocessing and feature engineering module for Pakistan Population Analytics.
Safely cleans data, creates derived metrics, detects data quality issues, and preserves raw data.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def clean_and_derive_metrics(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset and calculate derived metrics on a copy.
    Never modifies the original raw dataframe.
    """
    df = raw_df.copy()

    # 1. Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Map of standard columns expected (case-insensitive fallback)
    col_upper_map = {c.upper(): c for c in df.columns}
    
    # 2. Ensure numeric types for numerical columns
    numeric_candidates = [
        "AREA (sq.km)", "ALL SEXES (RURAL)", "MALE (RURAL)", "FEMALE (RURAL)",
        "TRANSGENDER (RURAL)", "SEX RATIO (RURAL)", "AVG HOUSEHOLD SIZE (RURAL)",
        "POPULATION 1998 (RURAL)", "ANNUAL GROWTH RATE (RURAL)",
        "ALL SEXES (URBAN)", "MALE (URBAN)", "FEMALE (URBAN)",
        "TRANSGENDER (URBAN)", "SEX RATIO (URBAN)", "AVG HOUSEHOLD SIZE (URBAN)",
        "POPULATION 1998 (URBAN)", "ANNUAL GROWTH RATE (URBAN)"
    ]

    for candidate in numeric_candidates:
        actual_col = col_upper_map.get(candidate.upper())
        if actual_col and actual_col in df.columns:
            # Strip commas or non-numeric chars if string
            if df[actual_col].dtype == object:
                df[actual_col] = df[actual_col].astype(str).str.replace(",", "").str.strip()
            df[actual_col] = pd.to_numeric(df[actual_col], errors="coerce").fillna(0)

    # Resolve actual column names
    c_area = col_upper_map.get("AREA (SQ.KM)")
    c_rural_all = col_upper_map.get("ALL SEXES (RURAL)")
    c_rural_m = col_upper_map.get("MALE (RURAL)")
    c_rural_f = col_upper_map.get("FEMALE (RURAL)")
    c_rural_t = col_upper_map.get("TRANSGENDER (RURAL)")
    c_rural_sr = col_upper_map.get("SEX RATIO (RURAL)")
    c_rural_hh = col_upper_map.get("AVG HOUSEHOLD SIZE (RURAL)")
    c_rural_98 = col_upper_map.get("POPULATION 1998 (RURAL)")
    c_rural_gr = col_upper_map.get("ANNUAL GROWTH RATE (RURAL)")

    c_urban_all = col_upper_map.get("ALL SEXES (URBAN)")
    c_urban_m = col_upper_map.get("MALE (URBAN)")
    c_urban_f = col_upper_map.get("FEMALE (URBAN)")
    c_urban_t = col_upper_map.get("TRANSGENDER (URBAN)")
    c_urban_sr = col_upper_map.get("SEX RATIO (URBAN)")
    c_urban_hh = col_upper_map.get("AVG HOUSEHOLD SIZE (URBAN)")
    c_urban_98 = col_upper_map.get("POPULATION 1998 (URBAN)")
    c_urban_gr = col_upper_map.get("ANNUAL GROWTH RATE (URBAN)")

    # 3. Calculate Core Derived Population Metrics
    rural_pop = df[c_rural_all] if c_rural_all else pd.Series(0, index=df.index)
    urban_pop = df[c_urban_all] if c_urban_all else pd.Series(0, index=df.index)
    
    df["Rural Total Population"] = rural_pop
    df["Urban Total Population"] = urban_pop
    df["Combined Population"] = rural_pop + urban_pop

    # Gender components
    rural_m = df[c_rural_m] if c_rural_m else pd.Series(0, index=df.index)
    rural_f = df[c_rural_f] if c_rural_f else pd.Series(0, index=df.index)
    rural_t = df[c_rural_t] if c_rural_t else pd.Series(0, index=df.index)

    urban_m = df[c_urban_m] if c_urban_m else pd.Series(0, index=df.index)
    urban_f = df[c_urban_f] if c_urban_f else pd.Series(0, index=df.index)
    urban_t = df[c_urban_t] if c_urban_t else pd.Series(0, index=df.index)

    df["Total Male Population"] = rural_m + urban_m
    df["Total Female Population"] = rural_f + urban_f
    df["Total Transgender Population"] = rural_t + urban_t

    # Safe percentage calculations
    comb_pop = df["Combined Population"]
    comb_safe = comb_pop.replace(0, np.nan)
    rural_safe = rural_pop.replace(0, np.nan)
    urban_safe = urban_pop.replace(0, np.nan)

    df["Rural Population Share"] = (rural_pop / comb_safe * 100).fillna(0).round(2)
    df["Urban Population Share"] = (urban_pop / comb_safe * 100).fillna(0).round(2)
    df["Urbanization Percentage"] = df["Urban Population Share"]

    df["Rural Male Percentage"] = (rural_m / rural_safe * 100).fillna(0).round(2)
    df["Rural Female Percentage"] = (rural_f / rural_safe * 100).fillna(0).round(2)
    df["Urban Male Percentage"] = (urban_m / urban_safe * 100).fillna(0).round(2)
    df["Urban Female Percentage"] = (urban_f / urban_safe * 100).fillna(0).round(2)

    df["Overall Male Percentage"] = (df["Total Male Population"] / comb_safe * 100).fillna(0).round(2)
    df["Overall Female Percentage"] = (df["Total Female Population"] / comb_safe * 100).fillna(0).round(2)
    df["Overall Transgender Percentage"] = (df["Total Transgender Population"] / comb_safe * 100).fillna(0).round(4)

    # Sex Ratios (males per 100 females)
    female_safe = df["Total Female Population"].replace(0, np.nan)
    df["Overall Sex Ratio"] = (df["Total Male Population"] / female_safe * 100).fillna(0).round(2)

    # Population Density
    if c_area and c_area in df.columns:
        area_safe = df[c_area].replace(0, np.nan)
        df["Population Density (sq.km)"] = (df["Combined Population"] / area_safe).round(2)
        df["Area (sq.km)"] = df[c_area]
    else:
        df["Population Density (sq.km)"] = np.nan
        df["Area (sq.km)"] = 0.0

    # 1998 Comparisons and Historical Growth
    pop_98_rural = df[c_rural_98] if c_rural_98 else pd.Series(0, index=df.index)
    pop_98_urban = df[c_urban_98] if c_urban_98 else pd.Series(0, index=df.index)
    df["1998 Total Population"] = pop_98_rural + pop_98_urban

    df["Population Change from 1998"] = df["Combined Population"] - df["1998 Total Population"]
    pop_98_safe = df["1998 Total Population"].replace(0, np.nan)
    df["Population Growth Percentage"] = ((df["Population Change from 1998"] / pop_98_safe) * 100).fillna(0).round(2)

    # Gaps & Differences
    df["Rural vs Urban Difference"] = df["Urban Total Population"] - df["Rural Total Population"]
    df["Male-Female Gap"] = df["Total Male Population"] - df["Total Female Population"]

    # Weighted Average Household Size
    rural_hh = df[c_rural_hh] if c_rural_hh else pd.Series(0, index=df.index)
    urban_hh = df[c_urban_hh] if c_urban_hh else pd.Series(0, index=df.index)
    
    # Combined household size weighted by rural and urban populations
    weighted_hh_numerator = (rural_pop * rural_hh) + (urban_pop * urban_hh)
    df["Weighted Avg Household Size"] = (weighted_hh_numerator / comb_safe).fillna(0).round(2)

    # Dominance Classification
    def classify_dominance(row):
        r = row["Rural Total Population"]
        u = row["Urban Total Population"]
        if r > 0 and u == 0:
            return "100% Rural"
        elif u > 0 and r == 0:
            return "100% Urban"
        elif r > u:
            return "Rural Dominant"
        elif u > r:
            return "Urban Dominant"
        else:
            return "Balanced"

    df["Dominance Category"] = df.apply(classify_dominance, axis=1)

    # Flag Anomalies / Data Quality Indicators
    df["is_zero_area"] = df[c_area] <= 0 if c_area else False
    df["is_100pct_urban"] = df["Rural Total Population"] == 0
    df["is_100pct_rural"] = df["Urban Total Population"] == 0
    
    # 100.0 growth rate placeholder flag (seen in census when rural went to 0)
    if c_rural_gr:
        df["is_growth_anomaly_rural"] = (df[c_rural_gr] >= 99.0) & (df["Rural Total Population"] == 0)
    else:
        df["is_growth_anomaly_rural"] = False

    return df


def get_data_quality_report(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data quality audit report.
    Identifies zero values, missing values, duplicates, and census data anomalies.
    """
    num_cols = raw_df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = raw_df.select_dtypes(include=["object", "string"]).columns.tolist()

    missing_by_col = {col: int(raw_df[col].isnull().sum()) for col in raw_df.columns if raw_df[col].isnull().sum() > 0}
    zeros_by_col = {}
    for col in num_cols:
        count = int((raw_df[col] == 0).sum())
        if count > 0:
            zeros_by_col[col] = {
                "count": count,
                "pct": round(count / len(raw_df) * 100, 2)
            }

    # Identify specific known census anomalies
    anomalies: List[Dict[str, Any]] = []

    # 1. Zero Area
    if "AREA (sq.km)" in raw_df.columns:
        zero_area_rows = raw_df[raw_df["AREA (sq.km)"] == 0]
        if len(zero_area_rows) > 0:
            anomalies.append({
                "type": "Zero Area Recorded",
                "severity": "High",
                "count": len(zero_area_rows),
                "details": f"{len(zero_area_rows)} sub-divisions have an AREA of 0 sq.km, preventing direct population density calculation.",
                "examples": zero_area_rows[["PROVINCE", "DISTRICT", "SUB DIVISION"]].head(5).to_dict("records") if "SUB DIVISION" in zero_area_rows else []
            })

    # 2. 100.0 Growth Rate placeholder
    if "ANNUAL GROWTH RATE (RURAL)" in raw_df.columns:
        extreme_growth = raw_df[raw_df["ANNUAL GROWTH RATE (RURAL)"] >= 99.0]
        if len(extreme_growth) > 0:
            anomalies.append({
                "type": "Census Growth Rate Placeholder (100.0%)",
                "severity": "Medium",
                "count": len(extreme_growth),
                "details": f"{len(extreme_growth)} sub-divisions (e.g. Lahore tehsils) record an Annual Growth Rate of 100.0% for Rural where Rural Population dropped to 0, representing an official census coding artifact rather than true annual population doubling.",
                "examples": extreme_growth[["PROVINCE", "DISTRICT", "SUB DIVISION", "ANNUAL GROWTH RATE (RURAL)"]].head(5).to_dict("records")
            })

    # 3. 100% Urban Sub-divisions
    if "ALL SEXES (RURAL)" in raw_df.columns:
        urban_only = raw_df[raw_df["ALL SEXES (RURAL)"] == 0]
        anomalies.append({
            "type": "Entirely Urban Administrative Units",
            "severity": "Informational",
            "count": len(urban_only),
            "details": f"{len(urban_only)} sub-divisions are 100% urban with 0 rural population (e.g., Karachi, Lahore tehsils). Rural demographic metrics (Rural Sex Ratio, Rural Household Size) are naturally 0 in these rows.",
            "examples": urban_only[["PROVINCE", "DISTRICT", "SUB DIVISION"]].head(5).to_dict("records") if "SUB DIVISION" in urban_only else []
        })

    # 4. 100% Rural Sub-divisions
    if "ALL SEXES (URBAN)" in raw_df.columns:
        rural_only = raw_df[raw_df["ALL SEXES (URBAN)"] == 0]
        anomalies.append({
            "type": "Entirely Rural Administrative Units",
            "severity": "Informational",
            "count": len(rural_only),
            "details": f"{len(rural_only)} sub-divisions are 100% rural with 0 urban population (common in remote Balochistan, KPK/FATA). Urban demographic metrics are naturally 0 in these rows.",
            "examples": rural_only[["PROVINCE", "DISTRICT", "SUB DIVISION"]].head(5).to_dict("records") if "SUB DIVISION" in rural_only else []
        })

    return {
        "total_rows": len(raw_df),
        "total_columns": len(raw_df.columns),
        "total_duplicates": int(raw_df.duplicated().sum()),
        "missing_by_column": missing_by_col,
        "total_missing_cells": int(raw_df.isnull().sum().sum()),
        "zeros_by_column": zeros_by_col,
        "numerical_column_count": len(num_cols),
        "categorical_column_count": len(cat_cols),
        "anomalies": anomalies,
        "cleaned_column_count": len(cleaned_df.columns),
        "derived_metrics_added": len(cleaned_df.columns) - len(raw_df.columns),
    }
