"""
Data loader module for Pakistan Population Analytics Dashboard.
Handles file detection, ingestion, and initial structure inspection.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional, Union
import io
import pandas as pd


def find_default_dataset_path() -> Optional[Path]:
    """
    Search for dataset in standard locations.
    Returns Path object or None.
    """
    candidates = [
        Path("data/sub-division_population_of_pakistan.csv"),
        Path("data/dataset.csv"),
        Path("sub-division_population_of_pakistan.csv"),
        Path("dataset.csv"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    # Search in data folder for any CSV
    data_dir = Path("data")
    if data_dir.exists() and data_dir.is_dir():
        csv_files = list(data_dir.glob("*.csv"))
        if csv_files:
            return csv_files[0]

    # Search current directory
    csv_files = list(Path(".").glob("*.csv"))
    if csv_files:
        return csv_files[0]

    return None


def load_dataset(source: Union[str, Path, io.BytesIO, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load dataset from file path or buffer.
    Never modifies the original data source.
    Returns (raw_dataframe, ingestion_metadata).
    """
    try:
        if isinstance(source, (str, Path)):
            raw_df = pd.read_csv(source)
            source_name = str(Path(source).name)
        else:
            raw_df = pd.read_csv(source)
            source_name = getattr(source, "name", "Uploaded CSV")

        # Basic metadata
        meta = {
            "source_name": source_name,
            "rows": raw_df.shape[0],
            "columns": raw_df.shape[1],
            "column_names": list(raw_df.columns),
            "memory_usage_kb": round(raw_df.memory_usage(deep=True).sum() / 1024, 2),
        }
        return raw_df, meta
    except Exception as e:
        raise ValueError(f"Failed to load dataset: {str(e)}")


def inspect_raw_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Inspect columns, data types, missing values, duplicates, and zeros in raw dataframe.
    """
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    
    missing_counts = df.isnull().sum().to_dict()
    missing_total = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    # Count zeros for numerical columns
    zero_counts = {}
    for col in num_cols:
        zeros = int((df[col] == 0).sum())
        zero_counts[col] = {
            "count": zeros,
            "pct": round((zeros / len(df)) * 100, 2) if len(df) > 0 else 0
        }

    # Verify hierarchy columns (case-insensitive search)
    col_map = {c.strip().upper(): c for c in df.columns}
    hierarchy_cols = {
        "PROVINCE": col_map.get("PROVINCE"),
        "DIVISION": col_map.get("DIVISION"),
        "DISTRICT": col_map.get("DISTRICT"),
        "SUB DIVISION": col_map.get("SUB DIVISION") or col_map.get("SUBDIVISION") or col_map.get("TEHSIL"),
    }

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "numerical_columns": num_cols,
        "categorical_columns": cat_cols,
        "missing_counts": missing_counts,
        "missing_total": missing_total,
        "duplicate_rows": duplicate_rows,
        "zero_counts": zero_counts,
        "hierarchy_detected": hierarchy_cols,
        "has_full_hierarchy": all(v is not None for v in hierarchy_cols.values()),
    }
