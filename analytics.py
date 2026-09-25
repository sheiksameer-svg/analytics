"""
Analytics module for Pakistan Population Analytics Dashboard.
Performs KPI computations, descriptive statistics, correlation analysis,
outlier detection, and hierarchical aggregation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute comprehensive KPI summary for currently filtered dataset.
    Handles empty dataframes gracefully.
    """
    if df.empty:
        return {
            "total_population": 0,
            "rural_population": 0,
            "urban_population": 0,
            "urbanization_pct": 0.0,
            "rural_share_pct": 0.0,
            "total_area": 0.0,
            "population_density": 0.0,
            "male_population": 0,
            "female_population": 0,
            "transgender_population": 0,
            "male_pct": 0.0,
            "female_pct": 0.0,
            "transgender_pct": 0.0,
            "pop_1998_total": 0,
            "pop_change_1998": 0,
            "growth_pct_1998": 0.0,
            "avg_growth_rate": 0.0,
            "sex_ratio": 0.0,
            "avg_household_size": 0.0,
            "subdivisions_count": 0,
            "districts_count": 0,
            "divisions_count": 0,
            "provinces_count": 0,
        }

    total_pop = int(df["Combined Population"].sum())
    rural_pop = int(df["Rural Total Population"].sum())
    urban_pop = int(df["Urban Total Population"].sum())
    
    urban_pct = round((urban_pop / total_pop * 100), 2) if total_pop > 0 else 0.0
    rural_pct = round((rural_pop / total_pop * 100), 2) if total_pop > 0 else 0.0

    total_area = round(float(df["Area (sq.km)"].sum()), 2) if "Area (sq.km)" in df.columns else 0.0
    pop_density = round(total_pop / total_area, 2) if total_area > 0 else 0.0

    male_pop = int(df["Total Male Population"].sum())
    female_pop = int(df["Total Female Population"].sum())
    trans_pop = int(df["Total Transgender Population"].sum())

    male_pct = round((male_pop / total_pop * 100), 2) if total_pop > 0 else 0.0
    female_pct = round((female_pop / total_pop * 100), 2) if total_pop > 0 else 0.0
    trans_pct = round((trans_pop / total_pop * 100), 4) if total_pop > 0 else 0.0

    sex_ratio = round((male_pop / female_pop * 100), 2) if female_pop > 0 else 0.0

    pop_98_total = int(df["1998 Total Population"].sum()) if "1998 Total Population" in df.columns else 0
    pop_change_98 = total_pop - pop_98_total
    growth_pct_98 = round((pop_change_98 / pop_98_total * 100), 2) if pop_98_total > 0 else 0.0

    # Calculate average annual growth rate excluding placeholder 100.0% records
    growth_rates = []
    if "ANNUAL GROWTH RATE (URBAN)" in df.columns and "ANNUAL GROWTH RATE (RURAL)" in df.columns:
        # Use valid non-placeholder rural and urban rates
        rural_valid = df[(df["ANNUAL GROWTH RATE (RURAL)"] > 0) & (df["ANNUAL GROWTH RATE (RURAL)"] < 50)]["ANNUAL GROWTH RATE (RURAL)"]
        urban_valid = df[(df["ANNUAL GROWTH RATE (URBAN)"] > 0) & (df["ANNUAL GROWTH RATE (URBAN)"] < 50)]["ANNUAL GROWTH RATE (URBAN)"]
        combined_rates = pd.concat([rural_valid, urban_valid])
        avg_growth_rate = round(float(combined_rates.mean()), 2) if len(combined_rates) > 0 else 0.0
    else:
        avg_growth_rate = 0.0

    # Weighted Average Household Size
    if "Weighted Avg Household Size" in df.columns and total_pop > 0:
        valid_hh = df[df["Weighted Avg Household Size"] > 0]
        if not valid_hh.empty:
            avg_hh = round(float((valid_hh["Weighted Avg Household Size"] * valid_hh["Combined Population"]).sum() / valid_hh["Combined Population"].sum()), 2)
        else:
            avg_hh = 0.0
    else:
        avg_hh = 0.0

    return {
        "total_population": total_pop,
        "rural_population": rural_pop,
        "urban_population": urban_pop,
        "urbanization_pct": urban_pct,
        "rural_share_pct": rural_pct,
        "total_area": total_area,
        "population_density": pop_density,
        "male_population": male_pop,
        "female_population": female_pop,
        "transgender_population": trans_pop,
        "male_pct": male_pct,
        "female_pct": female_pct,
        "transgender_pct": trans_pct,
        "pop_1998_total": pop_98_total,
        "pop_change_1998": pop_change_98,
        "growth_pct_1998": growth_pct_98,
        "avg_growth_rate": avg_growth_rate,
        "sex_ratio": sex_ratio,
        "avg_household_size": avg_hh,
        "subdivisions_count": df["SUB DIVISION"].nunique() if "SUB DIVISION" in df.columns else len(df),
        "districts_count": df["DISTRICT"].nunique() if "DISTRICT" in df.columns else 0,
        "divisions_count": df["DIVISION"].nunique() if "DIVISION" in df.columns else 0,
        "provinces_count": df["PROVINCE"].nunique() if "PROVINCE" in df.columns else 0,
    }


