
"""
Agent 2 – Financial Anomaly Detection for Audit Analytics

Processes the cleaned purchase ledger produced by Agent 1 and flags
three categories of vendor transaction anomalies:

    Rule 1 – Duplicate Invoice Detection
    Rule 2 – Unusual Transaction Amounts (Vendor Z-Score)
    Rule 3 – Round-Number Transaction Pattern

Input:  output_files/cleaned_purchase_ledger.csv
Output: output_files/anomaly_purchase_ledger.csv
"""

import numpy as np
import pandas as pd

try:
    # Package import path (works with: python -m agents.anomaly_agent)
    from agents.base_agent import BaseAgent
except ModuleNotFoundError:
    # Direct script fallback (works with: python agents/anomaly_agent.py)
    from base_agent import BaseAgent


# ---------------------------------------------------------------------------
# Rule 1 – Duplicate Invoice Detection
# ---------------------------------------------------------------------------

def detect_duplicate_invoices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag rows that share the same Vendor_ID, Invoice_Number, and
    Total_Amount combination — a strong indicator of duplicate vendor
    payments or double-entry accounting errors.

    Adds column:
        Duplicate_Invoice  (bool)
            True  → this row is part of a duplicate group
            False → unique transaction
    """
    # duplicated(..., keep=False) marks EVERY row in a duplicate group as True
    df["Duplicate_Invoice"] = df.duplicated(
        subset=["Vendor_ID", "Invoice_Number", "Total_Amount"],
        keep=False,
    )
    return df


# ---------------------------------------------------------------------------
# Rule 2 – Unusual Transaction Amounts (Vendor Z-Score)
# ---------------------------------------------------------------------------

def detect_vendor_zscore_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each vendor, compute a Z-score on Total_Amount relative to that
    vendor's own transaction history.  Transactions more than 3 standard
    deviations from the vendor mean are flagged as unusual — they may
    represent inflated invoices or one-off fraudulent charges.

    Per-vendor statistics:
        mean_amount  = mean(Total_Amount)   for the vendor
        std_amount   = std(Total_Amount)    for the vendor
        z_score      = (Total_Amount - mean_amount) / std_amount

    Where std_amount is 0 or NaN the Z-score defaults to 0 (no anomaly).

    Adds column:
        Unusual_Amount  (bool)
            True  → |z_score| > 3
            False → within normal range
    """
    # Calculate per-vendor mean and std using groupby transform so every
    # row keeps its own value aligned with the original index.
    vendor_mean = df.groupby("Vendor_ID")["Total_Amount"].transform("mean")
    vendor_std  = df.groupby("Vendor_ID")["Total_Amount"].transform("std")

    # Replace 0 / NaN std with 1 to avoid division-by-zero; the resulting
    # z_score will be 0 for any vendor with a single transaction or
    # perfectly uniform amounts, so no false positives are introduced.
    vendor_std_safe = vendor_std.replace(0, np.nan).fillna(1)

    z_scores = (df["Total_Amount"] - vendor_mean) / vendor_std_safe

    df["Unusual_Amount"] = z_scores.abs() > 3
    return df


# ---------------------------------------------------------------------------
# Rule 3 – Round-Number Transaction Pattern
# ---------------------------------------------------------------------------

