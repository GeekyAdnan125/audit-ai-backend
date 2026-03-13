
"""Data cleaning pipeline for purchase, sales, and general ledgers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd


LOGGER = logging.getLogger(__name__)

INPUT_FILENAME_CANDIDATES: Dict[str, List[str]] = {
    "purchase_ledger": ["purchase_ledger.csv", "Purchase_Ledger.csv"],
    "sales_ledger": ["sales_ledger.csv", "Sales_Ledger.csv"],
    "general_ledger": ["general_ledger.csv", "General_Ledger.csv"],
}

DATE_COLUMNS: Dict[str, List[str]] = {
    "purchase_ledger": ["Purchase_Date", "Payment_Date"],
    "sales_ledger": ["Sale_Date", "Payment_Date"],
    "general_ledger": ["Transaction_Date"],
}

NAME_COLUMNS: Dict[str, List[str]] = {
    "purchase_ledger": ["Vendor_Name"],
    "sales_ledger": ["Customer_Name"],
    "general_ledger": [],
}

CRITICAL_COLUMNS: Dict[str, List[str]] = {
    "purchase_ledger": ["Vendor_ID", "Invoice_Number", "Total_Amount"],
    "sales_ledger": ["Customer_ID", "Invoice_Number", "Sales_Amount"],
    "general_ledger": ["Journal_Entry_ID", "Debit_Amount", "Credit_Amount"],
}

OUTPUT_FILENAMES: Dict[str, str] = {
    "purchase_ledger": "cleaned_purchase_ledger.csv",
    "sales_ledger": "cleaned_sales_ledger.csv",
    "general_ledger": "cleaned_general_ledger.csv",
}


def _resolve_input_file(input_dir: Path, dataset_key: str) -> Path:
    for file_name in INPUT_FILENAME_CANDIDATES[dataset_key]:
        file_path = input_dir / file_name
        if file_path.exists():
            return file_path
    candidates = ", ".join(INPUT_FILENAME_CANDIDATES[dataset_key])
    raise FileNotFoundError(f"Missing input file for {dataset_key}. Tried: {candidates}")


def load_data(input_dir: str | Path) -> Dict[str, pd.DataFrame]:
    """Load ledger CSV files from input directory."""
    input_path = Path(input_dir)
    datasets: Dict[str, pd.DataFrame] = {}

    LOGGER.info("Loading input datasets from %s", input_path)
    for dataset_key in INPUT_FILENAME_CANDIDATES:
        file_path = _resolve_input_file(input_path, dataset_key)
        datasets[dataset_key] = pd.read_csv(file_path)
        LOGGER.info("Loaded %s (%s rows)", file_path.name, len(datasets[dataset_key]))

    return datasets


def standardize_date_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convert a date column to ISO format YYYY-MM-DD using coercion for invalid values."""
    if column_name not in df.columns:
        LOGGER.warning("Date column '%s' not found; skipping", column_name)
        return df

    parsed = pd.to_datetime(df[column_name], errors="coerce")
    df[column_name] = parsed.dt.strftime("%Y-%m-%d")
    return df


def standardize_dates(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Standardize all configured date columns in each dataset."""
    for dataset_key, columns in DATE_COLUMNS.items():
        for column_name in columns:
            dataframes[dataset_key] = standardize_date_column(dataframes[dataset_key], column_name)
    return dataframes


def normalize_entity_names(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Normalize entity names by case, spacing, and punctuation cleanup."""
    if column_name not in df.columns:
        LOGGER.warning("Name column '%s' not found; skipping", column_name)
        return df

    cleaned = (
        df[column_name]
        .astype("string")
        .str.lower()
        .str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df[column_name] = cleaned.replace("", pd.NA)
    return df


def normalize_names(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Normalize vendor/customer name fields across datasets."""
    for dataset_key, columns in NAME_COLUMNS.items():
        for column_name in columns:
            dataframes[dataset_key] = normalize_entity_names(dataframes[dataset_key], column_name)
    return dataframes


def flag_missing_critical_fields(df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
    """Flag rows where any required field is null or empty."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    for column in missing_columns:
        LOGGER.warning("Critical column '%s' not found; treating as missing", column)
        df[column] = pd.NA

    null_mask = df[required_columns].isna()
    empty_mask = df[required_columns].apply(lambda s: s.astype("string").str.strip().eq(""))
    df["Missing_Critical_Field"] = (null_mask | empty_mask).any(axis=1)
    return df


def flag_missing_fields(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Add Missing_Critical_Field flag to each dataset."""
    for dataset_key, columns in CRITICAL_COLUMNS.items():
        dataframes[dataset_key] = flag_missing_critical_fields(dataframes[dataset_key], columns)
    return dataframes


def save_outputs(dataframes: Dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    """Save cleaned dataframes to output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Saving cleaned files to %s", output_path)
    for dataset_key, df in dataframes.items():
        file_path = output_path / OUTPUT_FILENAMES[dataset_key]
        df.to_csv(file_path, index=False)
        LOGGER.info("Saved %s", file_path.name)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "input_files"
    output_dir = project_root / "output_files"

    datasets = load_data(input_dir)

    LOGGER.info("Cleaning Purchase Ledger...")
    LOGGER.info("Cleaning Sales Ledger...")
    LOGGER.info("Cleaning General Ledger...")
    datasets = standardize_dates(datasets)
    datasets = normalize_names(datasets)
    datasets = flag_missing_fields(datasets)

    save_outputs(datasets, output_dir)
    LOGGER.info("Data cleaning completed successfully")


if __name__ == "__main__":
    main()