def compute_descriptive_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Calculate full descriptive statistics: Mean, Median, Std, Min, Q1, Q2, Q3, Max, IQR.
    """
    if df.empty:
        return pd.DataFrame()

    default_cols = [
        "Combined Population", "Rural Total Population", "Urban Total Population",
        "Area (sq.km)", "Population Density (sq.km)", "Total Male Population",
        "Total Female Population", "Overall Sex Ratio", "Weighted Avg Household Size",
        "Population Growth Percentage", "Urbanization Percentage"
    ]
    cols_to_use = [c for c in (columns or default_cols) if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]

    stats_list = []
    for col in cols_to_use:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        q25 = float(s.quantile(0.25))
        q50 = float(s.median())
        q75 = float(s.quantile(0.75))
        iqr = q75 - q25

        stats_list.append({
            "Metric": col,
            "Count": int(s.count()),
            "Mean": round(float(s.mean()), 2),
            "Std Dev": round(float(s.std()), 2) if len(s) > 1 else 0.0,
            "Min": round(float(s.min()), 2),
            "25% (Q1)": round(q25, 2),
            "Median (Q2)": round(q50, 2),
            "75% (Q3)": round(q75, 2),
            "Max": round(float(s.max()), 2),
            "IQR": round(iqr, 2),
            "Skewness": round(float(s.skew()), 2) if len(s) > 2 else 0.0
        })

    return pd.DataFrame(stats_list)


def compute_correlation_matrix(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Compute Pearson correlation matrix of analytical variables.
    """
    if df.empty:
        return pd.DataFrame()

    default_cols = [
        "Combined Population", "Rural Total Population", "Urban Total Population",
        "Area (sq.km)", "Population Density (sq.km)", "Total Male Population",
        "Total Female Population", "Total Transgender Population",
        "Overall Sex Ratio", "Weighted Avg Household Size", "Urbanization Percentage",
        "Population Change from 1998"
    ]
    cols_to_use = [c for c in (columns or default_cols) if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    
    corr_df = df[cols_to_use].corr(method="pearson").round(3)
    return corr_df


def detect_outliers(df: pd.DataFrame, column: str, method: str = "iqr", threshold: float = 1.5) -> pd.DataFrame:
    """
    Detect statistical outliers using IQR or Z-score method.
    """
    if df.empty or column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return pd.DataFrame()

    s = df[column].dropna()
    if len(s) < 4:
        return pd.DataFrame()

    if method == "iqr":
        q25 = s.quantile(0.25)
        q75 = s.quantile(0.75)
        iqr = q75 - q25
        lower_bound = q25 - (threshold * iqr)
        upper_bound = q75 + (threshold * iqr)
        outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    else:  # z-score
        mean = s.mean()
        std = s.std()
        if std == 0:
            return pd.DataFrame()
        z_scores = ((df[column] - mean) / std).abs()
        outlier_mask = z_scores > threshold
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std

    outliers = df[outlier_mask].copy()
    if not outliers.empty:
        outliers["Outlier_Type"] = np.where(outliers[column] > upper_bound, "High Outlier", "Low Outlier")
        outliers["Lower_Bound"] = round(lower_bound, 2)
        outliers["Upper_Bound"] = round(upper_bound, 2)

    return outliers


def aggregate_by_hierarchy(df: pd.DataFrame, level_col: str) -> pd.DataFrame:
    """
    Aggregate demographic totals and recalculate rates correctly at hierarchical level
    (e.g., PROVINCE, DIVISION, DISTRICT).
    """
    if df.empty or level_col not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "Combined Population": "sum",
        "Rural Total Population": "sum",
        "Urban Total Population": "sum",
        "Total Male Population": "sum",
        "Total Female Population": "sum",
        "Total Transgender Population": "sum",
        "Area (sq.km)": "sum",
        "1998 Total Population": "sum",
        "Population Change from 1998": "sum",
        "SUB DIVISION": "count"
    }
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}

    grouped = df.groupby(level_col).agg(agg_dict).reset_index()
    grouped.rename(columns={"SUB DIVISION": "Sub Division Count"}, inplace=True)

    # Recalculate derived ratios properly at aggregated level
    comb = grouped["Combined Population"].replace(0, np.nan)
    grouped["Rural Population Share"] = (grouped["Rural Total Population"] / comb * 100).fillna(0).round(2)
    grouped["Urban Population Share"] = (grouped["Urban Total Population"] / comb * 100).fillna(0).round(2)
    grouped["Urbanization Percentage"] = grouped["Urban Population Share"]

    area = grouped["Area (sq.km)"].replace(0, np.nan)
    grouped["Population Density (sq.km)"] = (grouped["Combined Population"] / area).fillna(0).round(2)

    females = grouped["Total Female Population"].replace(0, np.nan)
    grouped["Overall Sex Ratio"] = (grouped["Total Male Population"] / females * 100).fillna(0).round(2)

    pop98 = grouped["1998 Total Population"].replace(0, np.nan)
    grouped["Population Growth Percentage"] = (grouped["Population Change from 1998"] / pop98 * 100).fillna(0).round(2)

    return grouped.sort_values(by="Combined Population", ascending=False)


def get_top_bottom_rankings(
    df: pd.DataFrame,
    column: str,
    n: int = 10,
    region_col: str = "SUB DIVISION"
) -> Dict[str, pd.DataFrame]:
    """
    Return top N and bottom N regions for specified numerical column.
    """
    if df.empty or column not in df.columns:
        return {"top": pd.DataFrame(), "bottom": pd.DataFrame()}

    cols_show = [c for c in ["PROVINCE", "DIVISION", "DISTRICT", region_col, column] if c in df.columns]
    
    valid_df = df[df[column] > 0].sort_values(by=column, ascending=False) if column in ["Combined Population", "Population Density (sq.km)"] else df.sort_values(by=column, ascending=False)
    
    top_n = valid_df.head(n)[cols_show].copy()
    bottom_n = valid_df.tail(n).sort_values(by=column, ascending=True)[cols_show].copy()

    return {"top": top_n, "bottom": bottom_n}