def detect_round_number_pattern(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fraudulent invoices frequently use psychologically convenient round
    numbers (multiples of 1 000).  This rule flags vendors whose invoices
    are disproportionately round.

    Step 1 – Identify individual round transactions:
        Is_Round_Transaction = (Total_Amount % 1000 == 0)

    Step 2 – Per vendor, compute the fraction of round transactions:
        round_ratio = round_transactions / total_transactions

    Step 3 – If round_ratio > 0.10 (10 %), ALL of that vendor's rows are
    flagged, reflecting systemic rather than incidental behaviour.

    Adds column:
        Round_Number_Risk  (bool)
            True  → vendor's round-number ratio exceeds 10 %
            False → within acceptable threshold
    """
    # Step 1: flag each transaction that is a clean multiple of 1 000
    df["Is_Round_Transaction"] = (df["Total_Amount"] % 1000 == 0)

    # Step 2: per-vendor ratio of round transactions using transform so
    # every row carries its vendor's aggregate ratio
    round_count = df.groupby("Vendor_ID")["Is_Round_Transaction"].transform("sum")
    total_count = df.groupby("Vendor_ID")["Is_Round_Transaction"].transform("count")
    round_ratio = round_count / total_count

    # Step 3: flag ALL transactions for vendors whose ratio exceeds 10 %
    df["Round_Number_Risk"] = round_ratio > 0.10
    return df


# ---------------------------------------------------------------------------
# Pipeline entry-point
# ---------------------------------------------------------------------------

def run_anomaly_detection() -> pd.DataFrame:
    """
    End-to-end anomaly detection pipeline:

    1. Load  output_files/cleaned_purchase_ledger.csv
    2. Drop  rows where Missing_Critical_Field == True
    3. Apply Rule 1 – duplicate invoice detection
    4. Apply Rule 2 – vendor Z-score anomaly detection
    5. Apply Rule 3 – round-number pattern detection
    6. Save  output_files/anomaly_purchase_ledger.csv

    Returns the annotated DataFrame.
    """
    input_path  = "output_files/cleaned_purchase_ledger.csv"
    output_path = "output_files/anomaly_purchase_ledger.csv"

    # Step 1 – Load cleaned ledger
    df = pd.read_csv(input_path)

    # Step 2 – Remove rows that still carry missing critical fields;
    # these cannot be reliably analysed and must not pollute group stats.
    df = df[df["Missing_Critical_Field"] != True].copy()

    # Step 3 – Duplicate invoice detection
    df = detect_duplicate_invoices(df)

    # Step 4 – Vendor Z-score anomaly detection
    df = detect_vendor_zscore_anomalies(df)

    # Step 5 – Round-number transaction pattern
    df = detect_round_number_pattern(df)

    # Step 6 – Persist annotated ledger
    df.to_csv(output_path, index=False)
    print(f"[AnomalyAgent] Saved {len(df)} rows → {output_path}")

    return df


# ---------------------------------------------------------------------------
# BaseAgent integration
# ---------------------------------------------------------------------------

class AnomalyAgent(BaseAgent):
    """
    Wraps the anomaly-detection pipeline inside the BaseAgent interface
    so it can be invoked uniformly by the orchestrator.
    """

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all three anomaly-detection rules to *df* and return the
        annotated DataFrame.  The caller is responsible for pre-filtering
        rows with Missing_Critical_Field == True before passing *df*.
        """
        df = detect_duplicate_invoices(df)
        df = detect_vendor_zscore_anomalies(df)
        df = detect_round_number_pattern(df)
        return df

    def generate_findings(self, df: pd.DataFrame) -> list:
        """
        Translate anomaly flags into structured finding records that can
        be forwarded to the report generator or LLM reasoning layer.
        """
        findings = []

        for _, row in df.iterrows():
            if row.get("Duplicate_Invoice"):
                findings.append({
                    "rule":           "duplicate_invoice",
                    "vendor_id":      row.get("Vendor_ID"),
                    "invoice_number": row.get("Invoice_Number"),
                    "total_amount":   row.get("Total_Amount"),
                    "purchase_date":  row.get("Purchase_Date"),
                })

            if row.get("Unusual_Amount"):
                findings.append({
                    "rule":           "unusual_amount_zscore",
                    "vendor_id":      row.get("Vendor_ID"),
                    "invoice_number": row.get("Invoice_Number"),
                    "total_amount":   row.get("Total_Amount"),
                    "purchase_date":  row.get("Purchase_Date"),
                })

            if row.get("Round_Number_Risk"):
                findings.append({
                    "rule":           "round_number_pattern",
                    "vendor_id":      row.get("Vendor_ID"),
                    "invoice_number": row.get("Invoice_Number"),
                    "total_amount":   row.get("Total_Amount"),
                    "purchase_date":  row.get("Purchase_Date"),
                })

        return findings


if __name__ == "__main__":
    run_anomaly_detection()
